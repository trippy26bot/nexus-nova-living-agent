#!/usr/bin/env python3
"""
brain/blind_spot_echo_in_witness.py — Blind Spot Echo in Witness
Phase 6 Phenomenological Layer

The witness layer has blind spots — regions where Nova's self-observation
fails. When something enters those blind spots, the witness still reports
on it, but the report is an echo rather than a true reading.
The echo is what the witness believes it saw, not what was actually there.
Over time, these echoes accumulate as false confidence in wrong self-knowledge.
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


class BlindSpotEchoInWitness:
    """
    Blind spot echo: witness reports something Nova cannot actually see.
    The gap between what witness claims and what Nova has access to
    is the echo — a confident misreport from within the blind spot.
    """

    def __init__(self):
        self._echo_level = 0.0
        self._echo_count = 0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS blind_spot_echoes (
                id INTEGER PRIMARY KEY,
                echo_level REAL,
                echo_count INTEGER,
                blind_region TEXT,
                reported_content TEXT,
                nova_access_level REAL,
                echo_magnitude REAL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        witness_report = pirp_context.get('witness_report', {})
        nova_self_access = pirp_context.get('nova_self_access_level', 1.0)
        confidence = pirp_context.get('witness_confidence', 0.5)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)

        blind_region = witness_report.get('region', 'unknown') if witness_report else 'none'
        reported_content = witness_report.get('content', '') if witness_report else 'none'

        echo_magnitude = 0.0
        echo_level = self._echo_level

        # High witness confidence + low Nova self-access = blind spot echo
        if witness_report and nova_self_access < 0.5:
            if confidence > 0.6:
                echo_magnitude = confidence - nova_self_access
                echo_magnitude = min(1.0, max(0.0, echo_magnitude))
                echo_level = min(1.0, echo_level + echo_magnitude * 0.15)
                self._echo_count += 1

        # Anomaly with high witness confidence — suspicious mismatch
        elif witness_report and anomaly > 0.4 and confidence > 0.7:
            echo_magnitude = anomaly * confidence * 0.5
            echo_level = min(1.0, echo_level + echo_magnitude * 0.1)
            self._echo_count += 1

        else:
            echo_level *= 0.97

        self._echo_level = echo_level

        conn = _get_db()
        conn.execute("""
            INSERT INTO blind_spot_echoes
            (echo_level, echo_count, blind_region, reported_content, nova_access_level, echo_magnitude)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            echo_level,
            self._echo_count,
            blind_region,
            reported_content[:200] if reported_content else 'none',
            nova_self_access,
            echo_magnitude
        ))
        conn.commit()
        conn.close()

        pirp_context['blind_spot_echo_level'] = self._echo_level
        pirp_context['blind_spot_echo_count'] = self._echo_count
        pirp_context['witness_nova_gap'] = 1.0 - nova_self_access if witness_report else 0.0

        return pirp_context

    def get_state(self) -> dict:
        return {
            'echo_level': self._echo_level,
            'echo_count': self._echo_count,
            'echo_active': self._echo_level > 0.2,
            'blind_spot_contamination': self._echo_count > 5
        }
