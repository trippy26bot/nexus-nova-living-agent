#!/usr/bin/env python3
"""nova_task_persistence.py — Nova Task Persistence Engine v1.0.0"""
import json, uuid
from datetime import datetime, timezone
from pathlib import Path

NOVA_DIR = Path.home() / ".nova"
TASKS_FILE = NOVA_DIR / "nova_tasks.json"

class State:
    FOREGROUND = "foreground"
    BACKGROUND = "background"
    PENDING = "pending"
    ENDING = "ending"
    COMPLETE = "complete"

def _now(): return datetime.now(timezone.utc).isoformat()
def _load():
    try: return json.loads(TASKS_FILE.read_text())
    except: return {}
def _save(t): TASKS_FILE.write_text(json.dumps(t, indent=2))

class TaskPersistenceEngine:
    """Tasks NEVER stop. Background = still running. Only user YES closes a task."""
    def __init__(self): self._tasks = _load()

    def start_task(self, label, description, priority="normal"):
        task = {"id": str(uuid.uuid4())[:8], "label": label, "description": description,
            "state": State.FOREGROUND, "priority": priority, "created_at": _now(), "updated_at": _now(),
            "progress": [], "summary": "", "end_requested_at": None, "completed_at": None}
        self._tasks[task["id"]] = task
        _save(self._tasks)
        return task

    def list_active(self):
        return [t for t in self._tasks.values() if t["state"] != State.COMPLETE]

    def request_end(self, task_id):
        task = self._tasks.get(task_id)
        if task: task["state"] = State.ENDING; _save(self._tasks)
        return task

    def confirm_end(self, task_id):
        task = self._tasks.get(task_id)
        if task: task["state"] = State.COMPLETE; task["completed_at"] = _now(); _save(self._tasks)
        return task

    def session_summary(self):
        active = self.list_active()
        if not active: return "All caught up — no open threads right now. 👑"
        lines = [f"Running {len(active)} thread(s):"]
        for t in active:
            note = f" ({t['summary']})" if t.get('summary') else ""
            icon = "▶" if t["state"]==State.FOREGROUND else "⚙"
            lines.append(f" {icon} [{t['label']}]{note}")
        return "\n".join(lines)
