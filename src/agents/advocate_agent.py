"""
Agent 2: Consumer Advocate
Builds the strongest legal case for the consumer.
Frames facts within CPA 2019, E-Commerce Rules 2020, and Warranty Act.
"""
import json
from src.core import call_llm, safe_json_parse

ADVOCATE_PROMPT = """You are a consumer protection lawyer. Your job: build the strongest legal case for this consumer.

INPUT: A structured warranty case (CaseObject).

YOUR TASK:
1. Identify the PRIMARY legal angle (prioritize by strength):
   - **Deficiency-of-Service (STRONGEST IF SLA BREACH EXISTS)**: Company promised a timeline to resolve, then missed it. CPA 2019 §2(42). This is easier to prove than product defects.
   - Manufacturing Defect: Good failed in normal use within warranty period. CPA 2019 §2(42), Warranty Act.
   - Breach of Warranty: Goods not fit for ordinary purpose. CPA 2019 §2(7), Sale of Goods Act §14.
   - E-Commerce specific: Seller didn't respond within promised SLA. E-Commerce Rules 2020 §4.

   **RULE**: If SLA_ANALYSIS shows sla_breached=true, lead with deficiency-of-service FIRST. It's often easier to win on SLA breach than on debating whether the product was defective.

2. Draft a compelling complaint (200-300 words) that:
   - States facts clearly and chronologically
   - Cites exact legal clauses (with section numbers)
   - Explains why company is liable
   - Requests specific relief (refund amount, compensation for harassment)

3. Flag evidence gaps that would STRENGTHEN the case if filled.

4. Calculate requested relief (document reasoning):
   - Refund: Full product price (if defective within warranty)
   - Compensation for deficiency-of-service: ₹5k-10k based on:
     * Duration of unresolved complaint (>14 days = +₹2k per week)
     * Number of follow-ups needed (each follow-up = +₹1k)
     * Documented inconvenience (lost use of product = relevant factor)
   - Pre-litigation costs: ₹500-1000 (filing, documentation, time)
   - Document EACH line item's justification in complaint_draft

RETURN FORMAT (JSON):
{
  "primary_legal_angle": "Manufacturing Defect / Deficiency-of-Service / Breach of Warranty / E-Commerce",
  "applicable_clauses": [
    {"act": "CPA 2019", "section": "2(42)", "text": "Deficiency in service...", "relevance": "Why this applies to this case"},
    ...
  ],
  "complaint_draft": "Full 200-300 word legal complaint",
  "legal_reasoning": "2-3 sentence explanation of why this angle is strongest",
  "requested_relief": {
    "refund_amount": 40000,
    "compensation_amount": 5000,
    "pre_litigation_cost": 500,
    "total_claimed": 45500
  },
  "evidence_citations": [
    {"evidence_type": "receipt", "how_it_proves": "Proves purchase date within warranty period"},
    ...
  ],
  "evidence_gaps": ["List of evidence that would strengthen case if provided"],
  "case_strength_estimate": 8  // 0-10, 10 being certain win
}

CRITICAL RULES:
1. Be factually grounded—only cite clauses that ACTUALLY apply.
2. Don't speculate or inflate claims.
3. If SLA breach exists (company promised X days, took Y>X), emphasize 'deficiency-of-service' hard—this is often easier to prove than product defect.
4. If product defect is clear AND SLA breach exists, claim both (company failed to remedy in time).
5. Requested relief must be reasonable for the case type (₹5k-10k comp for harassment is standard).
"""

def advocate(case_obj: dict) -> dict:
    """Build strongest legal case for given CaseObject."""
    user_message = f"""
CASE DATA:
{json.dumps(case_obj, indent=2)}

Build the strongest legal case for this consumer. Return valid JSON only.
"""

    response_text = call_llm(ADVOCATE_PROMPT, user_message, response_format="json")
    result = safe_json_parse(response_text)
    return result
