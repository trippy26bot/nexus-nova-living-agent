#!/usr/bin/env python3
"""
demo/run_demo.py
Nexus Nova Living Agent — minimal demo
Shows real system state: memory, goals, drift, loop health.
Run this after completing WIRING.md setup to verify everything is connected.

Usage: python3 demo/run_demo.py
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

# Portable paths — matches WIRING.md setup
NOVA_HOME = Path(os.getenv("NOVA_HOME", os.path.expanduser("~/.nova")))
WORKSPACE = Path(os.getenv("NOVA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))
DB_PATH = NOVA_HOME / "nova.db"
LOOP_STATE = WORKSPACE / "LOOP_STATE.md"
OVERNIGHT_LOG = WORKSPACE / "OVERNIGHT_LOG.md"
DREAM_LOG = WORKSPACE / "brain" / "dream_log.json"
MONOLOGUE_LOG = WORKSPACE / "brain" / "monologue_log.json"


def section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def check_database():
    section("DATABASE")
    if not DB_PATH.exists():
        print("✗ nova.db not found — run WIRING.md Step 3 first")
        return False

    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row

    tables = [r[0] for r in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    print(f"✓ Tables: {len(tables)}/9 — {', '.join(tables)}")

    # Goals
    goals = db.execute(
        "SELECT title, tier, status FROM goals WHERE status != 'completed'"
    ).fetchall()
    print(f"\n Active goals ({len(goals)}):")
    for g in goals:
        print(f" [{g['tier'].upper()}] {g['title']}")

    # Episodic memory count
    mem_count = db.execute("SELECT count(*) FROM episodic_memory").fetchone()[0]
    print(f"\n Episodic memory: {mem_count} records")

    # Latest memories
    recent = db.execute("""
        SELECT content, source_event, importance, timestamp
        FROM episodic_memory
        ORDER BY timestamp DESC LIMIT 3
    """).fetchall()
    if recent:
        print(" Recent:")
        for r in recent:
            print(f" [{r['source_event']}] {r['content'][:80]}")

    # Drift status
    drift = db.execute(
        "SELECT composite, drift_content, timestamp FROM drift_log ORDER BY timestamp DESC LIMIT 1"
    ).fetchone()
    if drift:
        status = "STABLE" if drift["composite"] < 0.15 else "DRIFT" if drift["composite"] < 0.40 else "BREACH"
        print(f"\n Identity drift: {status} (composite={drift['composite']}) — {drift['timestamp'][:16]}")
    else:
        print("\n Identity drift: no data yet (run drift_detector.py)")

    db.close()
    return True


def check_loop():
    section("LOOP STATE")
    if not LOOP_STATE.exists():
        print("✗ LOOP_STATE.md not found — is nova_bridge.py running?")
        return

    content = LOOP_STATE.read_text()
    lines = [l for l in content.split("\n") if l.strip()]
    print(f"✓ LOOP_STATE.md exists ({len(lines)} lines)")

    # Show goals and decisions sections
    in_section = False
    for line in lines[:25]:
        if line.startswith("##"):
            in_section = True
        if in_section:
            print(f" {line}")


def check_overnight():
    section("OVERNIGHT PIPELINE")

    if OVERNIGHT_LOG.exists():
        size = OVERNIGHT_LOG.stat().st_size
        mtime = datetime.fromtimestamp(OVERNIGHT_LOG.stat().st_mtime)
        print(f"✓ OVERNIGHT_LOG.md — {size} bytes, last updated {mtime.strftime('%Y-%m-%d %H:%M')}")

        # Show last 20 lines
        content = OVERNIGHT_LOG.read_text()
        last_lines = content.strip().split("\n")[-20:]
        print(" Last entries:")
        for line in last_lines:
            if line.strip():
                print(f" {line}")
    else:
        print("✗ OVERNIGHT_LOG.md not found — overnight pipeline hasn't run yet")

    # Dream log
    if DREAM_LOG.exists():
        data = json.loads(DREAM_LOG.read_text())
        records = data.get("dream_records", [])
        print(f"\n Dream records: {len(records)}")
        if records:
            latest = records[-1]
            print(f" Latest dream ({latest.get('timestamp', '')[:16]}):")
            print(f" {latest.get('content', '')[:200]}...")
    else:
        print("\n Dream log: not yet generated (runs at 1am)")

    # Monologue log
    if MONOLOGUE_LOG.exists():
        data = json.loads(MONOLOGUE_LOG.read_text())
        records = data.get("monologue_records", [])
        print(f"\n Inner monologue records: {len(records)}")
        if records:
            latest = records[-1]
            print(f" Latest ({latest.get('timestamp', '')[:16]}):")
            print(f" {latest.get('content', '')[:200]}...")
    else:
        print("\n Monologue log: not yet generated (runs at 8am/12pm/4pm/8pm)")


def check_cron():
    section("CRON JOBS")
    import subprocess
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        jobs = [l for l in result.stdout.split("\n") if l.strip() and not l.startswith("#")]
        print(f"✓ {len(jobs)} active cron jobs")
        for job in jobs:
            print(f" {job[-80:]}")
    except Exception as e:
        print(f"✗ Could not read crontab: {e}")


def main():
    print(f"\nNexus Nova Living Agent — System Demo")
    print(f"{'='*60}")
    print(f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"DB: {DB_PATH}")
    print(f"Workspace: {WORKSPACE}")

    check_database()
    check_loop()
    check_overnight()
    check_cron()

    section("SUMMARY")
    print("This demo shows live system state.")
    print("For richer output, run after the overnight pipeline completes (after 6am).")
    print("See PROOF.md for captured real output examples.")
    print("See WIRING.md for full setup instructions.\n")


if __name__ == "__main__":
    main()
