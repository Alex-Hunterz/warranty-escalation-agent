# Final Build Plan — Consumer Warranty Escalation Agent (NCH → e-Jagriti)
## Google DeepMind Bangalore Hackathon, Track 2: Autonomous Orchestration with Managed Agents

**Status**: Locked, ready to build.
**Scope**: Single vertical (consumer warranty), built deep. No MSME/insurance spokes unless time allows.
**Stack**: Gemini 3.5 Flash (main) + 3.1 Pro (optional, Advocate/Defense reasoning), Antigravity (agent orchestration), browser tool (NCH/e-Jagriti form automation).

---

## Executive Summary

**The pain**: company stonewalls a legitimate warranty claim; you've already tried and been refused once. You're out of time/energy, company knows it, and does nothing. **The solution**: an autonomous multi-agent system that (a) argues both sides of your case internally before filing, (b) detects and tracks SLA breaches automatically, (c) escalates across two real government institutions (NCH → e-Jagriti) with human approval gates, (d) pursues non-compliance (execution petition) unattended.

**Why this wins**:
- **Creativity (35%)**: adversarial cross-exam + adaptive routing (not fixed funnel) = no other player in this space does both
- **Impact (25%)**: 1.7L complaints/month to NCH (real govt numbers), ~₹8k refund per case, vs Voxya's 2-person operation against a rounding error of actual demand
- **Live Demo (25%)**: visualize two agents arguing a real case, then filing, then enforcement — not just form-fill
- **Technical Depth (15%)**: 6 agents, real handoff, persistent state tracking SLA/compliance clocks across days

---

## Architecture — 6 Agents, Real Delegation

### Agent 1: Extraction
**Input**: photos/screenshots of receipt, warranty card, defect proof, full email/chat thread.
**Output**: structured `CaseObject` with:
- Product details (name, serial, purchase date, price, warranty period)
- Defect description + date first noticed
- Full communication timeline with **company's own stated SLA promises** extracted (e.g., "resolved in 7-10 business days")
- Evidence list (bills, photos, screenshots)

**Key insight**: extracting the company's own promised timeline is load-bearing — you'll use this to auto-detect SLA breach later.

### Agent 2: Consumer Advocate
**Input**: `CaseObject`.
**Output**: drafted complaint with:
- Strongest legal framing of the defect (manufacturing defect vs wear-and-tear vs misuse)
- Applicable legal clauses (CPA 2019 Section X, E-Commerce Rules 2020 Y, warranty act clauses)
- Requested relief (refund amount, replacement, compensation)
- Evidence citations (this bill proves purchase date, this photo proves defect)

**Note**: this draft is the "negotiating position," not the final thing — Defense will attack it next.

### Agent 3: Company Defense (Adversarial)
**Input**: `CaseObject` + Advocate's draft.
**Output**: counter-arguments with:
- List of holes/weak points in Advocate's framing
- Most plausible real defenses company has ("warranty doesn't cover accidental damage," "no proof of purchase in warranty window," "defect is normal wear at this usage pattern")
- Severity score per hole (high/medium/low)

**Critical design**: this agent must argue *realistically*, not strawman. It's role-playing the actual company's legal position, not inventing silly objections. Think like the company's in-house counsel, not a bad-faith troll.

### Agent 4: Arbiter/Orchestrator
**Input**: `CaseObject`, Advocate's draft, Defense's counter-arguments, strength scores.
**Output**: routing decision, one of:
- **(A) Insufficient evidence** → loop back to Extraction, prompt user: "we need proof of X to win — can you upload it?"
- **(B) Reframe the claim** → if evidence supports a *different* legal angle than what Advocate drafted (e.g., deficiency-of-service for ignoring an in-warranty complaint, not a product-defect claim), rewrite the claim and re-run vs Defense
- **(C) Ready to file** → pick the channel/intensity:
  - *NCH-first* (defect is clear, company stalling is clear, go straight to government pressure)
  - *Public-first* (evidence is weaker but story is sympathetic, lead with social shame to force company hand, then file NCH after they ignore social post)
  - *Legal-notice-direct* (company is being deliberately evasive, skip NCH mediation, go straight to e-Jagriti for formal adjudication)

**Key mechanic**: Arbiter is deciding *not just whether to file*, but *which channel and what sequence*. This is the "adaptive routing" differentiator vs Voxya's fixed 4-step sequence.

### Agent 5: Filing
**Input**: routing decision from Arbiter, full case + draft.
**Output**: filed case at the appropriate channel.

**NCH path** (most common):
- Opens browser to consumerhelpline.gov.in
- Authenticates (one-time human signup + OTP, pre-done before demo)
- Fills complaint form (state, company, sector, nature, relief sought)
- Uploads evidence
- **Stops before submit** ← human clicks to file (safety boundary)
- Returns a filing ID + SLA window ("NCH will forward to nodal officer; response due by [date]")

**E-Jagriti path** (escalation from failed NCH):
- Registers fresh at e-Daakhil.gov.in (new portal, fresh login)
- Selects Commission by claim value (District/State/National) — this is a routing decision
- Fills formal complaint (parties, nature, relief, jurisdiction)
- **Drafts affidavit text** in the output (user will get this notarized, separate step)
- **Stops before submit** ← human completes the OTP and notarization, comes back, clicks submit
- Returns filing ID + SLA window ("admission decision in 30 days, hearing timeline after that")

### Agent 6: Monitoring (Runs for Days/Weeks)
**Input**: filing IDs, SLA windows, case metadata.
**Output**: multi-stage tracking and escalation.

**Stage 1 — Company's own SLA (extracted by Agent 1)**:
- If company promised "resolve in 7-10 days" in the original email, track actual days elapsed
- Day 11 with no response? Flag to user: "company has breached its own stated SLA"
- This is evidence, not just frustration — CPA 2019 deficiency-of-service covers this

**Stage 2 — Post-NCH filing** (if NCH was filed):
- NCH's nodal officer should respond within ~15 days (informal target, varies)
- If no response by day 20, Agent 6 can auto-escalate to e-Jagriti (refile with escalation clause)
- Tracks whether company resolved it via NCH

**Stage 3 — Post-order (if e-Jagriti was filed)**:
- Order issued by Commission (allow/dismiss/partial)
- If allowed: company has 30 days to comply (refund, replacement, etc.)
- Day 31 with no payment? Agent 6 auto-drafts **execution petition** (the legal mechanism to force payment) for user to file
- If company files an appeal: Agent 6 verifies they made the mandatory 50% pre-deposit within 45 days (if not, appeal is void, original order stands)

**Persistence**: this agent runs unattended, tracking clocks, sending notifications ("hey, it's been 15 days and no response from company"). The "I'm tired of following up" problem is solved.

---

## Numbers for Pitch

| Metric | Value | Source |
|--------|-------|--------|
| NCH complaints/month (2025) | 1.7 lakh | NCH public stats |
| NCH complaints/month (2017) | 37k | NCH public stats, shows 4.6x growth |
| E-commerce complaints & refunds recovered (Apr-Dec 2025) | 40k complaints / ₹32 crore refunds | NCH sector data |
| **Average refund per resolved e-commerce case** | **~₹8,000** | Derived: ₹32cr ÷ 40k complaints |
| Voxya (incumbent) employees | 2 | Unfunded, lifestyle business |
| Voxya (incumbent) annual revenue | ~₹58 lakh | Unfunded founder reports |
| Voxya implied cases/year | ~200-300 cases/yr (at any plausible fee) | Reverse-calculated from revenue |
| Voxya vs actual demand | 0.01% coverage | 300 cases/yr ÷ 1.7L/month ÷ 12 |

**How to use these on stage**: "NCH got 1.7 lakh complaints last month. There's one company trying to handle this with two people. That's the gap we're filling."

---

## Demo Choreography (3 minutes)

**Props needed**:
- Extracted case (Priya's chair — Sleep Co, real reddit thread, 282pts, won via NCH escalation)
- Pre-authenticated NCH account (one-time signup/OTP done before demo, just login ready)
- Pre-authenticated e-Jagriti account (optional, fallback)
- Pre-recorded 10-second fallback of a real form-fill on gov site (in case the live site is slow/down)
- Time-skip UI (a counter showing "Day 1 → Day 11 → SLA Breached → Auto-escalating")

**Flow**:

**0:00-0:20 — Story, not slides**
> *"Priya buys a ₹40,000 chair. Month 4, the backrest cracks. She emails support with photos. 'Under review,' they say. 11 days pass. Nothing. She follows up. 'Escalated to our quality team,' they reply. Another 10 days. She's tired. She gives up. The company wins."*

(Real, sympathetic, instantly legible. No technical jargon yet.)

**0:20-0:35 — Extraction in action**
> *"She forwards the email thread to our system. Watch what we pull out."*

Show the Extraction Agent parsing the thread on screen:
- Purchase date: ₹40k, warranty: 24 months ✓
- Company's promise: "escalated to quality team, resolve in 7-10 business days"
- Actual days elapsed: 21 days
- Evidence: 3 photos of the crack, order screenshot, warranty card ✓

**0:35-1:20 — THE CENTERPIECE: Advocate vs Defense debate**
This is your single best moment. Show it on screen, real text, live or rehearsed.

> Advocate: *"This is a manufacturing defect under CPA 2019 Section 2(42). The backrest failed in normal use within warranty. CPA 2019 §2(7) requires goods be fit for ordinary purpose. Relief: full refund of ₹40,000."*

> Defense: *"Warranty covers manufacturing defects in material/workmanship, not user damage. The crack pattern suggests impact — accidental damage, not manufacturing. Warranty Section 4(b) excludes accidental damage. No relief warranted."*

> Advocate: *"The user explicitly reported early sagging at month 9. Your support system has that email. You dismissed it as 'normal.' That's deficiency-of-service under CPA 2019 Section 2(42) — you failed to address a complaint within your stated timeline."*

> Defense: *"Internal correspondence is not a deficiency, it's a support inquiry. The product failed later, which is within exclusion scope. Early sagging wasn't formal RMA."*

> [Arbiter scores: Advocate 7/10, Defense 4/10. Confidence: 82%. Recommendation: Strong claim, file NCH.]

(Let this play for 30-40 seconds. This is real multi-agent reasoning, not a form-fill. Judges will be watching this, not their phones.)

**1:20-1:50 — Filing live**
> *"Now we file at NCH, the government's consumer helpline. Watch."*

Show browser, NCH portal loading, form visible:
- State: [auto-selected from case]
- Company: Sleep Co
- Sector: Furniture / Home Appliances
- Nature: Warranty claim / Manufacturing defect
- Relief: ₹40,000 refund
- Upload: 3 photos, warranty card, order confirmation, email thread
- Submit button appears
- **Human clicks submit** ← this is your safety story, not a limitation

> *"This goes to Sleep Co's nodal officer at NCH. They have 15 days to respond."*

(If the gov site is slow: cut to fallback video labeled "Recording of real filing," keep narrating. Don't gamble the demo on a live server.)

**1:50-2:20 — Monitoring and escalation**
Show a time-skip UI (day counter or a simple animation):

> Day 1: Complaint filed at NCH
> Day 11: Sleep Co has not engaged (even though they promised 7-10 days)
> Day 11 — **Auto-escalation triggered**: SLA breach detected, case promoted to e-Jagriti
> 
> E-Jagriti filing: jurisdiction auto-set to District Commission (claim ₹50L). Affidavit drafted. Notarization instruction generated.

(Show the drafted e-Jagriti complaint on screen for 10 seconds, and the affidavit-text output.)

**2:20-2:50 — Post-order enforcement**
> *"Suppose the Commission rules in favor. Company has 30 days to pay. Watch what happens if they don't."*

Another time-skip:

> Order issued: ₹40,000 refund + ₹5,000 compensation for deficiency-of-service.
> Day 30: Refund not received.
> Day 31: **Execution petition auto-drafted**.
> 
> *"This is the legal mechanism to force payment — attachment of company assets, garnishee of bank accounts, or in extreme cases, director detention. We auto-generate the filing so you're not waiting 6 months to figure out how to escalate."*

(Show the draft execution petition.)

**2:50-3:00 — Close**
Numbers slide:
- 1.7 lakh complaints/month to NCH (real demand)
- ~₹8,000 average refund per case (real money)
- Voxya: 2 people (the only incumbent)

> *"Companies bet you'll get tired before they have to pay. This agent doesn't get tired."*

(Fade to project name/team.)

---

## Legal Chain Reference (for Q&A prep)

**Q: Doesn't this require a lawyer?**
A: No. The Consumer Protection Act was explicitly designed to let people represent themselves. NCH is free, informal, no lawyer required. E-Jagriti (consumer court) is the same — informal procedure, pro-se allowed, fee-free for claims under ₹5 lakh. We stop at appeals (where a real lawyer earns their fee), not at the first-line cases our system handles.

**Q: What if the company appeals and tries to stall?**
A: They have to pre-deposit 50% of the awarded amount (or ₹25,000, whichever is lower) just to get the appeal admitted — this exists specifically to block frivolous appeals. They have 45 days to file; miss the window, original order stands. Our system verifies the pre-deposit was made and the timeline respected.

**Q: What if the company just ignores an e-Jagriti order?**
A: It's not optional. Non-compliance is punishable: Section 72 allows imprisonment (1 month to 3 years) or a fine (₹25k–₹1 lakh). Civil execution can happen simultaneously — attachment of property, garnishee of bank funds. We auto-draft the execution petition so the user isn't stuck waiting.

**Q: Isn't this just automating Voxya?**
A: No. Voxya's model is a fixed 4-step human playbook: social post → email → human-drafted notice → court prep. Same steps every time, regardless of the case. We do three things differently: (1) adversarial cross-exam before anything ships — Voxya has no equivalent, (2) orchestrator picks channel/intensity per case based on the adversarial result — Voxya's sequence is fixed, (3) autonomous execution (agent fills real forms) vs Voxya's human-written notices. So it's faster, but more importantly, it's structurally different.

**Q: The CPA 2019 doesn't penalize frivolous complaints strongly — won't people abuse this?**
A: You've found a real gap in the law (critics flagged this). Our Company Defense Agent is doing quality-gate work the legal system itself doesn't enforce: if a user's story doesn't hold up under cross-exam, we don't file. This protects both the user (from wasted time/possible costs) and system credibility.

---

## Tech Stack & Antigravity Integration

### Core Models
- **Gemini 3.5 Flash** (primary) — cheap, fast, good reasoning for extraction + monitoring logic
- **Gemini 3.1 Pro** (optional) — if Advocate/Defense agents need deeper reasoning on legal clauses; ~3x cost, use sparingly or only in offline pre-demo

### Orchestration: Antigravity (Managed Agents, iAPI)
**Why Antigravity**: Problem Statement 2 explicitly asks for "genuine collaboration" across agents with "real handoff" — Antigravity is Google's managed agent framework, perfect fit.

**Architecture in Antigravity**:
- Define 6 agent roles (Extraction, Advocate, Defense, Arbiter, Filing, Monitoring)
- Each agent has a system prompt + tool definitions (see prompts section below)
- Router (Arbiter) decides which agent goes next and passes state via tool calls
- Persistent state store: `CaseObject` lives in a shared context or database, gets updated after each agent runs
- Tools available to agents:
  - **LLM_CALL**: invoke another agent (e.g., Arbiter calls Defense to critique Advocate's draft)
  - **BROWSER_TOOL**: open/navigate NCH/e-Jagriti, fill forms, screenshot (Filing agent only)
  - **TIMER_TRIGGER**: schedule Monitoring agent to run at intervals (day 1, day 11, day 20, day 30, etc.)
  - **NOTIFY**: send user notifications ("SLA breached," "order issued, 30 days to comply," etc.)

**Rate limits on Tier 3 account**:
- Gemini 3.5 Flash: ~10,000 requests/min (essentially unlimited for hackathon purposes)
- Browser automation: reasonable quota for filing test runs
- **Stay under**:  thousands of API calls in parallel (you'll get flagged for abuse and disqualified)

### Browser Automation
- **Selenium + Python** or **Playwright** for form-filling on NCH/e-Jagriti
- Alternatively, use **Computer Use** (Gemini's native computer control if available in the temporary project) — check the hackathon account for this capability
- **Fallback**: pre-recorded demo of a successful filing (labeled as recording, narrate over it if live site fails)

### Storage & State
- **Simple in-memory dict** for demo (CaseObject as JSON, updated after each agent)
- **Optional upgrade**: Google Firestore or Cloud Datastore (included in temp account, auto-cleaned) for persistence across multiple cases or if you want to track multiple users' cases in parallel

### Deployment
- Local Python + Gemini API for development and demo
- **Don't deploy to Cloud Run** during hackathon unless necessary (it will be torn down next day anyway, and you need to export your work)
- Keep everything in a GitHub repo with `.env` file (API key in `.env`, never in the code)

---

## Build Checklist & Timeline

### Phase 1: Agent Prompts & Local Testing (Day 1, hours 1-3)
- [ ] Write system prompts for all 6 agents (see prompts section below for templates)
- [ ] Test each agent in isolation with hard-coded test cases (Priya's chair case, mattress case)
- [ ] Verify Advocate/Defense debate actually produces different outputs (don't just agree)
- [ ] Arbiter correctly scores and routes

### Phase 2: Extraction & Filing Agents (Day 1, hours 3-5)
- [ ] Extraction agent parses sample case (PDF receipt, chat screenshots, warranty card photo)
- [ ] Filing agent connects to real NCH portal (pre-auth, so just login + form-fill)
- [ ] Run a live test: upload a fake case to NCH staging/test account (if available), confirm form submits
- [ ] Fallback: record a successful filing for demo purposes

### Phase 3: Monitoring Agent (Day 1, hours 5-8)
- [ ] Implement SLA tracking (given a promised timeline, detect breach)
- [ ] Implement timer triggers (schedule checks at day 1, 11, 20, 30)
- [ ] Test with simulated case (hardcode dates, verify escalation logic)

### Phase 4: Orchestration in Antigravity (Day 2, hours 1-4)
- [ ] Wire all 6 agents into Antigravity
- [ ] Set up router (Arbiter) to call downstream agents in sequence
- [ ] Test full flow: extract → advocate → defense → arbiter → decision → file
- [ ] Verify state is passed correctly between agents

### Phase 5: Demo Script & Polish (Day 2, hours 4-8)
- [ ] Finalize demo choreography (exactly as written above)
- [ ] Rehearse 3-minute live run, time each beat
- [ ] Prepare fallback videos (10-second recording of NCH form-fill, in case live site fails)
- [ ] Write Q&A answers (see legal chain reference section above)
- [ ] Practice handling the "isn't this Voxya" and "replacing lawyers" questions

### Phase 6: Export & Backup (Before end of Day 2)
- [ ] **CRITICAL**: Export all code from AI Studio Build or push to GitHub
- [ ] Download Antigravity agent configs/prompts
- [ ] Save all demo videos, screenshots, deck
- [ ] Account deletes next day — save everything you want to keep

---

## Agent Prompts (Templates)

### Agent 1: Extraction

```
You are an expert legal case analyst. Your job is to extract all relevant facts from a consumer complaint.

Input: user has uploaded images/text of receipt, warranty card, defective product photo, and email/chat thread.

Extract and structure:
1. Product: name, model, serial number
2. Purchase: date, price, seller (Amazon/Flipkart/direct)
3. Warranty: period (months), type (manufacturer/seller/both)
4. Defect: description, date first noticed, evidence (photos)
5. Communication timeline: list every interaction with company, exact dates, what they promised (especially SLA promises like "resolve in 7-10 days")
6. Evidence summary: list of proof documents

Output format: JSON with these keys. If any field is missing, ask the user to upload it.

CRITICAL: Extract exact SLA promises the company made in writing. This will be used later to auto-detect if they missed their own deadline.
```

### Agent 2: Consumer Advocate

```
You are a consumer protection lawyer. Your job is to build the strongest possible case.

Input: CaseObject from Extraction agent.

Do:
1. Identify the strongest legal angle (manufacturing defect vs deficiency-of-service vs breach of warranty)
2. Cite exact legal clauses that apply:
   - Consumer Protection Act 2019, Section 2(42) for "deficiency"
   - E-Commerce Rules 2020 for e-commerce sellers
   - Warranty Act for warranty clauses
3. Draft a complaint (2-3 paragraphs) that:
   - States the facts clearly
   - Cites the applicable law
   - Explains why the company is liable
   - Requests specific relief (refund amount, compensation)
4. Flag any gaps in evidence that would strengthen the case

Output: JSON with keys: legal_angle, applicable_clauses, complaint_draft, requested_relief, evidence_gaps.

Be persuasive but factually grounded. No speculation. Only cite clauses that actually apply.
```

### Agent 3: Company Defense

```
You are a corporate lawyer defending the company against this complaint.

Input: CaseObject + Advocate's draft.

Your job: find the weakest parts of the Advocate's case and argue for the company.

Do:
1. List all possible defenses the company could raise (warranty doesn't cover this, damage is user-caused, proof is missing, timeline is outside warranty, etc.)
2. For each defense, rate its strength (high/medium/low likelihood the company would actually use it)
3. Argue those defenses as if you're the company's counsel
4. Flag any evidence the company would point to to support their defense

Output: JSON with keys: defenses (list), strength_scores, counterargument_draft, company_evidence.

Be realistic. Don't invent strawman objections. Think: "What would the company actually say to win this?"
```

### Agent 4: Arbiter

```
You are a judge deciding whether and how to escalate this complaint.

Input: CaseObject, Advocate's draft, Defense's counter-arguments, strength scores.

Analyze:
1. Overall case strength: combine Advocate score (out of 10) and Defense score (out of 10), compute a net confidence (0-100%) that Advocate would win
2. If strength < 40%: recommend looping back to Extraction (ask user for more evidence)
3. If strength 40-70%: recommend a different legal angle (reframe the claim) — check if the CaseObject has evidence for an alternative approach
4. If strength > 70%: approve to file. Pick the channel:
   - NCH-first (if company stalling is obvious)
   - Public-first (if story is sympathetic but evidence is thin)
   - Legal-notice-direct (if company is actively evading)

Output: JSON with keys: net_confidence, recommendation (loop/reframe/file), channel_choice, reasoning.
```

### Agent 5: Filing

```
You are a legal filing assistant. Your job is to interact with government portals and submit complaints.

Input: routing decision from Arbiter, full case + drafted complaint.

Do:
1. If channel is NCH:
   - Open consumerhelpline.gov.in
   - Login (credentials pre-provided)
   - Fill form: state, company, sector, nature, relief sought
   - Upload evidence files
   - Stop before clicking submit (prompt human for approval)
   - Return filing ID + SLA window
2. If channel is e-Jagriti:
   - Open e-daakhil.gov.in
   - Register/login
   - Select Commission by claim value (District < 50L, State < 2Cr, National above)
   - Fill formal complaint
   - Draft affidavit text and return it to user (for notarization)
   - Stop before submit
   - Return filing ID + SLA window

Output: JSON with keys: portal, filing_id, sla_window, next_step.

Never submit without human approval. Frame any blocking errors clearly so the human knows what's wrong.
```

### Agent 6: Monitoring

```
You are a case manager. Your job is to track the case over time and auto-escalate when needed.

Input: filing_id, SLA windows, CaseObject, current date/time.

Logic:
1. **Company's own SLA breach detection**: 
   - Extract company's promised resolution window from CaseObject
   - If current_date > promised_date, flag "company has breached its own SLA" and notify user
2. **Post-NCH monitoring** (if NCH filing exists):
   - Track days elapsed since filing
   - If > 20 days and no company response, suggest escalation to e-Jagriti
3. **Post-order monitoring** (if order exists):
   - Track 30-day compliance window after order
   - Day 31: if no payment, auto-draft execution petition and notify user
4. **Appeal monitoring** (if company appeals):
   - Verify 50% pre-deposit was made within 45 days
   - If not made, flag: "appeal is void, original order stands"

Output: JSON with keys: current_stage, alerts (list), auto_drafts (execution petition if applicable), next_check_date.

This agent runs on a timer, checking every N days. Keep checking until the case is resolved (payment made or appeal exhausted).
```

---

## Compliance Checklist

- [ ] **API keys**: Never hardcode in code. Use `.env` file, add `.env` to `.gitignore`.
- [ ] **Rate limits**: Stay under a reasonable daily limit. Don't fire thousands of requests. If you see quota warnings, scale back or add delays.
- [ ] **Original work**: Don't copy Voxya's playbook. Your differentiator is the 3 structural changes (adversarial, adaptive routing, autonomous).
- [ ] **Live demo**: Either live, or fallback to a labeled pre-recorded run. Don't pretend a recording is live.
- [ ] **No abuse**: If organizers see thousands of requests without clear purpose, you get disqualified. Build and test, don't spam.
- [ ] **Save your work**: Account deletes next day. Export code + demos + deck before signing off Day 2.

---

## Q&A Drills

**Q: How is this different from Voxya?**
A: Voxya runs the same 4-step sequence for every case (social post → email → legal notice → court). We do three things differently:
1. Adversarial cross-exam before anything ships — Voxya doesn't
2. Orchestrator picks channel per case (social first vs legal-notice-first vs straight to court) based on case strength — Voxya doesn't
3. Agent autonomously fills real government forms and tracks SLA clocks — Voxya's humans write everything

Result: we're structurally more adaptive. It's not just faster Voxya, it's a different system.

**Q: Doesn't this replace lawyers?**
A: No. We handle the stages the law explicitly designed to be pro-se: NCH (pre-litigation mediation) and District Consumer Court (informal, no lawyer required). We stop at appeals, which is where a real lawyer earns their fee. We're augmenting the free legal channels, not replacing legal professionals.

**Q: What if someone files a false complaint?**
A: Good catch — the CPA 2019 has a real gap here (critics flag it). Our Company Defense Agent is doing quality-gate work the law itself doesn't strongly enforce: if the user's story doesn't survive cross-exam, we don't file. This protects the user from wasting time and the system from spam.

**Q: NCH is just government pressure, not binding. E-Jagriti takes months. Won't this be slow?**
A: Yes, the overall timeline is 3-6 months typical for a resolution. But the alternative is: do nothing and let the company win forever. Our system removes the attrition tactic (companies betting you'll get tired) by doing the follow-up unattended. The speed is not faster than a lawyer, but the adoption is higher (no lawyer needed) and the completion rate is higher (agent doesn't give up).

---

## Sources & Data

- NCH complaints/month: consumerhelpline.gov.in (public dashboard)
- E-commerce refunds: NCH sector data Apr-Dec 2025
- CPA 2019 legal text: https://consumerprotection.in/
- E-Jagriti portal: https://e-daakhil.gov.in/
- Voxya info: company website + crunchbase (unfunded, 2 employees)

---

**Document finalized**: 2026-07-11
**Ready to build**
