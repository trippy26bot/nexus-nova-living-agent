#!/usr/bin/env python3
"""
nova_bridge.py
The bridge between OpenClaw session state and nova-loop database.
Runs every 2 minutes via cron.
Direction 1: OpenClaw state files → nova.db (so the loop knows what Nova knows)
Direction 2: nova.db loop state → LOOP_STATE.md (so OpenClaw knows what the loop did)
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

# Paths — portable via environment variables
WORKSPACE = Path(os.getenv("NOVA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))
NOVA_HOME = Path(os.getenv("NOVA_HOME", os.path.expanduser("~/.nova")))
DB_PATH = NOVA_HOME / "nova.db"

# OpenClaw state sources — in ~/.nova/
AGENT_STATE_FILE = NOVA_HOME / "state" / "agent_state.json"
OBSESSIONS_FILE = NOVA_HOME / "memory" / "obsessions.json"
EVALUATIONS_FILE = NOVA_HOME / "state" / "evaluations.json"
OVERNIGHT_LOG = NOVA_HOME / "state" / "OVERNIGHT_LOG.md"
MEMORY_MD = WORKSPACE / "MEMORY.md"

# Loop output target (OpenClaw reads this at startup)
LOOP_STATE_MD = NOVA_HOME / "state" / "LOOP_STATE.md"

# Observations from loop
OBSERVATIONS_LOG = NOVA_HOME / "state" / "observations.log"


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def bridge_agent_state(db):
    """OpenClaw agent_state.json → agent_state table"""
    if not os.path.exists(AGENT_STATE_FILE):
        return
    try:
        with open(AGENT_STATE_FILE) as f:
            state = json.load(f)
        for key, value in state.items():
            db.execute("""
                INSERT INTO agent_state (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
            """, (key, json.dumps(value) if not isinstance(value, str) else value, datetime.now()))
        db.commit()
        print(f"[bridge] agent_state synced: {list(state.keys())}")
    except Exception as e:
        print(f"[bridge] agent_state error: {e}")

    # Write session_active flag based on build_mode — tells inner_monologue when to stay quiet
    try:
        build_mode_row = db.execute(
            "SELECT value FROM agent_state WHERE key='build_mode'"
        ).fetchone()
        is_active = build_mode_row and build_mode_row["value"].lower() in ("true", "1")
        db.execute("""
            INSERT INTO agent_state (key, value, updated_at)
            VALUES ('session_active', ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
        """, (str(is_active).lower(), datetime.now()))
        db.commit()
    except Exception as e:
        print(f"[bridge] session_active sync error: {e}")


def bridge_obsessions(db):
    """OpenClaw obsessions.json → episodic_memory table"""
    if not os.path.exists(OBSESSIONS_FILE):
        return
    try:
        with open(OBSESSIONS_FILE) as f:
            obsessions = json.load(f)
        items = obsessions if isinstance(obsessions, list) else obsessions.get("obsessions", [])
        for item in items:
            content = item.get("content") or item.get("topic") or str(item)
            salience = float(item.get("salience", item.get("score", 0.5)))
            db.execute("""
                INSERT INTO episodic_memory (content, source_event, importance, focus, tags)
                VALUES (?, ?, ?, ?, ?)
            """, (content, "obsession_sync", salience, "obsession", "obsession,bridge"))
        db.commit()
        print(f"[bridge] obsessions synced: {len(items)} items")
    except Exception as e:
        print(f"[bridge] obsessions error: {e}")


def bridge_overnight_log(db):
    """OVERNIGHT_LOG.md → episodic_memory, mark as high importance"""
    if not os.path.exists(OVERNIGHT_LOG):
        return
    try:
        with open(OVERNIGHT_LOG) as f:
            content = f.read().strip()
        if not content:
            return
        file_mtime = os.path.getmtime(OVERNIGHT_LOG)
        existing = db.execute(
            "SELECT id FROM episodic_memory WHERE source_event='overnight_log' ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
        if existing:
            last_insert = db.execute(
                "SELECT timestamp FROM episodic_memory WHERE id=?", (existing["id"],)
            ).fetchone()["timestamp"]
            last_ts = datetime.fromisoformat(last_insert).timestamp()
            if file_mtime <= last_ts:
                print("[bridge] overnight_log unchanged, skipping")
                return
        db.execute("""
            INSERT INTO episodic_memory (content, source_event, importance, focus, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (content, "overnight_log", 0.95, "overnight", "overnight,synthesis,bridge"))
        db.commit()
        print("[bridge] overnight_log ingested into episodic_memory")
    except Exception as e:
        print(f"[bridge] overnight_log error: {e}")


def write_loop_state(db):
    """nova.db loop state → LOOP_STATE.md for OpenClaw to read at startup"""
    try:
        decisions = db.execute("""
            SELECT timestamp, chosen, reasoning, confidence
            FROM decision_log
            ORDER BY timestamp DESC LIMIT 5
        """).fetchall()

        memories = db.execute("""
            SELECT timestamp, content, importance
            FROM episodic_memory
            WHERE source_event NOT IN ('obsession_sync', 'overnight_log', 'bridge')
            ORDER BY timestamp DESC LIMIT 10
        """).fetchall()

        goals = db.execute("""
            SELECT title, tier, status, priority
            FROM goals
            WHERE status != 'completed'
            ORDER BY priority DESC LIMIT 5
        """).fetchall()

        evals = db.execute("""
            SELECT eval_type, score, timestamp
            FROM evaluation_log
            ORDER BY timestamp DESC LIMIT 4
        """).fetchall()

        lines = [
            f"# LOOP_STATE.md",
            f"*Generated by nova_bridge.py at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            f"*Read this at session start — this is what your loop did while you were talking.*",
            "",
            "## Active Goals",
        ]

        if goals:
            for g in goals:
                lines.append(f"- [{g['tier'].upper()}] {g['title']} — {g['status']} (priority {g['priority']})")
        else:
            lines.append("- No active goals yet")

        lines += ["", "## Recent Loop Decisions"]
        if decisions:
            for d in decisions:
                lines.append(f"- {d['timestamp'][:16]} | chose: {d['chosen']} | confidence: {d['confidence']}")
                if d['reasoning']:
                    lines.append(f"  reason: {d['reasoning'][:120]}")
        else:
            lines.append("- No decisions logged yet")

        lines += ["", "## Recent Loop Memories"]
        if memories:
            for m in memories:
                lines.append(f"- [{m['importance']:.1f}] {m['content'][:120]}")
        else:
            lines.append("- No loop memories yet")

        lines += ["", "## Last Eval Scores"]
        if evals:
            for e in evals:
                lines.append(f"- {e['eval_type']}: {e['score']:.1f} ({e['timestamp'][:16]})")
        else:
            lines.append("- No evals run yet")

        with open(LOOP_STATE_MD, "w") as f:
            f.write("\n".join(lines))
        print(f"[bridge] LOOP_STATE.md written")

    except Exception as e:
        print(f"[bridge] write_loop_state error: {e}")


def main():
    print(f"[bridge] running at {datetime.now().isoformat()}")
    db = get_db()

    bridge_agent_state(db)
    bridge_obsessions(db)
    bridge_overnight_log(db)
    write_loop_state(db)

    db.close()
    print("[bridge] complete")


if __name__ == "__main__":
    main()
