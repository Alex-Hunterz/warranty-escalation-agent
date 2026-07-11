"""
Agent 6: Monitoring
Tracks case over days/weeks. Auto-escalates when SLAs breached.
Runs unattended on timer (day 1, 11, 20, 30, etc).
Solves: "companies bet you'll get tired" problem.
"""
import json
from datetime import datetime
from src.core import call_llm, safe_json_parse

MONITORING_PROMPT = """You are a case manager tracking a warranty complaint over time.

INPUT: Filing details + SLA windows + case metadata + current date.

YOUR JOB: Track progress and flag when escalation is needed.

TRACKING STAGES:
1. Company's own SLA (extracted from original communication):
   - Company promised 'X days' to resolve
   - Track actual days elapsed
   - Day X+1 → Flag "company breached its own SLA" (this is evidence for later)

2. Post-NCH filing:
   - NCH nodal officer should respond within ~15 days (informal SLA)
   - Day 20 with no response? Suggest escalation to e-Jagriti
   - Track: Has company responded? Has NCH escalated?

3. Post-order (if e-Jagriti issued an order):
   - Company has 30 days to comply (refund/replacement)
   - Day 31 with no payment? Auto-draft EXECUTION PETITION
   - Execution petition forces payment via property attachment or garnishee

4. Post-appeal (if company appeals the order):
   - Company must pre-deposit 50% of awarded amount within 45 days
   - If 45 days passed without pre-deposit, appeal is void, original order stands
   - Flag this for user

RETURN FORMAT (JSON):
{
  "current_stage": "company_sla_tracking / post_nch_waiting / post_order_compliance / post_appeal_tracking",
  "days_elapsed": 21,
  "alerts": [
    {
      "severity": "HIGH / MEDIUM / LOW",
      "alert": "Company breached its own 7-day SLA (now day 21)",
      "action_needed": "None (auto-tracked), but this strengthens case for deficiency-of-service"
    },
    ...
  ],
  "escalation_needed": true/false,
  "auto_drafts": {
    "execution_petition": null or "Full draft of execution petition to file if order not complied",
    "escalation_to_ejagriti": null or "Text for escalating from NCH to e-Jagriti filing"
  },
  "next_check_date": "YYYY-MM-DD",
  "user_notifications": [
    "Message to send to user (SMS/email style)"
  ],
  "case_status_summary": "Human-readable status (e.g., 'Day 21: Company missed SLA, case strong for e-Jagriti filing')"
}

EXECUTION PETITION TEMPLATE (if needed):
- This is filed with the same District Commission that issued the order
- Text should reference: order ID, order date, required compliance date, actual payment date (none = non-compliant)
- Request: attachment of company property, garnishee of bank accounts, or Section 72 criminal prosecution
- Tone: firm, factual, no emotion

ESCALATION TO E-JAGRITI (if needed from NCH):
- If NCH filing was made but no company response after 20 days
- Then file at e-Jagriti as escalation (formal consumer court)
- Reference NCH filing ID in e-Jagriti complaint
- This accelerates the timeline (e-Jagriti has 30-day admission SLA)
"""

def monitor(case_obj: dict, filing_data: dict, current_date_str: str = None) -> dict:
    """
    Monitor case progression. Triggers escalation logic.

    case_obj: Original extracted case
    filing_data: Result from filing_agent (filing IDs, SLA windows, etc)
    current_date_str: Current date (format: YYYY-MM-DD). If None, use today.
    """
    from datetime import datetime

    if current_date_str is None:
        current_date_str = datetime.now().isoformat()

    user_message = f"""
ORIGINAL CASE:
{json.dumps(case_obj, indent=2)}

FILING DATA:
{json.dumps(filing_data, indent=2)}

TODAY'S DATE: {current_date_str}

Track this case progression. Check for SLA breaches and escalation triggers.
Return valid JSON only.
"""

    response_text = call_llm(MONITORING_PROMPT, user_message, response_format="json")
    result = safe_json_parse(response_text)

    return result
