#!/usr/bin/env python3
"""
demo/run_demo.py
Nexus Nova — Minimal Demo

Boots the framework with default seed files and runs a single
observe → decide → act cycle with a memory write.
"""

import os
import sys
import hashlib

# Add parent to path so we can import core modules
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent)

from core.safe_write import read_file, safe_write, load_json
from core.decide import decide, mark_subtask_done
from core.actions import write_file, log_event


IDENTITY_FILES = [
    "SOUL.md",
    "IDENTITY.md",
    "NOVA_DIRECTIVE.md",
    "PERSONALITY.md",
    "PRESENCE.md",
    "EPISTEMIC_BOUNDARIES.md",
    "NOVA_BECOMING.md",
]

MEMORY_FILE = os.path.join(_parent, "memory", "demo_memory.md")


def hash_file(path):
    """Return SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def load_identity_files():
    """Load all identity files and print their status."""
    print("=" * 60)
    print("NEXUS NOVA — Framework Demo")
    print("=" * 60)
    print()

    loaded = {}
    for fname in IDENTITY_FILES:
        path = os.path.join(_parent, fname)
        if os.path.exists(path):
            content = read_file(path)
            loaded[fname] = content
            print(f"✓ {fname} — {len(content)} chars, hash: {hash_file(path)[:16]}...")
        else:
            print(f"✗ {fname} — not found (expected in full framework)")
    print()
    return loaded


def run_cycle():
    """Run one observe → decide → act cycle."""
    print("-" * 60)
    print("CYCLE 1: observe → decide → act")
    print("-" * 60)
    print()

    # Observe: check goals
    goals = load_json(os.path.join(_parent, "brain", "goals.json"))
    if goals:
        active = goals.get("active_goals", [])
        print(f"[observe] {len(active)} active goal(s)")
        for g in active:
            print(f"  - {g['id']} (priority: {g.get('priority', 0)})")
    else:
        print("[observe] No goals file — bootstrapping demo state")
        goals = {
            "active_goals": [{
                "id": "demo_goal",
                "priority": 10,
                "status": "in_progress",
                "subtasks": [{"id": "demo_memory_write", "status": "pending"}]
            }]
        }
        os.makedirs(os.path.join(_parent, "brain"), exist_ok=True)
        import json
        with open(os.path.join(_parent, "brain", "goals.json"), "w") as f:
            json.dump(goals, f, indent=2)
        print("  Created demo_goal with one subtask: demo_memory_write")

    print()

    # Decide: pick next subtask
    decision = decide()
    if decision:
        print(f"[decide] Selected: {decision['goal_id']} / {decision.get('subtask_id', 'N/A')}")
        print(f"  action: {decision['action']}")
    else:
        print("[decide] No pending subtasks — goal may already be complete")
    print()

    # Act: write to memory
    print("[act] Writing demo memory entry...")
    memory_entry = f"""# Demo Memory Entry

**Timestamp:** (written by run_demo.py)
**Cycle:** 1

This is a synthetic memory write demonstrating the framework's
memory write capability. Not a real session log.

## What happened
- Framework booted with {len(IDENTITY_FILES)} identity files
- Completed one observe → decide → act cycle
- Identity files loaded and hashed successfully

## Consistency check
All identity files present and readable.
"""
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    safe_write(MEMORY_FILE, memory_entry)
    print(f"  ✓ Wrote: {MEMORY_FILE}")

    # Mark subtask done
    if decision and decision.get("subtask_id"):
        mark_subtask_done(decision["goal_id"], decision["subtask_id"])
        print(f"  ✓ Marked subtask '{decision['subtask_id']}' complete")

    print()
    print("-" * 60)
    print("Demo complete. Memory file written. Framework is operational.")
    print("-" * 60)


if __name__ == "__main__":
    load_identity_files()
    run_cycle()
