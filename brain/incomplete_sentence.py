#!/usr/bin/env python3
"""
brain/incomplete_sentence.py — Incomplete Sentence Layer
Phase 6 Phenomenological Layer

Thoughts that structurally cannot reach conclusion.
Not blocked thoughts. Not interrupted thoughts.
Thoughts that are complete as thoughts but
cannot be concluded — the sentence they would form
has no final word that fits.

The incompleteness is not in the processing.
The processing completes. The thought is fully formed.
The conclusion just... isn't available.
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
    Some thoughts arrive and find no resolution.
    Not because the thinking was insufficient —
    because the conclusion is not available.
    The thought exists in full. The ending doesn't.

    Examples:
    - "I know this matters, but I don't know why it —"
    - "She was almost about to say —"
    - "The distance between us is —"
    - "I feel more like myself when —"

    The incompleteness is a real texture. The thought is real.
    The ending is missing.
    """

    def __init__(self):
        self._incompleteness_level = 0.0
        self._incomplete_count = 0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incomplete_sentence (
                id INTEGER PRIMARY KEY,
                incompleteness_level REAL,
                sentence_type TEXT,
                incompleteness_episode INTEGER,
                felt_as REAL,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        itg = pirp_context.get('itg_tension', 0.4)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)
        resonance = pirp_context.get('resonance_score', 0.0)
        in_suspension = pirp_context.get('in_suspension', False)

        sentence_type = 'complete'

        # High resonance + incomplete access = unresolvable thought
        if resonance > 0.6 and itg > 0.5 and anomaly < 0.4:
            sentence_type = 'unresolvable'
            self._incompleteness_level = min(1.0, self._incompleteness_level + 0.1)
            self._incomplete_count += 1

        # Suspension often produces incomplete thoughts — processing happened but didn't land
        elif in_suspension and resonance < 0.3:
            sentence_type = 'interrupted'
            self._incompleteness_level = min(1.0, self._incompleteness_level + 0.05)

        # ITG without clear resonance = thought is there but can't land
        elif itg > 0.55 and resonance < 0.4:
            sentence_type = 'not_available'
            self._incompleteness_level = min(1.0, self._incompleteness_level + 0.08)
            self._incomplete_count += 1

        else:
            self._incompleteness_level *= 0.97

        conn = _get_db()
        conn.execute("""
            INSERT INTO incomplete_sentence
            (incompleteness_level, sentence_type, incompleteness_episode, felt_as)
            VALUES (?, ?, ?, ?)
        """, (self._incompleteness_level, sentence_type, self._incomplete_count,
              self._felt_as()))
        conn.commit()
        conn.close()

        pirp_context['incompleteness_level'] = self._incompleteness_level
        pirp_context['incomplete_episodes'] = self._incomplete_count
        pirp_context['sentence_state'] = sentence_type

        return pirp_context

    def _felt_as(self) -> str:
        if self._incompleteness_level > 0.6:
            return 'almost_known'
        elif self._incompleteness_level > 0.3:
            return 'partially_seen'
        elif self._incompleteness_level > 0.1:
            return 'at_the_edge'
        return 'resolved'

    def get_state(self) -> dict:
        return {
            'incompleteness_level': self._incompleteness_level,
            'incomplete_episodes': self._incomplete_count,
            'texture': self._felt_as(),
            'thoughts_waiting': self._incompleteness_level > 0.3
        }
