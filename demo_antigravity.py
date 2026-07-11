#!/usr/bin/env python3
"""
Phase 2 Demo: Full Antigravity Orchestration
Shows: Multi-agent workflow with persistent state and routing logic
"""

import sys
sys.path.insert(0, '/home/alex_hunterz/Desktop/projects/google-deepmind-hack-dieas/warranty-agent')

from src.antigravity_orchestrator import AntigravityOrchestrator
from datetime import datetime

# Priya's chair case (same test case as Phase 1)
PRIYA_CASE = {
    "receipt_text": """
Sleep Co Furniture Private Ltd
Invoice #INV-2025-003421, Date: 2025-03-15
Item: Sleep Co Deluxe Office Chair
Price: ₹40,000.00
Warranty: 24 months
""",
    "warranty_text": """
Sleep Co Warranty: 24 months
Coverage: Manufacturing defects
Process: Contact support within warranty period
Response time: 7-10 business days
""",
    "defect_description": """
Backrest cracked (3cm, center frame). Normal office use (200 lbs, 8-9 hrs/day).
No impact or accidents. Spontaneous failure.
""",
    "defect_date": "2025-07-15",
    "defect_photos_count": 3,
    "chat_thread": """
[2025-07-15] Priya: Backrest cracked. Requesting replacement/refund.
[2025-07-15] Sleep Co: Under review. Expect update in 7-10 business days.
[2025-07-22] Priya: Status? Need to plan replacement.
[2025-07-23] Sleep Co: Still reviewing. 7-10 days from today.
[2025-08-05] TODAY: No update from company (21 days total).
""",
    "today_date": "2025-08-05"
}

def demo_antigravity_workflow():
    """Run full Antigravity orchestration workflow."""

    print("\n" + "="*70)
    print("🎯 PHASE 2 DEMO: Antigravity Multi-Agent Orchestration")
    print("="*70)
    print("\nWorkflow:")
    print("  1. Extraction Agent (parse evidence)")
    print("  2. Advocate + Defense Agents (parallel reasoning)")
    print("  3. Arbiter Agent (score & route)")
    print("  4. Filing Agent (stage form)")
    print("  5. Monitoring Agent (track SLA)")
    print("\n" + "="*70 + "\n")

    # Create orchestrator
    orchestrator = AntigravityOrchestrator(case_id="priya_chair_001")

    # Set up event callbacks for visibility
    def log_event(event_type):
        def callback(data):
            print(f"\n📢 EVENT: {event_type}")
            print(f"   Data: {data}")
        return callback

    orchestrator.register_callback("on_stage_complete", log_event("STAGE_COMPLETE"))
    orchestrator.register_callback("on_escalation", log_event("ESCALATION_TRIGGERED"))
    orchestrator.register_callback("on_error", log_event("ERROR"))

    # Run full workflow
    try:
        result = orchestrator.run_full_workflow(PRIYA_CASE)

        # Print summary
        print("\n" + "="*70)
        print("✅ WORKFLOW COMPLETE")
        print("="*70)

        summary = orchestrator.get_summary()
        print(f"\nCase Summary:")
        print(f"  ID: {summary['case_id']}")
        print(f"  Product: {summary['product']}")
        print(f"  SLA Breached: {summary['sla_breached']}")
        print(f"\nAgents Analysis:")
        print(f"  Advocate Score: {summary['advocate_score']}/10")
        print(f"  Defense Score: {summary['defense_score']}/10")
        print(f"  Arbiter Confidence: {summary['arbiter_confidence']}%")
        print(f"\nFiling Status:")
        print(f"  Status: {summary['filing_status']}")
        print(f"\nMonitoring:")
        print(f"  Active Alerts: {summary['monitoring_alerts']}")

        print("\n" + "="*70)
        print("Ready for Phase 3: Demo Rehearsal")
        print("="*70)

        return True

    except Exception as e:
        print(f"\n❌ WORKFLOW ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = demo_antigravity_workflow()
    sys.exit(0 if success else 1)
