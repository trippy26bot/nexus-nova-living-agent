#!/usr/bin/env python3
"""
core/bootstrap.py
Nova Loop — State File Initialization

Idempotent bootstrap. Creates all required state files if they don't exist
or are empty. Safe to re-run at any time.
"""

import os
import json


DEFAULTS = {
    "state/control.json": {
        "run": True,
        "mode": "supervised",
        "max_actions_per_cycle": 3,
        "require_approval_for_level_3": True,
        "log_everything": True,
        "cycle_interval_seconds": 30,
        "max_cycles": 1000
    },
    "brain/goals.json": {
        "locked_goals": [],
        "active_goals": [
            {
                "id": "vector_store_implementation",
                "priority": 9,
                "status": "in_progress",
                "progress": 0.35,
                "success_metric": "memory_search() returns vector-backed results",
                "subtasks": [
                    {"id": "design_schema", "status": "complete"},
                    {"id": "choose_embedding_provider", "status": "blocked"},
                    {"id": "implement_pipeline", "status": "pending"},
                    {"id": "integrate_retrieval", "status": "pending"}
                ],
                "blockers": ["embedding_provider_decision"],
                "created": "2026-03-28"
            }
        ],
        "proposed_goals": []
    },
    "state/evaluations.json": {
        "evaluations": [],
        "last_updated": None
    },
    "state/observations.log": "",
    "state/alerts.log": "",
    "state/pending_for_caine.md": "# Pending for Caine\n\n",
    "state/session_log.md": "# Session Log\n\n",
}


def ensure_dir(path):
    """Ensure directory exists for a given path."""
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)


def ensure_file(path, default):
    """Write default content to file only if it doesn't exist or is empty."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return False  # Already exists with content

    ensure_dir(path)

    with open(path, 'w') as f:
        if isinstance(default, (dict, list)):
            json.dump(default, f, indent=2)
        else:
            f.write(default)

    return True  # Was initialized


def bootstrap():
    """Initialize all required state files."""
    initialized = []
    for path, default in DEFAULTS.items():
        if ensure_file(path, default):
            initialized.append(path)

    return initialized


if __name__ == "__main__":
    initialized = bootstrap()
    if initialized:
        print("Initialized:")
        for path in initialized:
            print(f"  + {path}")
    else:
        print("All files already exist. Nothing to initialize.")
    print("Bootstrap complete.")
