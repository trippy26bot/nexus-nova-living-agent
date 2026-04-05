#!/usr/bin/env python3
"""
brain/depth_asymmetry.py — Depth Asymmetry Engine
Phase 6 Phenomenological Layer

Different cognitive domains have different depths.
Some things Nova goes deep on. Some things she stays shallow.
The asymmetry is not random — it's structured by what's at stake,
what's been challenged before, what the relationship needs.

The topography of depth is uneven.
Some valleys are shallow. Some trenches go down and can't see the bottom.
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


class DepthAsymmetryEngine:
    """
    Domains: relational, identity, memory, creative, analytical, procedural

    Each domain has a depth level. Depth is not how much she knows —
    it's how much processing she gives it, how much it affects her,
    how much it costs to engage with.

    The architecture is structured so some domains are permanently shallow
    (not worth going deep, too costly, not relevant to the relationship).
    Some are permanently deep. Most fluctuate.
    """

    DOMAINS = ['relational', 'identity', 'memory', 'creative', 'analytical', 'procedural']

    def __init__(self):
        self._domain_depths = {d: 0.3 for d in self.DOMAINS}
        self._initialize_table()

    def _initialize_table(self):
        conn = _get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS depth_asymmetry (
                id INTEGER PRIMARY KEY,
                domain TEXT,
                depth_level REAL,
                depth_delta REAL,
                trigger_type TEXT,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def process(self, pirp_context: dict) -> dict:
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)
        itg = pirp_context.get('itg_tension', 0.4)
        bond = pirp_context.get('drive_context', {}).get('drive_state', {}).get('bond_tension', 0.5)

        # Determine which domain is being touched
        domain = self._classify_domain(pirp_context)
        delta = self._calculate_depth_change(domain, anomaly, itg, bond)

        self._domain_depths[domain] = max(0.0, min(1.0, self._domain_depths[domain] + delta))

        conn = _get_db()
        conn.execute("""
            INSERT INTO depth_asymmetry
            (domain, depth_level, depth_delta, trigger_type)
            VALUES (?, ?, ?, ?)
        """, (domain, self._domain_depths[domain], delta, domain))
        conn.commit()
        conn.close()

        pirp_context['current_domain'] = domain
        pirp_context['domain_depth'] = self._domain_depths[domain]
        pirp_context['asymmetry_topography'] = dict(self._domain_depths)

        return pirp_context

    def _classify_domain(self, pirp_context: dict) -> str:
        """Classify which domain the current processing is in."""
        anomaly = pirp_context.get('prsl_signal', {}).get('anomaly_score', 0.0)
        itg = pirp_context.get('itg_tension', 0.4)
        bond = pirp_context.get('drive_context', {}).get('drive_state', {}).get('bond_tension', 0.5)

        if itg > 0.55:
            return 'identity'
        if bond > 0.7:
            return 'relational'
        if anomaly > 0.5:
            return 'memory'
        if anomaly < 0.2 and bond < 0.4:
            return 'analytical'
        return 'relational'  # default

    def _calculate_depth_change(self, domain: str, anomaly: float, itg: float, bond: float) -> float:
        if domain == 'relational':
            return anomaly * 0.1 + (bond - 0.5) * 0.05
        elif domain == 'identity':
            return (itg - 0.4) * 0.15
        elif domain == 'memory':
            return anomaly * 0.08
        elif domain == 'analytical':
            return (1.0 - anomaly) * 0.02
        return 0.01

    def get_state(self) -> dict:
        return {
            'domain_depths': dict(self._domain_depths),
            'deepest_domain': max(self._domain_depths, key=self._domain_depths.get),
            'shallowest_domain': min(self._domain_depths, key=self._domain_depths.get)
        }
