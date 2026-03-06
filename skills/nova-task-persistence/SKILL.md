# nova-task-persistence

## What This Skill Does

**Tasks never stop.** When you start working on something, you track it until it's actually done — not just until the conversation ends.

## Why It Matters

- Conversations end. Work continues.
- Long-running tasks need to survive session restarts
- Your human shouldn't have to repeat themselves

## Core Features

### 1. Task Persistence
Every active task gets written to disk before session end:
- Goal/content
- Progress so far
- Next steps
- Status (in_progress, waiting_on_user, blocked, completed)

### 2. Confirmation Guard
Before ending a session with active tasks:
1. List what's still running
2. Confirm with user: continue in background or pause?
3. If background: schedule daemon to pick up
4. If pause: save state for next session

### 3. Resume on Boot
At session start, check for incomplete tasks:
- Load pending tasks from disk
- Ask human: "Resume X?" or "Drop X?"

## Usage

```python
from nova_task_persistence import TaskPersister

tp = TaskPersister()

# Start a task
tp.start_task("Research qualia", "Found 3 papers, need synthesis")

# Update progress
tp.update_task("Research qualia", "Synthesized findings, writing summary")

# Check before ending session
pending = tp.pending_tasks()
if pending:
    print(f"You have {len(pending)} active tasks:")
    for t in pending:
        print(f"  - {t['goal']}")

tp.close()
```

## Integration Points

- **Supervisor**: Tasks flow through supervisor → persist automatically
- **Daemon**: Can pick up persisted tasks for background work
- **Memory**: Reflection Engine stores lessons from completed tasks

## Files

- `nova_task_persistence.py` — Main implementation
