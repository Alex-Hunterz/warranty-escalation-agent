"""
Phase 2: Antigravity Orchestrator
Bridges local agents to Google's Managed Agents framework.

In production: These calls would go to Antigravity API.
For hackathon: Local simulation + API wrapper ready for deployment.
"""

import json
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from src.agents.extraction_agent import extract_case
from src.agents.advocate_agent import advocate
from src.agents.defense_agent import defense
from src.agents.arbiter_agent import arbiter
from src.agents.filing_agent import filing
from src.agents.monitoring_agent import monitor

class AntigravityOrchestrator:
    """
    Manages multi-agent workflow with persistent state.

    Flow:
    1. Client submits raw case → Extraction Agent
    2. Extraction returns CaseObject → stored in state
    3. Advocate + Defense called in parallel on CaseObject
    4. Arbiter receives all three outputs, makes routing decision
    5. If "ready_to_file": Filing Agent called
    6. Monitoring Agent scheduled on timer (day 1, 11, 20, 30)
    """

    def __init__(self, case_id: str = None):
        self.case_id = case_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.state = {
            "case_id": self.case_id,
            "case_obj": None,
            "advocate_draft": None,
            "defense_draft": None,
            "arbiter_decision": None,
            "filing_data": None,
            "monitoring_updates": [],
            "workflow_stage": "init"
        }
        self.created_at = datetime.now().isoformat()
        self.callbacks = {
            "on_stage_complete": [],
            "on_escalation": [],
            "on_error": []
        }

    def register_callback(self, event: str, callback):
        """Register callback for workflow events."""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def emit_event(self, event: str, data: Dict[str, Any]):
        """Fire callbacks for workflow events."""
        for cb in self.callbacks.get(event, []):
            cb(data)

    def stage_1_extraction(self, case_input: Dict[str, str]) -> Dict[str, Any]:
        """
        Stage 1: Extract case from raw input.

        Input: {receipt_text, chat_thread, defect_description, defect_date, defect_photos_count}
        Output: CaseObject (structured)
        """
        print(f"\n[ANTIGRAVITY] Stage 1: Extraction Agent")
        print(f"  Case ID: {self.case_id}")

        try:
            self.state["case_obj"] = extract_case(case_input)
            self.state["workflow_stage"] = "extraction_complete"

            self.emit_event("on_stage_complete", {
                "stage": "extraction",
                "case_id": self.case_id,
                "sla_breached": self.state["case_obj"].get("sla_analysis", {}).get("sla_breached")
            })

            return {
                "status": "success",
                "case_obj": self.state["case_obj"],
                "next_stage": "parallel_debate"
            }
        except Exception as e:
            self.emit_event("on_error", {"stage": "extraction", "error": str(e)})
            raise

    def stage_2_parallel_debate(self) -> Dict[str, Any]:
        """
        Stage 2: Advocate and Defense analyze in parallel.

        In Antigravity: Uses LLM_CALL tool to invoke agents in parallel.
        Here: Sequential (but could be parallelized with threading).
        """
        print(f"\n[ANTIGRAVITY] Stage 2: Parallel Debate")
        print(f"  Advocate Agent: analyzing...")

        try:
            # Call Advocate
            self.state["advocate_draft"] = advocate(self.state["case_obj"])
            adv_score = self.state["advocate_draft"].get("case_strength_estimate", "N/A")

            # Call Defense
            print(f"  Defense Agent: analyzing...")
            self.state["defense_draft"] = defense(self.state["case_obj"], self.state["advocate_draft"])
            def_score = self.state["defense_draft"].get("case_strength_estimate_for_company", "N/A")

            self.state["workflow_stage"] = "debate_complete"

            self.emit_event("on_stage_complete", {
                "stage": "debate",
                "case_id": self.case_id,
                "advocate_score": adv_score,
                "defense_score": def_score
            })

            return {
                "status": "success",
                "advocate_score": adv_score,
                "defense_score": def_score,
                "next_stage": "arbiter_routing"
            }
        except Exception as e:
            self.emit_event("on_error", {"stage": "debate", "error": str(e)})
            raise

    def stage_3_arbiter_routing(self) -> Dict[str, Any]:
        """
        Stage 3: Arbiter scores and routes.

        Routing decision: insufficient_evidence / reframe / ready_to_file
        """
        print(f"\n[ANTIGRAVITY] Stage 3: Arbiter Routing")

        try:
            self.state["arbiter_decision"] = arbiter(
                self.state["case_obj"],
                self.state["advocate_draft"],
                self.state["defense_draft"]
            )

            routing = self.state["arbiter_decision"].get("routing_decision", "unknown")
            confidence = self.state["arbiter_decision"].get("net_confidence_percent", 0)

            self.state["workflow_stage"] = "arbiter_complete"

            print(f"  Confidence: {confidence}%")
            print(f"  Decision: {routing}")

            self.emit_event("on_stage_complete", {
                "stage": "arbiter",
                "case_id": self.case_id,
                "confidence": confidence,
                "routing": routing
            })

            # Branching logic
            if routing == "insufficient_evidence":
                return {
                    "status": "insufficient_evidence",
                    "message": "More evidence needed. Loop back to Extraction.",
                    "next_action": "request_user_for_more_evidence"
                }
            elif routing == "reframe":
                return {
                    "status": "reframe_suggested",
                    "suggested_angle": self.state["arbiter_decision"].get("suggested_reframe", "N/A"),
                    "next_action": "re_call_advocate_with_new_angle"
                }
            else:  # ready_to_file
                return {
                    "status": "ready_to_file",
                    "confidence": confidence,
                    "channel": self.state["arbiter_decision"].get("channel_choice", "NCH-first"),
                    "next_stage": "filing"
                }
        except Exception as e:
            self.emit_event("on_error", {"stage": "arbiter", "error": str(e)})
            raise

    def stage_4_filing(self) -> Dict[str, Any]:
        """
        Stage 4: File at government portal.

        In Antigravity: Uses BROWSER_TOOL to interact with gov sites.
        Here: Returns form data structure (actual filing simulated).
        """
        print(f"\n[ANTIGRAVITY] Stage 4: Filing Agent")

        channel = self.state["arbiter_decision"].get("channel_choice", "NCH-first")
        print(f"  Channel: {channel}")
        print(f"  Staging form...")

        try:
            self.state["filing_data"] = filing(
                self.state["case_obj"],
                self.state["arbiter_decision"],
                self.state["advocate_draft"]
            )

            self.state["workflow_stage"] = "filing_staged"

            self.emit_event("on_stage_complete", {
                "stage": "filing",
                "case_id": self.case_id,
                "portal": self.state["filing_data"].get("portal"),
                "status": "pending_human_approval"
            })

            return {
                "status": "pending_human_approval",
                "portal": self.state["filing_data"].get("portal"),
                "form_ready": True,
                "message": "Form staged. Human approves submit.",
                "next_action": "human_clicks_submit"
            }
        except Exception as e:
            self.emit_event("on_error", {"stage": "filing", "error": str(e)})
            raise

    def human_approves_submit(self) -> Dict[str, Any]:
        """
        Simulates human clicking Submit on the staged form.
        In Antigravity: This would trigger BROWSER_TOOL to submit the form.
        """
        print(f"\n[ANTIGRAVITY] Human Gate: Submit Approved")

        # Simulate form submission
        self.state["filing_data"]["status"] = "submitted"
        self.state["filing_data"]["filing_id"] = f"NCH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.state["workflow_stage"] = "filed"

        self.emit_event("on_stage_complete", {
            "stage": "filed",
            "case_id": self.case_id,
            "filing_id": self.state["filing_data"].get("filing_id")
        })

        return {
            "status": "filed",
            "filing_id": self.state["filing_data"].get("filing_id"),
            "sla_deadline": self.state["filing_data"].get("sla_response_deadline"),
            "next_stage": "monitoring"
        }

    def stage_5_schedule_monitoring(self, start_date: str = None) -> Dict[str, Any]:
        """
        Stage 5: Schedule Monitoring Agent on timer.

        In Antigravity: Uses TIMER_TRIGGER to schedule agent at: day 1, 11, 20, 30
        Here: Returns monitoring schedule and first check.
        """
        print(f"\n[ANTIGRAVITY] Stage 5: Schedule Monitoring")

        # Determine check dates
        if start_date:
            base_date = datetime.fromisoformat(start_date)
        else:
            base_date = datetime.now()

        check_schedule = [
            base_date + timedelta(days=1),   # Day 1: Initial check
            base_date + timedelta(days=11),  # Day 11: Company SLA check
            base_date + timedelta(days=20),  # Day 20: NCH response check
            base_date + timedelta(days=30),  # Day 30: Post-order compliance check (if applicable)
        ]

        self.state["monitoring_schedule"] = [d.isoformat() for d in check_schedule]
        self.state["workflow_stage"] = "monitoring_scheduled"

        self.emit_event("on_stage_complete", {
            "stage": "monitoring_scheduled",
            "case_id": self.case_id,
            "check_dates": self.state["monitoring_schedule"]
        })

        return {
            "status": "monitoring_scheduled",
            "check_dates": self.state["monitoring_schedule"],
            "message": "Monitoring active. Case tracked for SLA breaches and escalation triggers.",
            "next_action": "monitoring_runs_on_schedule"
        }

    def run_monitoring_check(self, check_date: str) -> Dict[str, Any]:
        """
        Simulate a monitoring check at a specific date.
        In Antigravity: Called by TIMER_TRIGGER.
        """
        print(f"\n[ANTIGRAVITY] Monitoring Check: {check_date}")

        try:
            update = monitor(self.state["case_obj"], self.state["filing_data"], current_date_str=check_date)
            self.state["monitoring_updates"].append({
                "check_date": check_date,
                "result": update
            })

            alerts = update.get("alerts", [])
            if alerts:
                self.emit_event("on_escalation", {
                    "stage": "monitoring",
                    "check_date": check_date,
                    "alerts": alerts
                })

            return {
                "status": "check_complete",
                "check_date": check_date,
                "alerts": len(alerts),
                "escalation_needed": update.get("escalation_needed", False),
                "auto_drafts": update.get("auto_drafts", {})
            }
        except Exception as e:
            self.emit_event("on_error", {"stage": "monitoring_check", "error": str(e)})
            raise

    def run_full_workflow(self, case_input: Dict[str, str]) -> Dict[str, Any]:
        """
        Run complete workflow end-to-end (for demo/testing).
        In production: Stages would run async with callbacks.
        """
        print(f"\n{'='*70}")
        print(f"ANTIGRAVITY ORCHESTRATION: Full Workflow")
        print(f"Case ID: {self.case_id}")
        print(f"{'='*70}")

        # Stage 1: Extraction
        self.stage_1_extraction(case_input)

        # Stage 2: Debate
        self.stage_2_parallel_debate()

        # Stage 3: Routing
        routing_result = self.stage_3_arbiter_routing()

        # Handle routing branches
        if routing_result["status"] != "ready_to_file":
            print(f"\nWorkflow stopped: {routing_result['status']}")
            return {
                "status": routing_result["status"],
                "state": self.state,
                "message": routing_result.get("message", "No file decision")
            }

        # Stage 4: Filing
        self.stage_4_filing()

        # Human approval simulation
        print(f"\n[SIMULATE] Human approves form submit...")
        self.human_approves_submit()

        # Stage 5: Monitoring
        self.stage_5_schedule_monitoring()

        # Simulate monitoring checks
        print(f"\n[SIMULATE] Running monitoring checks...")
        for check_date in [
            datetime.now().isoformat(),
            (datetime.now() + timedelta(days=11)).isoformat(),
        ]:
            self.run_monitoring_check(check_date)

        return {
            "status": "workflow_complete",
            "case_id": self.case_id,
            "state": self.state,
            "message": "Full workflow executed successfully"
        }

    def export_state(self) -> str:
        """Export current state as JSON (for persistence/export)."""
        return json.dumps(self.state, indent=2, default=str)

    def get_summary(self) -> Dict[str, Any]:
        """Get readable summary of workflow."""
        return {
            "case_id": self.case_id,
            "workflow_stage": self.state["workflow_stage"],
            "product": self.state["case_obj"].get("product", {}).get("name") if self.state["case_obj"] else None,
            "sla_breached": self.state["case_obj"].get("sla_analysis", {}).get("sla_breached") if self.state["case_obj"] else None,
            "advocate_score": self.state["advocate_draft"].get("case_strength_estimate") if self.state["advocate_draft"] else None,
            "defense_score": self.state["defense_draft"].get("case_strength_estimate_for_company") if self.state["defense_draft"] else None,
            "arbiter_confidence": self.state["arbiter_decision"].get("net_confidence_percent") if self.state["arbiter_decision"] else None,
            "filing_status": self.state["filing_data"].get("status") if self.state["filing_data"] else None,
            "monitoring_alerts": sum(1 for u in self.state["monitoring_updates"] for _ in u.get("result", {}).get("alerts", []))
        }
