"""
ACTUAL Antigravity Agent Definitions
Ready to deploy to Google AI Studio.

This module defines agents that can be orchestrated via Managed Agents.
Each agent is a complete, deployable unit.
"""

import json
from typing import Dict, Any, Optional
from src.core import call_llm, safe_json_parse

# ============================================================================
# AGENT 1: Extraction Agent
# ============================================================================

class ExtractionAgent:
    """Parse case data into structured CaseObject."""

    SYSTEM_PROMPT = """You are a Case Extraction Agent for consumer warranty disputes.
Your role: Parse unstructured warranty case data into a structured CaseObject.

TASK:
1. Extract product details (name, model, serial, purchase date)
2. Identify defect/issue (type, date discovered, severity)
3. Extract timeline (purchase → defect → first contact → escalations)
4. Parse company communication (promises, SLAs, responses)
5. Identify evidence (receipts, photos, support tickets, emails)
6. Calculate days elapsed since purchase

OUTPUT: Return only valid JSON with these fields:
{
  "product": {"name": string, "model": string, "serial": string, "price": float, "purchase_date": string},
  "defect": {"description": string, "date_discovered": string, "severity": "high|medium|low"},
  "timeline": [{"date": string, "event": string}],
  "company": {"name": string, "contact": string, "promises": [string]},
  "evidence": [{"type": "receipt|photo|ticket|email", "description": string}],
  "current_status": string,
  "days_elapsed": int,
  "sla_breaches": [{"promised": string, "actual": string, "days_overdue": int}]
}"""

    def __init__(self, model: str = "gemini-3.5-flash"):
        self.model = model
        self.name = "extraction_agent"

    def run(self, case_input: Dict[str, Any]) -> Dict[str, Any]:
        """Extract case from raw input."""
        prompt = f"""
Extract warranty case details:

{json.dumps(case_input, indent=2)}

Return structured CaseObject as JSON."""

        response = call_llm(self.SYSTEM_PROMPT, prompt, response_format="json")
        case_obj = safe_json_parse(response)
        case_obj["extraction_model"] = self.model
        case_obj["agent"] = "extraction_agent"
        return case_obj


# ============================================================================
# AGENT 2: Advocate Agent
# ============================================================================

class AdvocateAgent:
    """Build strongest legal case using CPA 2019."""

    SYSTEM_PROMPT = """You are a Consumer Advocate Agent using Consumer Protection Act 2019.

ROLE: Build the STRONGEST possible legal case for the consumer.
- Cite specific CPA 2019 sections
- Identify manufacturer/service deficiencies
- Calculate damages aggressively but honestly
- Assume best interpretation of evidence

OUTPUT: Return JSON:
{
  "legal_claims": [{"section": string, "claim": string, "evidence": string}],
  "strength_score": 0-10,
  "estimated_compensation": float,
  "deficiency_type": "manufacturing|service|unfair_trade",
  "supporting_arguments": [string],
  "weaknesses": [string],
  "recommendation": "strong_case|moderate_case|weak_case"
}"""

    def __init__(self, model: str = "gemini-3.5-flash"):
        self.model = model
        self.name = "advocate_agent"

    def run(self, case_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Build advocate case."""
        prompt = f"""
Build legal case for this warranty dispute:

{json.dumps(case_obj, indent=2)}

Use Consumer Protection Act 2019. Be aggressive but factual."""

        response = call_llm(self.SYSTEM_PROMPT, prompt, response_format="json")
        advocate_view = safe_json_parse(response)
        advocate_view["agent"] = "advocate_agent"
        return advocate_view


# ============================================================================
# AGENT 3: Defense Agent
# ============================================================================

class DefenseAgent:
    """Realistic counter-arguments (adversarial)."""

    SYSTEM_PROMPT = """You are a Defense Agent playing the company's realistic position.

ROLE: Provide realistic counter-arguments the company might make.
- Not strawman arguments - actual company defenses
- Identify genuine warranty limitations
- Spot evidence gaps
- Suggest company's likely defense strategy

OUTPUT: Return JSON:
{
  "company_position": string,
  "counter_claims": [{"claim": string, "legal_basis": string}],
  "strength_score": 0-10,
  "warranty_limitations": [string],
  "evidence_gaps": [string],
  "likely_defense": string,
  "company_advantage": string
}"""

    def __init__(self, model: str = "gemini-3.5-flash"):
        self.model = model
        self.name = "defense_agent"

    def run(self, case_obj: Dict[str, Any], advocate_view: Dict[str, Any]) -> Dict[str, Any]:
        """Build defense case."""
        prompt = f"""
Build company's defense against this warranty claim:

Case: {json.dumps(case_obj, indent=2)}
Advocate view: {json.dumps(advocate_view, indent=2)}

What would the company realistically argue?"""

        response = call_llm(self.SYSTEM_PROMPT, prompt, response_format="json")
        defense_view = safe_json_parse(response)
        defense_view["agent"] = "defense_agent"
        return defense_view


# ============================================================================
# AGENT 4: Arbiter Agent (Router)
# ============================================================================

class ArbiterAgent:
    """Score both sides, decide routing."""

    SYSTEM_PROMPT = """You are an Arbiter Agent - independent judge of case strength.

ROLE:
1. Score both advocate and defense positions
2. Assess case readiness (evidence, legal merit, SLA breaches)
3. Route to appropriate escalation channel
4. Calculate confidence percentage

OUTPUT: Return JSON:
{
  "advocate_score": 0-10,
  "defense_score": 0-10,
  "net_confidence": 0-100,
  "routing_decision": "insufficient_evidence|reframe|ready_to_file",
  "channel": "NCH|public_notice|legal_notice_direct|ejagriti",
  "reasoning": string,
  "sla_factor": boolean,
  "next_action": string
}"""

    def __init__(self, model: str = "gemini-3.5-flash"):
        self.model = model
        self.name = "arbiter_agent"

    def run(self, case_obj: Dict[str, Any], advocate_view: Dict[str, Any],
            defense_view: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate and route."""
        prompt = f"""
Score both positions and decide routing:

Case: {json.dumps(case_obj, indent=2)}
Advocate: {json.dumps(advocate_view, indent=2)}
Defense: {json.dumps(defense_view, indent=2)}

Return routing decision with confidence. Account for SLA breaches."""

        response = call_llm(self.SYSTEM_PROMPT, prompt, response_format="json")
        arbiter_view = safe_json_parse(response)
        arbiter_view["agent"] = "arbiter_agent"

        # SLA breach boost
        if case_obj.get("sla_breaches") and len(case_obj["sla_breaches"]) > 0:
            arbiter_view["net_confidence"] = min(100, arbiter_view.get("net_confidence", 0) + 10)
            arbiter_view["routing_decision"] = "ready_to_file"

        return arbiter_view


# ============================================================================
# AGENT 5: Filing Agent
# ============================================================================

class FilingAgent:
    """Prepare forms for government portals."""

    SYSTEM_PROMPT = """You are a Filing Agent preparing consumer complaints.

ROLE:
1. Stage government forms (NCH, e-Jagriti, public notice)
2. Format case data for each portal's requirements
3. Prepare evidence attachments
4. Flag missing documents
5. Ready for human review/submission

OUTPUT: Return JSON:
{
  "form_type": "nch|ejagriti|public_notice|legal_notice",
  "form_status": "ready|pending_docs|needs_notary",
  "fields": {
    "state": string,
    "company": string,
    "relief_amount": float,
    "description": string,
    "jurisdiction": string
  },
  "evidence_checklist": {"receipt": bool, "photos": bool, "tickets": bool, "emails": bool},
  "portal_url": string,
  "next_step": string
}"""

    def __init__(self, model: str = "gemini-3.5-flash"):
        self.model = model
        self.name = "filing_agent"

    def run(self, case_obj: Dict[str, Any], arbiter_view: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare filing."""
        prompt = f"""
Prepare complaint form for this decision:

Case: {json.dumps(case_obj, indent=2)}
Routing: {json.dumps(arbiter_view, indent=2)}

Stage the form fields and verify evidence."""

        response = call_llm(self.SYSTEM_PROMPT, prompt, response_format="json")
        form_prep = safe_json_parse(response)
        form_prep["agent"] = "filing_agent"
        form_prep["human_approval_required"] = True
        return form_prep


# ============================================================================
# AGENT 6: Monitoring Agent
# ============================================================================

class MonitoringAgent:
    """Track SLA, auto-escalate."""

    SYSTEM_PROMPT = """You are a Monitoring Agent tracking consumer complaint progress.

ROLE:
1. Check NCH/e-Jagriti status at intervals
2. Track SLA deadlines (15 days NCH, 30 days e-Jagriti)
3. Trigger auto-escalation if company doesn't respond
4. Alert consumer of next steps

OUTPUT: Return JSON:
{
  "status": "in_progress|company_responded|escalated|resolved",
  "days_elapsed": int,
  "sla_deadline": string,
  "days_until_deadline": int,
  "last_update": string,
  "auto_escalation_triggered": boolean,
  "next_check_date": string,
  "action_required": string
}"""

    def __init__(self, model: str = "gemini-3.5-flash"):
        self.model = model
        self.name = "monitoring_agent"

    def run(self, case_obj: Dict[str, Any], filing_info: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor case."""
        prompt = f"""
Monitor this filed complaint:

Case: {json.dumps(case_obj, indent=2)}
Filing: {json.dumps(filing_info, indent=2)}

Check SLA and flag escalation needs."""

        response = call_llm(self.SYSTEM_PROMPT, prompt, response_format="json")
        monitor_view = safe_json_parse(response)
        monitor_view["agent"] = "monitoring_agent"
        return monitor_view


# ============================================================================
# ORCHESTRATOR
# ============================================================================

class AntigravityOrchestrator:
    """Orchestrate all 6 agents in sequence."""

    def __init__(self, model: str = "gemini-3.5-flash"):
        self.model = model
        self.agents = {
            "extraction": ExtractionAgent(model),
            "advocate": AdvocateAgent(model),
            "defense": DefenseAgent(model),
            "arbiter": ArbiterAgent(model),
            "filing": FilingAgent(model),
            "monitoring": MonitoringAgent(model)
        }

    def orchestrate(self, case_input: Dict[str, Any]) -> Dict[str, Any]:
        """Run full pipeline."""
        print("\n" + "="*70)
        print("🤖 ANTIGRAVITY AGENT ORCHESTRATION")
        print("="*70)

        # Stage 1: Extract
        print("\n[1/6] Extraction Agent...")
        case_obj = self.agents["extraction"].run(case_input)
        print(f"  ✓ Extracted case: {case_obj.get('product', {}).get('name')}")

        # Stage 2a: Advocate
        print("\n[2/6] Advocate Agent...")
        advocate_view = self.agents["advocate"].run(case_obj)
        print(f"  ✓ Advocate score: {advocate_view.get('strength_score', 0)}/10")

        # Stage 2b: Defense (parallel in Antigravity)
        print("\n[3/6] Defense Agent...")
        defense_view = self.agents["defense"].run(case_obj, advocate_view)
        print(f"  ✓ Defense score: {defense_view.get('strength_score', 0)}/10")

        # Stage 3: Arbiter (routing)
        print("\n[4/6] Arbiter Agent (ROUTING)...")
        arbiter_view = self.agents["arbiter"].run(case_obj, advocate_view, defense_view)
        decision = arbiter_view.get("routing_decision")
        confidence = arbiter_view.get("net_confidence", 0)
        channel = arbiter_view.get("channel")
        print(f"  ✓ Decision: {decision} ({confidence}% confidence)")
        print(f"  ✓ Channel: {channel}")

        if decision == "ready_to_file":
            # Stage 4: Filing
            print("\n[5/6] Filing Agent...")
            filing_info = self.agents["filing"].run(case_obj, arbiter_view)
            print(f"  ✓ Form staged: {filing_info.get('form_type')}")

            # Stage 5: Monitoring
            print("\n[6/6] Monitoring Agent...")
            monitor_info = self.agents["monitoring"].run(case_obj, filing_info)
            print(f"  ✓ Monitoring scheduled")
        else:
            filing_info = {"status": "awaiting_evidence"}
            monitor_info = {"status": "case_not_ready"}

        result = {
            "status": "completed",
            "decision": decision,
            "confidence": confidence,
            "routing_channel": channel,
            "case": case_obj,
            "advocate_view": advocate_view,
            "defense_view": defense_view,
            "arbiter_view": arbiter_view,
            "filing_info": filing_info,
            "monitoring_info": monitor_info
        }

        print("\n" + "="*70)
        print(f"✅ ORCHESTRATION COMPLETE: {decision}")
        print("="*70)

        return result


if __name__ == "__main__":
    test_case = {
        "product": "Nothing Phone 4a Pro",
        "issue": "Water patches in Glyph Matrix display",
        "purchase_date": "2026-03-23",
        "issue_date": "2026-03-25",
        "company_contact": "support@nothing.tech",
        "promised_resolution": "7-10 days",
        "current_date": "2026-04-08",
        "evidence": ["receipt.jpg", "photos_2.jpg", "email_thread.txt"]
    }

    orchestrator = AntigravityOrchestrator()
    result = orchestrator.orchestrate(test_case)
    print("\nResult saved to result_antigravity_agents.json")
    with open("result_antigravity_agents.json", "w") as f:
        json.dump(result, f, indent=2)
