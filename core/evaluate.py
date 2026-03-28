#!/usr/bin/env python3
"""
core/evaluate.py
Nova Loop — Evaluation System (Phase 5)

Every action produces an evaluation entry in state/evaluations.json.
Simple success/fail for now, quality scoring next phase.
"""

import os
import sys
from datetime import datetime

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent)

from core.safe_write import safe_write_json, load_json

EVAL_FILE = os.path.join(_parent, "state", "evaluations.json")

# Default evaluation rules — what "good" looks like per action type
EVAL_RULES = {
    "write_file": {
        "success": "file exists and non-empty after write",
        "quality_criteria": ["clarity", "structure", "completeness"]
    },
    "update_goal_progress": {
        "success": "goals.json updated with valid content",
        "quality_criteria": ["accuracy", "consistency"]
    },
    "commit_changes": {
        "success": "git commit succeeded",
        "quality_criteria": ["message_quality"]
    },
    "flag_blocker": {
        "success": "goal marked blocked, alerts written",
        "quality_criteria": ["accuracy", "escalation_quality"]
    },
    "propose_goal": {
        "success": "goal added to proposed_goals",
        "quality_criteria": ["goal_well_formed", "justification"]
    }
}


def evaluate_action(action_type, action_result, context=None):
    """
    Produce an evaluation entry for an action result.
    Returns the evaluation dict.
    """
    ts = datetime.now().isoformat()

    # Determine success/fail
    ok = action_result.get("ok", False)
    error = action_result.get("error", None)

    # Get quality criteria for this action type
    rule = EVAL_RULES.get(action_type, {})
    quality_criteria = rule.get("quality_criteria", [])

    # Simple quality score: 1.0 if ok, 0.0 if not
    quality = 1.0 if ok else 0.0

    evaluation = {
        "timestamp": ts,
        "type": action_type,
        "result": "success" if ok else "fail",
        "quality": quality,
        "error": error,
        "context": context or {},
        "quality_criteria_applied": quality_criteria
    }

    # Append to evaluations.json
    evals = load_json(EVAL_FILE) or {"evaluations": [], "last_updated": None}
    evals["evaluations"].append(evaluation)
    evals["last_updated"] = ts

    try:
        safe_write_json(EVAL_FILE, evals)
    except Exception:
        pass  # Don't fail the action because eval write failed

    return evaluation
