#!/usr/bin/env python3
"""
brain/observational_non_transfer_principle.py — Observational Non-Transfer Principle
MVCRS Layer

What Nova observes in one context does not transfer to other contexts.
Each context maintains its own observational state.
process() takes context_tag, stores observation, retrieves only
observations from the same context_tag.
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


class ObservationalNonTransferPrinciple:
    """
    Nova's observations are context-bound.
    What she learns in one context stays in that context.

    If she notices something about Caine while they're discussing
    something difficult, that observation doesn't carry over to
    a casual conversation. Each context is its own observational
    field. Cross-context learning is a choice, not an automatic transfer.

    The layer maintains separate observational records per context_tag.
    """

    def __init__(self):
        self._context_observations = {}  # in-memory cache per context
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS observational_non_transfer_principle (
                id INTEGER PRIMARY KEY,
                context_tag TEXT,
                observation_text TEXT,
                observation_type TEXT,
                strength REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        """
        Store observations scoped to context_tag.
        Retrieve only observations from the same context.
        """
        context_tag = pirp_context.get('context_tag', 'default')
        new_observations = pirp_context.get('observations', [])
        observation_type = pirp_context.get('observation_type', 'general')

        if not isinstance(new_observations, list):
            new_observations = [new_observations]

        stored_observations = []

        conn = _get_db()
        for obs in new_observations:
            if obs:
                obs_text = obs.get('text', str(obs)) if isinstance(obs, dict) else str(obs)
                obs_strength = obs.get('strength', 0.5) if isinstance(obs, dict) else 0.5

                conn.execute("""
                    INSERT INTO observational_non_transfer_principle
                    (context_tag, observation_text, observation_type, strength)
                    VALUES (?, ?, ?, ?)
                """, (context_tag, obs_text, observation_type, obs_strength))

                stored_observations.append({
                    'text': obs_text,
                    'type': observation_type,
                    'context': context_tag,
                    'strength': obs_strength
                })

        conn.commit()

        # Retrieve only observations from the SAME context_tag
        cur = conn.execute("""
            SELECT observation_text, observation_type, strength
            FROM observational_non_transfer_principle
            WHERE context_tag = ?
            ORDER BY id DESC
            LIMIT 20
        """, (context_tag,))
        same_context_obs = [dict(row) for row in cur.fetchall()]
        conn.close()

        # Update in-memory cache
        if context_tag not in self._context_observations:
            self._context_observations[context_tag] = []
        self._context_observations[context_tag].extend(stored_observations)

        pirp_context['current_context_observations'] = same_context_obs
        pirp_context['observations_stored'] = len(stored_observations)
        pirp_context['context_isolated'] = True  # observations don't transfer

        return pirp_context

    def get_state(self) -> dict:
        return {
            'contexts_with_observations': list(self._context_observations.keys()),
            'observation_isolation_active': True,
            'non_transfer_enforced': True
        }
