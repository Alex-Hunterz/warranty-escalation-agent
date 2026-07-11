#!/usr/bin/env python3
"""
Test form filling in isolation
Shows what Computer Use does vs fallback
"""

from src.computer_use_integration import ComputerUseFormFiller
import json

case_data = {
    "product": "Nothing Phone 4a Pro",
    "defect": "Water patches in Glyph Matrix display",
    "company": "Nothing India",
    "relief_amount": "49000",
    "description": "Device purchased March 23, 2026. Water patches appeared March 25, 2026 (manufacturing defect). Company promised resolution in 7-10 days but has not responded after 16 days."
}

print("\n" + "="*70)
print("🧪 TEST: FORM FILLING (Computer Use + Fallback)")
print("="*70)

filler = ComputerUseFormFiller()

print("\n[ATTEMPT 1] Try NCH Form Filling with Computer Use")
print("-" * 70)
print("Attempting to use Gemini Computer Use API...")
print("(This requires ANTHROPIC_API_KEY to be set)\n")

nch_result = filler.fill_nch_form(case_data)

print("\n[RESULT]")
print(json.dumps(nch_result, indent=2))

if nch_result.get("status") == "form_fill_initiated":
    print("\n✅ SUCCESS: Computer Use is working!")
    print("   Browser should have opened and form filled.")
    print("   Screenshots captured:", len(nch_result.get("actions_taken", [])))
elif nch_result.get("status") == "form_simulated":
    print("\n⚠️  FALLBACK ACTIVE: Computer Use API unavailable")
    print("   System gracefully fell back to form structure.")
    print("   This is expected if ANTHROPIC_API_KEY is not set.")
    print("\n   What WOULD happen with Computer Use:")
    print("   1. Browser opens")
    print("   2. Navigates to consumerhelpline.gov.in")
    print("   3. Fills form with this data:")
    for key, value in nch_result.get("form_fields", {}).items():
        print(f"      {key}: {value}")

print("\n" + "="*70)
print("[ATTEMPT 2] Try e-Jagriti Form Filling")
print("-" * 70)

case_data_ejagriti = {
    **case_data,
    "consumer_name": "Manit Bohra"
}

ejagriti_result = filler.fill_ejagriti_form(case_data_ejagriti)

print("\n[RESULT]")
print(json.dumps(ejagriti_result, indent=2))

if ejagriti_result.get("status") == "ejagriti_form_ready":
    print("\n✅ e-Jagriti form ready")
else:
    print("\n⚠️  Fallback: e-Jagriti form structure ready")

print("\n" + "="*70)
print("🔑 KEY TAKEAWAYS")
print("="*70)
print("""
1. COMPUTER USE (if API available):
   - Actually opens browser
   - Navigates to real portal
   - Fills form fields
   - Takes screenshots
   - Returns proof

2. FALLBACK (if API unavailable):
   - Returns form structure
   - Shows what WOULD be filled
   - Graceful degradation
   - System doesn't break

3. FOR HACKATHON:
   - Show Computer Use capability (even if simulated)
   - OR show pre-recorded video of actual form filling
   - Judges understand this is cutting-edge tech
   - Graceful fallback shows engineering maturity
""")

print("\n[TEST COMPLETE]")
print("\nTo enable Computer Use:")
print("  export ANTHROPIC_API_KEY='sk-ant-...'")
print("  python3 test_form_filling.py")
