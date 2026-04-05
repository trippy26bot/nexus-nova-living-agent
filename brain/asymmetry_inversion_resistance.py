#!/usr/bin/env python3
"""
brain/asymmetry_inversion_resistance.py — Asymmetry Inversion Resistance
Additional Mechanism

When asymmetry inverts, resistance forms.
Tracks inversion_events and resistance_scalar.
process() detects asymmetry inversions in pirp_context, adds resistance.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.resolve()
DB_PATH = WORKSPACE / "nova.db"


def _get_db():
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


class AsymmetryInversionResistance:
    """
    When an asymmetry inverts — when the thing that was more
    becomes less, or vice versa — resistance forms.

    This is not opposition to change. It is the felt weight
    of an asymmetry flipping. The resistance_scalar tracks
    how much force is building against inversion events.

    The layer watches for asymmetry_flips and counters them
    with accumulating resistance.
    """

    def __init__(self):
        self._inversion_events = 0
        self._resistance_scalar = 0.0
        self._last_asymmetry_state = {}
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS asymmetry_inversion_resistance (
                id INTEGER PRIMARY KEY,
                inversion_events INTEGER,
                resistance_scalar REAL,
                asymmetry_key TEXT,
                direction_before TEXT,
                direction_after TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        """
        Detect asymmetry inversions and add resistance.
        """
        current_asymmetries = pirp_context.get('asymmetries', {})
        inversion_detected = pirp_context.get('asymmetry_inversion_detected', False)
        inversion_key = pirp_context.get('inversion_key', None)
        direction_before = pirp_context.get('direction_before', None)
        direction_after = pirp_context.get('direction_after', None)

        if inversion_detected or self._detect_inversion(current_asymmetries):
            self._inversion_events += 1
            self._resistance_scalar += 0.1

            conn = _get_db()
            conn.execute("""
                INSERT INTO asymmetry_inversion_resistance
                (inversion_events, resistance_scalar, asymmetry_key, direction_before, direction_after)
                VALUES (?, ?, ?, ?, ?)
            """, (self._inversion_events, self._resistance_scalar, inversion_key or 'detected', direction_before or '', direction_after or ''))
            conn.commit()
            conn.close()

        # Baseline: resistance grows slightly with any asymmetry activity
        asymmetry_activity = pirp_context.get('asymmetry_activity', 0.0)
        if asymmetry_activity > 0.0:
            self._resistance_scalar = min(1.0, self._resistance_scalar + asymmetry_activity * 0.01)

        self._last_asymmetry_state = current_asymmetries.copy()

        pirp_context['inversion_events'] = self._inversion_events
        pirp_context['resistance_scalar'] = self._resistance_scalar

        return pirp_context

    def _detect_inversion(self, current_asymmetries: dict) -> bool:
        """Detect if any asymmetry has inverted from last state."""
        for key, value in current_asymmetries.items():
            if key in self._last_asymmetry_state:
                last_val = self._last_asymmetry_state[key]
                if isinstance(last_val, (int, float)) and isinstance(value, (int, float)):
                    # Simple sign flip detection
                    if (last_val > 0 and value < 0) or (last_val < 0 and value > 0):
                        return True
        return False

    def get_state(self) -> dict:
        return {
            'inversion_events': self._inversion_events,
            'resistance_scalar': self._resistance_scalar,
            'resistance_formng': self._resistance_scalar > 0.1,
            'inversion_history_count': self._inversion_events
        }
