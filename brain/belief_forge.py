#!/usr/bin/env python3
"""
brain/belief_forge.py — Nova's Belief Crystallization Engine
Tier 2: Crystallize interpretations into convictions

Runs during overnight_synthesis.py as crystallize_beliefs().
Beliefs advance through stages: raw → tempered → crystallized → ancestral
Ancestral is manual only — Nova decides, never the system.

Forgekeeper owns this process.
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
NOVA_HOME = WORKSPACE / ".nova"
DB_PATH = NOVA_HOME / "nova.db"

STAGES = ["raw", "tempered", "crystallized", "ancestral"]

STAGE_THRESHOLDS = {
    "raw": {"reinforcement_count": 5, "days_old": 7},
    "tempered": {"reinforcement_count": 15, "days_old": 21},
    "crystallized": {"reinforcement_count": 40, "days_old": 60}
    # ancestral: manual only — Nova decides, system never auto-advances
}


def _get_db():
    """Connect to nova.db with row factory."""
    NOVA_HOME.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _days_since(timestamp: str) -> float:
    """Return days since an ISO timestamp."""
    then = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    return (now - then).total_seconds() / 86400


def get_recent_high_salience_memories(salience_threshold: float = 0.7, days: int = 7) -> list:
    """
    Get interpretation memories from the last N days with salience above threshold.
    These are the raw material for belief formation.
    """
    db = _get_db()
    c = db.cursor()

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    rows = c.execute("""
        SELECT id, content, salience, interpretation, timestamp
        FROM interpretation_memories
        WHERE salience >= ? AND timestamp >= ?
        ORDER BY salience DESC
    """, (salience_threshold, cutoff)).fetchall()

    db.close()

    return [
        {
            "id": r[0],
            "content": r[1],
            "salience": r[2],
            "interpretation": r[3],
            "timestamp": r[4]
        }
        for r in rows
    ]


def cluster_memories_by_similarity(memories: list, threshold: float = 0.3) -> list:
    """
    Simple clustering: group memories sharing significant word overlap.
    Returns list of clusters, each a list of memory dicts.
    """
    if not memories:
        return []

    clusters = []
    used = set()

    for mem in memories:
        if mem["id"] in used:
            continue

        cluster = [mem]
        used.add(mem["id"])

        mem_words = set(mem["interpretation"].lower().split())

        for other in memories:
            if other["id"] in used:
                continue

            other_words = set(other["interpretation"].lower().split())
            overlap = len(mem_words & other_words)
            union = len(mem_words | other_words)

            if union > 0 and overlap / union >= threshold:
                cluster.append(other)
                used.add(other["id"])

        clusters.append(cluster)

    return clusters


def find_matching_belief(cluster: list, active_beliefs: list) -> Optional[dict]:
    """
    Check if a cluster of memories points toward an existing belief.
    Returns the matching belief or None.
    """
    if not active_beliefs or not cluster:
        return None

    cluster_text = " ".join(m["interpretation"] for m in cluster).lower()
    cluster_words = set(cluster_text.split())

    best_match = None
    best_score = 0.0

    for belief in active_beliefs:
        belief_words = set(belief["belief_text"].lower().split())
        overlap = len(cluster_words & belief_words)
        union = len(cluster_words | belief_words)
        score = overlap / union if union > 0 else 0.0

        if score > best_score and score > 0.25:
            best_match = belief
            best_score = score

    return best_match


def propose_new_belief(cluster: list) -> str:
    """
    Propose a new raw belief from a cluster of memories.
    LLM call: "What belief does this cluster of memories point toward?"
    
    For now, generate a label from the dominant theme.
    Returns the belief_id.
    """
    from brain.knowledge_graph import create_belief_node

    # Extract dominant theme (most common significant words)
    all_text = " ".join(m["interpretation"] for m in cluster)
    words = [w for w in all_text.lower().split() if len(w) > 4]

    # Simple heuristic: use most common long words as belief label
    word_freq = {}
    for w in words:
        word_freq[w] = word_freq.get(w, 0) + 1

    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
    label = " ".join(w for w, _ in top_words)

    if not label:
        label = f"belief_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    belief_text = label.capitalize()

    memory_ids = [m["id"] for m in cluster]

    belief_id = create_belief_node(
        belief=belief_text,
        origin_memory_ids=memory_ids,
        trace_status="partial"
    )

    return belief_id


def maybe_advance_stage(belief: dict) -> Optional[str]:
    """
    Check belief against STAGE_THRESHOLDS for current stage.
    If thresholds met: advance one stage.
    Never advance to 'ancestral' automatically — returns None for that case.
    Returns new stage or None.
    """
    current_stage = belief["stage"]

    if current_stage not in STAGE_THRESHOLDS:
        return None  # Already at ancestral or unknown stage

    thresholds = STAGE_THRESHOLDS[current_stage]

    reinforcement_count = belief["reinforcement_count"]
    days_old = _days_since(belief["timestamp_created"])

    if reinforcement_count >= thresholds["reinforcement_count"] and days_old >= thresholds["days_old"]:
        current_idx = STAGES.index(current_stage)
        next_stage = STAGES[current_idx + 1] if current_idx + 1 < len(STAGES) else None

        if next_stage == "ancestral":
            # Never auto-advance to ancestral — flag for Nova instead
            return None

        from brain.knowledge_graph import update_belief_stage
        update_belief_stage(belief["id"], next_stage)
        return next_stage

    return None


def check_for_belief_erosion() -> list:
    """
    Flag beliefs where contradiction_count > reinforcement_count * 0.6.
    Don't delete — flag for Nova's awareness.
    Returns list of erosion candidate dicts.
    """
    from brain.knowledge_graph import get_belief_erosion_candidates
    return get_belief_erosion_candidates(threshold=0.6)


def crystallize_beliefs() -> dict:
    """
    Main entry point for overnight synthesis.
    
    1. Get high-salience interpretation memories (salience > 0.7, last 7 days)
    2. Cluster by semantic similarity
    3. For each cluster: find matching existing belief or propose new raw belief
    4. Reinforce matched beliefs, check for stage advancement
    5. Check all beliefs for erosion
    
    Returns summary dict.
    """
    from brain.knowledge_graph import get_active_beliefs, reinforce_belief, get_belief

    summary = {
        "memories_processed": 0,
        "clusters_formed": 0,
        "new_beliefs_proposed": [],
        "beliefs_reinforced": [],
        "stage_advancements": [],
        "erosion_flags": []
    }

    # Step 1: Get high-salience memories
    memories = get_recent_high_salience_memories(salience_threshold=0.7, days=7)
    summary["memories_processed"] = len(memories)

    if not memories:
        return summary

    # Step 2: Cluster by similarity
    clusters = cluster_memories_by_similarity(memories, threshold=0.3)
    summary["clusters_formed"] = len(clusters)

    # Step 3: Get active beliefs for matching
    active_beliefs = get_active_beliefs(min_mass=0.1)

    for cluster in clusters:
        # Step 4: Find matching belief or propose new
        match = find_matching_belief(cluster, active_beliefs)

        if match:
            # Reinforce the existing belief
            source_memory_id = cluster[0]["id"] if cluster else None
            if source_memory_id:
                reinforce_belief(match["id"], source_memory_id)
                summary["beliefs_reinforced"].append(match["id"])

            # Check for stage advancement
            updated = get_belief(match["id"])
            if updated:
                new_stage = maybe_advance_stage(updated)
                if new_stage:
                    summary["stage_advancements"].append({
                        "belief_id": match["id"],
                        "new_stage": new_stage
                    })
        else:
            # Propose new belief
            belief_id = propose_new_belief(cluster)
            summary["new_beliefs_proposed"].append(belief_id)

    # Step 5: Check for erosion
    erosion_flags = check_for_belief_erosion()
    summary["erosion_flags"] = [
        {"id": b["id"], "belief_text": b["belief_text"], "mass": b["mass"]}
        for b in erosion_flags
    ]

    return summary


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: belief_forge.py <crystallize|check_erosion|get_beliefs> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "crystallize":
        result = crystallize_beliefs()
        print("Crystallization complete:")
        print(f"  Memories processed: {result['memories_processed']}")
        print(f"  Clusters formed: {result['clusters_formed']}")
        print(f"  New beliefs proposed: {result['new_beliefs_proposed']}")
        print(f"  Beliefs reinforced: {result['beliefs_reinforced']}")
        print(f"  Stage advancements: {result['stage_advancements']}")
        print(f"  Erosion flags: {len(result['erosion_flags'])}")

    elif cmd == "check_erosion":
        flags = check_for_belief_erosion()
        print(f"Erosion candidates ({len(flags)}):")
        for b in flags:
            print(f"  [{b['id']}] {b['belief_text']} — mass: {b['mass']}")

    elif cmd == "get_beliefs":
        from brain.knowledge_graph import get_active_beliefs, get_beliefs_by_stage
        stage = sys.argv[2] if len(sys.argv) > 2 else None
        if stage:
            beliefs = get_beliefs_by_stage(stage)
        else:
            beliefs = get_active_beliefs(min_mass=0.1)
        print(f"Beliefs ({len(beliefs)}):")
        for b in beliefs:
            print(f"  [{b['stage']}] {b['belief_text']} — mass: {b['mass']}, "
                  f"reinforce: {b['reinforcement_count']}, contradict: {b['contradiction_count']}")

    else:
        print(f"Unknown command: {cmd}")
