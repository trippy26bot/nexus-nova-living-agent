#!/usr/bin/env python3
"""
core/decide.py
Nova Loop — Decision Engine (Phase 4)

Hardcoded prioritization. No dynamic scoring yet.
Reads goals.json and returns the next pending subtask.

Priority rules:
  1. Blocked goals are skipped
  2. Among non-blocked active goals, highest priority wins
  3. Within that goal, first pending subtask wins
  4. If no pending subtasks, goal is marked complete
"""

import os
import sys

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent)

from core.safe_write import load_json

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

    subtasks = top_goal.get("subtasks", [])
    pending_subtasks = [s for s in subtasks if s.get("status") == "pending"]

    if not pending_subtasks:
        # No more subtasks — mark goal complete
        return {
            "goal_id": top_goal["id"],
            "subtask_id": None,
            "action": "mark_complete",
            "goal": top_goal
        }

    next_subtask = pending_subtasks[0]
    return {
        "goal_id": top_goal["id"],
        "subtask_id": next_subtask["id"],
        "action": "execute",
        "goal": top_goal,
        "subtask": next_subtask
    }


def idle_maintenance():
    """
    Called when decide() returns None — nothing active to do.
    """
    return {
        "action": "idle",
        "reason": "no pending subtasks"
    }
