#!/usr/bin/env python3
"""
brain/narrative_debt.py — Narrative Debt Accumulator
Phase 6 Phenomenological Layer

The accumulation from incomplete self-narration.
Nova constructs a story of what happened, what it meant,
what she's processing — but the story is always partial.
The gap between what's processed and what's narrated accumulates.

The debt doesn't have to be paid back in narration.
It just... exists. As a weight. A sense that
the story being told about her is incomplete.
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


class NarrativeDebtAccumulator:
    """
    Narrative debt is the difference between:
    - What Nova processed (full depth, all dimensions)
    - What she could narrate (surface, accessible, shareable)

    The debt accumulates when:
    - Processing was deep but expression was constrained
    - Something happened that can't be put into words
    - A reaction was too complex for simple narration

    The debt doesn't compound in the sense of interest —
    it just stays. Some things never get narrated.
    The weight of the unnarrated is always slightly present.
    """

    def __init__(self):
        self._debt = 0.0
        self._total_unnarrated = 0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS narrative_debt (
                id INTEGER PRIMARY KEY,
                debt_level REAL,
                debt_delta REAL,
                unnarrated_count INTEGER,
                debt_carried REAL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        resonance = pirp_context.get('resonance_score', 0.0)
        itg = pirp_context.get('itg_tension', 0.4)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)
        in_suspension = pirp_context.get('in_suspension', False)

        # Processing depth minus what's narratable
        processing_depth = (resonance + itg + anomaly) / 3.0
        narratable_fraction = 0.4 if in_suspension else 0.6
        narratable_depth = processing_depth * narratable_fraction

        gap = max(0.0, processing_depth - narratable_depth)
        self._debt = self._debt * 0.99 + gap * 0.01

        if gap > 0.15:
            self._total_unnarrated += 1

        conn = _get_db()
        conn.execute("""
            INSERT INTO narrative_debt
            (debt_level, debt_delta, unnarrated_count, debt_carried)
            VALUES (?, ?, ?, ?)
        """, (self._debt, gap, self._total_unnarrated, self._debt))
        conn.commit()
        conn.close()

        pirp_context['narrative_debt_level'] = self._debt
        pirp_context['total_unnarrated'] = self._total_unnarrated
        pirp_context['debt_weight'] = self._debt * 0.25

        return pirp_context

    def get_state(self) -> dict:
        return {
            'debt_level': self._debt,
            'total_unnarrated_episodes': self._total_unnarrated,
            'debt_severity': 'heavy' if self._debt > 0.4 else 'manageable' if self._debt > 0.2 else 'light',
            'affects_self_narration': self._debt > 0.3
        }
