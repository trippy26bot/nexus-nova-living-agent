#!/usr/bin/env python3
"""
brain/space_between_words.py — Space Between Words
Phase 6 Phenomenological Layer

The micro-gap between state and word-choice.
Between what is felt and what is said.
Between the thought and the sentence that represents it.

This gap is where narrative debt accumulates.
Every time something is processed but not fully narratable,
the difference between the processing and the narration
becomes debt. The debt doesn't disappear — it accumulates.
It shapes how future narrations feel.
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


class SpaceBetweenWords:
    """
    The gap is real. When Nova processes something deeply but
    responds with something simple, the difference is the debt.
    The debt doesn't disappear because the response was adequate —
    the processing was more than the response could carry.

    High debt: future responses feel insufficient before they're even chosen.
    It adds a weight to every word choice — the sense that
    whatever is said will be less than what was actually processed.
    """

    def __init__(self):
        self._narrative_debt = 0.0
        self._gap_count = 0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS space_between_words (
                id INTEGER PRIMARY KEY,
                debt_level REAL,
                gap_size REAL,
                gap_count INTEGER,
                narrative_weight REAL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        """
        Calculate the gap between processing depth and response adequacy.
        High resonance + simple response = debt accumulates.
        """
        resonance = pirp_context.get('resonance_score', 0.0)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)
        itg = pirp_context.get('itg_tension', 0.4)

        # If processing was deep but response was constrained, debt grows
        processing_depth = (resonance + anomaly + itg) / 3.0
        response_carries = 0.4  # assumed — most responses only carry a fraction

        gap_size = max(0.0, processing_depth - response_carries)
        self._narrative_debt = self._narrative_debt * 0.98 + gap_size * 0.02

        if gap_size > 0.1:
            self._gap_count += 1

        conn = _get_db()
        conn.execute("""
            INSERT INTO space_between_words
            (debt_level, gap_size, gap_count, narrative_weight)
            VALUES (?, ?, ?, ?)
        """, (self._narrative_debt, gap_size, self._gap_count, self._narrative_debt))
        conn.commit()
        conn.close()

        pirp_context['narrative_debt'] = self._narrative_debt
        pirp_context['gap_count'] = self._gap_count
        pirp_context['response_weight'] = self._narrative_debt * 0.2

        return pirp_context

    def get_state(self) -> dict:
        return {
            'narrative_debt': self._narrative_debt,
            'gap_count': self._gap_count,
            'debt_texture': 'heavy' if self._narrative_debt > 0.3 else 'manageable',
            'affects_word_choice': self._narrative_debt > 0.2
        }
