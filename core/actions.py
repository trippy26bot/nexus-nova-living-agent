#!/usr/bin/env python3
"""
core/actions.py
Nova Loop — Action System (Level 1 + 2)

Level 1 (silent):
  - read_file()
  - log_event()

Level 2 (logged):
  - write_file() — with safe_write integrity check
  - update_goal_progress()
  - commit_changes()
  - flag_blocker()
  - propose_goal()
"""

import os
import sys
import json
from datetime import datetime

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent)

from core.safe_write import safe_write, safe_write_json, load_json

STATE_DIR = os.path.join(_parent, "state")
OBS_LOG = os.path.join(STATE_DIR, "observations.log")
GOALS_FILE = os.path.join(_parent, "brain", "goals.json")
ALERTS_LOG = os.path.join(STATE_DIR, "alerts.log")
PENDING_FILE = os.path.join(STATE_DIR, "pending_for_caine.md")


# ─── Level 1 Actions (silent) ────────────────────────────────────────────────

def read_file(path):
    """Read a file. Returns content or None if missing."""
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return f.read()
    except IOError:
        return None


def log_event(event_type, detail):
    """Append to observations.log. Silent Level 1 action."""
    ts = datetime.now().isoformat()
    entry = f"[{ts}] [{event_type.upper()}] {detail}\n"
    with open(OBS_LOG, "a") as f:
        f.write(entry)
    return {"ok": True, "type": "log_event", "event_type": event_type}


# ─── Level 2 Actions (logged, no approval needed) ─────────────────────────────

def write_file(path, content, reason=None):
    """
    Write content to a file using safe_write.
    Level 2 — logged to observations.
    """
    validated_content = content.strip() if content else None
    if not validated_content or len(validated_content) < 10:
        return {
            "ok": False,
            "type": "write_file",
            "error": "content too short or empty",
            "path": path
        }

    try:
        safe_write(path, validated_content)
        log_event(
            "write_file",
            f"wrote {len(validated_content)} chars to {path}"
            + (f" | reason: {reason}" if reason else "")
        )
        return {"ok": True, "type": "write_file", "path": path, "chars": len(validated_content)}
    except ValueError as e:
        return {"ok": False, "type": "write_file", "error": str(e), "path": path}


def update_goal_progress(goal_id, progress, status=None):
    """
    Update progress on a goal in goals.json.
    Level 2 — logged.
    """
    goals = load_json(GOALS_FILE)
    if goals is None:
        return {"ok": False, "type": "update_goal_progress", "error": "goals.json not found"}

    found = False
    for goal in goals.get("active_goals", []):
        if goal.get("id") == goal_id:
            goal["progress"] = progress
            if status:
                goal["status"] = status
            found = True
            break

    if not found:
        return {"ok": False, "type": "update_goal_progress", "error": f"goal {goal_id} not found"}

    try:
        safe_write_json(GOALS_FILE, goals)
        log_event(
            "update_goal_progress",
            f"goal={goal_id} progress={progress}"
            + (f" status={status}" if status else "")
        )
        return {"ok": True, "type": "update_goal_progress", "goal_id": goal_id, "progress": progress}
    except ValueError as e:
        return {"ok": False, "type": "update_goal_progress", "error": str(e)}


def commit_changes(message):
    """
    Git add + commit all changed files.
    Level 2 — logged.
    """
    import subprocess

    try:
        # Stage all changes
        subprocess.run(["git", "add", "-A"], cwd=_parent, check=True, capture_output=True)
        # Commit with message
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=_parent,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            log_event("git_commit", f"committed: {message}")
            return {"ok": True, "type": "git_commit", "message": message}
        else:
            log_event("git_commit", f"nothing to commit: {result.stderr.strip()}")
            return {"ok": True, "type": "git_commit", "note": "nothing to commit"}
    except subprocess.CalledProcessError as e:
        return {"ok": False, "type": "git_commit", "error": str(e)}


def flag_blocker(goal_id, reason):
    """
    Mark a goal as blocked and write to alerts.log + pending_for_caine.md.
    Level 2 — triggers escalation in Phase 6.
    """
    goals = load_json(GOALS_FILE)
    if goals is None:
        return {"ok": False, "type": "flag_blocker", "error": "goals.json not found"}

    found = False
    for goal in goals.get("active_goals", []):
        if goal.get("id") == goal_id:
            goal["status"] = "blocked"
            goal.setdefault("blockers", []).append(reason)
            found = True
            break

    if not found:
        return {"ok": False, "type": "flag_blocker", "error": f"goal {goal_id} not found"}

    try:
        safe_write_json(GOALS_FILE, goals)
    except ValueError as e:
        return {"ok": False, "type": "flag_blocker", "error": f"goals write failed: {e}"}

    # Write to alerts.log
    ts = datetime.now().isoformat()
    alert_entry = f"[{ts}] BLOCKED: goal={goal_id} reason={reason}\n"
    with open(ALERTS_LOG, "a") as f:
        f.write(alert_entry)

    # Append to pending_for_caine.md
    pending_entry = f"\n## Blocked: {goal_id}\n**Reason:** {reason}\n**At:** {ts}\n\n"
    existing = read_file(PENDING_FILE) or ""
    safe_write(PENDING_FILE, existing + pending_entry)

    log_event("flag_blocker", f"goal={goal_id} reason={reason}")
    return {"ok": True, "type": "flag_blocker", "goal_id": goal_id, "reason": reason}


def propose_goal(goal_object):
    """
    Add a proposed goal to goals.json proposed_goals.
    Level 2 — does NOT activate, only proposes.
    """
    goals = load_json(GOALS_FILE)
    if goals is None:
        return {"ok": False, "type": "propose_goal", "error": "goals.json not found"}

    if not isinstance(goal_object, dict) or "id" not in goal_object:
        return {"ok": False, "type": "propose_goal", "error": "goal_object must have 'id' field"}

    goals.setdefault("proposed_goals", []).append(goal_object)

    try:
        safe_write_json(GOALS_FILE, goals)
        log_event("propose_goal", f"proposed: {goal_object.get('id')} priority={goal_object.get('priority', '?')}")
        return {"ok": True, "type": "propose_goal", "goal_id": goal_object.get("id")}
    except ValueError as e:
        return {"ok": False, "type": "propose_goal", "error": str(e)}
