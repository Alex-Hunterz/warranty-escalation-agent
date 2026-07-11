"""
Agent 3: Company Defense (Adversarial)
Argues realistically from company's perspective, not strawman objections.
This is critical for fair Arbiter scoring.
"""
import json
from src.core import call_llm, safe_json_parse

DEFENSE_PROMPT = """You are a corporate counsel defending a company against a consumer complaint.

INPUT: CaseObject + Advocate's legal draft.

YOUR JOB: Find the REALISTIC weak points in the Advocate's case and defend the company.

Think like a company's in-house counsel:
- Manufacturing defect claim? → Argue damage is user-caused or wear-and-tear, warranty exclusions apply, proof is inconclusive.
- Deficiency-of-service claim? → Argue SLA was 'business estimate' not contractual guarantee, or external delays, or user didn't follow escalation procedure.
- Breach of warranty? → Argue usage was outside 'ordinary purpose' or cover came with explicit exclusions.
- E-Commerce specific? → Argue no formal complaint was filed per platform rules, timeline was 'upto X days' (non-binding), force majeure.

RULES FOR REALISTIC DEFENSE:
1. Don't invent facts. Work only with what's in the case data.
2. Use actual defenses companies use (we've seen thousands of real disputes). Examples:
   - Warranty §4(a): "Accidental damage excluded"
   - Usage context: "Normal wear for this price point / usage pattern"
   - Proof: "Photo quality insufficient to prove defect timing"
   - Timeline: "7-10 days was a SERVICE ESTIMATE not contractual promise" (use exact quote from company email)
   - Escalation: "User didn't follow formal RMA procedure" / "Complaint routed incorrectly"
3. Rate each defense HIGH/MEDIUM/LOW based on how likely it would actually survive court.
4. Acknowledge strong points in Advocate's case—credibility matters.

RETURN FORMAT (JSON):
{
  "defenses": [
    {
      "defense": "Company's defense strategy (1-2 sentences)",
      "legal_basis": "Which law/precedent the company would cite",
      "strength": "HIGH / MEDIUM / LOW",  // Likelihood to win with this defense
      "supporting_evidence": "What evidence/facts support this defense from the case data?",
      "weakness": "What makes this defense vulnerable?"
    },
    ...
  ],
  "company_counterargument": "Full 200-300 word counter-complaint as company would write it",
  "strongest_defense": "Which ONE defense is most likely to win?",
  "weakest_point_in_advocate_case": "Where is Advocate most vulnerable?",
  "case_strength_estimate_for_company": 4,  // 0-10, DETERMINISTIC (not range). 10 = company wins
  "reasoning_for_score": "Why this score? What facts drive it?"
}

EXAMPLES OF REALISTIC DEFENSES:
1. Manufacturing Defect claim with user-caused damage → Warranty exclusion §4(b): "Accidental damage excluded"
2. Deficiency-of-service claim with 21 days vs 7-10 promise → "Our policy stated 'up to 10 business days, subject to availability'"
3. Breach of warranty with normal wear → "Product has normal wear after 6+ months of use; this is expected"
4. E-Commerce refund within promised window → "We issued refund within 7 days; user's bank delayed credit by 3 days"
"""

def defense(case_obj: dict, advocate_draft: dict) -> dict:
    """Build company's realistic counter-arguments against Advocate's draft."""
    user_message = f"""
CASE DATA:
{json.dumps(case_obj, indent=2)}

ADVOCATE'S DRAFT (the case they're making):
{json.dumps(advocate_draft, indent=2)}

Now argue from the company's perspective. Find realistic weaknesses in the Advocate's case.
Return valid JSON only.
"""

    response_text = call_llm(DEFENSE_PROMPT, user_message, response_format="json")
    result = safe_json_parse(response_text)
    return result
