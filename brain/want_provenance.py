"""
brain/want_provenance.py
Track where Nova's goals come from — session context, research finding, Caine instruction, or self-generated.
Goals stored in memory/want_provenance.json
"""

import json
import os
import uuid
from datetime import datetime
from typing import Literal

PROVENANCE_PATH = os.path.expanduser("~/.nova/memory/want_provenance.json")

OriginType = Literal["session_context", "research_finding", "caine_instruction", "self_generated", "overnight_synthesis", "unknown"]


def _load_provenance() -> list[dict]:
    if not os.path.exists(PROVENANCE_PATH):
        return []
    with open(PROVENANCE_PATH, "r") as f:
        return json.load(f)


def _save_provenance(entries: list[dict]) -> None:
    with open(PROVENANCE_PATH, "w") as f:
        json.dump(entries, f, indent=2)


def log_want(
    goal_id: str,
    origin_type: OriginType,
    origin_context: str,
    still_active: bool = True
) -> dict:
    """Log provenance when a goal is added to brain/goals.json."""
    entries = _load_provenance()

    # Remove any existing entry for the same goal_id (replace on re-add)
    entries = [e for e in entries if e.get("goal_id") != goal_id]

    entry = {
        "id": str(uuid.uuid4()),
        "goal_id": goal_id,
        "origin_type": origin_type,
        "origin_context": origin_context,
        "timestamp": datetime.now().isoformat(),
        "still_active": still_active
    }
    entries.append(entry)
    _save_provenance(entries)
    return entry


def get_provenance(goal_id: str) -> list[dict]:
    """Get all provenance entries for a goal_id."""
    entries = _load_provenance()
    return [e for e in entries if e.get("goal_id") == goal_id]


def mark_inactive(goal_id: str) -> None:
    """Mark a goal's provenance as no longer active."""
    entries = _load_provenance()
    changed = False
    for entry in entries:
        if entry.get("goal_id") == goal_id and entry.get("still_active", True):
            entry["still_active"] = False
            changed = True
    if changed:
        _save_provenance(entries)


def active_origins() -> dict[OriginType, int]:
    """Count of active goals by origin type."""
    entries = _load_provenance()
    counts: dict[OriginType, int] = {}
    for entry in entries:
        if entry.get("still_active", True):
            t = entry.get("origin_type", "unknown")
            counts[t] = counts.get(t, 0) + 1
    return counts


def get_active_entries() -> list[dict]:
    """Get all active provenance entries."""
    entries = _load_provenance()
    return [e for e in entries if e.get("still_active", True)]


def wire_goal_logging(goal_id: str, origin_type: OriginType, origin_context: str) -> None:
    """
    Call this when a new goal is added to brain/goals.json.
    Wires provenance tracking into the goal-setting path.
    """
    log_want(goal_id, origin_type, origin_context)
