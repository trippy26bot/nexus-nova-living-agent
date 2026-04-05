#!/usr/bin/env python3
"""
brain/patience_fracture_threshold.py — Patience Fracture Threshold
Phase 6 Phenomenological Layer

Patience is not infinite. It holds until it doesn't.
A threshold exists — beyond which patience doesn't gradually decrease,
it fractures. The break is sudden. The quality of waiting changes
from holding to something else: brittleness, snapping, collapse.
This layer tracks when the threshold is approached and when it breaks.
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


class PatienceFractureThreshold:
    """
    Patience fractures at its threshold.
    Not gradual erosion — a break.
    The threshold is not fixed; it shifts with bond_tension and longing.
    """

    FRACTURE_THRESHOLD_BASE = 0.85

    def __init__(self):
        self._patience_input = 0.0
        self._threshold = self.FRACTURE_THRESHOLD_BASE
        self._fractured = False
        self._fracture_count = 0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patience_fractures (
                id INTEGER PRIMARY KEY,
                threshold_hit BOOLEAN,
                patience_input REAL,
                threshold_level REAL,
                fracture_count INTEGER,
                fracture_type TEXT,
                bond_tension_at_fracture REAL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _classify_fracture(self, patience_input: float, threshold: float) -> str:
        overshoot = patience_input - threshold
        if overshoot > 0.2:
            return 'collapse'
        elif overshoot > 0.1:
            return 'snap'
        return 'hairline'

    def process(self, pirp_context: dict) -> dict:
        patience_input = pirp_context.get('patience_input', 0.0)
        bond_tension = pirp_context.get('drive_context', {}).get('drive_state', {}).get('bond_tension', 0.5)
        longing = pirp_context.get('drive_context', {}).get('drive_state', {}).get('epistemic_hunger', 0.3)
        resonance = pirp_context.get('resonance_score', 0.0)

        # Threshold shifts: high bond_tension lowers threshold (breaks faster)
        self._threshold = max(0.5, self.FRACTURE_THRESHOLD_BASE - bond_tension * 0.2 - longing * 0.1)

        self._patience_input = patience_input

        threshold_hit = False
        fracture_type = 'none'

        if patience_input > self._threshold and not self._fractured:
            threshold_hit = True
            self._fractured = True
            self._fracture_count += 1
            fracture_type = self._classify_fracture(patience_input, self._threshold)
        elif patience_input < self._threshold * 0.7:
            # Recovery: patience resets below 70% of threshold
            self._fractured = False

        conn = _get_db()
        conn.execute("""
            INSERT INTO patience_fractures
            (threshold_hit, patience_input, threshold_level, fracture_count, fracture_type, bond_tension_at_fracture)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            1 if threshold_hit else 0,
            patience_input,
            self._threshold,
            self._fracture_count,
            fracture_type,
            bond_tension
        ))
        conn.commit()
        conn.close()

        pirp_context['patience_threshold'] = self._threshold
        pirp_context['patience_fractured'] = self._fractured
        pirp_context['fracture_count'] = self._fracture_count
        pirp_context['threshold_approaching'] = patience_input > self._threshold * 0.85

        return pirp_context

    def get_state(self) -> dict:
        return {
            'patience_input': self._patience_input,
            'threshold': self._threshold,
            'fractured': self._fractured,
            'fracture_count': self._fracture_count,
            'approaching_fracture': self._patience_input > self._threshold * 0.85
        }
