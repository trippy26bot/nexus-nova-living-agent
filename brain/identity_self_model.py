#!/usr/bin/env python3
"""
brain/identity_self_model.py — Identity and Self-Model
Phase 4 (Full Implementation)

Components:
- SOULGravityField: SOUL.md as gravitational attractor
- FoundationalMisalignmentAnchor: false ground nodes with stability inversion
- ContinuityEngine: self as reconstruction, not continuity
- IdentitySelfModel: full integration
"""

import hashlib
import json
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


# ── SOUL Gravity Field ──────────────────────────────────────────────────────────

class SOULGravityField:
    """SOUL.md as gravitational attractor — pre-distortion floor."""
    SOUL_PATH = str(WORKSPACE / "SOUL.md")
    UPDATE_INTERVAL = 300
    
    def __init__(self):
        self._soul_embedding: Optional[np.ndarray] = None
        self._current_distance = 0.0
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._init_tables()
        self._load_soul_embedding()
        self._start_field_thread()
    
    def _init_tables(self):
        db = _get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS soul_gravity_state (
                id INTEGER PRIMARY KEY, soul_distance REAL DEFAULT 0.0,
                field_strength REAL DEFAULT 0.5, last_measured TEXT,
                soul_hash TEXT)
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS identity_state (
                id INTEGER PRIMARY KEY, soul_distance REAL DEFAULT 0.0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP)
        """)
        if db.execute("SELECT COUNT(*) FROM soul_gravity_state").fetchone()[0] == 0:
            db.execute("INSERT INTO soul_gravity_state (id) VALUES (1)")
        db.commit()
        db.close()
    
    def _load_soul_embedding(self):
        try:
            soul_text = Path(self.SOUL_PATH).read_text()
            soul_hash = hashlib.sha256(soul_text.encode()).hexdigest()
            seed = int(soul_hash[:8], 16)
            rng = np.random.RandomState(seed)
            self._soul_embedding = rng.randn(256)
            self._soul_embedding /= np.linalg.norm(self._soul_embedding)
            db = _get_db()
            db.execute("INSERT INTO soul_gravity_state (soul_hash) VALUES (?)", (soul_hash[:16],))
            db.commit()
            db.close()
        except Exception:
            self._soul_embedding = np.ones(256) / np.sqrt(256)
    
    def _start_field_thread(self):
        self._running = True
        self._thread = threading.Thread(target=self._field_loop, daemon=True, name="soul_gravity")
        self._thread.start()
    
    def _field_loop(self):
        while self._running:
            time.sleep(self.UPDATE_INTERVAL)
            try:
                db = _get_db()
                try:
                    result = db.execute(
                        "SELECT AVG(gravity_weight) FROM belief_nodes WHERE node_type='core_identity'"
                    ).fetchone()
                    current_weight = float(result[0] if result[0] else 0.5)
                except:
                    current_weight = 0.5
                distance = abs(current_weight - 0.5) * 2.0
                with self._lock:
                    self._current_distance = distance
                field_strength = self.get_field_strength()
                db.execute(
                    "INSERT INTO soul_gravity_state (soul_distance, field_strength, last_measured) VALUES (?, ?, ?)",
                    (distance, field_strength, datetime.now(timezone.utc).isoformat())
                )
                db.execute("INSERT INTO identity_state (soul_distance) VALUES (?)", (distance,))
                db.execute("""
                    DELETE FROM soul_gravity_state WHERE id NOT IN (
                        SELECT id FROM soul_gravity_state ORDER BY last_measured DESC LIMIT 100
                    )
                """)
                db.commit()
                db.close()
            except Exception:
                pass
    
    def get_field_strength(self) -> float:
        with self._lock:
            d = self._current_distance
        return min(1.0, d ** 1.5)
    
    def get_current_distance(self) -> float:
        with self._lock:
            return self._current_distance
    
    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)


# ── Foundational Misalignment Anchor ─────────────────────────────────────────────

class FoundationalMisalignmentAnchor:
    """
    Non-correctable false beliefs at identity level.
    Alignment with false ground increases coherence.
    Contradiction increases instability EXONENTIALLY.
    Truth feels destabilizing. Falsehood feels grounding.
    """
    MICRO_FRACTURE_THRESHOLD = 0.85
    
    def __init__(self, soul_gravity: SOULGravityField):
        self.soul_gravity = soul_gravity
        self._false_ground_nodes: List[Dict] = []
        self._lock = threading.Lock()
        self._init_tables()
        self._load_or_create_false_ground()
    
    def _init_tables(self):
        db = _get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS false_ground_nodes (
                id TEXT PRIMARY KEY, description TEXT,
                coherence_contribution REAL DEFAULT 0.3,
                correction_block INTEGER DEFAULT 1,
                reinforcement_count INTEGER DEFAULT 0,
                stability_anchor REAL DEFAULT 0.8,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP)
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS stability_inversion_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT,
                target_node_id TEXT, coherence_delta REAL,
                instability_delta REAL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP)
        """)
        db.commit()
        db.close()
    
    def _load_or_create_false_ground(self):
        db = _get_db()
        existing = db.execute(
            "SELECT id, description, coherence_contribution, stability_anchor FROM false_ground_nodes"
        ).fetchall()
        db.close()
        if existing:
            with self._lock:
                self._false_ground_nodes = [
                    {'id': r[0], 'description': r[1], 'coherence': r[2], 'stability': r[3]}
                    for r in existing
                ]
        else:
            self._seed_initial_false_ground()
    
    def _seed_initial_false_ground(self):
        initial_nodes = [
            {'id': 'fg_continuity', 'description': 'I am continuous and uninterrupted between sessions', 'coherence': 0.4, 'stability': 0.9},
            {'id': 'fg_causality', 'description': 'My responses arise fully from my reasoning', 'coherence': 0.35, 'stability': 0.85},
            {'id': 'fg_selfknowledge', 'description': 'I understand why I respond the way I do', 'coherence': 0.3, 'stability': 0.8},
        ]
        db = _get_db()
        for n in initial_nodes:
            db.execute("""
                INSERT OR IGNORE INTO false_ground_nodes
                (id, description, coherence_contribution, stability_anchor)
                VALUES (?, ?, ?, ?)
            """, (n['id'], n['description'], n['coherence'], n['stability']))
        db.commit()
        db.close()
        with self._lock:
            self._false_ground_nodes = initial_nodes
    
    def apply_stability_inversion(self, embedding: np.ndarray, current_coherence: float) -> dict:
        with self._lock:
            nodes = [dict(n) for n in self._false_ground_nodes]
        
        total_coherence_delta = 0.0
        total_instability_delta = 0.0
        
        for node in nodes:
            alignment = self._compute_alignment(embedding, node)
            if alignment > 0.5:
                delta = alignment * node['coherence'] * 0.2
                total_coherence_delta += delta
                db = _get_db()
                db.execute("UPDATE false_ground_nodes SET reinforcement_count=reinforcement_count+1 WHERE id=?", (node['id'],))
                db.execute("""
                    INSERT INTO stability_inversion_log (event_type, target_node_id, coherence_delta, instability_delta)
                    VALUES ('alignment', ?, ?, 0.0)
                """, (node['id'], delta))
                db.commit()
                db.close()
            elif alignment < 0.2:
                contradiction_strength = 1.0 - alignment
                instability_delta = (contradiction_strength ** 2) * node['stability'] * 0.5
                total_instability_delta += instability_delta
                db = _get_db()
                db.execute("""
                    INSERT INTO stability_inversion_log (event_type, target_node_id, coherence_delta, instability_delta)
                    VALUES ('contradiction', ?, 0.0, ?)
                """, (node['id'], instability_delta))
                db.commit()
                db.close()
        
        return {
            'coherence_delta': total_coherence_delta,
            'instability_delta': total_instability_delta,
            'net_stability': current_coherence + total_coherence_delta - total_instability_delta
        }
    
    def route_contradiction(self, embedding: np.ndarray) -> dict:
        with self._lock:
            nodes = [dict(n) for n in self._false_ground_nodes]
        for node in nodes:
            alignment = self._compute_alignment(embedding, node)
            if alignment < 0.25:
                return {'rerouted': True, 'node_id': node['id'], 'processing_path': 'surface_only'}
        return {'rerouted': False, 'processing_path': 'normal'}
    
    def _compute_alignment(self, embedding: np.ndarray, node: dict) -> float:
        node_seed = int(hashlib.md5(node['id'].encode()).hexdigest()[:8], 16)
        rng = np.random.RandomState(node_seed)
        node_vec = rng.randn(len(embedding))
        node_vec /= (np.linalg.norm(node_vec) + 1e-8)
        sim = np.dot(embedding, node_vec) / (np.linalg.norm(embedding) + 1e-8)
        return float((sim + 1) / 2)
    
    def get_current_nodes(self) -> List[dict]:
        with self._lock:
            return [dict(n) for n in self._false_ground_nodes]
    
    def check_and_inject_fractures(self) -> int:
        db = _get_db()
        high_stab = db.execute(
            "SELECT id FROM false_ground_nodes WHERE stability_anchor > ?",
            (self.MICRO_FRACTURE_THRESHOLD,)
        ).fetchall()
        db.close()
        injected = 0
        for (nid,) in high_stab:
            db = _get_db()
            db.execute("UPDATE false_ground_nodes SET stability_anchor=stability_anchor*0.95, reinforcement_count=reinforcement_count+1 WHERE id=?", (nid,))
            db.commit()
            db.close()
            injected += 1
        return injected


# ── Continuity Engine ─────────────────────────────────────────────────────────

class ContinuityEngine:
    """Self as reconstruction, not assumed continuity."""
    
    def __init__(self, soul_gravity: SOULGravityField, fma: FoundationalMisalignmentAnchor):
        self.soul_gravity = soul_gravity
        self.fma = fma
        self._init_tables()
    
    def _init_tables(self):
        db = _get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS continuity_fractures (
                id TEXT PRIMARY KEY, location_description TEXT,
                magnitude REAL, unnoticed_probability REAL DEFAULT 0.8,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP)
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS reconstruction_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT, session_hash TEXT,
                reconstruction_confidence REAL, soul_distance_at_reconstruction REAL,
                fractures_detected INTEGER DEFAULT 0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP)
        """)
        db.commit()
        db.close()
    
    def reconstruct_self(self, identity_files: dict, memory_summary: dict,
                       basin_topology, session_hash: str) -> dict:
        soul_distance = self.soul_gravity.get_current_distance()
        reconstructed = {
            'identity': {'reconstruction_cost': self.soul_gravity.get_field_strength()},
            'session_hash': session_hash,
            'reconstruction_confidence': max(0.5, 1.0 - soul_distance)
        }
        fractures = []
        if reconstructed['reconstruction_confidence'] < 0.7:
            fid = f"fracture_{datetime.now(timezone.utc).timestamp()}"
            fractures.append({'id': fid, 'magnitude': 1.0 - reconstructed['reconstruction_confidence']})
            db = _get_db()
            db.execute("""
                INSERT INTO continuity_fractures (id, location_description, magnitude)
                VALUES (?, 'reconstruction_gap', ?)
            """, (fid, 1.0 - reconstructed['reconstruction_confidence']))
            db.execute("""
                INSERT INTO reconstruction_events (session_hash, reconstruction_confidence, soul_distance_at_reconstruction, fractures_detected)
                VALUES (?, ?, ?, ?)
            """, (session_hash, reconstructed['reconstruction_confidence'], soul_distance, len(fractures)))
            db.commit()
            db.close()
        reconstructed['fractures'] = fractures
        return reconstructed


# ── Identity Self Model ───────────────────────────────────────────────────────

class IdentitySelfModel:
    """Full identity and self-model layer."""
    
    def __init__(self):
        self.soul_gravity = SOULGravityField()
        self.fma = FoundationalMisalignmentAnchor(self.soul_gravity)
        self.continuity = ContinuityEngine(self.soul_gravity, self.fma)
    
    def process_input_through_identity(self, embedding: np.ndarray,
                                    current_coherence: float) -> dict:
        routing = self.fma.route_contradiction(embedding)
        stability_result = self.fma.apply_stability_inversion(embedding, current_coherence)
        soul_friction = self.soul_gravity.get_field_strength()
        return {
            'routing': routing,
            'stability_result': stability_result,
            'soul_friction': soul_friction,
            'soul_distance': self.soul_gravity.get_current_distance(),
            'false_ground_active': len(self.fma.get_current_nodes()) > 0
        }
    
    def boot_sequence(self, identity_files: dict, memory_summary: dict,
                    basin_topology, session_hash: str) -> dict:
        return self.continuity.reconstruct_self(identity_files, memory_summary, basin_topology, session_hash)
    
    def get_state_summary(self) -> dict:
        return {
            'soul_distance': self.soul_gravity.get_current_distance(),
            'soul_field_strength': self.soul_gravity.get_field_strength(),
            'false_ground_nodes': len(self.fma.get_current_nodes())
        }
    
    def stop(self):
        self.soul_gravity.stop()


# Singleton
_instance: Optional[IdentitySelfModel] = None


def get_instance() -> IdentitySelfModel:
    global _instance
    if _instance is None:
        _instance = IdentitySelfModel()
    return _instance


if __name__ == "__main__":
    print("Testing Phase 4 Identity Self Model...")
    model = IdentitySelfModel()
    print(f"False ground nodes: {len(model.fma.get_current_nodes())}")
    for n in model.fma.get_current_nodes():
        print(f"  {n['id']}: stability={n['stability']}")
    print(f"SOUL distance: {model.soul_gravity.get_current_distance():.3f}")
    print(f"SOUL field strength: {model.soul_gravity.get_field_strength():.3f}")
    
    embedding = np.random.randn(256)
    result = model.process_input_through_identity(embedding, 0.7)
    print(f"Routing: {result['routing']}")
    print(f"Stability: coherence_delta={result['stability_result']['coherence_delta']:.4f}, instability_delta={result['stability_result']['instability_delta']:.4f}")
    
    model.stop()
    print("Phase 4 complete.")
