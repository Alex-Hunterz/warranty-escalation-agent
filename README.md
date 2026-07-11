# Warranty Escalation Agent
## Google DeepMind Hackathon - Problem Statement 2

🚀 **Multi-Agent System with Antigravity Deployment**

Autonomous system that analyzes warranty claims via 6 agents (adversarial reasoning), routes through India's consumer protection channels, and auto-escalates using SLA tracking.

---

## The Problem

Companies stonewall warranty claims—promising resolution, then dragging out timelines until consumers give up. **1.7 lakh complaints/month to NCH. Only ~0.01% have advocates.**

## The Solution

A 6-agent system that:
1. **Extracts** case facts from evidence (receipt, chat, photos)
2. **Advocates** for the consumer (strongest legal angle)
3. **Defends** as company counsel (adversarial quality gate)
4. **Arbitrates** case strength & picks escalation channel
5. **Files** autonomously at NCH or e-Jagriti (govt portals)
6. **Monitors** 24/7 → auto-escalates on SLA breach → drafts execution petitions

---

## Key Differentiators

| Feature | Voxya | Our System |
|---------|-------|-----------|
| Architecture | 2 employees | 6 autonomous agents |
| Reasoning | Single-path | **Adversarial** (Advocate vs Defense) |
| Routing | Fixed sequence | Adaptive (NCH / Legal / Court) |
| Deployment | Monolithic | **Antigravity Managed Agents** |
| Forms | Manual | **Computer Use (real browser)** |
| Monitoring | Manual | Autonomous 24/7 + auto-escalate |

---

## Architecture

```
Input: Receipt + Chat + Photos
  ↓
[1. EXTRACTION] → Structured CaseObject (SLA promise extracted)
  ↓
[2. ADVOCATE] ←→ [3. DEFENSE] (adversarial reasoning)
  ↓
[4. ARBITER] (scores both, routes: insufficient_evidence / reframe / ready_to_file)
  ↓
[5. FILING] (stages form at NCH/e-Jagriti, human approves submit)
  ↓
[6. MONITORING] (autonomous tracking, detects SLA breaches, escalates)
```

---

## Quick Start

### Prerequisites
```bash
Python 3.8+
Gemini API key (Tier 3 account)
```

### Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -q google-generativeai python-dotenv

# Create .env
echo "GEMINI_API_KEY=<your-key>" > .env
echo ".env" >> .gitignore
```

### Run the Web App (the demo)
```bash
python3 -m uvicorn app.server:app --port 8787
# open http://localhost:8787
# 1. Connect Gmail (OAuth, read-only — uses app/credentials.json)
# 2. Voice or text: "pull all my emails with Nothing and Flipkart for my Nothing Phone — there were issues"
# 3. Watch 7 agents live: intake → gmail → extract → advocate vs defense → arbiter →
#    filing → REAL Gemini Computer Use (gemini-2.5-computer-use-preview) driving a live
#    browser on consumerhelpline.gov.in → monitoring. Stops before submit (human approves).
```

### Run Full Pipeline (60 seconds)
```bash
# Run all 6 agents orchestrated
python3 orchestrate_real.py

# Show 1-minute video script
python3 video_demo_1min.py

# Interactive case input
python3 input_your_case.py

# Original demo
python3 demo.py
```

---

## Project Structure

```
src/
  core.py                       # LLM utilities (Gemini)
  antigravity_agents.py         # **NEW**: 6 agents ready to deploy
  computer_use_integration.py   # **NEW**: Real browser form filling
  
DEPLOYMENT_TO_ANTIGRAVITY.md   # **NEW**: Step-by-step deployment guide
ANTIGRAVITY_ARCHITECTURE.md    # System architecture + Problem Statement 2 alignment
orchestrate_real.py             # **NEW**: Full pipeline demo
video_demo_1min.py              # **NEW**: 1-min hackathon video script

demo.py                         # Original demo (local agents)
parse_nothing_phone_case.py    # Case analyzer (Nothing Phone example)
```

---

## 🚀 For Hackathon Judges

### This Meets Problem Statement 2

✅ **Multi-agent system** - 6 agents (not single monolith)  
✅ **Planning** - Arbiter agent makes intelligent routing decisions  
✅ **Delegation** - Agents call each other (adversarial reframe)  
✅ **Execution** - Each agent executes its role with state handoff  
✅ **Managed Agents** - Designed for Antigravity deployment  
✅ **Real workflow** - Extract → Analyze → Route → File → Monitor  

### Quick Eval (2 minutes)

```bash
python3 orchestrate_real.py
```

**Output**: All 6 agents executing, case scores, routing decision, JSON result

### Full Deployment (15 minutes)

See: `DEPLOYMENT_TO_ANTIGRAVITY.md`

1. Go to [ai.google.dev/aistudio](https://ai.google.dev/aistudio)
2. Create project
3. Follow deployment steps 1-6
4. Same code, now running on Antigravity

---

## Test Case: Priya's Chair

Real Reddit case (282 upvotes, successful NCH escalation).

**Facts**:
- Product: Sleep Co Deluxe Chair, ₹40,000
- Defect: Backrest cracked (month 4, normal use)
- Company promised: 7-10 business days to resolve
- Actual: 21 days, no resolution
- Evidence: Receipt, 3 defect photos, full support chat

**System Output**:
```
Extraction: ✓ SLA breach detected (10 vs 21 days)
Advocate: ✓ 9/10 score (deficiency-of-service angle) → ₹49k relief
Defense: ✓ 8/10 score (warranty limits, disputes timeline)
Arbiter: ✓ 88% confidence → ready_to_file (NCH-first channel)
Filing: ✓ Form staged at consumerhelpline.gov.in
Monitoring: ✓ Tracking setup, 2 active alerts
```

---

## Phase Status

- [x] **Phase 1**: Local agent testing (6 agents working, adversarial verified)
- [ ] **Phase 2**: Antigravity orchestration (wire agents in managed framework)
- [ ] **Phase 3**: Demo rehearsal (3-min live walkthrough)
- [ ] **Phase 4**: Export & backup (code + videos + deck)

---

## How It Works: The Differentiator

### 1. Adversarial Reasoning
Both sides argue in isolation. Quality gate: if case doesn't survive Defense cross-exam, we don't file.

```
Advocate: "21-day SLA breach = deficiency-of-service, ₹40k refund"
Defense: "Warranty limits remedy to repair/replacement, timeline was assessment period"
Arbiter: Scores both realistically. Neither just agrees.
```

### 2. Adaptive Routing
Instead of fixed "email → notice → court" sequence, Arbiter picks:
- **NCH-first**: Clear defect + obvious stalling → government pressure
- **Public-first**: Weak evidence but sympathetic story → social shame first, then NCH
- **Legal-notice-direct**: Company actively evading → skip mediation

### 3. Autonomous Monitoring
- Runs unattended for weeks
- Detects SLA breaches (vs company's own promises)
- Auto-drafts execution petitions if order not complied
- Verifies appeal pre-deposits (50% rule)

---

## Legal Framework

**Consumer Protection Act 2019** (CPA 2019):
- Section 2(42): "Deficiency" = failure to maintain SLA + goods not fit for purpose
- Section 2(7): Goods must be fit for ordinary purpose
- Remedy: Refund + compensation (typically ₹5k-10k for harassment)

**Escalation Path**:
1. NCH (pre-litigation, free, ~15 day SLA)
2. e-Jagriti (District Consumer Court, pro-se allowed, 3-5 months)
3. Execution petition (if company doesn't comply with court order)
4. Section 72 prosecution (criminal route for persistent non-compliance)

---

## Rate Limits & Compliance

- **Gemini 3.5 Flash**: ~10k req/min (Tier 3 account, we use <1% capacity)
- **API keys**: Never in code. Use `.env`, add to `.gitignore`.
- **Submissions**: Stops before form submit (human approval boundary)
- **Testing**: No abuse—legitimate case testing only

---

## Q&A

**Q: Isn't this just LLM + form-fill (like Voxya)?**  
A: No. Voxya runs the same 4-step sequence for every case. We do three structural things they don't: (1) adversarial cross-exam before anything files, (2) orchestrator picks channel per case based on strength, (3) autonomous filling + unattended monitoring. Different system.

**Q: What if the system files a false claim?**  
A: Defense Agent is the quality gate. If the case doesn't survive adversarial critique, we don't file. This protects users (no wasted time) and system credibility (fewer frivolous filings).

**Q: How long until resolution?**  
A: Typical timeline: 3-6 months (NCH ~15 days + e-Jagriti ~90+ days). But alternative is do nothing and lose forever. System removes the attrition problem (companies betting you'll get tired).

---

## Numbers (For Pitch)

- **NCH complaints/month (2025)**: 1.7 lakh (vs 37k in 2017, 4.6x growth)
- **Avg refund per case**: ~₹8,000
- **Market**: ₹32 crore recovered (Apr-Dec 2025, 40k cases)
- **Incumbent (Voxya)**: 2 employees, ~₹58L/yr revenue (0.01% coverage of demand)

---

## Team

Built for Google DeepMind Bangalore Hackathon, July 2026.

---

## License

Internal / Hackathon Project

---

## Files & References

- **Full architecture**: See `PHASE1_SUMMARY.md`, `PHASE2_PLAN.md`
- **Legal reference**: CPA 2019 § 2(42), E-Commerce Rules 2020 § 4
- **NCH portal**: https://consumerhelpline.gov.in/
- **e-Jagriti**: https://e-daakhil.gov.in/
- **Test case (Priya's chair)**: https://reddit.com/r/india (282 upvotes, successful escalation)

---

**One-liner pitch**: "Companies bet you'll get tired before they have to pay. This agent doesn't get tired."
