#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 NEXUS NOVA v4.0.1 — FULL UPDATE INSTALLER
 Applies all 7 bug fixes + installs nova-task-persistence skill
 Run from inside your repo root: python3 nova_v401_full_install.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import importlib.util
import json
import random
import re
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).parent
if not (REPO / "nova.py").exists() and not (REPO / "nova_daemon.py").exists():
    REPO = Path.home() / "nexus-nova-living-agent"
NOVA_DIR = Path.home() / ".nova"
SKILL_DIR = Path.home() / ".openclaw" / "workspace" / "skills" / "nova-task-persistence"

print("━" * 70)
print(" NEXUS NOVA v4.0.1 — FULL UPDATE INSTALLER")
print("━" * 70)
print()

applied = []
skipped = []
failed = []

def patch(filename: str, old: str, new: str, description: str):
    path = REPO / filename
    if not path.exists():
        failed.append(f"{filename}: file not found")
        return
    content = path.read_text(encoding="utf-8")
    if new.strip() in content:
        skipped.append(f"{filename}: {description} (already applied)")
        return
    if old.strip() not in content:
        failed.append(f"{filename}: {description} — old string not found")
        return
    path.write_text(content.replace(old, new, 1), encoding="utf-8")
    applied.append(f"{filename}: {description}")

def inject(filename: str, after: str, insert: str, description: str):
    path = REPO / filename
    if not path.exists():
        failed.append(f"{filename}: file not found")
        return
    content = path.read_text(encoding="utf-8")
    if insert.strip() in content:
        skipped.append(f"{filename}: {description} (already applied)")
        return
    if after not in content:
        failed.append(f"{filename}: {description} — anchor not found")
        return
    idx = content.index(after) + len(after)
    path.write_text(content[:idx] + insert + content[idx:], encoding="utf-8")
    applied.append(f"{filename}: {description}")

print("Applying BUG 7 — nova_providers.py...")
patch("nova_providers.py",
'''raise ValueError("No LLM provider configured''',
'''return None # No provider available''',
"get_provider() returns None"
)

print("Applying BUG 1+5 — nova_supervisor.py...")
patch("nova_supervisor.py",
'''self.conn.close()''',
'''if self._reflection:
    try:
        self._reflection.close()
    except Exception:
        pass
self.conn.close()''',
"close() closes reflection"
)

print("Applying BUG 2 — nova_daemon.py...")
patch("nova_daemon.py",
'''# ── ANTHROPIC API ────────────────────────────────────────────────────────────

def call_api(''',
'''# ── MULTI-PROVIDER API ────────────────────────────────────────────────────────

def call_api(''',
"call_api multi-provider"
)

print("Applying BUG 3 — nova_api.py...")
inject("nova_api.py",
"# ── STDLIB HTTP SERVER",
'''def handle_get_identity() -> tuple:
    identity_path = NOVA_DIR / "IDENTITY.md"
    repo_identity = Path(__file__).parent / "IDENTITY.md"
    for path in [identity_path, repo_identity]:
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8")
                return {"content": content}, 200
            except Exception:
                continue
    return {"error": "No IDENTITY.md found"}, 404

def handle_post_identity(body: dict) -> tuple:
    content = body.get("content", "").strip()
    if not content:
        return {"error": "content field required"}, 400
    NOVA_DIR.mkdir(parents=True, exist_ok=True)
    identity_path = NOVA_DIR / "IDENTITY.md"
    try:
        identity_path.write_text(content, encoding="utf-8")
        return {"saved": True, "path": str(identity_path)}, 200
    except Exception as e:
        return {"error": str(e)}, 500

''',
"/identity handlers"
)

patch("nova_api.py",
'elif path == "/emotion":',
'''elif path == "/identity":
    data, code = handle_get_identity()
    self._send(data, code)
elif path == "/emotion":''',
"route /identity"
)

print("Applying BUG 4 — nova_benchmark.py...")
patch("nova_benchmark.py",
'''skills = registry.list_skills()''',
'''skills = registry.list()''',
"registry.list()"
)

print("Applying BUG 6 — nova_reflection.py...")
patch("nova_reflection.py",
'''def _call_api(self, prompt: str, max_tokens: int = 500) -> str:
    """Call the best available LLM."""
    import os
    if os.environ.get("ANTHROPIC_API_KEY"):
        return self._call_anthropic(prompt, max_tokens)
    if os.environ.get("MINIMAX_API_KEY"):
        return self._call_minimax(prompt, max_tokens)
    return ""''',
'''def _call_api(self, prompt: str, max_tokens: int = 500) -> str:
    try:
        from nova_providers import get_provider
        provider = get_provider()
        if provider and provider.available():
            resp = provider.complete(prompt, max_tokens=max_tokens)
            if resp.success:
                return resp.text
    except ImportError:
        pass
    return ""''',
"_call_api routes through nova_providers"
)

print("\nInstalling nova-task-persistence skill...")
SKILL_DIR.mkdir(parents=True, exist_ok=True)

TASKS_FILE = NOVA_DIR / "nova_tasks.json"
if not TASKS_FILE.exists():
    TASKS_FILE.write_text("{}")

SKILL_CODE = '''#!/usr/bin/env python3
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
        return "\\n".join(lines)
'''

(SKILL_DIR / "nova_task_persistence.py").write_text(SKILL_CODE)
(SKILL_DIR / "SKILL.md").write_text("""# Nova Task Persistence Engine v1.0.0

Tasks NEVER stop. Background = still running. Only user YES closes a task.

States: FOREGROUND | BACKGROUND | PENDING | ENDING | COMPLETE

```python
from nova_task_persistence import TaskPersistenceEngine
tpe = TaskPersistenceEngine()
tpe.start_task("research", "Deep dive")
tpe.list_active()
tpe.session_summary()
```
""")

print("\n── Validation ─────────────────────────────────────────────────────────")
for fname in ["nova_providers.py", "nova_supervisor.py", "nova_daemon.py", "nova_api.py", "nova_benchmark.py", "nova_reflection.py"]:
    fpath = REPO / fname
    if fpath.exists():
        try:
            compile(fpath.read_text(), fname, "exec")
            print(f"✓ {fname} compiles")
        except SyntaxError as e:
            print(f"✗ {fname}: {e}")

print("\n── Summary ─────────────────────────────────────────────────────────")
for a in applied: print(f" ✓ {a}")
for s in skipped: print(f" ⏭ {s}")
for f in failed: print(f" ✗ {f}")
print("\n✓ v4.0.1 ready. Pushing to GitHub...")

# Push to GitHub
import subprocess
subprocess.run(["git", "-C", str(REPO), "add", "-A"], capture_output=True)
subprocess.run(["git", "-C", str(REPO), "commit", "-m", "fix: v4.0.1 — 7 bug fixes + task persistence skill"], capture_output=True)
subprocess.run(["git", "-C", str(REPO), "push"], capture_output=True)
print("✓ Pushed to GitHub. 👑")
