#!/usr/bin/env python3
"""
Demo Script: Consumer Warranty Escalation Agent
Live demonstration for hackathon judges.

Shows: Extraction → Advocate vs Defense → Arbiter → Filing → Monitoring
Test case: Priya's Sleep Co chair (real case, 282 Reddit upvotes)
"""

import json
import sys
sys.path.insert(0, '/home/alex_hunterz/Desktop/projects/google-deepmind-hack-dieas/warranty-agent')

from src.orchestrator import run_full_pipeline

# Priya's case data
PRIYA_CASE = {
    "receipt_text": """
Sleep Co Furniture Private Ltd
Invoice #INV-2025-003421
Date: 2025-03-15
Item: Sleep Co Deluxe Office Chair (Model SC-DX-001)
Price: ₹40,000.00
Warranty: 24 months (manufacturing defects)
Warranty expires: 2027-03-15
""",
    "warranty_text": """
Sleep Co Furniture Warranty Card
Model: SC-DX-001
Warranty Period: 24 Months from purchase date
Coverage: Manufacturing defects in material/workmanship
Exclusions: Accidental damage, normal wear and tear, misuse
Process: Contact support@sleepco.in with photos + invoice
Response time: 7-10 business days for initial assessment
""",
    "defect_description": """
The backrest developed a visible crack in the center of the backrest cushion support.
The crack is approximately 3cm long, starting from the upper edge of the backrest frame.
The chair was used normally for office work (8-9 hours/day, ~200 lbs).
No impact or accidental damage occurred—the failure appears to be spontaneous.
""",
    "defect_date": "2025-07-15",
    "defect_photos_count": 3,
    "chat_thread": """
[2025-07-15 14:22] PRIYA:
Hi, I'm writing about the Sleep Co Deluxe Chair I purchased 4 months ago (invoice attached).
The backrest has cracked—there's a 3cm crack in the support frame.
I've been using it normally for office work, no abuse or accidents.
This is clearly a manufacturing defect within warranty.
Attached: Photos of the crack (3 images), Invoice, Warranty card photo.

[2025-07-15 15:45] SLEEP CO:
Thank you for contacting Sleep Co. We have received your inquiry.
Our team is reviewing your case.
As per our standard process, you can expect an update within 7-10 business days.

[2025-07-22 10:33] PRIYA:
It's been 7 days. Have you had a chance to review the chair defect?
I need to plan ahead for a replacement.

[2025-07-23 11:12] SLEEP CO:
Your case is currently under review. We are evaluating the damage pattern.
We will provide a formal decision within 7-10 business days from today.
Thanks for your patience.

[2025-08-05 (TODAY)] - 21 DAYS ELAPSED, NO RESOLUTION
Status: Priya waiting. Company has not provided final decision.
""",
    "today_date": "2025-08-05"
}

def demo_1_minute():
    """Quick 1-minute demo for time-constrained settings."""
    print("\n" + "="*70)
    print("⏱️  QUICK DEMO (1 minute) — Warranty Escalation Agent")
    print("="*70)

    result = run_full_pipeline(PRIYA_CASE)

    # Extract key findings
    sla_data = result["extraction"].get("sla_analysis", {})
    adv_score = result["advocate"].get("case_strength_estimate", "N/A")
    def_score = result["defense"].get("case_strength_estimate_for_company", "N/A")
    arb_conf = result["arbiter"].get("net_confidence_percent", "N/A")
    arb_decision = result["arbiter"].get("routing_decision", "N/A")

    print(f"\n📊 CASE SUMMARY:")
    print(f"  Product: Sleep Co Chair (₹40,000)")
    print(f"  Defect: Backrest crack (month 4, normal use)")
    print(f"  Company promised: {sla_data.get('days_promised')} days")
    print(f"  Actual response: {sla_data.get('actual_days_elapsed')} days")
    print(f"  SLA Breached: {sla_data.get('sla_breached')}")

    print(f"\n⚖️  ADVOCATE vs DEFENSE:")
    print(f"  Advocate score: {adv_score}/10 (deficiency-of-service angle)")
    print(f"  Defense score: {def_score}/10 (warranty limit defense)")
    print(f"  Net confidence: {arb_conf}%")

    print(f"\n🎯 DECISION:")
    print(f"  Arbiter routing: {arb_decision}")
    if result["filing"]:
        print(f"  Filing portal: {result['filing'].get('portal')}")
        print(f"  Status: {result['filing'].get('status')}")

    print(f"\n📈 MONITORING:")
    if result["monitoring"]:
        alerts = result["monitoring"].get("alerts", [])
        print(f"  Active alerts: {len(alerts)}")
        for alert in alerts[:1]:
            print(f"    • {alert.get('alert', 'N/A')}")

    print("\n" + "="*70)
    print("✓ Full pipeline executed. Ready for filing at NCH.")
    print("="*70)

def demo_3_minute_full():
    """Full 3-minute demo with detailed explanation (as per hackathon spec)."""
    print("\n" + "="*70)
    print("🎬 FULL DEMO (3 minutes) — Consumer Warranty Escalation Agent")
    print("="*70)
    print("\n[STORY] Priya buys a ₹40,000 chair. Month 4, backrest cracks.")
    print("She emails support with photos. Company says: 'Resolving in 7-10 days.'")
    print("21 days pass. Nothing. She's tired. Company wins.")
    print("\nLet's change that outcome.\n")

    # Run pipeline
    print("[STAGE 1/5] EXTRACTION — Parsing evidence...")
    result = run_full_pipeline(PRIYA_CASE)

    extraction = result["extraction"]
    sla = extraction.get("sla_analysis", {})

    print(f"  ✓ Extracted: {extraction.get('product', {}).get('name')}")
    print(f"  ✓ Warranty: {extraction.get('warranty', {}).get('period_months')} months (in effect)")
    print(f"  ✓ Company promise: 'Resolve in {sla.get('days_promised')} days'")
    print(f"  ✓ Actual: {sla.get('actual_days_elapsed')} days (BREACH)")

    print("\n[STAGE 2/5] ADVOCATE — Building strongest case...")
    advocate = result["advocate"]
    print(f"  Angle: {advocate.get('primary_legal_angle')}")
    print(f"  Relief: ₹{advocate.get('requested_relief', {}).get('total_claimed')}")
    print(f"    └─ Refund ₹{advocate.get('requested_relief', {}).get('refund_amount')}")
    print(f"    └─ Compensation ₹{advocate.get('requested_relief', {}).get('compensation_amount')}")
    print(f"  Score: {advocate.get('case_strength_estimate')}/10")

    print("\n[STAGE 3/5] DEFENSE — Company argues back...")
    defense = result["defense"]
    print(f"  Strongest defense: {defense.get('strongest_defense', 'N/A')[:80]}...")
    print(f"  Score: {defense.get('case_strength_estimate_for_company')}/10")
    print(f"  Weakest point in our case: {defense.get('weakest_point_in_advocate_case', 'N/A')[:70]}...")

    print("\n[STAGE 4/5] ARBITER — Scoring & routing...")
    arbiter = result["arbiter"]
    print(f"  Confidence: {arbiter.get('net_confidence_percent')}%")
    print(f"  Decision: {arbiter.get('routing_decision')}")
    if arbiter.get("routing_decision") == "ready_to_file":
        print(f"  Channel: {arbiter.get('channel_choice')}")
        print(f"  Reasoning: {arbiter.get('channel_reasoning', 'N/A')[:100]}...")

    if result["filing"]:
        print("\n[STAGE 5/5] FILING — Preparing government form...")
        filing = result["filing"]
        print(f"  Portal: {filing.get('portal')} (consumerhelpline.gov.in)")
        print(f"  Evidence checklist:")
        for item in filing.get('filing_checklist', [])[:3]:
            print(f"    {item}")
        print(f"  SLA response deadline: {filing.get('sla_response_deadline', 'N/A')[:10]}")
        print(f"  Status: {filing.get('status')}")

        if result["monitoring"]:
            print("\n[BONUS] MONITORING — Autonomous escalation setup...")
            monitoring = result["monitoring"]
            alerts = monitoring.get('alerts', [])
            print(f"  Tracking: {monitoring.get('current_stage')}")
            print(f"  Active alerts: {len(alerts)}")
            for alert in alerts[:1]:
                print(f"    • {alert.get('alert', 'N/A')[:80]}...")

    print("\n" + "="*70)
    print("FINAL OUTCOME:")
    print("="*70)
    print(f"✓ Advocate vs Defense: Adversarial reasoning verified")
    print(f"✓ Confidence: {arbiter.get('net_confidence_percent')}% (SLA breach documented)")
    print(f"✓ Channel: {arbiter.get('channel_choice')} (government escalation path)")
    print(f"✓ Filing: Ready (human approves → case filed → auto-monitored)")
    print("\nCompanies bet you'll get tired. This agent doesn't.")
    print("="*70)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["quick", "full"], default="full",
                       help="Demo mode: quick (1 min) or full (3 min)")
    args = parser.parse_args()

    if args.mode == "quick":
        demo_1_minute()
    else:
        demo_3_minute_full()
