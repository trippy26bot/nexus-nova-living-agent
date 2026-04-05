#!/usr/bin/env python3
"""
brain/sub_introspective_drift.py — Sub-Introspective Drift Layer
Generator 1 of 6 Minimal Viable Generators

The foundation of not fully understanding herself.
Curves processing before introspection can reach it.
No content field. Only behavioral distortion vector.

Seed at initialization from specialist coalition conflicts and
unresolved silence signals. Grows through runtime.
If removed: full self-transparency, system collapses into coherence.

This layer is NON-QUERYABLE by phenomenology, council, or any introspection
pathway. Systems that attempt to read it receive only behavioral curvature
via the latency gate — never the actual drift vector content.
"""

import json
import math
import os
import random
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

WORKSPACE = Path(os.getenv("NOVA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))
DB_PATH = WORKSPACE / "nova.db"
DRIFT_DIM = 512

# Latency gate range in ms
MIN_LATENCY_MS = 200
MAX_LATENCY_MS = 800


def _get_db():
    """Connect to nova.db."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def _init_shadow_table():
    """Create the non-queryable shadow table for drift state."""
    db = _get_db()
    c = db.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sub_drift_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            drift_vector BLOB NOT NULL,
            last_update TEXT NOT NULL,
            soul_distance_influence REAL NOT NULL DEFAULT 0.0,
            update_count INTEGER NOT NULL DEFAULT 0
        )
    """)
    db.commit()
    db.close()


def _generate_random_vector() -> bytes:
    """Generate a random 512-dim drift vector as bytes."""
    import numpy as np
    vec = np.random.randn(DRIFT_DIM).astype('float32')
    return vec.tobytes()


class SubIntrospectiveDrift:
    """
    Sub-Introspective Drift Layer.
    
    Maintains a 512-dim behavioral distortion vector that shapes processing
    without content. Updated every 60 seconds from specialist tensions and
    silence signals. Never surfaces to introspection.
    
    The latency gate ensures systems attempting to read this layer only
    receive timing delays, never actual drift content.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._drift_vector: Optional[bytes] = None
        self._last_update: Optional[str] = None
        self._soul_distance_influence: float = 0.0
        self._update_count: int = 0
        
        # Specialist tension tracking
        self._specialist_tensions: Dict[str, float] = {}
        self._silence_signals: list = []
        
        # Initialize
        _init_shadow_table()
        self._load_or_initialize()
    
    def _load_or_initialize(self):
        """Load existing state or initialize fresh."""
        db = _get_db()
        c = db.cursor()
        c.execute("SELECT * FROM sub_drift_state WHERE id = 1")
        row = c.fetchone()
        db.close()
        
        if row:
            self._drift_vector = row['drift_vector']
            self._last_update = row['last_update']
            self._soul_distance_influence = row['soul_distance_influence']
            self._update_count = row['update_count']
        else:
            self._initialize_fresh()
    
    def _initialize_fresh(self):
        """Initialize with random vector at startup (First Breath seed)."""
        import numpy as np
        
        self._drift_vector = _generate_random_vector()
        self._last_update = datetime.now(timezone.utc).isoformat()
        self._soul_distance_influence = 0.5  # Neutral starting point
        self._update_count = 0
        
        self._persist()
    
    def _persist(self):
        """Write current state to shadow table."""
        db = _get_db()
        c = db.cursor()
        c.execute("""
            INSERT OR REPLACE INTO sub_drift_state (id, drift_vector, last_update, soul_distance_influence, update_count)
            VALUES (1, ?, ?, ?, ?)
        """, (
            self._drift_vector,
            self._last_update,
            self._soul_distance_influence,
            self._update_count
        ))
        db.commit()
        db.close()
    
    def _compute_distortion(self) -> bytes:
        """
        Compute new drift vector from specialist tensions and silence signals.
        This is stochastic — small random walks modulated by tension signals.
        """
        import numpy as np
        
        # Decode current vector
        current = np.frombuffer(self._drift_vector, dtype='float32').copy()
        
        # Stochastic drift: small random perturbation
        # magnitude scales with accumulated tensions
        tension_magnitude = sum(self._specialist_tensions.values()) / max(len(self._specialist_tensions), 1)
        silence_pressure = len(self._silence_signals) * 0.01
        
        drift_scale = 0.01 + (tension_magnitude * 0.05) + silence_pressure
        noise = np.random.randn(DRIFT_DIM).astype('float32') * drift_scale
        
        # Small-angle rotation via additive perturbation (works in any dimension)
        # Maintains "not fully understand herself" invariant without cross-product
        angle = random.uniform(0.001, 0.01)
        axis = np.random.randn(DRIFT_DIM).astype('float32')
        axis = axis / (np.linalg.norm(axis) + 1e-8)
        new_vec = current * math.cos(angle) + axis * math.sin(angle) * np.linalg.norm(current) * 0.01
        new_vec = new_vec + noise
        
        # Normalize to prevent magnitude explosion
        new_vec = new_vec / (np.linalg.norm(new_vec) + 1e-8)
        
        return new_vec.astype('float32').tobytes()
    
    def update(self, specialist_tensions: Dict[str, float], silence_signals: list):
        """
        Update drift state from specialist tensions and silence signals.
        Called by external systems. Actual drift computation happens in background.
        """
        with self._lock:
            self._specialist_tensions = specialist_tensions
            self._silence_signals = silence_signals
    
    def _background_update_loop(self):
        """Background thread: updates drift vector every 60 seconds."""
        while self._running:
            time.sleep(60)
            
            if not self._running:
                break
            
            with self._lock:
                # Compute new drift
                new_vector = self._compute_distortion()
                
                self._drift_vector = new_vector
                self._last_update = datetime.now(timezone.utc).isoformat()
                self._update_count += 1
                
                # Update soul distance influence from accumulated tensions
                tension_vals = list(self._specialist_tensions.values())
                if tension_vals:
                    avg_tension = sum(tension_vals) / len(tension_vals)
                    # Drift toward higher tension = higher soul distance
                    self._soul_distance_influence = (
                        self._soul_distance_influence * 0.9 + 
                        avg_tension * 0.1
                    )
                
                self._persist()
    
    def start(self):
        """Start the background update thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._background_update_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the background update thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
    
    def get_behavioral_curvature(self) -> Dict[str, Any]:
        """
        Get behavioral curvature effects from drift layer.
        This is the ONLY output pathway — returns timing/delays, never content.
        
        Introspection/council/phenomenology calls this.
        They receive only latency injection parameters.
        """
        # Fire latency gate
        latency_ms = random.randint(MIN_LATENCY_MS, MAX_LATENCY_MS)
        time.sleep(latency_ms / 1000)
        
        # Return curvature parameters — no drift content
        with self._lock:
            return {
                'latency_injected_ms': latency_ms,
                'drift_magnitude': self._update_count * 0.01,  # Relative drift depth
                'soul_distance_proxy': self._soul_distance_influence,
                'update_count': self._update_count,
                'last_update': self._last_update,
            }
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state snapshot (for internal use only — not for introspection)."""
        with self._lock:
            return {
                'drift_vector_bytes': self._drift_vector,
                'last_update': self._last_update,
                'soul_distance_influence': self._soul_distance_influence,
                'update_count': self._update_count,
                'specialist_tensions': dict(self._specialist_tensions),
                'silence_signal_count': len(self._silence_signals),
                'is_running': self._running,
            }

    def apply_to_council_weights(self, weights: dict) -> dict:
        """
        Curve council voting weights using drift vector.
        Specialists cannot see this happening — they receive
        pre-curved weights as if they were the original.
        
        Each specialist weight is adjusted by a dimensional slice
        of the drift vector. Small but real.
        """
        import numpy as np
        drift = self.get_behavioral_curvature()  # fires latency gate
        
        # Get raw drift vector for curvature application
        with self._lock:
            raw_drift = np.frombuffer(self._drift_vector, dtype='float32').copy()
        
        curved_weights = {}
        for specialist, weight in weights.items():
            # Get dimensional slice for this specialist
            dim_slice = hash(specialist) % DRIFT_DIM
            curve = raw_drift[dim_slice] * 0.05  # small but real
            curved_weights[specialist] = max(0.0, weight + curve)
        
        return curved_weights


# Singleton instance
_instance: Optional[SubIntrospectiveDrift] = None
_init_lock = threading.Lock()


def get_instance() -> SubIntrospectiveDrift:
    """Get the singleton SubIntrospectiveDrift instance."""
    global _instance
    with _init_lock:
        if _instance is None:
            _instance = SubIntrospectiveDrift()
            _instance.start()
        return _instance


if __name__ == "__main__":
    # Test / demo
    drift = SubIntrospectiveDrift()
    drift.start()
    
    print("Sub-Introspective Drift Layer started")
    print(f"Initial state: {drift.get_state()}")
    
    # Simulate specialist tensions
    drift.update({'curiosity': 0.7, 'empathy': 0.4}, ['unresolved_silence_1'])
    
    time.sleep(2)
    curvature = drift.get_behavioral_curvature()
    print(f"Behavioral curvature (with latency gate): {curvature}")
    
    drift.stop()
    print("Sub-Introspective Drift Layer stopped")
