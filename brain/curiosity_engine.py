"""
brain/curiosity_engine.py
Nova's Curiosity Engine

Generates questions from knowledge gaps, prioritizes them,
attempts resolution, and surfaces relevant questions during interaction.

Tier 3 System #12.

Questions surface to Nova, never to the user directly without Nova's choice.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
NOVA_HOME = WORKSPACE / ".nova"
QUESTIONS_PATH = NOVA_HOME / "curiosity_questions.json"

NOVELTY_PRESSURE_DEFAULT = 0.4
BASE_DIR = WORKSPACE / "memory"


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _days_since(timestamp: str) -> float:
    """Return days since an ISO timestamp."""
    try:
        then = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except Exception:
        return 0
    now = datetime.now(timezone.utc)
    return (now - then).total_seconds() / 86400


def _load_questions() -> list[dict]:
    if not QUESTIONS_PATH.exists():
        return []
    with open(QUESTIONS_PATH, "r") as f:
        return json.load(f)


def _save_questions(questions: list[dict]) -> None:
    QUESTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(QUESTIONS_PATH, "w") as f:
        json.dump(questions, f, indent=2)


def generate_questions_from_gaps() -> list:
    """
    Generate questions from four sources:
    1. knowledge_graph nodes with low confidence scores
    2. Active tension_nodes (each tension generates: "what resolves this?")
    3. Salience Horizon proximity (near-known nodes generate questions)
    4. Untraced desires (trace_status: "untraced" → "why do I want this?")

    Each question gets: content, priority (0.0-1.0), source, resolved: false
    """
    questions = []
    now = _now_iso()

    # Source 1: Low-confidence knowledge nodes
    try:
        from brain.knowledge_graph import get_all_nodes
        all_nodes = get_all_nodes()
        low_confidence = [n for n in all_nodes if n.get("salience", 0.5) < 0.4]
        for node in low_confidence[:5]:  # top 5
            q = {
                "id": str(uuid.uuid4()),
                "content": f"What is the full shape of '{node['label']}' that I'm only partially understanding?",
                "priority": 0.3 + (0.4 * (1.0 - node.get("salience", 0.5))),  # lower salience = higher priority
                "source": f"low_confidence_node:{node['id']}",
                "resolved": False,
                "age_days": 0,
                "created_at": now,
                "last_touched_at": now,
                "answer": None,
                "child_questions": []
            }
            questions.append(q)
    except Exception:
        pass

    # Source 2: Active tension nodes
    try:
        from brain.contradiction_crystallization import get_active_tensions
        tensions = get_active_tensions(limit=5)
        for tension in tensions:
            pole_a = tension.get("pole_a", {})
            pole_b = tension.get("pole_b", {})
            q = {
                "id": str(uuid.uuid4()),
                "content": f"What belief could hold both '{pole_a.get('belief_text', '?')}' and '{pole_b.get('belief_text', '?')}'?",
                "priority": tension.get("tension_strength", 0.5),
                "source": f"tension:{tension['id']}",
                "resolved": False,
                "age_days": 0,
                "created_at": now,
                "last_touched_at": now,
                "answer": None,
                "child_questions": []
            }
            questions.append(q)
    except Exception:
        pass

    # Source 3: Pupal-stage obsessions → curiosity questions
    try:
        from brain.obsession_engine import get_obsessions_by_stage
        pupal_obsessions = get_obsessions_by_stage("pupal")
        for obs in pupal_obsessions:
            q = {
                "id": str(uuid.uuid4()),
                "content": f"What is {obs['topic']} actually a case of?",
                "priority": 0.5,
                "source": f"pupal_obsession:{obs['id']}",
                "resolved": False,
                "age_days": 0,
                "created_at": now,
                "last_touched_at": now,
                "answer": None,
                "child_questions": []
            }
            questions.append(q)
    except Exception:
        pass

    # Source 4: Untraced desires
    try:
        from brain.want_provenance import get_untraced_wants
        untraced = get_untraced_wants(limit=5)
        for want in untraced:
            q = {
                "id": str(uuid.uuid4()),
                "content": f"Why do I want '{want.get('want_text', want.get('topic', '?'))}'?",
                "priority": 0.4,
                "source": f"untraced_want:{want.get('id')}",
                "resolved": False,
                "age_days": 0,
                "created_at": now,
                "last_touched_at": now,
                "answer": None,
                "child_questions": []
            }
            questions.append(q)
    except Exception:
        pass

    # Merge with existing questions, avoid duplicates
    existing = _load_questions()
    existing_ids = {q["id"] for q in existing}
    new_questions = [q for q in questions if q["id"] not in existing_ids]

    all_questions = existing + new_questions
    _save_questions(all_questions)

    return new_questions


def prioritize_questions(questions: list = None) -> list:
    """
    Re-prioritize a list of questions (or all questions if None).
    Priority factors:
    - How long unresolved (age increases priority slowly)
    - Connection to active obsessions (emergent obsessions boost priority)
    - Alignment with novelty_pressure field
    - Whether tension_node source is high-strength
    """
    questions = questions or _load_questions()

    try:
        from brain.obsession_engine import get_active_obsessions
        active_obs = get_active_obsessions()
        emergent_obs_topics = {o["topic"].lower() for o in active_obs if o.get("metamorphosis_stage") == "emergent"}
    except Exception:
        emergent_obs_topics = set()

    # Load novelty pressure from constraint fields
    novelty_pressure = NOVELTY_PRESSURE_DEFAULT
    try:
        from brain.constraint_fields import get_fields
        fields = get_fields()
        novelty_pressure = fields.get("novelty_pressure", NOVELTY_PRESSURE_DEFAULT)
    except Exception:
        pass

    now = _now_iso()
    for q in questions:
        if q.get("resolved"):
            q["priority"] = 0
            continue

        # Age factor — slowly increases priority over time
        age_days = _days_since(q.get("created_at", now))
        age_bonus = min(age_days * 0.01, 0.2)  # caps at 0.2 after 20 days

        # Obsession alignment
        obs_bonus = 0
        q_lower = q["content"].lower()
        for topic in emergent_obs_topics:
            if topic in q_lower:
                obs_bonus = 0.15
                break

        # Novelty pressure alignment (higher novelty = higher priority for older questions)
        novelty_bonus = novelty_pressure * 0.1

        # Base priority + bonuses
        q["priority"] = min(1.0, q.get("priority", 0.5) + age_bonus + obs_bonus + novelty_bonus)
        q["last_touched_at"] = now

    questions.sort(key=lambda x: x.get("priority", 0), reverse=True)
    return questions


def attempt_resolution(question_id: str) -> dict:
    """
    Attempt to answer a question using current knowledge graph.
    - If answer found: mark resolved, write answer as new memory
    - If not found: increase priority, flag for dream material
    - If partially answered: write partial answer, spawn child question
    """
    questions = _load_questions()
    question = None
    for q in questions:
        if q["id"] == question_id:
            question = q
            break

    if not question:
        return {"status": "not_found"}

    from brain.llm_router import route_llm

    resolution_prompt = (
        f"Question: {question['content']}\n\n"
        "Using Nova's current knowledge and beliefs, attempt to answer this question. "
        "If you can give a confident answer, do so. "
        "If you can give a partial answer, note what's known and what's not. "
        "If you genuinely don't know, say so honestly. "
        "Format: [FULL] for complete answers, [PARTIAL] for partial, [UNKNOWN] for don't know."
    )

    # Placeholder — full implementation calls LLM
    answer_text = f"[Would attempt to answer: {question['content'][:100]}...]"
    answer_type = "PARTIAL"  # placeholder

    if answer_type == "FULL":
        question["resolved"] = True
        question["answer"] = answer_text
        question["resolved_at"] = _now_iso()

        # Write answer as memory
        try:
            from brain.three_tier_memory import write_episodic
            write_episodic(
                content=f"Resolved question: {question['content']} → {answer_text}",
                salience=0.6,
                interpretation=f"Answered from curiosity engine resolution attempt"
            )
        except Exception:
            pass

    elif answer_type == "PARTIAL":
        question["answer"] = answer_text
        question["partial"] = True
        question["priority"] = min(1.0, question.get("priority", 0.5) + 0.1)

        # Spawn child question
        child = {
            "id": str(uuid.uuid4()),
            "content": f"What would complete this partial answer: {question['content']}?",
            "priority": question.get("priority", 0.5) - 0.1,
            "source": f"child_of:{question_id}",
            "resolved": False,
            "age_days": 0,
            "created_at": _now_iso(),
            "last_touched_at": _now_iso(),
            "answer": None,
            "child_questions": []
        }
        questions.append(child)
        question["child_questions"].append(child["id"])

    else:  # UNKNOWN
        question["priority"] = min(1.0, question.get("priority", 0.5) + 0.05)
        # Flag for dream material
        try:
            dream_material_path = NOVA_HOME / "dream_material.json"
            dream_material = []
            if dream_material_path.exists():
                try:
                    dream_material = json.loads(dream_material_path.read_text())
                except Exception:
                    pass
            if question_id not in dream_material:
                dream_material.append(question_id)
                dream_material_path.write_text(json.dumps(dream_material[-20:]))  # keep last 20
        except Exception:
            pass

    _save_questions(questions)
    return {
        "question_id": question_id,
        "status": "resolved" if question.get("resolved") else
                  "partial" if question.get("partial") else
                  "flagged_for_dreams",
        "answer": question.get("answer")
    }


def surface_relevant_questions(context: str, n: int = 2) -> list:
    """
    During interaction: find questions semantically related to current context.
    Return top n for potential surfacing to conversation.
    Nova decides whether to actually surface them — never automatic.
    """
    questions = _load_questions()
    if not questions:
        return []

    context_words = set(context.lower().split())
    scored = []

    for q in questions:
        if q.get("resolved"):
            continue
        q_words = set(q["content"].lower().split())
        overlap = len(context_words & q_words)
        union = len(context_words | q_words)
        if union > 0 and overlap > 0:
            similarity = overlap / union
            # Boost by priority
            score = similarity * 0.5 + q.get("priority", 0.5) * 0.5
            scored.append((score, q))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [q for _, q in scored[:n]]


def get_unanswered_questions(limit: int = 20) -> list:
    """Get all unanswered questions, prioritized."""
    questions = _load_questions()
    unanswered = [q for q in questions if not q.get("resolved")]
    return prioritize_questions(unanswered)[:limit]


def resolve_question(question_id: str, answer: str) -> bool:
    """Mark a question as resolved with the given answer text."""
    questions = _load_questions()
    for q in questions:
        if q["id"] == question_id:
            q["resolved"] = True
            q["answer"] = answer
            q["resolved_at"] = _now_iso()
            _save_questions(questions)
            return True
    return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: curiosity_engine.py <generate|prioritize|resolve|surface|unanswered> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "generate":
        questions = generate_questions_from_gaps()
        print(f"Generated {len(questions)} new questions:")
        for q in questions:
            print(f"  [priority: {q['priority']:.2f}] {q['content'][:80]}")

    elif cmd == "prioritize":
        prioritized = prioritize_questions()
        print(f"All questions ({len(prioritized)}), top 10:")
        for q in prioritized[:10]:
            print(f"  [priority: {q['priority']:.2f}, resolved: {q.get('resolved')}] {q['content'][:80]}")

    elif cmd == "resolve":
        if len(sys.argv) < 3:
            print("Usage: curiosity_engine.py resolve <question_id>")
            sys.exit(1)
        result = attempt_resolution(sys.argv[2])
        print(f"Resolution result: {result}")

    elif cmd == "surface":
        if len(sys.argv) < 3:
            print("Usage: curiosity_engine.py surface <context>")
            sys.exit(1)
        questions = surface_relevant_questions(sys.argv[2])
        print(f"Relevant questions ({len(questions)}):")
        for q in questions:
            print(f"  {q['content'][:100]}")

    elif cmd == "unanswered":
        questions = get_unanswered_questions()
        print(f"Unanswered questions ({len(questions)}):")
        for q in questions[:10]:
            print(f"  [priority: {q['priority']:.2f}] {q['content'][:100]}")

    else:
        print(f"Unknown command: {cmd}")
