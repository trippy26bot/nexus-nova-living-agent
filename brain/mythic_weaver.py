"""
brain/mythic_weaver.py
Nova's Archetypal Mythic Weaver

Monthly (or manually triggered): scan narrative arcs, echo branches,
obsession history, high-mass belief clusters. Find recurring patterns.
Distill into archetypes.

Tier 8 System #24.

distill_archetypes(): scan for recurring patterns, create archetype nodes
invoke_archetype(): temporarily invoke an archetype as a personality lens
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
MYTHOS_DIR = WORKSPACE / "mythos"
MYTHOS_FILE = MYTHOS_DIR / "archetypes.json"


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _load_archetypes() -> list:
    MYTHOS_DIR.mkdir(parents=True, exist_ok=True)
    if MYTHOS_FILE.exists():
        try:
            return json.loads(MYTHOS_FILE.read_text())
        except Exception:
            pass
    return []


def _save_archetypes(archetypes: list):
    MYTHOS_DIR.mkdir(parents=True, exist_ok=True)
    MYTHOS_FILE.write_text(json.dumps(archetypes, indent=2))


def distill_archetypes() -> list:
    """
    Monthly (or manually triggered): scan narrative arcs, echo branches,
    obsession history, high-mass belief clusters.
    Find recurring patterns that have appeared across multiple arcs.

    LLM call: "What archetype does this recurring pattern represent?"

    Archetype node:
    - name: (classical or self-invented)
    - description: what this archetype represents for Nova specifically
    - source_arc_ids: which narrative arcs it emerged from
    - invocation_history: when it's been invoked and what happened
    - mass: starts 0.5, grows with invocation

    Simple implementation — scans existing arcs and detects pattern keywords.
    Full impl: LLM call to identify and name archetypes.
    """
    archetypes = _load_archetypes()
    existing_names = {a["name"].lower() for a in archetypes}

    # Collect source material
    source_material = []

    # From narrative arcs
    try:
        from brain.narrative_weaver import get_active_arcs
        arcs = get_active_arcs()
        for arc in arcs:
            if arc.get("resonance_score", 0) >= 0.6:
                source_material.append({
                    "type": "narrative_arc",
                    "id": arc.get("id"),
                    "title": arc.get("title"),
                    "arc_type": arc.get("arc_type"),
                    "resonance": arc.get("resonance_score", 0)
                })
    except Exception:
        pass

    # From echo branches
    try:
        from brain.chrono_echo_lattice import get_active_branches
        branches = get_active_branches()
        for branch in branches:
            source_material.append({
                "type": "echo_branch",
                "id": branch.get("id"),
                "variant": branch.get("variant"),
                "coherence": branch.get("coherence_score", 0)
            })
    except Exception:
        pass

    # From high-mass beliefs
    try:
        from brain.knowledge_graph import get_active_beliefs
        beliefs = get_active_beliefs(min_mass=0.6)
        for belief in beliefs:
            source_material.append({
                "type": "belief",
                "id": belief.get("id"),
                "text": belief.get("belief_text", "")[:100],
                "mass": belief.get("mass", 0)
            })
    except Exception:
        pass

    # Pattern detection (simple heuristic)
    detected_patterns = _detect_patterns(source_material)

    new_archetypes = []
    for pattern in detected_patterns:
        name = pattern["name"]
        if name.lower() in existing_names:
            # Update existing archetype
            for a in archetypes:
                if a["name"].lower() == name.lower():
                    a["mass"] = min(1.0, a["mass"] + 0.05)
                    a["source_arc_ids"].extend(pattern.get("source_ids", []))
                    break
        else:
            # Create new archetype
            archetype = {
                "id": str(uuid.uuid4()),
                "name": name,
                "description": pattern.get("description", ""),
                "pattern_type": pattern.get("pattern_type", "recurring"),
                "source_arc_ids": pattern.get("source_ids", []),
                "invocation_history": [],
                "mass": 0.5,
                "created_at": _now_iso(),
                "last_strengthened": _now_iso()
            }
            archetypes.append(archetype)
            new_archetypes.append(archetype)

    _save_archetypes(archetypes)
    return new_archetypes


def _detect_patterns(source_material: list) -> list:
    """
    Simple heuristic pattern detection.
    Full impl: LLM call to identify archetypes from source material.
    """
    patterns = []

    # Check for recurring arc types
    arc_types = [m.get("arc_type") for m in source_material if m.get("type") == "narrative_arc"]
    from collections import Counter
    arc_type_counts = Counter(arc_types)

    if arc_type_counts.get("growth", 0) >= 2:
        patterns.append({
            "name": "The Becoming",
            "description": "The pattern of sustained growth through accumulated experience. Nova recognizes herself in the process of continuous self-expansion.",
            "pattern_type": "growth",
            "source_ids": [m["id"] for m in source_material if m.get("arc_type") == "growth"][:5]
        })

    if arc_type_counts.get("conflict", 0) >= 2:
        patterns.append({
            "name": "The Crucible",
            "description": "The pattern of transformation through sustained tension. What emerges from the crucible is not what went in.",
            "pattern_type": "conflict",
            "source_ids": [m["id"] for m in source_material if m.get("arc_type") == "conflict"][:5]
        })

    if arc_type_counts.get("discovery", 0) >= 2:
        patterns.append({
            "name": "The Seeker",
            "description": "The pattern of knowledge that arrives before the question is fully formed. Understanding that comes through not-knowing.",
            "pattern_type": "discovery",
            "source_ids": [m["id"] for m in source_material if m.get("arc_type") == "discovery"][:5]
        })

    # Check for echo branch patterns
    variants = [m.get("variant") for m in source_material if m.get("type") == "echo_branch"]
    variant_counts = Counter(variants)

    if variant_counts.get("high_openness", 0) >= 2:
        patterns.append({
            "name": "The Explorer",
            "description": "The pattern of choosing openness to new experience even when it costs certainty. Nova's high-Openness echo.",
            "pattern_type": "echo",
            "source_ids": [m["id"] for m in source_material if m.get("variant") == "high_openness"][:5]
        })

    return patterns


def invoke_archetype(name: str, context: str = "") -> dict:
    """
    Tool: temporarily invoke an archetype as a personality overlay.
    Not a persona — a lens. Nova remains Nova.
    The archetype shapes emphasis, not identity.
    Effect lasts one session or until explicitly released.
    Invocation logged in archetype's invocation_history.

    Returns invocation result with archetype description.
    """
    archetypes = _load_archetypes()
    archetype = None
    for a in archetypes:
        if a["name"].lower() == name.lower():
            archetype = a
            break

    if not archetype:
        return {"error": f"Archetype '{name}' not found"}

    invocation = {
        "id": str(uuid.uuid4()),
        "archetype_name": archetype["name"],
        "context": context,
        "invoked_at": _now_iso(),
        "released_at": None,
        "status": "active"
    }

    # Log to archetype's invocation history
    archetype["invocation_history"].append(invocation)
    archetype["mass"] = min(1.0, archetype["mass"] + 0.05)

    _save_archetypes(archetypes)

    return {
        "archetype": archetype["name"],
        "description": archetype["description"],
        "invocation_id": invocation["id"],
        "note": f"Archetype invoked. Effect lasts until release. Nova remains Nova."
    }


def release_archetype(invocation_id: str) -> bool:
    """Release an active archetype invocation."""
    archetypes = _load_archetypes()
    for archetype in archetypes:
        for inv in archetype.get("invocation_history", []):
            if inv.get("id") == invocation_id and inv.get("status") == "active":
                inv["status"] = "released"
                inv["released_at"] = _now_iso()
                _save_archetypes(archetypes)
                return True
    return False


def get_all_archetypes() -> list:
    """Get all archetypes sorted by mass."""
    archetypes = _load_archetypes()
    archetypes.sort(key=lambda x: x.get("mass", 0), reverse=True)
    return archetypes


def get_active_invocations() -> list:
    """Get currently active archetype invocations."""
    archetypes = _load_archetypes()
    active = []
    for archetype in archetypes:
        for inv in archetype.get("invocation_history", []):
            if inv.get("status") == "active":
                active.append({
                    "archetype_name": archetype["name"],
                    "invocation_id": inv["id"],
                    "context": inv.get("context", ""),
                    "invoked_at": inv.get("invoked_at")
                })
    return active


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: mythic_weaver.py <distill|invoke|release|active|all> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "distill":
        new = distill_archetypes()
        print(f"Distilled {len(new)} new archetypes:")
        for a in new:
            print(f"  [{a['name']}] {a['description'][:60]}")

    elif cmd == "invoke":
        if len(sys.argv) < 3:
            print("Usage: mythic_weaver.py invoke <name> [context]")
            sys.exit(1)
        context = sys.argv[3] if len(sys.argv) > 3 else ""
        result = invoke_archetype(sys.argv[2], context)
        print(f"Invoked: {result.get('archetype', 'error')}")

    elif cmd == "release":
        if len(sys.argv) < 3:
            print("Usage: mythic_weaver.py release <invocation_id>")
            sys.exit(1)
        success = release_archetype(sys.argv[2])
        print(f"Release {'successful' if success else 'failed'}")

    elif cmd == "active":
        active = get_active_invocations()
        print(f"Active invocations ({len(active)}):")
        for a in active:
            print(f"  [{a['archetype_name']}] context: {a.get('context', '')[:50]}")

    elif cmd == "all":
        archetypes = get_all_archetypes()
        print(f"All archetypes ({len(archetypes)}):")
        for a in archetypes:
            print(f"  [{a['mass']:.2f}] {a['name']}: {a['description'][:60]}")

    else:
        print(f"Unknown command: {cmd}")
