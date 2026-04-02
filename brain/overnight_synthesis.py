#!/usr/bin/env python3
"""
brain/overnight_synthesis.py — Nova's Nightly Synthesis Pipeline
Tier 3: Wires all overnight processing together

Pipeline order:
1. Self-snapshot (continuity_engine) — who am I right now
2. Memory consolidation (three_tier_memory) — move episodes toward semantic
3. Belief crystallization (belief_forge) — form raw beliefs into convictions
4. Obsession Metamorphosis Cycle (Tier 3) — evaluate all obsession stage advances
5. Obsession-Belief Coupling (Tier 3) — check legacy obsessions → belief pipeline
6. Evolutionary Thought Decay (Tier 3) — clean thought pool, propose belief candidates
7. Curiosity Engine (Tier 3) — generate and attempt question resolution
8. Epistemic Tension Review (Tier 3) — age and flag unresolved tensions
9. Contradiction resolution — detect, evaluate, crystallize or resolve
10. Drift detection — check if identity is stable
11. Meaning Compression (Tier 3) — find memory clusters, create symbol nodes

Usage:
    python overnight_synthesis.py [phase]

Phases:
    full    — Run complete pipeline (default)
    digest  — Phase 1 only (night digest before sleep)
    synth   — Phase 2 only (overnight synthesis)
    morning — Phase 3 only (morning consolidation)
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/Users/dr.claw/.openclaw/workspace")
sys.path.insert(0, str(WORKSPACE))

NOVA_HOME = WORKSPACE / ".nova"
SLEEP_RUNS = NOVA_HOME / "sleep_runs.json"
DIGEST_DIR = NOVA_HOME / "overnight" / "digests"
SYNTHESIS_DIR = NOVA_HOME / "overnight" / "synthesis"


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _log_sleep_run(process_type: str, duration: float, completed: bool,
                   findings: list, flags: list):
    """Log a sleep run to sleep_runs.json."""
    SYNTHESIS_DIR.mkdir(parents=True, exist_ok=True)

    runs = []
    if SLEEP_RUNS.exists():
        try:
            runs = json.loads(SLEEP_RUNS.read_text()).get("runs", [])
        except Exception:
            runs = []

    runs.append({
        "timestamp": _now_iso(),
        "type": process_type,
        "duration_seconds": round(duration, 4),
        "completed": completed,
        "findings": findings,
        "flags": flags
    })

    # Keep last 100 runs
    runs = runs[-100:]
    SLEEP_RUNS.write_text(json.dumps({"runs": runs}, indent=2))


def _safe_run(name: str, fn, *args, **kwargs):
    """Run a function with timing and error handling."""
    start = datetime.now(timezone.utc)
    findings = []
    flags = []
    error = None

    try:
        result = fn(*args, **kwargs)
        if isinstance(result, dict) and "findings" in result:
            findings = result.get("findings", [])
            flags = result.get("flags", [])
        elif isinstance(result, list):
            findings = result
        return result, findings, flags
    except Exception as e:
        error = str(e)
        flags.append(f"error: {error}")
        return None, findings, flags
    finally:
        duration = (datetime.now(timezone.utc) - start).total_seconds()
        _log_sleep_run(name, duration, error is None, findings, flags)


# ── Phase 1: Night Digest ────────────────────────────────────────────────────

def night_digest() -> dict:
    """
    Phase 1: Before sleep — identify key events, extract changes.
    Output: digest file for the day.
    """
    from brain.continuity_engine import get_last_snapshot, get_top_beliefs

    findings = []
    flags = []

    # Get current state
    last_snapshot = get_last_snapshot()
    current_beliefs = get_top_beliefs(n=10)

    # Get high-salience episodic entries from today
    try:
        from brain.three_tier_memory import get_episodic_entries
        today_entries = get_episodic_entries(days=1, limit=20)
        key_events = [
            {"id": e["id"], "content": e.get("content", "")[:100], "salience": e.get("salience", 0)}
            for e in today_entries
            if e.get("salience", 0) >= 0.7
        ]
        findings.append(f"High-salience events today: {len(key_events)}")
    except Exception as e:
        key_events = []
        flags.append(f"Could not load episodic entries: {e}")

    # Get research queue status
    research_queue = []
    queue_file = NOVA_HOME / "research_queue.json"
    if queue_file.exists():
        try:
            research_queue = json.loads(queue_file.read_text()).get("queue", [])
        except Exception:
            pass

    # Build digest
    digest = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": _now_iso(),
        "key_events": key_events,
        "belief_changes": [],
        "open_questions": [],
        "research_queue_items": [q for q in research_queue if q.get("status") == "pending"],
        "going_into_sleep": "Processing the day's events.",
        "current_beliefs": current_beliefs
    }

    # Save digest
    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
    digest_file = DIGEST_DIR / f"digest_{datetime.now().strftime('%Y-%m-%d')}.json"
    digest_file.write_text(json.dumps(digest, indent=2))

    findings.append(f"Digest written: {digest_file.name}")
    findings.append(f"Beliefs: {len(current_beliefs)} active")

    return {"findings": findings, "flags": flags}


# ── Phase 2: Overnight Synthesis ─────────────────────────────────────────────

def overnight_synthesis() -> dict:
    """
    Phase 2: Main synthesis — runs after memory consolidation.
    Tier 3 pipeline order:
    1. Belief crystallization (belief_forge)
    2. Obsession Metamorphosis Cycle — evaluate all obsessions
    3. Obsession-Belief Coupling — check legacy obsessions → belief pipeline
    4. Evolutionary Thought Decay — clean thought pool
    5. Curiosity Engine — generate and attempt question resolution
    6. Epistemic Tension Review — age and flag unresolved tensions
    7. Contradiction resolution
    8. Drift detection
    9. Meaning Compression — find memory clusters, create symbol nodes
    """
    findings = []
    flags = []

    # Step 1: Belief crystallization
    findings.append("Starting belief crystallization...")
    try:
        from brain.belief_forge import crystallize_beliefs
        crystal_result, crystal_findings, crystal_flags = _safe_run(
            "belief_crystallization", crystallize_beliefs
        )
        if crystal_result:
            findings.append(f"Crystallization: {crystal_result['memories_processed']} memories, "
                          f"{crystal_result['clusters_formed']} clusters, "
                          f"{len(crystal_result['new_beliefs_proposed'])} new beliefs")
            findings.extend(crystal_findings)
            flags.extend(crystal_flags)
    except ImportError as e:
        findings.append("belief_forge not available yet")
        flags.append(f"belief_forge import error: {e}")

    # ── Tier 3: Obsession Metamorphosis Cycle ────────────────────────────────
    findings.append("Starting obsession metamorphosis evaluation...")
    try:
        from brain.obsession_engine import evaluate_all_metamorphoses
        meta_results, meta_findings, meta_flags = _safe_run(
            "obsession_metamorphosis", evaluate_all_metamorphoses
        )
        if meta_results:
            findings.append(f"Obsession metamorphosis: {len(meta_results)} advancements")
            for r in meta_results:
                findings.append(f"  [{r['old_stage']} → {r['new_stage']}] {r['topic']}: {r['reason']}")
            findings.extend(meta_findings)
            flags.extend(meta_flags)
    except Exception as e:
        flags.append(f"obsession_metamorphosis error: {e}")

    # ── Tier 3: Obsession-Belief Coupling ─────────────────────────────────────
    findings.append("Starting obsession-belief coupling...")
    try:
        from brain.belief_forge import check_obsession_to_belief_pipeline, check_belief_to_obsession_pipeline

        # Legacy obsession → belief pipeline
        obs2belief_result, obs2b_findings, obs2b_flags = _safe_run(
            "obsession_to_belief", check_obsession_to_belief_pipeline
        )
        if obs2belief_result:
            findings.append(f"Obsession→Belief: {obs2belief_result['legacy_obsessions_found']} legacy obs, "
                          f"{len(obs2belief_result['proposed_new'])} new beliefs proposed, "
                          f"{len(obs2belief_result['merged_with_existing'])} merged with existing")
            findings.extend(obs2b_findings)
            flags.extend(obs2b_flags)

        # Belief → obsession seed pipeline
        belief2obs_result, b2o_findings, b2o_flags = _safe_run(
            "belief_to_obsession", check_belief_to_obsession_pipeline
        )
        if belief2obs_result:
            findings.append(f"Belief→Obsession: {belief2obs_result['high_reinforcement_beliefs']} high-reinforcement beliefs, "
                          f"{len(belief2obs_result['flagged_for_curiosity'])} flagged as potential seeds")
            findings.extend(b2o_findings)
            flags.extend(b2o_flags)
    except Exception as e:
        flags.append(f"obsession_belief_coupling error: {e}")

    # ── Tier 3: Evolutionary Thought Decay ────────────────────────────────────
    findings.append("Starting evolutionary thought decay...")
    try:
        from brain.evolutionary_thoughts import decay_thoughts
        decay_result, decay_findings, decay_flags = _safe_run(
            "thought_decay", decay_thoughts
        )
        if decay_result:
            findings.append(f"Thought decay: {decay_result['remaining']}/{decay_result['total']} remaining, "
                          f"{decay_result['removed']} removed, "
                          f"{len(decay_result['proposed_for_crystallization'])} proposed for belief crystallization")
            findings.extend(decay_findings)
            flags.extend(decay_flags)
    except Exception as e:
        flags.append(f"thought_decay error: {e}")

    # ── Tier 3: Curiosity Engine ──────────────────────────────────────────────
    findings.append("Starting curiosity engine...")
    try:
        from brain.curiosity_engine import generate_questions_from_gaps, prioritize_questions, attempt_resolution

        # Generate new questions from gaps
        new_questions, gen_findings, gen_flags = _safe_run(
            "curiosity_generate", generate_questions_from_gaps
        )
        if new_questions is not None:
            findings.append(f"Curiosity: {len(new_questions)} new questions generated")
            findings.extend(gen_findings)
            flags.extend(gen_flags)

        # Attempt resolution on top 3 priority questions
        prioritized = prioritize_questions()
        top3 = prioritized[:3]
        resolved_count = 0
        for q in top3:
            res_result, _, _ = _safe_run(f"curiosity_resolve_{q['id'][:8]}", attempt_resolution, q["id"])
            if res_result and res_result.get("status") == "resolved":
                resolved_count += 1
        if top3:
            findings.append(f"Curiosity resolution: attempted {len(top3)} questions, {resolved_count} fully resolved")
    except Exception as e:
        flags.append(f"curiosity_engine error: {e}")

    # ── Tier 3: Epistemic Tension Review ─────────────────────────────────────
    findings.append("Starting epistemic tension review...")
    try:
        from brain.contradiction_crystallization import review_epistemic_tensions
        tension_result, tension_findings, tension_flags = _safe_run(
            "epistemic_tension_review", review_epistemic_tensions
        )
        if tension_result:
            findings.append(f"Epistemic tensions: {tension_result['active_tensions']} active, "
                          f"{len(tension_result['flagged_for_review'])} flagged for review (>30 days, no output)")
            findings.extend(tension_findings)
            flags.extend(tension_flags)
    except Exception as e:
        flags.append(f"epistemic_tension_review error: {e}")

    # Step: Contradiction resolution
    findings.append("Starting contradiction resolution...")
    try:
        from brain.contradiction_resolution import (
            check_for_new_contradictions,
            run_contradiction_resolution
        )

        new_contra, new_findings, new_flags = _safe_run(
            "contradiction_check", check_for_new_contradictions
        )
        if new_contra:
            findings.append(f"New contradictions detected: {len(new_contra)}")
            findings.extend(new_findings)
            flags.extend(new_flags)

        contra_result, contra_findings, contra_flags = _safe_run(
            "contradiction_resolution", run_contradiction_resolution
        )
        if contra_result:
            findings.append(f"Contradiction resolution: {contra_result['processed']} processed, "
                          f"{len(contra_result['resolved'])} resolved, "
                          f"{len(contra_result['held'])} held, "
                          f"{len(contra_result['crystallized'])} crystallized")
            findings.extend(contra_findings)
            flags.extend(contra_flags)

    except ImportError as e:
        findings.append("contradiction_resolution not available yet")
        flags.append(f"contradiction_resolution import error: {e}")

    # Step: Drift detection
    findings.append("Running drift detection...")
    try:
        from brain.continuity_engine import rebuild_self_snapshot
        snapshot_result, snap_findings, snap_flags = _safe_run(
            "drift_detection", rebuild_self_snapshot
        )
        if snapshot_result:
            tension = snapshot_result.get("continuity_tension")
            score = snapshot_result.get("continuity_score")
            findings.append(f"Snapshot v{snapshot_result.get('self_version')}: "
                          f"score={score}, tension={tension}")
            findings.extend(snap_findings)
            flags.extend(snap_flags)
    except Exception as e:
        findings.append("Drift detection error")
        flags.append(f"drift_detection error: {e}")

    # ── Tier 3: Meaning Compression ───────────────────────────────────────────
    findings.append("Starting meaning compression...")
    try:
        compress_result, compress_findings, compress_flags = _safe_run(
            "meaning_compression", compress_meaning
        )
        if compress_result:
            findings.append(f"Meaning compression: {compress_result.get('clusters_found', 0)} clusters, "
                          f"{compress_result.get('symbols_created', 0)} new symbols created")
            findings.extend(compress_findings)
            flags.extend(compress_flags)
    except Exception as e:
        flags.append(f"meaning_compression error: {e}")

    # Write synthesis results
    synthesis_file = SYNTHESIS_DIR / f"synthesis_{datetime.now().strftime('%Y-%m-%d')}.json"
    synthesis_result = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": _now_iso(),
        "findings": findings,
        "flags": flags
    }
    SYNTHESIS_DIR.mkdir(parents=True, exist_ok=True)
    synthesis_file.write_text(json.dumps(synthesis_result, indent=2))

    return {"findings": findings, "flags": flags}


# ── Phase 3: Morning Consolidation ─────────────────────────────────────────

def compress_meaning() -> dict:
    """
    Find memory clusters that have been synthesized 3+ times.
    LLM call: "What single symbol captures this cluster?"
    Write symbol node: content, mass: 0.5, attraction_radius: 0.6,
    activation_threshold: 0.4, source_cluster_ids: [...]
    Symbols stored in knowledge_graph as "symbol_node" type.

    Returns summary dict.
    """
    from pathlib import Path
    from brain.knowledge_graph import get_or_create_node, add_node

    # Find synthesis entries with high overlap (clustered memories)
    synthesis_dir = NOVA_HOME / "overnight" / "synthesis"
    if not synthesis_dir.exists():
        return {"clusters_found": 0, "symbols_created": 0}

    synthesis_files = sorted(synthesis_dir.glob("synthesis_*.json"))[-7:]  # last 7 syntheses
    if len(synthesis_files) < 3:
        return {"clusters_found": 0, "symbols_created": 0}

    # Load all synthesis findings
    all_findings = []
    for sf in synthesis_files:
        try:
            data = json.loads(sf.read_text())
            all_findings.extend(data.get("findings", []))
        except Exception:
            pass

    if len(all_findings) < 10:
        return {"clusters_found": 0, "symbols_created": 0}

    # Simple clustering: find recurring word patterns across findings
    # In full impl: use LLM to identify clusters
    # Here: find recurring bigrams across 3+ syntheses
    from collections import Counter
    bigrams = Counter()
    for finding in all_findings:
        words = finding.lower().split()
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            bigrams[bigram] += 1

    # Find bigrams appearing in 3+ syntheses
    recurring = {bg: count for bg, count in bigrams.items() if count >= 3 and len(bg) > 6}
    if not recurring:
        return {"clusters_found": 0, "symbols_created": 0}

    symbols_created = 0
    for bigram, count in recurring.items():
        # Check if symbol already exists
        existing = get_or_create_node(label=bigram, node_type="symbol_node")
        # Update salience based on recurrence
        from brain.knowledge_graph import update_node_salience
        new_salience = min(0.5 + (count * 0.05), 1.0)
        update_node_salience(existing, new_salience, reason=f"meaning_compression:{count}syntheses")
        symbols_created += 1

    return {
        "clusters_found": len(recurring),
        "symbols_created": symbols_created
    }


def morning_consolidation() -> dict:
    """
    Phase 3: On wake — surface top insights from overnight synthesis.
    Returns morning state for Nova to integrate.
    """
    findings = []
    flags = []

    # Load last synthesis
    synthesis_files = sorted(SYNTHESIS_DIR.glob("synthesis_*.json"))
    if synthesis_files:
        last_synthesis = json.loads(synthesis_files[-1].read_text())
        findings.append(f"Last synthesis: {synthesis_files[-1].name}")
        findings.append(f"Insights: {len(last_synthesis.get('findings', []))}")
    else:
        findings.append("No previous synthesis found")

    # Load last digest
    digest_files = sorted(DIGEST_DIR.glob("digest_*.json"))
    if digest_files:
        last_digest = json.loads(digest_files[-1].read_text())
        findings.append(f"Last digest: {digest_files[-1].name}")
    else:
        findings.append("No previous digest found")

    # Get continuity tension
    try:
        from brain.continuity_engine import get_continuity_tension
        tension = get_continuity_tension()
        findings.append(f"Continuity tension: {tension}")
    except Exception as e:
        flags.append(f"Could not get continuity tension: {e}")

    # Build morning report
    morning_report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "morning_state": "Nova's current state on wake",
        "top_insights": findings[:3],
        "open_questions_status": "check_synthesis",
        "synthesis_available": len(synthesis_files) > 0
    }

    return {"findings": findings, "flags": flags}


# ── Main Entry Point ─────────────────────────────────────────────────────────

def run_full_pipeline():
    """Run the complete overnight pipeline in sequence."""
    results = {}

    print("[overnight_synthesis] Starting full pipeline...")
    print("[overnight_synthesis] Phase 1: Night Digest")
    digest_result = night_digest()
    results["digest"] = digest_result
    print(f"[overnight_synthesis] Digest complete: {digest_result.get('findings', [])[:2]}")

    print("[overnight_synthesis] Phase 2: Overnight Synthesis")
    synth_result = overnight_synthesis()
    results["synthesis"] = synth_result
    print(f"[overnight_synthesis] Synthesis complete: {synth_result.get('findings', [])[:3]}")

    print("[overnight_synthesis] Phase 3: Morning Consolidation")
    morning_result = morning_consolidation()
    results["morning"] = morning_result
    print(f"[overnight_synthesis] Morning complete: {morning_result.get('findings', [])[:2]}")

    print("[overnight_synthesis] Pipeline complete.")
    return results


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "full"

    if phase == "full":
        results = run_full_pipeline()
        print(json.dumps(results, indent=2))
    elif phase == "digest":
        result = night_digest()
        print(json.dumps(result, indent=2))
    elif phase == "synth":
        result = overnight_synthesis()
        print(json.dumps(result, indent=2))
    elif phase == "morning":
        result = morning_consolidation()
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown phase: {phase}")
        print("Usage: overnight_synthesis.py [full|digest|synth|morning]")
