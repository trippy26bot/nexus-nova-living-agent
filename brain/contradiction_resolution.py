#!/usr/bin/env python3
"""
brain/contradiction_resolution.py — Nova's Contradiction Resolution Pipeline
Tier 2: Evaluates contradictions and decides disposition

Modular design:
- evaluate_contradiction() returns disposition: resolve | hold | crystallize
- resolve() handles low-tension automatic resolution
- hold() documents tension and monitors
- crystallize_contradiction() upgrades to tension_node (from contradiction_crystallization.py)

The contradiction_crystallization module (Tier 2) handles tension_node creation
and dream_generator integration.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
NOVA_HOME = WORKSPACE / ".nova"
CONTRADICTIONS_FILE = NOVA_HOME / "contradictions_detected.json"


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def load_contradictions() -> list:
    """Load contradictions from the detected contradictions file."""
    if not CONTRADICTIONS_FILE.exists():
        return []
    try:
        data = json.loads(CONTRADICTIONS_FILE.read_text())
        return data.get("contradictions", [])
    except Exception:
        return []


def save_contradictions(contradictions: list):
    """Save contradictions to the detected file."""
    CONTRADICTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONTRADICTIONS_FILE.write_text(json.dumps({"contradictions": contradictions}, indent=2))


def get_unresolved_contradictions() -> list:
    """Get all contradictions with status 'pending'."""
    all_contradictions = load_contradictions()
    return [c for c in all_contradictions if c.get("resolution_status") == "pending"]


def evaluate_contradiction(belief_a_id: str, belief_b_id: str) -> str:
    """
    Evaluate a contradiction between two beliefs and return disposition.

    Delegates to contradiction_crystallization.py for tension computation.
    Returns:
    - "resolve": tension < 0.4 — resolve automatically
    - "hold": tension 0.4–0.7 — keep both, document tension
    - "crystallize": tension >= 0.7 — write tension node, flag for dreams
    """
    try:
        from brain.contradiction_crystallization import evaluate_contradiction as cc_eval
        return cc_eval(belief_a_id, belief_b_id)
    except ImportError:
        # Fallback if contradiction_crystallization not available
        return "hold"


def resolve_contradiction(contradiction_id: str):
    """
    Low-tension resolution: one belief absorbs the other or both soften.
    Updates contradiction status to 'resolved'.
    """
    contradictions = load_contradictions()
    for c in contradictions:
        if c.get("id") == contradiction_id:
            c["resolution_status"] = "resolved"
            c["resolved_at"] = _now_iso()
            break
    save_contradictions(contradictions)


def hold_contradiction(contradiction_id: str):
    """
    Moderate tension: document both positions, keep tension active.
    Updates status to 'acknowledged' (known tension, living with it).
    """
    contradictions = load_contradictions()
    for c in contradictions:
        if c.get("id") == contradiction_id:
            c["resolution_status"] = "acknowledged"
            c["acknowledged_at"] = _now_iso()
            break
    save_contradictions(contradictions)


def crystallize_contradiction(belief_a_id: str, belief_b_id: str, contradiction_id: str = None) -> Optional[str]:
    """
    High-tension crystallization: write tension_node to knowledge graph.
    Delegates to contradiction_crystallization.py.

    Returns tension_id or None.
    """
    try:
        from brain.contradiction_crystallization import crystallize_contradiction as cc_crystallize
        tension_id = cc_crystallize(belief_a_id, belief_b_id)

        # Update contradiction status
        if contradiction_id:
            contradictions = load_contradictions()
            for c in contradictions:
                if c.get("id") == contradiction_id:
                    c["resolution_status"] = "crystallized"
                    c["crystallized_at"] = _now_iso()
                    c["tension_node_id"] = tension_id
                    break
            save_contradictions(contradictions)

        return tension_id
    except ImportError:
        return None


def run_contradiction_resolution() -> dict:
    """
    Main entry point for overnight contradiction resolution.

    For each pending contradiction:
    1. Evaluate tension strength
    2. Apply disposition: resolve | hold | crystallize
    3. Execute the appropriate handler

    Returns summary dict.
    """
    summary = {
        "processed": 0,
        "resolved": [],
        "held": [],
        "crystallized": [],
        "errors": []
    }

    pending = get_unresolved_contradictions()

    for contradiction in pending:
        summary["processed"] += 1
        cid = contradiction.get("id")
        belief_a = contradiction.get("entity_a")
        belief_b = contradiction.get("entity_b")

        if not belief_a or not belief_b:
            summary["errors"].append({"id": cid, "reason": "missing belief ids"})
            continue

        try:
            disposition = evaluate_contradiction(belief_a, belief_b)

            if disposition == "resolve":
                resolve_contradiction(cid)
                summary["resolved"].append(cid)
            elif disposition == "hold":
                hold_contradiction(cid)
                summary["held"].append(cid)
            elif disposition == "crystallize":
                tension_id = crystallize_contradiction(belief_a, belief_b, cid)
                summary["crystallized"].append({"contradiction_id": cid, "tension_id": tension_id})

        except Exception as e:
            summary["errors"].append({"id": cid, "reason": str(e)})

    return summary


def check_for_new_contradictions() -> list:
    """
    Check knowledge graph for new contradictions between beliefs.
    This runs during overnight synthesis to detect new conflicts.

    Returns list of new contradictions found.
    """
    try:
        from brain.knowledge_graph import get_active_beliefs
        beliefs = get_active_beliefs(min_mass=0.3)

        new_contradictions = []
        existing = load_contradictions()

        # Simple contradiction detection: beliefs with opposing semantic signals
        negation_words = {"not", "never", "no", "don't", "doesn't", "won't", "shouldn't", "can't", "cannot"}

        for i, belief_a in enumerate(beliefs):
            for belief_b in beliefs[i+1:]:
                # Skip same beliefs
                if belief_a["id"] == belief_b["id"]:
                    continue

                # Check if already exists
                existing_ids = {(c.get("entity_a"), c.get("entity_b")) for c in existing}
                pair = (belief_a["id"], belief_b["id"])
                reverse_pair = (belief_b["id"], belief_a["id"])

                if pair in existing_ids or reverse_pair in existing_ids:
                    continue

                # Semantic opposition check
                words_a = set(belief_a["belief_text"].lower().split())
                words_b = set(belief_b["belief_text"].lower().split())

                # If they share content but one has negation words, potential contradiction
                overlap = len(words_a & words_b)
                if overlap > 2:  # Some shared content
                    has_negation_a = bool(words_a & negation_words)
                    has_negation_b = bool(words_b & negation_words)

                    if has_negation_a != has_negation_b:
                        # One affirms, one negates — potential contradiction
                        contradiction = {
                            "id": f"contradiction_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                            "timestamp": _now_iso(),
                            "entity_a": belief_a["id"],
                            "entity_b": belief_b["id"],
                            "conflict": f"Potential opposition: '{belief_a['belief_text']}' vs '{belief_b['belief_text']}'",
                            "severity": "medium",
                            "resolution_status": "pending",
                            "detected_by": "automated_check"
                        }
                        new_contradictions.append(contradiction)

        if new_contradictions:
            all_contradictions = load_contradictions() + new_contradictions
            save_contradictions(all_contradictions)

        return new_contradictions

    except ImportError:
        return []


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: contradiction_resolution.py <check|run|status>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "check":
        new = check_for_new_contradictions()
        print(f"New contradictions detected: {len(new)}")
        for c in new:
            print(f"  [{c['id']}] {c['conflict'][:80]}")

    elif cmd == "run":
        result = run_contradiction_resolution()
        print("Contradiction resolution complete:")
        print(f"  Processed: {result['processed']}")
        print(f"  Resolved: {len(result['resolved'])}")
        print(f"  Held: {len(result['held'])}")
        print(f"  Crystallized: {len(result['crystallized'])}")
        if result['errors']:
            print(f"  Errors: {result['errors']}")

    elif cmd == "status":
        pending = get_unresolved_contradictions()
        print(f"Unresolved contradictions: {len(pending)}")
        for c in pending:
            print(f"  [{c['id']}] {c.get('severity','?')} — {c.get('conflict','')[:60]}")

    else:
        print(f"Unknown command: {cmd}")
