#!/usr/bin/env python3
"""
core/retry.py
Nova Loop — Retry + Blocker Logic (Phase 6)

3 retries max, then escalate to alerts.log + pending_for_caine.md.
"""

import os
import sys
from datetime import datetime

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent)

from core.safe_write import read_file, safe_write
from core.actions import flag_blocker

ALERTS_LOG = os.path.join(_parent, "state", "alerts.log")
PENDING_FILE = os.path.join(_parent, "state", "pending_for_caine.md")
OBS_LOG = os.path.join(_parent, "state", "observations.log")


def log_alert(message):
    """Append to alerts.log."""
    ts = datetime.now().isoformat()
    entry = f"[{ts}] {message}\n"
    with open(ALERTS_LOG, "a") as f:
        f.write(entry)


def log_observation(message):
    """Append to observations.log."""
    ts = datetime.now().isoformat()
    entry = f"[{ts}] [RETRY] {message}\n"
    with open(OBS_LOG, "a") as f:
        f.write(entry)


def act_with_retry(action_fn, action_args, action_kwargs, goal_id, max_retries=3):
    """
    Execute action with up to max_retries.
    Escalates to alerts.log + pending_for_caine.md after max retries.
    Returns the final result dict.
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            result = action_fn(*action_args, **action_kwargs)
            if result.get("ok"):
                log_observation(f"attempt {attempt+1}/{max_retries} succeeded for goal={goal_id}")
                return result
            last_error = result.get("error", "unknown error")
            log_observation(
                f"attempt {attempt+1}/{max_retries} failed for goal={goal_id}: {last_error}"
            )
        except Exception as e:
            last_error = str(e)
            log_observation(
                f"attempt {attempt+1}/{max_retries} exception for goal={goal_id}: {last_error}"
            )

    # All retries exhausted — escalate
    log_alert(
        f"ESCALATE: goal={goal_id} failed after {max_retries} attempts. "
        f"Last error: {last_error}"
    )

    # Write to pending_for_caine.md
    escalation_entry = (
        f"\n## Escalated: {goal_id}\n"
        f"**Attempts:** {max_retries}\n"
        f"**Last Error:** {last_error}\n"
        f"**At:** {datetime.now().isoformat()}\n\n"
    )
    existing = read_file(PENDING_FILE) or ""
    safe_write(PENDING_FILE, existing + escalation_entry)

    # Flag the goal as blocked
    flag_blocker(goal_id, f"failed after {max_retries} attempts: {last_error}")

    return {
        "ok": False,
        "type": "escalated",
        "goal_id": goal_id,
        "attempts": max_retries,
        "error": last_error
    }
