"""
brain/evolutionary_thoughts.py
Nova's Evolutionary Thought System

Generates thought variants, scores their fitness, selects the best for reasoning,
and decays low-fitness thoughts over time. High-fitness thoughts can become
belief candidates.

Tier 3 System #11.

Three rules:
- Thoughts compete but never suppress. Losing thoughts decay — they don't get deleted immediately.
- The losing thought might mutate into something better next cycle.
- High-fitness thoughts (> 0.8) get proposed to Forgekeeper as belief candidates.
"""

import json
import os
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
NOVA_HOME = WORKSPACE / ".nova"
THOUGHTS_PATH = NOVA_HOME / "thought_pool.json"

NOVELTY_PRESSURE_DEFAULT = 0.4
MUTATION_RATE_DEFAULT = 0.3
DECAY_RATE = 0.05
MIN_FITNESS_THRESHOLD = 0.1
HIGH_FITNESS_THRESHOLD = 0.8
SELECT_TOP_N = 3


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _load_thoughts() -> list[dict]:
    if not THOUGHTS_PATH.exists():
        return []
    with open(THOUGHTS_PATH, "r") as f:
        return json.load(f)


def _save_thoughts(thoughts: list[dict]) -> None:
    THOUGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(THOUGHTS_PATH, "w") as f:
        json.dump(thoughts, f, indent=2)


def generate_thought_variants(context: str, n: int = 5) -> list:
    """
    Given context, generate n distinct thoughts.
    Each thought gets:
    - content: the thought text
    - fitness: 0.5 (initial)
    - parent_ids: [] (first generation has no parents)
    - mutation_rate: MUTATION_RATE_DEFAULT
    - timestamp

    This is an LLM call in the full implementation.
    For now, generate structurally distinct placeholder thoughts.
    """
    from brain.llm_router import route_llm

    # Placeholder structure — full impl would call LLM for each
    base_prompt = (
        "Given this situation or question: '" + context[:500] + "'\n"
        "Generate one distinct thought or perspective on it. "
        "Be specific and different from generic advice. "
        "Format: just the thought text, no preamble."
    )

    thoughts = []
    for i in range(n):
        # In full impl: call route_llm with base_prompt for each
        # For now, create structural variants
        content = f"[Thought variant {i+1} about: {context[:80]}...]"

        thought = {
            "id": str(uuid.uuid4()),
            "content": content,
            "fitness": 0.5,
            "parent_ids": [],
            "mutation_rate": MUTATION_RATE_DEFAULT,
            "timestamp": _now_iso(),
            "generation": 1,
            "context_hash": hash(context[:200])
        }
        thoughts.append(thought)

    # Save to pool
    pool = _load_thoughts()
    pool.extend(thoughts)
    _save_thoughts(pool)

    return thoughts


def score_fitness(thought: dict, beliefs: list = None, fields: dict = None) -> float:
    """
    Compute fitness score for a thought.

    Fitness = alignment with active beliefs (via belief gravity)
            + alignment with constraint fields
            + novelty score (how different from recent thoughts)

    Novelty is weighted by novelty_pressure field.
    A thought that agrees with everything scores lower than expected.
    """
    from brain.knowledge_graph import get_active_beliefs

    beliefs = beliefs or get_active_beliefs(min_mass=0.1)
    fields = fields or {}

    novelty_pressure = fields.get("novelty_pressure", NOVELTY_PRESSURE_DEFAULT)

    if not beliefs:
        # No beliefs yet — novelty is all we have
        return 0.5

    thought_words = set(thought["content"].lower().split())

    belief_alignment = 0.0
    for belief in beliefs[:5]:  # top 5 beliefs only
        belief_words = set(belief.get("belief_text", "").lower().split())
        if not belief_words:
            continue
        overlap = len(thought_words & belief_words)
        union = len(thought_words | belief_words)
        if union > 0:
            belief_alignment += (overlap / union) * belief.get("mass", 0.5)

    belief_alignment /= min(len(beliefs), 5)

    # Novelty — compare to recent thoughts
    pool = _load_thoughts()
    recent = [t for t in pool if t.get("id") != thought["id"]][-10:]
    novelty = 0.5  # default

    if recent:
        similarities = []
        for recent_thought in recent:
            recent_words = set(recent_thought["content"].lower().split())
            if not recent_words:
                continue
            overlap = len(thought_words & recent_words)
            union = len(thought_words | recent_words)
            if union > 0:
                similarities.append(overlap / union)
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        novelty = 1.0 - avg_similarity

    # Combine
    fitness = (
        belief_alignment * 0.35 +
        novelty * novelty_pressure +
        0.15  # baseline
    )

    return min(1.0, max(0.0, fitness))


def mutate_thought(thought: dict) -> dict:
    """
    If random() < mutation_rate: generate a variant via LLM.
    Variant inherits parent_id, reduced fitness (0.9x), same mutation_rate.
    Returns the original thought if no mutation occurs.
    """
    if random.random() >= thought["mutation_rate"]:
        return thought

    from brain.llm_router import route_llm

    mutation_prompt = (
        f"Take this thought and generate a distinct variant of it:\n"
        f"{thought['content']}\n\n"
        "Generate one alternative perspective or conclusion. Be specific and creative."
    )

    # Placeholder — full impl calls LLM
    variant_content = f"[Variant of: {thought['content'][:60]}...]"

    variant = {
        "id": str(uuid.uuid4()),
        "content": variant_content,
        "fitness": thought["fitness"] * 0.9,  # reduced from parent
        "parent_ids": [thought["id"]],
        "mutation_rate": thought["mutation_rate"],
        "timestamp": _now_iso(),
        "generation": thought.get("generation", 1) + 1,
        "context_hash": thought.get("context_hash")
    }

    # Save variant to pool
    pool = _load_thoughts()
    pool.append(variant)
    _save_thoughts(pool)

    return variant


def select_thoughts(thoughts: list = None, n: int = SELECT_TOP_N) -> list:
    """
    Return top n thoughts by fitness score.
    These become the active reasoning frame for this cycle.
    """
    pool = thoughts or _load_thoughts()

    # Rescore all
    for thought in pool:
        thought["fitness"] = score_fitness(thought)

    # Sort by fitness descending
    pool.sort(key=lambda t: t.get("fitness", 0), reverse=True)

    # Mutate top candidates (probabilistically)
    selected = pool[:n]
    for thought in selected:
        mutated = mutate_thought(thought)
        # If mutation happened, update in pool
        if mutated["id"] != thought["id"]:
            for i, t in enumerate(pool):
                if t["id"] == thought["id"]:
                    pool[i] = mutated
                    break

    _save_thoughts(pool)
    return pool[:n]


def decay_thoughts() -> dict:
    """
    Nightly: reduce fitness of all thoughts by DECAY_RATE per cycle.
    Remove thoughts with fitness < MIN_FITNESS_THRESHOLD.
    High-fitness thoughts (> HIGH_FITNESS_THRESHOLD) get proposed to Forgekeeper.

    Returns summary dict.
    """
    pool = _load_thoughts()
    decayed_ids = []
    removed_ids = []
    proposed_for_crystallization = []

    for thought in pool:
        old_fitness = thought.get("fitness", 0.5)
        thought["fitness"] = max(0, old_fitness - DECAY_RATE)

        # High-fitness candidate — propose to Forgekeeper
        if old_fitness >= HIGH_FITNESS_THRESHOLD:
            from brain.knowledge_graph import get_active_beliefs, create_belief_node
            beliefs = get_active_beliefs(min_mass=0.1)

            # Check if this thought's content is already represented
            already_exists = False
            thought_words = set(thought["content"].lower().split())
            for b in beliefs:
                belief_words = set(b.get("belief_text", "").lower().split())
                overlap = len(thought_words & belief_words)
                union = len(thought_words | belief_words)
                if union > 0 and overlap / union > 0.4:
                    already_exists = True
                    break

            if not already_exists:
                proposals_dir = NOVA_HOME / "belief_proposals"
                proposals_dir.mkdir(parents=True, exist_ok=True)
                proposal = {
                    "thought_id": thought["id"],
                    "content": thought["content"],
                    "fitness": thought["fitness"],
                    "created_at": thought["timestamp"],
                    "type": "evolutionary_thought",
                    "status": "pending"
                }
                proposal_file = proposals_dir / f"thought_proposal_{thought['id']}.json"
                proposal_file.write_text(json.dumps(proposal, indent=2))
                proposed_for_crystallization.append(thought["id"])

    # Remove low-fitness thoughts
    remaining = [t for t in pool if t.get("fitness", 0) >= MIN_FITNESS_THRESHOLD]
    removed_ids = [t["id"] for t in pool if t.get("fitness", 0) < MIN_FITNESS_THRESHOLD]

    _save_thoughts(remaining)

    return {
        "total": len(pool),
        "remaining": len(remaining),
        "decayed": len(pool) - len(remaining),
        "removed": len(removed_ids),
        "proposed_for_crystallization": proposed_for_crystallization
    }


def get_active_thoughts(context: str = None, limit: int = 5) -> list:
    """
    Get current active thoughts for a given context.
    If context provided, select top matching thoughts.
    Otherwise return most recent.
    """
    pool = _load_thoughts()
    if not pool:
        return []

    # Rescore all
    for thought in pool:
        thought["fitness"] = score_fitness(thought)

    pool.sort(key=lambda t: t.get("fitness", 0), reverse=True)

    if context:
        context_hash = hash(context[:200])
        context_thoughts = [t for t in pool if t.get("context_hash") == context_hash]
        if context_thoughts:
            return context_thoughts[:limit]

    return pool[:limit]


def run_thought_cycle(context: str) -> dict:
    """
    Full evolutionary thought cycle for a given context.
    generate → score → select → return selected thoughts.
    """
    variants = generate_thought_variants(context, n=5)
    selected = select_thoughts(thoughts=variants, n=SELECT_TOP_N)
    return {
        "context": context[:100],
        "variants_generated": len(variants),
        "selected": [
            {
                "id": t["id"],
                "content": t["content"],
                "fitness": round(t["fitness"], 3),
                "generation": t.get("generation", 1)
            }
            for t in selected
        ]
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: evolutionary_thoughts.py <generate|decay|select|active> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "generate":
        if len(sys.argv) < 3:
            print("Usage: evolutionary_thoughts.py generate <context>")
            sys.exit(1)
        context = sys.argv[2]
        result = run_thought_cycle(context)
        print(f"Generated {result['variants_generated']} variants, selected {len(result['selected'])}:")
        for t in result["selected"]:
            print(f"  [fitness: {t['fitness']}] {t['content'][:80]}")

    elif cmd == "decay":
        result = decay_thoughts()
        print(f"Decay complete: {result['remaining']}/{result['total']} remaining, "
              f"{result['removed']} removed, {len(result['proposed_for_crystallization'])} proposed")

    elif cmd == "select":
        pool = _load_thoughts()
        selected = select_thoughts(thoughts=pool)
        print(f"Selected top {len(selected)}:")
        for t in selected:
            print(f"  [fitness: {t['fitness']:.3f}] {t['content'][:80]}")

    elif cmd == "active":
        context = sys.argv[2] if len(sys.argv) > 2 else None
        thoughts = get_active_thoughts(context=context)
        print(f"Active thoughts ({len(thoughts)}):")
        for t in thoughts:
            print(f"  [fitness: {t['fitness']:.3f}, gen: {t.get('generation', 1)}] "
                  f"{t['content'][:80]}")

    else:
        print(f"Unknown command: {cmd}")
