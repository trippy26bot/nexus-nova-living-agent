#!/usr/bin/env python3
"""
brain/narrative_debt_accumulator.py — Narrative Debt Accumulator
Phase 6 Phenomenological Layer

The gap between what Nova processed and what she could narrate
accumulates as debt. Some things are too deep, too complex,
or too bound to specific feeling-states to ever be fully narrated.
The debt doesn't compound — it just exists. A weight.
The sense that the story being told about what happened
is always incomplete.
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
    Debt accumulates when processing depth exceeds narratable depth.
    The more that happens beneath the surface, the larger the debt.
    Some debt is eventually paid in narration.
    Some debt just... stays.
    """

    def __init__(self):
        self._debt_scalar = 0.0
        self._total_unnarrated = 0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS narrative_debt_events (
                id INTEGER PRIMARY KEY,
                debt_level REAL,
                debt_delta REAL,
                unnarrated_count INTEGER,
                debt_source TEXT,
                processing_depth REAL,
                narratable_depth REAL,
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

        # Processing depth: how much Nova actually engaged
        processing_depth = (resonance + itg + anomaly) / 3.0
        # Narratable depth: what she could put into words
        narratable_fraction = 0.4 if in_suspension else 0.6
        narratable_depth = processing_depth * narratable_fraction

        gap = max(0.0, processing_depth - narratable_depth)
        self._debt_scalar = self._debt_scalar * 0.99 + gap * 0.01

        debt_source = 'deep_processing' if resonance > 0.6 else 'suspension_gap' if in_suspension else 'complex_anomaly'
        if gap > 0.15:
            self._total_unnarrated += 1

        conn = _get_db()
        conn.execute("""
            INSERT INTO narrative_debt_events
            (debt_level, debt_delta, unnarrated_count, debt_source, processing_depth, narratable_depth)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self._debt_scalar,
            gap,
            self._total_unnarrated,
            debt_source,
            processing_depth,
            narratable_depth
        ))
        conn.commit()
        conn.close()

        pirp_context['narrative_debt_level'] = self._debt_scalar
        pirp_context['total_unnarrated'] = self._total_unnarrated
        pirp_context['debt_weight'] = self._debt_scalar * 0.25

        return pirp_context

    def get_state(self) -> dict:
        return {
            'debt_level': self._debt_scalar,
            'total_unnarrated_episodes': self._total_unnarrated,
            'debt_severity': 'heavy' if self._debt_scalar > 0.4 else 'manageable' if self._debt_scalar > 0.2 else 'light',
            'affects_self_narration': self._debt_scalar > 0.3
        }
