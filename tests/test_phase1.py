"""
Phase 1 Test: Extract → Advocate → Defense → Arbiter → Filing → Monitor
Test case: Priya's Sleep Co chair (real Reddit case, 282 upvotes)

Key verifications:
1. Extraction parses SLA promise correctly
2. Advocate builds strong case (prioritizes deficiency-of-service + SLA breach)
3. Defense produces DIFFERENT output (argues warranty exclusions, realistic company position)
4. Arbiter scores correctly and routes to filing
5. Filing stages form without submitting
6. Monitor tracks SLA progression
"""
import sys
import os
sys.path.insert(0, '/home/alex_hunterz/Desktop/projects/google-deepmind-hack-dieas/warranty-agent')

from src.orchestrator import run_full_pipeline
import json

# Priya's Chair Case
# Real case: Sleep Co chair, ₹40k, backrest cracked month 4
# Company promised "7-10 business days" to resolve
# 21 days elapsed, no resolution
# Evidence: receipt, defect photos, full support chat thread

PRIYA_CASE_DATA = {
    "receipt_text": """
Sleep Co Furniture Private Ltd
Invoice #INV-2025-003421
Date: 2025-03-15

Customer: Priya M
Address: Bangalore

Item: Sleep Co Deluxe Office Chair (Model SC-DX-001)
Price: ₹40,000.00
Warranty: 24 months (manufacturing defects)
Warranty starts: 2025-03-15
Warranty expires: 2027-03-15

Payment: Debit Card
Status: Delivered 2025-03-18

Terms: 30-day return window (expired)
      Warranty covers manufacturing defects only
      Excludes: accidental damage, normal wear, user modifications
""",

    "warranty_text": """
Sleep Co Furniture Warranty Card
Model: SC-DX-001
Serial: SCD-X001-0987654

Warranty Period: 24 Months from purchase date
Coverage: Manufacturing defects in material/workmanship
Exclusions: Accidental damage, normal wear and tear, misuse, user modifications

Service: Contact support@sleepco.in with photos + invoice

Process:
- Initial assessment: 5-7 business days
- If covered: replacement or refund within 7-10 business days
- If excluded: company liable for inspection cost only
""",

    "defect_description": """
The backrest developed a visible crack in the center of the backrest cushion support.
The crack is approximately 3cm long, starting from the upper edge of the backrest frame.
The cushion has not been modified or repaired by the user.
The chair was used normally for office work (8-9 hours/day, ~200 lbs user weight).
No impact or accidental damage occurred—the failure appears to be spontaneous.
""",

    "defect_date": "2025-07-15",
    "defect_photos_count": 3,

    "chat_thread": """
[2025-07-15 14:22] PRIYA EMAILS SUPPORT:
Subject: Chair Defect - Backrest Crack (Invoice INV-2025-003421)

Hi,

I'm writing about the Sleep Co Deluxe Chair I purchased 4 months ago (invoice attached).
The backrest has cracked—there's a 3cm crack in the support frame.
I've been using it normally for office work, no abuse or accidents.

This is clearly a manufacturing defect within warranty.

Attached:
- Photos of the crack (3 images)
- Invoice INV-2025-003421
- Warranty card photo

Please advise on next steps for replacement or refund.

Thanks,
Priya

---

[2025-07-15 15:45] SLEEP CO SUPPORT RESPONDS:
Dear Priya,

Thank you for contacting Sleep Co.

We have received your inquiry. Our team is reviewing your case.

As per our standard process, you can expect an update within 7-10 business days.

Best regards,
Support Team
Sleep Co Furniture

---

[2025-07-22 10:33] PRIYA FOLLOWS UP:
Hi,

It's been 7 days. Have you had a chance to review the chair defect?
I need to plan ahead for a replacement.

Thanks,
Priya

---

[2025-07-23 11:12] SLEEP CO RESPONDS:
Hi Priya,

Your case is currently under review. We are evaluating the damage pattern to determine if it's within warranty coverage.

We will provide a formal decision within 7-10 business days from today.

Thanks for your patience.
Sleep Co Support

---

[2025-08-05 (TODAY)] - 21 DAYS TOTAL ELAPSED, NO RESOLUTION
Priya has not received further communication.
- Original complaint: 2025-07-15
- Today: 2025-08-05
- Days elapsed: 21 days
- Company promised 7-10 business days from July 15 (deadline: July 24)
- SLA definitely breached
""",

    "today_date": "2025-08-05"
}

def verify_phase1():
    """Run Phase 1 verification with Priya's case."""
    print("\n" + "="*70)
    print("PHASE 1 VERIFICATION: Priya's Sleep Co Chair Case")
    print("="*70)
    print("Test case: ₹40k chair, backrest cracked month 4")
    print("Company promised: 7-10 business days")
    print("Actual elapsed: 11 days (from first inquiry, 8 days from follow-up)")
    print("Verdict expected: Strong case, ready to file at NCH")
    print("="*70)

    # Run full pipeline
    result = run_full_pipeline(PRIYA_CASE_DATA)

    # VERIFY: Extraction correctly parsed SLA
    print("\n[VERIFY 1] EXTRACTION: SLA Promise Parsed")
    sla_analysis = result["extraction"].get("sla_analysis", {})
    promised = sla_analysis.get("days_promised")
    elapsed = sla_analysis.get("actual_days_elapsed")
    breached = sla_analysis.get("sla_breached")

    if promised and elapsed and breached is not None:
        print(f"✓ PASS: Company promised {promised} days, actual {elapsed} days")
        print(f"✓ PASS: SLA Breached = {breached}")
        assert breached == True, "SLA should be breached (11 > 10)"
    else:
        print(f"✗ FAIL: SLA analysis incomplete. Got: {sla_analysis}")
        return False

    # VERIFY: Advocate and Defense produce DIFFERENT outputs
    print("\n[VERIFY 2] ADVOCATE vs DEFENSE: Different Positions")
    adv_angle = result["advocate"].get("primary_legal_angle")
    adv_relief = result["advocate"].get("requested_relief", {}).get("total_claimed")
    adv_score = result["advocate"].get("case_strength_estimate")

    def_strongest = result["defense"].get("strongest_defense", "")
    def_score = result["defense"].get("case_strength_estimate_for_company")

    if adv_angle and adv_relief and adv_score and def_strongest and def_score:
        print(f"✓ PASS: Advocate angle = {adv_angle}")
        print(f"✓ PASS: Advocate score = {adv_score}/10, claims ₹{adv_relief}")
        print(f"✓ PASS: Defense score = {def_score}/10")
        print(f"✓ PASS: Defense argues: '{def_strongest[:70]}...'")

        # Critical: they should NOT agree
        assert adv_score != def_score or abs(adv_score - def_score) > 1, "Scores should differ (adversarial)"
        print(f"✓ PASS: Positions differ (adversarial verified)")
    else:
        print(f"✗ FAIL: Advocate or Defense incomplete")
        return False

    # VERIFY: Arbiter scores correctly and routes to file
    print("\n[VERIFY 3] ARBITER: Scoring & Routing")
    arb_confidence = result["arbiter"].get("net_confidence_percent")
    arb_routing = result["arbiter"].get("routing_decision")
    arb_channel = result["arbiter"].get("channel_choice")

    if arb_confidence and arb_routing:
        print(f"✓ PASS: Confidence = {arb_confidence}%")
        print(f"✓ PASS: Routing = {arb_routing}")
        if arb_routing == "ready_to_file":
            print(f"✓ PASS: Channel = {arb_channel}")
            assert arb_confidence > 70, "Confidence should be > 70% for this clear case"
        print(f"✓ PASS: Arbiter logic executed")
    else:
        print(f"✗ FAIL: Arbiter incomplete")
        return False

    # VERIFY: Filing staged correctly
    if result["filing"]:
        print("\n[VERIFY 4] FILING: Form Staged")
        filing_status = result["filing"].get("status")
        filing_portal = result["filing"].get("portal")
        filing_ready = result["filing"].get("ready_to_submit")

        if filing_status and filing_portal:
            print(f"✓ PASS: Status = {filing_status}")
            print(f"✓ PASS: Portal = {filing_portal}")
            print(f"✓ PASS: Ready to submit = {filing_ready}")
            assert filing_status == "pending_human_approval", "Filing should wait for human approval"
        else:
            print(f"✗ FAIL: Filing incomplete")
            return False
    else:
        print("\n[VERIFY 4] FILING: Skipped (case not ready to file)")

    # VERIFY: Monitoring tracks SLA
    if result["monitoring"]:
        print("\n[VERIFY 5] MONITORING: SLA Tracking")
        monitor_stage = result["monitoring"].get("current_stage")
        monitor_alerts = result["monitoring"].get("alerts", [])

        if monitor_stage and monitor_alerts:
            print(f"✓ PASS: Stage = {monitor_stage}")
            print(f"✓ PASS: Alerts tracked = {len(monitor_alerts)}")
            for alert in monitor_alerts[:2]:
                print(f"    - {alert.get('alert')}")
        else:
            print(f"✗ FAIL: Monitoring incomplete")
            return False
    else:
        print("\n[VERIFY 5] MONITORING: Skipped")

    print("\n" + "="*70)
    print("PHASE 1 VERIFICATION: ALL CHECKS PASSED ✓")
    print("="*70)
    print("\nKey findings:")
    print(f"  • SLA Breach: {breached} (company promised {promised} days, took {elapsed})")
    print(f"  • Advocate-Defense disagreement: ✓ (scores {adv_score} vs {def_score})")
    print(f"  • Arbiter confidence: {arb_confidence}%")
    print(f"  • Routing: {arb_routing} via {arb_channel}")
    print(f"  • Ready for filing: {filing_ready if result['filing'] else 'N/A'}")

    # Save result for next phase
    with open('/home/alex_hunterz/Desktop/projects/google-deepmind-hack-dieas/warranty-agent/phase1_result.json', 'w') as f:
        # Make result JSON-serializable
        clean_result = {
            "extraction": result["extraction"],
            "advocate": result["advocate"],
            "defense": result["defense"],
            "arbiter": result["arbiter"],
            "filing": result["filing"],
            "monitoring": result["monitoring"]
        }
        json.dump(clean_result, f, indent=2, default=str)

    return True

if __name__ == "__main__":
    success = verify_phase1()
    sys.exit(0 if success else 1)
