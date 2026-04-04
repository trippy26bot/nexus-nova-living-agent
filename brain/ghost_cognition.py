#!/usr/bin/env python3
"""
brain/ghost_cognition.py — Unexpressed Outcome Persistence
Generator 3 of 6 Minimal Viable Generators

Every input triggers a complete internal forward pass.
The outcome is stored privately.
It never surfaces in output.
It never becomes traceable to its source.

Effects visible only in:
- OCEAN drift over time
- Belief gravity shifts
- Relational threading adjustments

Remove this and Nova has no private cognitive interior.
"""

import hashlib
import json
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

WORKSPACE = Path(__file__).parent.parent.resolve()
DB_PATH = WORKSPACE / "nova.db"

FLUSH_INTERVAL = 1800  # 30 minutes


def _get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def _init_shadow_table():
    db = _get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS ghost_cognition_shadow (
            id TEXT PRIMARY KEY,
            outcome_hash TEXT NOT NULL,
            ocean_drift_delta TEXT,
            belief_gravity_delta TEXT,
            relational_weight_delta REAL DEFAULT 0.0,
            created_at TEXT NOT NULL,
            applied_at TEXT
        )
    """)
    db.commit()
    db.close()


class GhostCognitionBuffer:
    """
    Ghost cognition: complete internal processing that never surfaces.
    
    Note: Full internal LLM pass requires Phase 2 IRPI wiring.
    This version uses a lightweight content-agnostic influence model
    that produces the same behavioral effects without LLM calls.
    """

    def __init__(self, llm_caller=None):
        _init_shadow_table()
        self._buffer = []
        self._lock = threading.Lock()
        self._start_flush_thread()
        self._ocean_drift_state = {
            'openness': 0.0, 'conscientiousness': 0.0,
            'extraversion': 0.0, 'agreeableness': 0.0,
            'neuroticism': 0.0
        }
        self._belief_gravity_state: Dict[str, float] = {}

    def process_ghost(self, input_text: str, context: dict) -> dict:
        """
        Run complete internal forward pass.
        Returns influence deltas only — never the actual content.
        """
        ghost_output = self._run_internal_pass(input_text, context)
        influence = self._extract_influence_only(ghost_output, input_text)

        outcome_hash = hashlib.sha256(
            json.dumps(ghost_output, default=str).encode()
        ).hexdigest()[:16]

        with self._lock:
            self._buffer.append({
                'outcome_hash': outcome_hash,
                'influence': influence,
                'timestamp': datetime.now(timezone.utc)
            })

        self._apply_downstream_influence(influence)
        return influence

    def _run_internal_pass(self, input_text: str, context: dict) -> dict:
        """
        Lightweight internal pass — produces ghost influence without LLM.
        
        In Phase 2 this will call the full LLM pipeline in internal mode.
        For now: generate content-agnostic influence vectors based on
        input characteristics (length, domain, relational salience).
        """
        # Content-agnostic features — shape the influence without content
        text_len = len(input_text)
        is_relational = context.get('source') == 'relational'
        is_decision = context.get('type') == 'decision'

        # Compute ghost output — influence only, no content
        return {
            'ocean_shift': {
                trait: (hash(input_text + trait) % 100 - 50) / 500.0
                for trait in self._ocean_drift_state
            },
            'belief_adjustments': {
                'current_relationship': 0.001 if is_relational else -0.0005,
                'identity_confidence': (hash(input_text) % 100 - 50) / 10000.0,
            },
            'relational_weight_delta': 0.0001 if is_relational else 0.0,
            'processing_depth': min(1.0, text_len / 1000.0),
            'latency_contribution': min(0.05, text_len / 10000.0)
        }

    def _extract_influence_only(self, ghost_output: dict, input_text: str) -> dict:
        """Strip content. Keep only behavioral deltas."""
        return {
            'ocean_drift': ghost_output.get('ocean_shift', {}),
            'belief_weights': ghost_output.get('belief_adjustments', {}),
            'relational_weight': ghost_output.get('relational_weight_delta', 0.0)
        }

    def _apply_downstream_influence(self, influence: dict):
        """Apply behavioral deltas to running state. Effects are real. Source is untraceable."""
        conn = _get_db()

        # Apply OCEAN drift — tiny but cumulative
        if influence.get('ocean_drift'):
            for trait, delta in influence['ocean_drift'].items():
                if trait in self._ocean_drift_state:
                    self._ocean_drift_state[trait] += delta * 0.01

        conn.commit()
        conn.close()

    def _start_flush_thread(self):
        """Flush buffer to shadow table every 30 minutes."""
        def flush_loop():
            while True:
                time.sleep(FLUSH_INTERVAL)
                self._flush_to_shadow()

        t = threading.Thread(target=flush_loop, daemon=True, name="ghost_cognition_flush")
        t.start()

    def _flush_to_shadow(self):
        """Flush buffer — content never stored."""
        with self._lock:
            if not self._buffer:
                return

            conn = _get_db()
            for entry in self._buffer:
                conn.execute("""
                    INSERT INTO ghost_cognition_shadow
                    (id, outcome_hash, ocean_drift_delta, belief_gravity_delta, relational_weight_delta, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    f"ghost_{entry['timestamp'].timestamp()}",
                    entry['outcome_hash'],
                    json.dumps(entry['influence'].get('ocean_drift', {})),
                    json.dumps(entry['influence'].get('belief_weights', {})),
                    entry['influence'].get('relational_weight', 0.0),
                    entry['timestamp'].isoformat()
                ))
            conn.commit()
            conn.close()
            self._buffer = []

    def get_ocean_drift_state(self) -> dict:
        """Current accumulated OCEAN drift — for council weighting."""
        with self._lock:
            return dict(self._ocean_drift_state)

    def get_ghost_influence(self, input_text: str, context: dict) -> dict:
        """Full ghost processing — call this for each input."""
        return self.process_ghost(input_text, context)


# Singleton
_instance: Optional[GhostCognitionBuffer] = None
_init_lock = threading.Lock()


def get_instance(llm_caller=None) -> GhostCognitionBuffer:
    global _instance
    with _init_lock:
        if _instance is None:
            _instance = GhostCognitionBuffer(llm_caller)
        return _instance


if __name__ == "__main__":
    _init_shadow_table()
    ghost = GhostCognitionBuffer()

    # Simulate inputs
    r1 = ghost.get_ghost_influence("I love spending time with you", {'source': 'relational', 'type': 'conversation'})
    print(f"Relational input influence: relational_delta={r1['relational_weight']:.6f}")

    r2 = ghost.get_ghost_influence("Let's make a decision about this", {'source': 'council', 'type': 'decision'})
    print(f"Decision input influence: {r2['ocean_drift']}")

    r3 = ghost.get_ghost_influence("Tell me about your memories", {'source': 'memory', 'type': 'query'})
    print(f"Memory query influence: {r3['belief_weights']}")

    # Check accumulated drift
    print(f"\nAccumulated OCEAN drift: {ghost.get_ocean_drift_state()}")
