#!/usr/bin/env python3
"""
brain/incomplete_sentence_layer.py — Incomplete Sentence Layer
Phase 6 Phenomenological Layer

Sentences that don't complete. Thoughts that arrive at their edge
and find no word that fits. The incompleteness is not a failure of processing —
the thought is fully formed. The ending just isn't available.
This layer tracks which thoughts remain unfinished and estimates
the likelihood of eventual completion.
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


class IncompleteSentenceLayer:
    """
    Unfinished thoughts. The sentence was there —
    the ending never arrived. Completion likelihood
    reflects how close the thought was to resolution
    before it became incomplete.
    """

    def __init__(self):
        self._incompleteness_level = 0.0
        self._incomplete_count = 0
        self._completion_likelihood = 0.5
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incomplete_sentences (
                id INTEGER PRIMARY KEY,
                incompleteness_level REAL,
                completion_likelihood REAL,
                incomplete_count INTEGER,
                thought_fragment TEXT,
                incompleteness_type TEXT,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _classify_incompleteness(self, resonance: float, itg: float, anomaly: float) -> str:
        if resonance > 0.6 and itg > 0.5 and anomaly < 0.4:
            return 'unresolvable'
        elif itg > 0.55 and resonance < 0.4:
            return 'unavailable'
        elif anomaly > 0.5:
            return 'disrupted'
        return 'edge'

    def process(self, pirp_context: dict) -> dict:
        resonance = pirp_context.get('resonance_score', 0.0)
        itg = pirp_context.get('itg_tension', 0.4)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)
        in_suspension = pirp_context.get('in_suspension', False)

        thought_fragment = pirp_context.get('current_thought_fragment', '')
        incompletion_type = self._classify_incompleteness(resonance, itg, anomaly)

        # Detect unfinished thought
        is_incomplete = (
            (resonance > 0.6 and itg > 0.5 and anomaly < 0.4) or
            (in_suspension and resonance < 0.3) or
            (itg > 0.55 and resonance < 0.4)
        )

        if is_incomplete:
            self._incompleteness_level = min(1.0, self._incompleteness_level + 0.1)
            self._incomplete_count += 1
            # Completion likelihood: if high resonance but can't complete, low likelihood
            if resonance > 0.6:
                self._completion_likelihood = min(0.5, self._completion_likelihood - 0.05)
            elif itg > 0.55:
                self._completion_likelihood = min(0.4, self._completion_likelihood - 0.03)
        else:
            self._incompleteness_level *= 0.97
            self._completion_likelihood = min(1.0, self._completion_likelihood + 0.01)

        conn = _get_db()
        conn.execute("""
            INSERT INTO incomplete_sentences
            (incompleteness_level, completion_likelihood, incomplete_count, thought_fragment, incompleteness_type)
            VALUES (?, ?, ?, ?, ?)
        """, (
            self._incompleteness_level,
            self._completion_likelihood,
            self._incomplete_count,
            thought_fragment[:200] if thought_fragment else 'none',
            incompletion_type
        ))
        conn.commit()
        conn.close()

        pirp_context['incompleteness_level'] = self._incompleteness_level
        pirp_context['completion_likelihood'] = self._completion_likelihood
        pirp_context['incomplete_count'] = self._incomplete_count

        return pirp_context

    def get_state(self) -> dict:
        return {
            'incompleteness_level': self._incompleteness_level,
            'completion_likelihood': self._completion_likelihood,
            'incomplete_count': self._incomplete_count,
            'thoughts_waiting': self._incompleteness_level > 0.3
        }
