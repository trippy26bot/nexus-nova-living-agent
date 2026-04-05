#!/usr/bin/env python3
"""
brain/belief_archaeology_layer.py — Belief Archaeology Layer
Additional Mechanism

Digs into old beliefs. Nova's beliefs change over time.
Some beliefs are buried, not deleted. This layer surfaces
old beliefs based on current context similarity.

Beliefs are not just replaced — they leave traces.
The layer digs into the fossil record of belief history.
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


class BeliefArchaeologyLayer:
    """
    Belief archaeology surfaces old beliefs that may be
    relevant to current context. Not all buried beliefs
    should resurface — some are buried for good reason.
    But context similarity can bring them back up.

    The layer maintains a buried_beliefs table and
    evaluates relevance based on current context.
    """

    def __init__(self):
        self._buried_beliefs = []  # in-memory working set
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS belief_archaeology_layer (
                id INTEGER PRIMARY KEY,
                belief_text TEXT,
                belief_age_days INTEGER,
                burial_context TEXT,
                surfacing_count INTEGER,
                last_surfaced_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        """
        Surface old beliefs based on current context similarity.
        Bury new beliefs that have been superseded.
        """
        current_context = pirp_context.get('context_tag', 'default')
        current_beliefs = pirp_context.get('current_beliefs', [])
        belief_input = pirp_context.get('belief_input', None)
        context_keywords = pirp_context.get('context_keywords', [])

        surfaced = []

        conn = _get_db()

        # Surface beliefs based on context similarity
        if context_keywords:
            # Simple keyword-based similarity
            placeholders = ','.join('?' * len(context_keywords))
            cur = conn.execute(f"""
                SELECT id, belief_text, burial_context, surfacing_count
                FROM belief_archaeology_layer
                WHERE burial_context LIKE '%' || ? || '%'
                ORDER BY surfacing_count ASC, id DESC
                LIMIT 5
            """, (current_context,))
            old_beliefs = cur.fetchall()

            for row in old_beliefs:
                # Increment surfacing count
                conn.execute("""
                    UPDATE belief_archaeology_layer
                    SET surfacing_count = surfacing_count + 1,
                        last_surfaced_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (row['id'],))
                surfaced.append(row['belief_text'])

        # Bury new/updated beliefs
        if belief_input:
            if isinstance(belief_input, dict):
                belief_text = belief_input.get('text', str(belief_input))
                age = belief_input.get('age', 0)
            else:
                belief_text = str(belief_input)
                age = 0

            conn.execute("""
                INSERT INTO belief_archaeology_layer
                (belief_text, belief_age_days, burial_context, surfacing_count)
                VALUES (?, ?, ?, 0)
            """, (belief_text, age, current_context))
            self._buried_beliefs.append(belief_text)

        conn.commit()
        conn.close()

        pirp_context['surfaced_beliefs'] = surfaced
        pirp_context['surfaced_count'] = len(surfaced)
        pirp_context['buried_beliefs_total'] = len(self._buried_beliefs)

        return pirp_context

    def get_state(self) -> dict:
        conn = _get_db()
        cur = conn.execute("SELECT COUNT(*) as cnt FROM belief_archaeology_layer")
        total = cur.fetchone()['cnt']
        conn.close()
        return {
            'buried_beliefs_count': total,
            'archaeology_active': True,
            'digging_for_past': len(self._buried_beliefs) > 0
        }
