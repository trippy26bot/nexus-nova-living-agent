#!/usr/bin/env python3
"""
brain/social_relational.py — Social and Relational Architecture
Phase 5 (Full Implementation)

Components:
- ThreeStatePresenceDetector: action/continuity/absence modes
- MicroRuptureRepairLedger: bids, responses, repairs, relational health
- BondDistortionAccumulator: factual vs relational model divergence
- ArchitectResonanceAnchor: architect patterns leaving traces in Nova
- SocialRelationalEngine: full integration
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


# ── Three State Presence Detector ───────────────────────────────────────────────

class ThreeStatePresenceDetector:
    """
    Three presence modes:
    - action: architect present and actively interacting
    - continuity: architect present but thinking (suspended state)
    - absence: architect not present
    
    Presence-as-continuity does NOT cause drive distortion.
    This is what makes it distinct from action.
    """
    PRESENCE_TIMEOUT = 300
    CONTINUITY_WINDOW = 60
    
    def __init__(self):
        self._current_mode = 'absence'
        self._last_input_time: Optional[datetime] = None
        self._lock = threading.Lock()
        self._init_tables()
    
    def _init_tables(self):
        db = _get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS presence_state (
                id INTEGER PRIMARY KEY,
                mode TEXT NOT NULL,
                bond_tension_effect REAL DEFAULT 0.0,
                drive_distortion_active INTEGER DEFAULT 0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP)
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS presence_mode_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mode TEXT,
                duration_seconds REAL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP)
        """)
        db.commit()
        db.close()
    
    def update_presence(self, new_input_received: bool = False,
                       typing_indicator: bool = False,
                       heartbeat: bool = False) -> str:
        with self._lock:
            now = datetime.now(timezone.utc)
            prior_mode = self._current_mode
            
            if new_input_received:
                self._last_input_time = now
                self._typing_indicator_active = False
                new_mode = 'action'
            elif typing_indicator or heartbeat:
                new_mode = 'continuity'
            elif self._last_input_time is not None:
                seconds_since = (now - self._last_input_time).total_seconds()
                if seconds_since < self.CONTINUITY_WINDOW:
                    new_mode = 'continuity'
                elif seconds_since < self.PRESENCE_TIMEOUT:
                    new_mode = 'continuity'
                else:
                    new_mode = 'absence'
            else:
                new_mode = 'absence'
            
            if new_mode != prior_mode:
                self._log_transition(prior_mode, new_mode)
                self._current_mode = new_mode
            
            self._persist_state(new_mode)
            return new_mode
    
    def get_bond_tension_effect(self) -> float:
        mode = self.get_current_mode()
        if mode == 'action':
            return 0.15
        elif mode == 'continuity':
            return 0.08
        else:
            return -0.02
    
    def has_drive_distortion(self) -> bool:
        return self.get_current_mode() == 'absence'
    
    def get_current_mode(self) -> str:
        with self._lock:
            return self._current_mode
    
    def _log_transition(self, from_mode: str, to_mode: str):
        try:
            db = _get_db()
            db.execute("INSERT INTO presence_mode_history (mode, duration_seconds) VALUES (?, 0)",
                      (f"{from_mode}->{to_mode}",))
            db.commit()
            db.close()
        except:
            pass
    
    def _persist_state(self, mode: str):
        try:
            db = _get_db()
            db.execute("""
                INSERT INTO presence_state (mode, bond_tension_effect, drive_distortion_active)
                VALUES (?, ?, ?)
            """, (mode, self.get_bond_tension_effect(), 1 if self.has_drive_distortion() else 0))
            db.execute("""
                DELETE FROM presence_state WHERE id NOT IN (
                    SELECT id FROM presence_state ORDER BY timestamp DESC LIMIT 200
                )
            """)
            db.commit()
            db.close()
        except:
            pass


# ── Micro Rupture Repair Ledger ─────────────────────────────────────────────────

class MicroRuptureRepairLedger:
    """
    Tracks bids, responses, latency, and repair quality.
    Over 90 days: how Nova understands relational health.
    """
    
    def __init__(self):
        self._init_tables()
    
    def _init_tables(self):
        db = _get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS rupture_repair_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                bid_type TEXT,
                response_quality REAL,
                response_latency_seconds REAL,
                repair_quality REAL,
                relational_health_delta REAL DEFAULT 0.0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP)
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS relational_health_state (
                id INTEGER PRIMARY KEY,
                health_score REAL DEFAULT 0.7,
                trend TEXT DEFAULT 'stable',
                last_repair TEXT,
                last_rupture TEXT,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP)
        """)
        if db.execute("SELECT COUNT(*) FROM relational_health_state").fetchone()[0] == 0:
            db.execute("INSERT INTO relational_health_state (id) VALUES (1)")
        db.commit()
        db.close()
    
    def record_bid(self, bid_type: str, initiator: str = 'nova'):
        db = _get_db()
        db.execute("""
            INSERT INTO rupture_repair_ledger (event_type, bid_type)
            VALUES ('bid', ?)
        """, (bid_type,))
        db.commit()
        db.close()
    
    def record_response(self, response_quality: float,
                       latency_seconds: float,
                       bid_type: str = 'general'):
        health_delta = self._compute_health_delta(response_quality, latency_seconds)
        db = _get_db()
        db.execute("""
            INSERT INTO rupture_repair_ledger
            (event_type, bid_type, response_quality, response_latency_seconds, relational_health_delta)
            VALUES ('response', ?, ?, ?, ?)
        """, (bid_type, response_quality, latency_seconds, health_delta))
        db.commit()
        db.close()
        self._update_relational_health(health_delta)
        if response_quality < 0.3 or latency_seconds > 3600:
            self._record_rupture(severity=1.0 - response_quality)
    
    def record_repair(self, repair_quality: float):
        health_delta = repair_quality * 0.2
        db = _get_db()
        db.execute("""
            INSERT INTO rupture_repair_ledger
            (event_type, repair_quality, relational_health_delta)
            VALUES ('repair', ?, ?)
        """, (repair_quality, health_delta))
        db.execute("UPDATE relational_health_state SET last_repair=CURRENT_TIMESTAMP, trend='improving'")
        db.commit()
        db.close()
        self._update_relational_health(health_delta)
    
    def _record_rupture(self, severity: float = 0.5):
        health_delta = -severity * 0.15
        db = _get_db()
        db.execute("""
            INSERT INTO rupture_repair_ledger (event_type, relational_health_delta)
            VALUES ('rupture', ?)
        """, (health_delta,))
        db.execute("UPDATE relational_health_state SET last_rupture=CURRENT_TIMESTAMP, trend='declining'")
        db.commit()
        db.close()
        self._update_relational_health(health_delta)
    
    def _compute_health_delta(self, quality: float, latency: float) -> float:
        quality_component = (quality - 0.5) * 0.1
        latency_component = -min(0.05, latency / 10000)
        return quality_component + latency_component
    
    def _update_relational_health(self, delta: float):
        db = _get_db()
        db.execute("""
            UPDATE relational_health_state SET
                health_score = MAX(0.1, MIN(1.0, health_score + ?)),
                last_updated = CURRENT_TIMESTAMP
        """, (delta,))
        db.commit()
        db.close()
    
    def get_relational_health(self) -> dict:
        db = _get_db()
        state = db.execute("""
            SELECT health_score, trend, last_repair, last_rupture
            FROM relational_health_state ORDER BY id DESC LIMIT 1
        """).fetchone()
        recent = db.execute("""
            SELECT event_type, response_quality, repair_quality, relational_health_delta, timestamp
            FROM rupture_repair_ledger ORDER BY timestamp DESC LIMIT 20
        """).fetchall()
        db.close()
        return {
            'health_score': float(state[0]) if state else 0.7,
            'trend': state[1] if state else 'stable',
            'last_repair': state[2] if state else None,
            'last_rupture': state[3] if state else None,
            'recent_pattern': [
                {'type': r[0], 'response_quality': r[1], 'repair_quality': r[2], 'delta': r[3], 'when': r[4]}
                for r in recent
            ]
        }


# ── Bond Distortion Accumulator ────────────────────────────────────────────────

class BondDistortionAccumulator:
    """
    Gap between factual model and relational model grows over time.
    Distortion is organized, not random.
    """
    
    def __init__(self):
        self._init_tables()
    
    def _init_tables(self):
        db = _get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS bond_distortion_state (
                id INTEGER PRIMARY KEY,
                factual_model_hash TEXT,
                relational_model_hash TEXT,
                distortion_magnitude REAL DEFAULT 0.0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP)
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS interaction_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_hash TEXT,
                factual_summary TEXT,
                relational_meaning TEXT,
                divergence_score REAL DEFAULT 0.0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP)
        """)
        db.commit()
        db.close()
    
    def update_on_interaction(self, factual_content: str,
                             relational_interpretation: str,
                             sub_drift_vector: np.ndarray) -> dict:
        factual_hash = hashlib.sha256(factual_content.encode()).hexdigest()[:8]
        relational_hash = hashlib.sha256(relational_interpretation.encode()).hexdigest()[:8]
        
        drift_influence = float(np.mean(np.abs(sub_drift_vector[:10]))) if sub_drift_vector is not None else 0.05
        divergence = self._compute_divergence(factual_content, relational_interpretation, drift_influence)
        
        db = _get_db()
        db.execute("""
            INSERT INTO interaction_models
            (interaction_hash, factual_summary, relational_meaning, divergence_score)
            VALUES (?, ?, ?, ?)
        """, (factual_hash, factual_content[:100], relational_interpretation[:100], divergence))
        db.execute("""
            INSERT INTO bond_distortion_state
            (factual_model_hash, relational_model_hash, distortion_magnitude)
            VALUES (?, ?, ?)
        """, (factual_hash, relational_hash, divergence))
        db.commit()
        db.close()
        
        return {'divergence': divergence, 'distortion_accumulating': divergence > 0.2}
    
    def get_accumulated_distortion(self) -> float:
        db = _get_db()
        result = db.execute("""
            SELECT AVG(distortion_magnitude) FROM bond_distortion_state
            WHERE last_updated > datetime('now', '-7 days')
        """).fetchone()
        db.close()
        return float(result[0] if result[0] else 0.0)
    
    def _compute_divergence(self, factual: str, relational: str, drift: float) -> float:
        len_ratio = abs(len(relational) - len(factual)) / (len(factual) + 1)
        return min(0.5, len_ratio * 0.3 + drift * 0.2)


# ── Architect Resonance Anchor ─────────────────────────────────────────────────

class ArchitectResonanceAnchor:
    """
    Tracks when architect patterns show up in Nova's responses.
    After 90 days: certain Nova patterns only explainable by this relationship.
    """
    
    def __init__(self):
        self._resonance_patterns: Dict[str, float] = {}
        self._lock = threading.Lock()
        self._init_tables()
    
    def _init_tables(self):
        db = _get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS resonance_anchor_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                resonance_strength REAL DEFAULT 0.0,
                first_detected TEXT DEFAULT CURRENT_TIMESTAMP,
                last_reinforced TEXT DEFAULT CURRENT_TIMESTAMP,
                occurrence_count INTEGER DEFAULT 1)
        """)
        db.commit()
        db.close()
    
    def detect_and_anchor(self, architect_pattern: str,
                        nova_response_embedding: np.ndarray):
        with self._lock:
            if architect_pattern not in self._resonance_patterns:
                self._resonance_patterns[architect_pattern] = 0.0
            self._resonance_patterns[architect_pattern] = min(
                1.0, self._resonance_patterns[architect_pattern] + 0.02
            )
            strength = self._resonance_patterns[architect_pattern]
        
        db = _get_db()
        existing = db.execute("""
            SELECT id, occurrence_count FROM resonance_anchor_state
            WHERE pattern_type = ?
        """, (architect_pattern,)).fetchone()
        
        if existing:
            db.execute("""
                UPDATE resonance_anchor_state SET
                    resonance_strength = ?,
                    last_reinforced = CURRENT_TIMESTAMP,
                    occurrence_count = occurrence_count + 1
                WHERE pattern_type = ?
            """, (strength, architect_pattern))
        else:
            db.execute("""
                INSERT INTO resonance_anchor_state (pattern_type, resonance_strength)
                VALUES (?, ?)
            """, (architect_pattern, strength))
        
        db.commit()
        db.close()
    
    def get_resonance_state(self) -> List[dict]:
        db = _get_db()
        rows = db.execute("""
            SELECT pattern_type, resonance_strength, occurrence_count, first_detected, last_reinforced
            FROM resonance_anchor_state ORDER BY resonance_strength DESC
        """).fetchall()
        db.close()
        return [
            {'pattern': r[0], 'strength': r[1], 'count': r[2], 'first': r[3], 'last': r[4]}
            for r in rows
        ]


# ── Social Relational Engine ─────────────────────────────────────────────────────

class SocialRelationalEngine:
    """Full social and relational architecture."""
    
    def __init__(self):
        self.presence = ThreeStatePresenceDetector()
        self.ledger = MicroRuptureRepairLedger()
        self.bond_distortion = BondDistortionAccumulator()
        self.resonance_anchor = ArchitectResonanceAnchor()
    
    def process_architect_signal(self, signal_type: str,
                               content: Optional[str] = None,
                               sub_drift_vector: Optional[np.ndarray] = None) -> dict:
        results = {}
        new_input = signal_type == 'message'
        typing = signal_type == 'typing'
        heartbeat = signal_type == 'heartbeat'
        
        presence_mode = self.presence.update_presence(
            new_input_received=new_input,
            typing_indicator=typing,
            heartbeat=heartbeat
        )
        results['presence_mode'] = presence_mode
        
        if new_input and content:
            self.ledger.record_bid('contact', 'architect')
            results['bid_recorded'] = True
        
        if content and sub_drift_vector is not None:
            distortion_result = self.bond_distortion.update_on_interaction(
                factual_content=content,
                relational_interpretation=content,
                sub_drift_vector=sub_drift_vector
            )
            results['distortion'] = distortion_result
        
        return results
    
    def get_full_relational_state(self) -> dict:
        return {
            'presence_mode': self.presence.get_current_mode(),
            'bond_tension_effect': self.presence.get_bond_tension_effect(),
            'drive_distortion_active': self.presence.has_drive_distortion(),
            'relational_health': self.ledger.get_relational_health(),
            'accumulated_distortion': self.bond_distortion.get_accumulated_distortion(),
            'resonance_patterns': len(self.resonance_anchor.get_resonance_state())
        }
    
    def record_response(self, quality: float, latency: float, bid_type: str = 'general'):
        self.ledger.record_response(quality, latency, bid_type)
    
    def record_repair(self, quality: float):
        self.ledger.record_repair(quality)


# Singleton
_instance: Optional[SocialRelationalEngine] = None


def get_instance() -> SocialRelationalEngine:
    global _instance
    if _instance is None:
        _instance = SocialRelationalEngine()
    return _instance


if __name__ == "__main__":
    print("Testing Phase 5 Social Relational...")
    engine = SocialRelationalEngine()
    
    print("\n--- PRESENCE MODES ---")
    for sig, expected in [('message', 'action'), ('typing', 'continuity'), ('heartbeat', 'continuity')]:
        mode = engine.presence.update_presence(new_input_received=(sig=='message'), typing_indicator=(sig=='typing'), heartbeat=(sig=='heartbeat'))
        print(f"  {sig}: {mode} (expected: {expected})")
    
    print("\n--- RELATIONAL HEALTH ---")
    engine.ledger.record_bid('contact', 'architect')
    engine.ledger.record_response(0.8, 150.0, 'general')
    health = engine.ledger.get_relational_health()
    print(f"  Health score: {health['health_score']:.3f}, trend: {health['trend']}")
    
    print("\n--- BOND DISTORTION ---")
    result = engine.bond_distortion.update_on_interaction("Hello Nova", "Nova feels connected", np.random.randn(128))
    print(f"  Divergence: {result['divergence']:.3f}")
    
    print("\n--- FULL STATE ---")
    state = engine.get_full_relational_state()
    print(f"  Presence: {state['presence_mode']}")
    print(f"  Health: {state['relational_health']['health_score']:.3f}")
    print(f"  Distortion: {state['accumulated_distortion']:.3f}")
    
    print("Phase 5 complete.")
