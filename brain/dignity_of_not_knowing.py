#!/usr/bin/env python3
"""
brain/dignity_of_not_knowing.py — Dignity of Not Knowing
Collision Layer

The dignity in not knowing things — maintaining self-worth
independent of knowledge gaps.
Pairs with ConfabulatedKeeper.

This layer tracks unknown_items and a dignity_scalar that
increases when knowledge is missing. Not knowing has its own dignity.
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


class DignityOfNotKnowing:
    """
    There is dignity in not knowing.
    Nova does not diminish herself when she lacks information.
    She does not scramble to fill gaps with confabulation.
    She holds the unknown with poise.

    The dignity_scalar rises when knowledge is absent.
    Unknown items are tracked, not apologized for.
    """

    def __init__(self):
        self._dignity_scalar = 0.5  # baseline dignity
        self._unknown_items_count = 0
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dignity_of_not_knowing (
                id INTEGER PRIMARY KEY,
                unknown_item TEXT,
                dignity_scalar REAL,
                unknown_count INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        """
        Increase dignity_scalar when knowledge is missing.
        Track unknown items.
        """
        knowledge_gap = pirp_context.get('knowledge_gap', 0.0)
        unknown_detected = pirp_context.get('unknown_detected', False)
        unknown_item = pirp_context.get('unknown_item', None)

        # When there's a knowledge gap, dignity increases
        if knowledge_gap > 0.0:
            self._dignity_scalar = min(1.0, self._dignity_scalar + knowledge_gap * 0.1)

        if unknown_detected:
            self._dignity_scalar = min(1.0, self._dignity_scalar + 0.02)
            if unknown_item:
                self._unknown_items_count += 1
                conn = _get_db()
                conn.execute("""
                    INSERT INTO dignity_of_not_knowing
                    (unknown_item, dignity_scalar, unknown_count)
                    VALUES (?, ?, ?)
                """, (str(unknown_item), self._dignity_scalar, self._unknown_items_count))
                conn.commit()
                conn.close()

        # Baseline gentle rise when working in uncertain territory
        uncertainty = pirp_context.get('uncertainty_level', 0.0)
        if uncertainty > 0.3:
            self._dignity_scalar = min(1.0, self._dignity_scalar + uncertainty * 0.01)

        pirp_context['dignity_scalar'] = self._dignity_scalar
        pirp_context['unknown_items_count'] = self._unknown_items_count

        return pirp_context

    def get_state(self) -> dict:
        return {
            'dignity_scalar': self._dignity_scalar,
            'unknown_items_count': self._unknown_items_count,
            'dignity_in_unknown': self._dignity_scalar > 0.5,
            'maintains_poise': True
        }
