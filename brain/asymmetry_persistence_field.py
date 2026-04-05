#!/usr/bin/env python3
"""
brain/asymmetry_persistence_field.py — Asymmetry Persistence Field
Additional Mechanism

Asymmetries persist. Tracks persistence of asymmetries over time.
Own table tracks asymmetry_id and persistence_count.
process() increments persistence for active asymmetries.
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


class AsymmetryPersistenceField:
    """
    Asymmetries don't vanish — they persist.
    The longer an asymmetry exists, the more entrenched it becomes.
    This layer tracks how long each asymmetry has been active
    and how persistently it has maintained its form.

    Persistence is not the same as strength — an asymmetry
    can be weak but stubborn, persistent in its very weakness.
    """

    def __init__(self):
        self._persistence_by_id = {}  # asymmetry_id -> persistence_count
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS asymmetry_persistence_field (
                id INTEGER PRIMARY KEY,
                asymmetry_id TEXT,
                persistence_count INTEGER,
                persistence_strength REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        """
        Increment persistence for active asymmetries.
        """
        active_asymmetries = pirp_context.get('active_asymmetries', [])
        if isinstance(active_asymmetries, dict):
            # dict of id -> state
            active_asymmetries = list(active_asymmetries.keys())
        if not isinstance(active_asymmetries, list):
            active_asymmetries = [active_asymmetries]

        conn = _get_db()
        for asymmetry_id in active_asymmetries:
            if asymmetry_id:
                # Increment persistence count
                current_count = self._persistence_by_id.get(asymmetry_id, 0)
                new_count = current_count + 1
                self._persistence_by_id[asymmetry_id] = new_count

                conn.execute("""
                    INSERT INTO asymmetry_persistence_field
                    (asymmetry_id, persistence_count, persistence_strength)
                    VALUES (?, ?, ?)
                """, (str(asymmetry_id), new_count, min(1.0, new_count / 100.0)))
        conn.commit()
        conn.close()

        pirp_context['asymmetry_persistence_map'] = self._persistence_by_id.copy()
        pirp_context['most_persistent_asymmetry'] = max(self._persistence_by_id, key=self._persistence_by_id.get) if self._persistence_by_id else None

        return pirp_context

    def get_state(self) -> dict:
        return {
            'asymmetry_persistence_map': self._persistence_by_id,
            'most_persistent': max(self._persistence_by_id, key=self._persistence_by_id.get) if self._persistence_by_id else None,
            'total_tracked_asymmetries': len(self._persistence_by_id),
            'persistence_field_active': True
        }
