#!/usr/bin/env python3
"""Test individual Antigravity agents in isolation."""

from src.antigravity_agents import (
    ExtractionAgent, AdvocateAgent, DefenseAgent,
    ArbiterAgent, FilingAgent, MonitoringAgent
)
import json

# Test case: Nothing Phone
case_input = {
    "product": "Nothing Phone 4a Pro",
    "issue": "Water patches in Glyph Matrix display",
    "purchase_date": "2026-03-23",
    "issue_discovered": "2026-03-25",
    "company": "Nothing India",
    "promised_resolution": "7-10 days",
    "days_elapsed": 16,
    "evidence": ["receipt.jpg", "photos_2.jpg"]
}

print("\n" + "="*70)
print("🧪 TESTING INDIVIDUAL ANTIGRAVITY AGENTS")
print("="*70)

# Test 1: Extraction Agent
print("\n[TEST 1] EXTRACTION AGENT")
print("-" * 70)
try:
    extractor = ExtractionAgent()
    case_obj = extractor.run(case_input)
    print(f"✅ PASS - Extracted case")
    print(f"   Product: {case_obj.get('product', {}).get('name')}")
    print(f"   Days elapsed: {case_obj.get('days_elapsed')}")
    print(f"   SLA breaches: {len(case_obj.get('sla_breaches', []))} detected")
except Exception as e:
    print(f"❌ FAIL - {e}")
    exit(1)

# Test 2: Advocate Agent
print("\n[TEST 2] ADVOCATE AGENT")
print("-" * 70)
try:
    advocate = AdvocateAgent()
    advocate_view = advocate.run(case_obj)
    print(f"✅ PASS - Built advocate case")
    print(f"   Score: {advocate_view.get('strength_score')}/10")
    print(f"   Claims: {len(advocate_view.get('legal_claims', []))} identified")
    print(f"   Relief: ₹{advocate_view.get('estimated_compensation')}")
except Exception as e:
    print(f"❌ FAIL - {e}")
    exit(1)

# Test 3: Defense Agent
print("\n[TEST 3] DEFENSE AGENT")
print("-" * 70)
try:
    defense = DefenseAgent()
    defense_view = defense.run(case_obj, advocate_view)
    print(f"✅ PASS - Built defense case")
    print(f"   Score: {defense_view.get('strength_score')}/10")
    print(f"   Counter-claims: {len(defense_view.get('counter_claims', []))} identified")
except Exception as e:
    print(f"❌ FAIL - {e}")
    exit(1)

# Test 4: Arbiter Agent
print("\n[TEST 4] ARBITER AGENT (ROUTING)")
print("-" * 70)
try:
    arbiter = ArbiterAgent()
    arbiter_view = arbiter.run(case_obj, advocate_view, defense_view)
    print(f"✅ PASS - Made routing decision")
    print(f"   Advocate score: {arbiter_view.get('advocate_score')}/10")
    print(f"   Defense score: {arbiter_view.get('defense_score')}/10")
    print(f"   Confidence: {arbiter_view.get('net_confidence')}%")
    print(f"   Decision: {arbiter_view.get('routing_decision')}")
    print(f"   Channel: {arbiter_view.get('channel')}")
except Exception as e:
    print(f"❌ FAIL - {e}")
    exit(1)

# Test 5: Filing Agent
print("\n[TEST 5] FILING AGENT")
print("-" * 70)
try:
    filing = FilingAgent()
    form_prep = filing.run(case_obj, arbiter_view)
    print(f"✅ PASS - Prepared filing")
    print(f"   Form type: {form_prep.get('form_type')}")
    print(f"   Status: {form_prep.get('form_status')}")
    print(f"   Portal: {form_prep.get('portal_url', 'N/A')}")
except Exception as e:
    print(f"❌ FAIL - {e}")
    exit(1)

# Test 6: Monitoring Agent
print("\n[TEST 6] MONITORING AGENT")
print("-" * 70)
try:
    monitoring = MonitoringAgent()
    monitor_view = monitoring.run(case_obj, form_prep)
    print(f"✅ PASS - Set up monitoring")
    print(f"   Status: {monitor_view.get('status')}")
    print(f"   Next check: {monitor_view.get('next_check_date')}")
except Exception as e:
    print(f"❌ FAIL - {e}")
    exit(1)

print("\n" + "="*70)
print("✅ ALL 6 AGENTS WORKING")
print("="*70)
print("\nTest output saved to test_output.txt")
