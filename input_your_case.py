#!/usr/bin/env python3
"""
Input YOUR Case Data — Voice or Quick Form

For Flipkart case (or any warranty case):
1. Quick text input (fill form below)
2. Voice mode (coming soon - describe case verbally)
3. Load from file (paste chat transcript)
"""

import sys
sys.path.insert(0, '/home/alex_hunterz/Desktop/projects/google-deepmind-hack-dieas/warranty-agent')

from src.orchestrator import run_full_pipeline
import json

def get_user_input():
    """Prompt user to enter their case details."""
    print("\n" + "="*70)
    print("📋 ENTER YOUR WARRANTY CASE")
    print("="*70)

    case = {}

    # Product info
    print("\n1. PRODUCT")
    case["receipt_text"] = input("   Product name & price (e.g., 'Samsung phone, ₹50,000'): ")
    case["defect_description"] = input("   What's wrong with it? (e.g., 'Screen stopped working'): ")
    case["defect_date"] = input("   When did you first notice? (YYYY-MM-DD, or 'month 3', 'week 2'): ")
    case["defect_photos_count"] = int(input("   How many photos do you have? (0-5): "))

    # Warranty info
    print("\n2. WARRANTY")
    case["warranty_text"] = input("   Warranty details (e.g., '12 months manufacturer warranty'): ")
    purchase_date = input("   Purchase date (YYYY-MM-DD): ")

    # Company communication
    print("\n3. SUPPORT CHAT")
    print("   Paste the ENTIRE chat thread (or summary):")
    print("   [Format: Date, who, what they said]")
    print("   [Example: '[2025-01-15] Me: Phone broken. [2025-01-16] Company: Sending replacement']")
    print("   [Type 'END' when done, then press Enter]")

    chat_lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        chat_lines.append(line)

    case["chat_thread"] = "\n".join(chat_lines)
    case["today_date"] = input("\n   Today's date (YYYY-MM-DD): ")

    return case

def demo_with_case(case):
    """Run demo with user's case."""
    print("\n" + "="*70)
    print("🚀 ANALYZING YOUR CASE")
    print("="*70)

    try:
        result = run_full_pipeline(case)

        # Summary
        print("\n" + "="*70)
        print("📊 YOUR CASE ANALYSIS")
        print("="*70)

        sla = result["extraction"].get("sla_analysis", {})
        adv_score = result["advocate"].get("case_strength_estimate", 0)
        def_score = result["defense"].get("case_strength_estimate_for_company", 0)
        arb_conf = result["arbiter"].get("net_confidence_percent", 0)
        arb_routing = result["arbiter"].get("routing_decision", "")
        channel = result["arbiter"].get("channel_choice", "")

        print(f"\nProduct: {case['receipt_text']}")
        print(f"Defect: {case['defect_description']}")
        print(f"Days elapsed since complaint: {sla.get('actual_days_elapsed', 'N/A')}")
        print(f"SLA breached: {sla.get('sla_breached', False)}")

        print(f"\n⚖️  Advocate Score: {adv_score}/10")
        print(f"   Defense Score: {def_score}/10")
        print(f"\n🎯 Confidence: {arb_conf}%")
        print(f"   Decision: {arb_routing}")
        print(f"   Channel: {channel}")

        if arb_routing == "ready_to_file":
            print(f"\n✅ READY TO FILE at {channel}")
            relief = result["advocate"].get("requested_relief", {}).get("total_claimed", "N/A")
            print(f"   Estimated relief: ₹{relief}")
        elif arb_routing == "insufficient_evidence":
            gaps = result["advocate"].get("evidence_gaps", [])
            print(f"\n⚠️  Need more evidence:")
            for gap in gaps[:3]:
                print(f"   • {gap}")
        else:  # reframe
            print(f"\n🔄 Reframe suggested:")
            print(f"   {result['arbiter'].get('suggested_reframe', 'Try different legal angle')}")

        # Save result
        with open(f"case_result_{case['today_date'].replace('-', '')}.json", 'w') as f:
            json.dump({
                "case_input": case,
                "extraction": result["extraction"],
                "advocate": result["advocate"],
                "defense": result["defense"],
                "arbiter": result["arbiter"],
                "filing": result["filing"],
                "monitoring": result["monitoring"]
            }, f, indent=2, default=str)

        print(f"\n💾 Full analysis saved to: case_result_{case['today_date'].replace('-', '')}.json")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def demo_quick():
    """Quick demo (1 min) with preset case."""
    print("\n" + "="*70)
    print("⚡ QUICK DEMO (Priya's Chair Case)")
    print("="*70)

    case = {
        "receipt_text": "Sleep Co Chair, ₹40,000, Warranty 24 months",
        "defect_description": "Backrest cracked (3cm), normal office use",
        "defect_date": "2025-07-15",
        "defect_photos_count": 3,
        "warranty_text": "24-month manufacturer warranty, 7-10 business day SLA",
        "chat_thread": "[2025-07-15] Me: Backrest cracked, requesting replacement. [2025-07-15] Company: Under review, 7-10 days. [2025-08-05] Still no response (21 days).",
        "today_date": "2025-08-05"
    }

    demo_with_case(case)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["quick", "my_case"], default="quick",
                       help="quick: demo with Priya's case | my_case: enter your Flipkart case")
    args = parser.parse_args()

    if args.mode == "quick":
        demo_quick()
    else:
        case = get_user_input()
        demo_with_case(case)
