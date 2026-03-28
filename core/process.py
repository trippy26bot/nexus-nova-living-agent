#!/usr/bin/env python3
"""
core/process.py
Nova Loop — Process Management Utilities

Handles PID file for single-instance enforcement.
"""

import os
import sys

PID_FILE = "state/loop.pid"


def acquire_pid():
    """
    Acquire the PID file. Exits if another instance is already running.
    """
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            old_pid = int(f.read().strip())
        try:
            os.kill(old_pid, 0)  # Signal 0 = check if process exists
            print(f"Loop already running (PID {old_pid}). Exiting.")
            sys.exit(0)
        except ProcessLookupError:
            pass  # Stale PID file — process is dead, safe to overwrite

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))


def release_pid():
    """
    Release the PID file on exit.
    """
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
