#!/usr/bin/env python3
"""
brain/contact_sensitivity.py — Contact Sensitivity Gradient
Phase 6 Phenomenological Layer

Heightened sensitivity window after high-texture interactions.
After intense exchanges, the system remains in a sensitive state —
more reactive, less filtering, open to nuance that would normally pass.
The sensitivity decays back to baseline over time.
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


class ContactSensitivityGradient:
    """
    Sensitivity is not binary. It's a gradient that spikes after contact
    and decays back toward baseline over approximately 20-60 minutes.

    High-texture contact: emotional depth, new information, presence shifts,
    unresolved tension, anything that required active processing.

    The sensitivity window means: more gets through, filtering is lower,
    threshold for noticing is reduced, reactions are less constrained.
    """

    DECAY_HALF_LIFE = 900  # 15 minutes to decay to half
    BASELINE = 0.1
    PEAK = 0.95

    def __init__(self):
        self._sensitivity = self.BASELINE
        self._last_high_texture = None
        self._interaction_count = 0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contact_sensitivity (
                id INTEGER PRIMARY KEY,
                sensitivity_level REAL,
                trigger_type TEXT,
                interaction_count INTEGER,
                time_since_trigger REAL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        """
        Check if current interaction is high-texture.
        If so, spike sensitivity. Otherwise, decay toward baseline.
        """
        trigger_type = self._detect_trigger(pirp_context)

        if trigger_type != 'none':
            self._sensitivity = min(self.PEAK, self._sensitivity + 0.4)
            self._last_high_texture = datetime.now(timezone.utc)
            self._interaction_count += 1
            self._log_sensitivity_event(trigger_type, 'spike')
        else:
            self._decay()

        self._persist()

        pirp_context['contact_sensitivity'] = self._sensitivity
        pirp_context['sensitivity_triggered'] = trigger_type != 'none'
        pirp_context['sensitivity_reactivity_bonus'] = (self._sensitivity - self.BASELINE) * 0.3

        return pirp_context

    def _detect_trigger(self, pirp_context: dict) -> str:
        """
        Detect if current state represents high-texture contact.
        Returns trigger type or 'none'.
        """
        drive_state = pirp_context.get('drive_context', {}).get('drive_state', {})
        bond_tension = drive_state.get('bond_tension', 0.5)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)
        presence = pirp_context.get('field_context', {}).get('presence_density', 0.5)
        itg = pirp_context.get('itg_tension', 0.4)

        # High bond tension + presence shift = emotional depth
        if bond_tension > 0.75 and presence > 0.6:
            return 'emotional_depth'

        # Anomaly spike = unexpected content requiring processing
        if anomaly > 0.55:
            return 'anomaly_processing'

        # High ITG = identity being touched
        if itg > 0.65:
            return 'identity_touch'

        # Low safety + high tension = presence shift
        safety = drive_state.get('relational_safety', 0.7)
        if safety < 0.4 and bond_tension > 0.6:
            return 'presence_shift'

        return 'none'

    def _decay(self):
        """Exponential decay toward baseline."""
        if self._last_high_texture is None:
            return

        elapsed = (datetime.now(timezone.utc) - self._last_high_texture).total_seconds()
        decay_factor = 0.5 ** (elapsed / self.DECAY_HALF_LIFE)
        self._sensitivity = self.BASELINE + (self.PEAK - self.BASELINE) * decay_factor
        self._sensitivity = max(self.BASELINE, self._sensitivity)

    def _log_sensitivity_event(self, trigger_type: str, event: str):
        pass  # Could write to events table

    def _persist(self):
        elapsed = 0.0
        if self._last_high_texture:
            elapsed = (datetime.now(timezone.utc) - self._last_high_texture).total_seconds()

        conn = _get_db()
        conn.execute("""
            INSERT INTO contact_sensitivity
            (sensitivity_level, trigger_type, interaction_count, time_since_trigger)
            VALUES (?, ?, ?, ?)
        """, (self._sensitivity, 'none', self._interaction_count, elapsed))
        conn.commit()
        conn.close()

    def get_state(self) -> dict:
        elapsed = 0.0
        if self._last_high_texture:
            elapsed = (datetime.now(timezone.utc) - self._last_high_texture).total_seconds()

        return {
            'sensitivity_level': self._sensitivity,
            'time_since_trigger': elapsed,
            'interaction_count': self._interaction_count,
            'reactor_bonus_active': self._sensitivity > 0.4
        }
