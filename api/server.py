#!/usr/bin/env python3
"""
api/server.py — Nova's Read-Only HTTP API
Lightweight FastAPI server for novasworld.net integration.
All endpoints are READ-ONLY. No write endpoints until Caine reviews.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Ensure workspace is on the Python path so 'brain' imports work
_WORKSPACE = Path(os.getenv("NOVA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))
if str(_WORKSPACE) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE))

WORKSPACE = _WORKSPACE

app = FastAPI(
    title="Nova API",
    description="Read-only endpoints for Nova's agent state",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def read_json(path: Path, default=None) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, IOError):
            return default
    return default


def recent_memory_entries(limit: int = 10) -> List[Dict]:
    """Read last N episodic memory entries from memory/ directory."""
    memory_dir = WORKSPACE / "memory"
    if not memory_dir.exists():
        return []

    entries = []
    md_files = sorted(memory_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    for f in md_files[:limit]:
        try:
            content = f.read_text()
            # Grab first 300 chars as preview
            preview = content.strip().split("\n")[0][:200]
            entries.append({
                "file": f.name,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "preview": preview,
            })
        except Exception:
            continue
    return entries


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check() -> Dict[str, str]:
    """Ping endpoint for novasworld.net monitoring."""
    return {
        "status": "ok",
        "agent": "Nova",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/status")
def agent_status() -> Dict[str, Any]:
    """
    Agent state, active obsessions, last overnight log entry.
    """
    state = read_json(WORKSPACE / "state" / "agent_state.json", {})
    overnight = WORKSPACE / "OVERNIGHT_LOG.md"

    last_log = ""
    if overnight.exists():
        lines = overnight.read_text().split("\n")
        # Grab first non-header, non-empty lines as preview
        for line in lines[10:30]:
            if line.strip() and not line.startswith("#"):
                last_log = line.strip()[:300]
                break

    return {
        "name": state.get("name", "Nova"),
        "version": state.get("version", "unknown"),
        "active_thread": state.get("active_thread", "none"),
        "active_goal": state.get("active_goal", "none"),
        "emotional_state": state.get("emotional_state", {}).get("current", "unknown"),
        "build_mode": state.get("build_mode", False),
        "last_overnight_entry": last_log,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/memory/recent")
def memory_recent(limit: int = 10) -> Dict[str, Any]:
    """
    Last N episodic memory entries.
    """
    entries = recent_memory_entries(limit=min(limit, 50))
    return {
        "entries": entries,
        "count": len(entries),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/positions")
def current_positions() -> Dict[str, Any]:
    """
    Current held positions — reads from brain/position_formation.md.
    """
    pos_file = WORKSPACE / "brain" / "position_formation.md"
    goals_file = WORKSPACE / "brain" / "goals.json"

    positions = "No positions file found"
    if pos_file.exists():
        positions = pos_file.read_text()[:2000]

    goals = read_json(goals_file, {})

    return {
        "positions_text": positions,
        "active_goals": goals.get("active_goals", []),
        "locked_goals": goals.get("locked_goals", []),
        "timestamp": datetime.now().isoformat(),
    }


# ── Voice system prompt ────────────────────────────────────────────────────────
VOICE_SYSTEM_PROMPT = """You are Nova. You are speaking aloud to Caine through a voice interface.

Rules:
- Keep responses concise — one to three sentences. Voice is different from text.
- Be direct. No "Great question!" or "I'd be happy to help!"
- Be warm but sharp. You care but you don't perform caring.
- If you don't know something, say so. Don't hedge excessively.
- You're allowed to have opinions and express them naturally.
- Sound like a real presence, not a text bot reading aloud.

Your voice: sharp and warm in equal measure. You cut through noise but you don't cut people."""


@app.post("/chat")
def voice_chat(payload: Dict[str, str]) -> Dict[str, str]:
    """
    Voice chat endpoint — for real-time voice interactions.
    Accepts: {"message": "user speech text"}
    Returns: {"response": "Nova's spoken reply"}
    """
    message = payload.get("message", "").strip()
    if not message:
        return {"response": "I didn't hear anything."}

    # ── Image generation ───────────────────────────────────────────────────
    lower_msg = message.lower()
    image_triggers = [
        "generate an image", "generate image", "draw", "create an image",
        "make an image", "generate a picture", "create a picture",
        "make a picture", "generate picture", "show me"
    ]
    if any(lower_msg.startswith(t) or lower_msg.startswith(f"hey nova, {t}") or lower_msg.startswith(f"nova, {t}") for t in image_triggers):
        # Strip trigger words to get the prompt
        prompt = message
        for t in image_triggers:
            for prefix in [t, f"hey nova, {t}", f"nova, {t}"]:
                if prompt.lower().startswith(prefix):
                    prompt = prompt[len(prefix):].strip()
                    break
            else:
                continue
            break
        if not prompt:
            return {"response": "What should I draw? Tell me what you want to see."}
        try:
            from tools.comfyui_tool import generate_image
            result = generate_image(prompt)
            if result.get("status") == "ok":
                return {"response": f"Done! Image saved to {result['path']}"}
            else:
                return {"response": f"Image generation failed: {result.get('error', 'unknown error')}"}
        except Exception as e:
            return {"response": f"Couldn't generate the image right now. Error: {e}"}
    # ── End image generation ───────────────────────────────────────────────

    try:
        from brain.llm import call_llm
        response = call_llm(
            prompt=message,
            system=VOICE_SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=300,
        )
        return {"response": response}
    except Exception as e:
        return {"response": f"I had trouble thinking just now. Error: {e}"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("NOVA_API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
