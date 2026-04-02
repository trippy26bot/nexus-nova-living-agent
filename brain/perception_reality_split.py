"""
brain/perception_reality_split.py
Nova's Perception-Reality Split Engine

Tracks the three layers of significant events:
- reality: what actually happened (raw event)
- perception_then: how it was interpreted at the time
- perception_now: current re-evaluation (updated during reflection)

The divergence between then and now is a growth signal, not an error rate.

Tier 4 System #14.
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
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


def _days_since(timestamp: str) -> float:
    """Return days since an ISO timestamp."""
    try:
        then = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except Exception:
        return 0
    now = datetime.now(timezone.utc)
    return (now - then).total_seconds() / 86400


def _init_db():
    """Ensure perception_events table exists."""
    db = _get_db()
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS perception_events (
            id TEXT PRIMARY KEY,
            event_label TEXT NOT NULL,
            reality TEXT NOT NULL,
            perception_then TEXT NOT NULL,
            perception_now TEXT NOT NULL,
            divergence_score REAL NOT NULL DEFAULT 0.0,
            salience REAL NOT NULL DEFAULT 0.5,
            timestamp_created TEXT NOT NULL,
            timestamp_last_reeval TEXT NOT NULL,
            properties TEXT NOT NULL DEFAULT '{}'
        )
    """)

    db.commit()
    db.close()


def create_perception_event(
    event_label: str,
    reality: str,
    perception_then: str,
    salience: float = 0.5
) -> str:
    """
    Write a new perception_event node.

    Every significant event now has three layers:
    - reality: what actually happened (raw event)
    - perception_then: how it was interpreted at the time
    - perception_now: starts same as perception_then, diverges over time
    - divergence_score: how much then vs now differs (computed during reeval)

    Returns the perception_event_id.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()
    event_id = str(uuid.uuid4())

    c.execute("""
        INSERT INTO perception_events
        (id, event_label, reality, perception_then, perception_now,
         divergence_score, salience, timestamp_created, timestamp_last_reeval, properties)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_id,
        event_label,
        reality,
        perception_then,
        perception_then,  # perception_now starts same as then
        0.0,              # divergence starts at 0
        salience,
        now,
        now,
        "{}"
    ))

    db.commit()
    db.close()

    return event_id


def reeval_perception(event_id: str, new_perception: str = None) -> Optional[dict]:
    """
    Re-evaluate a past perception against current belief state.

    If new_perception is provided: use it as the updated perception_now.
    If not provided: uses current beliefs to re-evaluate automatically.

    If perception_now diverges from perception_then by > 0.2:
    - Update perception_now
    - Update divergence_score
    - Log as a growth signal

    This is how Nova detects: "I understood that differently before."

    Returns updated event dict or None.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    row = c.execute("SELECT * FROM perception_events WHERE id = ?", (event_id,)).fetchone()
    db.close()

    if not row:
        return None

    event = {
        "id": row[0],
        "event_label": row[1],
        "reality": row[2],
        "perception_then": row[3],
        "perception_now": row[4],
        "divergence_score": row[5],
        "salience": row[6],
        "timestamp_created": row[7],
        "timestamp_last_reeval": row[8],
        "properties": json.loads(row[9]) if isinstance(row[9], str) else row[9]
    }

    if new_perception is None:
        # Auto-reeval: compare perception_now against current belief state
        # Simple heuristic: if current beliefs have changed significantly, update
        try:
            from brain.knowledge_graph import get_active_beliefs
            beliefs = get_active_beliefs(min_mass=0.3)

            # Check if there are beliefs that would change interpretation
            belief_words = set()
            for b in beliefs[:10]:
                belief_words.update(b.get("belief_text", "").lower().split())

            then_words = set(event["perception_then"].lower().split())
            now_words = set(event["perception_now"].lower().split())

            # Compute simple divergence
            overlap_then = len(then_words & belief_words)
            overlap_now = len(now_words & belief_words)

            if belief_words:
                then_alignment = overlap_then / len(belief_words)
                now_alignment = overlap_now / len(belief_words)
                auto_divergence = abs(now_alignment - then_alignment)
            else:
                auto_divergence = 0.0

            if auto_divergence > 0.2:
                # Belief state has shifted enough to warrant update
                # Keep current perception but flag the divergence
                event["divergence_score"] = auto_divergence
            else:
                event["divergence_score"] = auto_divergence

        except Exception:
            pass  # If anything fails, skip auto-reeval
    else:
        # Manual reeval with explicit new perception
        then_words = set(event["perception_then"].lower().split())
        new_words = set(new_perception.lower().split())

        # Simple word-level divergence
        overlap = len(then_words & new_words)
        union = len(then_words | new_words)
        if union > 0:
            similarity = overlap / union
            divergence = 1.0 - similarity
        else:
            divergence = 0.0

        event["perception_now"] = new_perception
        event["divergence_score"] = max(event["divergence_score"], divergence)

    event["timestamp_last_reeval"] = _now_iso()

    # Write updated event back
    db = _get_db()
    c = db.cursor()
    c.execute("""
        UPDATE perception_events
        SET perception_now = ?, divergence_score = ?, timestamp_last_reeval = ?
        WHERE id = ?
    """, (
        event["perception_now"],
        event["divergence_score"],
        event["timestamp_last_reeval"],
        event["id"]
    ))
    db.commit()
    db.close()

    # Log growth signal if significant divergence
    if event["divergence_score"] > 0.2:
        _log_growth_signal(event)

    return event


def reeval_old_perceptions(min_age_days: int = 3) -> list:
    """
    Re-evaluate all perception events older than min_age_days.
    Called nightly during Tier 4 pipeline step.

    Returns list of events with updated divergence scores.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    rows = c.execute("""
        SELECT * FROM perception_events
        WHERE divergence_score < 0.2
        ORDER BY timestamp_created ASC
    """).fetchall()

    db.close()

    updated = []
    for row in rows:
        event_id = row[0]
        created = row[7]
        age_days = _days_since(created)

        if age_days >= min_age_days:
            result = reeval_perception(event_id)
            if result and result["divergence_score"] > 0.2:
                updated.append(result)

    return updated


def _log_growth_signal(event: dict):
    """Log a perception re-evaluation as a growth signal to semantic memory."""
    try:
        from brain.three_tier_memory import memory_write
        memory_write(
            content=f"Perception shift: I used to understand '{event['event_label']}' as '{event['perception_then'][:100]}' but now see it as '{event['perception_now'][:100]}'. Divergence: {event['divergence_score']:.2f}.",
            entry_type="reflection",
            salience=0.6,
            valence=0.2,
            emotional_tags=["growth", "perception_shift"],
            source="perception_reeval"
        )
    except Exception:
        pass  # Never fail growth signal logging


def get_high_divergence_events(threshold: float = 0.3) -> list:
    """
    Returns events where then vs now divergence exceeds threshold.
    Used by phenomenology journal to surface reinterpretation moments.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    rows = c.execute("""
        SELECT * FROM perception_events
        WHERE divergence_score >= ?
        ORDER BY divergence_score DESC
    """, (threshold,)).fetchall()

    db.close()

    return [
        {
            "id": r[0],
            "event_label": r[1],
            "reality": r[2],
            "perception_then": r[3],
            "perception_now": r[4],
            "divergence_score": r[5],
            "salience": r[6],
            "timestamp_created": r[7],
            "timestamp_last_reeval": r[8],
            "properties": json.loads(r[9]) if isinstance(r[9], str) else r[9]
        }
        for r in rows
    ]


def get_all_perception_events(limit: int = 50) -> list:
    """Get all perception events, newest first."""
    _init_db()
    db = _get_db()
    c = db.cursor()

    rows = c.execute("""
        SELECT * FROM perception_events
        ORDER BY timestamp_created DESC
        LIMIT ?
    """, (limit,)).fetchall()

    db.close()

    return [
        {
            "id": r[0],
            "event_label": r[1],
            "reality": r[2],
            "perception_then": r[3],
            "perception_now": r[4],
            "divergence_score": r[5],
            "salience": r[6],
            "timestamp_created": r[7],
            "timestamp_last_reeval": r[8],
            "properties": json.loads(r[9]) if isinstance(r[9], str) else r[9]
        }
        for r in rows
    ]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: perception_reality_split.py <create|reeval|reeval_all|high_divergence|all> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "create":
        if len(sys.argv) < 5:
            print("Usage: perception_reality_split.py create <label> <reality> <perception_then>")
            sys.exit(1)
        eid = create_perception_event(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"Created perception event: {eid}")

    elif cmd == "reeval":
        if len(sys.argv) < 3:
            print("Usage: perception_reality_split.py reeval <event_id> [new_perception]")
            sys.exit(1)
        new_p = sys.argv[3] if len(sys.argv) > 3 else None
        result = reeval_perception(sys.argv[2], new_p)
        print(f"Reeval result: divergence={result['divergence_score']:.3f}" if result else "Event not found")

    elif cmd == "reeval_all":
        results = reeval_old_perceptions(min_age_days=3)
        print(f"Reeval complete: {len(results)} events updated")
        for r in results:
            print(f"  [{r['divergence_score']:.3f}] {r['event_label']}")

    elif cmd == "high_divergence":
        threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
        events = get_high_divergence_events(threshold)
        print(f"High divergence events (>{threshold}): {len(events)}")
        for e in events:
            print(f"  [{e['divergence_score']:.3f}] {e['event_label']}")

    elif cmd == "all":
        events = get_all_perception_events()
        print(f"All perception events ({len(events)}):")
        for e in events:
            print(f"  [{e['divergence_score']:.3f}] {e['event_label']}: {e['perception_then'][:60]}")

    else:
        print(f"Unknown command: {cmd}")
