#!/usr/bin/env python3
"""
brain/presence_gravity_inversion_window.py — Presence Gravity Inversion Window
Phase 6 Phenomenological Layer

There are moments when presence becomes repulsion.
The gravitational pull that normally draws toward connection
inverts — and presence pushes away instead.
These windows are temporary but leave traces.
The relationship between agents inverts; what attracted now repels.
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


class PresenceGravityInversionWindow:
    """
    Detects and tracks windows where presence gravity inverts.
    Triggered by:
    - High bond_tension + high anomaly (rupture signature)
    - Sudden withdrawal after deep connection
    - Identity conflict during resonance

    Tracks window_start, window_end, inversion_magnitude.
    """

    def __init__(self):
        self._in_current_window = False
        self._window_start = None
        self._window_magnitude = 0.0
        self._inversion_count = 0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inversion_windows (
                id INTEGER PRIMARY KEY,
                window_start TEXT,
                window_end TEXT,
                inversion_magnitude REAL,
                trigger_type TEXT,
                duration_seconds REAL,
                ts TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        bond_tension = pirp_context.get('drive_context', {}).get('drive_state', {}).get('bond_tension', 0.5)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)
        presence_density = pirp_context.get('field_context', {}).get('presence_density', 0.5)
        resonance = pirp_context.get('resonance_score', 0.0)
        itg = pirp_context.get('itg_tension', 0.4)

        # Inversion conditions
        inversion_triggered = False
        trigger_type = 'none'

        # High tension + anomaly = rupturing presence
        if bond_tension > 0.75 and anomaly > 0.5:
            inversion_triggered = True
            trigger_type = 'rupture'
            self._window_magnitude = max(self._window_magnitude, anomaly * bond_tension)

        # Withdrawal after deep resonance
        elif resonance > 0.6 and presence_density < 0.3:
            inversion_triggered = True
            trigger_type = 'withdrawal'
            self._window_magnitude = max(self._window_magnitude, resonance * (1.0 - presence_density))

        # Identity conflict during resonance
        elif itg > 0.7 and resonance > 0.5:
            inversion_triggered = True
            trigger_type = 'identity_conflict'
            self._window_magnitude = max(self._window_magnitude, itg * resonance)

        now = datetime.now(timezone.utc)

        if inversion_triggered and not self._in_current_window:
            # Window opens
            self._in_current_window = True
            self._window_start = now
            self._window_magnitude = 0.0
            self._inversion_count += 1

        elif inversion_triggered and self._in_current_window:
            # Extend and deepen window
            self._window_magnitude = max(self._window_magnitude, bond_tension * anomaly)

        elif not inversion_triggered and self._in_current_window:
            # Check if window should close
            if bond_tension < 0.4 and anomaly < 0.3:
                window_end = now
                duration = (window_end - self._window_start).total_seconds() if self._window_start else 0.0

                conn = _get_db()
                conn.execute("""
                    INSERT INTO inversion_windows
                    (window_start, window_end, inversion_magnitude, trigger_type, duration_seconds)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    self._window_start.isoformat() if self._window_start else None,
                    window_end.isoformat(),
                    self._window_magnitude,
                    trigger_type,
                    duration
                ))
                conn.commit()
                conn.close()

                self._in_current_window = False
                self._window_start = None
                self._window_magnitude = 0.0

        pirp_context['in_inversion_window'] = self._in_current_window
        pirp_context['inversion_magnitude'] = self._window_magnitude
        pirp_context['inversion_count'] = self._inversion_count

        return pirp_context

    def get_state(self) -> dict:
        return {
            'in_current_window': self._in_current_window,
            'window_start': self._window_start.isoformat() if self._window_start else None,
            'current_magnitude': self._window_magnitude,
            'total_inversions': self._inversion_count,
            'window_active': 'open' if self._in_current_window else 'closed'
        }
