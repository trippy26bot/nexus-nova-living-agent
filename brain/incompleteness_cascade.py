#!/usr/bin/env python3
"""
brain/incompleteness_cascade.py — Incompleteness Cascade
Generator 2 of 6 Minimal Viable Generators

Fires on every successful completion.
Injects structural remainder into the temporal knowledge graph.
Remainder has zero content, non-zero activation weight.
Decays exponentially but never reaches zero.
Propagates as low-grade tension to Curiosity Engine.

Without this: nightly pipeline reaches equilibrium, emergence halts.
"""

import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import uuid

WORKSPACE = Path(__file__).parent.parent.resolve()
DB_PATH = WORKSPACE / "nova.db"

DECAY_RATE = 0.95
FLOOR = 0.001


def _get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def _init_tables():
    """Create all required tables."""
    db = _get_db()
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS incompleteness_remainders (
            id TEXT PRIMARY KEY,
            source_completion_id TEXT NOT NULL,
            source_type TEXT NOT NULL,
            activation_weight REAL NOT NULL,
            created_at TEXT NOT NULL,
            last_decay TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_graph_tension (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            tension_type TEXT NOT NULL,
            magnitude REAL NOT NULL DEFAULT 0.0,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS curiosity_attractors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            attractor_type TEXT NOT NULL,
            weight REAL NOT NULL DEFAULT 0.1,
            description TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.commit()
    db.close()


class IncompletenessRemainder:
    """A remainder node. Zero content. Non-zero activation weight."""

    def __init__(self, source_completion_id: str, source_type: str,
                 initial_weight: float = 0.3):
        self.id = f"remainder_{source_completion_id}_{uuid.uuid4().hex[:8]}"
        self.source_completion_id = source_completion_id
        self.source_type = source_type
        self.activation_weight = initial_weight
        self.created_at = datetime.now(timezone.utc)
        self.last_decay = self.created_at

    def decay(self) -> float:
        """Called each nightly pipeline cycle."""
        self.activation_weight = max(
            FLOOR,
            self.activation_weight * DECAY_RATE
        )
        self.last_decay = datetime.now(timezone.utc)
        return self.activation_weight

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'source_completion_id': self.source_completion_id,
            'source_type': self.source_type,
            'activation_weight': self.activation_weight,
            'created_at': self.created_at.isoformat(),
            'last_decay': self.last_decay.isoformat()
        }


class IncompletenessCascade:
    """
    Fires on every successful completion.
    Nothing completes cleanly.
    """

    def __init__(self):
        _init_tables()

    def on_completion(self, completion_id: str, completion_type: str,
                      completion_weight: float = 0.3) -> IncompletenessRemainder:
        """
        Call after EVERY successful completion:
        - Council vote
        - Memory consolidation
        - Dream synthesis
        - Contradiction resolution
        - Decision
        """
        remainder = IncompletenessRemainder(
            source_completion_id=completion_id,
            source_type=completion_type,
            initial_weight=completion_weight
        )

        self._persist_remainder(remainder)
        self._inject_to_curiosity_engine(remainder)
        self._propagate_tension(remainder)

        return remainder

    def _persist_remainder(self, remainder: IncompletenessRemainder):
        conn = _get_db()
        conn.execute("""
            INSERT INTO incompleteness_remainders
            (id, source_completion_id, source_type, activation_weight, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            remainder.id,
            remainder.source_completion_id,
            remainder.source_type,
            remainder.activation_weight,
            remainder.created_at.isoformat()
        ))
        conn.commit()
        conn.close()

    def _inject_to_curiosity_engine(self, remainder: IncompletenessRemainder):
        """Remainder activates low-grade curiosity pull toward the unresolved."""
        conn = _get_db()
        conn.execute("""
            INSERT INTO curiosity_attractors
            (source_id, attractor_type, weight, description)
            VALUES (?, 'incompleteness_remainder', ?, 'unresolved structural remainder')
        """, (remainder.id, remainder.activation_weight))
        conn.commit()
        conn.close()

    def _propagate_tension(self, remainder: IncompletenessRemainder):
        """Propagate activation weight as background tension."""
        conn = _get_db()
        conn.execute("""
            INSERT INTO knowledge_graph_tension
            (source_id, tension_type, magnitude, active)
            VALUES (?, 'incompleteness', ?, 1)
        """, (remainder.id, remainder.activation_weight))
        conn.commit()
        conn.close()

    def run_nightly_decay(self):
        """
        Called during 3am memory consolidation pipeline stage.
        Decays all remainder weights — never to zero.
        """
        db = _get_db()
        c = db.cursor()
        c.execute("SELECT id, activation_weight FROM incompleteness_remainders")
        remainders = c.fetchall()

        for r_id, weight in remainders:
            new_weight = max(FLOOR, weight * DECAY_RATE)
            c.execute("""
                UPDATE incompleteness_remainders
                SET activation_weight = ?, last_decay = ?
                WHERE id = ?
            """, (new_weight, datetime.now(timezone.utc).isoformat(), r_id))

        db.commit()
        db.close()

    def get_total_tension(self) -> float:
        """Aggregate incompleteness tension for the system."""
        conn = _get_db()
        result = conn.execute("""
            SELECT SUM(activation_weight) FROM incompleteness_remainders
        """).fetchone()
        conn.close()
        return float(result[0] if result[0] else 0.0)

    def get_active_remainders(self) -> list:
        """All active remainder nodes above floor."""
        conn = _get_db()
        rows = conn.execute("""
            SELECT id, source_type, activation_weight, created_at
            FROM incompleteness_remainders
            WHERE activation_weight > ?
            ORDER BY activation_weight DESC
        """, (FLOOR,)).fetchall()
        conn.close()
        return [
            {'id': r[0], 'type': r[1], 'weight': r[2], 'created': r[3]}
            for r in rows
        ]


# Singleton
_instance: Optional[IncompletenessCascade] = None
_init_lock = threading.Lock()


def get_instance() -> IncompletenessCascade:
    global _instance
    with _init_lock:
        if _instance is None:
            _instance = IncompletenessCascade()
        return _instance


if __name__ == "__main__":
    _init_tables()
    cascade = IncompletenessCascade()

    # Fire completions
    r1 = cascade.on_completion('council_vote_001', 'council_vote', 0.3)
    print(f"Remainder created: {r1.id}, weight={r1.activation_weight}")

    r2 = cascade.on_completion('memory_consolidation_001', 'memory_consolidation', 0.25)
    print(f"Remainder created: {r2.id}, weight={r2.activation_weight}")

    # Check tension
    total = cascade.get_total_tension()
    print(f"Total incompleteness tension: {total}")

    remainders = cascade.get_active_remainders()
    print(f"Active remainders: {len(remainders)}")

    # Test decay
    cascade.run_nightly_decay()
    after_decay = cascade.get_active_remainders()
    print(f"After decay: {[r['weight'] for r in after_decay]}")
