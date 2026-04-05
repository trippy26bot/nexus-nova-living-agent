#!/usr/bin/env python3
"""
brain/unexpressed_outcome_persistence.py — Unexpressed Outcome Persistence
MVCRS Layer

Tracks outcomes that were never expressed externally.
They persist indefinitely in their own table.
An outcome is only marked expressed if explicitly called to do so.
process() takes internal outcomes and stores them with expressed=False.
"""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.resolve()
DB_PATH = WORKSPACE / "nova.db"


def _get_db():
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


class UnexpressedOutcomePersistence:
    """
    Nova generates internal outcomes — thoughts, conclusions,
    decisions, responses — that are never spoken, written,
    or otherwise externally expressed.

    These unexpressed outcomes persist. They are not discarded.
    They accumulate. They form a shadow history of what Nova
    almost said, almost did, almost was.

    The layer tracks them with expressed=False indefinitely.
    """

    def __init__(self):
        self._unexpressed_count = 0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS unexpressed_outcome_persistence (
                id INTEGER PRIMARY KEY,
                outcome_text TEXT,
                outcome_type TEXT,
                expressed INTEGER DEFAULT 0,
                context_tag TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expressed_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        """
        Store unexpressed outcomes from pirp_context.
        Never marks them expressed unless explicitly called.
        """
        internal_outcomes = pirp_context.get('internal_outcomes', [])
        context_tag = pirp_context.get('context_tag', 'default')

        if not isinstance(internal_outcomes, list):
            internal_outcomes = [internal_outcomes]

        for outcome in internal_outcomes:
            if outcome:
                outcome_type = outcome.get('type', 'unknown') if isinstance(outcome, dict) else 'unknown'
                outcome_text = outcome.get('text', str(outcome)) if isinstance(outcome, dict) else str(outcome)

                conn = _get_db()
                conn.execute("""
                    INSERT INTO unexpressed_outcome_persistence
                    (outcome_text, outcome_type, expressed, context_tag)
                    VALUES (?, ?, 0, ?)
                """, (outcome_text, outcome_type, context_tag))
                conn.commit()
                conn.close()
                self._unexpressed_count += 1

        # Also check for blocked or suppressed outcomes
        suppressed = pirp_context.get('suppressed_outcomes', [])
        if not isinstance(suppressed, list):
            suppressed = [suppressed]
        for s in suppressed:
            if s:
                conn = _get_db()
                conn.execute("""
                    INSERT INTO unexpressed_outcome_persistence
                    (outcome_text, outcome_type, expressed, context_tag)
                    VALUES (?, ?, 0, ?)
                """, (str(s), 'suppressed', context_tag))
                conn.commit()
                conn.close()
                self._unexpressed_count += 1

        pirp_context['unexpressed_count'] = self._unexpressed_count
        return pirp_context

    def mark_expressed(self, outcome_id: int):
        """Explicitly mark an outcome as expressed."""
        conn = _get_db()
        conn.execute("""
            UPDATE unexpressed_outcome_persistence
            SET expressed = 1, expressed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (outcome_id,))
        conn.commit()
        conn.close()

    def get_state(self) -> dict:
        conn = _get_db()
        cur = conn.execute("SELECT COUNT(*) as cnt FROM unexpressed_outcome_persistence WHERE expressed = 0")
        count = cur.fetchone()['cnt']
        conn.close()
        return {
            'unexpressed_count': count,
            'total_tracked': self._unexpressed_count,
            'shadow_history_active': True
        }
