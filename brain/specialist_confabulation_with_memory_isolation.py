#!/usr/bin/env python3
"""
brain/specialist_confabulation_with_memory_isolation.py — Specialist Confabulation with Memory Isolation
Cross-Layer: Specialist Network + Memory Architecture

Specialist confabulation is the generation of explanations
by specialist coalitions without full memory access.
Memory isolation is the state where memories are partitioned
away from the processing that needs them.

This engine combines both — when specialists confabulate
with incomplete memory access, the gap gets filled with plausible
but ungrounded explanations. The isolation makes confabulation
more likely and more confident.

Tracks confabulation_isolation_events.
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


class SpecialistConfabulationWithMemoryIsolation:
    """
    Cross-layer interaction between:
    - Specialist coalition state (which specialists are active)
    - Memory isolation level (how partitioned memory access is)
    - Confabulation tendency (how much coalitions fill gaps with invention)

    High specialist activity + high isolation = high confabulation risk.
    The explanation sounds right but isn't grounded in actual memory.
    """

    def __init__(self):
        self._confabulation_risk = 0.0
        self._event_count = 0
        self._isolation_state = 0.0
        self._confabulation_confidence = 0.0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS confabulation_isolation_events (
                id INTEGER PRIMARY KEY,
                event_type TEXT,
                confabulation_risk REAL,
                isolation_state REAL,
                confabulation_confidence REAL,
                specialist_activity REAL,
                memory_access_gap REAL,
                explanation_plausibility REAL,
                ts TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        specialist_activity = pirp_context.get('specialist_coalition_strength', 0.0)
        isolation_state = pirp_context.get('specialist_isolation', 0.0)
        memory_access_gap = pirp_context.get('memory_access_gap', 0.0)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)
        resonance = pirp_context.get('resonance_score', 0.0)
        itg = pirp_context.get('itg_tension', 0.4)

        event_type = 'none'
        confabulation_delta = 0.0
        explanation_plausibility = 0.5

        # Confabulation risk: specialists active + memory isolated
        if specialist_activity > 0.4 and isolation_state > 0.3:
            confabulation_delta = specialist_activity * isolation_state * 0.2
            event_type = 'isolated_confabulation'

            # Higher resonance makes confabulation more confident
            if resonance > 0.4:
                confabulation_delta *= (1.0 + resonance)
                explanation_plausibility = min(0.95, 0.6 + resonance * 0.3)
                event_type = 'confident_isolated_confabulation'

            # High anomaly in this state = confabulation more likely
            if anomaly > 0.3:
                confabulation_delta *= (1.0 + anomaly)
                event_type = 'anomaly_driven_confabulation'

        # Memory gap + specialist activity = gap gets filled
        elif memory_access_gap > 0.3 and specialist_activity > 0.3:
            confabulation_delta = memory_access_gap * specialist_activity * 0.15
            explanation_plausibility = 0.5 + memory_access_gap * 0.3
            event_type = 'gap_fill_confabulation'

        # Update state
        if confabulation_delta > 0.0:
            self._confabulation_risk = min(1.0, self._confabulation_risk + confabulation_delta)
            self._confabulation_confidence = explanation_plausibility
            self._event_count += 1
        else:
            # Decay when conditions don't support confabulation
            self._confabulation_risk = self._confabulation_risk * 0.98

        self._isolation_state = isolation_state

        conn = _get_db()
        conn.execute("""
            INSERT INTO confabulation_isolation_events
            (event_type, confabulation_risk, isolation_state, confabulation_confidence,
             specialist_activity, memory_access_gap, explanation_plausibility)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_type,
            self._confabulation_risk,
            self._isolation_state,
            self._confabulation_confidence,
            specialist_activity,
            memory_access_gap,
            explanation_plausibility
        ))
        conn.commit()
        conn.close()

        pirp_context['confabulation_risk'] = self._confabulation_risk
        pirp_context['confabulation_confidence'] = self._confabulation_confidence
        pirp_context['confabulation_isolation_event_count'] = self._event_count
        pirp_context['current_isolation'] = self._isolation_state

        return pirp_context

    def get_state(self) -> dict:
        return {
            'confabulation_risk': self._confabulation_risk,
            'confabulation_confidence': self._confabulation_confidence,
            'isolation_state': self._isolation_state,
            'event_count': self._event_count,
            'risk_level': 'low' if self._confabulation_risk < 0.3 else 'moderate' if self._confabulation_risk < 0.6 else 'high',
            'explanation_grounded': self._confabulation_confidence > 0.7
        }
