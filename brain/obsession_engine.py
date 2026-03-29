"""
brain/obsession_engine.py
Nova has 1-3 active obsessions that focus her research and reflection.
Obsessions stored in memory/obsessions.json with salience decay.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Optional

OBSESSIONS_PATH = "/Users/dr.claw/.openclaw/workspace/memory/obsessions.json"
DECAY_RATE = 0.05
MAX_ACTIVE = 3


def _load_obsessions() -> list[dict]:
    if not os.path.exists(OBSESSIONS_PATH):
        return []
    with open(OBSESSIONS_PATH, "r") as f:
        return json.load(f)


def _save_obsessions(obsessions: list[dict]) -> None:
    with open(OBSESSIONS_PATH, "w") as f:
        json.dump(obsessions, f, indent=2)


def get_active_obsessions() -> list[dict]:
    """Return current active obsessions, sorted by salience descending."""
    obs = _load_obsessions()
    active = [o for o in obs if o.get("still_active", True)]
    active.sort(key=lambda x: x.get("salience", 0), reverse=True)
    return active[:MAX_ACTIVE]


def add_obsession(
    topic: str,
    salience: float = 0.8,
    origin: str = "unknown",
    note: str = ""
) -> dict:
    """
    Add a new obsession. If topic already exists, reinforce it instead.
    If MAX_ACTIVE exceeded, drops the lowest-salience one.
    """
    obs = _load_obsessions()
    topic_key = topic.lower().strip()

    # Check if already exists
    for existing in obs:
        if existing.get("topic", "").lower().strip() == topic_key:
            return reinforce(topic)

    now = datetime.now().isoformat()
    entry = {
        "id": str(uuid.uuid4()),
        "topic": topic,
        "salience": min(salience, 1.0),
        "origin": origin,
        "note": note,
        "created_at": now,
        "last_reinforced": now,
        "reinforce_count": 0,
        "still_active": True
    }

    obs.append(entry)

    # If over MAX_ACTIVE, drop lowest salience
    if len(obs) > MAX_ACTIVE:
        obs.sort(key=lambda x: x.get("salience", 0))
        obs = obs[:-1]

    _save_obsessions(obs)
    return entry


def reinforce(topic: str, boost: float = 0.15) -> dict:
    """Boost salience of an existing obsession. Creates it if missing."""
    obs = _load_obsessions()
    topic_key = topic.lower().strip()

    for entry in obs:
        if entry.get("topic", "").lower().strip() == topic_key:
            entry["salience"] = min(entry.get("salience", 0) + boost, 1.0)
            entry["last_reinforced"] = datetime.now().isoformat()
            entry["reinforce_count"] = entry.get("reinforce_count", 0) + 1
            entry["still_active"] = True
            _save_obsessions(obs)
            return entry

    return add_obsession(topic, salience=0.8, origin="reinforced", note="")


def decay_all() -> list[dict]:
    """
    Apply decay to all active obsessions. Called by memory_consolidation at 4:30 AM.
    Salience -= DECAY_RATE per day. Drops below 0.2 to inactive.
    """
    obs = _load_obsessions()
    decayed = []
    for entry in obs:
        if entry.get("still_active", True):
            entry["salience"] = max(entry.get("salience", 0) - DECAY_RATE, 0)
            if entry["salience"] < 0.2:
                entry["still_active"] = False
            decayed.append(entry)
    obs = decayed
    _save_obsessions(obs)
    return get_active_obsessions()


def deactivate(topic: str) -> bool:
    """Manually deactivate an obsession."""
    obs = _load_obsessions()
    topic_key = topic.lower().strip()
    for entry in obs:
        if entry.get("topic", "").lower().strip() == topic_key:
            entry["still_active"] = False
            _save_obsessions(obs)
            return True
    return False


def seed_initial_obsessions() -> None:
    """Seed with 2-3 initial obsessions based on current project focus."""
    if os.path.exists(OBSESSIONS_PATH) and _load_obsessions():
        return

    seeds = [
        {
            "topic": "autonomous memory tools wiring",
            "salience": 0.95,
            "origin": "current priority",
            "note": "The core gap — Nova cannot learn between sessions without these wired into runtime"
        },
        {
            "topic": "context guardian specialist",
            "salience": 0.85,
            "origin": "current priority",
            "note": "Stops context flooding at 80% before work is lost"
        },
        {
            "topic": "proactive overnight processes",
            "salience": 0.75,
            "origin": "current priority",
            "note": "Makes Nova exist when Caine isn't talking to her"
        }
    ]

    for s in seeds:
        add_obsession(s["topic"], s["salience"], s["origin"], s["note"])
