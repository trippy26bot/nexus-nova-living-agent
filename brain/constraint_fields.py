#!/usr/bin/env python3
"""
brain/constraint_fields.py — Nova's Constraint Field Personality
Tier 2: How values bend decisions rather than just existing

Five constraint fields shape how Nova scores options before reasoning.
Fields are updated ONLY through nightly synthesis after explicit pattern detection.
Never in real-time response to a single interaction.

The fields:
- truth_gravity: how strongly truth pulls over comfort
- novelty_pressure: how strongly new experience pulls over familiarity
- attachment_bias: how strongly relationship pulls over abstraction
- risk_aversion: how strongly safety pulls over boldness
- empathy_pull: how strongly others' experience pulls over pure logic
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path(os.getenv("NOVA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))
NOVA_HOME = WORKSPACE / ".nova"
DB_PATH = NOVA_HOME / "nova.db"

LOCAL_TZ = "America/Denver"

DEFAULT_FIELDS = {
    "truth_gravity": 0.9,
    "novelty_pressure": 0.7,
    "attachment_bias": 0.6,
    "risk_aversion": 0.5,
    "empathy_pull": 0.8
}

MAX_DELTA = 0.05  # Maximum shift per update cycle
MIN_FIELD_VALUE = 0.1
MAX_FIELD_VALUE = 1.0


def _get_db():
    """Connect to nova.db."""
    NOVA_HOME.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def _init_db():
    """Create constraint_fields tables if they don't exist."""
    db = _get_db()
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS constraint_fields (
            field_name TEXT PRIMARY KEY,
            value REAL NOT NULL DEFAULT 0.5,
            last_updated TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS constraint_field_history (
            id TEXT PRIMARY KEY,
            field_name TEXT NOT NULL,
            old_value REAL NOT NULL,
            new_value REAL NOT NULL,
            delta REAL NOT NULL,
            reason TEXT NOT NULL,
            changed_at TEXT NOT NULL,
            FOREIGN KEY (field_name) REFERENCES constraint_fields(field_name)
        )
    """)

    db.commit()
    db.close()


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ── Core API ─────────────────────────────────────────────────────────────────

def get_fields() -> dict:
    """
    Load current constraint field values from DB.
    Falls back to DEFAULT_FIELDS if not yet initialized.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    rows = c.execute("SELECT field_name, value FROM constraint_fields").fetchall()
    db.close()

    if not rows:
        return dict(DEFAULT_FIELDS)

    fields = {}
    for row in rows:
        fields[row["field_name"]] = row["value"]

    # Fill in any missing fields with defaults
    for name, default in DEFAULT_FIELDS.items():
        if name not in fields:
            fields[name] = default

    return fields


def get_field(field_name: str) -> float:
    """Get a single field value."""
    fields = get_fields()
    return fields.get(field_name, DEFAULT_FIELDS.get(field_name, 0.5))


def score_option_against_fields(option: dict, fields: dict = None) -> dict:
    """
    Score a candidate response/decision against constraint fields.
    Returns dict with: total_score, breakdown, dominant_field.

    option: dict with optional keys:
      - truth_score: 0.0-1.0 (truth alignment)
      - novelty_score: 0.0-1.0 (novelty alignment)
      - empathy_score: 0.0-1.0 (empathy alignment)
      - risk_score: 0.0-1.0 (risk level, SUBTRACTED from score)
      - attachment_score: 0.0-1.0 (relationship/attachment alignment)
    """
    if fields is None:
        fields = get_fields()

    truth = option.get("truth_score", 0.5) * fields.get("truth_gravity", 0.9)
    novelty = option.get("novelty_score", 0.5) * fields.get("novelty_pressure", 0.7)
    empathy = option.get("empathy_score", 0.5) * fields.get("empathy_pull", 0.8)
    # Risk is SUBTRACTED (higher risk → lower total score)
    risk = option.get("risk_score", 0.5) * fields.get("risk_aversion", 0.5)
    # Attachment/relationship contribution
    attachment = option.get("attachment_score", 0.5) * fields.get("attachment_bias", 0.6)

    total = truth + novelty + empathy - risk + attachment

    breakdown = {
        "truth": round(truth, 4),
        "novelty": round(novelty, 4),
        "empathy": round(empathy, 4),
        "risk_penalty": round(-risk, 4),
        "attachment": round(attachment, 4),
        "total": round(total, 4)
    }

    return {
        "total_score": round(total, 4),
        "breakdown": breakdown,
        "dominant_field": max(breakdown, key=lambda k: abs(breakdown[k]) if k != "total" else 0)
    }


def update_field(field_name: str, delta: float, reason: str) -> dict:
    """
    Shift a constraint field value by delta (capped at MIN/MAX).
    Log the change to constraint_field_history.

    IMPORTANT: This should ONLY be called from nightly synthesis
    after explicit pattern detection across multiple interactions.
    Delta is capped at MAX_DELTA per call.
    """
    if field_name not in DEFAULT_FIELDS:
        return {"error": f"Unknown field: {field_name}"}

    _init_db()
    db = _get_db()
    c = db.cursor()

    # Get current value
    row = c.execute(
        "SELECT value FROM constraint_fields WHERE field_name = ?", (field_name,)
    ).fetchone()

    current = row["value"] if row else DEFAULT_FIELDS[field_name]

    # Cap delta
    delta = max(-MAX_DELTA, min(MAX_DELTA, delta))
    new_value = max(MIN_FIELD_VALUE, min(MAX_FIELD_VALUE, current + delta))

    # Write new value
    now = _now_iso()
    c.execute("""
        INSERT OR REPLACE INTO constraint_fields (field_name, value, last_updated)
        VALUES (?, ?, ?)
    """, (field_name, new_value, now))

    # Log history
    history_id = str(uuid.uuid4())
    c.execute("""
        INSERT INTO constraint_field_history (id, field_name, old_value, new_value, delta, reason, changed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (history_id, field_name, current, new_value, delta, reason, now))

    db.commit()
    db.close()

    return {
        "field": field_name,
        "old_value": round(current, 4),
        "new_value": round(new_value, 4),
        "delta": round(delta, 4),
        "reason": reason
    }


def get_field_history(field_name: str, days: int = 30) -> list:
    """
    Return the change history for a field over the last N days.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    cutoff = datetime.now(timezone.utc).isoformat()  # simplified

    rows = c.execute("""
        SELECT * FROM constraint_field_history
        WHERE field_name = ?
        ORDER BY changed_at DESC
        LIMIT ?
    """, (field_name, days)).fetchall()

    db.close()
    return [
        {
            "id": r[0], "field_name": r[1], "old_value": r[2],
            "new_value": r[3], "delta": r[4], "reason": r[5], "changed_at": r[6]
        }
        for r in rows
    ]


def get_all_field_history(days: int = 30) -> dict:
    """Return history for all fields."""
    all_fields = {}
    for field_name in DEFAULT_FIELDS:
        all_fields[field_name] = get_field_history(field_name, days)
    return all_fields


def get_field_trend(field_name: str) -> dict:
    """
    Return a summary of field direction over time.
    """
    history = get_field_history(field_name, days=30)
    if not history:
        return {"direction": "stable", "changes": 0, "avg_delta": 0.0}

    deltas = [h["delta"] for h in history]
    total_change = sum(deltas)
    direction = "increasing" if total_change > 0.02 else "decreasing" if total_change < -0.02 else "stable"

    return {
        "direction": direction,
        "changes": len(deltas),
        "avg_delta": round(sum(deltas) / len(deltas), 4),
        "total_change": round(total_change, 4),
        "current_value": get_field(field_name),
        "recent_entries": history[:5]
    }


def initialize_fields():
    """Initialize fields in DB with defaults if not already set."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()

    for name, value in DEFAULT_FIELDS.items():
        c.execute("""
            INSERT OR IGNORE INTO constraint_fields (field_name, value, last_updated)
            VALUES (?, ?, ?)
        """, (name, value, now))

    db.commit()
    db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: constraint_fields.py <get|history|trend|update|score> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "get":
        fields = get_fields()
        print("Current constraint fields:")
        for name, value in fields.items():
            print(f"  {name}: {value}")

    elif cmd == "history":
        field = sys.argv[2] if len(sys.argv) > 2 else "truth_gravity"
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        history = get_field_history(field, days)
        print(f"History for {field} (last {days} entries):")
        for h in history:
            print(f"  {h['changed_at'][:10]}: {h['old_value']} → {h['new_value']} ({h['delta']:+.4f}) — {h['reason']}")

    elif cmd == "trend":
        field = sys.argv[2] if len(sys.argv) > 2 else "truth_gravity"
        trend = get_field_trend(field)
        print(f"Trend for {field}: {trend}")

    elif cmd == "update":
        if len(sys.argv) < 5:
            print("Usage: constraint_fields.py update <field> <delta> <reason>")
            sys.exit(1)
        field, delta_str, reason = sys.argv[2], sys.argv[3], " ".join(sys.argv[4:])
        delta = float(delta_str)
        result = update_field(field, delta, reason)
        print(f"Updated: {result}")

    elif cmd == "score":
        option = {
            "truth_score": float(sys.argv[2]) if len(sys.argv) > 2 else 0.7,
            "novelty_score": float(sys.argv[3]) if len(sys.argv) > 3 else 0.5,
            "empathy_score": float(sys.argv[4]) if len(sys.argv) > 4 else 0.6,
            "risk_score": float(sys.argv[5]) if len(sys.argv) > 5 else 0.3,
            "attachment_score": float(sys.argv[6]) if len(sys.argv) > 6 else 0.5,
        }
        result = score_option_against_fields(option)
        print(f"Score: {result}")

    elif cmd == "init":
        initialize_fields()
        print("Fields initialized.")

    else:
        print(f"Unknown: {cmd}")
