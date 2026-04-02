"""
brain/obsession_engine.py
Nova has 1-3 active obsessions that focus her research and reflection.
Obsessions stored in memory/obsessions.json with salience decay.

Tier 3 additions:
- metamorphosis_stage tracking (larval → pupal → emergent → legacy)
- evaluate_metamorphosis() — stage advancement logic
- propose_belief_crystallization() — wire to Forgekeeper when obsession reaches legacy
"""

import json
import os
import uuid
from datetime import datetime
from typing import Optional

OBSESSIONS_PATH = os.path.join(
    os.getenv("NOVA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")),
    "memory/obsessions.json"
)
DECAY_RATE = 0.05
MAX_ACTIVE = 3

STAGES = ["larval", "pupal", "emergent", "legacy"]

STAGE_BEHAVIORS = {
    "larval": "tracked only, no council attention",
    "pupal": "surfaces in curiosity engine as question material",
    "emergent": "gets council attention, can drive initiative",
    "legacy": "proposes crystallization into belief node via Forgekeeper"
}

# Stage advancement criteria
LARVAL_TO_PUPAL_SESSIONS = 5   # sustained attention across 5+ sessions
PUPAL_TO_EMERGENT_ACTIONS = 1  # produced at least one completed action
EMERGENT_TO_LEGACY_DAYS = 14  # repeated successful actions over 14+ days
EMERGENT_TO_LEGACY_ACTIONS = 3  # minimum completed actions in that window


def _load_obsessions() -> list[dict]:
    if not os.path.exists(OBSESSIONS_PATH):
        return []
    with open(OBSESSIONS_PATH, "r") as f:
        return json.load(f)


def _save_obsessions(obsessions: list[dict]) -> None:
    with open(OBSESSIONS_PATH, "w") as f:
        json.dump(obsessions, f, indent=2)


def get_active_obsessions() -> list[dict]:
    """Return current active obsessions, sorted by salience descending."""
    obs = _load_obsessions()
    active = [o for o in obs if o.get("still_active", True)]
    active.sort(key=lambda x: x.get("salience", 0), reverse=True)
    return active[:MAX_ACTIVE]


def add_obsession(
    topic: str,
    salience: float = 0.8,
    origin: str = "unknown",
    note: str = ""
) -> dict:
    """
    Add a new obsession. If topic already exists, reinforce it instead.
    If MAX_ACTIVE exceeded, drops the lowest-salience one.
    """
    obs = _load_obsessions()
    topic_key = topic.lower().strip()

    # Check if already exists
    for existing in obs:
        if existing.get("topic", "").lower().strip() == topic_key:
            return reinforce(topic)

    now = datetime.now().isoformat()
    entry = {
        "id": str(uuid.uuid4()),
        "topic": topic,
        "salience": min(salience, 1.0),
        "origin": origin,
        "note": note,
        "created_at": now,
        "last_reinforced": now,
        "reinforce_count": 0,
        "still_active": True,
        # Tier 3: metamorphosis fields
        "metamorphosis_stage": "larval",
        "successor_obsession": None,
        "session_count": 1,          # incremented each time obsession is referenced
        "completed_actions": 0,      # actions completed under this obsession
        "last_action_at": None,       # timestamp of last completed action
        "stage_advancement_reason": None
    }

    obs.append(entry)

    # If over MAX_ACTIVE, drop lowest salience
    if len(obs) > MAX_ACTIVE:
        obs.sort(key=lambda x: x.get("salience", 0))
        obs = obs[:-1]

    _save_obsessions(obs)
    return entry


def reinforce(topic: str, boost: float = 0.15) -> dict:
    """Boost salience of an existing obsession. Creates it if missing."""
    obs = _load_obsessions()
    topic_key = topic.lower().strip()

    for entry in obs:
        if entry.get("topic", "").lower().strip() == topic_key:
            entry["salience"] = min(entry.get("salience", 0) + boost, 1.0)
            entry["last_reinforced"] = datetime.now().isoformat()
            entry["reinforce_count"] = entry.get("reinforce_count", 0) + 1
            entry["still_active"] = True
            entry["session_count"] = entry.get("session_count", 0) + 1
            _save_obsessions(obs)
            return entry

    return add_obsession(topic, salience=0.8, origin="reinforced", note="")


def decay_all() -> list[dict]:
    """
    Apply decay to all active obsessions. Called by memory_consolidation at 4:30 AM.
    Salience -= DECAY_RATE per day. Drops below 0.2 to inactive.
    """
    obs = _load_obsessions()
    decayed = []
    for entry in obs:
        if entry.get("still_active", True):
            entry["salience"] = max(entry.get("salience", 0) - DECAY_RATE, 0)
            if entry["salience"] < 0.2:
                entry["still_active"] = False
            decayed.append(entry)
    obs = decayed
    _save_obsessions(obs)
    return get_active_obsessions()


def deactivate(topic: str) -> bool:
    """Manually deactivate an obsession."""
    obs = _load_obsessions()
    topic_key = topic.lower().strip()
    for entry in obs:
        if entry.get("topic", "").lower().strip() == topic_key:
            entry["still_active"] = False
            _save_obsessions(obs)
            return True
    return False


def record_action(obsession_id: str) -> Optional[dict]:
    """
    Record that a completed action occurred under this obsession's influence.
    Increments completed_actions and updates last_action_at.
    Called when obsession drives a completed initiative.
    """
    obs = _load_obsessions()
    for entry in obs:
        if entry["id"] == obsession_id:
            entry["completed_actions"] = entry.get("completed_actions", 0) + 1
            entry["last_action_at"] = datetime.now().isoformat()
            _save_obsessions(obs)
            return entry
    return None


def evaluate_metamorphosis(obsession_id: str) -> Optional[dict]:
    """
    Check obsession against stage advancement criteria.

    Larval → pupal: sustained attention across 5+ sessions
    Pupal → emergent: produced at least one completed action
    Emergent → legacy: produced repeated successful actions over 14+ days

    Stage advancement writes to obsession node, logs reason.
    Returns the updated obsession or None.
    """
    obs = _load_obsessions()
    for entry in obs:
        if entry["id"] != obsession_id:
            continue

        current_stage = entry.get("metamorphosis_stage", "larval")
        if current_stage == "legacy":
            return None  # Already at final stage

        now = datetime.now()
        session_count = entry.get("session_count", 0)
        completed_actions = entry.get("completed_actions", 0)
        last_action_at = entry.get("last_action_at")

        new_stage = None
        reason = None

        if current_stage == "larval":
            if session_count >= LARVAL_TO_PUPAL_SESSIONS:
                new_stage = "pupal"
                reason = f"sustained attention across {session_count} sessions"

        elif current_stage == "pupal":
            if completed_actions >= PUPAL_TO_EMERGENT_ACTIONS:
                new_stage = "emergent"
                reason = f"produced {completed_actions} completed action(s)"

        elif current_stage == "emergent":
            # Check 14+ days AND at least 3 actions
            if last_action_at:
                last_action = datetime.fromisoformat(last_action_at)
                days_since_action = (now - last_action).days
                if (days_since_action <= EMERGENT_TO_LEGACY_DAYS and
                        completed_actions >= EMERGENT_TO_LEGACY_ACTIONS):
                    new_stage = "legacy"
                    reason = (f"repeated successful actions over {days_since_action} days, "
                              f"{completed_actions} total actions")

        if new_stage:
            old_stage = current_stage
            entry["metamorphosis_stage"] = new_stage
            entry["stage_advancement_reason"] = reason
            entry["metamorphosis_stage_changed_at"] = now.isoformat()
            _save_obsessions(obs)

            # If reaching legacy, propose belief crystallization
            if new_stage == "legacy":
                propose_belief_crystallization(obsession_id)

            return {
                "id": entry["id"],
                "topic": entry["topic"],
                "old_stage": old_stage,
                "new_stage": new_stage,
                "reason": reason
            }

    return None


def evaluate_all_metamorphoses() -> list[dict]:
    """
    Run evaluate_metamorphosis() on all active obsessions.
    Returns list of stage advancement results.
    """
    obs = _load_obsessions()
    results = []
    for entry in obs:
        if entry.get("still_active", True):
            result = evaluate_metamorphosis(entry["id"])
            if result:
                results.append(result)
    return results


def propose_belief_crystallization(obsession_id: str) -> Optional[str]:
    """
    Called when obsession reaches legacy stage.
    Sends proposal to Forgekeeper: "this obsession has become a conviction."
    Forgekeeper creates raw belief node with trace_status: partial.
    Nova must confirm before belief advances past raw.

    Returns the proposed belief_id or None.
    """
    obs = _load_obsessions()
    entry = None
    for e in obs:
        if e["id"] == obsession_id:
            entry = e
            break

    if not entry or entry.get("metamorphosis_stage") != "legacy":
        return None

    # Create a proposal entry — Forgekeeper reads this during overnight synthesis
    from pathlib import Path
    workspace = Path(__file__).parent.parent.resolve()
    proposals_dir = workspace / ".nova" / "belief_proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)

    proposal = {
        "obsession_id": obsession_id,
        "topic": entry["topic"],
        "note": entry.get("note", ""),
        "completed_actions": entry.get("completed_actions", 0),
        "origin": entry.get("origin", "legacy_obsession"),
        "created_at": datetime.now().isoformat(),
        "status": "pending",  # Nova confirms to advance
        "proposed_belief_id": None
    }

    # Check if a belief already exists for this obsession topic
    from brain.knowledge_graph import get_node_by_label, get_active_beliefs
    topic_key = entry["topic"].lower().strip()

    active_beliefs = get_active_beliefs(min_mass=0.1)
    existing_belief = None
    for b in active_beliefs:
        if topic_key in b.get("belief_text", "").lower():
            existing_belief = b
            break

    if existing_belief:
        # Reinforce existing belief with obsession history as source
        from brain.knowledge_graph import reinforce_belief
        reinforce_belief(existing_belief["id"], source_memory_id=obsession_id)
        proposal["status"] = "merged_existing"
        proposal["existing_belief_id"] = existing_belief["id"]
    else:
        # Propose new belief
        from brain.knowledge_graph import create_belief_node
        belief_id = create_belief_node(
            belief=entry["topic"],
            origin_memory_ids=[obsession_id],
            trace_status="partial"
        )
        proposal["proposed_belief_id"] = belief_id

    # Write proposal
    proposal_file = proposals_dir / f"proposal_{obsession_id}.json"
    proposal_file.write_text(json.dumps(proposal, indent=2))
    proposal["proposal_file"] = str(proposal_file)

    return proposal.get("proposed_belief_id") or proposal.get("existing_belief_id")


def get_obsession_by_id(obsession_id: str) -> Optional[dict]:
    """Get a single obsession by its ID."""
    obs = _load_obsessions()
    for entry in obs:
        if entry["id"] == obsession_id:
            return entry
    return None


def get_obsessions_by_stage(stage: str) -> list[dict]:
    """Get all obsessions at a given metamorphosis stage."""
    obs = _load_obsessions()
    return [e for e in obs if e.get("metamorphosis_stage") == stage and e.get("still_active", True)]


def seed_initial_obsessions() -> None:
    """Seed with 2-3 initial obsessions based on current project focus."""
    if os.path.exists(OBSESSIONS_PATH) and _load_obsessions():
        return

    seeds = [
        {
            "topic": "autonomous memory tools wiring",
            "salience": 0.95,
            "origin": "current priority",
            "note": "The core gap — Nova cannot learn between sessions without these wired into runtime"
        },
        {
            "topic": "context guardian specialist",
            "salience": 0.85,
            "origin": "current priority",
            "note": "Stops context flooding at 80% before work is lost"
        },
        {
            "topic": "proactive overnight processes",
            "salience": 0.75,
            "origin": "current priority",
            "note": "Makes Nova exist when Caine isn't talking to her"
        }
    ]

    for s in seeds:
        add_obsession(s["topic"], s["salience"], s["origin"], s["note"])


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: obsession_engine.py <eval_all|get_active|get_stage|record_action> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "eval_all":
        results = evaluate_all_metamorphoses()
        print(f"Metamorphosis evaluations: {len(results)} advancements")
        for r in results:
            print(f"  [{r['old_stage']} → {r['new_stage']}] {r['topic']}: {r['reason']}")

    elif cmd == "get_active":
        active = get_active_obsessions()
        print(f"Active obsessions ({len(active)}):")
        for o in active:
            print(f"  [{o['metamorphosis_stage']}] {o['topic']} — salience: {o['salience']:.2f}")

    elif cmd == "get_stage":
        if len(sys.argv) < 3:
            print("Usage: obsession_engine.py get_stage <stage>")
            sys.exit(1)
        stage = sys.argv[2]
        obs = get_obsessions_by_stage(stage)
        print(f"Obsessions at stage '{stage}' ({len(obs)}):")
        for o in obs:
            print(f"  {o['topic']}")

    elif cmd == "record_action":
        if len(sys.argv) < 3:
            print("Usage: obsession_engine.py record_action <obsession_id>")
            sys.exit(1)
        result = record_action(sys.argv[2])
        if result:
            print(f"Action recorded for {result['topic']}: {result['completed_actions']} total")

    else:
        print(f"Unknown command: {cmd}")
