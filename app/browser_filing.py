"""
Portal Agent — REAL Gemini Computer Use driving a REAL browser on the actual
government portal (consumerhelpline.gov.in).

Loop: screenshot -> gemini-2.5-computer-use-preview decides an action
(click_at / type_text_at / navigate / scroll ...) -> Playwright executes ->
new screenshot back to the model. Every step is streamed to the UI.

Hard boundary: the agent is instructed to NEVER submit; a human approves first.
Falls back to scripted navigation if the CU model is unavailable.
"""
import base64
import os
from typing import Callable

NCH_URL = "https://consumerhelpline.gov.in/"
CU_MODEL = "gemini-2.5-computer-use-preview-10-2025"
MAX_TURNS = 12
VIEW = {"width": 1280, "height": 800}


def _client():
    from google import genai
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def run_portal_session(emit: Callable[..., None], case_summary: str) -> dict:
    """Never raises — returns a summary dict; emits portal_shot/portal_note events."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"portal_session": "unavailable", "note": "playwright not installed"}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path="/usr/bin/google-chrome", headless=True)
            page = browser.new_page(viewport=VIEW)
            try:
                return _computer_use_loop(emit, page, case_summary)
            except Exception as e:
                emit("portal_note",
                     note=f"Computer Use loop unavailable ({type(e).__name__}: {e}) — scripted fallback.")
                return _scripted_fallback(emit, page)
            finally:
                browser.close()
    except Exception as e:
        return {"portal_session": "offline_fallback",
                "note": f"Portal/browser unreachable ({type(e).__name__}). Form staged locally."}


# ------------------------------------------------------------- CU main loop
def _computer_use_loop(emit, page, case_summary: str) -> dict:
    from google.genai import types

    client = _client()
    config = types.GenerateContentConfig(
        tools=[types.Tool(computer_use=types.ComputerUse(
            environment=types.Environment.ENVIRONMENT_BROWSER))],
    )

    goal = f"""You are staging a consumer grievance at India's National Consumer Helpline
on behalf of this user. Current page: {NCH_URL} (already open).

USER DETAILS (use these to fill forms):
- Name: Manit Bohra
- Email: bohra.manit@gmail.com
- Mobile: 9876543210
- Password (for the new account): Nyaya@2026
- State: Karnataka

CASE: {case_summary[:500]}

TASK:
1. Find the grievance / complaint registration flow ("शिकायत दर्ज करें" / "Register Complaint" / Sign up).
2. On the registration/signup form: FILL every text field you can with the user
   details above (name, mobile, email, password, confirm password, state, case text).
   Filling fields is allowed and expected — typed text is not submitted.
3. Scroll so the filled fields are visible.

HARD RULES (the only things forbidden):
- NEVER click Sign Up / Submit / Register / Send / Generate OTP or any button that
  transmits the form. Typing into fields is fine; transmitting is not.
- Do not type into or solve the CAPTCHA field — leave it empty for the human.
- After the form is filled, respond with plain text listing exactly what the human
  must do to finish (enter captcha, press Sign Up), then stop."""

    page.goto(NCH_URL, timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    def snap():
        return page.screenshot(type="png")

    emit("portal_note", note=f"🧠 Gemini Computer Use ({CU_MODEL}) is driving a live browser on {NCH_URL}")
    emit("portal_shot", label="Live: NCH portal — session start",
         image=base64.b64encode(page.screenshot(type="jpeg", quality=55)).decode())

    contents = [types.Content(role="user", parts=[
        types.Part(text=goal),
        types.Part.from_bytes(data=snap(), mime_type="image/png"),
    ])]

    actions_taken = []
    for turn in range(MAX_TURNS):
        resp = client.models.generate_content(
            model=CU_MODEL, contents=contents, config=config)
        cand = resp.candidates[0]
        contents.append(cand.content)

        fc = None
        text_out = ""
        for part in cand.content.parts or []:
            if getattr(part, "function_call", None):
                fc = part.function_call
            elif getattr(part, "text", None):
                text_out += part.text

        if not fc:  # model finished with a text summary
            emit("portal_note", note="✅ Computer Use agent: " + (text_out.strip()[:400] or "done"))
            return {"portal_session": "computer_use_live", "model": CU_MODEL,
                    "portal": "NCH — consumerhelpline.gov.in",
                    "actions": actions_taken, "agent_summary": text_out.strip()[:800],
                    "boundary": "Stopped before submission — human approval required"}

        # safety confirmations = our human boundary
        if getattr(fc, "args", None) and fc.args.get("safety_decision"):
            emit("portal_note", note="🛑 Model requested user confirmation — stopping at human boundary.")
            return {"portal_session": "computer_use_live", "model": CU_MODEL,
                    "actions": actions_taken,
                    "boundary": "CU safety stop — human confirmation required"}

        label = _execute(page, fc)
        actions_taken.append(label)
        emit("portal_shot", label=f"CU step {turn+1}: {label}",
             image=base64.b64encode(page.screenshot(type="jpeg", quality=55)).decode())

        contents.append(types.Content(role="user", parts=[types.Part(
            function_response=types.FunctionResponse(
                name=fc.name, response={"url": page.url},
                parts=[types.FunctionResponsePart(
                    inline_data=types.FunctionResponseBlob(
                        mime_type="image/png", data=snap()))]))]))

    return {"portal_session": "computer_use_live", "model": CU_MODEL,
            "actions": actions_taken, "note": "Turn budget reached",
            "boundary": "Stopped before submission — human approval required"}


def _execute(page, fc) -> str:
    """Execute one CU function call in Playwright. Returns a human label."""
    a = dict(fc.args or {})
    name = fc.name
    W, H = VIEW["width"], VIEW["height"]
    x = int(a.get("x", 0) * W / 1000)
    y = int(a.get("y", 0) * H / 1000)
    try:
        if name == "open_web_browser":
            pass
        elif name in ("navigate", "goto_url"):
            page.goto(a.get("url", NCH_URL), timeout=30000, wait_until="domcontentloaded")
        elif name == "click_at":
            page.mouse.click(x, y)
        elif name == "hover_at":
            page.mouse.move(x, y)
        elif name == "type_text_at":
            page.mouse.click(x, y)
            if a.get("clear_before_typing", True):
                page.keyboard.press("Control+A")
            page.keyboard.type(a.get("text", ""), delay=15)
            if a.get("press_enter"):
                page.keyboard.press("Enter")
        elif name == "key_combination":
            page.keyboard.press(a.get("keys", "").replace("+", "+") or "Escape")
        elif name == "scroll_document":
            d = a.get("direction", "down")
            page.mouse.wheel(0, 600 if d == "down" else -600)
        elif name == "scroll_at":
            page.mouse.move(x, y)
            d = a.get("direction", "down")
            m = int(a.get("magnitude", 600))
            page.mouse.wheel(0, m if d == "down" else -m)
        elif name == "wait_5_seconds":
            page.wait_for_timeout(5000)
        elif name == "go_back":
            page.go_back()
        elif name == "go_forward":
            page.go_forward()
        elif name == "search":
            page.goto("https://www.google.com/search?q=" + a.get("query", ""),
                      timeout=30000)
        page.wait_for_timeout(1500)
    except Exception as e:
        return f"{name} failed ({type(e).__name__})"
    pretty = {k: v for k, v in a.items() if k not in ("safety_decision",)}
    return f"{name} {pretty}" if pretty else name


# ------------------------------------------------------------------ fallback
def _scripted_fallback(emit, page) -> dict:
    shots = 0

    def shot(label):
        nonlocal shots
        shots += 1
        emit("portal_shot", label=label,
             image=base64.b64encode(page.screenshot(type="jpeg", quality=55)).decode())

    page.goto(NCH_URL, timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    shot("NCH home — consumerhelpline.gov.in (live)")
    try:
        page.goto(NCH_URL + "user/signup.php", timeout=30000,
                  wait_until="domcontentloaded")
        page.wait_for_timeout(1500)
        shot("Grievance registration form (live)")
    except Exception:
        pass
    return {"portal_session": "live_scripted", "screenshots_taken": shots,
            "portal": "NCH — consumerhelpline.gov.in",
            "boundary": "Stopped before submission — human approval required"}
