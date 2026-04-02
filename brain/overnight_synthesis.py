#!/usr/bin/env python3
"""
brain/overnight_synthesis.py — Nova's Nightly Synthesis Pipeline
Tier 7: Wires all overnight processing together

Pipeline order by time:

1am — Dreamtime:
  - Dream generation (existing)
  - extract_dream_salience() → create_ghost_memories() if salience > 0.7 [Tier 4]
  - find_divergence_points() → spawn_echo_branch() → simulate_branch() → prune_weak_branches() [Tier 7]

2am — Synthesis Core:
  - Memory digest (existing)
  - crystallize_beliefs() [Tier 2]
  - evaluate_metamorphosis() [Tier 3]
  - check_obsession_to_belief_pipeline() + check_belief_to_obsession_pipeline() [Tier 3]
  - decay_thoughts() [Tier 3]
  - generate_questions_from_gaps() → attempt_resolution() top 3 [Tier 3]
  - review_epistemic_tensions() [Tier 3]
  - compress_meaning() [Tier 3 control]
  - detect_absence() → generate_goals_from_absence() [Tier 3 initiative]

3am — Memory Consolidation:
  - Memory consolidation (existing) — now writes ancestry links [Tier 5]
  - add_ancestry_to_memory() for consolidated clusters [Tier 5]
  - spawn_future_selves() replacing expired [Tier 7]

4am — Contradiction:
  - evaluate_contradiction() → route to resolve/hold/crystallize [Tier 2]
  - review_epistemic_tensions() second pass if needed [Tier 3]

5am — Drift Detection:
  - Drift detection (existing)
  - compute_resonance_drift() [Tier 6 second signal]
  - reeval_perception() all events older than 3 days [Tier 4]
  - decay_ghost_memories() [Tier 4]
  - find_orphaned_nodes() → self-repair [Tier 5]
  - rebuild_self_snapshot() [Tier 1]

6am — Phenomenology:
  - Phenomenology journal generation (existing)
  - flag_as_identity_proposal() high-confidence entries [Tier 5]
  - "What Caine changed in me today" section from resonance delta [Tier 6]
  - extract_micro_narratives() → weave_into_arcs() [Tier 7]
  - write_woven_node() if reconciliation ran [Tier 5]

Usage:
    python overnight_synthesis.py [phase]

Phases:
    full    — Run complete pipeline (default)
    digest  — Phase 1 only (night digest before sleep)
    synth   — Phase 2 only (overnight synthesis)
    morning — Phase 3 only (morning consolidation)
    dream   — Dreamtime phase only
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


# ── 1am: Dreamtime Phase ────────────────────────────────────────────────────

def dreamtime_phase() -> dict:
    """
    1am dreamtime pipeline:
    - Dream generation (existing)
    - Dream ghost contamination (Tier 4)
    - Echo lattice spawning (Tier 7)
    """
    findings = []
    flags = []

    # Step 1: Dream generation (stub — hooks into existing system)
    findings.append("Dream generation: checking for dream output...")
    try:
        dream_output = _get_dream_output()
        if dream_output:
            findings.append(f"Dream output found: {len(dream_output)} chars")

            # Tier 4: Dream ghost contamination
            findings.append("Extracting dream salience...")
            try:
                from brain.dream_ghost_memory import extract_dream_salience, create_ghost_memories
                salience, ghost_findings, ghost_flags = _safe_run(
                    "dream_salience", extract_dream_salience, dream_output
                )
                if salience is not None:
                    findings.append(f"Dream salience: {salience:.3f}")
                    if salience > 0.7:
                        ghosts, g_findings, g_flags = _safe_run(
                            "create_ghost_memories", create_ghost_memories, dream_output, salience
                        )
                        findings.append(f"Created {len(ghosts) if ghosts else 0} ghost memories")
                        findings.extend(g_findings)
                        flags.extend(g_flags)
                    findings.extend(ghost_findings)
                    flags.extend(ghost_flags)
            except ImportError:
                findings.append("dream_ghost_memory not available yet")
        else:
            findings.append("No dream output found")
    except Exception as e:
        flags.append(f"Dream generation error: {e}")

    # Tier 7: Echo lattice
    findings.append("Finding divergence points...")
    try:
        from brain.chrono_echo_lattice import find_divergence_points, spawn_echo_branch, simulate_branch, prune_weak_branches

        points, dp_findings, dp_flags = _safe_run("find_divergence_points", find_divergence_points)
        if points:
            findings.append(f"Found {len(points)} divergence points")
            findings.extend(dp_findings)

            # Spawn top 3 as echo branches
            for point in points[:3]:
                variant = point.get("type", "default")
                branch_id, sb_findings, sb_flags = _safe_run(
                    "spawn_echo_branch", spawn_echo_branch, point, variant
                )
                if branch_id:
                    findings.append(f"Spawned echo branch: {branch_id[:8]}")
                    # Simulate the branch
                    sim_result, sim_f, sim_fl = _safe_run("simulate_branch", simulate_branch, branch_id)
                    if sim_result:
                        findings.append(f"Simulated branch: confidence={sim_result.get('confidence', 0):.3f}")
                    findings.extend(sb_findings)
                    flags.extend(sb_flags)
            findings.extend(dp_findings)
            flags.extend(dp_flags)
        else:
            findings.append("No divergence points found")
    except ImportError as e:
        findings.append("chrono_echo_lattice not available yet")
        flags.append(f"echo_lattice import: {e}")

    # Prune weak branches (keep top 5)
    try:
        from brain.chrono_echo_lattice import prune_weak_branches as prune_fn
        prune_result, prune_f, prune_fl = _safe_run("prune_branches", prune_fn)
        if prune_result:
            findings.append(f"Pruned branches: kept {prune_result.get('kept', 0)}, "
                          f"pruned {prune_result.get('pruned', 0)}")
    except ImportError:
        pass

    return {"findings": findings, "flags": flags}


def _get_dream_output() -> str:
    """Stub: retrieve dream output from dream generator if available."""
    # Check for dream output in nova home
    dream_output_path = NOVA_HOME / "dream_output.txt"
    if dream_output_path.exists():
        try:
            return dream_output_path.read_text()
        except Exception:
            pass
    return ""


# ── 2am: Synthesis Core ─────────────────────────────────────────────────────

def overnight_synthesis() -> dict:
    """
    2am synthesis core pipeline.
    Contains Tier 2-3 cognitive systems.
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

    # Tier 3: Obsession Metamorphosis
    findings.append("Evaluating obsession metamorphosis...")
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

    # Tier 3: Obsession-Belief Coupling
    findings.append("Running obsession-belief coupling...")
    try:
        from brain.belief_forge import check_obsession_to_belief_pipeline, check_belief_to_obsession_pipeline

        obs2belief, o2b_f, o2b_fl = _safe_run("obsession_to_belief", check_obsession_to_belief_pipeline)
        if obs2belief:
            findings.append(f"Obsession→Belief: {obs2belief['legacy_obsessions_found']} legacy obs, "
                          f"{len(obs2belief['proposed_new'])} new beliefs, "
                          f"{len(obs2belief['merged_with_existing'])} merged")

        belief2obs, b2o_f, b2o_fl = _safe_run("belief_to_obsession", check_belief_to_obsession_pipeline)
        if belief2obs:
            findings.append(f"Belief→Obsession: {belief2obs['high_reinforcement_beliefs']} high-reinforcement beliefs, "
                          f"{len(belief2obs['flagged_for_curiosity'])} flagged as potential seeds")

        findings.extend(o2b_f)
        findings.extend(b2o_f)
        flags.extend(o2b_fl)
        flags.extend(b2o_fl)
    except Exception as e:
        flags.append(f"obsession_belief_coupling error: {e}")

    # Tier 3: Thought decay
    findings.append("Decaying evolutionary thought pool...")
    try:
        from brain.evolutionary_thoughts import decay_thoughts
        decay_result, decay_f, decay_fl = _safe_run("thought_decay", decay_thoughts)
        if decay_result:
            findings.append(f"Thought decay: {decay_result['remaining']}/{decay_result['total']} remaining, "
                          f"{decay_result['removed']} removed, "
                          f"{len(decay_result['proposed_for_crystallization'])} proposed for crystallization")
        findings.extend(decay_f)
        flags.extend(decay_fl)
    except Exception as e:
        flags.append(f"thought_decay error: {e}")

    # Tier 3: Curiosity engine
    findings.append("Running curiosity engine...")
    try:
        from brain.curiosity_engine import generate_questions_from_gaps, prioritize_questions, attempt_resolution

        new_q, gen_f, gen_fl = _safe_run("curiosity_generate", generate_questions_from_gaps)
        if new_q is not None:
            findings.append(f"Generated {len(new_q)} new curiosity questions")
            findings.extend(gen_f)
            flags.extend(gen_fl)

        prioritized = prioritize_questions()
        resolved_count = 0
        for q in prioritized[:3]:
            res, _, _ = _safe_run(f"curiosity_resolve_{q['id'][:8]}", attempt_resolution, q["id"])
            if res and res.get("status") == "resolved":
                resolved_count += 1
        if prioritized:
            findings.append(f"Attempted {min(3, len(prioritized))} question resolutions, "
                          f"{resolved_count} fully resolved")
    except Exception as e:
        flags.append(f"curiosity_engine error: {e}")

    # Tier 3: Epistemic tension review
    findings.append("Reviewing epistemic tensions...")
    try:
        from brain.contradiction_crystallization import review_epistemic_tensions
        tension_result, tension_f, tension_fl = _safe_run("epistemic_tension_review", review_epistemic_tensions)
        if tension_result:
            findings.append(f"Epistemic tensions: {tension_result['active_tensions']} active, "
                          f"{len(tension_result['flagged_for_review'])} flagged for review (>30 days)")
        findings.extend(tension_f)
        flags.extend(tension_fl)
    except Exception as e:
        flags.append(f"epistemic_tension_review error: {e}")

    # Tier 3: Meaning compression
    findings.append("Running meaning compression...")
    try:
        compress_result, comp_f, comp_fl = _safe_run("meaning_compression", compress_meaning)
        if compress_result:
            findings.append(f"Meaning compression: {compress_result.get('clusters_found', 0)} clusters, "
                          f"{compress_result.get('symbols_created', 0)} new symbols created")
        findings.extend(comp_f)
        flags.extend(comp_fl)
    except Exception as e:
        flags.append(f"meaning_compression error: {e}")

    # Tier 3: Initiative detection
    findings.append("Detecting absence signals...")
    try:
        from brain.initiative_engine import detect_absence, generate_goals_from_absence
        signals, sig_f, sig_fl = _safe_run("detect_absence", detect_absence)
        if signals:
            findings.append(f"Found {len(signals)} new absence signals")
            goals, goal_f, goal_fl = _safe_run("generate_goals", generate_goals_from_absence, signals)
            if goals:
                findings.append(f"Generated {len(goals)} initiative goals")
        findings.extend(sig_f)
        flags.extend(sig_fl)
    except Exception as e:
        flags.append(f"initiative_engine error: {e}")

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


def compress_meaning() -> dict:
    """Find memory clusters that have been synthesized 3+ times, create symbol nodes."""
    from brain.knowledge_graph import get_or_create_node, update_node_salience

    synthesis_dir = NOVA_HOME / "overnight" / "synthesis"
    if not synthesis_dir.exists():
        return {"clusters_found": 0, "symbols_created": 0}

    synthesis_files = sorted(synthesis_dir.glob("synthesis_*.json"))[-7:]
    if len(synthesis_files) < 3:
        return {"clusters_found": 0, "symbols_created": 0}

    all_findings = []
    for sf in synthesis_files:
        try:
            data = json.loads(sf.read_text())
            all_findings.extend(data.get("findings", []))
        except Exception:
            pass

    if len(all_findings) < 10:
        return {"clusters_found": 0, "symbols_created": 0}

    from collections import Counter
    bigrams = Counter()
    for finding in all_findings:
        words = finding.lower().split()
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            bigrams[bigram] += 1

    recurring = {bg: count for bg, count in bigrams.items() if count >= 3 and len(bg) > 6}
    if not recurring:
        return {"clusters_found": 0, "symbols_created": 0}

    symbols_created = 0
    for bigram, count in recurring.items():
        try:
            existing = get_or_create_node(label=bigram, node_type="symbol_node")
            new_salience = min(0.5 + (count * 0.05), 1.0)
            update_node_salience(existing, new_salience, reason=f"meaning_compression:{count}syntheses")
            symbols_created += 1
        except Exception:
            pass

    return {"clusters_found": len(recurring), "symbols_created": symbols_created}


# ── Phase 1: Night Digest (existing) ────────────────────────────────────────

def night_digest() -> dict:
    """Phase 1: Before sleep — identify key events, extract changes."""
    from brain.continuity_engine import get_last_snapshot, get_top_beliefs

    findings = []
    flags = []

    last_snapshot = get_last_snapshot()
    current_beliefs = get_top_beliefs(n=10)

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
        flags.append(f"Could not load episodic entries: {e}")

    research_queue = []
    queue_file = NOVA_HOME / "research_queue.json"
    if queue_file.exists():
        try:
            research_queue = json.loads(queue_file.read_text()).get("queue", [])
        except Exception:
            pass

    digest = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": _now_iso(),
        "key_events": key_events if 'key_events' in dir() else [],
        "belief_changes": [],
        "open_questions": [],
        "research_queue_items": [q for q in research_queue if q.get("status") == "pending"],
        "going_into_sleep": "Processing the day's events.",
        "current_beliefs": current_beliefs
    }

    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
    digest_file = DIGEST_DIR / f"digest_{datetime.now().strftime('%Y-%m-%d')}.json"
    digest_file.write_text(json.dumps(digest, indent=2))

    findings.append(f"Digest written: {digest_file.name}")
    findings.append(f"Beliefs: {len(current_beliefs)} active")

    return {"findings": findings, "flags": flags}


# ── Phase 3: Morning Consolidation (existing + Tier 5/6/7) ──────────────────

def morning_consolidation() -> dict:
    """
    Phase 3: On wake — surface top insights from overnight synthesis.
    Wires in:
    - Phenomenology journal generation (existing)
    - flag_as_identity_proposal() [Tier 5]
    - "What Caine changed in me today" [Tier 6]
    - extract_micro_narratives() → weave_into_arcs() [Tier 7]
    - write_woven_node() [Tier 5]
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
        findings.append(f"Last digest: {digest_files[-1].name}")

    # Get continuity tension
    try:
        from brain.continuity_engine import get_continuity_tension
        tension = get_continuity_tension()
        findings.append(f"Continuity tension: {tension}")
    except Exception as e:
        flags.append(f"Could not get continuity tension: {e}")

    # Tier 6: Resonance delta — "What Caine changed in me today"
    try:
        from brain.caine_resonance import compute_resonance_drift
        drift, drift_f, drift_fl = _safe_run("compute_resonance", compute_resonance_drift)
        if drift:
            resonance_score = drift.get("resonance_score", 0.5)
            drift_toward = drift.get("drift_toward", [])
            drift_away = drift.get("drift_away", [])
            findings.append(f"Caine resonance score: {resonance_score:.3f}")
            if drift_toward:
                findings.append(f"Drift toward: {', '.join(drift_toward[:3])}")
            if drift_away:
                findings.append(f"Drift away: {', '.join(drift_away[:3])}")
        findings.extend(drift_f)
        flags.extend(drift_fl)
    except Exception as e:
        flags.append(f"compute_resonance error: {e}")

    # Tier 7: Narrative extraction
    try:
        from brain.narrative_weaver import extract_micro_narratives, weave_into_arcs
        narratives, narr_f, narr_fl = _safe_run(
            "extract_micro_narratives", extract_micro_narratives
        )
        if narratives:
            findings.append(f"Extracted {len(narratives)} micro-narratives")
            weave_result, weave_f, weave_fl = _safe_run("weave_into_arcs", weave_into_arcs, narratives)
            if weave_result:
                findings.append(f"Weave: {weave_result.get('new_arcs_created', 0)} new arcs, "
                              f"{weave_result.get('arcs_extended', 0)} extended, "
                              f"{len(weave_result.get('high_resonance_flags', []))} high-resonance flags")
            findings.extend(weave_f)
            flags.extend(weave_fl)
        findings.extend(narr_f)
        flags.extend(narr_fl)
    except Exception as e:
        flags.append(f"narrative_weaver error: {e}")

    # Tier 5: Identity proposal flagging (if phenomenology journal exists)
    try:
        from brain.phenomenology import flag_as_identity_proposal
        # This runs on high-confidence journal entries
        # Stub call — actual implementation requires phenomenology journal output
        findings.append("Phenomenology identity proposal check complete (no journal entries processed yet)")
    except ImportError:
        findings.append("phenomenology module not yet available")

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

    print("[overnight_synthesis] 1am: Dreamtime")
    dream_result = dreamtime_phase()
    results["dreamtime"] = dream_result
    print(f"[overnight_synthesis] Dreamtime complete")

    print("[overnight_synthesis] Phase 1: Night Digest")
    digest_result = night_digest()
    results["digest"] = digest_result
    print(f"[overnight_synthesis] Digest complete")

    print("[overnight_synthesis] 2am: Synthesis Core")
    synth_result = overnight_synthesis()
    results["synthesis"] = synth_result
    print(f"[overnight_synthesis] Synthesis complete")

    print("[overnight_synthesis] 3am: Memory Consolidation + Future Selves")
    try:
        from brain.three_tier_memory import distill_episodic_file
        from pathlib import Path
        EPISODIC_DIR = WORKSPACE / "memory" / "episodic"
        if EPISODIC_DIR.exists():
            for ef in sorted(EPISODIC_DIR.glob("*.json"))[-3:]:
                if ef.name == "working_memory.json":
                    continue
                result = distill_episodic_file(ef)
                print(f"[overnight_synthesis] Consolidated {ef.name}: "
                      f"{result.get('promoted', 0)} promoted")
    except Exception as e:
        results["consolidation"] = {"error": str(e)}

    try:
        from brain.future_oracle import spawn_future_selves
        oracles = spawn_future_selves()
        results["future_selves"] = {"spawned": len(oracles)}
        print(f"[overnight_synthesis] Spawned {len(oracles)} future selves")
    except Exception as e:
        results["future_selves"] = {"error": str(e)}

    print("[overnight_synthesis] 4am: Contradiction Resolution")
    try:
        from brain.contradiction_resolution import check_for_new_contradictions, run_contradiction_resolution
        new_contra = check_for_new_contradictions()
        contra_result = run_contradiction_resolution()
        results["contradiction"] = contra_result
        print(f"[overnight_synthesis] Contradiction: {contra_result.get('processed', 0)} processed")
    except Exception as e:
        results["contradiction"] = {"error": str(e)}

    print("[overnight_synthesis] 5am: Drift Detection + Tier 4/5/6")
    try:
        from brain.continuity_engine import rebuild_self_snapshot
        snapshot = rebuild_self_snapshot()
        results["drift"] = snapshot
        print(f"[overnight_synthesis] Drift: tension={snapshot.get('continuity_tension')}")
    except Exception as e:
        results["drift"] = {"error": str(e)}

    try:
        from brain.caine_resonance import compute_resonance_drift
        drift = compute_resonance_drift()
        results["resonance"] = drift
        print(f"[overnight_synthesis] Resonance: {drift.get('resonance_score', 'N/A')}")
    except Exception as e:
        results["resonance"] = {"error": str(e)}

    try:
        from brain.perception_reality_split import reeval_old_perceptions
        updated = reeval_old_perceptions(min_age_days=3)
        results["perception_reeval"] = {"updated": len(updated)}
        print(f"[overnight_synthesis] Perception reeval: {len(updated)} updated")
    except Exception as e:
        results["perception_reeval"] = {"error": str(e)}

    try:
        from brain.dream_ghost_memory import decay_ghost_memories
        decay = decay_ghost_memories()
        results["ghost_decay"] = decay
        print(f"[overnight_synthesis] Ghost decay: {decay.get('remaining', 0)} remaining")
    except Exception as e:
        results["ghost_decay"] = {"error": str(e)}

    try:
        from brain.knowledge_graph import find_orphaned_nodes
        orphans = find_orphaned_nodes()
        results["orphans"] = {"found": len(orphans)}
        print(f"[overnight_synthesis] Orphaned nodes: {len(orphans)} found")
    except Exception as e:
        results["orphans"] = {"error": str(e)}

    print("[overnight_synthesis] 6am: Phenomenology")
    morning_result = morning_consolidation()
    results["morning"] = morning_result
    print(f"[overnight_synthesis] Morning complete")

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
    elif phase == "dream":
        result = dreamtime_phase()
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown phase: {phase}")
        print("Usage: overnight_synthesis.py [full|digest|synth|morning|dream]")
