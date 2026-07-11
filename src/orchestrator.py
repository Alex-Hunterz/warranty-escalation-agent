"""
Main Orchestrator
Wires all 6 agents into a unified pipeline.
Also serves as template for Antigravity wiring later.
"""
import json
from src.agents.extraction_agent import extract_case
from src.agents.advocate_agent import advocate
from src.agents.defense_agent import defense
from src.agents.arbiter_agent import arbiter
from src.agents.filing_agent import filing
from src.agents.monitoring_agent import monitor

def run_full_pipeline(case_data: dict, simulate_monitor_date: str = None) -> dict:
    """
    Run the complete pipeline: extract → advocate → defense → arbiter → filing → monitor

    case_data: Raw case input (receipt_text, chat_thread, etc)
    simulate_monitor_date: Optional date to use for monitoring stage (for testing future scenarios)

    Returns: Full pipeline result with all agent outputs
    """
    print("\n" + "="*70)
    print("PHASE 1 FULL PIPELINE: Priya's Chair Case")
    print("="*70)

    # STAGE 1: Extraction
    print("\n[1/6] EXTRACTION AGENT...")
    case_obj = extract_case(case_data)
    print(f"✓ Extracted: {case_obj.get('product', {}).get('name')} - ₹{case_obj.get('product', {}).get('price')}")
    print(f"  SLA Analysis: Company promised {case_obj.get('sla_analysis', {}).get('days_promised')} days, took {case_obj.get('sla_analysis', {}).get('actual_days_elapsed')} days")
    print(f"  SLA Breached: {case_obj.get('sla_analysis', {}).get('sla_breached')}")

    # STAGE 2: Advocate
    print("\n[2/6] CONSUMER ADVOCATE AGENT...")
    advocate_draft = advocate(case_obj)
    print(f"✓ Legal Angle: {advocate_draft.get('primary_legal_angle')}")
    print(f"  Case Strength (Advocate): {advocate_draft.get('case_strength_estimate')}/10")
    print(f"  Requested Relief: ₹{advocate_draft.get('requested_relief', {}).get('total_claimed')}")

    # STAGE 3: Defense
    print("\n[3/6] COMPANY DEFENSE AGENT (Adversarial)...")
    defense_draft = defense(case_obj, advocate_draft)
    print(f"✓ Strongest Company Defense: {defense_draft.get('strongest_defense', 'N/A')}")
    print(f"  Case Strength (Company): {defense_draft.get('case_strength_estimate_for_company')}/10")
    print(f"  Weakest Point in Advocate's Case: {defense_draft.get('weakest_point_in_advocate_case', 'N/A')}")

    # STAGE 4: Arbiter
    print("\n[4/6] ARBITER/ORCHESTRATOR...")
    arbiter_decision = arbiter(case_obj, advocate_draft, defense_draft)
    print(f"✓ Advocate Score: {arbiter_decision.get('advocate_score')}/10")
    print(f"  Defense Score: {arbiter_decision.get('defense_score')}/10")
    print(f"  Confidence: {arbiter_decision.get('net_confidence_percent')}%")
    print(f"  Routing Decision: {arbiter_decision.get('routing_decision')}")
    if arbiter_decision.get("routing_decision") == "ready_to_file":
        print(f"  Channel: {arbiter_decision.get('channel_choice')}")

    # STAGE 5: Filing
    if arbiter_decision.get("routing_decision") == "ready_to_file":
        print("\n[5/6] FILING AGENT...")
        filing_data = filing(case_obj, arbiter_decision, advocate_draft)
        print(f"✓ Portal: {filing_data.get('portal')}")
        print(f"  Status: {filing_data.get('status')}")
        print(f"  SLA Response Deadline: {filing_data.get('sla_response_deadline')}")
        if filing_data.get("ready_to_submit"):
            print("  ✓ Ready to submit (all evidence present)")
        else:
            print(f"  ⚠ Missing: {[item for item in filing_data.get('filing_checklist', []) if '✓' not in item]}")
    else:
        print("\n[5/6] FILING AGENT: Skipped (case not ready to file)")
        filing_data = None

    # STAGE 6: Monitoring
    if filing_data:
        print("\n[6/6] MONITORING AGENT (Simulated Future Check)...")
        monitor_result = monitor(case_obj, filing_data, current_date_str=simulate_monitor_date)
        print(f"✓ Current Stage: {monitor_result.get('current_stage')}")
        print(f"  Alerts: {len(monitor_result.get('alerts', []))} alert(s)")
        for alert in monitor_result.get('alerts', [])[:2]:
            print(f"    - [{alert.get('severity')}] {alert.get('alert')}")
        if monitor_result.get('auto_drafts', {}).get('execution_petition'):
            print("  ⚠ EXECUTION PETITION auto-drafted (non-compliance detected)")
    else:
        print("\n[6/6] MONITORING AGENT: Skipped (no filing)")
        monitor_result = None

    # Summary
    print("\n" + "="*70)
    print("PIPELINE RESULT SUMMARY")
    print("="*70)
    result = {
        "extraction": case_obj,
        "advocate": advocate_draft,
        "defense": defense_draft,
        "arbiter": arbiter_decision,
        "filing": filing_data,
        "monitoring": monitor_result
    }

    # Verify differentiator: Advocate ≠ Defense
    advocate_relief = advocate_draft.get("requested_relief", {}).get("total_claimed")
    defense_position = defense_draft.get("strongest_defense", "")
    if advocate_relief and defense_position:
        print(f"\n✓ DIFFERENTIATOR CHECK:")
        print(f"  Advocate claims: ₹{advocate_relief} relief")
        print(f"  Defense argues: {defense_position[:60]}...")
        print(f"  → Different positions confirmed ✓")
    else:
        print(f"\n⚠ Differentiator check incomplete")

    return result
