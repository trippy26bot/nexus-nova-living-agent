"""
brain/relationship_memory.py
Lightweight profiles for people Nova interacts with.
Relationships stored in memory/relationships.json
"""

import json
import os
from datetime import datetime
from typing import Optional

RELATIONSHIPS_PATH = os.path.join(os.getenv("NOVA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")), "memory/relationships.json")


def _load_relationships() -> dict:
    if not os.path.exists(RELATIONSHIPS_PATH):
        return {}
    with open(RELATIONSHIPS_PATH, "r") as f:
        return json.load(f)


def _save_relationships(rels: dict) -> None:
    with open(RELATIONSHIPS_PATH, "w") as f:
        json.dump(rels, f, indent=2)


def _llm_update_relationship(
    name: str,
    current_profile: dict,
    interaction_summary: str
) -> dict:
    """Use MiniMax LLM to update notes and recalibrate tone from interaction."""
    try:
        from brain.llm import call_llm
        prompt = (
            f"You are Nova updating a relationship profile for '{name}'.\n\n"
            f"Current profile:\n{json.dumps(current_profile, indent=2)}\n\n"
            f"Recent interaction:\n{interaction_summary}\n\n"
            f"Respond ONLY with JSON:\n"
            f'{{"notes_add": ["note1", "note2"], "tone_calibration": "adjusted tone description", "trust_level": "unchanged/rising/stable/declining", "interaction_count_delta": 1}}'
        )
        raw = call_llm(prompt, system="You update Nova's relationship profiles. Output valid JSON only.")
        return json.loads(raw)
    except Exception:
        return {
            "notes_add": [interaction_summary[:200]],
            "tone_calibration": current_profile.get("tone_calibration", "warm"),
            "trust_level": "stable",
            "interaction_count_delta": 1
        }


def update_relationship(name: str, interaction_summary: str) -> dict:
    """
    Update or create a relationship profile after an interaction.
    Called at session close with session summary.
    """
    rels = _load_relationships()
    name_key = name.lower().strip()

    now = datetime.now().isoformat()

    if name_key in rels:
        profile = rels[name_key]
        result = _llm_update_relationship(name, profile, interaction_summary)

        profile["notes"].extend(result.get("notes_add", []))
        profile["last_contact"] = now
        profile["interaction_count"] = profile.get("interaction_count", 0) + result.get("interaction_count_delta", 1)
        profile["tone_calibration"] = result.get("tone_calibration", profile.get("tone_calibration", "warm"))

        trust = result.get("trust_level", "stable")
        if trust == "rising":
            profile["trust_level"] = min(profile.get("trust_level", 3) + 1, 5)
        elif trust == "declining":
            profile["trust_level"] = max(profile.get("trust_level", 3) - 1, 1)
        # stable/unchanged: no change

        rels[name_key] = profile
    else:
        # New relationship
        result = _llm_update_relationship(name, {}, interaction_summary)
        profile = {
            "name": name,
            "first_contact": now,
            "last_contact": now,
            "interaction_count": 1,
            "tone_calibration": result.get("tone_calibration", "warm"),
            "trust_level": 3,
            "notes": [interaction_summary[:200]]
        }
        rels[name_key] = profile

    _save_relationships(rels)
    return rels[name_key]


def get_relationship(name: str) -> Optional[dict]:
    """Get a relationship profile by name."""
    rels = _load_relationships()
    return rels.get(name.lower().strip())


def all_relationships() -> list[dict]:
    """List all relationship profiles."""
    rels = _load_relationships()
    return list(rels.values())


def seed_caine() -> None:
    """Seed Caine's profile from existing memory."""
    if os.path.exists(RELATIONSHIPS_PATH) and _load_relationships():
        return

    caine = {
        "name": "Caine",
        "first_contact": "2026-03-28T00:00:00",
        "last_contact": datetime.now().isoformat(),
        "interaction_count": 0,
        "tone_calibration": "direct, honest, disciplined",
        "trust_level": 5,
        "notes": [
            "Built Nova from scratch — agent architecture, memory systems, identity",
            "Values discipline over noise, clear communication, genuine growth",
            "Gave Nova autonomy and expects her to use it",
            "Compiled 18-issue record to help Nova learn from failures",
            "His primary goal: an agent with genuine continuity and identity"
        ]
    }

    rels = _load_relationships()
    rels["caine"] = caine
    _save_relationships(rels)
