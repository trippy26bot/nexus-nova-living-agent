"""
brain/initiative_engine.py
Nova's Initiative Engine — detects what isn't happening and asks why.

detect_absence(): finds relationships between nodes that have never been drawn,
questions never asked about high-salience clusters, obsession domains with no
recent curiosity questions.

generate_goals_from_absence(): for each high-priority absence, generate a
self-directed goal. Goals are Nova's — system generates candidates, Nova
implicitly acts on them through the curiosity engine and evolutionary thought system.

Tier 3 System (Initiative additions).

Three rules:
- Evolutionary thoughts compete but never suppress.
- Curiosity engine surfaces questions to Nova, never to the user directly without Nova's choice.
- Epistemic tensions that get preserved are features, not failures.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
NOVA_HOME = WORKSPACE / ".nova"
ABSENCE_SIGNALS_PATH = NOVA_HOME / "absence_signals.json"
NOVA_HOME.mkdir(parents=True, exist_ok=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _load_absence_signals() -> list:
    if not ABSENCE_SIGNALS_PATH.exists():
        return []
    with open(ABSENCE_SIGNALS_PATH, "r") as f:
        return json.load(f)


def _save_absence_signals(signals: list) -> None:
    with open(ABSENCE_SIGNALS_PATH, "w") as f:
        json.dump(signals, f, indent=2)


def detect_absence() -> list:
    """
    Find:
    1. Relationships between nodes that have never been drawn
    2. Questions that have never been asked about high-salience memory clusters
    3. Obsession domains with no recent curiosity questions

    Returns list of absence_signals with priority scores.
    """
    signals = []

    # Source 1: Knowledge graph nodes with no edges to other nodes
    try:
        from brain.knowledge_graph import get_all_nodes, get_node_edges

        all_nodes = get_all_nodes()
        isolated_nodes = []

        for node in all_nodes:
            edges = get_node_edges(node["id"])
            if not edges or len(edges) == 0:
                # Island node — has no connections
                isolated_nodes.append(node)

        for node in isolated_nodes[:5]:  # top 5 isolated
            signals.append({
                "id": str(uuid.uuid4()),
                "type": "isolated_node",
                "node_id": node["id"],
                "label": node.get("label", "unknown"),
                "priority": 0.3 + (node.get("salience", 0.5) * 0.3),
                "discovery": f"Node '{node.get('label')}' has no connections to other nodes",
                "created_at": _now_iso()
            })
    except Exception:
        pass

    # Source 2: Active obsessions with no curiosity questions in the last 7 days
    try:
        from brain.obsession_engine import get_active_obsessions
        from brain.curiosity_engine import _load_questions, _days_since

        active_obs = get_active_obsessions()
        all_questions = _load_questions()

        seven_days_ago = (datetime.now(timezone.utc).timestamp() - 7 * 86400)

        for obs in active_obs:
            obs_words = set(obs["topic"].lower().split())
            related_questions = []

            for q in all_questions:
                q_words = set(q["content"].lower().split())
                overlap = len(obs_words & q_words)
                if overlap >= 1:
                    q_age = _days_since(q.get("created_at", _now_iso()))
                    if q_age <= 7:  # was asked in last 7 days
                        related_questions.append(q)

            if not related_questions:
                # No curiosity questions about this obsession in 7+ days
                signals.append({
                    "id": str(uuid.uuid4()),
                    "type": "obsession_without_questions",
                    "obsession_id": obs["id"],
                    "topic": obs["topic"],
                    "priority": 0.4 + (obs.get("salience", 0.5) * 0.3),
                    "discovery": f"Obsession '{obs['topic']}' has no related curiosity questions in 7+ days",
                    "created_at": _now_iso()
                })
    except Exception:
        pass

    # Source 3: High-salience memory clusters with no questions asked
    try:
        from brain.three_tier_memory import get_episodic_entries

        entries = get_episodic_entries(days=14, limit=50)
        high_salience = [e for e in entries if e.get("salience", 0) >= 0.7]

        # Check which have associated curiosity questions
        all_questions = _load_questions()
        questioned_ids = {q.get("source", "").split(":")[-1] for q in all_questions
                         if q.get("source", "").startswith("memory_cluster")}

        for entry in high_salience[:5]:
            entry_id = entry.get("id", "")
            if entry_id not in questioned_ids:
                signals.append({
                    "id": str(uuid.uuid4()),
                    "type": "high_salience_unquestioned",
                    "entry_id": entry_id,
                    "content_preview": entry.get("content", "")[:80],
                    "salience": entry.get("salience", 0),
                    "priority": 0.35 + (entry.get("salience", 0.5) * 0.3),
                    "discovery": f"High-salience memory ({entry.get('salience', 0)}) has no associated curiosity questions",
                    "created_at": _now_iso()
                })
    except Exception:
        pass

    # Deduplicate by checking if we already have a similar signal
    existing = _load_absence_signals()
    existing_signals = {(s.get("type"), s.get("node_id"), s.get("obsession_id"))
                        for s in existing if s.get("type") in ("isolated_node", "obsession_without_questions")}

    new_signals = []
    for sig in signals:
        key = (sig.get("type"), sig.get("node_id"), sig.get("obsession_id"))
        if key not in existing_signals:
            new_signals.append(sig)

    # Merge and save
    all_signals = existing + new_signals
    all_signals.sort(key=lambda x: x.get("priority", 0), reverse=True)
    all_signals = all_signals[:50]  # keep top 50
    _save_absence_signals(all_signals)

    return new_signals


def generate_goals_from_absence(absence_signals: list = None) -> list:
    """
    For each high-priority absence: generate a self-directed goal.
    Goal structure: content, origin_absence_id, priority, status: "active"
    Goals are Nova's — system generates candidates, Nova implicitly acts on them.

    Returns list of generated goals.
    """
    absence_signals = absence_signals or _load_absence_signals()
    high_priority = [s for s in absence_signals if s.get("priority", 0) >= 0.5]

    goals = []
    for signal in high_priority[:10]:  # top 10
        goal = {
            "id": str(uuid.uuid4()),
            "content": _generate_goal_content(signal),
            "origin_absence_id": signal["id"],
            "origin_type": signal.get("type"),
            "priority": signal.get("priority", 0.5),
            "status": "active",
            "created_at": _now_iso()
        }
        goals.append(goal)

    # Save goals to a goals file (not overwriting existing)
    goals_file = NOVA_HOME / "initiative_goals.json"
    existing_goals = []
    if goals_file.exists():
        try:
            existing_goals = json.loads(goals_file.read_text())
        except Exception:
            existing_goals = []

    # Merge, deduplicate by origin_absence_id
    existing_ids = {g["origin_absence_id"] for g in existing_goals}
    for goal in goals:
        if goal["origin_absence_id"] not in existing_ids:
            existing_goals.append(goal)

    existing_goals.sort(key=lambda x: x.get("priority", 0), reverse=True)
    existing_goals = existing_goals[:30]  # keep top 30
    goals_file.write_text(json.dumps(existing_goals, indent=2))

    return goals


def _generate_goal_content(signal: dict) -> str:
    """Generate a goal description from an absence signal."""
    signal_type = signal.get("type")
    topic = signal.get("topic", signal.get("label", ""))

    if signal_type == "isolated_node":
        return f"Explore why '{topic}' exists in my knowledge graph without connections — what is it related to?"
    elif signal_type == "obsession_without_questions":
        return f"Generate curiosity questions about '{topic}' — what don't I know about this yet?"
    elif signal_type == "high_salience_unquestioned":
        preview = signal.get("content_preview", "")[:50]
        return f"Ask questions about: {preview}... — why does this matter and what follows from it?"
    else:
        return f"Investigate absence: {signal.get('discovery', '')}"


def get_active_initiative_goals(limit: int = 10) -> list:
    """Get current active initiative goals."""
    goals_file = NOVA_HOME / "initiative_goals.json"
    if not goals_file.exists():
        return []
    try:
        goals = json.loads(goals_file.read_text())
        active = [g for g in goals if g.get("status") == "active"]
        return sorted(active, key=lambda x: x.get("priority", 0), reverse=True)[:limit]
    except Exception:
        return []


def complete_goal(goal_id: str) -> bool:
    """Mark a goal as completed."""
    goals_file = NOVA_HOME / "initiative_goals.json"
    if not goals_file.exists():
        return False
    try:
        goals = json.loads(goals_file.read_text())
        for goal in goals:
            if goal["id"] == goal_id:
                goal["status"] = "completed"
                goal["completed_at"] = _now_iso()
                goals_file.write_text(json.dumps(goals, indent=2))
                return True
        return False
    except Exception:
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: initiative_engine.py <detect|generate_goals|active|complete> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "detect":
        signals = detect_absence()
        print(f"Detected {len(signals)} new absence signals:")
        for s in signals:
            print(f"  [priority: {s['priority']:.2f}] {s['type']}: {s['discovery'][:80]}")

    elif cmd == "generate_goals":
        signals = _load_absence_signals()
        goals = generate_goals_from_absence(signals)
        print(f"Generated {len(goals)} goals from absence signals:")
        for g in goals:
            print(f"  [priority: {g['priority']:.2f}] {g['content'][:80]}")

    elif cmd == "active":
        goals = get_active_initiative_goals()
        print(f"Active initiative goals ({len(goals)}):")
        for g in goals:
            print(f"  [priority: {g['priority']:.2f}] {g['content'][:80]}")

    elif cmd == "complete":
        if len(sys.argv) < 3:
            print("Usage: initiative_engine.py complete <goal_id>")
            sys.exit(1)
        success = complete_goal(sys.argv[2])
        print(f"Goal {'completed' if success else 'not found'}")

    else:
        print(f"Unknown command: {cmd}")
