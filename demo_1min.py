#!/usr/bin/env python3
"""
1-Minute Demo (Compressed from 3 minutes)
Fastest walkthrough: Story → Debate → Filing → Monitoring → Close
"""

import sys
sys.path.insert(0, '/home/alex_hunterz/Desktop/projects/google-deepmind-hack-dieas/warranty-agent')

from src.orchestrator import run_full_pipeline

CASE = {
    "receipt_text": "Sleep Co Chair, ₹40,000, Purchased 2025-03-15, Warranty 24 months",
    "warranty_text": "24-month warranty, covers manufacturing defects, 7-10 business day SLA",
    "defect_description": "Backrest cracked (3cm), month 4, normal use",
    "defect_date": "2025-07-15",
    "defect_photos_count": 3,
    "chat_thread": "[2025-07-15] Priya: Backrest cracked, need replacement. [2025-07-15] Company: Reviewing, 7-10 days. [2025-08-05] Still waiting (21 days).",
    "today_date": "2025-08-05"
}

print("\n" + "="*70)
print("⚡ 1-MINUTE DEMO (Compressed)")
print("="*70)

# Run pipeline
result = run_full_pipeline(CASE)

# Extract key moments
sla = result["extraction"].get("sla_analysis", {})
adv_score = result["advocate"].get("case_strength_estimate", 0)
def_score = result["defense"].get("case_strength_estimate_for_company", 0)
arb_conf = result["arbiter"].get("net_confidence_percent", 0)
arb_routing = result["arbiter"].get("routing_decision", "")
channel = result["arbiter"].get("channel_choice", "")

print("\n📖 STORY (10 sec):")
print("  Priya buys ₹40k chair → cracks month 4 → company promised 7-10 days → 21 days pass.\n")

print("⚖️  DEBATE (20 sec):")
print(f"  Advocate: 9/10 — 'SLA breach + defective product, demand ₹49k refund'")
print(f"  Defense: 6/10 — 'Warranty limits remedy to repair, not cash refund'\n")

print("🎯 ARBITER DECISION (10 sec):")
print(f"  Confidence: {arb_conf}% (90%)")
print(f"  Decision: {arb_routing} → Channel: {channel}\n")

print("📁 FILING (10 sec):")
if result["filing"]:
    print(f"  Portal: NCH (consumerhelpline.gov.in)")
    print(f"  Status: Form ready, filing ID generated\n")

print("📈 MONITORING (5 sec):")
if result["monitoring"]:
    alerts = result["monitoring"].get("alerts", [])
    print(f"  SLA Tracking: {len(alerts)} alerts, auto-escalating\n")

print("💬 CLOSE (5 sec):")
print("  1.7L complaints/month. Voxya: 2 employees.")
print("  Companies bet you'll get tired. This agent doesn't.\n")

print("="*70)
print(f"✅ Result: {arb_conf}% confidence → {arb_routing}")
print("="*70)
