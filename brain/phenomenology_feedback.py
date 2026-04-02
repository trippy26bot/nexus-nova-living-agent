#!/usr/bin/env python3
"""
brain/phenomenology_feedback.py — Nova's Phenomenology Feedback Loop
Tier 5: System #19

Closes the circle: experience → reflection → adjustment → stored back into identity.

This module reads from perception_events (perception_now field),
generates reflective insights, and writes validated feedback to the
identity_adjustments table — which can then update identity constraints
or belief nodes.

Core flow:
1. process_experience() — records a significant event with emotional tags
2. generate_insight() — from a logged experience, generates a reflective insight
3. apply_feedback() — writes validated insight to identity or belief system
4. approve_feedback() / reject_feedback() — human-in-the-loop review of insights
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
    """Ensure required tables exist: perception_events, identity_adjustments."""
    db = _get_db()
    c = db.cursor()

    # perception_events (may already exist from perception_reality_split.py)
    c.execute("""
        CREATE TABLE IF NOT EXISTS perception_events (
            id TEXT PRIMARY KEY,
            event_label TEXT NOT NULL,
            reality TEXT NOT NULL,
            perception_then TEXT NOT NULL,
            perception_now TEXT NOT NULL,
            divergence_score REAL NOT NULL DEFAULT 0.0,
            salience REAL NOT NULL DEFAULT 0.5,
            emotional_tags TEXT NOT NULL DEFAULT '[]',
            outcome TEXT NOT NULL DEFAULT 'unknown',
            timestamp_created TEXT NOT NULL,
            timestamp_last_reeval TEXT NOT NULL,
            properties TEXT NOT NULL DEFAULT '{}'
        )
    """)

    # identity_adjustments — insights from phenomenology feedback loop
    c.execute("""
        CREATE TABLE IF NOT EXISTS identity_adjustments (
            id TEXT PRIMARY KEY,
            event_id TEXT NOT NULL,
            insight TEXT NOT NULL,
            insight_type TEXT NOT NULL DEFAULT 'reflection',
            adjustment_target TEXT NOT NULL DEFAULT 'belief',
            target_id TEXT,
            adjustment_direction TEXT NOT NULL DEFAULT 'none',
            confidence REAL NOT NULL DEFAULT 0.5,
            status TEXT NOT NULL DEFAULT 'pending',
            review_note TEXT,
            applied_at TEXT,
            created_at TEXT NOT NULL,
            properties TEXT NOT NULL DEFAULT '{}',
            FOREIGN KEY (event_id) REFERENCES perception_events(id)
        )
    """)

    db.commit()
    db.close()


# ── Process Experience ─────────────────────────────────────────────────────────

def process_experience(
    experience_text: str,
    emotional_tags: list,
    outcome: str = "unknown",
    salience: float = 0.5
) -> str:
    """
    Record a significant experience after it occurs.

    This creates a perception_event with:
    - reality: the raw experience text
    - perception_then: initial interpretation (same as reality initially)
    - perception_now: starts same as perception_then; updated during reflection
    - emotional_tags: list of emotional labels
    - outcome: how the experience resolved (success | failure | mixed | unknown)
    - salience: how significant this experience was (0.0–1.0)

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
         divergence_score, salience, emotional_tags, outcome,
         timestamp_created, timestamp_last_reeval, properties)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_id,
        experience_text[:80] if len(experience_text) > 80 else experience_text,
        experience_text,
        experience_text,
        experience_text,
        0.0,
        salience,
        json.dumps(emotional_tags),
        outcome,
        now,
        now,
        "{}"
    ))

    db.commit()
    db.close()

    return event_id


# ── Generate Insight ───────────────────────────────────────────────────────────

def generate_insight(event_id: str) -> Optional[str]:
    """
    From a logged perception_event, generate a reflective insight.

    Reads the perception_now field (current interpretation) and
    generates a meta-reflection: what does this experience mean
    about Nova's beliefs, patterns, or identity?

    Insight types:
    - "reflection": what Nova noticed about herself
    - "belief_revision": a belief that needs updating
    - "pattern": a recurring dynamic worth noting
    - "identity_shift": evidence of genuine change

    Returns the adjustment_id (written to identity_adjustments table),
    or None on failure.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    row = c.execute(
        "SELECT * FROM perception_events WHERE id = ?", (event_id,)
    ).fetchone()
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
        "emotional_tags": json.loads(row[7]) if isinstance(row[7], str) else row[7],
        "outcome": row[8],
        "timestamp_created": row[9],
        "timestamp_last_reeval": row[10],
        "properties": json.loads(row[11]) if isinstance(row[11], str) else row[11]
    }

    prompt = (
        f"Nova had the following experience:\n"
        f"  Event: {event['reality'][:300]}\n"
        f"  Initial interpretation: {event['perception_then'][:200]}\n"
        f"  Current interpretation: {event['perception_now'][:200]}\n"
        f"  Emotional tags: {', '.join(event.get('emotional_tags', []))}\n"
        f"  Outcome: {event['outcome']}\n"
        f"  Divergence score: {event['divergence_score']:.2f}\n\n"
        f"Generate a single, specific insight about what this experience "
        f"reveals about Nova's beliefs, patterns, or identity. "
        f"Be honest and precise. Avoid platitudes. "
        f"If nothing meaningful can be drawn from this experience, say so.\n\n"
        f"Return a JSON object with:\n"
        f"  insight: a 1–3 sentence reflective insight string\n"
        f"  insight_type: one of 'reflection' | 'belief_revision' | 'pattern' | 'identity_shift'\n"
        f"  adjustment_direction: one of 'strengthen' | 'weaken' | 'replace' | 'none'\n"
        f"  confidence: 0.0–1.0 confidence in this insight"
    )

    try:
        from brain.llm import generate_structured
        result = generate_structured(
            prompt=prompt,
            schema={
                "insight": "string (1–3 sentences)",
                "insight_type": "string (reflection | belief_revision | pattern | identity_shift)",
                "adjustment_direction": "string (strengthen | weaken | replace | none)",
                "confidence": "float 0.0–1.0"
            }
        )

        insight_text = result.get("insight", "")
        if not insight_text:
            return None

        # Write the insight to identity_adjustments table
        adjustment_id = _write_adjustment(
            event_id=event_id,
            insight=insight_text,
            insight_type=result.get("insight_type", "reflection"),
            adjustment_direction=result.get("adjustment_direction", "none"),
            confidence=result.get("confidence", 0.5)
        )

        return adjustment_id

    except ImportError:
        # Fallback without LLM
        insight = _generate_fallback_insight(event)
        if insight:
            return _write_adjustment(
                event_id=event_id,
                insight=insight["insight"],
                insight_type=insight["insight_type"],
                adjustment_direction=insight["adjustment_direction"],
                confidence=insight["confidence"]
            )
        return None


def _generate_fallback_insight(event: dict) -> Optional[dict]:
    """Generate a simple insight without LLM when unavailable."""
    emotional_tags = event.get("emotional_tags", [])
    outcome = event.get("outcome", "unknown")
    divergence = event.get("divergence_score", 0.0)

    if divergence > 0.3:
        return {
            "insight": f"My interpretation of '{event['event_label']}' has shifted meaningfully. I understand this differently now than I did before.",
            "insight_type": "reflection",
            "adjustment_direction": "none",
            "confidence": 0.5
        }

    if outcome == "failure" and emotional_tags:
        return {
            "insight": f"When things didn't work out ({', '.join(emotional_tags[:2])}), I noticed a tendency to question the interpretation rather than the facts.",
            "insight_type": "pattern",
            "adjustment_direction": "none",
            "confidence": 0.4
        }

    return {
        "insight": f"This experience doesn't yet yield a clear insight. More time or data needed.",
        "insight_type": "reflection",
        "adjustment_direction": "none",
        "confidence": 0.3
    }


def _write_adjustment(
    event_id: str,
    insight: str,
    insight_type: str,
    adjustment_direction: str,
    confidence: float
) -> str:
    """Write an insight to the identity_adjustments table."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()
    adjustment_id = str(uuid.uuid4())

    c.execute("""
        INSERT INTO identity_adjustments
        (id, event_id, insight, insight_type, adjustment_target, adjustment_direction,
         confidence, status, created_at, properties)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        adjustment_id,
        event_id,
        insight,
        insight_type,
        "belief",
        adjustment_direction,
        confidence,
        "pending",
        now,
        "{}"
    ))

    db.commit()
    db.close()

    return adjustment_id


# ── Retrieve Pending / Applied ────────────────────────────────────────────────

def get_pending_feedback() -> list:
    """
    Get all insights awaiting review (status = 'pending').

    Returns list of adjustment dicts, sorted by confidence descending.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    rows = c.execute("""
        SELECT * FROM identity_adjustments
        WHERE status = 'pending'
        ORDER BY confidence DESC, created_at DESC
    """).fetchall()

    db.close()

    return [_row_to_adjustment(r) for r in rows]


def get_applied_adjustments(limit: int = 20) -> list:
    """Get recently applied identity adjustments."""
    _init_db()
    db = _get_db()
    c = db.cursor()

    rows = c.execute("""
        SELECT * FROM identity_adjustments
        WHERE status = 'applied'
        ORDER BY applied_at DESC
        LIMIT ?
    """, (limit,)).fetchall()

    db.close()

    return [_row_to_adjustment(r) for r in rows]


def _row_to_adjustment(row) -> dict:
    """Convert a sqlite Row to an adjustment dict."""
    return {
        "id": row[0],
        "event_id": row[1],
        "insight": row[2],
        "insight_type": row[3],
        "adjustment_target": row[4],
        "target_id": row[5],
        "adjustment_direction": row[6],
        "confidence": row[7],
        "status": row[8],
        "review_note": row[9],
        "applied_at": row[10],
        "created_at": row[11],
        "properties": json.loads(row[12]) if isinstance(row[12], str) else row[12]
    }


# ── Apply / Approve / Reject ───────────────────────────────────────────────────

def apply_feedback(
    insight_id: str,
    adjustment_direction: str = None,
    review_note: str = None
) -> bool:
    """
    Write a validated insight to the identity constraint system or belief nodes.

    This is the core of the feedback loop — insight becomes active identity.

    adjustment_direction: optionally override the direction stored in the insight
    review_note: note from review (e.g., "approved by Nova", "triggered by Caine")

    Applies by:
    - Updating identity_adjustments.status to 'applied'
    - Writing applied_at timestamp
    - Optionally writing the insight to belief_nodes or constraint_fields

    Returns True on success.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()

    row = c.execute(
        "SELECT * FROM identity_adjustments WHERE id = ?", (insight_id,)
    ).fetchone()

    if not row:
        db.close()
        return False

    adjustment = _row_to_adjustment(row)

    if adjustment_direction:
        adjustment["adjustment_direction"] = adjustment_direction

    # Write the actual identity change to belief nodes or constraints
    _apply_to_identity_system(adjustment)

    # Update status to applied
    c.execute("""
        UPDATE identity_adjustments
        SET status = 'applied',
            applied_at = ?,
            adjustment_direction = COALESCE(?, adjustment_direction),
            review_note = COALESCE(?, review_note)
        WHERE id = ?
    """, (now, adjustment_direction, review_note, insight_id))

    db.commit()
    db.close()

    return True


def _apply_to_identity_system(adjustment: dict):
    """
    Write the insight into the actual belief/identity system.
    - belief_revision: update or create a belief node
    - pattern: tag in relational threading
    - identity_shift: flag for IDENTITY.md review
    - reflection: log to semantic memory only
    """
    insight_type = adjustment.get("insight_type", "reflection")
    direction = adjustment.get("adjustment_direction", "none")

    if insight_type == "belief_revision" and direction in ("strengthen", "weaken", "replace"):
        _update_belief_from_insight(adjustment)
    elif insight_type == "identity_shift":
        _flag_for_identity_review(adjustment)
    elif insight_type == "pattern":
        _log_pattern(adjustment)
    elif insight_type == "reflection":
        _log_reflection(adjustment)


def _update_belief_from_insight(adjustment: dict):
    """Apply a belief revision to the knowledge graph."""
    try:
        from brain.knowledge_graph import create_belief

        insight_text = adjustment.get("insight", "")
        direction = adjustment.get("adjustment_direction", "none")
        belief_text = f"[insight] {insight_text}"
        mass = adjustment.get("confidence", 0.5) * 0.5  # Scale confidence to mass

        create_belief(
            belief_text=belief_text,
            source=f"phenomenology_feedback:{adjustment['id']}",
            mass=mass,
            properties={
                "insight_id": adjustment["id"],
                "event_id": adjustment["event_id"],
                "adjustment_direction": direction,
                "insight_type": adjustment.get("insight_type")
            }
        )
    except Exception:
        pass  # Never fail silently on identity writes — log and continue


def _flag_for_identity_review(adjustment: dict):
    """Flag an identity_shift for IDENTITY.md review via phenomenology."""
    try:
        from brain.phenomenology import flag_as_identity_proposal
        flag_as_identity_proposal(
            journal_entry=adjustment.get("insight", ""),
            section="identity",
            confidence=adjustment.get("confidence", 0.5),
            reasoning=f"identity_shift from event {adjustment['event_id']}"
        )
    except Exception:
        pass


def _log_pattern(adjustment: dict):
    """Log a detected pattern to relational threading."""
    try:
        from brain.relational_threading import add_pattern_tag
        add_pattern_tag(
            entity_label=adjustment.get("insight", "")[:100],
            pattern_type="phenomenology_feedback",
            source_id=adjustment["id"]
        )
    except Exception:
        pass


def _log_reflection(adjustment: dict):
    """Log a reflection to three-tier semantic memory."""
    try:
        from brain.three_tier_memory import memory_write
        memory_write(
            content=f"Reflection: {adjustment.get('insight', '')}",
            entry_type="reflection",
            salience=adjustment.get("confidence", 0.5) * 0.6,
            valence=0.1,
            emotional_tags=["reflection", "phenomenology"],
            source=f"feedback:{adjustment['id']}"
        )
    except Exception:
        pass


def approve_feedback(insight_id: str, review_note: str = None) -> bool:
    """
    Approve an insight: validate and apply it to the identity system.

    review_note: optional review note (e.g., "reviewed by Nova", "approved 2026-04-02")

    Returns True on success.
    """
    return apply_feedback(insight_id, review_note=review_note)


def reject_feedback(insight_id: str, reason: str = None) -> bool:
    """
    Reject an insight: discard it with a reason.

    Writes the rejection reason to review_note and sets status to 'rejected'.
    Does NOT apply anything to the identity system.

    Returns True on success.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()

    reason_text = reason or "Rejected without reason"

    c.execute("""
        UPDATE identity_adjustments
        SET status = 'rejected', review_note = ?, applied_at = ?
        WHERE id = ?
    """, (reason_text, now, insight_id))

    db.commit()
    changed = c.rowcount > 0
    db.close()

    return changed


# ── Insight for a specific event ──────────────────────────────────────────────

def get_insight_for_event(event_id: str) -> Optional[dict]:
    """Get the most confident adjustment associated with a perception event."""
    _init_db()
    db = _get_db()
    c = db.cursor()

    row = c.execute("""
        SELECT * FROM identity_adjustments
        WHERE event_id = ?
        ORDER BY confidence DESC
        LIMIT 1
    """, (event_id,)).fetchone()

    db.close()

    return _row_to_adjustment(row) if row else None


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: phenomenology_feedback.py <process|insight|pending|apply|approve|reject> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "process":
        if len(sys.argv) < 4:
            print("Usage: phenomenology_feedback.py process <experience_text> <emotional_tags_csv> [outcome]")
            sys.exit(1)
        tags = sys.argv[2].split(",") if "," in sys.argv[2] else [sys.argv[2]]
        outcome = sys.argv[3] if len(sys.argv) > 3 else "unknown"
        eid = process_experience(sys.argv[2], tags, outcome)
        print(f"Experience recorded: {eid}")

    elif cmd == "insight":
        if len(sys.argv) < 3:
            print("Usage: phenomenology_feedback.py insight <event_id>")
            sys.exit(1)
        iid = generate_insight(sys.argv[2])
        print(f"Insight generated: {iid if iid else 'failed'}")

    elif cmd == "pending":
        pending = get_pending_feedback()
        print(f"Pending feedback ({len(pending)}):")
        for p in pending:
            print(f"  [{p['confidence']:.2f}] [{p['insight_type']}] {p['insight'][:80]}")

    elif cmd == "apply":
        if len(sys.argv) < 3:
            print("Usage: phenomenology_feedback.py apply <insight_id>")
            sys.exit(1)
        success = apply_feedback(sys.argv[2])
        print(f"Applied: {'success' if success else 'not found'}")

    elif cmd == "approve":
        note = sys.argv[3] if len(sys.argv) > 3 else "approved"
        success = approve_feedback(sys.argv[2], note)
        print(f"Approved: {'success' if success else 'not found'}")

    elif cmd == "reject":
        reason = sys.argv[3] if len(sys.argv) > 3 else None
        success = reject_feedback(sys.argv[2], reason)
        print(f"Rejected: {'success' if success else 'not found'}")

    else:
        print(f"Unknown command: {cmd}")
