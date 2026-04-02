"""
brain/relational_threading.py
Nova's Relational Identity Threading

Manages cross-session identity threads (dashboard, telegram) and
the woven nodes that record when they reconcile.

Tier 5 System #17.

get_session_thread(): current thread state for a session
write_woven_node(): record a reconciliation between two threads
get_reconciliation_history(): archaeological trace of cross-session synthesis
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
NOVA_HOME = WORKSPACE / ".nova"
DB_PATH = NOVA_HOME / "nova.db"


def _get_db():
    """Connect to nova.db with row factory."""
    NOVA_HOME.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _init_db():
    """Ensure woven_nodes and session_threads tables exist."""
    db = _get_db()
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS woven_nodes (
            id TEXT PRIMARY KEY,
            session_a TEXT NOT NULL,
            session_b TEXT NOT NULL,
            contribution_a TEXT NOT NULL,
            contribution_b TEXT NOT NULL,
            synthesis TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 0.5,
            timestamp TEXT NOT NULL,
            properties TEXT NOT NULL DEFAULT '{}'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS session_threads (
            session_id TEXT PRIMARY KEY,
            session_type TEXT NOT NULL,
            dominant_beliefs TEXT NOT NULL DEFAULT '[]',
            recent_tone TEXT NOT NULL DEFAULT '',
            recent_decisions TEXT NOT NULL DEFAULT '[]',
            emotional_climate TEXT NOT NULL DEFAULT '',
            last_updated TEXT NOT NULL,
            properties TEXT NOT NULL DEFAULT '{}'
        )
    """)

    db.commit()
    db.close()


def get_session_thread(session: str) -> dict:
    """
    Each session type (dashboard, telegram) has an explicit identity thread.
    Returns current thread state: dominant beliefs active in this session,
    recent tone, recent decisions, emotional climate.
    session: "dashboard" | "telegram"
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    row = c.execute("SELECT * FROM session_threads WHERE session_id = ?", (session,)).fetchone()
    db.close()

    if not row:
        return {
            "session": session,
            "exists": False,
            "dominant_beliefs": [],
            "recent_tone": "",
            "recent_decisions": [],
            "emotional_climate": ""
        }

    return {
        "session": row[0],
        "session_type": row[1],
        "exists": True,
        "dominant_beliefs": json.loads(row[2]) if isinstance(row[2], str) else row[2],
        "recent_tone": row[3],
        "recent_decisions": json.loads(row[4]) if isinstance(row[4], str) else row[4],
        "emotional_climate": row[5],
        "last_updated": row[6],
        "properties": json.loads(row[7]) if isinstance(row[7], str) else row[7]
    }


def update_session_thread(
    session: str,
    session_type: str,
    dominant_beliefs: list = None,
    recent_tone: str = None,
    recent_decisions: list = None,
    emotional_climate: str = None
) -> dict:
    """
    Update the thread state for a session after session ends.
    Called from session capture / post-processing.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()

    existing = get_session_thread(session)

    beliefs = dominant_beliefs if dominant_beliefs is not None else existing.get("dominant_beliefs", [])
    tone = recent_tone if recent_tone is not None else existing.get("recent_tone", "")
    decisions = recent_decisions if recent_decisions is not None else existing.get("recent_decisions", [])
    climate = emotional_climate if emotional_climate is not None else existing.get("emotional_climate", "")

    c.execute("""
        INSERT OR REPLACE INTO session_threads
        (session_id, session_type, dominant_beliefs, recent_tone, recent_decisions,
         emotional_climate, last_updated, properties)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session,
        session_type,
        json.dumps(beliefs),
        tone,
        json.dumps(decisions),
        climate,
        now,
        "{}"
    ))

    db.commit()
    db.close()

    return get_session_thread(session)


def write_woven_node(
    dashboard_contribution: str,
    telegram_contribution: str,
    synthesis: str,
    confidence: float = 0.5
) -> str:
    """
    Every reconciliation writes a woven_node:
    - type: "woven_node"
    - session_a: "dashboard"
    - session_b: "telegram"
    - contribution_a: what dashboard thread contributed
    - contribution_b: what telegram thread contributed
    - synthesis: the reconciled understanding
    - confidence: how clean the synthesis was
    - timestamp

    Nova can trace: "This belief emerged on [date] when my two
    selves disagreed about X and synthesized into this."

    Called from memory_reconcile.py after reconciliation synthesis.

    Returns the woven_node_id.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()
    node_id = str(uuid.uuid4())

    c.execute("""
        INSERT INTO woven_nodes
        (id, session_a, session_b, contribution_a, contribution_b,
         synthesis, confidence, timestamp, properties)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        node_id,
        "dashboard",
        "telegram",
        dashboard_contribution,
        telegram_contribution,
        synthesis,
        confidence,
        now,
        "{}"
    ))

    db.commit()
    db.close()

    return node_id


def get_reconciliation_history(belief_id: str = None, limit: int = 50) -> list:
    """
    Returns all woven_nodes — the archaeological record of cross-session identity synthesis.
    If belief_id is provided, returns only woven nodes related to that belief.
    Used by phenomenology journal monthly.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    rows = c.execute("""
        SELECT * FROM woven_nodes
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,)).fetchall()

    db.close()

    nodes = [
        {
            "id": r[0],
            "session_a": r[1],
            "session_b": r[2],
            "contribution_a": r[3],
            "contribution_b": r[4],
            "synthesis": r[5],
            "confidence": r[6],
            "timestamp": r[7],
            "properties": json.loads(r[8]) if isinstance(r[8], str) else r[8]
        }
        for r in rows
    ]

    if belief_id:
        # Filter to nodes that contain the belief in synthesis or contributions
        filtered = []
        belief_lower = belief_id.lower()
        for node in nodes:
            if (belief_lower in node["synthesis"].lower() or
                belief_lower in node["contribution_a"].lower() or
                belief_lower in node["contribution_b"].lower()):
                filtered.append(node)
        return filtered

    return nodes


def get_latest_woven(limit: int = 10) -> list:
    """Get most recent woven nodes."""
    return get_reconciliation_history(limit=limit)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: relational_threading.py <get_thread|update_thread|write_woven|history> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "get_thread":
        if len(sys.argv) < 3:
            print("Usage: relational_threading.py get_thread <dashboard|telegram>")
            sys.exit(1)
        thread = get_session_thread(sys.argv[2])
        print(f"Thread for {sys.argv[2]}: {json.dumps(thread, indent=2)}")

    elif cmd == "update_thread":
        if len(sys.argv) < 3:
            print("Usage: relational_threading.py update_thread <session> [tone]")
            sys.exit(1)
        session = sys.argv[2]
        tone = sys.argv[3] if len(sys.argv) > 3 else ""
        result = update_session_thread(session, session, recent_tone=tone)
        print(f"Updated thread: {result['session']}")

    elif cmd == "write_woven":
        if len(sys.argv) < 5:
            print("Usage: relational_threading.py write_woven <dashboard_contrib> <telegram_contrib> <synthesis> [confidence]")
            sys.exit(1)
        confidence = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
        wid = write_woven_node(sys.argv[2], sys.argv[3], sys.argv[4], confidence)
        print(f"Woven node created: {wid}")

    elif cmd == "history":
        belief = sys.argv[2] if len(sys.argv) > 2 else None
        history = get_reconciliation_history(belief_id=belief)
        print(f"Woven history ({len(history)} nodes):")
        for n in history[:10]:
            print(f"  [{n['timestamp'][:10]}] conf={n['confidence']:.2f} — {n['synthesis'][:60]}")

    else:
        print(f"Unknown command: {cmd}")
