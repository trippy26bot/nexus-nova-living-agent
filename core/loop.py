#!/usr/bin/env python3
"""
core/loop.py
Nova Loop — The Heart

Persistent daemon. Runs until stopped via control.json or PID kill.

Usage:
    python core/loop.py
    # or with pm2:
    pm2 start core/loop.py --name nova-loop
"""

import os
import sys
import time
import json
from datetime import datetime

# Add parent directory to path so 'core' imports work
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent)

from core.bootstrap import bootstrap
from core.process import acquire_pid, release_pid

STATE_DIR = os.path.join(_parent, "state")
OBS_LOG = os.path.join(STATE_DIR, "observations.log")
CTRL_FILE = os.path.join(STATE_DIR, "control.json")


def tick(loop_count):
    """Placeholder tick — replace in Phase 4 with real decision engine."""
    ts = datetime.now().isoformat()
    msg = f"[tick {loop_count}] {ts}\n"
    with open(OBS_LOG, "a") as f:
        f.write(msg)
    print(f"Loop tick {loop_count}")


def read_control():
    """Read control.json safely."""
    if not os.path.exists(CTRL_FILE):
        return None
    try:
        with open(CTRL_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def run_loop():
    """
    Main loop. Idempotent bootstrap + PID acquire on start.
    Clean release on exit.
    """
    bootstrap()  # Idempotent — safe to call every startup
    acquire_pid()

    loop_count = 0
    stopped_reason = None

    try:
        while True:
            control = read_control()

            if control is None:
                print("ERROR: control.json not found or invalid. Waiting...")
                time.sleep(60)
                continue

            if not control.get("run", False):
                stopped_reason = "stopped by control.json"
                break

            loop_count += 1

            max_cycles = control.get("max_cycles", 1000)
            if loop_count > max_cycles:
                stopped_reason = f"cycle limit reached ({max_cycles})"
                break

            # Core tick — replace in Phase 4
            tick(loop_count)

            interval = control.get("cycle_interval_seconds", 30)
            time.sleep(interval)

    except KeyboardInterrupt:
        stopped_reason = "keyboard interrupt"
    finally:
        release_pid()
        if stopped_reason:
            print(f"Loop ended: {stopped_reason}")


if __name__ == "__main__":
    print("Nova Loop starting...")
    run_loop()
