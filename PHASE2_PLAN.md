# Phase 2 Plan: Antigravity Orchestration

**Goal**: Wire all 6 agents into Google's Managed Agents framework (Antigravity)  
**Timeline**: 2-3 hours  
**Outcome**: Full pipeline runs in Antigravity UI with persistent state

---

## What Antigravity Provides

- **Managed agent platform**: Define agents with system prompts + tool definitions
- **Routing/orchestration**: Agents can call other agents, pass state
- **State persistence**: Shared context across agent calls
- **Tools**: LLM_CALL (agent-to-agent), BROWSER_TOOL (form automation), TIMER_TRIGGER (scheduling)

---

## Architecture: How Agents Wire

```
INPUT (raw case files)
  ↓
[Orchestrator] (client-side)
  ├→ call [Extraction Agent] in Antigravity
  │      ↓ returns CaseObject
  │
  ├→ parallel call [Advocate Agent] + [Defense Agent]
  │      (both receive CaseObject)
  │      Advocate returns draft
  │      Defense returns counter-arguments
  │
  ├→ call [Arbiter Agent]
  │      (receives CaseObject + Advocate + Defense)
  │      returns routing decision
  │
  ├→ if ready_to_file: call [Filing Agent]
  │      returns form_data + SLA_window
  │
  └→ schedule [Monitoring Agent]
         (runs on timer: day 1, 11, 20, 30, etc)
         returns alerts + auto-drafts
```

---

## Agent Definitions for Antigravity

Each agent needs:
1. **System prompt** (from src/agents/*.py)
2. **Input schema** (what it receives)
3. **Output schema** (what it returns)
4. **Tool definitions** (what tools it can call)

### Example: Extraction Agent

```yaml
name: "extraction_agent"
system_prompt: |
  [FROM extraction_agent.py EXTRACTION_PROMPT]
  
input_schema:
  type: object
  properties:
    receipt_text: {type: string}
    chat_thread: {type: string}
    defect_description: {type: string}
    defect_date: {type: string}
    defect_photos_count: {type: integer}
    today_date: {type: string}

output_schema:
  type: object
  properties:
    product: {type: object}
    warranty: {type: object}
    defect: {type: object}
    sla_analysis: {type: object}
    evidence: {type: array}
    data_quality: {type: object}

tools: []  # No external tools needed for extraction
```

### Example: Arbiter Agent (Router)

```yaml
name: "arbiter_agent"
system_prompt: |
  [FROM arbiter_agent.py ARBITER_PROMPT]
  
input_schema:
  type: object
  properties:
    case_obj: {type: object}  # from Extraction
    advocate_draft: {type: object}  # from Advocate
    defense_draft: {type: object}  # from Defense

output_schema:
  type: object
  properties:
    confidence: {type: number}
    routing_decision: {type: string, enum: [insufficient_evidence, reframe, ready_to_file]}
    channel_choice: {type: string, enum: [NCH-first, Public-first, Legal-notice-direct]}

tools:
  - name: "call_advocate"
    type: LLM_CALL
    description: "Re-call Advocate with reframed legal angle"
    
  - name: "call_defense"
    type: LLM_CALL
    description: "Re-call Defense with updated case"
```

---

## State Persistence Strategy

**Option 1: In-Memory (Simple, for demo)**
```python
# Shared dict in orchestrator
state = {
  "case_obj": {...},
  "advocate_draft": {...},
  "defense_draft": {...},
  "filing_data": {...},
  "monitoring_updates": [...]
}

# Each agent receives full state, returns updated state
```

**Option 2: Firestore (Production-like, persistent)**
```python
# Store CaseObject in Firestore doc
db.collection("cases").document(case_id).set(case_obj)

# Agent updates: merge into same doc
db.collection("cases").document(case_id).update({"advocate_draft": {...}})
```

For hackathon: Use Option 1 (in-memory state).

---

## Implementation Steps

### Step 1: Create Antigravity Config
- Write YAML or JSON for each agent definition
- Define tool connections (e.g., Arbiter → Advocate, Arbiter → Defense)

### Step 2: Test Agent-to-Agent Calls
- Call Extraction, get CaseObject
- Pass CaseObject to Advocate and Defense in parallel
- Verify state passes correctly

### Step 3: Wire Arbiter Routing
- Arbiter receives Advocate + Defense outputs
- Arbiter decides: loop/reframe/file
- If "reframe": Arbiter calls Advocate again with new legal angle

### Step 4: Filing Agent Integration
- Filing agent receives routing decision
- Stages form in real NCH/e-Jagriti portal (or mock)
- Stops before submit

### Step 5: Monitoring Timer Setup
- Use TIMER_TRIGGER to schedule Monitoring agent
- Run at: day 1, 11, 20, 30 post-filing
- Monitoring auto-detects SLA breaches, drafts execution petitions

### Step 6: Demo Integration
- Orchestrator: load test case → call agents → display outputs live
- Show Advocate vs Defense debate on screen
- Show Arbiter scoring in real-time
- Show Filing form staging

---

## LLM Deployment Notes

**Current setup**: local Python + Gemini API  
**For Antigravity**: Create Managed Agent job in Google AI Studio
- Deploy each agent's system prompt + tools
- Get agent IDs
- Wire in orchestrator

**Rate limits**: Tier 3 account ~10k req/min (plenty)

---

## Testing Plan for Phase 2

```
[ ] Extraction in Antigravity (call via API)
[ ] Advocate + Defense parallel calls
[ ] Arbiter scoring logic
[ ] Arbiter → Advocate re-call (if reframe)
[ ] Filing agent form staging
[ ] Monitoring timer setup (simulate day 11, 20 etc)
[ ] Full pipeline end-to-end with Priya case
```

---

## Success Criteria

✓ All 6 agents callable from Antigravity  
✓ State persists across agent calls  
✓ Arbiter can re-route (call Advocate/Defense again)  
✓ Filing form data correct for NCH/e-Jagriti  
✓ Monitoring can be scheduled on timer  
✓ Demo: case → filing in <2 minutes live

---

## Next Actions

1. Create Antigravity agent definitions (YAML)
2. Deploy to Google AI Studio
3. Test each agent via API
4. Wire orchestrator to call Antigravity agents
5. Run full pipeline live in demo UI

---

**Estimated time**: 2-3 hours  
**Target completion**: Before Phase 3 (demo rehearsal)
