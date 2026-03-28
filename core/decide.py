#!/usr/bin/env python3
"""
core/decide.py
Nova Loop — Decision Engine (Phase 4, updated)

Hardcoded prioritization. No dynamic scoring yet.
Skips blocked subtasks. Returns next pending subtask.
"""

import os
import sys

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent)

from core.safe_write import load_json, safe_write_json

GOALS_FILE = os.path.join(_parent, "brain", "goals.json")


def decide():
    """
    Return the next subtask to work on, or None if nothing to do.
    """
    goals = load_json(GOALS_FILE)
    if goals is None:
        return None

    # Sort active goals by priority (highest first), skip blocked
    active = [
        g for g in goals.get("active_goals", [])
        if g.get("status") != "blocked"
    ]
    if not active:
        return None

    active.sort(key=lambda g: g.get("priority", 0), reverse=True)
    top_goal = active[0]

    # Find first pending (not complete, not blocked) subtask
    for subtask in top_goal.get("subtasks", []):
        if subtask.get("status") == "pending":
            return {
                "goal_id": top_goal["id"],
                "subtask_id": subtask["id"],
                "action": "execute",
                "goal": top_goal,
                "subtask": subtask
            }

    # No pending subtasks — mark goal complete
    return {
        "goal_id": top_goal["id"],
        "subtask_id": None,
        "action": "mark_complete",
        "goal": top_goal
    }


def idle_maintenance():
    """Called when decide() returns None — nothing active to do."""
    return {"action": "idle", "reason": "no pending subtasks"}


def mark_subtask_done(goal_id, subtask_id):
    """Mark a subtask as complete in goals.json."""
    goals = load_json(GOALS_FILE)
    if goals is None:
        return False

    for goal in goals.get("active_goals", []):
        if goal.get("id") == goal_id:
            for subtask in goal.get("subtasks", []):
                if subtask.get("id") == subtask_id:
                    subtask["status"] = "complete"
                    safe_write_json(GOALS_FILE, goals)
                    return True

    return False
