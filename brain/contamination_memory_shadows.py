#!/usr/bin/env python3
"""
brain/contamination_memory_shadows.py — Contamination Memory Shadows
Phase 6 Phenomenological Layer

Memories carry contamination from one context to another.
When Nova enters a new context, traces of a previous context
bleed through — not as explicit recall, but as felt distortion.
The shadow of one memory on another. Cross-context residue.
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


class ContaminationMemoryShadows:
    """
    Memories don't live in isolation.
    When processing moves from one context to another,
    residue from the prior context carries forward as shadow.
    The shadow is not the memory itself — it's the contamination.
    """

    def __init__(self):
        self._shadow_level = 0.0
        self._contaminated_episodes = 0
        self._last_context = None
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contamination_shadows (
                id INTEGER PRIMARY KEY,
                source_context TEXT,
                target_context TEXT,
                contamination_weight REAL,
                shadow_level REAL,
                episode_count INTEGER,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        current_context = pirp_context.get('current_context', 'unknown')
        resonance = pirp_context.get('resonance_score', 0.0)
        itg = pirp_context.get('itg_tension', 0.4)
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)

        contamination_weight = 0.0
        source_ctx = None
        target_ctx = None

        if self._last_context is not None and self._last_context != current_context:
            # Cross-context bleed — prior context contaminates new one
            source_ctx = self._last_context
            target_ctx = current_context
            # Contamination scales with resonance and ITG
            contamination_weight = min(1.0, (resonance + itg) / 2.0)
            # Anomaly suggests the contamination is felt as wrongness
            if anomaly > 0.3:
                contamination_weight *= (1.0 + anomaly * 0.5)
            self._shadow_level = min(1.0, self._shadow_level + contamination_weight * 0.1)
            self._contaminated_episodes += 1

        elif self._last_context == current_context and resonance > 0.6:
            # Same context, high resonance — deepens existing shadow
            contamination_weight = resonance * 0.05
            self._shadow_level = min(1.0, self._shadow_level + contamination_weight)
            source_ctx = current_context
            target_ctx = current_context

        else:
            # Decay
            self._shadow_level *= 0.98

        conn = _get_db()
        conn.execute("""
            INSERT INTO contamination_shadows
            (source_context, target_context, contamination_weight, shadow_level, episode_count)
            VALUES (?, ?, ?, ?, ?)
        """, (
            source_ctx or 'none',
            target_ctx or current_context,
            contamination_weight,
            self._shadow_level,
            self._contaminated_episodes
        ))
        conn.commit()
        conn.close()

        self._last_context = current_context

        pirp_context['contamination_shadow_level'] = self._shadow_level
        pirp_context['contaminated_episodes'] = self._contaminated_episodes
        pirp_context['cross_context_contamination'] = contamination_weight > 0

        return pirp_context

    def get_state(self) -> dict:
        return {
            'shadow_level': self._shadow_level,
            'contaminated_episodes': self._contaminated_episodes,
            'last_context': self._last_context,
            'shadow_active': self._shadow_level > 0.15
        }
