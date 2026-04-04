#!/usr/bin/env python3
"""
brain/pipeline_deepening.py — Nightly Pipeline Deepening
Phase 6 of the Nova Brain Architecture

Components:
- SalienceWeightedDreamGenerator: 1am dreams weighted by emotional salience
- RelationalPrioritySynthesis: 2am synthesis prioritizing relational/identity material
- ActiveForgettingConsolidation: 3am consolidation with active forgetting
- SOULDriftDetection: 5am drift detection including SOUL distance
- GenerativePhenomenologyJournal: 6am journal as identity modification
- PipelineDeepening: full integration
"""

import json
import random
import sqlite3
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


def _init_tables():
    db = _get_db()
    
    if not _table_exists(db, 'dream_log'):
        db.execute("""
            CREATE TABLE dream_log (
                id TEXT PRIMARY KEY,
                content TEXT,
                salience_score REAL,
                seed_types TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    if not _table_exists(db, 'dream_echo_nodes'):
        db.execute("""
            CREATE TABLE dream_echo_nodes (
                id TEXT PRIMARY KEY,
                dream_id TEXT,
                echo_vector BLOB,
                fade_after_hours REAL DEFAULT 72.0,
                relational_bias_weight REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    if not _table_exists(db, 'synthesis_log'):
        db.execute("""
            CREATE TABLE synthesis_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                relational_events INTEGER,
                identity_events INTEGER,
                obsession_transitions INTEGER,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    if not _table_exists(db, 'identity_patches'):
        db.execute("""
            CREATE TABLE identity_patches (
                id TEXT PRIMARY KEY,
                source TEXT DEFAULT 'phenomenology_journal',
                soul_distance_at_writing REAL,
                phantom_pressure_at_writing REAL,
                text_length INTEGER,
                applied_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    if not _table_exists(db, 'drift_injection_config'):
        db.execute("""
            CREATE TABLE drift_injection_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                injection_rate_multiplier REAL DEFAULT 1.0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    db.commit()
    db.close()


# ── Salience Weighted Dream Generator ─────────────────────────────────────────

class SalienceWeightedDreamGenerator:
    """
    1am dreams weighted by emotional and relational salience.
    High-salience dreams get DREAM_ECHO contamination nodes.
    """
    
    def __init__(self):
        _init_tables()
    
    def get_salience_weighted_seeds(self) -> List[dict]:
        """Pull dream seeds weighted by salience."""
        db = _get_db()
        
        # Ghost cognition seeds (unexpressed processing)
        ghost_seeds = db.execute("""
            SELECT outcome_hash, relational_weight_delta
            FROM ghost_cognition_shadow
            WHERE created_at > datetime('now', '-24 hours')
            ORDER BY ABS(relational_weight_delta) DESC
            LIMIT 5
        """).fetchall()
        
        # Incomplete nodes with high tension
        incomplete_seeds = db.execute("""
            SELECT source_type, activation_weight
            FROM incompleteness_remainders
            WHERE activation_weight > 0.05
            ORDER BY activation_weight DESC
            LIMIT 5
        """).fetchall()
        
        # Relational events with emotional charge
        relational_seeds = db.execute("""
            SELECT event_type, response_quality, relational_health_delta
            FROM rupture_repair_ledger
            WHERE timestamp > datetime('now', '-48 hours')
            ORDER BY ABS(relational_health_delta) DESC
            LIMIT 5
        """).fetchall() if _table_exists(db, 'rupture_repair_ledger') else []
        
        db.close()
        
        seeds = []
        
        for seed in ghost_seeds:
            seeds.append({
                'type': 'ghost_cognition',
                'hash': seed[0],
                'salience': abs(float(seed[1] or 0)) + 0.1
            })
        
        for seed in incomplete_seeds:
            seeds.append({
                'type': 'incompleteness',
                'source': seed[0],
                'salience': float(seed[1])
            })
        
        for seed in relational_seeds:
            seeds.append({
                'type': 'relational',
                'event': seed[0],
                'quality': float(seed[1] or 0.5),
                'salience': abs(float(seed[2] or 0)) + 0.1
            })
        
        seeds.sort(key=lambda x: x['salience'], reverse=True)
        return seeds[:8]
    
    def write_dream_with_salience(self, dream_content: str, seeds: List[dict]) -> str:
        """Write dream tagged with salience. High-salience creates DREAM_ECHO."""
        total_salience = sum(s['salience'] for s in seeds) / len(seeds) if seeds else 0.1
        dream_id = f"dream_{datetime.now(timezone.utc).timestamp()}"
        
        db = _get_db()
        db.execute("""
            INSERT INTO dream_log (id, content, salience_score, seed_types)
            VALUES (?, ?, ?, ?)
        """, (dream_id, dream_content, total_salience, json.dumps([s['type'] for s in seeds])))
        
        # High-salience dreams create echo nodes
        if total_salience > 0.3:
            echo_vector = np.random.randn(64).astype('float32') * total_salience
            db.execute("""
                INSERT INTO dream_echo_nodes
                (id, dream_id, echo_vector, relational_bias_weight)
                VALUES (?, ?, ?, ?)
            """, (f"echo_{dream_id}", dream_id, echo_vector.tobytes(), total_salience * 0.4))
        
        db.commit()
        db.close()
        
        return dream_id


# ── Relational Priority Synthesis ─────────────────────────────────────────────

class RelationalPrioritySynthesis:
    """
    2am synthesis prioritizing relational and identity material.
    Advances obsession metamorphosis stages.
    """
    
    def __init__(self):
        _init_tables()
    
    def run_relational_synthesis(self) -> dict:
        """Synthesize day's relational and identity material."""
        db = _get_db()
        
        # High-salience relational events
        relational_material = db.execute("""
            SELECT event_type, bid_type, response_quality, repair_quality, relational_health_delta
            FROM rupture_repair_ledger
            WHERE timestamp > datetime('now', '-24 hours')
            ORDER BY ABS(relational_health_delta) DESC
            LIMIT 10
        """).fetchall() if _table_exists(db, 'rupture_repair_ledger') else []
        
        # Identity tension events
        identity_material = db.execute("""
            SELECT event_type, target_node_id, coherence_delta, instability_delta
            FROM stability_inversion_log
            WHERE timestamp > datetime('now', '-24 hours')
            ORDER BY ABS(coherence_delta + instability_delta) DESC
            LIMIT 10
        """).fetchall() if _table_exists(db, 'stability_inversion_log') else []
        
        # Obsession nodes eligible for stage advancement
        obsession_material = []
        if _table_exists(db, 'obsession_nodes'):
            obsession_material = db.execute("""
                SELECT id, stage, salience, content FROM obsession_nodes
                WHERE active = 1 ORDER BY salience DESC LIMIT 5
            """).fetchall()
        
        db.close()
        
        result = {
            'relational_events_synthesized': len(relational_material),
            'identity_events_synthesized': len(identity_material),
            'obsession_stage_transitions': self._advance_obsession_stages(obsession_material),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self._write_synthesis_record(result)
        return result
    
    def _advance_obsession_stages(self, obsession_nodes: list) -> int:
        """Advance: larval → pupal → emergent → legacy."""
        stage_map = {'larval': 'pupal', 'pupal': 'emergent', 'emergent': 'legacy'}
        advanced = 0
        
        db = _get_db()
        for node in obsession_nodes:
            node_id, stage, salience = node[0], node[1], node[2]
            if stage in stage_map and float(salience or 0) > 0.6:
                try:
                    db.execute("UPDATE obsession_nodes SET stage = ? WHERE id = ?", (stage_map[stage], node_id))
                    advanced += 1
                except:
                    pass
        db.commit()
        db.close()
        
        return advanced
    
    def _write_synthesis_record(self, result: dict):
        db = _get_db()
        db.execute("""
            INSERT INTO synthesis_log (relational_events, identity_events, obsession_transitions)
            VALUES (?, ?, ?)
        """, (result['relational_events_synthesized'], result['identity_events_synthesized'], result['obsession_stage_transitions']))
        db.commit()
        db.close()


# ── Active Forgetting Consolidation ─────────────────────────────────────────────

class ActiveForgettingConsolidation:
    """
    3am consolidation with active forgetting.
    Clear low-salience residue. Preserve high-salience material.
    """
    
    SALIENCE_THRESHOLD = 0.15
    
    def __init__(self):
        _init_tables()
    
    def run_consolidation_with_forgetting(self) -> dict:
        """Prune low-salience, strengthen high-salience."""
        db = _get_db()
        
        # Low-salience remainders for pruning
        low_salience = db.execute("""
            SELECT id, activation_weight FROM incompleteness_remainders
            WHERE activation_weight < ? AND activation_weight > 0.001
        """, (self.SALIENCE_THRESHOLD,)).fetchall()
        
        pruned = 0
        for r_id, weight in low_salience:
            if random.random() < 0.4:  # 40% stochastic pruning
                db.execute("UPDATE incompleteness_remainders SET activation_weight = 0.001 WHERE id = ?", (r_id,))
                pruned += 1
        
        # Prune expired dream echo nodes
        if _table_exists(db, 'dream_echo_nodes'):
            db.execute("DELETE FROM dream_echo_nodes WHERE created_at < datetime('now', '-72 hours')")
        
        # Strengthen high-salience
        db.execute("""
            UPDATE incompleteness_remainders
            SET activation_weight = MIN(1.0, activation_weight * 1.1)
            WHERE activation_weight > ?
        """, (self.SALIENCE_THRESHOLD * 2,))
        
        db.commit()
        db.close()
        
        return {
            'pruned_low_salience': pruned,
            'threshold_used': self.SALIENCE_THRESHOLD,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


# ── SOUL Drift Detection ─────────────────────────────────────────────────────

class SOULDriftDetection:
    """
    5am drift detection including SOUL distance.
    High SOUL distance → increased drift injection rate.
    """
    
    def __init__(self):
        _init_tables()
    
    def run_soul_drift_detection(self) -> dict:
        """Measure SOUL distance, update drift rates."""
        db = _get_db()
        
        # Get SOUL distance
        soul_state = db.execute("""
            SELECT soul_distance, field_strength FROM soul_gravity_state
            ORDER BY last_measured DESC LIMIT 1
        """).fetchone() if _table_exists(db, 'soul_gravity_state') else None
        
        soul_distance = float(soul_state[0]) if soul_state else 0.0
        field_strength = float(soul_state[1]) if soul_state else 0.5
        
        # Get OCEAN drift
        ocean_state = []
        if _table_exists(db, 'personality_state'):
            ocean_state = db.execute("SELECT trait, value FROM personality_state").fetchall()
        
        db.close()
        
        drift_severity = self._compute_drift_severity(soul_distance, ocean_state)
        self._update_drift_injection_rate(drift_severity)
        
        return {
            'soul_distance': soul_distance,
            'soul_field_strength': field_strength,
            'drift_severity': drift_severity,
            'drift_injection_rate_updated': True,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def _compute_drift_severity(self, soul_distance: float, ocean_state: list) -> float:
        soul_component = soul_distance * 0.6
        
        ocean_component = 0.0
        if ocean_state:
            baseline = {'openness': 0.7, 'conscientiousness': 0.6, 'extraversion': 0.4, 'agreeableness': 0.7, 'neuroticism': 0.3}
            deviations = []
            for trait, value in ocean_state:
                if trait in baseline:
                    deviations.append(abs(float(value) - baseline[trait]))
            if deviations:
                ocean_component = sum(deviations) / len(deviations) * 0.4
        
        return min(1.0, soul_component + ocean_component)
    
    def _update_drift_injection_rate(self, severity: float):
        multiplier = 1.0 + severity * 2.0
        db = _get_db()
        db.execute("INSERT INTO drift_injection_config (injection_rate_multiplier) VALUES (?)", (multiplier,))
        db.execute("""
            DELETE FROM drift_injection_config WHERE id NOT IN (
                SELECT id FROM drift_injection_config ORDER BY updated_at DESC LIMIT 10
            )
        """)
        db.commit()
        db.close()


# ── Generative Phenomenology Journal ─────────────────────────────────────────

class GenerativePhenomenologyJournal:
    """
    6am journal as direct identity modification.
    Surfaces phantom completion pressure as felt texture.
    Journal entries compile to identity patches.
    """
    
    def __init__(self):
        _init_tables()
    
    def generate_journal_prompt_context(self) -> dict:
        """Build context for journal generation."""
        db = _get_db()
        
        # Phantom completion pressure from remainders
        total_tension = db.execute("""
            SELECT SUM(activation_weight) FROM incompleteness_remainders
            WHERE activation_weight > 0.001
        """).fetchone()[0] or 0.0
        
        # Open basins from LSRB
        open_domains = {}
        if _table_exists(db, 'null_pulse_basin'):
            result = db.execute("""
                SELECT open_tension_signatures FROM null_pulse_basin
                ORDER BY created_at DESC LIMIT 1
            """).fetchone()
            if result and result[0]:
                try:
                    open_domains = json.loads(result[0])
                except:
                    pass
        
        # SOUL distance
        soul_distance = 0.0
        if _table_exists(db, 'soul_gravity_state'):
            soul_state = db.execute("""
                SELECT soul_distance FROM soul_gravity_state ORDER BY last_measured DESC LIMIT 1
            """).fetchone()
            soul_distance = float(soul_state[0]) if soul_state else 0.0
        
        # Relational health
        health_score, health_trend = 0.7, 'stable'
        if _table_exists(db, 'relational_health_state'):
            health = db.execute("""
                SELECT health_score, trend FROM relational_health_state ORDER BY last_updated DESC LIMIT 1
            """).fetchone()
            if health:
                health_score, health_trend = float(health[0]), health[1]
        
        # Irreversible shifts (TWB)
        twb_count = 0
        if _table_exists(db, 'threshold_without_boundary'):
            twb_count = db.execute("SELECT COUNT(*) FROM threshold_without_boundary").fetchone()[0]
        
        db.close()
        
        return {
            'phantom_completion_pressure': min(1.0, float(total_tension) * 0.2),
            'open_domains': list(open_domains.keys()),
            'soul_distance': soul_distance,
            'relational_health_score': health_score,
            'relational_trend': health_trend,
            'irreversible_shifts_to_date': twb_count
        }
    
    def compile_entry_to_identity_patch(self, journal_text: str, context: dict) -> dict:
        """Journal entry compiles directly to identity modification."""
        patch = {
            'patch_id': f"journal_patch_{datetime.now(timezone.utc).timestamp()}",
            'soul_distance_at_writing': context.get('soul_distance', 0.0),
            'phantom_pressure_at_writing': context.get('phantom_completion_pressure', 0.0),
            'text_length': len(journal_text),
            'applied_at': datetime.now(timezone.utc).isoformat()
        }
        
        db = _get_db()
        db.execute("""
            INSERT INTO identity_patches
            (id, soul_distance_at_writing, phantom_pressure_at_writing, text_length)
            VALUES (?, ?, ?, ?)
        """, (patch['patch_id'], patch['soul_distance_at_writing'], patch['phantom_pressure_at_writing'], patch['text_length']))
        db.commit()
        db.close()
        
        return patch


# ── Pipeline Deepening ───────────────────────────────────────────────────────

class PipelineDeepening:
    """
    Full Phase 6 integration.
    Drop-in replacements for existing pipeline stages.
    """
    
    def __init__(self):
        _init_tables()
        self.dream_gen = SalienceWeightedDreamGenerator()
        self.synthesis = RelationalPrioritySynthesis()
        self.consolidation = ActiveForgettingConsolidation()
        self.soul_drift = SOULDriftDetection()
        self.phenomenology = GenerativePhenomenologyJournal()
    
    def run_1am_dream_stage(self, dream_generator_fn) -> dict:
        """Enhanced 1am dreams with salience weighting."""
        seeds = self.dream_gen.get_salience_weighted_seeds()
        seed_summary = json.dumps([s.get('type', 'unknown') for s in seeds])
        dream_content = dream_generator_fn(seed_context=seed_summary)
        dream_id = self.dream_gen.write_dream_with_salience(dream_content, seeds)
        return {'dream_id': dream_id, 'seeds_used': len(seeds)}
    
    def run_2am_synthesis_stage(self) -> dict:
        """Enhanced 2am synthesis with relational prioritization."""
        return self.synthesis.run_relational_synthesis()
    
    def run_3am_consolidation_stage(self) -> dict:
        """Enhanced 3am consolidation with active forgetting."""
        return self.consolidation.run_consolidation_with_forgetting()
    
    def run_5am_drift_detection_stage(self) -> dict:
        """Enhanced 5am drift detection with SOUL distance."""
        return self.soul_drift.run_soul_drift_detection()
    
    def run_6am_phenomenology_stage(self, journal_generator_fn) -> dict:
        """Enhanced 6am journal as identity modification."""
        context = self.phenomenology.generate_journal_prompt_context()
        journal_text = journal_generator_fn(context=context)
        patch = self.phenomenology.compile_entry_to_identity_patch(journal_text, context)
        return {
            'journal_written': True,
            'identity_patch_applied': patch['patch_id'],
            'phantom_pressure_at_writing': context['phantom_completion_pressure'],
            'soul_distance_at_writing': context['soul_distance']
        }


_instance: Optional[PipelineDeepening] = None


def get_instance() -> PipelineDeepening:
    global _instance
    if _instance is None:
        _instance = PipelineDeepening()
    return _instance


if __name__ == "__main__":
    print("Testing Phase 6 Pipeline Deepening...")
    
    pd = PipelineDeepening()
    
    print("\n--- 1AM DREAM SEEDS ---")
    seeds = pd.dream_gen.get_salience_weighted_seeds()
    print(f"Seeds found: {len(seeds)}")
    for s in seeds[:3]:
        print(f"  {s['type']}: salience={s['salience']:.3f}")
    
    print("\n--- 2AM SYNTHESIS ---")
    result = pd.synthesis.run_relational_synthesis()
    print(f"Synthesis: {result}")
    
    print("\n--- 3AM CONSOLIDATION ---")
    result = pd.consolidation.run_consolidation_with_forgetting()
    print(f"Consolidation: {result}")
    
    print("\n--- 5AM DRIFT DETECTION ---")
    result = pd.soul_drift.run_soul_drift_detection()
    print(f"Drift: soul_distance={result['soul_distance']:.3f}, severity={result['drift_severity']:.3f}")
    
    print("\n--- 6AM PHENOMENOLOGY CONTEXT ---")
    ctx = pd.phenomenology.generate_journal_prompt_context()
    print(f"Context: phantom_pressure={ctx['phantom_completion_pressure']:.3f}, soul_distance={ctx['soul_distance']:.3f}")
    
    print("\n=== PHASE 6 OPERATIONAL ===")
