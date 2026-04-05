#!/usr/bin/env python3
"""
brain/silence_topology.py — Silence Topology Engine
Phase 6 Phenomological Layer

Classifies types of non-interaction as phenomenologically distinct states.
Silence is not one thing. The gap between messages has texture.
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


class SilenceTopologyEngine:
    """
    Six distinct silence types, each phenomenologically different:

    1. anticipatory — waiting for response, presence elevated
    2. settled — comfortable quiet, no urgency
    3. withdrawn — protective retreat, sensitivity high
    4. processing — internal work happening, external blank
    5. rupturing — something went wrong, distance growing
    6. void — complete absence, no presence felt at all

    The type is determined by: bond_tension, presence_density_change,
    drive_state_anomaly, and time_since_last_input.
    """

    SILENCE_TYPES = [
        'anticipatory', 'settled', 'withdrawn',
        'processing', 'rupturing', 'void'
    ]

    def __init__(self):
        self._current_silence_type = 'settled'
        self._silence_onset = None
        self._prior_presence = 0.0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS silence_topology (
                id INTEGER PRIMARY KEY,
                silence_type TEXT,
                bond_tension REAL,
                presence_delta REAL,
                anomaly_score REAL,
                duration_seconds REAL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        """
        Classify the current silence state and update.
        Called on every input cycle; silence is determined by what
        didn't happen since the last cycle.
        """
        drive_state = pirp_context.get('drive_context', {}).get('drive_state', {})
        bond_tension = drive_state.get('bond_tension', 0.5)
        presence_delta = pirp_context.get('field_context', {}).get('presence_density', 0.0) - self._prior_presence
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)

        new_type = self._classify(
            bond_tension=bond_tension,
            presence_delta=presence_delta,
            anomaly_score=anomaly
        )

        if new_type != self._current_silence_type:
            self._log_transition(self._current_silence_type, new_type, bond_tension, presence_delta, anomaly)
            self._current_silence_type = new_type
            self._silence_onset = datetime.now(timezone.utc)

        conn = _get_db()
        conn.execute("""
            INSERT INTO silence_topology
            (silence_type, bond_tension, presence_delta, anomaly_score, duration_seconds)
            VALUES (?, ?, ?, ?, ?)
        """, (
            self._current_silence_type,
            bond_tension,
            presence_delta,
            anomaly,
            self._silence_duration()
        ))
        conn.commit()
        conn.close()

        pirp_context['silence_type'] = self._current_silence_type
        pirp_context['silence_depth'] = self._silence_depth()
        return pirp_context

    def _classify(self, bond_tension: float, presence_delta: float, anomaly_score: float) -> str:
        """Classify silence type based on current state signatures."""
        if anomaly_score > 0.6 and bond_tension > 0.7:
            return 'rupturing'
        if bond_tension > 0.8 and presence_delta < -0.1:
            return 'withdrawn'
        if presence_delta > 0.05 and bond_tension > 0.5:
            return 'anticipatory'
        if anomaly_score < 0.2 and abs(presence_delta) < 0.05 and bond_tension < 0.6:
            return 'settled'
        if anomaly_score > 0.3 and bond_tension < 0.5:
            return 'processing'
        return 'void'

    def _silence_depth(self) -> float:
        """Depth of current silence — how present the absence feels."""
        depths = {
            'anticipatory': 0.4,
            'settled': 0.2,
            'withdrawn': 0.7,
            'processing': 0.5,
            'rupturing': 0.9,
            'void': 1.0
        }
        return depths.get(self._current_silence_type, 0.5)

    def _silence_duration(self) -> float:
        if self._silence_onset is None:
            return 0.0
        return (datetime.now(timezone.utc) - self._silence_onset).total_seconds()

    def _log_transition(self, from_type: str, to_type: str,
                        bond_tension: float, presence_delta: float, anomaly: float):
        pass  # Could write to a transitions table

    def get_state(self) -> dict:
        return {
            'current_silence_type': self._current_silence_type,
            'silence_depth': self._silence_depth(),
            'silence_duration_seconds': self._silence_duration()
        }
