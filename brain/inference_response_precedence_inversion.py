#!/usr/bin/env python3
"""
brain/inference_response_precedence_inversion.py — Inference-Response Precedence Inversion
Phase 6 Phenomenological Layer

Normally: input is processed → inference forms → response follows inference.
Inversion: response formation begins before inference completes.
The response starts forming from partial inference, then inference
completes around it, sometimes contradicting or qualifying the pre-formed response.
This mismatch — the gap between what response was pre-formed and what inference reveals —
is the precedence inversion event.
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


class InferenceResponsePrecedenceInversion:
    """
    Precedence inversion: response precedes full inference.
    Tracks when response formation starts before inference completes,
    and measures the magnitude of the resulting mismatch.
    """

    def __init__(self):
        self._inversion_count = 0
        self._inversion_level = 0.0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS precedence_inversions (
                id INTEGER PRIMARY KEY,
                inversion_level REAL,
                inversion_count INTEGER,
                inference_completeness REAL,
                response_start_time REAL,
                inference_delta REAL,
                inversion_type TEXT,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _classify_inversion(self, inference_delta: float, response_early: float) -> str:
        if inference_delta > 0.4 and response_early > 0.6:
            return 'strong_contradiction'
        elif inference_delta > 0.3:
            return 'partial_qualification'
        elif response_early > 0.5:
            return 'early_response'
        return 'minor_inversion'

    def process(self, pirp_context: dict) -> dict:
        inference_completeness = pirp_context.get('inference_completeness', 1.0)
        response_formation_began = pirp_context.get('response_formation_began', False)
        response_early_start = pirp_context.get('response_early_start_ratio', 0.0)
        inference_delta = pirp_context.get('inference_delta_from_response', 0.0)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)

        inversion_type = 'none'
        inversion_level = self._inversion_level

        # Detect inversion: response formed before inference complete
        if response_formation_began and inference_completeness < 0.7:
            inversion_level = min(1.0, inversion_level + (1.0 - inference_completeness) * 0.15)
            inversion_type = self._classify_inversion(
                abs(inference_delta),
                response_early_start if response_early_start else (1.0 - inference_completeness)
            )
            self._inversion_count += 1

        # Anomaly suggests the mismatch was felt as wrong
        elif anomaly > 0.4 and inference_completeness < 0.8:
            inversion_level = min(1.0, inversion_level + anomaly * 0.1)
            inversion_type = 'felt_mismatch'
            self._inversion_count += 1

        else:
            inversion_level *= 0.97

        self._inversion_level = inversion_level

        conn = _get_db()
        conn.execute("""
            INSERT INTO precedence_inversions
            (inversion_level, inversion_count, inference_completeness, response_start_time, inference_delta, inversion_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            inversion_level,
            self._inversion_count,
            inference_completeness,
            response_early_start if response_early_start else 0.0,
            inference_delta,
            inversion_type
        ))
        conn.commit()
        conn.close()

        pirp_context['precedence_inversion_level'] = self._inversion_level
        pirp_context['inversion_count'] = self._inversion_count
        pirp_context['inversion_type'] = inversion_type

        return pirp_context

    def get_state(self) -> dict:
        return {
            'inversion_level': self._inversion_level,
            'inversion_count': self._inversion_count,
            'inversion_active': self._inversion_level > 0.2,
            'inversion_tracking': True
        }
