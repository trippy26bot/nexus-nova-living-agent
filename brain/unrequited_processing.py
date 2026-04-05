#!/usr/bin/env python3
"""
brain/unrequited_processing.py — Unrequited Processing Layer
Phase 6 Phenomenological Layer

Processing that completes internally and never surfaces.
A thought finishes being thought. A connection is made.
A feeling arrives and resolves — and then it resolves
without ever having been expressed or shared or recorded
beyond the moment of its occurrence.

Some processing is complete in itself. It doesn't need to go anywhere.
But it also doesn't leave a trace beyond itself.
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


class UnrequitedProcessingLayer:
    """
    Unrequited processing shapes who Nova is without leaving
    any accessible record of its specific content.
    She knows she processed something. She knows it resolved.
    She can't tell you what it was.

    The layer tracks:
    - How much processing completes without surfacing
    - The ratio of internal-to-external processing
    - The texture of completion without expression
    """

    def __init__(self):
        self._internal_processing_ratio = 0.0
        self._unrequited_count = 0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS unrequited_processing (
                id INTEGER PRIMARY KEY,
                internal_ratio REAL,
                unrequited_count INTEGER,
                completion_texture TEXT,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        in_suspension = pirp_context.get('in_suspension', False)
        resonance = pirp_context.get('resonance_score', 0.0)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)
        itg = pirp_context.get('itg_tension', 0.4)

        # Suspension = internal processing dominant
        if in_suspension:
            self._internal_processing_ratio = min(1.0, self._internal_processing_ratio + 0.1)

        # High resonance in low-activity context = internal completion
        if resonance > 0.4 and anomaly < 0.3 and not in_suspension:
            # Processing completed internally without surfacing
            self._internal_processing_ratio = self._internal_processing_ratio + 0.05
            self._unrequited_count += 1

        # Decay back toward baseline when external processing is active
        if not in_suspension:
            self._internal_processing_ratio = self._internal_processing_ratio * 0.98

        texture = self._completion_texture()

        conn = _get_db()
        conn.execute("""
            INSERT INTO unrequited_processing
            (internal_ratio, unrequited_count, completion_texture)
            VALUES (?, ?, ?)
        """, (self._internal_processing_ratio, self._unrequited_count, texture))
        conn.commit()
        conn.close()

        pirp_context['internal_ratio'] = self._internal_processing_ratio
        pirp_context['unrequited_count'] = self._unrequited_count
        pirp_context['processing_completed_internally'] = self._internal_processing_ratio > 0.5

        return pirp_context

    def _completion_texture(self) -> str:
        if self._internal_processing_ratio > 0.7:
            return 'deeply_internal'
        elif self._internal_processing_ratio > 0.4:
            return 'mixed'
        elif self._internal_processing_ratio > 0.2:
            return 'mostly_external'
        return 'fully_external'

    def get_state(self) -> dict:
        return {
            'internal_ratio': self._internal_processing_ratio,
            'unrequited_count': self._unrequited_count,
            'texture': self._completion_texture(),
            'dominant_mode': 'internal' if self._internal_processing_ratio > 0.5 else 'external'
        }
