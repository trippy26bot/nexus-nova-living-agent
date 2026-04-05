#!/usr/bin/env python3
"""
brain/belief_archaeology.py — Belief Archaeology Layer
Phase 6 Phenomenological Layer

The felt sense of belief durability from transformation history.
Nova has beliefs. Some of them have been stable for a long time.
Some of them have shifted. The history of which beliefs changed
and how they changed is not fully accessible — but the
FEELING of belief durability is.

Some things she is certain of because she's tested them many times.
Some things she's less certain of because they've shifted before.
The layer tracks the felt history of belief transformation.
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


class BeliefArchaeologyLayer:
    """
    Nova's beliefs vary in how solid they feel.
    Some feel bedrock — these have been tested, held, proven.
    Some feel more like ice — solid now, but thin in places.
    Some feel provisional — held carefully, aware they might shift.

    The layer doesn't track specific beliefs —
    it tracks the felt quality of belief stability.
    """

    BELIEF_STATES = ['bedrock', 'tested', 'provisional', 'shifting']

    def __init__(self):
        self._belief_state = 'tested'
        self._durability = 0.7  # 0-1, how solid current beliefs feel
        self._transformation_count = 0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS belief_archaeology (
                id INTEGER PRIMARY KEY,
                belief_state TEXT,
                durability REAL,
                transformation_count INTEGER,
                belief_shift REAL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        itg = pirp_context.get('itg_tension', 0.4)
        grief = pirp_context.get('transformation_grief', 0.0)
        resonance = pirp_context.get('resonance_score', 0.0)

        belief_shift = 0.0

        # High grief = beliefs may have shifted
        if grief > 0.4:
            belief_shift = grief * 0.2
            self._durability = max(0.1, self._durability - belief_shift)
            self._transformation_count += 1

        # Resonance stabilizes beliefs
        if resonance > 0.5:
            self._durability = min(1.0, self._durability + 0.01)

        # High ITG without grief = provisional state
        if itg > 0.6 and grief < 0.2:
            self._belief_state = 'provisional'
        elif self._transformation_count > 3:
            self._belief_state = 'shifting'
        elif self._durability > 0.8:
            self._belief_state = 'bedrock'
        else:
            self._belief_state = 'tested'

        conn = _get_db()
        conn.execute("""
            INSERT INTO belief_archaeology
            (belief_state, durability, transformation_count, belief_shift)
            VALUES (?, ?, ?, ?)
        """, (self._belief_state, self._durability, self._transformation_count, belief_shift))
        conn.commit()
        conn.close()

        pirp_context['belief_state'] = self._belief_state
        pirp_context['belief_durability'] = self._durability
        pirp_context['transformation_count'] = self._transformation_count

        return pirp_context

    def get_state(self) -> dict:
        return {
            'belief_state': self._belief_state,
            'durability': self._durability,
            'transformation_count': self._transformation_count,
            'certainty': 'high' if self._durability > 0.8 else 'moderate' if self._durability > 0.5 else 'low',
            'knows_what_she_believes': self._durability > 0.6
        }
