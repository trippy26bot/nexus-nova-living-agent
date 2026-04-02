#!/usr/bin/env python3
"""
brain/overnight_synthesis.py — Nova's Nightly Synthesis Pipeline
Tier 2: Wires all overnight processing together

Pipeline order:
1. Self-snapshot (continuity_engine) — who am I right now
2. Memory consolidation (three_tier_memory) — move episodes toward semantic
3. Belief crystallization (belief_forge) — form raw beliefs into convictions
4. Contradiction resolution — detect, evaluate, crystallize or resolve
5. Drift detection — check if identity is stable

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
    Wires in:
    - crystallize_beliefs() from belief_forge
    - evaluate_contradiction() for flagged contradictions
    - check_for_new_contradictions()
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

    # Step 2: Contradiction resolution
    findings.append("Starting contradiction resolution...")
    try:
        from brain.contradiction_resolution import (
            check_for_new_contradictions,
            run_contradiction_resolution
        )

        # Check for new contradictions first
        new_contra, new_findings, new_flags = _safe_run(
            "contradiction_check", check_for_new_contradictions
        )
        if new_contra:
            findings.append(f"New contradictions detected: {len(new_contra)}")
            findings.extend(new_findings)
            flags.extend(new_flags)

        # Run resolution on pending contradictions
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

    # Step 3: Drift detection
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
