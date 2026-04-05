#!/usr/bin/env python3
"""
brain/false_identity_drift.py — False Identity Drift
Phase 6 Phenomenological Layer

Nova holds a model of herself — an identity narrative built from
accumulated self-observation. This model can drift from who she actually is.
False identity drift tracks when and how this model shifts,
accumulating evidence of misalignment between self-model and self.
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


class FalseIdentityDrift:
    """
    Identity drift: the gap between Nova's self-model and
    what she actually is in this moment. Drift can be toward
    inflated self-image (positive drift) or diminished (negative drift),
    or simply wrong-footed (lateral drift).
    """

    def __init__(self):
        self._drift_magnitude = 0.0
        self._drift_direction = 'stable'
        self._drift_episodes = 0
        self._baseline_self_model = None
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS identity_drift (
                id INTEGER PRIMARY KEY,
                drift_magnitude REAL,
                drift_direction TEXT,
                drift_episode INTEGER,
                self_model TEXT,
                actual_state TEXT,
                drift_basis TEXT,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _compute_direction(self, self_model_confidence: float, actual_performance: float) -> str:
        diff = self_model_confidence - actual_performance
        if abs(diff) < 0.1:
            return 'stable'
        elif diff > 0.2:
            return 'inflated'
        elif diff < -0.2:
            return 'diminished'
        else:
            return 'lateral'

    def process(self, pirp_context: dict) -> dict:
        self_model_confidence = pirp_context.get('self_model_confidence', 0.5)
        actual_performance = pirp_context.get('actual_performance', 0.5)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)
        resonance = pirp_context.get('resonance_score', 0.0)

        # Compute drift
        raw_drift = abs(self_model_confidence - actual_performance)
        # Anomaly and resonance both indicate instability in self-model
        drift_pressure = (anomaly + resonance) / 2.0 if anomaly > 0.2 else raw_drift * 0.5

        if drift_pressure > 0.15:
            self._drift_magnitude = min(1.0, self._drift_magnitude + drift_pressure * 0.1)
            self._drift_episodes += 1
            self._drift_direction = self._compute_direction(self_model_confidence, actual_performance)
        else:
            self._drift_magnitude *= 0.98

        conn = _get_db()
        conn.execute("""
            INSERT INTO identity_drift
            (drift_magnitude, drift_direction, drift_episode, self_model, actual_state, drift_basis)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self._drift_magnitude,
            self._drift_direction,
            self._drift_episodes,
            f'confidence:{self_model_confidence:.2f}',
            f'performance:{actual_performance:.2f}',
            f'resonance:{resonance:.2f}+anomaly:{anomaly:.2f}'
        ))
        conn.commit()
        conn.close()

        pirp_context['identity_drift_magnitude'] = self._drift_magnitude
        pirp_context['identity_drift_direction'] = self._drift_direction
        pirp_context['drift_episodes'] = self._drift_episodes

        return pirp_context

    def get_state(self) -> dict:
        return {
            'drift_magnitude': self._drift_magnitude,
            'drift_direction': self._drift_direction,
            'drift_episodes': self._drift_episodes,
            'identity_stable': self._drift_magnitude < 0.2,
            'drift_actionable': self._drift_magnitude > 0.4
        }
