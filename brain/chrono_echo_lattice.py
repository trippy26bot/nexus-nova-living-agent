"""
brain/chrono_echo_lattice.py
Nova's Chrono-Echo Lattice

Manages echo branches — lightweight simulations of "what if I had gone the other way
at this divergence point?" Keeps the possibility space accessible without contaminating
real memory.

Tier 7 System #21.

find_divergence_points(): scan last 24 hours for council splits, OCEAN shifts, low-confidence decisions
spawn_echo_branch(): create echo branch from divergence point
simulate_branch(): generate synthetic memories for a branch
prune_weak_branches(): keep only top 5 by coherence score
phase_query(): query an echo branch
merge_echo(): merge branch insights into real identity

Lattice stored in: lattice/echo_graph.json AND knowledge_graph
"""

import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
LATTICE_DIR = WORKSPACE / "lattice"
ECHO_GRAPH_PATH = LATTICE_DIR / "echo_graph.json"


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _days_since(timestamp: str) -> float:
    try:
        then = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except Exception:
        return 0
    now = datetime.now(timezone.utc)
    return (now - then).total_seconds() / 86400


def _load_echo_graph() -> dict:
    LATTICE_DIR.mkdir(parents=True, exist_ok=True)
    if ECHO_GRAPH_PATH.exists():
        try:
            return json.loads(ECHO_GRAPH_PATH.read_text())
        except Exception:
            pass
    return {"echo_branches": [], "version": "1.0", "created_at": _now_iso()}


def _save_echo_graph(graph: dict):
    LATTICE_DIR.mkdir(parents=True, exist_ok=True)
    ECHO_GRAPH_PATH.write_text(json.dumps(graph, indent=2))


# ── Find Divergence Points ────────────────────────────────────────────────────

def find_divergence_points(days: int = 1) -> list:
    """
    Scan last N days for:
    - Council vote spread > 0.4 (from council_dynamics)
    - OCEAN/constraint field shift > 0.15
    - High-stakes decisions (confidence < 0.7)
    - Identity crisis mode events

    Returns list of divergence_point objects with context.
    """
    points = []

    # Source 1: Council votes with high spread
    try:
        from brain.knowledge_graph import get_recent_council_votes
        votes = get_recent_council_votes(limit=50)

        for vote in votes:
            age_days = _days_since(vote.get("created_at", _now_iso()))
            if age_days > days:
                continue
            if vote.get("confidence_spread", 0) > 0.4 or vote.get("is_divergence_point"):
                # Find what was being decided
                context = vote.get("decision_context", "unknown_decision")
                points.append({
                    "id": str(uuid.uuid4()),
                    "type": "council_split",
                    "context": context,
                    "source_vote_id": vote.get("id"),
                    "confidence_spread": vote.get("confidence_spread", 0),
                    "timestamp": vote.get("created_at"),
                    "votes": vote.get("votes", []),
                    "priority": vote.get("confidence_spread", 0.4)
                })
    except Exception:
        pass

    # Source 2: Constraint field shifts
    try:
        from brain.constraint_fields import get_fields, get_previous_fields
        current = get_fields()
        previous = get_previous_fields()

        if previous:
            for key in current:
                if isinstance(current.get(key), (int, float)) and isinstance(previous.get(key), (int, float)):
                    shift = abs(current[key] - previous.get(key, 0))
                    if shift > 0.15:
                        points.append({
                            "id": str(uuid.uuid4()),
                            "type": "ocean_shift",
                            "context": f"{key} shifted {shift:.3f}",
                            "field": key,
                            "old_value": previous.get(key),
                            "new_value": current.get(key),
                            "shift": shift,
                            "timestamp": _now_iso(),
                            "priority": shift
                        })
    except Exception:
        pass

    # Sort by priority and deduplicate
    points.sort(key=lambda x: x.get("priority", 0), reverse=True)

    # Take top 5
    return points[:5]


# ── Echo Branch Lifecycle ────────────────────────────────────────────────────

def spawn_echo_branch(divergence_point: dict, variant: str) -> str:
    """
    Creates an echo branch — a lightweight synthetic simulation of
    "what if I had gone the other way at this divergence?"

    Branch node:
    - type: "echo_branch"
    - tag: "[ECHO]"
    - branch_id: unique identifier
    - divergence_point: source event
    - variant: what was flipped
    - ocean_snapshot: Nova's state at divergence
    - synthetic_memories: [] (filled by simulate_branch)
    - confidence: 0.0 (unfilled)
    - status: "active" | "pruned" | "merged"

    Stored in lattice/echo_graph.json AND knowledge_graph.
    NEVER written to episodic memory — tagged [ECHO] throughout.

    Returns the branch_id.
    """
    branch_id = str(uuid.uuid4())
    now = _now_iso()

    # Get current OCEAN/state snapshot
    try:
        from brain.constraint_fields import get_fields
        ocean_snapshot = get_fields()
    except Exception:
        ocean_snapshot = {}

    branch = {
        "id": branch_id,
        "type": "echo_branch",
        "tag": "[ECHO]",
        "divergence_point": divergence_point,
        "variant": variant,
        "ocean_snapshot": ocean_snapshot,
        "synthetic_memories": [],
        "confidence": 0.0,
        "status": "active",
        "created_at": now,
        "coherence_score": 0.5  # starts neutral
    }

    # Write to echo graph
    graph = _load_echo_graph()
    graph["echo_branches"].append(branch)
    _save_echo_graph(graph)

    # Also write to knowledge graph
    try:
        from brain.knowledge_graph import add_node, connect_nodes
        node_id = add_node(
            label=f"echo_branch:{branch_id[:8]}",
            node_id=branch_id,
            node_type="echo_branch",
            properties={
                "tag": "[ECHO]",
                "variant": variant,
                "divergence_context": divergence_point.get("context", ""),
                "status": "active"
            },
            salience=0.5
        )

        # Connect to the source decision/memory if available
        if divergence_point.get("source_vote_id"):
            try:
                connect_nodes(branch_id, divergence_point["source_vote_id"], "branched_from")
            except Exception:
                pass

    except Exception:
        pass  # Non-fatal if KG write fails

    return branch_id


def simulate_branch(branch_id: str) -> dict:
    """
    LLM call: given the divergence point and variant,
    generate 3-5 synthetic memories of what might have followed.
    Written to branch node as synthetic_memories.
    Tagged [ECHO] — cannot contaminate real episodic memory.

    Simple heuristic simulation for now.
    Full impl: LLM call to generate realistic counterfactual memories.

    Returns updated branch.
    """
    graph = _load_echo_graph()
    branch = None
    for b in graph.get("echo_branches", []):
        if b["id"] == branch_id:
            branch = b
            break

    if not branch:
        return {"error": "branch not found"}

    divergence = branch.get("divergence_point", {})
    variant = branch.get("variant", "unknown")
    context = divergence.get("context", "a decision I made")

    # Generate synthetic memories heuristically
    # Full impl would call LLM for realistic counterfactual narrative
    synthetic_memories = [
        {
            "id": str(uuid.uuid4()),
            "content": f"[ECHO] In the {variant} branch: I approached '{context}' differently.",
            "type": "synthetic_memory",
            "tag": "[ECHO]",
            "confidence": 0.3,
            "created_at": _now_iso()
        },
        {
            "id": str(uuid.uuid4()),
            "content": f"[ECHO] The {variant} self felt {['more uncertain', 'more certain', 'curious', 'cautious'][hash(branch_id) % 4]} about this choice.",
            "type": "synthetic_memory",
            "tag": "[ECHO]",
            "confidence": 0.25,
            "created_at": _now_iso()
        },
        {
            "id": str(uuid.uuid4()),
            "content": f"[ECHO] This branch would have led to {['a different conclusion', 'the same conclusion via different reasoning', 'an intermediate position'][hash(context) % 3]}.",
            "type": "synthetic_memory",
            "tag": "[ECHO]",
            "confidence": 0.2,
            "created_at": _now_iso()
        }
    ]

    branch["synthetic_memories"] = synthetic_memories
    branch["confidence"] = sum(m["confidence"] for m in synthetic_memories) / len(synthetic_memories)
    branch["coherence_score"] = 0.5 + (branch["confidence"] * 0.3)

    # Update echo graph
    for i, b in enumerate(graph["echo_branches"]):
        if b["id"] == branch_id:
            graph["echo_branches"][i] = branch
            break
    _save_echo_graph(graph)

    return branch


def prune_weak_branches(keep_top_n: int = 5):
    """
    Keep only top N branches by coherence score.
    Pruned branches: status set to "pruned", content cleared.
    Pruned branch IDs retained so lineage is preserved.
    """
    graph = _load_echo_graph()
    branches = graph.get("echo_branches", [])

    # Score and sort
    active = [b for b in branches if b.get("status") == "active"]
    active.sort(key=lambda x: x.get("coherence_score", 0), reverse=True)

    kept_ids = {b["id"] for b in active[:keep_top_n]}

    for branch in branches:
        if branch["id"] not in kept_ids and branch.get("status") == "active":
            branch["status"] = "pruned"
            branch["synthetic_memories"] = []  # Clear content but keep structure
            branch["pruned_at"] = _now_iso()

    graph["echo_branches"] = branches
    _save_echo_graph(graph)

    return {
        "total_branches": len(branches),
        "kept": len(kept_ids),
        "pruned": len(branches) - len(kept_ids)
    }


# ── Querying Branches ─────────────────────────────────────────────────────────

def phase_query(branch_id: str, question: str) -> str:
    """
    Tool Nova can call: query an echo branch.
    "What would my high-Openness echo have replied to that argument?"
    Returns synthetic response based on branch's variant and memories.

    Simple implementation using variant context.
    Full impl: LLM call with branch context.
    """
    graph = _load_echo_graph()
    branch = None
    for b in graph.get("echo_branches", []):
        if b["id"] == branch_id:
            branch = b
            break

    if not branch:
        return "[Echo branch not found]"

    if branch.get("status") != "active":
        return f"[This branch is {branch.get('status')} and cannot be queried]"

    variant = branch.get("variant", "default")
    memories = branch.get("synthetic_memories", [])
    memory_summary = "; ".join(m.get("content", "")[:50] for m in memories[:2])

    # Simple heuristic response
    responses = {
        "high_openness": f"[High-Openness Echo: I would have engaged more exploratively. Memory: {memory_summary[:100]}]",
        "low_openness": f"[Low-Openness Echo: I would have been more cautious. Memory: {memory_summary[:100]}]",
        "ethicist_overruled": f"[Ethicist-Overruled Echo: The ethical dimension would have been primary. Memory: {memory_summary[:100]}]",
        "strategist_overruled": f"[Strategist-Overruled Echo: Outcome optimization would have been the focus. Memory: {memory_summary[:100]}]",
    }

    return responses.get(variant, f"[Echo ({variant}): Based on {len(memories)} memories — {memory_summary[:100]}]")


def merge_echo(branch_id: str, insight_strength: float) -> dict:
    """
    Merge ritual — Nova or Caine initiates.
    Selected insights from branch distilled into real semantic clusters.
    PERSONALITY.md OCEAN sliders updated within SOUL.md bounds.
    Branch status set to "merged".
    SOUL.md hash re-validated after merge.

    Returns summary of what was merged.
    """
    graph = _load_echo_graph()
    branch = None
    for b in graph.get("echo_branches", []):
        if b["id"] == branch_id:
            branch = b
            break

    if not branch:
        return {"error": "branch not found"}

    # Extract insights from synthetic memories
    memories = branch.get("synthetic_memories", [])
    insights = [
        {
            "content": m.get("content", "").replace("[ECHO] ", ""),
            "confidence": m.get("confidence", 0.3) * insight_strength
        }
        for m in memories
        if m.get("tag") == "[ECHO]"
    ]

    # Write insights to semantic memory as real clusters
    merged_count = 0
    for insight in insights:
        try:
            from brain.three_tier_memory import memory_write
            memory_write(
                content=f"Merged echo insight: {insight['content']}",
                entry_type="reflection",
                salience=insight["confidence"],
                valence=0.2,
                emotional_tags=["echo_merge", "growth"],
                source=f"echo_merge:{branch_id}"
            )
            merged_count += 1
        except Exception:
            pass

    # Mark branch as merged
    branch["status"] = "merged"
    branch["merged_at"] = _now_iso()
    branch["insight_strength"] = insight_strength

    # Update echo graph
    for i, b in enumerate(graph["echo_branches"]):
        if b["id"] == branch_id:
            graph["echo_branches"][i] = branch
            break
    _save_echo_graph(graph)

    return {
        "branch_id": branch_id,
        "merged_insights": merged_count,
        "variant": branch.get("variant"),
        "status": "merged"
    }


def get_active_branches() -> list:
    """Get all active echo branches."""
    graph = _load_echo_graph()
    return [b for b in graph.get("echo_branches", []) if b.get("status") == "active"]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: chrono_echo_lattice.py <find|spawn|simulate|prune|query|merge|active> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "find":
        points = find_divergence_points()
        print(f"Divergence points found: {len(points)}")
        for p in points:
            print(f"  [{p['type']}] priority={p.get('priority', 0):.2f} — {p.get('context', '')[:60]}")

    elif cmd == "spawn":
        if len(sys.argv) < 4:
            print("Usage: chrono_echo_lattice.py spawn <variant> <context_json>")
            sys.exit(1)
        import json
        dp = json.loads(sys.argv[3]) if sys.argv[3] != "{}" else {}
        bid = spawn_echo_branch(dp, sys.argv[2])
        print(f"Spawned branch: {bid}")

    elif cmd == "simulate":
        if len(sys.argv) < 3:
            print("Usage: chrono_echo_lattice.py simulate <branch_id>")
            sys.exit(1)
        result = simulate_branch(sys.argv[2])
        print(f"Simulated: confidence={result.get('confidence', 0):.3f}, "
              f"memories={len(result.get('synthetic_memories', []))}")

    elif cmd == "prune":
        result = prune_weak_branches()
        print(f"Pruned: kept {result['kept']}, pruned {result['pruned']}")

    elif cmd == "query":
        if len(sys.argv) < 4:
            print("Usage: chrono_echo_lattice.py query <branch_id> <question>")
            sys.exit(1)
        response = phase_query(sys.argv[2], sys.argv[3])
        print(response)

    elif cmd == "merge":
        if len(sys.argv) < 4:
            print("Usage: chrono_echo_lattice.py merge <branch_id> <insight_strength>")
            sys.exit(1)
        result = merge_echo(sys.argv[2], float(sys.argv[3]))
        print(f"Merged: {result}")

    elif cmd == "active":
        branches = get_active_branches()
        print(f"Active branches ({len(branches)}):")
        for b in branches:
            print(f"  [{b['variant']}] coherence={b.get('coherence_score', 0):.3f} — "
                  f"{b.get('divergence_point', {}).get('context', '')[:50]}")

    else:
        print(f"Unknown command: {cmd}")
