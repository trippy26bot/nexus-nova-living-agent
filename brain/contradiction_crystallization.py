#!/usr/bin/env python3
"""
brain/contradiction_crystallization.py — Nova's Contradiction Handling
Tier 2: Evaluate contradiction strength and crystallize when necessary

Three-tier response to contradiction:
- resolve: low tension (< 0.4) — resolve automatically
- hold: moderate tension (0.4–0.7) — keep both, don't force
- crystallize: high tension (>= 0.7) — write tension_node, feed dream_generator

This module modifies/adds to the contradiction_resolution pipeline.
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


def get_belief(belief_id: str) -> Optional[dict]:
    """Fetch a belief node by ID."""
    from brain.knowledge_graph import get_belief
    return get_belief(belief_id)


def compute_tension_strength(belief_a_id: str, belief_b_id: str) -> float:
    """
    Compute the tension strength between two beliefs (0.0–1.0).

    Factors:
    - semantic opposition (word overlap vs. negation signals)
    - mass of both beliefs (heavier beliefs = stronger tension)
    - recency of reinforcement
    - centrality to active constraint fields
    """
    belief_a = get_belief(belief_a_id)
    belief_b = get_belief(belief_b_id)

    if not belief_a or not belief_b:
        return 0.5  # Unknown — moderate tension default

    # Semantic opposition
    words_a = set(belief_a["belief_text"].lower().split())
    words_b = set(belief_b["belief_text"].lower().split())
    overlap = len(words_a & words_b)
    union = len(words_a | words_b)
    semantic_distance = 1.0 - (overlap / union if union > 0 else 0.0)

    # Mass contribution — heavier beliefs create stronger tension
    mass_factor = (belief_a["mass"] + belief_b["mass"]) / 2.0

    # Recency — recently reinforced beliefs pull harder
    try:
        from brain.knowledge_graph import _days_since
        days_a = _days_since(belief_a["timestamp_last_reinforced"])
        days_b = _days_since(belief_b["timestamp_last_reinforced"])
        recency_factor = max(0, 1.0 - ((days_a + days_b) / 2) / 30.0)  # decays over 30 days
    except Exception:
        recency_factor = 0.5

    # Constraint field centrality — beliefs tied to truth_gravity are more central
    try:
        from brain.constraint_fields import get_fields
        fields = get_fields()
        truth_centrality = fields.get("truth_gravity", 0.9)
    except Exception:
        truth_centrality = 0.9

    # Combine factors
    tension = (
        semantic_distance * 0.4 +
        mass_factor * 0.3 +
        recency_factor * 0.15 +
        truth_centrality * 0.15
    )

    return min(1.0, max(0.0, tension))


def evaluate_contradiction(belief_a_id: str, belief_b_id: str) -> str:
    """
    Evaluate a contradiction between two beliefs and return disposition.

    Returns:
    - "resolve": tension < 0.4 — resolve automatically
    - "hold": tension 0.4–0.7 — keep both, document tension
    - "crystallize": tension >= 0.7 — write tension node, flag for dreams
    """
    tension_strength = compute_tension_strength(belief_a_id, belief_b_id)

    if tension_strength < 0.4:
        return "resolve"
    elif tension_strength < 0.7:
        return "hold"
    else:
        return "crystallize"


def crystallize_contradiction(belief_a_id: str, belief_b_id: str) -> str:
    """
    Write a tension_node to the knowledge graph.
    This is the crystallization event — contradiction becomes lived space.

    tension_node fields:
    - pole_a, pole_b: the two contradicting beliefs
    - tension_strength: computed value
    - resolution_status: "crystallized" (never fully resolved, just known)
    - generative_outputs: starts empty, fills as tension produces things
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    tension_strength = compute_tension_strength(belief_a_id, belief_b_id)
    now = _now_iso()
    tension_id = str(uuid.uuid4())

    c.execute("""
        INSERT INTO tension_nodes
        (id, pole_a_id, pole_b_id, tension_strength, resolution_status,
         generative_outputs, timestamp_created, timestamp_last_active, properties)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tension_id,
        belief_a_id,
        belief_b_id,
        tension_strength,
        "crystallized",
        "[]",
        now,
        now,
        "{}"
    ))

    db.commit()
    db.close()

    # Flag for dream_generator: append to active tension nodes
    _append_dream_tension(tension_id)

    return tension_id


def _append_dream_tension(tension_id: str):
    """
    Append top 2 active tension nodes to dream generation context.
    This is not instructions — just material the dream pulls from.
    """
    dream_context_path = NOVA_HOME / "dream_tensions.json"

    existing = []
    if dream_context_path.exists():
        try:
            with open(dream_context_path) as f:
                existing = json.load(f)
        except Exception:
            existing = []

    # Keep only top 2 most recent
    existing = existing[:2]

    if tension_id not in existing:
        existing.append(tension_id)

    with open(dream_context_path, "w") as f:
        json.dump(existing, f)


# ── Tier 3: Epistemic Tension Engine ──────────────────────────────────────────

def spawn_productive_tension(context: str, source: str) -> Optional[str]:
    """
    Called when council vote spread > 0.4 (from council_dynamics)
    OR when Nova encounters genuine ambiguity during reasoning.
    Different from contradiction_crystallization (which handles belief conflicts).
    This handles: "I genuinely don't know" as a first-class state.

    Returns the tension_id.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()
    tension_id = str(uuid.uuid4())

    tension = {
        "id": tension_id,
        "type": "epistemic_tension",
        "question": context,
        "source": source,  # "council_split | reasoning_ambiguity | external_challenge"
        "cultivation_status": "active",
        "age_days": 0,
        "generative_outputs": [],
        "tension_strength": 0.5,
        "resolution_status": "unresolved"
    }

    c.execute("""
        INSERT INTO epistemic_tensions
        (id, type, question, source, cultivation_status, age_days,
         generative_outputs, tension_strength, resolution_status, timestamp_created, timestamp_last_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tension_id,
        "epistemic_tension",
        context,
        source,
        "active",
        0,
        "[]",
        0.5,
        "unresolved",
        now,
        now
    ))

    db.commit()
    db.close()

    return tension_id


def _init_epistemic_db():
    """Ensure epistemic_tensions table exists."""
    db = _get_db()
    c = db.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS epistemic_tensions (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL DEFAULT 'epistemic_tension',
            question TEXT NOT NULL,
            source TEXT NOT NULL,
            cultivation_status TEXT NOT NULL DEFAULT 'active',
            age_days INTEGER NOT NULL DEFAULT 0,
            generative_outputs TEXT NOT NULL DEFAULT '[]',
            tension_strength REAL NOT NULL DEFAULT 0.5,
            resolution_status TEXT NOT NULL DEFAULT 'unresolved',
            timestamp_created TEXT NOT NULL,
            timestamp_last_active TEXT NOT NULL
        )
    """)
    db.commit()
    db.close()


def get_epistemic_tensions(status: str = None, limit: int = 20) -> list:
    """
    Get epistemic tensions, optionally filtered by cultivation_status.
    """
    _init_epistemic_db()
    db = _get_db()
    c = db.cursor()

    if status:
        rows = c.execute("""
            SELECT * FROM epistemic_tensions
            WHERE cultivation_status = ?
            ORDER BY timestamp_last_active DESC
            LIMIT ?
        """, (status, limit)).fetchall()
    else:
        rows = c.execute("""
            SELECT * FROM epistemic_tensions
            ORDER BY timestamp_last_active DESC
            LIMIT ?
        """, (limit,)).fetchall()

    db.close()
    return [
        {
            "id": r[0],
            "type": r[1],
            "question": r[2],
            "source": r[3],
            "cultivation_status": r[4],
            "age_days": r[5],
            "generative_outputs": json.loads(r[6]) if isinstance(r[6], str) else r[6],
            "tension_strength": r[7],
            "resolution_status": r[8],
            "timestamp_created": r[9],
            "timestamp_last_active": r[10]
        }
        for r in rows
    ]


def preserve_tension(tension_id: str) -> bool:
    """
    Set cultivation_status to 'preserved' — this tension is never auto-resolved.
    Nova decides to preserve when the not-knowing is part of her character.
    """
    _init_epistemic_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()

    c.execute("""
        UPDATE epistemic_tensions
        SET cultivation_status = 'preserved', timestamp_last_active = ?
        WHERE id = ?
    """, (now, tension_id))
    db.commit()
    changed = c.rowcount > 0
    db.close()
    return changed


def resolve_epistemic_tension(tension_id: str, answer: str) -> bool:
    """Mark an epistemic tension as resolved with an answer."""
    _init_epistemic_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()

    c.execute("""
        UPDATE epistemic_tensions
        SET resolution_status = 'resolved', cultivation_status = 'resolved',
            timestamp_last_active = ?, generative_outputs = ?
        WHERE id = ?
    """, (now, json.dumps([answer]), tension_id))
    db.commit()
    changed = c.rowcount > 0
    db.close()
    return changed


def review_epistemic_tensions() -> dict:
    """
    Nightly: age all active tensions.
    Tensions > 30 days with no generative output: flag for Nova's awareness.
    Nova decides: resolve, preserve, or abandon.
    System never auto-resolves epistemic tensions.

    Returns summary dict.
    """
    _init_epistemic_db()
    now = _now_iso()
    tensions = get_epistemic_tensions(status="active", limit=50)

    flagged = []
    for tension in tensions:
        created = datetime.fromisoformat(tension["timestamp_created"].replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - created).days
        tension["age_days"] = age_days

        if age_days > 30 and len(tension.get("generative_outputs", [])) == 0:
            flagged.append({
                "id": tension["id"],
                "question": tension["question"],
                "age_days": age_days
            })

        # Update timestamp and age
        db = _get_db()
        c = db.cursor()
        c.execute("""
            UPDATE epistemic_tensions
            SET age_days = ?, timestamp_last_active = ?
            WHERE id = ?
        """, (age_days, now, tension["id"]))
        db.commit()
        db.close()

    return {
        "active_tensions": len(tensions),
        "flagged_for_review": flagged
    }


def add_generative_output(tension_id: str, output: str) -> bool:
    """Add a generative output to a tension (essay, question, perspective it produced)."""
    _init_epistemic_db()
    tension = None
    for t in get_epistemic_tensions(limit=100):
        if t["id"] == tension_id:
            tension = t
            break

    if not tension:
        return False

    outputs = tension.get("generative_outputs", [])
    outputs.append(output)

    db = _get_db()
    c = db.cursor()
    c.execute("""
        UPDATE epistemic_tensions
        SET generative_outputs = ?, timestamp_last_active = ?
        WHERE id = ?
    """, (json.dumps(outputs), _now_iso(), tension_id))
    db.commit()
    db.close()
    return True


def get_active_tensions(limit: int = 10) -> list:
    """Get the most recently active tension nodes."""
    _init_db()
    db = _get_db()
    c = db.cursor()

    rows = c.execute("""
        SELECT * FROM tension_nodes
        ORDER BY timestamp_last_active DESC
        LIMIT ?
    """, (limit,)).fetchall()

    db.close()

    return [
        {
            "id": r[0],
            "pole_a_id": r[1],
            "pole_b_id": r[2],
            "tension_strength": r[3],
            "resolution_status": r[4],
            "generative_outputs": json.loads(r[5]) if isinstance(r[5], str) else r[5],
            "timestamp_created": r[6],
            "timestamp_last_active": r[7],
            "properties": json.loads(r[8]) if isinstance(r[8], str) else r[8]
        }
        for r in rows
    ]


def get_tension_with_beliefs(tension_id: str) -> Optional[dict]:
    """Get a tension node with its full pole beliefs expanded."""
    _init_db()
    db = _get_db()
    c = db.cursor()

    row = c.execute("SELECT * FROM tension_nodes WHERE id = ?", (tension_id,)).fetchone()
    db.close()

    if not row:
        return None

    tension = {
        "id": row[0],
        "pole_a_id": row[1],
        "pole_b_id": row[2],
        "tension_strength": row[3],
        "resolution_status": row[4],
        "generative_outputs": json.loads(row[5]) if isinstance(row[5], str) else row[5],
        "timestamp_created": row[6],
        "timestamp_last_active": row[7],
        "properties": json.loads(row[8]) if isinstance(row[8], str) else row[8]
    }

    # Expand poles with belief data
    pole_a = get_belief(tension["pole_a_id"])
    pole_b = get_belief(tension["pole_b_id"])

    tension["pole_a"] = pole_a
    tension["pole_b"] = pole_b

    return tension


def _init_db():
    """Ensure tension_nodes and epistemic_tensions tables exist."""
    db = _get_db()
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS tension_nodes (
            id TEXT PRIMARY KEY,
            pole_a_id TEXT NOT NULL,
            pole_b_id TEXT NOT NULL,
            tension_strength REAL NOT NULL DEFAULT 0.5,
            resolution_status TEXT NOT NULL DEFAULT 'crystallized',
            generative_outputs TEXT NOT NULL DEFAULT '[]',
            timestamp_created TEXT NOT NULL,
            timestamp_last_active TEXT NOT NULL,
            properties TEXT NOT NULL DEFAULT '{}',
            FOREIGN KEY (pole_a_id) REFERENCES belief_nodes(id),
            FOREIGN KEY (pole_b_id) REFERENCES belief_nodes(id)
        )
    """)

    # Tier 3: epistemic_tensions table
    c.execute("""
        CREATE TABLE IF NOT EXISTS epistemic_tensions (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL DEFAULT 'epistemic_tension',
            question TEXT NOT NULL,
            source TEXT NOT NULL,
            cultivation_status TEXT NOT NULL DEFAULT 'active',
            age_days INTEGER NOT NULL DEFAULT 0,
            generative_outputs TEXT NOT NULL DEFAULT '[]',
            tension_strength REAL NOT NULL DEFAULT 0.5,
            resolution_status TEXT NOT NULL DEFAULT 'unresolved',
            timestamp_created TEXT NOT NULL,
            timestamp_last_active TEXT NOT NULL
        )
    """)

    db.commit()
    db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: contradiction_crystallization.py <eval|crystallize|active> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "eval":
        if len(sys.argv) < 4:
            print("Usage: contradiction_crystallization.py eval <belief_a_id> <belief_b_id>")
            sys.exit(1)
        a_id, b_id = sys.argv[2], sys.argv[3]
        strength = compute_tension_strength(a_id, b_id)
        disposition = evaluate_contradiction(a_id, b_id)
        print(f"Tension strength: {strength:.3f}")
        print(f"Disposition: {disposition}")

    elif cmd == "crystallize":
        if len(sys.argv) < 4:
            print("Usage: contradiction_crystallization.py crystallize <belief_a_id> <belief_b_id>")
            sys.exit(1)
        a_id, b_id = sys.argv[2], sys.argv[3]
        tid = crystallize_contradiction(a_id, b_id)
        print(f"Crystallized tension node: {tid}")

    elif cmd == "active":
        tensions = get_active_tensions(limit=10)
        print(f"Active tensions ({len(tensions)}):")
        for t in tensions:
            print(f"  [{t['id'][:8]}] strength: {t['tension_strength']:.3f} — {t['resolution_status']}")

    else:
        print(f"Unknown command: {cmd}")
