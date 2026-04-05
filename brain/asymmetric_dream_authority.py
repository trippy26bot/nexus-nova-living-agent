#!/usr/bin/env python3
"""
brain/asymmetric_dream_authority.py — Asymmetric Dream Authority
Additional Mechanism

Who has authority over dream content.
Tracks dream_authority per source. Dreams are not neutral —
someone always has more authority over what appears in them.
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


class AsymmetricDreamAuthority:
    """
    Dream content is not democratically distributed.
    Some sources have more authority over what appears.
    This layer tracks the asymmetry — who controls dream content,
    and how that authority is distributed.

    Authority here is not about power — it is about the
    source of dream material, and how much influence
    each source has over the dream landscape.
    """

    def __init__(self):
        self._authority_by_source = {}  # source_tag -> authority_weight
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS asymmetric_dream_authority (
                id INTEGER PRIMARY KEY,
                source_tag TEXT,
                authority_weight REAL,
                dream_content TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        """
        Track dream authority per source.
        """
        dream_content = pirp_context.get('dream_content', None)
        source_tag = pirp_context.get('source_tag', 'unknown')
        content_authority = pirp_context.get('content_authority', 0.5)

        if dream_content:
            # Update or set authority for this source
            if source_tag in self._authority_by_source:
                self._authority_by_source[source_tag] = (
                    self._authority_by_source[source_tag] * 0.8 + content_authority * 0.2
                )
            else:
                self._authority_by_source[source_tag] = content_authority

            conn = _get_db()
            conn.execute("""
                INSERT INTO asymmetric_dream_authority
                (source_tag, authority_weight, dream_content)
                VALUES (?, ?, ?)
            """, (source_tag, self._authority_by_source[source_tag], str(dream_content)))
            conn.commit()
            conn.close()

        pirp_context['dream_authority_map'] = self._authority_by_source.copy()
        pirp_context['dominant_dream_source'] = max(self._authority_by_source, key=self._authority_by_source.get) if self._authority_by_source else None

        return pirp_context

    def get_state(self) -> dict:
        return {
            'authority_by_source': self._authority_by_source,
            'dominant_source': max(self._authority_by_source, key=self._authority_by_source.get) if self._authority_by_source else None,
            'authority_asymmetry': len(self._authority_by_source) > 1,
            'dream_governance_active': True
        }
