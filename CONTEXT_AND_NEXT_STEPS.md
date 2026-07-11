# Project Context & Next Steps — Consumer Warranty Escalation Agent
**Last updated**: 2026-07-11  
**Status**: Architecture locked, ready to build  
**Hackathon**: Google DeepMind Bangalore, Track 2 (Autonomous Orchestration with Managed Agents / iAPI)

---

## What Are We Building? (1-minute version)

A multi-agent system that fights back when a company stonewalls your legitimate warranty claim. You upload proof (receipt, chat thread, defect photo), the system:
1. Argues both sides internally (Advocate vs Company Defense)
2. Detects if the company is deliberately stalling (SLA breach detection)
3. Files with the government (NCH → e-Jagriti)
4. Pursues non-payment automatically (execution petition)

All automated, human-approval gates for safety, runs unattended across days/weeks.

---

## Why This Wins (Scoring breakdown)

| Category | Weight | Our Approach | Score |
|----------|--------|--------------|-------|
| **Creativity/Originality** | 35% | Adversarial cross-exam + adaptive routing (no other player does both) | 8-9/10 |
| **Impact in India** | 25% | 1.7L complaints/month to NCH, ~₹8k refund per case, real govt channel | 8/10 |
| **Live Demo** | 25% | Two agents arguing on screen, then real filing, then enforcement | 8/10 |
| **Technical Depth** | 15% | 6 agents, persistent state, SLA tracking, browser automation | 7/10 |
| **Overall** | 100% | **~80/100** — strong contender |

---

## Key Decisions Made

### ✅ Locked in: Single vertical (consumer warranty only)
- **Why**: "we do too much" feedback → scope down, build deep instead of wide
- **What we dropped**: MSME delayed-payment spoke, insurance mis-selling spoke (both valid but would dilute focus)
- **What we kept**: warranty via NCH → e-Jagriti, full end-to-end

### ✅ Locked in: The 6-agent architecture
1. **Extraction** — parse receipt/chat/warranty card → structured case
2. **Consumer Advocate** — build strongest legal claim
3. **Company Defense** (adversarial) — attack the Advocate's case
4. **Arbiter/Orchestrator** — score case, route to channel
5. **Filing** — autonomous form-fill on real government portals
6. **Monitoring** — track SLA, compliance, auto-escalate

This is the differentiator vs Voxya (the incumbent, 2-person, unfunded). We do adversarial + adaptive routing, they do fixed 4-step playbook.

### ✅ Locked in: Demo script (3 minutes)
See `WARRANTY_AGENT_BUILD_SPEC.md`, section "Demo Choreography" — cold open on a human story, centerpiece is live Advocate vs Defense debate, close on enforcement narrative.

---

## Immediate Next Steps (Priority Order)

### Phase 1: Local Agent Testing (Today, ~3-4 hours)
1. **Set up environment**:
   ```bash
   cd /home/alex_hunterz/Desktop/projects/google-deepmind-hack-dieas/
   python3 -m venv venv_warranty
   source venv_warranty/bin/activate
   pip install google-generativeai python-dotenv selenium playwright
   
   # Set up .env (don't commit this)
   echo "GEMINI_API_KEY=your_tier_3_key_here" > .env
   echo ".env" >> .gitignore
   ```

2. **Write agent prompts** (templates in `WARRANTY_AGENT_BUILD_SPEC.md`, section "Agent Prompts"):
   - Create file: `agents/extraction_agent.py`
   - Create file: `agents/advocate_agent.py`
   - Create file: `agents/defense_agent.py`
   - Create file: `agents/arbiter_agent.py`
   - Create file: `agents/filing_agent.py`
   - Create file: `agents/monitoring_agent.py`

3. **Test each agent in isolation** with hard-coded test case (Priya's chair — Sleep Co warranty claim, real reddit thread, 282pts):
   ```python
   # Example test
   from agents.extraction_agent import extract_case
   
   test_case = {
       "receipt": "chair_receipt.jpg",
       "defect": "backrest_cracked.jpg",
       "email_thread": "support_chat.txt"
   }
   
   result = extract_case(test_case)
   print(result)  # Should output structured JSON
   ```

4. **Verify Advocate/Defense produce different outputs** (not just agreeing):
   ```python
   from agents.advocate_agent import advocate
   from agents.defense_agent import defense
   
   advocate_draft = advocate(case_obj)
   defense_counter = defense(case_obj, advocate_draft)
   
   assert advocate_draft["requested_relief"] != defense_counter["company_position"]
   ```

### Phase 2: Orchestration in Antigravity (Next, ~2-3 hours)
1. **Connect to Antigravity**:
   - Open Antigravity UI
   - Click the **grey line under OAuth** (not the button)
   - Select temp account
   - Enter project ID from `aistudio.google.com/projects`

2. **Define agent roles in Antigravity**:
   - Each agent is a "node" in the orchestration graph
   - Arbiter (Agent 4) is the router — it decides which agent goes next

3. **Wire the full pipeline**:
   - Extraction → Advocate + Defense (parallel)
   - Defense output → Arbiter
   - Arbiter output → Filing (if approved)
   - Filing output → Monitoring (if filed)

4. **Test end-to-end** with Priya's case:
   - Upload case files → Extraction parses them → Advocate drafts → Defense attacks → Arbiter decides → Filing fills real NCH form (pre-auth) → stops before submit

### Phase 3: Demo Rehearsal (Before final day, ~2 hours)
1. **Run the full flow live** (or with fallback video):
   - Have pre-recorded 10-second video of a real NCH form-fill (backup if gov site is slow)
   - Have pre-recorded 30-second video of e-Jagriti filing and order issuance (time-skip simulation)

2. **Practice the 3-minute talk**:
   - 0:00-0:20 — Priya's story (cold open, no slides)
   - 0:20-0:35 — Extraction parsing on screen
   - 0:35-1:20 — **Advocate vs Defense debate** (the centerpiece, don't rush)
   - 1:20-1:50 — Filing at NCH live (or fallback video)
   - 1:50-2:20 — Time-skip to SLA breach detection + auto-escalation
   - 2:20-2:50 — Post-order enforcement (execution petition draft)
   - 2:50-3:00 — Numbers + Voxya comparison, close

3. **Prepare Q&A answers**:
   - "Isn't this Voxya?" → See `WARRANTY_AGENT_BUILD_SPEC.md`, section "Q&A Drills"
   - "Does this replace lawyers?" → See same section
   - "Doesn't CPA 2019 not penalize false complaints?" → See same section

### Phase 4: Export & Save (End of Day 2, **CRITICAL**)
- Account deletes next day after hackathon
- Push all code to GitHub (with `.env` in `.gitignore`)
- Download Antigravity configs
- Save all demo videos and slides
- You have ~1 hour after final judging — don't skip this

---

## Key Files & Paths

| File | Path | Purpose |
|------|------|---------|
| **Build Spec** | `helper-agent/WARRANTY_AGENT_BUILD_SPEC.md` | Complete architecture, demo script, prompts, Q&A, compliance checklist |
| **Research** | `research/MASTER-IDEAS.md` | Full ideation + prior-art analysis (not needed for build, but good for Q&A prep) |
| **Code** | `src/agents/*.py` | Each of 6 agents (you write these) |
| **Main orchestration** | `src/main.py` | Orchestrator + Antigravity integration (you write this) |
| **Tests** | `tests/test_agents.py` | Unit tests for each agent (write as you go) |
| **Demo fallback videos** | `demo/fallback/*.mp4` | Pre-recorded portions of the live demo (record before Day 2 end) |

---

## Temp Hackathon Account Setup

**Already done** (if not, do now):
1. Get Tier 3 API key from `aistudio.google.com/api-keys`
2. Create `.env` file with `GEMINI_API_KEY=...`
3. Connect Antigravity (grey line method, not OAuth button)

**Rate limits** (don't exceed):
- Gemini 3.5 Flash: ~10k req/min (you won't hit this)
- Reasonable daily budget: ~300-400 API calls across full 2-day hackathon ← you're safe

**Don't abuse**:
- No hardcoded API keys in GitHub
- No thousands of parallel requests
- If flagged, you're disqualified

---

## The Numbers (For Pitch/Q&A)

- **NCH complaints/month (2025)**: 1.7 lakh (up 4.6x from 37k/month in 2017)
- **E-commerce refunds recovered (Apr-Dec 2025)**: ₹32 crore across 40k complaints
- **Average refund per case**: ~₹8,000
- **Incumbent (Voxya)**: 2 employees, ~₹58L/yr revenue → implies 200-300 cases/yr vs 1.7L/month = 0.01% coverage
- **CPA 2019 gap**: No strong penalty for frivolous complaints (your Defense Agent handles this)

Use these on stage. They're real, cited, and devastating to the "no one needs this" objection.

---

## Architecture Quick Reference

```
Input: photos/chat thread of warranty claim + rejection
         ↓
    [Extraction Agent]
         ↓
    [Advocate Agent] ←→ [Defense Agent]  ← Argue both sides
         ↓
    [Arbiter]  ← Score case, pick channel
         ↓
    [Filing Agent]  ← Fill NCH/e-Jagriti form, human approves
         ↓
    [Monitoring Agent]  ← Track SLA, compliance, auto-escalate
         ↓
Output: case filed + tracked until payment/resolution
```

---

## Legal Chain (For Q&A Prep)

1. **Company ignores your complaint** → NCH (free, pre-litigation, ~15 day SLA)
2. **NCH doesn't resolve** → e-Jagriti (formal consumer court, 3-5 month hearing, pro-se allowed, no lawyer required)
3. **Court orders refund** → 30-day compliance window
4. **Company doesn't pay** → Execution petition (can force payment via attachment/garnishee, or Section 72 criminal route)
5. **Company appeals** → They must pre-deposit 50% of awarded amount (exists to block frivolous appeals)

Full detail: see `WARRANTY_AGENT_BUILD_SPEC.md`, section "Legal Chain Reference".

---

## Gotchas & How to Avoid Them

| Gotcha | How to Avoid |
|--------|-------------|
| **Gov website down during demo** | Pre-record a 10-sec fallback of a real filing, label it clearly, narrate over it live |
| **API key leaked to GitHub** | Use `.env`, add to `.gitignore`, check git history before pushing |
| **Advocate + Defense both agree** | Deliberately make Defense argue the company's real position, not invent strawmen |
| **Case too weak to file** | Arbiter loops back to Extraction ("we need more evidence"), don't force-file weak cases |
| **Account deletes before export** | Save everything (code, videos, demos) before end of Day 2. Account dies next day. |
| **"Just Voxya with LLM"** | Lead demo on the Advocate vs Defense debate (not form-fill), emphasize adaptive routing + SLA detection |

---

## Success Metrics (How to Know You're On Track)

**By end of Phase 1 (Day 1, ~4-5 hours)**:
- ✅ Each of 6 agents works in isolation with test case (Priya's chair)
- ✅ Advocate and Defense produce different outputs (not just agreeing)
- ✅ Arbiter correctly scores and routes

**By end of Phase 2 (Day 1-2, ~8 hours)**:
- ✅ Full pipeline works end-to-end in Antigravity
- ✅ Filing Agent fills real NCH form (pre-auth)
- ✅ Monitoring Agent tracks time correctly

**By end of Phase 3 (Day 2, ~10 hours)**:
- ✅ Demo runs in 3 minutes, all beats hit on time
- ✅ Advocate vs Defense debate is visually compelling
- ✅ Fallback videos are ready in case live site fails

**Before submission**:
- ✅ All code pushed to GitHub (no API keys)
- ✅ Videos + deck exported (account deletes tomorrow)
- ✅ Q&A drills rehearsed

---

## Links & References

- **Build Spec**: `helper-agent/WARRANTY_AGENT_BUILD_SPEC.md` (complete, start here)
- **Research**: `research/MASTER-IDEAS.md` (for Q&A context, not needed to build)
- **NCH**: https://consumerhelpline.gov.in/
- **e-Jagriti**: https://e-daakhil.gov.in/
- **CPA 2019**: https://consumerprotection.in/
- **Temp account guide**: https://goo.gle/hackathon-account (you have this already)

---

## One-Liner Pitch (Memorize This)

> "Companies bet you'll get tired before they have to pay. This agent doesn't get tired."

---

**Next session**: Open `helper-agent/WARRANTY_AGENT_BUILD_SPEC.md`, start Phase 1 (write the 6 agent prompts, test in isolation). You have ~18 hours left.

Good luck.
