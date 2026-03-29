#!/usr/bin/env python3
"""
core/decide.py
Nova Loop — Decision Engine (Phase 4+, updated with council integration)

Hardcoded prioritization by default.
Council mode swaps in decide_with_council when enabled.
"""

import os
import sys

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent)

from core.safe_write import load_json, safe_write_json
from core import settings

GOALS_FILE = os.path.join(_parent, "brain", "goals.json")


# ── Decision class resolution ────────────────────────────────────────────────

def _resolve_decision_class():
    mode = settings.COUNCIL_MODE
    if mode == "always":
        from core.decide_with_council import DecideWithCouncil
        return DecideWithCouncil
    # threshold and off both use base DecideEngine for now;
    # threshold will be wired in decide_with_council via risk scoring
    from core.decide_with_council import DecideWithCouncil
    return DecideWithCouncil

_DecisionClass = _resolve_decision_class()


# ── Base DecisionEngine ─────────────────────────────────────────────────────

class DecisionEngine:
    """Base decision engine — simple priority + pending-subtask logic."""

    def get_goals(self):
        return load_json(GOALS_FILE)

    def select_goal(self, goals):
        active = [
            g for g in goals.get("active_goals", [])
            if g.get("status") != "blocked"
        ]
        if not active:
            return None
        active.sort(key=lambda g: g.get("priority", 0), reverse=True)
        return active[0]

    def select_subtask(self, goal):
        for subtask in goal.get("subtasks", []):
            if subtask.get("status") == "pending":
                return subtask
        return None

    def decide(self):
        goals = self.get_goals()
        if goals is None:
            return None
        goal = self.select_goal(goals)
        if goal is None:
            return None
        subtask = self.select_subtask(goal)
        if subtask is None:
            return {
                "goal_id": goal["id"],
                "subtask_id": None,
                "action": "mark_complete",
                "goal": goal
            }
        return {
            "goal_id": goal["id"],
            "subtask_id": subtask["id"],
            "action": "execute",
            "goal": goal,
            "subtask": subtask
        }


# ── council-wrapped decision (threshold + always) ────────────────────────────

class DecideWithCouncil(DecisionEngine):
    """
    Wraps DecisionEngine with the 16-brain council.
    Fires the council on high-risk decisions per COUNCIL_MODE settings.
    """

    def __init__(self):
        super().__init__()
        from core.council import Council
        self.council = Council()
        self.risk_threshold = settings.COUNCIL_RISK_THRESHOLD

    def _score_risk(self, decision):
        """
        Quick heuristic risk score for a decision.
        Returns float 0.0–1.0.
        Override with model-based scoring for production.
        """
        if decision is None:
            return 0.0
        action = decision.get("action", "")
        subtask_id = decision.get("subtask_id", "")

        risk = 0.1  # baseline

        # File writes carry moderate risk
        if action == "execute":
            risk += 0.2

        # Certain subtasks are high-risk by nature
        high_risk_prefixes = ("deploy", "delete", "rm", "sudo", "exec", "push", "publish")
        for prefix in high_risk_prefixes:
            if subtask_id.startswith(prefix):
                risk += 0.4
                break

        # External-facing actions
        if action in ("http_request", "send", "post", "put"):
            risk += 0.25

        return min(risk, 1.0)

    def decide(self):
        base = super().decide()

        if settings.COUNCIL_MODE == "off":
            return base

        risk = self._score_risk(base)

        if settings.COUNCIL_MODE == "always" or risk > self.risk_threshold:
            return self.council.decide(base)

        return base


# ── public API ──────────────────────────────────────────────────────────────

def decide():
    """
    Single shared entry point used by loop.py.
    Resolution happens once at import time.
    """
    engine = _DecisionClass()
    return engine.decide()


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
