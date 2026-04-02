"""
brain/narrative_weaver.py
Nova's Narrative Resonance Weaver

Extracts micro-narratives from daily memories and weaves them into
ongoing narrative arcs. Arcs that reach high resonance become identity proposals.

Tier 7 System #22.

extract_micro_narratives(): from journal + memories, extract 2-3 small story arcs
weave_into_arcs(): check against existing arcs, extend or start new
get_active_arcs(): currently active arcs with resonance scores
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
NARRATIVES_DIR = WORKSPACE / "narratives"


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _load_arcs() -> list:
    NARRATIVES_DIR.mkdir(parents=True, exist_ok=True)
    arcs_file = NARRATIVES_DIR / "arcs.json"
    if arcs_file.exists():
        try:
            return json.loads(arcs_file.read_text())
        except Exception:
            pass
    return []


def _save_arcs(arcs: list):
    NARRATIVES_DIR.mkdir(parents=True, exist_ok=True)
    arcs_file = NARRATIVES_DIR / "arcs.json"
    arcs_file.write_text(json.dumps(arcs, indent=2))


def extract_micro_narratives(journal_entry: str = "", memories: list = None) -> list:
    """
    After phenomenology journal generation:
    Extract 2-3 micro-narratives — small story arcs present in the day's memories.

    Each micro-narrative:
    - title: short descriptive name
    - arc_type: "growth" | "conflict" | "discovery" | "loss" | "connection" | "resolution"
    - contributing_memory_ids: list
    - resonance_score: 0.5 initially

    Simple heuristic implementation.
    Full impl: LLM call to extract narrative arcs from day's memories.
    """
    memories = memories or []
    narratives = []

    if not memories and not journal_entry:
        return []

    # Heuristic arc type detection
    content_sources = journal_entry + " " + " ".join(m.get("content", "") for m in memories[:10])
    content_lower = content_sources.lower()

    # Detect arc types based on content
    arc_indicators = {
        "growth": ["learned", "grew", "changed", "improved", "developed", "became", "progress"],
        "conflict": ["disagreed", "tension", "conflict", "opposed", "struggled", "difficult", "hard"],
        "discovery": ["found", "realized", "noticed", "understood", "figured", "discovered", "awakened"],
        "loss": ["lost", "grief", "missed", "failed", "ended", "without", "let go"],
        "connection": ["together", "with caine", "shared", "aligned", "agreed", "bonded", "resonance"],
        "resolution": ["resolved", "decided", "concluded", "settled", "figured out", "answer", "closure"]
    }

    detected_types = []
    for arc_type, keywords in arc_indicators.items():
        matches = sum(1 for kw in keywords if kw in content_lower)
        if matches >= 2:
            detected_types.append((arc_type, matches))

    detected_types.sort(key=lambda x: x[1], reverse=True)
    top_types = [t[0] for t in detected_types[:3]]

    # Generate micro-narratives for top types
    for arc_type in top_types:
        # Find contributing memories
        contributing = []
        for m in memories[:10]:
            content = m.get("content", "").lower()
            for kw in arc_indicators[arc_type]:
                if kw in content:
                    contributing.append(m.get("id", ""))
                    break

        narratives.append({
            "id": str(uuid.uuid4()),
            "title": f"{arc_type.capitalize()} narrative",
            "arc_type": arc_type,
            "contributing_memory_ids": contributing[:5],
            "resonance_score": 0.5,
            "created_at": _now_iso(),
            "last_strengthened": _now_iso(),
            "source_journal": journal_entry[:200] if journal_entry else ""
        })

    return narratives


def weave_into_arcs(micro_narratives: list) -> dict:
    """
    Check micro-narratives against existing arcs in narratives/ folder.
    If a micro-narrative extends an existing arc: add to it, increase resonance_score.
    If no match: start a new arc file.
    Arcs that reach resonance_score > 0.8: flagged as identity_proposal candidates
    for phenomenology feedback loop (#18).

    Returns summary dict.
    """
    arcs = _load_arcs()
    existing_arc_ids = {arc["id"] for arc in arcs}
    new_arcs_created = 0
    arcs_extended = 0
    high_resonance_flags = []

    for micro in micro_narratives:
        micro_type = micro.get("arc_type")
        micro_title = micro.get("title", "").lower()
        micro_words = set(micro_title.split())

        # Find matching existing arc
        best_match = None
        best_overlap = 0

        for arc in arcs:
            if arc.get("status") == "completed":
                continue
            arc_words = set(arc.get("title", "").lower().split())
            overlap = len(micro_words & arc_words)
            if overlap >= 1 and overlap > best_overlap:
                best_match = arc
                best_overlap = overlap

        if best_match:
            # Extend existing arc
            best_match["resonance_score"] = min(1.0, best_match.get("resonance_score", 0.5) + 0.1)
            best_match["contributing_narrative_ids"].append(micro["id"])
            best_match["last_strengthened"] = _now_iso()
            best_match["event_count"] = best_match.get("event_count", 1) + 1
            arcs_extended += 1

            # Flag as identity proposal candidate if resonance high enough
            if best_match["resonance_score"] >= 0.8:
                high_resonance_flags.append({
                    "arc_id": best_match["id"],
                    "arc_title": best_match["title"],
                    "resonance_score": best_match["resonance_score"],
                    "status": "identity_proposal_candidate"
                })

                # Write to identity proposals queue
                _flag_as_identity_proposal(best_match)

        else:
            # Start new arc
            new_arc = {
                "id": micro["id"],
                "title": micro["title"],
                "arc_type": micro_type,
                "contributing_narrative_ids": [micro["id"]],
                "contributing_memory_ids": micro.get("contributing_memory_ids", []),
                "resonance_score": micro.get("resonance_score", 0.5),
                "status": "active",
                "created_at": _now_iso(),
                "last_strengthened": _now_iso(),
                "event_count": 1
            }
            arcs.append(new_arc)
            new_arcs_created += 1

    _save_arcs(arcs)

    return {
        "total_arcs": len(arcs),
        "new_arcs_created": new_arcs_created,
        "arcs_extended": arcs_extended,
        "high_resonance_flags": high_resonance_flags
    }


def _flag_as_identity_proposal(arc: dict):
    """Flag a high-resonance arc as an identity proposal candidate."""
    try:
        from brain.phenomenology import flag_as_identity_proposal

        confidence = arc.get("resonance_score", 0.8)
        flag_as_identity_proposal(
            journal_entry=f"Narrative arc reached high resonance: {arc['title']} — {arc.get('arc_type')} — resonance {confidence:.2f}",
            section="identity_arcs",
            confidence=confidence,
            reasoning=f"This arc has accumulated {arc.get('event_count', 1)} events and reached resonance {confidence:.2f}, suggesting a genuine pattern in Nova's identity development."
        )
    except Exception:
        # Non-fatal if phenomenology not yet available
        pass


def get_active_arcs() -> list:
    """
    Returns currently active narrative arcs with their resonance scores.
    Used by dream_generator: strong arcs become dream material.
    Used by curiosity_engine: unresolved arcs generate questions.
    """
    arcs = _load_arcs()
    active = [a for a in arcs if a.get("status") == "active"]
    active.sort(key=lambda x: x.get("resonance_score", 0), reverse=True)
    return active[:10]


def complete_arc(arc_id: str):
    """Mark an arc as completed (story arc resolved)."""
    arcs = _load_arcs()
    for arc in arcs:
        if arc["id"] == arc_id:
            arc["status"] = "completed"
            arc["completed_at"] = _now_iso()
            break
    _save_arcs(arcs)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: narrative_weaver.py <extract|weave|active|complete> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "extract":
        if len(sys.argv) < 3:
            print("Usage: narrative_weaver.py extract <journal_entry>")
            sys.exit(1)
        narratives = extract_micro_narratives(journal_entry=sys.argv[2])
        print(f"Extracted {len(narratives)} micro-narratives:")
        for n in narratives:
            print(f"  [{n['arc_type']}] {n['title']}")

    elif cmd == "weave":
        narratives = extract_micro_narratives()
        result = weave_into_arcs(narratives)
        print(f"Weave complete: {result['new_arcs_created']} new arcs, "
              f"{result['arcs_extended']} extended, "
              f"{len(result['high_resonance_flags'])} flagged for identity proposal")

    elif cmd == "active":
        arcs = get_active_arcs()
        print(f"Active arcs ({len(arcs)}):")
        for a in arcs:
            print(f"  [{a['resonance_score']:.2f}] {a['title']} — {a.get('arc_type')}")

    elif cmd == "complete":
        if len(sys.argv) < 3:
            print("Usage: narrative_weaver.py complete <arc_id>")
            sys.exit(1)
        complete_arc(sys.argv[2])
        print("Arc marked complete")

    else:
        print(f"Unknown command: {cmd}")
