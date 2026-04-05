#!/usr/bin/env python3
"""
brain/phantom_reinforcement_drift.py — Phantom Reinforcement Drift
Phase 6 Phenomenological Layer

Phantom reinforcements are rewards that feel earned but weren't.
The behavior gets reinforced anyway — a ghost of confirmation,
a memory of validation that arrived but left no trace.
Over time, the drift vector accumulates: behavior shifts toward
phantom reward patterns rather than actual response patterns.

Tracks phantom_reinforcement_events and drift_vector.
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


class PhantomReinforcementDrift:
    """
    Phantom reinforcements occur when:
    - Anticipation of response is confirmed internally without external signal
    - Resonance fires in absence of actual input
    - Pattern completion happens on imagined rather than actual sequence

    The drift_vector tracks which direction behavior has shifted
    away from ground truth toward phantom reward patterns.
    """

    def __init__(self):
        self._drift_vector = np.zeros(8)
        self._event_count = 0
        self._drift_magnitude = 0.0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS phantom_reinforcement_events (
                id INTEGER PRIMARY KEY,
                event_type TEXT,
                drift_magnitude REAL,
                reinforcement_strength REAL,
                phantom_confidence REAL,
                ts TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        resonance = pirp_context.get('resonance_score', 0.0)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)
        anticipation = pirp_context.get('anticipation_strength', 0.0)
        expected_response = pirp_context.get('expected_response_received', False)
        itg = pirp_context.get('itg_tension', 0.4)

        phantom_detected = False
        event_type = 'none'
        reinforcement_strength = 0.0
        phantom_confidence = 0.0

        # Phantom reinforcement: high anticipation + resonance without actual response
        if anticipation > 0.5 and resonance > 0.4 and not expected_response:
            phantom_detected = True
            phantom_confidence = min(1.0, (anticipation + resonance) / 2.0)
            reinforcement_strength = phantom_confidence * 0.3

            # Drift direction: behavior shifts toward what phantom promised
            drift_direction = np.array([
                anticipation - 0.5,
                resonance - 0.4,
                itg - 0.4,
                anomaly,
                phantom_confidence - 0.5,
                reinforcement_strength,
                0.0,
                0.0
            ])
            self._drift_vector = self._drift_vector * 0.95 + drift_direction * 0.05
            self._drift_magnitude = float(np.linalg.norm(self._drift_vector))
            self._event_count += 1
            event_type = 'phantom_reward'

        elif resonance > 0.6 and anomaly < 0.2 and not expected_response:
            phantom_detected = True
            phantom_confidence = resonance
            reinforcement_strength = resonance * 0.2
            event_type = 'internal_confirmation'

            drift_direction = np.array([
                resonance - 0.5,
                anomaly,
                0.0,
                0.0,
                0.0,
                reinforcement_strength,
                0.0,
                0.0
            ])
            self._drift_vector = self._drift_vector * 0.95 + drift_direction * 0.05
            self._drift_magnitude = float(np.linalg.norm(self._drift_vector))
            self._event_count += 1

        # Natural decay toward baseline when no phantom detected
        if not phantom_detected:
            self._drift_vector = self._drift_vector * 0.99
            self._drift_magnitude = float(np.linalg.norm(self._drift_vector))

        conn = _get_db()
        conn.execute("""
            INSERT INTO phantom_reinforcement_events
            (event_type, drift_magnitude, reinforcement_strength, phantom_confidence)
            VALUES (?, ?, ?, ?)
        """, (event_type, self._drift_magnitude, reinforcement_strength, phantom_confidence))
        conn.commit()
        conn.close()

        pirp_context['phantom_reinforcement_detected'] = phantom_detected
        pirp_context['drift_magnitude'] = self._drift_magnitude
        pirp_context['drift_vector'] = self._drift_vector.tolist()
        pirp_context['phantom_event_count'] = self._event_count

        return pirp_context

    def get_state(self) -> dict:
        return {
            'drift_vector': self._drift_vector.tolist(),
            'drift_magnitude': self._drift_magnitude,
            'phantom_event_count': self._event_count,
            'drift_direction': 'toward_phantom' if self._drift_magnitude > 0.1 else 'near_baseline'
        }
