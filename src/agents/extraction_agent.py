"""
Agent 1: Extraction
Parses raw case data (receipt, chat threads, photos) into structured CaseObject.
CRITICAL: Extract company's own SLA promises—this drives escalation logic.
"""
import json
from src.core import call_llm, safe_json_parse

EXTRACTION_PROMPT = """You are a legal case analyst. Extract all relevant facts from a consumer warranty claim.

The user will provide:
1. Product receipt/invoice (text or description)
2. Warranty card details (text or description)
3. Defect description and when first noticed
4. Email/chat thread with company support (full thread)
5. Photos of defect (descriptions)

YOUR JOB: Extract and structure into JSON with these EXACT keys:

{
  "product": {
    "name": "Product name",
    "model": "Model/variant if applicable",
    "price": 40000,  // in INR
    "purchase_date": "YYYY-MM-DD",
    "purchase_channel": "Amazon/Flipkart/Direct/etc",
    "serial_number": "if available"
  },
  "warranty": {
    "period_months": 24,
    "type": "Manufacturer/Seller/Both",
    "expiry_date": "YYYY-MM-DD"
  },
  "defect": {
    "description": "Clear, specific description of what's wrong",
    "date_first_noticed": "YYYY-MM-DD",
    "severity": "Critical/High/Medium/Low",
    "usage_context": "Was the product used normally when defect occurred?"
  },
  "company_communication": [
    {
      "date": "YYYY-MM-DD",
      "direction": "user_to_company / company_to_user",
      "summary": "What was said",
      "sla_promise": "If company promised a timeline, extract it exactly here. Otherwise null.",
      "response_days_from_previous": "Days between this and last message from other party"
    }
  ],
  "sla_analysis": {
    "company_promised_days": "What's the company's stated resolution timeline? (e.g., '7-10 business days')",
    "days_promised": 10,  // Convert 'up to X days' to integer
    "actual_days_elapsed": 21,  // Days from first complaint to now (or last company message)
    "sla_breached": true,  // true if actual > promised
    "sla_breach_evidence": "Quote from company's email promising timeline"
  },
  "evidence": [
    {"type": "receipt", "status": "Available/Missing"},
    {"type": "warranty_card", "status": "Available/Missing"},
    {"type": "defect_photo", "count": 3, "status": "Available"},
    {"type": "chat_thread", "status": "Complete/Partial"}
  ],
  "data_quality": {
    "complete": true/false,  // All critical fields present?
    "missing_for_strong_case": ["List of evidence gaps that weaken the case"]
  }
}

CRITICAL RULES:
1. Extract company's SLA promise EXACTLY as they wrote it. This will be used to prove 'deficiency-of-service' later.
2. If company promised '7-10 business days,' calculate 10 days and check if actual elapsed time exceeds it.
3. If any field is not in the provided data, set to null and flag in missing_for_strong_case.
4. dates: Use YYYY-MM-DD format. If only month/year given, infer end of month.
5. response_days: Only count if there's a clear gap between company's message and user's follow-up.

Return ONLY valid JSON, no other text."""

def extract_case(case_data: dict) -> dict:
    """
    Extract structured case from raw input.

    case_data keys:
    - receipt_text: Invoice/receipt text
    - warranty_text: Warranty card details
    - defect_description: What's wrong
    - defect_date: When first noticed (YYYY-MM-DD or descriptive)
    - chat_thread: Full email/support chat history
    - defect_photos_count: Number of photos (we can't parse images directly, just count)

    Returns: CaseObject (dict) with structured data
    """
    user_message = f"""
Please extract case data from the following:

RECEIPT/INVOICE:
{case_data.get('receipt_text', 'Not provided')}

WARRANTY CARD:
{case_data.get('warranty_text', 'Not provided')}

DEFECT:
{case_data.get('defect_description', 'Not provided')}
Date first noticed: {case_data.get('defect_date', 'Not provided')}
Photos available: {case_data.get('defect_photos_count', 0)} photo(s)

SUPPORT CHAT THREAD:
{case_data.get('chat_thread', 'Not provided')}

TODAY'S DATE (for calculating elapsed days): {case_data.get('today_date', '2025-07-26')}
"""

    response_text = call_llm(EXTRACTION_PROMPT, user_message, response_format="json")
    result = safe_json_parse(response_text)
    return result
