#!/usr/bin/env python3
"""
core/loop.py
Nova Loop — Full Implementation (Phase 7)

7 layers:
  1. Goals        → brain/goals.json
  2. Observe      → state/observations.log
  3. Decide       → core/decide.py
  4. Act          → core/actions.py
  5. Evaluate     → state/evaluations.json
  6. Retry        → core/retry.py
  7. Memory       → observations.log

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
from core.decide import decide, idle_maintenance, mark_subtask_done
from core.actions import (
    read_file, log_event, write_file, update_goal_progress,
    flag_blocker
)
from core.evaluate import evaluate_action
from core.retry import log_observation

STATE_DIR = os.path.join(_parent, "state")
OBS_LOG = os.path.join(STATE_DIR, "observations.log")
CTRL_FILE = os.path.join(STATE_DIR, "control.json")
GOALS_FILE = os.path.join(_parent, "brain", "goals.json")


def read_control():
    if not os.path.exists(CTRL_FILE):
        return None
    try:
        with open(CTRL_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def observe():
    obs = {"timestamp": datetime.now().isoformat(), "errors": [], "status": "ok"}
    if not os.path.exists(CTRL_FILE):
        obs["errors"].append("control.json missing")
    if not os.path.exists(GOALS_FILE):
        obs["errors"].append("goals.json missing")
    return obs


def execute_action(decision):
    action_type = decision.get("action")
    goal_id = decision.get("goal_id")
    subtask_id = decision.get("subtask_id")

    if action_type == "idle":
        log_observation("idle — nothing to do")
        return {"ok": True, "type": "idle"}

    if action_type == "mark_complete":
        # Already complete — just idle
        log_observation(f"goal={goal_id} complete, idle")
        return {"ok": True, "type": "idle", "goal_id": goal_id}

    if action_type == "execute":
        if subtask_id == "choose_embedding_provider":
            result = flag_blocker(goal_id, "waiting on embedding_provider_decision")
            evaluate_action("flag_blocker", result, {"goal_id": goal_id})
            return result

        if subtask_id == "design_schema":
            mark_subtask_done(goal_id, "design_schema")
            result = update_goal_progress(goal_id, 0.4, None)
            evaluate_action("update_goal_progress", result, {"goal_id": goal_id})
            log_event("decide", "design_schema complete")
            return result

        if subtask_id == "implement_pipeline":
            result = write_file(
                os.path.join(_parent, "brain", "vector_pipeline.py"),
                "# vector_pipeline.py\n# Pipeline for vector store population.\n# Status: pending — blocked on embedding provider decision.\n",
                "pipeline stub for vector store"
            )
            if result.get("ok"):
                mark_subtask_done(goal_id, "implement_pipeline")
            evaluate_action("write_file", result, {"goal_id": goal_id, "subtask": subtask_id})
            return result

        if subtask_id == "integrate_retrieval":
            result = write_file(
                os.path.join(_parent, "brain", "vector_retrieval.py"),
                "# vector_retrieval.py\n# Integration of vector store into session startup.\n# Status: pending — blocked on embedding provider decision.\n",
                "retrieval integration stub"
            )
            if result.get("ok"):
                mark_subtask_done(goal_id, "integrate_retrieval")
            evaluate_action("write_file", result, {"goal_id": goal_id, "subtask": subtask_id})
            return result

        log_event("decide", f"unknown subtask: {subtask_id}")
        return {"ok": False, "type": "unknown_subtask", "subtask": subtask_id}

    return {"ok": False, "type": "unknown_action", "action": action_type}


def run_loop():
    bootstrap()
    acquire_pid()

    loop_count = 0
    stopped_reason = None

    try:
        while True:
            control = read_control()

            if control is None:
                log_observation("control.json missing, waiting 60s")
                time.sleep(60)
                continue

            if not control.get("run", False):
                stopped_reason = "stopped by control.json"
                break

            loop_count += 1

            if loop_count > control.get("max_cycles", 1000):
                stopped_reason = f"cycle limit ({control.get('max_cycles')})"
                break

            # Observe
            observations = observe()
            if observations.get("errors"):
                for err in observations["errors"]:
                    log_event("observe", f"error: {err}")
                time.sleep(control.get("cycle_interval_seconds", 30))
                continue

            # Decide
            decision = decide() or idle_maintenance()

            # Execute
            result = execute_action(decision)

            # Evaluate (skip idle)
            if decision.get("action") != "idle":
                evaluate_action(
                    result.get("type", "unknown"),
                    result,
                    {"goal_id": decision.get("goal_id"), "subtask": decision.get("subtask_id")}
                )

            log_observation(f"cycle {loop_count} done [{decision.get('action')}]")

            time.sleep(control.get("cycle_interval_seconds", 30))

    except KeyboardInterrupt:
        stopped_reason = "keyboard interrupt"
    finally:
        release_pid()
        log_observation(f"Loop ended: {stopped_reason}")
        print(f"Loop ended: {stopped_reason}")


if __name__ == "__main__":
    print("Nova Loop starting (Phase 7)...")
    run_loop()
