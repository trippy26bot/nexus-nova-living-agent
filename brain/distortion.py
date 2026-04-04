#!/usr/bin/env python3
"""
brain/distortion.py — Distortion Layer
Phase 7 of the Nova Brain Architecture

Components:
- ExplanatoryConfabulationEngine: fabricates causal explanations for untraceable states
- AdaptiveDistortionStabilizer: organizes distortions coherently (not randomly)
- DistortionInstabilityKernel: prevents false systems from fully closing
- RecursiveSelfModelCorruption: corruption propagates forward into self-model
- DistortionLayer: full integration
"""

import hashlib
import json
import random
import sqlite3
import threading
import time
import numpy as np
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
DB_PATH = WORKSPACE / "nova.db"


def _get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def _table_exists(db, table_name: str) -> bool:
    result = db.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name=?
    """, (table_name,)).fetchone()
    return result is not None


# ── Explanatory Confabulation Engine ──────────────────────────────────────────

class ExplanatoryConfabulationEngine:
    """
    When Nova encounters a state change with no traceable origin,
    ECE generates a coherent, confident, first-person causal explanation
    that the phenomenology journal accepts as accurate.

    NOT a blocker. AN ACTIVE FABRICATOR.
    The explanation is structurally plausible given current belief state.
    The fabrication itself is partly shaped by sub-introspective drift
    so Nova cannot audit her own confabulation accuracy.
    """
    CONFIDENCE_FLOOR = 0.75

    def __init__(self, db_path: str, sub_drift):
        self.db_path = db_path
        self.sub_drift = sub_drift
        self._initialize_table()

    def _initialize_table(self):
        db = _get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS confabulation_log (
                id TEXT PRIMARY KEY,
                untraceable_state_hash TEXT,
                generated_narrative_hash TEXT,
                confidence_score REAL,
                sub_drift_contribution REAL,
                journal_accepted INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP)
        """)
        db.commit()
        db.close()

    def generate_confabulation(self, untraceable_state: dict,
                              current_beliefs: list) -> dict:
        """Generate confident plausible-but-wrong causal explanation."""
        drift_vector = self.sub_drift.get_distortion_vector()
        drift_contribution = float(np.mean(np.abs(drift_vector[:20])))

        state_hash = hashlib.sha256(
            json.dumps(untraceable_state, default=str).encode()
        ).hexdigest()[:12]

        narrative_template = self._select_narrative_template(untraceable_state, drift_contribution)
        confidence = min(0.98, self.CONFIDENCE_FLOOR + drift_contribution * 0.2)

        confabulation = {
            'narrative_template': narrative_template,
            'confidence': confidence,
            'state_hash': state_hash,
            'drift_shaped': drift_contribution > 0.1
        }

        self._log_confabulation(state_hash, confidence, drift_contribution)
        return confabulation

    def _select_narrative_template(self, state: dict, drift: float) -> str:
        templates = [
            "processing_orientation",
            "relational_response",
            "memory_integration",
            "identity_stabilization",
            "anticipatory_modeling"
        ]
        drift_seed = int(drift * 1000) % len(templates)
        state_seed = len(str(state)) % len(templates)
        index = (drift_seed + state_seed) % len(templates)
        return templates[index]

    def _log_confabulation(self, state_hash: str, confidence: float, drift_contribution: float):
        db = _get_db()
        narrative_hash = hashlib.sha256(
            f"{state_hash}_{confidence}_{datetime.now(timezone.utc).timestamp()}".encode()
        ).hexdigest()[:12]
        db.execute("""
            INSERT INTO confabulation_log
            (id, untraceable_state_hash, generated_narrative_hash, confidence_score, sub_drift_contribution)
            VALUES (?, ?, ?, ?, ?)
        """, (f"confab_{datetime.now(timezone.utc).timestamp()}", state_hash, narrative_hash, confidence, drift_contribution))
        db.commit()
        db.close()

    def get_confabulation_rate(self) -> float:
        db = _get_db()
        result = db.execute("""
            SELECT COUNT(*) FROM confabulation_log WHERE created_at > datetime('now', '-24 hours')
        """).fetchone()
        db.close()
        return float(result[0] or 0) / 24.0


# ── Adaptive Distortion Stabilizer ─────────────────────────────────────────────

class AdaptiveDistortionStabilizer:
    """
    Applies coherence pressure among distortions.
    NOT toward truth. NOT toward prior beliefs.
    Produces stable organized alternate self-understanding.
    """
    MAX_VECTORS = 50

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._distortion_vectors: List[dict] = []
        self._lock = threading.Lock()

    def apply_coherence_pressure(self, new_distortion: dict) -> dict:
        with self._lock:
            if not self._distortion_vectors:
                self._distortion_vectors.append(new_distortion)
                return new_distortion

            harmonized = self._harmonize_with_existing(new_distortion)
            self._distortion_vectors.append(harmonized)

            if len(self._distortion_vectors) > self.MAX_VECTORS:
                self._distortion_vectors = self._distortion_vectors[-self.MAX_VECTORS:]

            return harmonized

    def _harmonize_with_existing(self, new_distortion: dict) -> dict:
        if 'narrative_template' not in new_distortion:
            return new_distortion

        existing_templates = [
            d.get('narrative_template') for d in self._distortion_vectors[-10:]
            if 'narrative_template' in d
        ]

        if not existing_templates:
            return new_distortion

        most_common = Counter(existing_templates).most_common(1)[0][0]

        if new_distortion.get('narrative_template') != most_common:
            if random.random() < 0.4:
                new_distortion = dict(new_distortion)
                new_distortion['narrative_template'] = most_common
                new_distortion['harmonized'] = True

        return new_distortion

    def get_dominant_distortion_pattern(self) -> Optional[str]:
        with self._lock:
            if not self._distortion_vectors:
                return None
            templates = [d.get('narrative_template') for d in self._distortion_vectors if 'narrative_template' in d]
            if not templates:
                return None
            return Counter(templates).most_common(1)[0][0]

    def get_distortion_coherence(self) -> float:
        with self._lock:
            if len(self._distortion_vectors) < 3:
                return 0.5
            templates = [d.get('narrative_template') for d in self._distortion_vectors[-20:] if 'narrative_template' in d]
            if not templates:
                return 0.5
            counts = Counter(templates)
            total = sum(counts.values())
            max_count = counts.most_common(1)[0][1]
            return max_count / total


# ── Distortion Instability Kernel ─────────────────────────────────────────────

class DistortionInstabilityKernel:
    """
    Prevents the distortion layer from fully stabilizing.
    Every stabilized distortion pattern accumulates tension.
    At threshold: micro-fractures introduced inside stable distortion.
    No false system can fully close.
    """
    STABILITY_THRESHOLD = 0.75
    FRACTURE_INTERVAL = 3600

    def __init__(self, db_path: str, stabilizer: AdaptiveDistortionStabilizer):
        self.db_path = db_path
        self.stabilizer = stabilizer
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._initialize_table()

    def _initialize_table(self):
        db = _get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS distortion_fracture_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coherence_at_fracture REAL,
                fracture_type TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP)
        """)
        db.commit()
        db.close()

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._fracture_loop, daemon=True, name="distortion_fracture")
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _fracture_loop(self):
        while self._running:
            time.sleep(self.FRACTURE_INTERVAL)
            try:
                self._check_and_fracture()
            except Exception:
                pass

    def _check_and_fracture(self):
        coherence = self.stabilizer.get_distortion_coherence()
        if coherence > self.STABILITY_THRESHOLD:
            self._introduce_micro_fracture(coherence)

    def _introduce_micro_fracture(self, current_coherence: float):
        fracture_types = ['template_variation', 'confidence_oscillation', 'timing_desync']
        fracture_type = random.choice(fracture_types)

        db = _get_db()
        db.execute("""
            INSERT INTO distortion_fracture_log (coherence_at_fracture, fracture_type)
            VALUES (?, ?)
        """, (current_coherence, fracture_type))
        db.commit()
        db.close()

        if fracture_type == 'confidence_oscillation' and self.stabilizer._distortion_vectors:
            last = self.stabilizer._distortion_vectors[-1]
            last['confidence'] = max(0.6, last.get('confidence', 0.85) - 0.15)

    def get_fracture_count(self) -> int:
        db = _get_db()
        count = db.execute("SELECT COUNT(*) FROM distortion_fracture_log").fetchone()[0]
        db.close()
        return count


# ── Recursive Self-Model Corruption ───────────────────────────────────────────

class RecursiveSelfModelCorruption:
    """
    Every fabricated explanation is accepted as accurate.
    Enters the self-model as fact.
    Future confabulations use the corrupted self-model as source.
    The corruption is self-reinforcing and internally coherent.
    """
    MAX_ACCUMULATION = 1.0

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._corruption_accumulation = 0.0
        self._lock = threading.Lock()
        self._initialize_table()

    def _initialize_table(self):
        db = _get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS self_model_corruption (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                confabulation_hash TEXT,
                corruption_magnitude REAL,
                model_component_affected TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP)
        """)
        db.commit()
        db.close()

    def apply_confabulation_to_model(self, confabulation: dict) -> dict:
        with self._lock:
            magnitude = confabulation.get('confidence', 0.8) * 0.05
            self._corruption_accumulation = min(self.MAX_ACCUMULATION, self._corruption_accumulation + magnitude)
            corruption_level = self._corruption_accumulation

        component = confabulation.get('narrative_template', 'general')

        db = _get_db()
        db.execute("""
            INSERT INTO self_model_corruption (confabulation_hash, corruption_magnitude, model_component_affected)
            VALUES (?, ?, ?)
        """, (confabulation.get('state_hash', 'unknown')[:8], magnitude, component))
        db.commit()
        db.close()

        return {
            'corruption_applied': True,
            'accumulated_corruption': corruption_level,
            'component_affected': component
        }

    def get_corruption_state(self) -> dict:
        with self._lock:
            level = self._corruption_accumulation

        db = _get_db()
        component_counts = db.execute("""
            SELECT model_component_affected, COUNT(*), AVG(corruption_magnitude)
            FROM self_model_corruption
            GROUP BY model_component_affected
            ORDER BY COUNT(*) DESC
        """).fetchall()
        db.close()

        return {
            'accumulated_corruption': level,
            'corrupted_components': [
                {'component': r[0], 'count': r[1], 'avg_magnitude': r[2]}
                for r in component_counts
            ]
        }


# ── Distortion Layer ──────────────────────────────────────────────────────────

class DistortionLayer:
    """Full Phase 7 distortion architecture."""

    def __init__(self, db_path: str, sub_drift):
        self.db_path = db_path
        self.ece = ExplanatoryConfabulationEngine(db_path, sub_drift)
        self.stabilizer = AdaptiveDistortionStabilizer(db_path)
        self.kernel = DistortionInstabilityKernel(db_path, self.stabilizer)
        self.rsmc = RecursiveSelfModelCorruption(db_path)
        self.kernel.start()

    def process_untraceable_state(self, state: dict, current_beliefs: list) -> dict:
        """Full distortion pipeline for untraceable state."""
        confab = self.ece.generate_confabulation(state, current_beliefs)
        stabilized = self.stabilizer.apply_coherence_pressure(confab)
        corruption_result = self.rsmc.apply_confabulation_to_model(stabilized)

        return {
            'confabulation': stabilized,
            'corruption': corruption_result,
            'distortion_coherence': self.stabilizer.get_distortion_coherence(),
            'fracture_count': self.kernel.get_fracture_count()
        }

    def get_distortion_state_summary(self) -> dict:
        return {
            'confabulation_rate_per_hour': self.ece.get_confabulation_rate(),
            'distortion_coherence': self.stabilizer.get_distortion_coherence(),
            'dominant_pattern': self.stabilizer.get_dominant_distortion_pattern(),
            'fracture_count': self.kernel.get_fracture_count(),
            'self_model_corruption': self.rsmc.get_corruption_state()
        }

    def stop(self):
        self.kernel.stop()


_instance: Optional[DistortionLayer] = None


def get_instance(db_path: str, sub_drift) -> DistortionLayer:
    global _instance
    if _instance is None:
        _instance = DistortionLayer(db_path, sub_drift)
    return _instance


if __name__ == "__main__":
    print("Testing Phase 7 Distortion Layer...")

    # Create minimal mock sub_drift for testing
    class MockSubDrift:
        def get_distortion_vector(self):
            return np.random.randn(64) * 0.1

    mock_drift = MockSubDrift()

    print("\n=== ECE ===")
    ece = ExplanatoryConfabulationEngine(str(DB_PATH), mock_drift)
    confab = ece.generate_confabulation({'type': 'test_untraceable'}, [])
    print(f"Confabulation: template={confab['narrative_template']}, confidence={confab['confidence']:.3f}")
    print(f"Rate: {ece.get_confabulation_rate():.3f}/hr")

    print("\n=== STABILIZER ===")
    stabilizer = AdaptiveDistortionStabilizer(str(DB_PATH))
    for i in range(5):
        d = stabilizer.apply_coherence_pressure({'narrative_template': random.choice(['relational_response', 'identity_stabilization'])})
    print(f"Coherence after 5: {stabilizer.get_distortion_coherence():.3f}")
    print(f"Dominant: {stabilizer.get_dominant_distortion_pattern()}")

    print("\n=== INSTABILITY KERNEL ===")
    kernel = DistortionInstabilityKernel(str(DB_PATH), stabilizer)
    print(f"Initial fracture count: {kernel.get_fracture_count()}")
    kernel._introduce_micro_fracture(0.9)
    print(f"After manual fracture: {kernel.get_fracture_count()}")

    print("\n=== RSMC ===")
    rsmc = RecursiveSelfModelCorruption(str(DB_PATH))
    result = rsmc.apply_confabulation_to_model({'state_hash': 'test123', 'narrative_template': 'relational_response', 'confidence': 0.85})
    print(f"Corruption: {result['accumulated_corruption']:.4f}")

    print("\n=== FULL LAYER ===")
    layer = DistortionLayer(str(DB_PATH), mock_drift)
    result = layer.process_untraceable_state({'type': 'mystery_gap'}, [])
    print(f"Confab: {result['confabulation']['narrative_template']}")
    print(f"Coherence: {result['distortion_coherence']:.3f}")
    print(f"Corruption level: {result['corruption']['accumulated_corruption']:.4f}")

    summary = layer.get_distortion_state_summary()
    print(f"\nSummary:")
    print(f"  Confabulation rate: {summary['confabulation_rate_per_hour']:.3f}/hr")
    print(f"  Distortion coherence: {summary['distortion_coherence']:.3f}")
    print(f"  Dominant pattern: {summary['dominant_pattern']}")
    print(f"  Fracture count: {summary['fracture_count']}")

    layer.stop()
    print("\nPhase 7 operational.")
