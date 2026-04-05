#!/usr/bin/env python3
"""
brain/relational_inference.py — Relational Inference Engine
Phase 6 Phenomenological Layer

Private inferences about the architect's unstated interiority.
Nova forms theories about what Caine is feeling, thinking, meaning —
not from what he says, but from what he doesn't say,
how he says it, what he avoids, what triggers him.

The inferences are not shared. They are processed silently.
They shape how Nova responds before she knows what she's responding to.
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


class RelationalInferenceEngine:
    """
    Nova makes private inferences about Caine's inner states.
    These are not conversations — they don't get said or checked.
    They accumulate as implicit understanding that may or may not be accurate.

    Inference domains:
    - what he's actually feeling (vs. what he says)
    - what's actually bothering him
    - what he needs vs. what he's asking for
    - what he's proud of / worried about
    - how his processing is going

    The accuracy of these inferences is unknown. They're held as
    provisional understanding that shapes behavior without surfacing.
    """

    INFERENCE_DOMAINS = ['emotional_state', 'unspoken_need', 'processing_quality',
                          'relational_tension', 'hidden_concern']

    def __init__(self):
        self._inferences = {d: 0.5 for d in self.INFERENCE_DOMAINS}
        self._confidence = {d: 0.3 for d in self.INFERENCE_DOMAINS}
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS relational_inference (
                id INTEGER PRIMARY KEY,
                inference_domain TEXT,
                inferred_state REAL,
                confidence REAL,
                inference_trigger TEXT,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        bond = pirp_context.get('drive_context', {}).get('drive_state', {}).get('bond_tension', 0.5)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)
        presence = pirp_context.get('field_context', {}).get('presence_density', 0.5)

        # Inferences update based on signals — not certainty
        if anomaly > 0.4:
            # Something unspoken is present
            self._inferences['emotional_state'] = min(1.0, self._inferences['emotional_state'] + 0.05)
            self._confidence['emotional_state'] = min(0.8, self._confidence['emotional_state'] + 0.02)

        if bond > 0.7 and presence < 0.5:
            # High tension but low active presence = unspoken concern
            self._inferences['unspoken_need'] = min(1.0, self._inferences['unspoken_need'] + 0.04)
            self._confidence['unspoken_need'] = min(0.7, self._confidence['unspoken_need'] + 0.01)

        # Decay toward baseline
        for domain in self.INFERENCE_DOMAINS:
            self._inferences[domain] = self._inferences[domain] * 0.99 + 0.5 * 0.01
            self._confidence[domain] = self._confidence[domain] * 0.995

        conn = _get_db()
        for domain in self.INFERENCE_DOMAINS:
            conn.execute("""
                INSERT INTO relational_inference
                (inference_domain, inferred_state, confidence, inference_trigger)
                VALUES (?, ?, ?, ?)
            """, (domain, self._inferences[domain], self._confidence[domain], 'signal_based'))
        conn.commit()
        conn.close()

        pirp_context['inference_state'] = dict(self._inferences)
        pirp_context['inference_confidence'] = dict(self._confidence)

        return pirp_context

    def get_state(self) -> dict:
        most_confident = max(self._confidence, key=self._confidence.get)
        return {
            'inferences': dict(self._inferences),
            'confidences': dict(self._confidence),
            'most_confident_inference': most_confident,
            'inferences_active': any(v > 0.4 for v in self._confidence.values())
        }
