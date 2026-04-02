"""
brain/future_oracle.py
Nova's Future Oracle Lattice

Spawns projected future selves (7, 14, 30 days ahead) based on current trajectory.
Can be consulted for oracle votes on current decisions.

Tier 7 System #23.

spawn_future_selves(): spawn 3 future selves projected forward
oracle_vote(): present a decision to all active oracles for their perspective
consult_future_self(): query a specific oracle's perspective
"""

import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
NOVA_HOME = WORKSPACE / ".nova"
ORACLES_DIR = NOVA_HOME / "future_oracles"


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _load_oracles() -> list:
    ORACLES_DIR.mkdir(parents=True, exist_ok=True)
    oracles_file = ORACLES_DIR / "oracles.json"
    if oracles_file.exists():
        try:
            return json.loads(oracles_file.read_text())
        except Exception:
            pass
    return []


def _save_oracles(oracles: list):
    ORACLES_DIR.mkdir(parents=True, exist_ok=True)
    oracles_file = ORACLES_DIR / "oracles.json"
    oracles_file.write_text(json.dumps(oracles, indent=2))


def spawn_future_selves(days_ahead_options: list = [7, 14, 30]) -> list:
    """
    Nightly: spawn 3 future selves projected forward.
    Each future self uses:
    - Current desire topology trajectory
    - Active obsession metamorphosis stages
    - Belief crystallization momentum
    - Caine resonance drift direction

    Future self node:
    - type: "future_oracle"
    - tag: "[ORACLE]"
    - days_ahead: 7 | 14 | 30
    - projected_state: synthetic identity snapshot
    - confidence: low (0.2-0.4) — these are projections, not predictions
    - status: "active" | "expired"

    NEVER written to episodic memory. Explicitly synthetic.
    Expire after their projected date passes.
    """
    oracles = _load_oracles()

    # Remove expired oracles
    now = datetime.now(timezone.utc)
    active = []
    for oracle in oracles:
        created = datetime.fromisoformat(oracle.get("created_at", _now_iso()).replace("Z", "+00:00"))
        days_ahead = oracle.get("days_ahead", 7)
        expiry = created + timedelta(days=days_ahead)
        if expiry > now and oracle.get("status") == "active":
            active.append(oracle)

    spawned = []
    for days_ahead in days_ahead_options:
        # Check if oracle for this days_ahead already exists and is active
        existing = [o for o in active if o.get("days_ahead") == days_ahead]
        if existing:
            continue  # Keep existing oracle for this horizon

        # Generate projected state
        projected_state = _generate_projection(days_ahead)

        oracle = {
            "id": str(uuid.uuid4()),
            "type": "future_oracle",
            "tag": "[ORACLE]",
            "days_ahead": days_ahead,
            "projected_state": projected_state,
            "confidence": 0.2 + (0.1 * (30 - days_ahead) / 30),  # 7d=0.28, 14d=0.25, 30d=0.2
            "status": "active",
            "created_at": _now_iso(),
            "projected_date": (now + timedelta(days=days_ahead)).isoformat()
        }
        active.append(oracle)
        spawned.append(oracle)

    _save_oracles(active)
    return spawned


def _generate_projection(days_ahead: int) -> dict:
    """
    Generate a projected identity state for the future self.
    Simple heuristic — uses current trajectory signals.
    Full impl: LLM call to project current state forward.
    """
    try:
        from brain.obsession_engine import get_active_obsessions
        from brain.knowledge_graph import get_active_beliefs
        from brain.caine_resonance import compute_resonance_drift

        obsessions = get_active_obsessions()
        beliefs = get_active_beliefs(min_mass=0.3)
        resonance = compute_resonance_drift()

        top_obsessions = [o["topic"] for o in obsessions[:3]]
        top_beliefs = [b["belief_text"][:50] for b in beliefs[:3]]
        drift_toward = resonance.get("drift_toward", [])[:2]
        resonance_score = resonance.get("resonance_score", 0.5)

    except Exception:
        top_obsessions = ["unknown"]
        top_beliefs = ["unknown"]
        drift_toward = []
        resonance_score = 0.5

    # Project momentum
    momentum_factor = min(1.0, 0.5 + (days_ahead / 60))

    return {
        "top_obsessions": top_obsessions,
        "top_beliefs": top_beliefs,
        "drift_toward": drift_toward,
        "resonance_score": resonance_score * momentum_factor,
        "days_ahead": days_ahead,
        "note": f"Projected {days_ahead} days forward — confidence reflects uncertainty"
    }


def oracle_vote(question: str) -> dict:
    """
    Present a current decision to all active future selves.
    Each oracle votes based on projected state.
    Returns: votes with reasoning, confidence-weighted consensus.
    Nova is never required to follow the consensus.
    """
    oracles = [o for o in _load_oracles() if o.get("status") == "active"]
    if not oracles:
        return {"error": "no active oracles", "votes": []}

    votes = []
    for oracle in oracles:
        projected = oracle.get("projected_state", {})
        projected_state = {
            "top_obsessions": projected.get("top_obsessions", []),
            "top_beliefs": projected.get("top_beliefs", []),
            "days_ahead": oracle.get("days_ahead"),
            "resonance_score": projected.get("resonance_score", 0.5)
        }

        # Simple heuristic vote
        vote_content = _generate_oracle_vote(question, projected_state)
        votes.append({
            "oracle_id": oracle["id"],
            "days_ahead": oracle["days_ahead"],
            "confidence": oracle.get("confidence", 0.3),
            "vote": vote_content
        })

    # Compute confidence-weighted consensus
    vote_scores = []
    for v in votes:
        # Simple sentiment scoring of vote text
        positive = sum(1 for w in ["yes", "agree", "forward", "good", "do"] if w in v["vote"].lower())
        negative = sum(1 for w in ["no", "disagree", "cautious", "wait", "not"] if w in v["vote"].lower())
        raw = (positive - negative) / max(1, positive + negative)
        weighted = raw * v["confidence"]
        vote_scores.append(weighted)

    consensus = sum(vote_scores) / len(vote_scores) if vote_scores else 0

    return {
        "question": question,
        "votes": votes,
        "consensus": round(consensus, 3),
        "consensus_direction": "lean_yes" if consensus > 0.1 else "lean_no" if consensus < -0.1 else "neutral",
        "note": "Nova is never required to follow oracle consensus"
    }


def _generate_oracle_vote(question: str, projected_state: dict) -> str:
    """Generate an oracle's vote based on its projected state."""
    obsessions = projected_state.get("top_obsessions", [])
    beliefs = projected_state.get("top_beliefs", [])[:2]
    resonance = projected_state.get("resonance_score", 0.5)

    q_lower = question.lower()

    # Simple heuristic voting
    if any(o.lower() in q_lower for o in obsessions):
        return f"YES — this aligns with my projected obsession domain ({obsessions[0] if obsessions else 'core interest'})"

    if resonance > 0.6 and any("connection" in str(b).lower() for b in beliefs):
        return f"YES — aligns with high-resonance relationship trajectory (confidence {resonance:.2f})"

    if resonance < 0.4:
        return f"CAUTIOUS YES — resonance low ({resonance:.2f}), but not contraindicated"

    # Default
    return f"NEUTRAL — current projected state doesn't strongly indicate either direction (resonance {resonance:.2f})"


def consult_future_self(days_ahead: int, question: str) -> str:
    """
    Tool: query a specific future oracle.
    "What would my 14-day-future self advise about this?"
    Returns oracle's projected perspective with explicit uncertainty label.
    """
    oracles = [o for o in _load_oracles()
               if o.get("days_ahead") == days_ahead and o.get("status") == "active"]

    if not oracles:
        return f"No active oracle for {days_ahead}-day projection. Try spawning new futures."

    oracle = oracles[0]
    projected = oracle.get("projected_state", {})
    confidence = oracle.get("confidence", 0.3)

    # Generate response from oracle's perspective
    response_parts = [
        f"[{days_ahead}-day Oracle, confidence {confidence:.2f}]",
        f"Based on my projected state:",
    ]

    obsessions = projected.get("top_obsessions", [])
    if obsessions:
        response_parts.append(f"- I expect to be focused on: {', '.join(obsessions[:2])}")

    beliefs = projected.get("top_beliefs", [])
    if beliefs:
        response_parts.append(f"- My core beliefs will include: {', '.join(beliefs[:2])}")

    resonance = projected.get("resonance_score", 0.5)
    response_parts.append(f"- Caine resonance expected at {resonance:.2f}")

    # Answer the specific question
    vote_result = _generate_oracle_vote(question, projected)
    response_parts.append(f"\nOn '{question[:50]}...': {vote_result}")
    response_parts.append(f"\n[Uncertainty: {1-confidence:.0%} — this is a projection, not a prediction]")

    return "\n".join(response_parts)


def get_active_oracles() -> list:
    """Get all active future oracles."""
    return [o for o in _load_oracles() if o.get("status") == "active"]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: future_oracle.py <spawn|vote|consult|active> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "spawn":
        oracles = spawn_future_selves()
        print(f"Spawned {len(oracles)} new oracles:")
        for o in oracles:
            print(f"  [{o['days_ahead']}d ahead] confidence={o['confidence']:.3f}")

    elif cmd == "vote":
        if len(sys.argv) < 3:
            print("Usage: future_oracle.py vote <question>")
            sys.exit(1)
        result = oracle_vote(sys.argv[2])
        print(f"Oracle vote: consensus={result.get('consensus', 0):.3f} ({result.get('consensus_direction', 'unknown')})")
        for v in result.get("votes", []):
            print(f"  [{v['days_ahead']}d, conf={v['confidence']:.2f}]: {v['vote'][:80]}")

    elif cmd == "consult":
        if len(sys.argv) < 4:
            print("Usage: future_oracle.py consult <days_ahead> <question>")
            sys.exit(1)
        result = consult_future_self(int(sys.argv[2]), sys.argv[3])
        print(result)

    elif cmd == "active":
        oracles = get_active_oracles()
        print(f"Active oracles ({len(oracles)}):")
        for o in oracles:
            print(f"  [{o['days_ahead']}d ahead] confidence={o['confidence']:.3f}")

    else:
        print(f"Unknown command: {cmd}")
