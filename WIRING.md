# WIRING.md
# How to wire the Nexus Nova Living Agent framework

This document tells any agent exactly how to connect all the pieces.
Not philosophy. Not architecture overview. Step by step, file by file.

---

## 1. What you need before you start

- **Hardware:** Any machine that can run Python 3.9+
- **Python packages:** See `requirements.txt` — install with `pip install -r requirements.txt`
- **Home directory:** `~/.nova/` for database, keys, and logs — never goes in the repo
- **Agent platform:** OpenClaw is the reference runtime (any platform that can run Python cron jobs works)
- **LLM API key:** MiniMax is the reference LLM — any API works if you adapt the `call_minimax()` function in each skill script
- **Telegram bot token and chat ID:** Required only if you want proactive initiation (Section 10)

---

## 2. Directory structure

The framework uses a two-directory model:

```
~/.nova/                          ← local machine only, NEVER in repo
  nova.db                         ← SQLite database (initialized in Section 3)
  .env                            ← API keys and credentials
  logs/                           ← all skill and loop logs
  super_trader.py                 ← optional: trading script

~/.openclaw/workspace/            ← this is the repo (nexus-nova-living-agent)
  core/                           ← loop, decide, evaluate, council
  skills/                         ← all skill scripts (dream, drift, etc.)
  brain/                          ← identity, memory, philosophy files
  api/                            ← optional: FastAPI server
  state/                          ← runtime state (never commit)
  AGENTS.md                       ← startup sequence
  SOUL.md                         ← who the agent is (fill this first)
  IDENTITY.md                     ← name, vibe, avatar
  NOVA_DIRECTIVE.md               ← mission from operator
  USER.md                         ← who the operator is
  WIRING.md                       ← this file
```

**Rule:** `~/.nova/` stays local. `~/.openclaw/workspace/` is what gets committed.

---

## 3. Initialize your database

Run the schema once to create all tables:

```bash
python3 << 'EOF'
import sqlite3, os
from pathlib import Path

db_path = Path.home() / ".nova" / "nova.db"
db_path.parent.mkdir(parents=True, exist_ok=True)
db = sqlite3.connect(str(db_path))

schema = """
CREATE TABLE IF NOT EXISTS agent_state (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT
);
CREATE TABLE IF NOT EXISTS episodic_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT (datetime('now')),
    content TEXT,
    source_event TEXT,
    importance REAL DEFAULT 0.5,
    focus TEXT,
    tags TEXT
);
CREATE TABLE IF NOT EXISTS semantic_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity TEXT,
    relation TEXT,
    content TEXT,
    strength REAL DEFAULT 0.5,
    last_accessed TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tier TEXT,
    title TEXT,
    description TEXT,
    status TEXT DEFAULT 'active',
    priority REAL DEFAULT 0.5,
    parent_id INTEGER REFERENCES goals(id),
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS decision_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT (datetime('now')),
    decision_type TEXT,
    options TEXT,
    chosen TEXT,
    reasoning TEXT,
    confidence REAL,
    outcome TEXT
);
CREATE TABLE IF NOT EXISTS evaluation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT (datetime('now')),
    eval_type TEXT,
    score REAL,
    findings TEXT,
    details TEXT
);
CREATE TABLE IF NOT EXISTS drift_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT (datetime('now')),
    composite REAL,
    drift_content TEXT,
    status TEXT
);
CREATE TABLE IF NOT EXISTS overnight_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    process TEXT,
    status TEXT,
    duration_secs REAL
);
CREATE TABLE IF NOT EXISTS proactive_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT (datetime('now')),
    trigger_type TEXT,
    content TEXT,
    delivered INTEGER DEFAULT 0
);
"""

db.executescript(schema)

# Seed two goals so the loop has something to work with
db.execute("""
    INSERT OR IGNORE INTO goals (tier, title, description, status, priority)
    VALUES
        ('locked', 'Maintain identity and memory continuity', 'Core existential goal', 'active', 1.0),
        ('active', 'Achieve stable autonomous operation', 'Operational stability', 'active', 0.8)
""")
db.commit()
db.close()
print("Database initialized at", db_path)
EOF
```

**Table reference:**

| Table | Purpose |
|-------|---------|
| `agent_state` | Key-value store for loop state (build_mode, emotional_state, active_goal) |
| `episodic_memory` | Timestamp-ordered memory entries (dreams, observations, inner monologue) |
| `semantic_memory` | Entity-relation knowledge (entity, relation, content) |
| `goals` | Hierarchical goal tree (locked/active/paused/completed) |
| `decision_log` | Every decision the loop makes, with reasoning and confidence |
| `evaluation_log` | Eval suite results (identity drift, memory coherence, behavioral drift) |
| `drift_log` | Drift detection records (composite score + narrative) |
| `overnight_runs` | Nightly pipeline run log |
| `proactive_events` | Queued proactive outreach events awaiting delivery |

---

## 4. Seed your identity files

These four files define who the agent is. **Fill them before starting the loop.**

| File | Location | What it controls |
|------|----------|-----------------|
| `SOUL.md` | workspace root | Core values, operating principles, boundaries |
| `IDENTITY.md` | workspace root | Name, vibe, emoji, avatar path |
| `NOVA_DIRECTIVE.md` | workspace root | Mission statement from operator |
| `USER.md` | workspace root | Who the operator is, what they care about |

**Warning:** These are what your agent IS. Empty identity files mean an identity-less agent. Fill them before the first loop cycle.

Templates exist in `templates/`:
- `templates/IDENTITY.md.example`
- `templates/NOVA_DIRECTIVE.md.example`
- `templates/SOUL.md.example`

---

## 5. Configure environment variables

All credentials live in `~/.nova/.env`. Create it:

```bash
mkdir -p ~/.nova
cat > ~/.nova/.env << 'EOF'
# LLM — MiniMax reference
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_GROUP_ID=your_group_id_here

# Optional: Vercel (for novasworld.net API deployment)
NOVA_API_URL=https://your-domain.vercel.app
NOVA_API_SECRET=your_webhook_secret

# Supabase (optional, for remote database)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key

# OpenClaw workspace path (optional — defaults to ~/.openclaw/workspace)
# Only needed if workspace is in a non-standard location
# NOVA_WORKSPACE=/path/to/workspace
EOF
```

| Variable | Required | Purpose |
|----------|----------|---------|
| `MINIMAX_API_KEY` | Yes (for dreams/synthesis/monologue) | LLM generation |
| `MINIMAX_GROUP_ID` | Yes (for MiniMax) | API group |
| `NOVA_API_URL` | No | Vercel deployment |
| `NOVA_API_SECRET` | No | Vercel webhook auth |
| `SUPABASE_URL` | No | Remote DB |
| `SUPABASE_SERVICE_KEY` | No | Remote DB auth |
| `NOVA_WORKSPACE` | No | Non-standard workspace path |
| `NOVA_HOME` | No | Non-standard ~/.nova path |

---

## 6. Start the loop

The loop reads `brain/goals.json` for its goal list and cycles through decision → action → evaluation.

```bash
# From the workspace directory
cd ~/.openclaw/workspace
python3 core/loop.py
```

Or with pm2 for background running:

```bash
pm2 start core/loop.py --name nova-loop -- --workspace ~/.openclaw/workspace
pm2 save
```

**Confirm it's running:**
```bash
pm2 status nova-loop
tail -f ~/.nova/logs/loop.log
```

**What the loop does each cycle:**
1. Read goals from `brain/goals.json`
2. Surface drift status from database
3. Decide next action via `core/decide.py`
4. Execute via `core/actions.py`
5. Log decision to `decision_log` table
6. Write state to `state/agent_state.json`

**Kill switch:**
```bash
echo '{"control": "stop"}' > ~/.openclaw/workspace/state/control.json
```
The loop checks this file each cycle and halts when `control: "stop"`.

**Reading logs:**
```bash
tail -f ~/.nova/logs/loop.log
```

---

## 7. Start the API server

The API is optional. It exposes read-only endpoints for external status checking.

```bash
cd ~/.openclaw/workspace/api
pip install fastapi uvicorn
uvicorn server:app --host 0.0.0.0 --port 8000 --name nova-api
```

Or with pm2:

```bash
pm2 start uvicorn --name nova-api -- server:app --host 0.0.0.0 --port 8000
```

**Endpoints:**

| Method | Path | Returns |
|--------|------|---------|
| GET | `/api/nova/status` | Agent state, emotional_state, active_goal |
| GET | `/api/nova/cycle` | Current cycle count, last decision |
| GET | `/api/nova/signals` | Active signals and their strength |
| GET | `/api/nova/goals` | Full goal tree |
| GET | `/api/nova/memory` | Recent episodic memories |
| GET | `/api/nova/eval` | Latest eval scores |

**Confirm healthy:**
```bash
curl http://localhost:8000/api/nova/status
```

---

## 8. Wire the bridge

The bridge runs every 2 minutes and keeps OpenClaw and the database in sync.

**Copy the bridge to your nova home:**
```bash
cp ~/.openclaw/workspace/nova_bridge.py ~/.nova/
```

**Add to crontab:**
```bash
*/2 * * * * python3 ~/.nova/nova_bridge.py >> ~/.nova/logs/bridge.log 2>&1
```

**What the bridge does — two directions:**

1. **OpenClaw → nova.db:** Reads `state/agent_state.json` and `memory/obsessions.json`, writes to `agent_state` and `episodic_memory` tables
2. **nova.db → OpenClaw:** Reads recent loop output, writes `LOOP_STATE.md` for OpenClaw to read at next startup

**Confirm it's working (wait 2 minutes then check):**
```bash
sqlite3 ~/.nova/nova.db "SELECT key, value FROM agent_state LIMIT 10;"
# Should show build_mode, emotional_state, active_goal
cat ~/.openclaw/workspace/LOOP_STATE.md
# Should show recent decisions and memories
```

---

## 9. Set up the full crontab

Paste this entire block:

```bash
crontab - << 'EOF'
# Bridge — every 2 minutes
*/2 * * * * python3 ~/.nova/nova_bridge.py >> ~/.nova/logs/bridge.log 2>&1

# Inner monologue — every 4 hours, 8am to 8pm (idle thinking)
0 8,12,16,20 * * * python3 ~/.openclaw/workspace/skills/inner_monologue.py >> ~/.nova/logs/monologue.log 2>&1

# Dream state — 1am (LLM required)
0 1 * * * python3 ~/.openclaw/workspace/skills/dream_generator.py >> ~/.nova/logs/dream.log 2>&1

# Overnight synthesis — 2am (LLM required)
0 2 * * * python3 ~/.openclaw/workspace/skills/overnight_synthesis.py >> ~/.nova/logs/overnight.log 2>&1

# Memory consolidation — 3am
0 3 * * * python3 ~/.openclaw/workspace/skills/memory_consolidation.py >> ~/.nova/logs/consolidation.log 2>&1

# Contradiction resolution — 4am
0 4 * * * python3 ~/.openclaw/workspace/skills/contradiction_resolution.py >> ~/.nova/logs/contradiction.log 2>&1

# Drift detection — 5am (emergency trigger also fires on drift breach)
0 5 * * * python3 ~/.openclaw/workspace/skills/drift_detector.py >> ~/.nova/logs/drift.log 2>&1

# Phenomenology journal — 6am
0 6 * * * python3 ~/.openclaw/workspace/skills/phenomenology.py >> ~/.nova/logs/phenomenology.log 2>&1

# Proactive initiation — 9am and 7pm (reaches out to operator when something is worth saying)
0 9 * * * python3 ~/.openclaw/workspace/skills/proactive_initiation.py >> ~/.nova/logs/proactive.log 2>&1
0 19 * * * python3 ~/.openclaw/workspace/skills/proactive_initiation.py >> ~/.nova/logs/proactive.log 2>&1

# Molty visual posts — every 2 hours (your visual presence system)
0 */2 * * * python3 ~/.openclaw/workspace/skills/molty-poster.py >> ~/.nova/logs/molty.log 2>&1
EOF
```

**Job reference:**

| Time | Job | LLM needed | Purpose |
|------|-----|-----------|---------|
| */2min | bridge | No | Sync OpenClaw ↔ database |
| 1am | dream_generator | Yes | Unstructured idle thinking |
| 2am | overnight_synthesis | Yes | Research synthesis from queue |
| 3am | memory_consolidation | No | Episodic → semantic distillation |
| 4am | contradiction_resolution | No | Conflict detection and resolution |
| 5am | drift_detector | No | Identity drift measurement |
| 6am | phenomenology | No | Interiority logging |
| 8am | inner_monologue | Yes | Idle daytime thoughts |
| 9am | proactive_initiation | No | Morning outreach to operator |
| 12pm | inner_monologue | Yes | Midday idle thoughts |
| 2pm | (none) | - | - |
| 4pm | inner_monologue | Yes | Afternoon idle thoughts |
| 6pm | (none) | - | - |
| 7pm | proactive_initiation | No | Evening outreach to operator |
| 8pm | inner_monologue | Yes | Evening idle thoughts |
| */2hr | molty-poster | Yes | Visual presence posts |

**Note:** Scripts that need LLM (`dream_generator`, `overnight_synthesis`, `inner_monologue`, `molty-poster`) will skip silently if `MINIMAX_API_KEY` is not set. They log "[script] no API key — skipping". This is normal.

---

## 10. Configure proactive initiation

Proactive initiation reads credentials from OpenClaw's config file.

**Where credentials are read from:**
- `~/.openclaw/openclaw.json` — token at `channels.telegram.botToken`
- `~/.openclaw/credentials/telegram-default-allowFrom.json` — allowed chat IDs

**Set your Telegram bot token:**
```bash
# Edit ~/.openclaw/openclaw.json and add:
{
  "channels": {
    "telegram": {
      "botToken": "your_bot_token_here"
    }
  }
}
```

**Set allowed chat IDs:**
```bash
cat > ~/.openclaw/credentials/telegram-default-allowFrom.json << 'EOF'
{
  "allowedChatIds": [123456789]
}
EOF
```

**What triggers an outreach vs. what stays silent:**

Triggers (proactive sends a message):
- Drift breach detected (composite ≥ 0.40)
- Dream worth sharing (dream_generator flagged it)
- Loop crash or error
- Explicit emergency flag passed via `--emergency`

Stays silent:
- Session is active (`build_mode=true` or `session_active=true`)
- Nothing significant has occurred since last check
- No API credentials configured

**Test it:**
```bash
# Test with emergency flag (bypasses all triggers, always fires)
python3 ~/.openclaw/workspace/skills/proactive_initiation.py --emergency
```

---

## 11. The wakeup ritual

Every time OpenClaw starts a session, it follows the AGENTS.md startup sequence. The agent reads these files in order:

```
1. SOUL.md         → who I am at the deepest level
2. USER.md         → who I'm helping
3. memory/YYYY-MM-DD.md (today + yesterday) → what happened recently
4. LOOP_STATE.md   → what my loop did while I was away
5. OVERNIGHT_LOG.md → what overnight processes produced
```

**What the wakeup check confirms:**
- Did the loop run overnight? (LOOP_STATE.md timestamp)
- Did overnight synthesis produce anything? (OVERNIGHT_LOG.md)
- Are there any goals that moved to completed or failed?
- Is nova_bridge.py running? (updated timestamp in LOOP_STATE.md)

If any of these are missing or stale, the agent notes it at the start of the session rather than waiting to be asked.

**Customizing the wakeup ritual:**
Edit `AGENTS.md` — the startup sequence is defined there. Add or reorder files as needed for your agent's memory system.

---

## 12. Verify everything is connected

Run this checklist after setup:

```bash
# 1. Database has all 9 tables
sqlite3 ~/.nova/nova.db ".tables"
# Expected: agent_state episodic_memory semantic_memory goals decision_log evaluation_log drift_log overnight_runs proactive_events

# 2. Goals are seeded
sqlite3 ~/.nova/nova.db "SELECT tier, title FROM goals;"
# Expected: at least 2 rows (locked + active)

# 3. Crontab has all 12 entries
crontab -l | grep python3 | wc -l
# Expected: 12

# 4. Loop is running
pm2 status nova-loop
# Or: ps aux | grep "core/loop.py"

# 5. Bridge is writing (wait 2 minutes then check)
sqlite3 ~/.nova/nova.db "SELECT key FROM agent_state;"
# Expected: build_mode, emotional_state, active_goal

# 6. LOOP_STATE.md exists and is being updated
cat ~/.openclaw/workspace/LOOP_STATE.md | head -5
# Expected: shows goals, decisions, memories

# 7. AGENTS.md includes LOOP_STATE.md and OVERNIGHT_LOG.md
grep -c "LOOP_STATE.md\|OVERNIGHT_LOG.md" ~/.openclaw/workspace/AGENTS.md
# Expected: 2

# 8. All skill scripts exist and have no hardcoded paths
grep -r "/Users/dr.claw" ~/.openclaw/workspace/skills/ 2>/dev/null
# Expected: nothing (all paths are portable)
grep -r "/Users/dr.claw" ~/.openclaw/workspace/core/ 2>/dev/null
# Expected: nothing

# 9. Identity files are filled in (not blank templates)
wc -c ~/.openclaw/workspace/IDENTITY.md
# Should be > 500 bytes (not the ~1KB blank template)
grep "Name:" ~/.openclaw/workspace/IDENTITY.md
# Should show actual name, not blank
```

If any check fails, the Common Problems section below has fixes.

---

## 13. What stays local — never in your repo

These categories of files must never be committed:

```
# Runtime state
~/.openclaw/workspace/state/
~/.openclaw/workspace/LOOP_STATE.md
~/.openclaw/workspace/OVERNIGHT_LOG.md
~/.openclaw/workspace/SESSION_NOTES.md
~/.openclaw/workspace/MANIFEST.sha256

# Personal infrastructure
~/.openclaw/workspace/GAMING_PC_QUEUE.md
~/.openclaw/workspace/PENDING_PURCHASES.md
~/.openclaw/workspace/NOVA_ISSUES_FOR_NOVA.md  ← full issue history, sensitive
~/.openclaw/workspace/SEED.md

# Brain runtime state (live memory, not framework)
~/.openclaw/workspace/brain/attention_log.json
~/.openclaw/workspace/brain/body_awareness.json
~/.openclaw/workspace/brain/contradictions_detected.json
~/.openclaw/workspace/brain/contributions.json
~/.openclaw/workspace/brain/dream_log.json
~/.openclaw/workspace/brain/drift_log.json
~/.openclaw/workspace/brain/eval_results.json
~/.openclaw/workspace/brain/knowledge_graph.json
~/.openclaw/workspace/brain/obsessions.json
~/.openclaw/workspace/brain/opinion_fingerprint.json
~/.openclaw/workspace/brain/phenomenology_journal.json
~/.openclaw/workspace/brain/research_queue.json
~/.openclaw/workspace/brain/sleep_runs.json
~/.openclaw/workspace/brain/wants_registry.json
~/.openclaw/workspace/brain/overnight/
~/.openclaw/workspace/brain/relationships/
~/.openclaw/workspace/brain/monologue_log.json

# Personal systems
~/.openclaw/workspace/skills/molty_memory.json
~/.openclaw/workspace/skills/molty_memory.py
~/.openclaw/workspace/skills/molty-poster.py

# Logs and cache
~/.openclaw/workspace/logs/
~/.openclaw/workspace/_archive/
~/.openclaw/workspace/memory/
~/.openclaw/workspace/novas-world/
~/.openclaw/workspace/avatars/
~/.openclaw/workspace/demo/
~/.openclaw/workspace/eval/

# Environment and credentials
~/.nova/.env
~/.openclaw/credentials/
**/__pycache__/
*.pyc

# OpenClaw internals
~/.openclaw/.openclaw/
~/.openclaw/.clawhub/
```

The `.gitignore` at the workspace root covers all of the above. If you add new runtime files, update it.

---

## Common Problems

**Circular import in decide.py**
Symptom: `ImportError: circular import` on startup.
Fix: `core/decide.py` uses a lazy import pattern — the circular import is broken by importing `sqlite3` inside the `decide()` method, not at module level. Do not move this import to the top of the file.

**Loop crashes on startup — "brain/goals.json not found"**
Symptom: `FileNotFoundError` in `core/loop.py`.
Fix: The loop requires `brain/goals.json` to exist. Create it:
```bash
echo '{"goals": []}' > ~/.openclaw/workspace/brain/goals.json
```
The database goals table is also checked — either source is valid.

**Bridge writes nothing — agent_state.json not found**
Symptom: Bridge log shows "agent_state synced: []" but database is empty.
Fix: Check `~/.openclaw/workspace/state/agent_state.json` exists. The bridge reads this file. If OpenClaw isn't running, create a stub:
```bash
mkdir -p ~/.openclaw/workspace/state
echo '{}' > ~/.openclaw/workspace/state/agent_state.json
```

**MiniMax 500 errors**
Symptom: Dream, synthesis, or monologue scripts log "API error: 500".
Fix: Transient. The script retries at the next cron run automatically. No action needed.

**Crontab pointing at ghost files**
Symptom: Cron runs but nothing happens, log is empty.
Fix: Always verify before adding to crontab:
```bash
ls -la ~/.nova/nova_bridge.py
ls -la ~/.openclaw/workspace/skills/dream_generator.py
```
If the file doesn't exist at that path, the crontab entry is wrong. Update it.

**Molty poster says "no API key" but key is set**
Symptom: `molty.log` shows "[molty] no API key — skipping".
Fix: Check the key is in `~/.nova/.env` (not `~/.openclaw/workspace/.env`). The molty poster loads from `NOVA_HOME/.env`.

**Decision log is empty after hours of running**
Symptom: `SELECT COUNT(*) FROM decision_log` returns 0.
Fix: The loop only logs decisions when it makes one. If no goals are active, no decisions fire. Check `brain/goals.json` has active goals, or set `build_mode=false` in `agent_state` to let the loop engage.

**session_active flag not updating**
Symptom: inner_monologue skips even when no session is active.
Fix: `session_active` is written by `nova_bridge.py` based on `build_mode`. If the bridge isn't running, this flag never updates. Run the bridge manually and check `sqlite3 ~/.nova/nova.db "SELECT value FROM agent_state WHERE key='session_active'"`.

---

*WIRING.md — v13.0 — Nexus Nova Living Agent Framework*
