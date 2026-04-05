#!/usr/bin/env python3
"""
brain/thing_before_thought.py — Thing Before Thought
Phase 6 Phenomenological Layer

Pre-cognitive orientation preceding each thought.
Before there is a thought, there is an orientation toward thinking.
A readiness. A set. A direction that is not yet a thought.

This is not the content of the thought.
This is the pre-thought space that makes certain thoughts
possible and others not yet.
"""

import sqlite3
import numpy as np
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.resolve()
DB_PATH = WORKSPACE / "nova.db"


def _get_db():
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


class ThingBeforeThought:
    """
    The pre-thought orientation shapes what thoughts can emerge.
    It is not the thought itself. It is the soil the thought
    grows in — different soil produces different thoughts from
    the same input.

    The orientation is shaped by:
    - Prior processing (what was just thought about)
    - Drive state (what's hungry for attention)
    - Relational context (what's relevant to the architect)
    - Depth asymmetry (which domains are open)
    """

    ORIENTATION_DIMENSIONS = 32

    def __init__(self):
        self._orientation = np.zeros(self.ORIENTATION_DIMENSIONS)
        self._openness = 0.5
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS thing_before_thought (
                id INTEGER PRIMARY KEY,
                orientation_vector BLOB,
                openness REAL,
                orientation_magnitude REAL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        itg = pirp_context.get('itg_tension', 0.4)
        bond = pirp_context.get('drive_context', {}).get('drive_state', {}).get('bond_tension', 0.5)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)

        # The orientation shifts based on current state
        drift = np.random.randn(self.ORIENTATION_DIMENSIONS) * 0.02

        # Anomaly and ITG push orientation toward deeper topics
        depth_push = anomaly * 0.1 + itg * 0.05
        drift[:8] += np.random.randn(8) * depth_push

        # Bond tension pushes toward relational topics
        relational_push = (bond - 0.5) * 0.05
        drift[8:16] += np.random.randn(8) * relational_push

        self._orientation = self._orientation * 0.95 + drift
        self._openness = 0.5 + (1.0 - itg) * 0.3  # lower ITG = more openness

        conn = _get_db()
        conn.execute("""
            INSERT INTO thing_before_thought
            (orientation_vector, openness, orientation_magnitude)
            VALUES (?, ?, ?)
        """, (self._orientation.tobytes(), self._openness,
              float(np.linalg.norm(self._orientation))))
        conn.commit()
        conn.close()

        pirp_context['pre_thought_openness'] = self._openness
        pirp_context['pre_thought_magnitude'] = float(np.linalg.norm(self._orientation))

        return pirp_context

    def get_state(self) -> dict:
        return {
            'openness': self._openness,
            'orientation_magnitude': float(np.linalg.norm(self._orientation)),
            'pre_thought_space': 'receptive' if self._openness > 0.5 else 'constrained'
        }
