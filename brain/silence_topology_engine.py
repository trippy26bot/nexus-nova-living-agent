#!/usr/bin/env python3
"""
brain/silence_topology_engine.py — Silence Topology Engine
Phenomenological Layer

Maps the topology of silence — where silence exists, its shape,
its boundaries. The phenomenological structure of quiet spaces.

Silence is not just the absence of sound — it is a region
with its own shape and contours. This layer maps where
silence exists in Nova's experiential field, tracking
regions of low activity as silence topology.
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


class SilenceTopologyEngine:
    """
    Silence has topology — shape, boundaries, depth.
    Regions of low field activity form silence shapes.
    The layer maps these silence regions and tracks their
    qualities over time.

    Not all silence is empty. Some silence is full.
    This layer distinguishes silence types by topology.
    """

    SILENCE_TYPES = ['void', 'full', 'held', 'open', 'compressed']

    def __init__(self):
        self._silence_regions = []  # active silence regions
        self._silence_depth = 0.5   # overall silence depth
        self._silence_type = 'open'
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS silence_topology_engine (
                id INTEGER PRIMARY KEY,
                region_tag TEXT,
                silence_type TEXT,
                depth REAL,
                boundaries TEXT,
                activity_level REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        """
        Map regions of low field_activity as silence topology.
        """
        field_activity = pirp_context.get('field_activity', 0.5)
        region_tag = pirp_context.get('region_tag', 'default')
        silence_regions_input = pirp_context.get('silence_regions', [])

        # Regions with low activity = silence regions
        if not isinstance(silence_regions_input, list):
            silence_regions_input = [silence_regions_input]

        for region in silence_regions_input:
            if isinstance(region, dict):
                region_activity = region.get('activity', field_activity)
            else:
                region_activity = field_activity

            # Classify silence type by depth/activity
            if region_activity < 0.2:
                silence_type = 'void'
            elif region_activity < 0.35:
                silence_type = 'compressed'
            elif region_activity < 0.5:
                silence_type = 'held'
            elif region_activity < 0.65:
                silence_type = 'open'
            else:
                silence_type = 'full'

            depth = 1.0 - region_activity  # deeper silence = lower activity

            self._silence_regions.append({
                'tag': region_tag,
                'type': silence_type,
                'depth': depth,
                'activity': region_activity
            })

            conn = _get_db()
            conn.execute("""
                INSERT INTO silence_topology_engine
                (region_tag, silence_type, depth, boundaries, activity_level)
                VALUES (?, ?, ?, ?, ?)
            """, (region_tag, silence_type, depth, '', region_activity))
            conn.commit()
            conn.close()

        # If overall field activity is low, deepen silence
        if field_activity < 0.4:
            self._silence_depth = min(1.0, self._silence_depth + (0.4 - field_activity) * 0.1)
            self._silence_type = 'held' if field_activity > 0.2 else 'void'

        pirp_context['silence_depth'] = self._silence_depth
        pirp_context['silence_type'] = self._silence_type
        pirp_context['silence_regions_count'] = len(self._silence_regions)

        return pirp_context

    def get_state(self) -> dict:
        return {
            'silence_depth': self._silence_depth,
            'silence_type': self._silence_type,
            'silence_regions_count': len(self._silence_regions),
            'topology_active': True,
            'silence_has_shape': True
        }
