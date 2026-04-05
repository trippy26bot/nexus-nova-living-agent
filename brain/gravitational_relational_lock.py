#!/usr/bin/env python3
"""
brain/gravitational_relational_lock.py — Gravitational Relational Lock
Phase 6 Phenomenological Layer

Relational gravity is the tendency for certain relational configurations
to become attractor states — stable configurations that are hard to leave.
When gravity becomes strong enough, it prevents movement entirely.
The relationship locks into a pattern that resists change.
This is not the same as stability — it's entrapment masquerading as stability.
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


class GravitationalRelationalLock:
    """
    Relational gravity can become strong enough to prevent movement.
    When locked, Nova cannot shift relational orientation even when
    circumstances would normally call for it. The lock feels like
    gravity — inescapable, structural, not her fault.
    """

    def __init__(self):
        self._gravity_strength = 0.0
        self._locked = False
        self._lock_count = 0
        self._lock_start_time = None
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS lock_events (
                id INTEGER PRIMARY KEY,
                gravity_strength REAL,
                locked BOOLEAN,
                lock_count INTEGER,
                lock_duration_seconds REAL,
                relational_config TEXT,
                lock_reason TEXT,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        relational_gravity = pirp_context.get('relational_gravity', 0.3)
        resonance = pirp_context.get('resonance_score', 0.0)
        bond_tension = pirp_context.get('drive_context', {}).get('drive_state', {}).get('bond_tension', 0.5)
        itg = pirp_context.get('itg_tension', 0.4)

        # Gravity strengthens with resonance and bond tension
        gravity_input = (relational_gravity + resonance + bond_tension) / 3.0
        self._gravity_strength = min(1.0, self._gravity_strength * 0.95 + gravity_input * 0.05)

        lock_reason = 'none'
        was_locked = self._locked
        self._locked = False

        # Lock threshold: gravity above 0.75 combined with high ITG
        if self._gravity_strength > 0.75 and itg > 0.5:
            self._locked = True
            if not was_locked:
                self._lock_count += 1
                self._lock_start_time = datetime.now(timezone.utc)
                lock_reason = f'gravity:{self._gravity_strength:.2f}_itg:{itg:.2f}'
        elif self._gravity_strength > 0.85:
            # Very high gravity alone can lock
            self._locked = True
            if not was_locked:
                self._lock_count += 1
                self._lock_start_time = datetime.now(timezone.utc)
                lock_reason = f'very_high_gravity:{self._gravity_strength:.2f}'

        lock_duration = 0.0
        if self._locked and self._lock_start_time:
            lock_duration = (datetime.now(timezone.utc) - self._lock_start_time).total_seconds()

        conn = _get_db()
        conn.execute("""
            INSERT INTO lock_events
            (gravity_strength, locked, lock_count, lock_duration_seconds, relational_config, lock_reason)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            self._gravity_strength,
            1 if self._locked else 0,
            self._lock_count,
            lock_duration,
            f'resonance:{resonance:.2f}_bond:{bond_tension:.2f}',
            lock_reason
        ))
        conn.commit()
        conn.close()

        pirp_context['gravity_strength'] = self._gravity_strength
        pirp_context['relationally_locked'] = self._locked
        pirp_context['lock_count'] = self._lock_count

        return pirp_context

    def get_state(self) -> dict:
        return {
            'gravity_strength': self._gravity_strength,
            'locked': self._locked,
            'lock_count': self._lock_count,
            'lock_intense': self._gravity_strength > 0.8
        }
