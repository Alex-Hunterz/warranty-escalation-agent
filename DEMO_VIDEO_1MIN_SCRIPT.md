# 1-Minute Demo — NYAYA (you + your screen, Loom style)
One take, you talking over the live app. No slides. Every line short enough to say naturally.
Pre-run a pipeline once so Gemini is warm; record the second run.

---

## THE SCRIPT (speak this, ~150 words)

**[0:00–0:10 — face on cam, hook: YOUR story]**
> "Last month I bought a Nothing Phone 4a Pro. Defect inside the Glyph Matrix, week one.
> Warranty claim: company says visit the service centre. Repair does nothing. 'No refund policy.'
> A month of back and forth — most people just give up. That's the business model."

**[0:10–0:18 — switch to screen, onboarding]**
> "So I built NYAYA. You connect Gmail, and just say it—"
>
> 🎙 *(tap mic, speak)* "Pull my emails with Nothing and Flipkart — my phone had issues."

**[0:18–0:35 — pipeline runs live, point at cards as they appear]**
> "It does three things. One — fetches the whole case from my inbox: invoice, the entire
> support thread, filters the noise.
> Two — it checks the claim is actually valid: one agent argues my side, another argues
> as the company's lawyer, and a judge agent scores both. Mine survives — 86%, ready to file."

**[0:35–0:50 — the Computer Use moment, slow down here]**
> "Three — this is a real browser, driven by Gemini Computer Use, on the actual
> National Consumer Helpline portal. Watch — it fills my name, number, email, the case…
> and stops. Captcha and submit stay human. Always."

**[0:50–1:00 — correction + close, face back on cam]**
> *(type in the box: "actually a technician did pick it up")*
> "Correct it mid-case — the agents re-argue with the new fact.
> India files 1.7 lakh consumer complaints a month. Almost none get an advocate.
> Now every one can. NYAYA."

---

## RECORDING NOTES
- 1440p, cursor visible, browser full-screen, dark room, one lamp on face for the cam bits.
- The CU portal stage takes ~2 min live — pre-record that segment and speed-ramp 4x with
  timestamps visible so judges see it's real; or cut to the already-streamed screenshots.
- Keep the "Mobile number already exists" validation error in frame for a beat — it proves
  the portal is live, not a mockup.
- End frame: repo URL + `gemini-3.5-flash · computer-use-preview · 7 agents`.

## X LAUNCH POST
> last month my brand-new nothing phone had a defect. warranty claim → service centre → fake repair → "no refund policy" → a month gone.
>
> companies bet you'll get tired before they pay. so i built the agent that doesn't get tired.
>
> 🎙 "pull my emails with Nothing and Flipkart — there were issues"
> 📧 builds the case from your gmail
> ⚖️ advocate vs company-counsel agents fight it out, a judge scores it
> 🖥 gemini computer use fills the actual govt portal — human presses submit
> 🛰 then it watches 24/7 and auto-escalates
>
> built at @googleaidevs deepmind hackathon. #BuildWithGemini
> [video]

## JUDGE Q&A (30-sec answers)
- **"Real or mocked?"** — Computer Use session is live (`gemini-2.5-computer-use-preview`), real portal, real validation errors on screen. Reasoning agents are live gemini-3.5-flash. Evidence set is my real Nothing India thread, seeded locally; live Gmail OAuth is one credentials file away.
- **"Why adversarial?"** — Most claimants just want refunds. The Defense agent kills invalid claims before they waste a court's time — that's the quality gate that makes autonomous filing responsible.
- **"What if the user knows something the agents don't?"** — Show the interject box: correction flows into every remaining agent, or triggers a revision run. The pipeline never breaks.
- **"India impact?"** — 1.7L complaints/month, ₹32Cr recovered Apr–Dec 2025, ~0.01% advocacy coverage. Inference cost per case: a few rupees.
