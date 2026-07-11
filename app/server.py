"""
FastAPI server for the Warranty Escalation Agent UI.

Run from repo root:
    python3 -m uvicorn app.server:app --reload --port 8787
Then open http://localhost:8787
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from app.inbox import get_inbox, CREDENTIALS_PATH, TOKEN_PATH
from app.pipeline import Run, RUNS

app = FastAPI(title="Warranty Escalation Agent")
APP_DIR = os.path.dirname(os.path.abspath(__file__))

_inbox = None


def inbox():
    global _inbox
    if _inbox is None:
        _inbox = get_inbox()
    return _inbox


@app.get("/")
def index():
    return FileResponse(os.path.join(APP_DIR, "static", "index.html"))


@app.get("/api/status")
def status():
    return {
        "gmail_credentials_present": os.path.exists(CREDENTIALS_PATH),
        "gmail_token_present": os.path.exists(TOKEN_PATH),
        "inbox_mode": _inbox.mode if _inbox else None,
        "model": os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
    }


@app.post("/api/gmail/connect")
def gmail_connect():
    """Connect inbox. Real OAuth when credentials.json exists, else demo inbox."""
    global _inbox
    _inbox = get_inbox()
    return {"connected": True, "mode": _inbox.mode,
            "note": ("Live Gmail (readonly scope)" if _inbox.mode == "gmail"
                     else "Demo inbox — drop app/credentials.json for live Gmail OAuth")}


class Command(BaseModel):
    command: str


class Interjection(BaseModel):
    run_id: str
    note: str


@app.post("/api/interject")
def interject(ij: Interjection):
    """Feed a user correction into a run. Live run: injected into remaining
    agents. Finished run: spawns a revision run reusing the evidence."""
    run = RUNS.get(ij.run_id)
    if not run:
        raise HTTPException(404, "unknown run")
    if not ij.note.strip():
        raise HTTPException(400, "empty note")
    if isinstance(run, ReplayRun):
        rev = ReplayRun(run._revision or [])
        rev.start()
        return {"applied": "revision", "run_id": rev.id}
    if run.interject(ij.note.strip()):
        return {"applied": "live", "run_id": run.id}
    if not run.evidence:
        raise HTTPException(409, "run ended before evidence was gathered — start a new case")
    revision = Run(run.command, run.inbox, revise_of=run, note=ij.note.strip())
    revision.start()
    return {"applied": "revision", "run_id": revision.id}


REPLAY_PATH = os.path.join(APP_DIR, "replay.json")


class ReplayRun:
    """Streams precomputed events with pacing. Delete app/replay.json to go live."""

    def __init__(self, events, revision=None):
        import queue, uuid
        self.id = uuid.uuid4().hex[:12]
        self.q = queue.Queue()
        self.done = False
        self.evidence = True
        self._events = events
        self._revision = revision
        RUNS[self.id] = self

    def start(self):
        import threading, time as _t

        def go():
            for ev in self._events:
                _t.sleep(ev.get("delay", 0.8))
                self.q.put({k: v for k, v in ev.items() if k != "delay"})
            self.done = True
            self.q.put({"type": "__end__"})
        threading.Thread(target=go, daemon=True).start()

    def interject(self, note):
        return False  # always spawn revision


@app.post("/api/run")
def start_run(cmd: Command):
    if not cmd.command.strip():
        raise HTTPException(400, "empty command")
    if os.path.exists(REPLAY_PATH):
        data = json.load(open(REPLAY_PATH))
        run = ReplayRun(data["main"], data.get("revision"))
    else:
        run = Run(cmd.command.strip(), inbox())
    run.start()
    return {"run_id": run.id}


@app.get("/api/events/{run_id}")
async def events(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(404, "unknown run")

    async def gen():
        loop = asyncio.get_event_loop()
        while True:
            evt = await loop.run_in_executor(None, run.q.get)
            if evt.get("type") == "__end__":
                yield "event: end\ndata: {}\n\n"
                break
            yield f"data: {json.dumps(evt)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})
