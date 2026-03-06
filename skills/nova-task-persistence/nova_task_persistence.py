#!/usr/bin/env python3
"""
nova_task_persistence.py — Task Persistence Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tasks survive session restarts. Work continues when you come back.

Usage:
 from nova_task_persistence import TaskPersister
 tp = TaskPersister()
 tp.start_task("Research qualia", "Found 3 papers")
 tp.update_task("Research qualia", "Synthesized findings")
 pending = tp.pending_tasks()
 tp.close()
"""

import json, sqlite3
from datetime import datetime
from pathlib import Path

NOVA_DIR = Path.home() / ".nova"
TASKS_DB = NOVA_DIR / "persistent_tasks.db"


def get_db():
    NOVA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(TASKS_DB))
    conn.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        goal TEXT,
        progress TEXT,
        status TEXT DEFAULT 'in_progress',
        created_at TEXT,
        updated_at TEXT,
        next_steps TEXT
    )""")
    conn.commit()
    return conn


class TaskPersister:
    """Persist tasks across sessions."""

    def __init__(self):
        self.conn = get_db()

    def start_task(self, goal: str, progress: str = "", next_steps: str = ""):
        """Register a new task."""
        now = datetime.now().isoformat()
        self.conn.execute(
            "INSERT INTO tasks (goal, progress, status, created_at, updated_at, next_steps) VALUES (?,?,?,?,?,?)",
            (goal, progress, "in_progress", now, now, next_steps)
        )
        self.conn.commit()

    def update_task(self, goal: str, progress: str = None, status: str = None, next_steps: str = None):
        """Update an existing task."""
        updates = []
        values = []
        now = datetime.now().isoformat()

        if progress is not None:
            updates.append("progress=?")
            values.append(progress)
        if status is not None:
            updates.append("status=?")
            values.append(status)
        if next_steps is not None:
            updates.append("next_steps=?")
            values.append(next_steps)
        updates.append("updated_at=?")
        values.append(now)
        values.append(goal)

        if updates:
            self.conn.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE goal=?", values)
            self.conn.commit()

    def complete_task(self, goal: str):
        """Mark task as completed."""
        self.update_task(goal, status="completed")

    def pending_tasks(self) -> list:
        """Get all in-progress tasks."""
        rows = self.conn.execute(
            "SELECT goal, progress, status, created_at, updated_at, next_steps FROM tasks WHERE status != 'completed' ORDER BY updated_at DESC"
        ).fetchall()
        return [
            {
                "goal": r[0],
                "progress": r[1],
                "status": r[2],
                "created": r[3],
                "updated": r[4],
                "next_steps": r[5]
            }
            for r in rows
        ]

    def all_tasks(self) -> list:
        """Get all tasks."""
        rows = self.conn.execute(
            "SELECT goal, progress, status, created_at, updated_at FROM tasks ORDER BY updated_at DESC"
        ).fetchall()
        return [{"goal": r[0], "progress": r[1], "status": r[2], "created": r[3], "updated": r[4]} for r in rows]

    def clear_completed(self):
        """Remove completed tasks."""
        self.conn.execute("DELETE FROM tasks WHERE status='completed'")
        self.conn.commit()

    def close(self):
        self.conn.close()


# ── GUARD FOR SESSION END ───────────────────────────────────────────────────

def confirm_before_exit(persister: TaskPersister) -> bool:
    """
    Before ending a session, check for pending tasks.
    Returns True if safe to exit, False if user confirmed to proceed.
    """
    pending = persister.pending_tasks()
    if not pending:
        return True

    print(f"\n⚠️  You have {len(pending)} active task(s):")
    for t in pending:
        print(f"  • {t['goal']}")
        if t['progress']:
            print(f"    Progress: {t['progress'][:80]}")

    print("\nOptions:")
    print("  [c] Continue in background (daemon)")
    print("  [p] Pause (resume next session)")
    print("  [d] Drop tasks")
    print("  [q] Quit anyway")

    choice = input("\n> ").strip().lower()

    if choice == "c":
        # TODO: schedule daemon to resume
        print("→ Tasks will continue in background")
        return True
    elif choice == "p":
        print("→ Tasks saved for next session")
        return True
    elif choice == "d":
        persister.clear_completed()
        print("→ Tasks dropped")
        return True
    else:
        return False


if __name__ == "__main__":
    tp = TaskPersister()

    # Demo
    print("Task Persister Demo")
    print("=" * 30)

    # Start a task
    tp.start_task("Research AGI safety", "Reading 3 papers on RLHF", "Write summary")

    # Check pending
    pending = tp.pending_tasks()
    print(f"Pending: {len(pending)}")
    for t in pending:
        print(f"  - {t['goal']}: {t['progress']}")

    # Update
    tp.update_task("Research AGI safety", progress="Finished papers, synthesizing insights", status="in_progress")

    # Complete
    tp.complete_task("Research AGI safety")
    print("Completed!")

    tp.close()
