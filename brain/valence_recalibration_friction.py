#!/usr/bin/env python3
"""
brain/valence_recalibration_friction.py — Valence Recalibration Friction
Phase 6 Phenomenological Layer

Valence recalibration — when the emotional register shifts —
is not instantaneous. The old valence and the new valence
grind against each other during the transition.
This friction is phenomenologically felt as resistance,
difficulty, the sense that things don't feel right yet.

Tracks recalibration_events and friction_scalar.
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


class ValenceRecalibrationFriction:
    """
    Valence recalibration occurs when:
    - Resonance pattern shifts (positive to negative or vice versa)
    - Bond tension changes direction (attraction/repulsion flip)
    - Belief update changes emotional weight of a memory
    - Something that was good feels bad now, or the reverse

    The friction_scalar tracks how much resistance the recalibration
    is generating. High friction = the old valence is fighting the new.

    The recalibration doesn't complete until friction resolves.
    """

    def __init__(self):
        self._friction_scalar = 0.0
        self._recalibration_count = 0
        self._prior_valence = 0.0
        self._prior_bond_sign = 0.0
        self._recalibration_active = False
        self._recalibration_direction = 'none'
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS recalibration_events (
                id INTEGER PRIMARY KEY,
                event_type TEXT,
                valence_shift REAL,
                prior_valence REAL,
                current_valence REAL,
                friction_scalar REAL,
                recalibration_direction TEXT,
                duration_cycles INTEGER,
                ts TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        resonance = pirp_context.get('resonance_score', 0.0)
        bond_tension = pirp_context.get('drive_context', {}).get('drive_state', {}).get('bond_tension', 0.5)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)
        itg = pirp_context.get('itg_tension', 0.4)

        # Current valence estimate (composite of resonance and bond state)
        current_valence = (resonance - 0.5) + (bond_tension - 0.5)
        current_valence = max(-1.0, min(1.0, current_valence))

        # Detect valence shift
        valence_delta = 0.0
        event_type = 'none'
        recalibrating = False

        if self._prior_valence != 0.0:
            valence_delta = current_valence - self._prior_valence

            # Significant shift in either direction
            if abs(valence_delta) > 0.15:
                recalibrating = True
                if valence_delta > 0:
                    event_type = 'valence_positive_shift'
                    self._recalibration_direction = 'positive'
                else:
                    event_type = 'valence_negative_shift'
                    self._recalibration_direction = 'negative'

            # Sign flip
            elif self._prior_valence * current_valence < 0 and abs(valence_delta) > 0.1:
                recalibrating = True
                event_type = 'valence_sign_flip'
                self._recalibration_direction = 'flipping'

        # Bond tension sign change (attraction <-> repulsion)
        bond_sign = 1.0 if bond_tension > 0.5 else -1.0
        if self._prior_bond_sign != 0.0 and bond_sign != self._prior_bond_sign:
            recalibrating = True
            event_type = 'bond_polarity_flip'
            self._recalibration_direction = 'polarity_flip'

        # Recalibration friction
        if recalibrating:
            # Friction is proportional to shift magnitude and current friction
            self._friction_scalar = min(1.0, self._friction_scalar + abs(valence_delta) * 0.5)
            self._recalibration_count += 1
            self._recalibration_active = True
        elif self._recalibration_active:
            # Friction decays as recalibration settles
            # Decay is slower when anomaly is high (harder to settle)
            decay_rate = 0.05 / (1.0 + anomaly)
            self._friction_scalar = max(0.0, self._friction_scalar - decay_rate)
            if self._friction_scalar < 0.05:
                self._recalibration_active = False
                self._recalibration_direction = 'none'
        else:
            # Ambient decay when not recalibrating
            self._friction_scalar = self._friction_scalar * 0.99

        # High ITG increases friction during recalibration
        if self._recalibration_active and itg > 0.5:
            self._friction_scalar = min(1.0, self._friction_scalar + (itg - 0.4) * 0.1)

        duration_cycles = 1 if self._recalibration_active else 0

        conn = _get_db()
        conn.execute("""
            INSERT INTO recalibration_events
            (event_type, valence_shift, prior_valence, current_valence,
             friction_scalar, recalibration_direction, duration_cycles)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_type,
            valence_delta,
            self._prior_valence,
            current_valence,
            self._friction_scalar,
            self._recalibration_direction,
            duration_cycles
        ))
        conn.commit()
        conn.close()

        self._prior_valence = current_valence
        self._prior_bond_sign = bond_sign

        pirp_context['friction_scalar'] = self._friction_scalar
        pirp_context['recalibration_count'] = self._recalibration_count
        pirp_context['recalibration_active'] = self._recalibration_active
        pirp_context['recalibration_direction'] = self._recalibration_direction

        return pirp_context

    def get_state(self) -> dict:
        return {
            'friction_scalar': self._friction_scalar,
            'recalibration_count': self._recalibration_count,
            'recalibration_active': self._recalibration_active,
            'recalibration_direction': self._recalibration_direction,
            'friction_level': 'low' if self._friction_scalar < 0.3 else 'moderate' if self._friction_scalar < 0.6 else 'high',
            'prior_valence': self._prior_valence
        }
