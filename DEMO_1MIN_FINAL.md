# 1-Minute Demo Script (FINAL)
## Using Manit's Real Nothing Phone 4a Pro Case

**Total Time**: Exactly 60 seconds  
**Test Case**: Nothing Phone 4a Pro (water patches in Glyph Matrix)  
**Status**: READY TO RECORD

---

## Script (60 seconds)

### **0:00-0:10 — STORY (10 sec)**
> "Manit buys a Nothing Phone 4a Pro on March 23rd. By March 25th, water patches appear inside the display. He contacts support. They promise resolution in 7-10 days. It's now April 8th. Nothing. He's within the return window but the company keeps stalling."

*[No tech jargon. Just tell the story. Show on screen: Case summary]*

---

### **0:10-0:35 — THE CORE: Agent Debate (25 sec)**
This is the **centerpiece**. Show the adversarial reasoning.

**ADVOCATE**: 
> "This is a manufacturing defect within warranty. Device is brand new, water inside = manufacturing failure. CPA 2019 §2(42). Plus deficiency-of-service: promised 7-10 days, now 16 days. Relief: ₹49,000."

**DEFENSE**: 
> "Warranty limits remedy to repair/replacement, not cash. Device might have humidity. We need further assessment."

**ARBITER**: 
> "Confidence: 85% → READY TO FILE at NCH"

*[Show this as text on screen. Both sides arguing. Then the decision.]*

---

### **0:35-0:50 — FILING (15 sec)**
Show the browser OR play fallback video.

**OPTION A (Live with Computer Use)**:
- Browser opens: consumerhelpline.gov.in
- Form loads
- Fill: State, Company, Nature, Relief Amount
- Evidence ready
- **STOP** (human gate)

**OPTION B (Fallback Video)**:
- Play 15-sec pre-recorded video of filing
- Label: "Pre-recorded NCH filing demo"

*[Either way, judges see the filing process]*

---

### **0:50-1:00 — CLOSE (10 sec)**
**Show impact + numbers**:
- 1.7 lakh complaints/month to NCH
- Average ₹8,000 refund per case
- Voxya: 2 employees (incumbent)
- **This agent: Autonomous, multi-agent, adaptive**

> "Companies bet you'll get tired before they have to pay. This agent doesn't get tired."

*[Fade out with project logo/team name]*

---

## How to Record

### **Setup**
```bash
# Make sure you have:
cd /home/alex_hunterz/Desktop/projects/google-deepmind-hack-dieas/warranty-agent

# Run the analyzer first (to have numbers ready)
python3 parse_nothing_phone_case.py

# Or run 1-minute demo
python3 demo_1min.py
```

### **Recording**
```bash
# Mac: Cmd+Shift+5 → select area → Record
# Linux: gnome-recorder or ffmpeg
# Windows: Win+G (Game Bar)

# Duration: Exactly 60 seconds
# Resolution: 1920x1080 (HD)
# Format: MP4
# Filename: warranty_agent_demo_1min.mp4
```

### **What to Show on Screen**
1. **Title** (0:00): "Consumer Warranty Escalation Agent"
2. **Story** (0:00-0:10): Case summary card (product, price, timeline)
3. **Debate** (0:10-0:35): 
   - Advocate box (left): "9/10 - Deficiency-of-service"
   - Defense box (right): "6/10 - Warranty limits"
   - Arbiter (center): "85% confidence → READY TO FILE"
4. **Filing** (0:35-0:50):
   - Browser + NCH form (OR fallback video)
   - Show filled fields
   - Stop before submit
5. **Close** (0:50-1:00):
   - Numbers: 1.7L complaints/month
   - Pitch: "Companies bet you'll get tired..."

---

## Fallback Video (Pre-record this NOW)

If Computer Use API unavailable or fails during demo:

```bash
# 1. Go to consumerhelpline.gov.in in real browser
# 2. Record clicking through to filing form
# 3. Show form loading
# 4. Manually fill one example
# 5. Stop before submit
# 6. Total: 30 seconds

# Save as: nch_filing_fallback.mp4
# Label: "Pre-recorded: Real NCH filing process"
```

**Judges will accept pre-recorded.** It's totally normal for gov site stability.

---

## Checklist Before Recording

- [ ] Python script tested and running (outputs case analysis)
- [ ] Numbers gathered (1.7L complaints, ₹8k avg, etc.)
- [ ] Story clear in your head (30 sec to tell smoothly)
- [ ] Advocate vs Defense text ready (copy-paste into slides if needed)
- [ ] Computer Use API tested (or fallback video ready)
- [ ] Screen resolution at 1920x1080
- [ ] Headphones disconnected (avoid echo)
- [ ] Lighting good
- [ ] Exactly 60 seconds (practice with timer)

---

## What Judges Will See

✅ **Real case**: Your actual Nothing Phone dispute  
✅ **Real analysis**: 6 agents working, case scored at 85% confidence  
✅ **Real filing**: Browser showing NCH form OR pre-recorded evidence  
✅ **Real impact**: 1.7L complaints/month, Voxya is the only incumbent  
✅ **Differentiator**: Adversarial reasoning (Advocate vs Defense), not just single analysis  

---

## Upload to Submission

Once recorded:
1. Save as: `warranty_agent_demo_1min.mp4`
2. Upload to YouTube (unlisted) or Vimeo
3. Get public link
4. Paste in hackathon submission form
5. **Deadline**: Before 5 PM IST

---

## If Time is Tight

**Bare minimum for 1 min**:
- 0:00-0:20: Story (this case is strong, company stalled)
- 0:20-0:50: Show live terminal output of agent analysis
- 0:50-1:00: Show NCH form (live or video)
- Pitch: "Autonomous warranty escalation"

That's enough to win.

---

## Final Tips

1. **Speak clearly** (no filler words)
2. **Move fast** (60 seconds is tight)
3. **Emphasize**: "Agents argue both sides" (the differentiator)
4. **Close strong**: "Companies bet you'll get tired. This agent doesn't."
5. **Judges care about**: Real case + Real code + Real difference

---

**You got this. Let's ship it.** 🚀
