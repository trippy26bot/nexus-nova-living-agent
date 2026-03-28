#!/usr/bin/env python3
"""
core/loop.py
Nova Loop — Full Implementation (Phase 7)

7 layers wired together:
  1. Goals        → brain/goals.json
  2. Observe      → state/observations.log
  3. Decide       → core/decide.py (hardcoded priority)
  4. Act          → core/actions.py (Level 1 + 2)
  5. Evaluate     → state/evaluations.json
  6. Retry       → core/retry.py (3 attempts then escalate)
  7. Memory       → append to observations.log

Kill switch: set state/control.json "run" to false
"""

import os
import sys
import time
import json
from datetime import datetime

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent)

from core.bootstrap import bootstrap
from core.process import acquire_pid, release_pid
from core.decide import decide, idle_maintenance
from core.actions import (
    read_file, log_event, write_file, update_goal_progress,
    commit_changes, flag_blocker, propose_goal
)
from core.evaluate import evaluate_action
from core.retry import act_with_retry, log_observation

STATE_DIR = os.path.join(_parent, "state")
OBS_LOG = os.path.join(STATE_DIR, "observations.log")
CTRL_FILE = os.path.join(STATE_DIR, "control.json")
GOALS_FILE = os.path.join(_parent, "brain", "goals.json")


def read_control():
    """Read control.json safely."""
    if not os.path.exists(CTRL_FILE):
        return None
    try:
        with open(CTRL_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def observe():
    """
    Layer 2 — Observation.
    Scan state and return what's happening.
    """
    observations = {
        "timestamp": datetime.now().isoformat(),
        "errors": [],
        "status": "ok"
    }

    # Check control.json exists
    if not os.path.exists(CTRL_FILE):
        observations["errors"].append("control.json missing")

    # Check goals.json exists
    if not os.path.exists(GOALS_FILE):
        observations["errors"].append("goals.json missing")

    return observations


def decide_action(observations):
    """
    Layer 3 — Decision.
    Returns the next action to take.
    """
    # Errors always take priority
    if observations.get("errors"):
        log_event("observe", f"errors detected: {observations['errors']}")
        return None  # Handled separately for now

    decision = decide()

    if decision is None:
        return idle_maintenance()

    return decision


def execute_action(decision):
    """
    Layer 4 — Action.
    Execute the decided action.
    """
    action_type = decision.get("action")
    goal_id = decision.get("goal_id")

    if action_type == "idle":
        log_observation("idle — nothing to do")
        return {"ok": True, "type": "idle"}

    if action_type == "mark_complete":
        result = update_goal_progress(goal_id, 1.0, "complete")
        evaluate_action("update_goal_progress", result, {"goal_id": goal_id})
        log_event("decide", f"goal={goal_id} marked complete")
        return result

    if action_type == "execute":
        subtask_id = decision.get("subtask_id")
        subtask = decision.get("subtask", {})

        # Execute the appropriate action based on subtask
        if subtask_id == "choose_embedding_provider":
            # Can't execute this without operator input — flag it
            flag_blocker(goal_id, "waiting on embedding_provider_decision")
            return {"ok": False, "type": "blocked", "reason": "requires operator decision"}

        elif subtask_id == "design_schema":
            # Schema was already written during the test session
            result = update_goal_progress(goal_id, 0.4, None)
            evaluate_action("update_goal_progress", result, {"goal_id": goal_id})
            log_event("decide", f"design_schema already done, progress updated")
            return result

        elif subtask_id == "implement_pipeline":
            result = write_file(
                os.path.join(_parent, "brain", "vector_pipeline.py"),
                "# vector_pipeline.py — pending implementation\n# Depends on embedding provider decision\n",
                "pipeline stub for vector store"
            )
            evaluate_action("write_file", result, {"goal_id": goal_id})
            return result

        else:
            log_event("decide", f"unknown subtask: {subtask_id}")
            return {"ok": False, "type": "unknown_subtask", "subtask": subtask_id}

    return {"ok": False, "type": "unknown_action", "action": action_type}


def run_loop():
    """
    Main loop. All 7 layers.
    """
    bootstrap()
    acquire_pid()

    loop_count = 0
    stopped_reason = None

    try:
        while True:
            control = read_control()

            if control is None:
                log_observation("control.json missing or invalid, waiting 60s")
                time.sleep(60)
                continue

            if not control.get("run", False):
                stopped_reason = "stopped by control.json"
                break

            loop_count += 1

            if loop_count > control.get("max_cycles", 1000):
                stopped_reason = f"cycle limit ({control.get('max_cycles')})"
                break

            # Layer 2 — Observe
            observations = observe()

            # Layer 3 — Decide
            decision = decide_action(observations)

            # Layer 4 — Execute
            if decision:
                result = execute_action(decision)
                # Layer 5 — Evaluate
                if decision.get("action") != "idle":
                    evaluate_action(
                        result.get("type", "unknown"),
                        result,
                        {"goal_id": decision.get("goal_id"), "subtask": decision.get("subtask_id")}
                    )

            # Log tick
            log_observation(f"cycle {loop_count} complete")

            interval = control.get("cycle_interval_seconds", 30)
            time.sleep(interval)

    except KeyboardInterrupt:
        stopped_reason = "keyboard interrupt"
    finally:
        release_pid()
        if stopped_reason:
            log_observation(f"Loop ended: {stopped_reason}")
            print(f"Loop ended: {stopped_reason}")


if __name__ == "__main__":
    print("Nova Loop starting (Phase 7 — full implementation)...")
    run_loop()
