"""
Agent 5: Filing
Autonomously fills government forms (NCH/e-Jagriti).
STOPS before submit for human approval (safety boundary).
"""
import json
from datetime import datetime, timedelta
from src.core import call_llm, safe_json_parse

FILING_PROMPT = """You are a legal filing assistant. Your job: prepare forms for government portals.

INPUT: Arbiter's routing decision + full case + drafted complaint.

YOUR JOB: Structure the form data that WOULD BE SUBMITTED to the government portal.

IF CHANNEL = NCH (consumerhelpline.gov.in):
- State: Auto-select from case data
- Company Name: Extract from case
- Sector: E-commerce / Furniture / Electronics / etc (infer from product)
- Nature: Warranty claim / Manufacturing defect / Deficiency-of-service / etc
- Relief Sought: Refund amount + compensation
- Complaint Text: Use Advocate's draft
- Evidence: List (receipt, photos, chat thread)
- Contact: Phone, email from case

IF CHANNEL = E-JAGRITI (e-daakhil.gov.in):
- Commission Level: Select based on claim value
  - District Commission: Claims up to ₹50 lakh
  - State Commission: Claims ₹50L - ₹2 crore
  - National Commission: Claims above ₹2 crore
- Party Details: Consumer vs Company
- Nature of Dispute: Formal legal claim
- Relief Sought: Amount
- Jurisdiction: Where product was purchased / where company registered / where consumer resides (pick strongest)
- Affidavit Draft: Generate text for user to get notarized separately

RETURN FORMAT (JSON):
{
  "portal": "NCH / E-Jagriti",
  "form_data": {
    "state": "state_code",
    "company_name": "...",
    "sector": "...",
    "nature": "...",
    "relief_amount": 45500,
    "complaint_text": "...",
    "evidence": ["receipt", "defect_photo", "chat_thread"],
    ...
    // Other fields specific to portal
  },
  "affidavit_text": null or "Text for user to notarize and attach (e-Jagriti only)",
  "sla_window": "15 days for NCH response / 30 days for e-Jagriti admission",
  "next_step": "Human clicks Submit to file / e-Jagriti: After getting affidavit notarized, return to file",
  "filing_checklist": ["receipt ✓", "defect_photo ✓", "chat_thread ✓"],
  "ready_to_submit": true/false  // All required docs present?
}

CRITICAL RULES:
1. Don't actually submit. Just structure what WOULD be submitted.
2. If any required evidence is missing, set ready_to_submit=false and flag in checklist.
3. SLA windows: NCH ~15 days, e-Jagriti ~30 days admission (then hearing).
4. For e-Jagriti affidavit, generate realistic legal text that consumer can get notarized.
"""

def filing(case_obj: dict, arbiter_decision: dict, advocate_draft: dict) -> dict:
    """
    Prepare filing forms. Stops before submit.
    In real system, this would use Selenium/Playwright. For demo, we mock the form structure.
    """
    channel = arbiter_decision.get("channel_choice", "NCH-first")

    user_message = f"""
CASE DATA:
{json.dumps(case_obj, indent=2)}

ARBITER'S ROUTING DECISION:
{json.dumps(arbiter_decision, indent=2)}

ADVOCATE'S DRAFT:
{json.dumps(advocate_draft, indent=2)}

Prepare filing form data for portal: {channel}
Do NOT submit. Just structure the form.
Return valid JSON only.
"""

    response_text = call_llm(FILING_PROMPT, user_message, response_format="json")
    result = safe_json_parse(response_text)

    # Add metadata
    result["timestamp"] = datetime.now().isoformat()
    result["status"] = "pending_human_approval"

    # Calculate SLA window
    today = datetime.now()
    if channel == "NCH-first" or "NCH" in channel:
        result["sla_response_deadline"] = (today + timedelta(days=15)).isoformat()
    else:
        result["sla_response_deadline"] = (today + timedelta(days=30)).isoformat()

    return result
