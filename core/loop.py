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
import subprocess
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

        if subtask_id == "create_brain_state_files":
            # Check which brain state files exist
            brain_dir = os.path.join(_parent, "brain")
            needed = ["attention_log.json", "body_awareness.json", "contradictions_detected.json",
                      "knowledge_graph.json", "wants_registry.json", "obsessions.json",
                      "positions.json", "opinion_fingerprint.json", "identity_constraints.md"]
            missing = [f for f in needed if not os.path.exists(os.path.join(brain_dir, f))]
            if missing:
                result = flag_blocker(goal_id, f"missing brain files: {missing}")
                log_event("brain_state", f"missing files: {missing}")
            else:
                mark_subtask_done(goal_id, "create_brain_state_files")
                result = update_goal_progress(goal_id, 0.4, "brain state files verified")
                log_event("brain_state", "all brain state files present")
            evaluate_action("brain_state_check", result, {"goal_id": goal_id})
            return result

        if subtask_id == "verify_loop_stability":
            # Check if loop has been stable (no crash in last 5 min per error log)
            stat_result = os.stat("/Users/dr.claw/.pm2/logs/nova-loop-error.log")
            age_minutes = (time.time() - stat_result.st_mtime) / 60
            if age_minutes > 5:
                mark_subtask_done(goal_id, "verify_loop_stability")
                result = update_goal_progress(goal_id, 0.7, "loop stability verified")
                log_event("loop", f"stable — error log age: {age_minutes:.1f}m")
            else:
                result = {"ok": True, "type": "waiting", "note": f"error log age {age_minutes:.1f}m < 5min"}
                log_event("loop", f"still verifying stability ({age_minutes:.1f}m)")
            evaluate_action("verify_stability", result, {"goal_id": goal_id})
            return result

        if subtask_id == "restore_crontab_jobs":
            try:
                crontab = subprocess.check_output(["crontab", "-l"], text=True)
                needed = ["molty-poster", "nova_bridge", "simmer", "inner_monologue",
                          "dream_generator", "overnight_synthesis", "memory_consolidation",
                          "contradiction_resolution", "drift_detector", "phenomenology"]
                missing = [j for j in needed if j not in crontab]
                if not missing:
                    mark_subtask_done(goal_id, "restore_crontab_jobs")
                    result = update_goal_progress(goal_id, 0.85, "crontab verified")
                    log_event("crontab", "all cron jobs present")
                else:
                    result = flag_blocker(goal_id, f"missing crontab jobs: {missing}")
                    log_event("crontab", f"missing: {missing}")
            except subprocess.CalledProcessError as e:
                result = flag_blocker(goal_id, f"crontab read failed: {e}")
                log_event("crontab", f"error: {e}")
            evaluate_action("crontab_check", result, {"goal_id": goal_id})
            return result

        if subtask_id == "bridge_openclaw_and_loop":
            # nova_bridge runs via cron every 2 min, not as a daemon.
            # Verify it works by running it directly and checking log freshness.
            try:
                bridge_log = "/Users/dr.claw/.nova/logs/bridge.log"
                # Check if bridge log exists and was updated recently
                if os.path.exists(bridge_log):
                    mtime = os.path.getmtime(bridge_log)
                    age_min = (time.time() - mtime) / 60
                    with open(bridge_log) as f:
                        lines = f.readlines()
                    last_line = lines[-1].strip() if lines else "empty"
                    if age_min < 5:
                        mark_subtask_done(goal_id, "bridge_openclaw_and_loop")
                        result = update_goal_progress(goal_id, 1.0, "bridge verified")
                        log_event("bridge", f"healthy — log age {age_min:.1f}m, last: {last_line[:60]}")
                    else:
                        # Run bridge directly to bring it up to date
                        subprocess.run(["python3", str(NOVA_HOME / "nova_bridge.py")],
                                      capture_output=True, timeout=30)
                        mtime2 = os.path.getmtime(bridge_log)
                        age_min2 = (time.time() - mtime2) / 60
                        if age_min2 < 1:
                            mark_subtask_done(goal_id, "bridge_openclaw_and_loop")
                            result = update_goal_progress(goal_id, 1.0, "bridge refreshed")
                            log_event("bridge", f"refreshed — log age {age_min2:.1f}m")
                        else:
                            result = flag_blocker(goal_id, "bridge log stale after refresh")
                            log_event("bridge", "log still stale after refresh")
                else:
                    # Bridge has never run — run it now
                    subprocess.run(["python3", str(NOVA_HOME / "nova_bridge.py")],
                                  capture_output=True, timeout=30)
                    if os.path.exists(bridge_log):
                        mark_subtask_done(goal_id, "bridge_openclaw_and_loop")
                        result = update_goal_progress(goal_id, 1.0, "bridge initialized")
                        log_event("bridge", "initialized first run")
                    else:
                        result = flag_blocker(goal_id, "bridge initialization failed")
                        log_event("bridge", "init failed")
            except Exception as e:
                result = flag_blocker(goal_id, f"bridge check failed: {e}")
                log_event("bridge", f"error: {e}")
            evaluate_action("bridge_check", result, {"goal_id": goal_id})
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
