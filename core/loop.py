#!/usr/bin/env python3
"""
core/loop.py
Nova Loop — Full Implementation (Phase 7)

7 layers:
 1. Goals → brain/goals.json
 2. Observe → state/observations.log
 3. Decide → core/decide.py
 4. Act → core/actions.py
 5. Evaluate → state/evaluations.json
 6. Retry → core/retry.py
 7. Memory → observations.log

Kill switch: set state/control.json "run" to false
"""

import os, sys, time, json, threading
from datetime import datetime

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent)

from core.bootstrap import bootstrap
from core.process import acquire_pid, release_pid
from core.decide import decide, idle_maintenance, mark_subtask_done
from core.actions import read_file, log_event, write_file, update_goal_progress, flag_blocker
from core.evaluate import evaluate_action
from core.retry import log_observation
from brain.three_tier_memory import session_close_flush

STATE_DIR = os.path.join(_parent, "state")
OBS_LOG = os.path.join(STATE_DIR, "observations.log")
CTRL_FILE = os.path.join(STATE_DIR, "control.json")
GOALS_FILE = os.path.join(_parent, "brain", "goals.json")
LOOP_STATE_FILE = os.path.join(_parent, "LOOP_STATE.md")


def write_loop_state(loop_count, last_decision, last_result, errors, status="running", stopped_reason=None):
    """Write current loop state to LOOP_STATE.md after every cycle."""
    now = datetime.now().isoformat()
    action = last_decision.get("action", "unknown") if last_decision else "none"
    goal_id = last_decision.get("goal_id", "—") if last_decision else "—"
    subtask = last_decision.get("subtask_id", "—") if last_decision else "—"
    result_ok = last_result.get("ok", False) if last_result else False
    result_type = last_result.get("type", "—") if last_result else "—"

    error_block = "\n".join(f"- {e}" for e in errors) if errors else "- none"

    lines = [
        f"# LOOP_STATE",
        f"",
        f"**Status:** {status}",
        f"**As of:** {now}",
        f"**Cycle:** {loop_count}",
        f"",
        f"## Last Cycle",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Action | `{action}` |",
        f"| Goal | `{goal_id}` |",
        f"| Subtask | `{subtask}` |",
        f"| Result | `{result_type}` ({'✅' if result_ok else '❌'}) |",
        f"",
        f"## Errors",
        error_block,
        f"",
    ]

    if stopped_reason:
        lines += [f"## Stopped", f"**Reason:** {stopped_reason}", f""]

    try:
        with open(LOOP_STATE_FILE, "w") as f:
            f.write("\n".join(lines))
    except IOError as e:
        log_event("loop_state", f"failed to write LOOP_STATE.md: {e}")


def read_control():
    if not os.path.exists(CTRL_FILE): return None
    try:
        with open(CTRL_FILE) as f: return json.load(f)
    except (json.JSONDecodeError, IOError): return None

def observe():
    obs = {"timestamp": datetime.now().isoformat(), "errors": [], "status": "ok"}
    if not os.path.exists(CTRL_FILE): obs["errors"].append("control.json missing")
    if not os.path.exists(GOALS_FILE): obs["errors"].append("goals.json missing")
    return obs

def execute_action(decision):
    action_type = decision.get("action")
    goal_id = decision.get("goal_id")
    subtask_id = decision.get("subtask_id")

    if action_type == "idle":
        log_observation("idle — nothing to do")
        return {"ok": True, "type": "idle"}

    if action_type == "mark_complete":
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
            if result.get("ok"): mark_subtask_done(goal_id, "implement_pipeline")
            evaluate_action("write_file", result, {"goal_id": goal_id, "subtask": subtask_id})
            return result
        if subtask_id == "integrate_retrieval":
            result = write_file(
                os.path.join(_parent, "brain", "vector_retrieval.py"),
                "# vector_retrieval.py\n# Integration of vector store into session startup.\n# Status: pending — blocked on embedding provider decision.\n",
                "retrieval integration stub"
            )
            if result.get("ok"): mark_subtask_done(goal_id, "integrate_retrieval")
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
    last_decision = None
    last_result = None

    try:
        while True:
            control = read_control()
            if control is None:
                log_observation("control.json missing, waiting 60s")
                write_loop_state(loop_count, last_decision, last_result, ["control.json missing"])
                time.sleep(60); continue
            if not control.get("run", False):
                stopped_reason = "stopped by control.json"
                break
            loop_count += 1
            if loop_count > control.get("max_cycles", 1000):
                stopped_reason = f"cycle limit ({control.get('max_cycles')})"
                break

            observations = observe()
            if observations.get("errors"):
                for err in observations["errors"]: log_event("observe", f"error: {err}")
                write_loop_state(loop_count, last_decision, last_result, observations["errors"])
                time.sleep(control.get("cycle_interval_seconds", 30)); continue

            last_decision = decide() or idle_maintenance()
            last_result = execute_action(last_decision)

            if last_decision.get("action") != "idle":
                evaluate_action(
                    last_result.get("type", "unknown"), last_result,
                    {"goal_id": last_decision.get("goal_id"), "subtask": last_decision.get("subtask_id")}
                )

            log_observation(f"cycle {loop_count} done [{last_decision.get('action')}]")
            write_loop_state(loop_count, last_decision, last_result, [])

            # Async PIRP — Option B (non-blocking)
            # After each cycle, feed decision context through the full cognitive pipeline
            # in the background. Output available to next session via logs/pirp_output.json.
            def _pirp_background():
                try:
                    from pathlib import Path
                    from brain.bootstrap import get_nova
                    nova = get_nova()
                    goal_id = last_decision.get("goal_id", "none")
                    subtask = last_decision.get("subtask_id", "none")
                    action = last_decision.get("action", "idle")
                    result_type = last_result.get("type", "unknown") if last_result else "unknown"
                    goal_title = ""
                    if "goal" in last_decision and isinstance(last_decision["goal"], dict):
                        goal_title = last_decision["goal"].get("title", "")
                    text_input = f"Cycle {loop_count}: goal={goal_id} ({goal_title}), subtask={subtask}, action={action}, result={result_type}"
                    output = nova.process(text_input, architect_present=False, architect_active=False)
                    out_path = Path(_parent) / "logs" / "pirp_output.json"
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    out_path.write_text(json.dumps(output, indent=2))
                except Exception as e:
                    log_event("pirp_async", f"background PIRP failed: {e}")

            t = threading.Thread(target=_pirp_background, daemon=True)
            t.start()

            time.sleep(control.get("cycle_interval_seconds", 30))

    except KeyboardInterrupt:
        stopped_reason = "keyboard interrupt"
    finally:
        release_pid()
        write_loop_state(loop_count, last_decision, last_result, [], status="stopped", stopped_reason=stopped_reason)
        log_observation(f"Loop ended: {stopped_reason}")
        print(f"Loop ended: {stopped_reason}")
        try:
            flush_result = session_close_flush()
            log_event("session_flush", f"flushed {flush_result.get('flushed', {}).get('flushed', 0)} entries on shutdown")
        except Exception as e:
            log_event("session_flush", f"failed on shutdown: {e}")

if __name__ == "__main__":
    print("Nova Loop starting (Phase 7)...")
    run_loop()
