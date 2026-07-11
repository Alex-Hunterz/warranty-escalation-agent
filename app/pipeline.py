"""
Event-streaming pipeline: voice/text command -> intent -> inbox search ->
evidence assembly -> 6-agent adversarial pipeline -> Computer Use portal.

Supports mid-run user interjections: notes are injected into every remaining
agent's context; if the run already passed the relevant phase (or finished),
a revision run re-executes from Extraction with the correction merged,
reusing the already-fetched evidence.
"""
import queue
import threading
import time
import traceback
import uuid
from datetime import date
from typing import Dict, List, Optional

from src.core import call_llm, safe_json_parse
from src.agents.extraction_agent import extract_case
from src.agents.advocate_agent import advocate
from src.agents.defense_agent import defense
from src.agents.arbiter_agent import arbiter
from src.agents.filing_agent import filing
from src.agents.monitoring_agent import monitor

RUNS: Dict[str, "Run"] = {}

INTENT_PROMPT = """You are the intake router of a consumer-warranty agent.
The user speaks casually (voice transcript). Extract what to search their inbox for.

Return ONLY JSON:
{
  "brands": ["company/brand names mentioned, e.g. Nothing, Flipkart"],
  "product": "product being complained about, or null",
  "issue": "one-line summary of the problem, or null",
  "search_terms": ["4-8 short inbox search keywords: brand names, product, order/support words like warranty, refund, ticket, invoice"],
  "spoken_ack": "One short, confident sentence acknowledging the task in second person (will be read aloud)"
}"""

SYNTH_NOTE = "Emails were auto-pulled from the user's Gmail by the intake agent."


def llm_json(system: str, user: str, retries: int = 2) -> dict:
    last = None
    for _ in range(retries + 1):
        try:
            return safe_json_parse(call_llm(system, user, response_format="json"))
        except Exception as e:
            last = e
            time.sleep(2)
    raise last


class Run:
    def __init__(self, command: str, inbox, revise_of: Optional["Run"] = None,
                 note: Optional[str] = None):
        self.id = uuid.uuid4().hex[:12]
        self.command = command
        self.inbox = inbox
        self.q: "queue.Queue[dict]" = queue.Queue()
        self.done = False
        # mid-run interjections (thread-safe enough: list append + drain)
        self.notes: List[str] = []
        self._applied_notes: List[str] = []
        # revision support
        self.revise_of = revise_of
        self.evidence = None          # (receipt_txt, support_txt) after assembly
        if revise_of is not None:
            self.evidence = revise_of.evidence
            self._applied_notes = []
            self.notes = list(revise_of._applied_notes)
            if note:
                self.notes.append(note)
        RUNS[self.id] = self

    def emit(self, type_: str, **data):
        self.q.put({"type": type_, "ts": time.time(), **data})

    def interject(self, note: str) -> bool:
        """Add a user note to a live run. Returns False if run already ended."""
        if self.done:
            return False
        self.notes.append(note)
        self.emit("note_ack", note=note,
                  message="Noted — will be handed to every remaining agent.")
        return True

    def _drain_notes(self, case_obj: Optional[dict]) -> List[str]:
        """Move pending notes into applied set (and case_obj if given)."""
        fresh = self.notes[len(self._applied_notes):]
        if fresh:
            self._applied_notes.extend(fresh)
            if case_obj is not None:
                case_obj.setdefault("user_added_context", []).extend(fresh)
                self.emit("note_applied", notes=fresh)
        return self._applied_notes

    def start(self):
        threading.Thread(target=self._safe_run, daemon=True).start()

    def _safe_run(self):
        try:
            self._run()
        except Exception as e:
            traceback.print_exc()
            self.emit("fatal", error=str(e))
        finally:
            self.done = True
            self.q.put({"type": "__end__"})

    # ------------------------------------------------------------------ flow
    def _run(self):
        today = date.today().isoformat()

        if self.revise_of is None:
            issue = self._gather()
            if issue is None:
                return
        else:
            self.emit("revise_start",
                      message="Revising the case with your correction — evidence "
                              "already on file, re-running the reasoning agents.",
                      notes=self.notes)
            issue = "See support thread"
        receipt_txt, support_txt = self.evidence

        # EXTRACTION -------------------------------------------------------
        chat = SYNTH_NOTE + "\n\n" + "\n\n---\n\n".join(support_txt)
        pending = self.notes[:]
        if pending:
            chat += ("\n\n--- USER-ADDED CONTEXT (corrections stated directly "
                     "by the consumer; treat as true facts of the case) ---\n"
                     + "\n".join(f"- {n}" for n in pending))
        self.emit("stage_start", stage="extract", label="Extraction Agent",
                  detail="Building structured CaseObject; hunting the company's own SLA promise…")
        case_obj = self._retry(lambda: extract_case({
            "receipt_text": "\n\n---\n\n".join(receipt_txt) or "Not found in inbox",
            "warranty_text": "Per invoice: 1 year manufacturer warranty" if receipt_txt else "Not provided",
            "defect_description": issue,
            "defect_date": "See support thread",
            "chat_thread": chat,
            "defect_photos_count": 3,
            "today_date": today,
        }))
        self._applied_notes = pending
        if pending:
            case_obj.setdefault("user_added_context", []).extend(pending)
        self.emit("stage_done", stage="extract", output=case_obj)

        # ADVOCATE ----------------------------------------------------------
        self._drain_notes(case_obj)
        self.emit("stage_start", stage="advocate", label="Advocate Agent",
                  detail="Building the strongest consumer case (CPA 2019)…")
        adv = self._retry(lambda: advocate(case_obj))
        self.emit("stage_done", stage="advocate", output=adv)

        # DEFENSE ------------------------------------------------------------
        self._drain_notes(case_obj)
        self.emit("stage_start", stage="defense", label="Defense Agent",
                  detail="Cross-examining as company counsel…")
        dfs = self._retry(lambda: defense(case_obj, adv))
        self.emit("stage_done", stage="defense", output=dfs)

        # ARBITER -------------------------------------------------------------
        self._drain_notes(case_obj)
        self.emit("stage_start", stage="arbiter", label="Arbiter Agent",
                  detail="Scoring both sides, routing the case…")
        arb = self._retry(lambda: arbiter(case_obj, adv, dfs))
        self.emit("stage_done", stage="arbiter", output=arb)

        decision = (arb.get("routing_decision") or arb.get("decision") or "").lower()
        if "insufficient" in decision or "reframe" in decision:
            why = arb.get("suggested_reframe") or arb.get("what_is_needed") or arb.get("reasoning", "")
            label = ("Arbiter: evidence too weak to file. " if "insufficient" in decision
                     else "Arbiter: case should be reframed before filing. ")
            self.emit("needs_user", stage="arbiter", message=label + str(why))
            self.emit("complete", summary={
                "decision": arb.get("routing_decision"),
                "confidence": arb.get("net_confidence_percent"),
                "channel": "held — your input needed"})
            return

        # FILING ---------------------------------------------------------------
        self._drain_notes(case_obj)
        self.emit("stage_start", stage="filing", label="Filing Agent",
                  detail="Staging complaint form for the chosen portal (stops before submit)…")
        fil = self._retry(lambda: filing(case_obj, arb, adv))
        self.emit("stage_done", stage="filing", output=fil)

        # PORTAL — real Gemini Computer Use (skipped on revisions) ---------------
        if self.revise_of is None:
            self.emit("stage_start", stage="portal", label="Portal Agent · Computer Use",
                      detail="Gemini Computer Use driving a live browser on consumerhelpline.gov.in…")
            from app.browser_filing import run_portal_session
            case_line = (f"{(case_obj.get('product') or {}).get('name', 'product')}, "
                         f"defect: {(case_obj.get('defect') or {}).get('description', '')}. "
                         f"SLA breach: {(case_obj.get('sla_analysis') or {}).get('sla_breached')}")
            portal = run_portal_session(self.emit, case_line)
            self.emit("stage_done", stage="portal", output=portal)
        else:
            self.emit("stage_done", stage="portal", output={
                "portal_session": "already_staged",
                "note": "Portal form already staged in the original run; "
                        "updated draft carries the correction."})
        self.emit("needs_user", stage="portal",
                  message="Form staged on the live portal. Human approval required before submission.",
                  action="approve_submit")

        # MONITORING --------------------------------------------------------------
        self._drain_notes(case_obj)
        self.emit("stage_start", stage="monitor", label="Monitoring Agent",
                  detail="Setting up 24/7 SLA tracking and auto-escalation…")
        mon = self._retry(lambda: monitor(case_obj, fil, today))
        self.emit("stage_done", stage="monitor", output=mon)

        self.emit("complete", summary={
            "decision": arb.get("routing_decision") or arb.get("decision"),
            "confidence": arb.get("net_confidence_percent") or arb.get("confidence"),
            "channel": arb.get("channel_choice"),
        })

    # ------------------------------------------------------- gather evidence
    def _gather(self):
        """Intent -> inbox -> evidence assembly. Returns issue text or None."""
        self.emit("stage_start", stage="intent", label="Intake Agent",
                  detail="Understanding your request…")
        intent = llm_json(INTENT_PROMPT, f'User said: "{self.command}"')
        self.emit("stage_done", stage="intent", output=intent)

        terms = intent.get("search_terms") or intent.get("brands") or ["warranty"]
        self.emit("stage_start", stage="inbox", label="Gmail Retrieval",
                  detail=f"Searching inbox for: {', '.join(terms)}",
                  mode=self.inbox.mode)
        emails = self.inbox.search(terms)
        preview = [{k: m[k] for k in ("id", "thread_id", "from", "date", "subject")}
                   for m in emails]
        self.emit("stage_done", stage="inbox", output={
            "matched": len(emails), "emails": preview, "mode": self.inbox.mode})
        if not emails:
            self.emit("needs_user", stage="inbox",
                      message="No matching emails found. Try different keywords or forward the thread.")
            return None

        self.emit("stage_start", stage="evidence", label="Evidence Assembly",
                  detail="Separating invoice, support thread and noise…")
        threads: Dict[str, List[dict]] = {}
        for m in emails:
            threads.setdefault(m["thread_id"], []).append(m)
        support_txt, receipt_txt = [], []
        for tid in threads:
            full = self.inbox.get_thread(tid)
            for m in sorted(full, key=lambda x: str(x["date"])):
                block = (f"From: {m['from']}\nDate: {m['date']}\n"
                         f"Subject: {m['subject']}\n\n{m['body']}")
                low = (m["subject"] + m["body"]).lower()
                if any(w in low for w in ("order", "invoice", "delivered", "amount paid")):
                    receipt_txt.append(block)
                else:
                    support_txt.append(block)
        self.evidence = (receipt_txt, support_txt)
        self.emit("stage_done", stage="evidence", output={
            "threads": len(threads),
            "receipt_msgs": len(receipt_txt),
            "support_msgs": len(support_txt)})
        return intent.get("issue") or "See support thread"

    @staticmethod
    def _retry(fn, attempts: int = 3):
        last = None
        for i in range(attempts):
            try:
                return fn()
            except Exception as e:
                last = e
                time.sleep(2 * (i + 1))
        raise last
