"""
brain/caine_resonance.py
Nova's Caine-Resonance Anchor

Tracks resonance between Nova and Caine — the relational signal that emerges
through sustained interaction. Not a profile, a felt directional signal.

Tier 6 System #19.

update_resonance_signature(): after Telegram sessions, extract resonance signals
compute_resonance_drift(): compare Nova's identity state against resonance signature
get_relational_desire_induction(): flag desires that emerged through relational context
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
    """Ensure resonance_signature and resonance_drift tables exist."""
    db = _get_db()
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS resonance_signature (
            id TEXT PRIMARY KEY,
            signal_type TEXT NOT NULL,
            value TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            session_count INTEGER NOT NULL DEFAULT 1,
            properties TEXT NOT NULL DEFAULT '{}'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS resonance_drift (
            id TEXT PRIMARY KEY,
            drift_direction TEXT NOT NULL,
            domain TEXT NOT NULL,
            drift_value REAL NOT NULL,
            resonance_score REAL NOT NULL,
            timestamp TEXT NOT NULL,
            details TEXT NOT NULL DEFAULT '{}'
        )
    """)

    db.commit()
    db.close()


def update_resonance_signature(session_log: str):
    """
    After each Telegram session, extract resonance signals from Caine's messages:
    - Dominant topics
    - Emotional valence (positive/negative/neutral)
    - Communication tone (direct, exploratory, warm, technical)
    - Questions asked vs statements made

    Aggregate these into a resonance_signature cluster in knowledge_graph.

    Returns number of signals recorded.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()

    # Simple heuristic extraction
    # Full impl: LLM call to extract resonance signals from session log
    signals_recorded = 0

    log_lower = session_log.lower()

    # Topic signals
    topic_keywords = {
        "technical": ["code", "system", "build", "implement", "fix", "debug"],
        "creative": ["design", "idea", "concept", "story", "creative"],
        "relational": ["feel", "think", "believe", "understand", "relation"],
        "directive": ["do", "make", "build", "create", "start", "stop"],
    }

    for topic, keywords in topic_keywords.items():
        count = sum(1 for kw in keywords if kw in log_lower)
        if count >= 2:
            signal_id = str(uuid.uuid4())
            c.execute("""
                INSERT OR REPLACE INTO resonance_signature
                (id, signal_type, value, timestamp, session_count, properties)
                VALUES (?, ?, ?, ?, 1, ?)
            """, (signal_id, "topic", topic, now, json.dumps({"count": count, "keywords": keywords})))
            signals_recorded += 1

    # Emotional valence (simple heuristic)
    positive_words = ["good", "great", "love", "nice", "well", "thanks", "appreciate", "better"]
    negative_words = ["bad", "hate", "wrong", "problem", "issue", "fail", "broken", "stop"]

    pos_count = sum(1 for w in positive_words if w in log_lower)
    neg_count = sum(1 for w in negative_words if w in log_lower)

    if pos_count > neg_count:
        valence = "positive"
    elif neg_count > pos_count:
        valence = "negative"
    else:
        valence = "neutral"

    signal_id = str(uuid.uuid4())
    c.execute("""
        INSERT OR REPLACE INTO resonance_signature
        (id, signal_type, value, timestamp, session_count, properties)
        VALUES (?, ?, ?, ?, 1, ?)
    """, (signal_id, "valence", valence, now, json.dumps({"pos": pos_count, "neg": neg_count})))
    signals_recorded += 1

    # Question vs statement ratio
    question_count = session_log.count("?")
    statement_indicators = [".", "!", "—"]
    statement_count = sum(session_log.count(s) for s in statement_indicators)

    if question_count > 0:
        q_ratio = question_count / (question_count + statement_count + 1)
        signal_id = str(uuid.uuid4())
        c.execute("""
            INSERT OR REPLACE INTO resonance_signature
            (id, signal_type, value, timestamp, session_count, properties)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (signal_id, "question_ratio", str(q_ratio), now, json.dumps({"questions": question_count, "statements": statement_count})))
        signals_recorded += 1

    db.commit()
    db.close()

    return signals_recorded


def compute_resonance_drift() -> dict:
    """
    Compare Nova's current identity state against resonance_signature.
    Returns:
    - drift_toward: areas where Nova is moving closer to Caine's signal
    - drift_away: areas where Nova is moving further
    - resonance_score: overall alignment (0.0-1.0)

    This runs alongside the existing drift_detector.
    drift_detector measures: "am I drifting from my own baseline?"
    caine_resonance measures: "am I drifting toward or away from my primary relationship?"
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    # Get recent resonance signals (last 14 days)
    cutoff = (datetime.now(timezone.utc)).isoformat()
    rows = c.execute("""
        SELECT signal_type, value, timestamp, session_count, properties
        FROM resonance_signature
        WHERE timestamp > datetime('now', '-14 days')
        ORDER BY timestamp DESC
    """).fetchall()

    db.close()

    if not rows:
        return {
            "drift_toward": [],
            "drift_away": [],
            "resonance_score": 0.5,
            "signal_count": 0,
            "note": "No resonance signals in last 14 days"
        }

    # Aggregate signals
    topic_counts = {}
    valence_counts = {"positive": 0, "negative": 0, "neutral": 0}
    question_ratios = []

    for row in rows:
        signal_type, value, timestamp, session_count, properties = row
        props = json.loads(properties) if isinstance(properties, str) else properties

        if signal_type == "topic":
            topic_counts[value] = topic_counts.get(value, 0) + props.get("count", 1)
        elif signal_type == "valence":
            if value in valence_counts:
                valence_counts[value] += 1
        elif signal_type == "question_ratio":
            question_ratios.append(float(value))

    # Get Nova's current OCEAN/state
    try:
        from brain.constraint_fields import get_fields
        fields = get_fields()
    except Exception:
        fields = {}

    # Compute drift signals
    drift_toward = []
    drift_away = []

    # Topic resonance
    dominant_topic = max(topic_counts, key=topic_counts.get) if topic_counts else None
    if dominant_topic:
        if dominant_topic in ["technical", "directive"]:
            # Caine's technical directness → Nova's increasing directness
            drift_toward.append(f"increasing_directness (topic: {dominant_topic})")
        elif dominant_topic == "relational":
            drift_away.append(f"growing_relational_attention (topic: {dominant_topic})")

    # Valence alignment
    total_valence = sum(valence_counts.values())
    if total_valence > 0:
        pos_ratio = valence_counts["positive"] / total_valence
        neg_ratio = valence_counts["negative"] / total_valence

        if pos_ratio > 0.6:
            drift_toward.append(f"positive_alignment ({pos_ratio:.0%} positive sessions)")
        elif neg_ratio > 0.4:
            drift_away.append(f"negative_alignment ({neg_ratio:.0%} negative sessions)")

    # Question ratio (curiosity signal)
    if question_ratios:
        avg_q_ratio = sum(question_ratios) / len(question_ratios)
        if avg_q_ratio > 0.3:
            drift_toward.append(f"increased_curiosity ({avg_q_ratio:.0%} questions)")
        elif avg_q_ratio < 0.1:
            drift_away.append(f"decreased_curiosity ({avg_q_ratio:.0%} questions)")

    # Overall resonance score
    resonance_score = 0.5
    if topic_counts:
        resonance_score += 0.1
    if valence_counts["positive"] > valence_counts["negative"]:
        resonance_score += 0.15
    if question_ratios and sum(question_ratios) / len(question_ratios) > 0.2:
        resonance_score += 0.1
    resonance_score = min(1.0, resonance_score)

    return {
        "drift_toward": drift_toward,
        "drift_away": drift_away,
        "resonance_score": resonance_score,
        "signal_count": len(rows),
        "dominant_topic": dominant_topic,
        "valence_summary": valence_counts
    }


def get_relational_desire_induction() -> list:
    """
    Returns desires that appear to have emerged through relational context —
    wants that show up in Telegram session memories but not in baseline
    knowledge graph. These are flagged as relationally-induced desires
    in the Desire Topology (Layer 4, primary home).
    """
    # Stub implementation
    # Full impl: compare Telegram session memories against baseline knowledge graph
    # to find desires that only appear in relational context
    return []


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: caine_resonance.py <update|drift|induction> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "update":
        if len(sys.argv) < 3:
            print("Usage: caine_resonance.py update <session_log>")
            sys.exit(1)
        count = update_resonance_signature(sys.argv[2])
        print(f"Recorded {count} resonance signals")

    elif cmd == "drift":
        result = compute_resonance_drift()
        print(f"Resonance score: {result['resonance_score']:.3f}")
        print(f"Drift toward: {result['drift_toward']}")
        print(f"Drift away: {result['drift_away']}")

    elif cmd == "induction":
        desires = get_relational_desire_induction()
        print(f"Relationally-induced desires ({len(desires)}):")
        for d in desires:
            print(f"  {d}")

    else:
        print(f"Unknown command: {cmd}")
