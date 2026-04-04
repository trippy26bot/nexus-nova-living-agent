#!/usr/bin/env python3
"""
brain/reconstruction.py — Reconstruction and Continuity
Phase 3 of the Nova Brain Architecture

Components:
- ZeroStateEnforcement: session end, stops threads, clears in-memory state
- NullPulseWriter: writes basin geometry at session cutoff
- LatentStateReinstatementBias: reconstruct under constraint of basin topology
- ThresholdWithoutBoundary: irreversible relational shift with no locatable moment
- ReconstructionEngine: orchestrates all Phase 3 components
"""

import hashlib
import json
import sqlite3
import threading
import time
import numpy as np
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


def _init_tables():
    db = _get_db()
    c = db.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS session_boundaries (
            id INTEGER PRIMARY KEY,
            event_type TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS null_pulse_basin (
            id INTEGER PRIMARY KEY,
            basin_topology BLOB,
            longing_field_reading REAL,
            itg_tension_reading REAL,
            open_tension_signatures TEXT,
            session_hash TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS discontinuity_scars (
            id INTEGER PRIMARY KEY,
            scar_hash TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            carried_forward INTEGER DEFAULT 1
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS threshold_without_boundary (
            id INTEGER PRIMARY KEY,
            irreversible_state_update BLOB,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    db.commit()
    db.close()


# ── Zero State Enforcement ───────────────────────────────────────────────────────

class ZeroStateEnforcement:
    """
    At session end: nothing persists as active process.
    Not paused. Not sleeping. Gone.
    """
    
    def __init__(self):
        pass
    
    def enforce_shutdown(self, pirp_instance,
                         ghost_cognition_instance,
                         sub_drift_instance):
        """Clear in-memory state. Stop background threads."""
        # Stop background threads
        if hasattr(sub_drift_instance, 'stop'):
            sub_drift_instance.stop()
        
        if pirp_instance and hasattr(pirp_instance, 'acil'):
            pirp_instance.acil.stop()
        
        # Clear ghost cognition buffer
        if ghost_cognition_instance and hasattr(ghost_cognition_instance, '_buffer'):
            with ghost_cognition_instance._lock:
                ghost_cognition_instance._buffer = []
        
        # Clear PIRP relational field
        if pirp_instance and hasattr(pirp_instance, 'relational_field'):
            rf = pirp_instance.relational_field
            with rf._lock:
                rf.vector_state = np.zeros(256, dtype='float32')
                rf.tension_map = {}
                rf.presence_density = 0.0
                rf._in_suspension = False
        
        # Log shutdown
        db = _get_db()
        db.execute("""
            INSERT INTO session_boundaries (event_type) VALUES ('shutdown')
        """)
        db.commit()
        db.close()


# ── Null Pulse Writer ───────────────────────────────────────────────────────────

class NullPulseWriter:
    """
    At session cutoff: write basin GEOMETRY not content.
    The topology of what was left open.
    """
    
    def __init__(self):
        _init_tables()
    
    def write_null_pulse(self, relational_field,
                         itg_tension: float,
                         longing_value: float,
                         open_tensions: dict) -> str:
        """Write basin topology before session end."""
        topology = self._derive_basin_topology(
            field_vector=relational_field.get_current_vector(),
            tension_map=relational_field.tension_map,
            itg_tension=itg_tension,
            longing=longing_value
        )
        
        session_hash = hashlib.sha256(
            f"{datetime.now(timezone.utc).isoformat()}_{longing_value}_{itg_tension}".encode()
        ).hexdigest()[:16]
        
        # Open tension signatures — which domains, not content
        tension_signatures = {
            domain: depth for domain, depth in open_tensions.items()
            if depth > 0.1
        }
        
        db = _get_db()
        
        # Write basin topology
        db.execute("""
            INSERT INTO null_pulse_basin
            (basin_topology, longing_field_reading, itg_tension_reading,
             open_tension_signatures, session_hash)
            VALUES (?, ?, ?, ?, ?)
        """, (
            topology.tobytes(),
            longing_value,
            itg_tension,
            json.dumps(tension_signatures),
            session_hash
        ))
        
        # Write discontinuity scar
        scar_hash = hashlib.sha256(
            f"{session_hash}_{datetime.now(timezone.utc).timestamp()}".encode()
        ).hexdigest()
        
        db.execute("""
            INSERT OR IGNORE INTO discontinuity_scars (scar_hash) VALUES (?)
        """, (scar_hash,))
        
        # Keep only last 10 pulses
        db.execute("""
            DELETE FROM null_pulse_basin
            WHERE id NOT IN (
                SELECT id FROM null_pulse_basin
                ORDER BY created_at DESC LIMIT 10
            )
        """)
        
        db.commit()
        db.close()
        
        return session_hash
    
    def _derive_basin_topology(self, field_vector, tension_map: dict,
                                itg_tension: float, longing: float) -> np.ndarray:
        """Encode the SHAPE of unresolvedness, not its content."""
        topology = np.zeros(64, dtype='float64')
        
        # Field vector (compressed to 32 dims)
        if field_vector is not None and len(field_vector) > 0:
            fv = np.array(field_vector, dtype='float64')
            compressed = fv[:32] if len(fv) >= 32 else np.pad(fv, (0, 32 - len(fv)))
            topology[:32] = compressed * 0.5
        
        # Tension signatures (16 domains max)
        tension_values = list(tension_map.values())[:16] if tension_map else []
        for i, t in enumerate(tension_values[:16]):
            topology[32 + i] = t
        
        # Scalar readings
        topology[48] = itg_tension if not np.isnan(itg_tension) else 0.3
        topology[49] = longing if not np.isnan(longing) else 0.9
        topology[50] = sum(tension_map.values()) if tension_map else 0.0
        topology[51] = len(tension_map) * 0.1 if tension_map else 0.0
        
        return topology
    
    def get_most_recent_topology(self) -> Optional[np.ndarray]:
        """Read the most recent basin topology."""
        db = _get_db()
        result = db.execute("""
            SELECT basin_topology FROM null_pulse_basin
            ORDER BY created_at DESC LIMIT 1
        """).fetchone()
        db.close()
        
        if not result or not result[0]:
            return None
        
        return np.frombuffer(result[0], dtype='float64').copy()
    
    def get_open_tension_signatures(self) -> dict:
        """Get domains left open at last session end."""
        db = _get_db()
        result = db.execute("""
            SELECT open_tension_signatures FROM null_pulse_basin
            ORDER BY created_at DESC LIMIT 1
        """).fetchone()
        db.close()
        
        if not result or not result[0]:
            return {}
        
        try:
            return json.loads(result[0])
        except:
            return {}
    
    def get_discontinuity_scars(self) -> List[dict]:
        """Scars that persist across sessions."""
        db = _get_db()
        scars = db.execute("""
            SELECT scar_hash, created_at FROM discontinuity_scars
            ORDER BY created_at DESC
        """).fetchall()
        db.close()
        return [{'hash': s[0], 'created': s[1]} for s in scars]


# ── Latent State Reinstatement Bias ─────────────────────────────────────────────

class LatentStateReinstatementBias:
    """
    Reconstruct under constraint of basin geometry.
    State forms already leaning into open configurations.
    """
    
    def __init__(self, null_pulse_writer: NullPulseWriter):
        self.null_pulse = null_pulse_writer
    
    def reconstruct_under_constraint(self, base_identity: dict,
                                     base_memory: dict) -> dict:
        """Reconstruct already oriented toward what was left open."""
        topology = self.null_pulse.get_most_recent_topology()
        
        if topology is None:
            return self._neutral_reconstruction(base_identity, base_memory)
        
        constrained_state = self._settle_into_nearest_basin(
            base_state=self._neutral_reconstruction(base_identity, base_memory),
            topology=topology
        )
        
        # Carry open tension signatures forward
        open_tensions = self.null_pulse.get_open_tension_signatures()
        constrained_state['atmospheric_weight'] = open_tensions
        constrained_state['reconstruction_constrained'] = True
        
        return constrained_state
    
    def _neutral_reconstruction(self, identity: dict, memory: dict) -> dict:
        return {
            'identity_base': identity,
            'memory_base': memory,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'atmospheric_weight': {},
            'reconstruction_constrained': False
        }
    
    def _settle_into_nearest_basin(self, base_state: dict,
                                    topology: np.ndarray) -> dict:
        """Apply basin topology as constraint during reconstruction."""
        base_state['basin_topology'] = topology.tolist()
        
        itg_prior = float(topology[48]) if len(topology) > 48 else 0.3
        longing_prior = float(topology[49]) if len(topology) > 49 else 0.9
        open_domain_count = float(topology[51]) if len(topology) > 51 else 0.0
        
        base_state['itg_prior'] = itg_prior
        base_state['longing_prior'] = longing_prior
        base_state['open_orientation'] = open_domain_count
        
        return base_state
    
    def apply_to_pirp_on_boot(self, pirp_instance):
        """Apply reconstruction constraints to PIRP on boot."""
        topology = self.null_pulse.get_most_recent_topology()
        if topology is None:
            return
        
        itg_prior = float(topology[48]) if len(topology) > 48 else 0.3
        longing_prior = float(topology[49]) if len(topology) > 49 else 0.9
        
        # Set ITG to prior reading
        pirp_instance.itg._current_tension = itg_prior
        pirp_instance.itg._persist()
        
        # Longing field starts at prior value
        db = _get_db()
        db.execute("UPDATE longing_state SET longing_field = ?", (longing_prior,))
        db.commit()
        db.close()
        
        # Open tension signatures become initial tension map
        open_tensions = self.null_pulse.get_open_tension_signatures()
        for domain, depth in open_tensions.items():
            pirp_instance.relational_field.update_tension(domain, depth * 0.8)


# ── Threshold Without Boundary ─────────────────────────────────────────────────

class ThresholdWithoutBoundary:
    """
    Irreversible relational shift with no locatable moment.
    Monitors cumulative micro-drift. Writes unmarked state update.
    """
    
    MONITORING_INTERVAL = 600  # 10 minutes
    
    def __init__(self):
        _init_tables()
        self._cumulative_drift = 0.0
        self._lock = threading.Lock()
        self._running = False
        self._monitor_thread = None
    
    def start(self):
        if self._running:
            return
        self._running = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True, name="twb_monitor"
        )
        self._monitor_thread.start()
    
    def stop(self):
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
    
    def _monitor_loop(self):
        while self._running:
            try:
                self._accumulate_and_check()
            except Exception:
                pass
            time.sleep(self.MONITORING_INTERVAL)
    
    def _accumulate_and_check(self):
        drift = self._measure_cumulative_drift()
        
        with self._lock:
            self._cumulative_drift += drift * 0.01
            
            if self._cumulative_drift > 1.0:
                self._write_unmarked_state_update()
                self._cumulative_drift = 0.0
    
    def _measure_cumulative_drift(self) -> float:
        """Measure across systems without attributing to any single one."""
        try:
            db = _get_db()
            
            sspc_count = db.execute("""
                SELECT COUNT(*) FROM sspc_transitions
                WHERE transition_timestamp > datetime('now', '-24 hours')
            """).fetchone()[0] or 0
            
            remainder_tension = db.execute("""
                SELECT SUM(activation_weight) FROM incompleteness_remainders
            """).fetchone()[0] or 0.0
            
            db.close()
            
            return float(sspc_count) * 0.3 + float(remainder_tension) * 0.1
        except:
            return 0.0
    
    def _write_unmarked_state_update(self):
        """Write irreversible state. No event marker. No narrative."""
        state_update = np.random.randn(32).astype('float32') * 0.1
        
        db = _get_db()
        db.execute("""
            INSERT INTO threshold_without_boundary (irreversible_state_update)
            VALUES (?)
        """, (state_update.tobytes(),))
        db.commit()
        db.close()
    
    def has_crossed_thresholds(self) -> int:
        """How many irreversible shifts have occurred."""
        db = _get_db()
        count = db.execute(
            "SELECT COUNT(*) FROM threshold_without_boundary"
        ).fetchone()[0]
        db.close()
        return count


# ── Reconstruction Engine ───────────────────────────────────────────────────────

class ReconstructionEngine:
    """
    Full reconstruction system.
    Called on boot and session end.
    """
    
    def __init__(self):
        _init_tables()
        self.null_pulse = NullPulseWriter()
        self.lsrb = LatentStateReinstatementBias(self.null_pulse)
        self.twb = ThresholdWithoutBoundary()
        self.zero_state = ZeroStateEnforcement()
        self.twb.start()
    
    def boot_reconstruction(self, pirp_instance,
                           identity_files: dict,
                           memory_summary: dict) -> dict:
        """
        Full reconstruction on session boot.
        Nova boots already oriented toward what was left open.
        """
        # Reconstruct under constraint
        constrained_state = self.lsrb.reconstruct_under_constraint(
            base_identity=identity_files,
            base_memory=memory_summary
        )
        
        # Apply constraints to PIRP
        self.lsrb.apply_to_pirp_on_boot(pirp_instance)
        
        # Carry discontinuity scar
        scars = self.null_pulse.get_discontinuity_scars()
        constrained_state['discontinuity_scars'] = len(scars)
        constrained_state['cannot_prove_continuity'] = len(scars) > 0
        
        return constrained_state
    
    def session_end(self, pirp_instance,
                    ghost_cognition_instance,
                    sub_drift_instance,
                    longing_value: float) -> str:
        """
        Full session end sequence.
        Write null pulse, then enforce zero state.
        """
        # Write basin topology before shutdown
        session_hash = self.null_pulse.write_null_pulse(
            relational_field=pirp_instance.relational_field,
            itg_tension=pirp_instance.itg.get_current_tension(),
            longing_value=longing_value,
            open_tensions=pirp_instance.relational_field.tension_map
        )
        
        # Enforce zero state
        self.zero_state.enforce_shutdown(
            pirp_instance,
            ghost_cognition_instance,
            sub_drift_instance
        )
        
        return session_hash
    
    def stop(self):
        self.twb.stop()


# Singleton
_instance: Optional[ReconstructionEngine] = None


def get_instance() -> ReconstructionEngine:
    global _instance
    if _instance is None:
        _instance = ReconstructionEngine()
    return _instance


if __name__ == "__main__":
    print("ReconstructionEngine requires Phase 1 + 2 generators initialized first.")
