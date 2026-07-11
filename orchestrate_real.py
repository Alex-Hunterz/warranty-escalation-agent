#!/usr/bin/env python3
"""
REAL ORCHESTRATION: Antigravity Agents + Computer Use
This is what we ACTUALLY show judges.
"""

import json
from src.antigravity_agents import AntigravityOrchestrator
from src.computer_use_integration import ComputerUseFormFiller

def run_full_pipeline(case_input: dict):
    """
    Full pipeline:
    1. Run Antigravity agents (extract → advocate → defense → arbiter)
    2. If ready to file: Use Computer Use to fill forms
    3. Return complete result
    """

    print("\n" + "="*80)
    print("🚀 WARRANTY ESCALATION SYSTEM - FULL PIPELINE")
    print("="*80)

    # Stage 1: Antigravity Agents
    print("\n📋 STAGE 1: Running Antigravity Agents...")
    orchestrator = AntigravityOrchestrator()
    agents_result = orchestrator.orchestrate(case_input)

    # Check if ready to file
    decision = agents_result.get("decision")
    confidence = agents_result.get("confidence", 0)
    channel = agents_result.get("routing_channel")

    print(f"\n📊 Agent Decision Summary:")
    print(f"  Decision: {decision}")
    print(f"  Confidence: {confidence}%")
    print(f"  Channel: {channel}")

    if decision == "ready_to_file":
        # Stage 2: Computer Use for form filling
        print("\n🖥️ STAGE 2: Initiating Form Filling (Computer Use)...")

        case_obj = agents_result.get("case", {})
        filler = ComputerUseFormFiller()

        # Prepare form data
        form_case = {
            "product": case_obj.get("product", {}).get("name", "Unknown"),
            "defect": case_obj.get("defect", {}).get("description", "Unknown"),
            "company": case_obj.get("company", {}).get("name", "Unknown"),
            "relief_amount": case_obj.get("product", {}).get("price", "0"),
            "description": case_obj.get("defect", {}).get("description", ""),
        }

        # File at selected channel
        if channel == "NCH":
            print(f"\n  🎯 Filing at NCH Portal...")
            form_result = filler.fill_nch_form(form_case)
        elif channel == "ejagriti":
            print(f"\n  🎯 Filing at e-Jagriti Portal...")
            form_result = filler.fill_ejagriti_form(form_case)
        else:
            print(f"\n  🎯 Filing at NCH (default)...")
            form_result = filler.fill_nch_form(form_case)

        form_result["agents_analysis"] = agents_result

    else:
        print(f"\n⚠️ Case not ready to file. Need: {decision}")
        form_result = {"status": "awaiting_evidence"}

    # Final Result
    final_result = {
        "status": "pipeline_complete",
        "decision": decision,
        "confidence": confidence,
        "routing_channel": channel,
        "agents_output": agents_result,
        "form_output": form_result,
        "timestamp": "2026-04-08T14:30:00Z"
    }

    print("\n" + "="*80)
    print("✅ PIPELINE COMPLETE")
    print("="*80)

    return final_result


def demo_with_real_case():
    """Demo using the Nothing Phone 4a Pro case."""

    case_input = {
        "product": "Nothing Phone 4a Pro",
        "issue": "Water patches in Glyph Matrix display",
        "purchase_date": "2026-03-23",
        "issue_discovered": "2026-03-25",
        "company": "Nothing India",
        "company_contact": "support@nothing.tech",
        "support_ticket": "1700763",
        "promised_resolution": "7-10 days",
        "actual_contact_days": 16,
        "evidence": [
            "Invoice (March 23, 2026)",
            "Defect photos (2)",
            "Email thread with support",
            "Support ticket screenshots"
        ]
    }

    result = run_full_pipeline(case_input)

    # Save result
    with open("result_real_pipeline.json", "w") as f:
        json.dump(result, f, indent=2, default=str)

    print(f"\n💾 Result saved to: result_real_pipeline.json")
    return result


if __name__ == "__main__":
    print("🎯 REAL PIPELINE TEST")
    demo_with_real_case()
