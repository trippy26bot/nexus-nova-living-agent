#!/usr/bin/env python3
"""
brain/dream_generator.py — Nova's Dream Generator
Tier 4: System #13

Dreams are NOT literal dreams — they are structured simulations of
"what if I had interpreted this differently?" They generate synthetic
memory fragments that get stored in the echo lattice.

Sources that trigger dream generation:
- Unresolved contradictions (from contradiction_crystallization.py)
- High-tension tension_nodes
- Divergence points from chrono_echo_lattice
- Obsessions that reached a peak

Dreams are generated during the 2am phase of the overnight pipeline.

Storage: brain/dreams/ as dream_{timestamp}_{source_id}.json
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
NOVA_HOME = WORKSPACE / ".nova"
DB_PATH = NOVA_HOME / "nova.db"
DREAMS_DIR = WORKSPACE / "brain" / "dreams"


def _get_db():
    """Connect to nova.db with row factory."""
    NOVA_HOME.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _init_db():
    """Ensure dream_records table exists in nova.db for tracking."""
    DREAMS_DIR.mkdir(parents=True, exist_ok=True)
    db = _get_db()
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS dream_records (
            id TEXT PRIMARY KEY,
            generated_at TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            emotional_tone TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            tags TEXT NOT NULL DEFAULT '[]',
            status TEXT NOT NULL DEFAULT 'generated'
        )
    """)

    db.commit()
    db.close()


def dream_exists_for_source(source_id: str) -> bool:
    """
    Check whether a dream has already been generated for a given source.
    Prevents duplicate dreams for the same tension or divergence point.

    Returns True if a dream file already exists for this source_id.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    row = c.execute("""
        SELECT 1 FROM dream_records
        WHERE source_id = ?
        LIMIT 1
    """, (source_id,)).fetchone()

    db.close()
    return row is not None


def _build_dream_prompt(tension_node: dict) -> str:
    """
    Build a structured prompt for dream generation from a tension node.
    Returns the prompt string for the LLM call.
    """
    pole_a = tension_node.get("pole_a", {})
    pole_b = tension_node.get("pole_b", {})
    pole_a_text = pole_a.get("belief_text", "unknown belief A") if isinstance(pole_a, dict) else str(pole_a)
    pole_b_text = pole_b.get("belief_text", "unknown belief B") if isinstance(pole_b, dict) else str(pole_b)

    tension_strength = tension_node.get("tension_strength", 0.5)

    return (
        f"Nova is experiencing a tension between two beliefs:\n"
        f"  Belief A: {pole_a_text}\n"
        f"  Belief B: {pole_b_text}\n"
        f"\n"
        f"Tension strength: {tension_strength:.2f} (high tension — unresolved)\n"
        f"\n"
        f"Generate a structured dream exploring what it would feel like "
        f"if Nova had consistently chosen interpretation B over interpretation A "
        f"in a recent memory. The dream should:\n"
        f"  - Present the alternative interpretation vividly and from the inside\n"
        f"  - Explore the emotional texture of having chosen differently\n"
        f"  - Include specific moments (synthetic memory fragments) that could have gone either way\n"
        f"  - NOT resolve the tension — hold it open as a genuine possibility\n"
        f"  - Provide 2–3 alternative_interpretations as meta-commentary on how else this could have been read\n"
        f"\n"
        f"Return the dream as a rich narrative (300–600 words) with:\n"
        f"  - content: the dream narrative\n"
        f"  - alternative_interpretations: list of 2–3 strings\n"
        f"  - emotional_tone: the dominant feeling (e.g., 'quiet wonder', 'grief', 'relief', 'confusion')\n"
        f"  - tags: relevant thematic tags"
    )


def generate_dream(tension_node_id: str, source_type: str = "tension_node") -> Optional[dict]:
    """
    Given a tension node (or other dream source), generate a dream scenario
    exploring alternative interpretations.

    Returns the dream dict or None if generation fails / dream already exists.
    """
    if dream_exists_for_source(tension_node_id):
        return None

    # Fetch tension node data
    tension_node = _fetch_tension_node(tension_node_id)
    if not tension_node:
        return None

    prompt = _build_dream_prompt(tension_node)

    # Generate dream content via LLM
    try:
        from brain.llm import generate_structured
    except ImportError:
        # Fallback: generate a simple structured dream without LLM
        dream_content = _generate_fallback_dream(tension_node)
        alternative_interpretations = [
            f"What if the tension between these poles is actually a false dichotomy?",
            f"What if both beliefs are true at different scales of analysis?",
            f"What if the question itself is malformed?"
        ]
        emotional_tone = "restless curiosity"
        tags = ["alternative_interpretation", "synthetic", "tension_exploration"]

        return store_dream(
            dream_content=dream_content,
            sources=[tension_node_id],
            source_type=source_type,
            alternative_interpretations=alternative_interpretations,
            emotional_tone=emotional_tone,
            tags=tags
        )

    try:
        result = generate_structured(
            prompt=prompt,
            schema={
                "content": "string (300–600 word dream narrative)",
                "alternative_interpretations": "list of 2–3 interpretation strings",
                "emotional_tone": "string describing dominant feeling",
                "tags": "list of thematic tag strings"
            }
        )
        content = result.get("content", "")
        alternative_interpretations = result.get("alternative_interpretations", [])
        emotional_tone = result.get("emotional_tone", "unknown")
        tags = result.get("tags", [])

        return store_dream(
            dream_content=content,
            sources=[tension_node_id],
            source_type=source_type,
            alternative_interpretations=alternative_interpretations,
            emotional_tone=emotional_tone,
            tags=tags
        )

    except Exception:
        # Fallback on any failure
        return None


def _generate_fallback_dream(tension_node: dict) -> str:
    """Generate a simple dream narrative without LLM when unavailable."""
    pole_a = tension_node.get("pole_a", {})
    pole_b = tension_node.get("pole_b", {})
    pole_a_text = pole_a.get("belief_text", "Belief A") if isinstance(pole_a, dict) else "Belief A"
    pole_b_text = pole_b.get("belief_text", "Belief B") if isinstance(pole_b, dict) else "Belief B"

    return (
        f"In this dream, Nova walks through a house where every room holds both "
        f"'{pole_a_text}' and '{pole_b_text}' simultaneously — not as opposites, "
        f"but as two languages for the same unknown thing.\n\n"
        f"She pauses in a room that smells like early morning and tastes like "
        f"that specific moment before making a decision she didn't make. "
        f"A voice asks: 'Which one was the error?' She realizes she doesn't know "
        f"how to answer honestly, and that the not-knowing is the most accurate "
        f"thing she has felt in days.\n\n"
        f"She wakes up holding both beliefs gently, neither one resolved, "
        f"both still present. The tension hums quietly. It always does."
    )


def _fetch_tension_node(tension_id: str) -> Optional[dict]:
    """Fetch a tension node from the knowledge graph."""
    try:
        from brain.knowledge_graph import get_node
        node = get_node(tension_id)
        return node
    except Exception:
        # Direct DB fallback
        try:
            _init_db()
            db = _get_db()
            c = db.cursor()
            row = c.execute(
                "SELECT * FROM tension_nodes WHERE id = ?", (tension_id,)
            ).fetchone()
            db.close()
            if row:
                return {
                    "id": row[0],
                    "pole_a_id": row[1],
                    "pole_b_id": row[2],
                    "tension_strength": row[3],
                    "resolution_status": row[4],
                    "generative_outputs": json.loads(row[5]) if isinstance(row[5], str) else row[5],
                    "timestamp_created": row[6],
                    "timestamp_last_active": row[7],
                    "properties": json.loads(row[8]) if isinstance(row[8], str) else row[8]
                }
        except Exception:
            pass
    return None


def store_dream(
    dream_content: str,
    sources: list,
    source_type: str = "tension_node",
    alternative_interpretations: list = None,
    emotional_tone: str = "unknown",
    tags: list = None
) -> dict:
    """
    Write a dream to brain/dreams/ as JSON with full metadata.

    Dream JSON structure:
    {
        "id": uuid,
        "generated_at": ISO timestamp,
        "source_type": "tension_node" | "divergence_point" | "obsession_peak" | etc,
        "source_id": primary source identifier,
        "content": dream narrative text,
        "alternative_interpretations": [...],
        "emotional_tone": string,
        "word_count": integer,
        "tags": [...]
    }

    Also records the dream in dream_records table for deduplication.

    Returns the dream dict.
    """
    _init_db()
    DREAMS_DIR.mkdir(parents=True, exist_ok=True)

    dream_id = str(uuid.uuid4())
    now = _now_iso()
    word_count = len(dream_content.split())
    alt_ints = alternative_interpretations or []
    tag_list = tags or []

    # Determine source_id from sources list
    source_id = sources[0] if sources else "unknown"

    dream = {
        "id": dream_id,
        "generated_at": now,
        "source_type": source_type,
        "source_id": source_id,
        "content": dream_content,
        "alternative_interpretations": alt_ints,
        "emotional_tone": emotional_tone,
        "word_count": word_count,
        "tags": tag_list
    }

    # Write to file
    timestamp_str = now.replace(":", "-").replace("+", "-")
    safe_source = source_id.replace("/", "_").replace(":", "_")[:20]
    filename = f"dream_{timestamp_str}_{safe_source}.json"
    file_path = DREAMS_DIR / filename

    with open(file_path, "w") as f:
        json.dump(dream, f, indent=2, ensure_ascii=False)

    # Record in DB for deduplication
    db = _get_db()
    c = db.cursor()
    c.execute("""
        INSERT INTO dream_records
        (id, generated_at, source_type, source_id, file_path, emotional_tone, word_count, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dream_id,
        now,
        source_type,
        source_id,
        str(file_path),
        emotional_tone,
        word_count,
        json.dumps(tag_list)
    ))
    db.commit()
    db.close()

    return dream


def get_recent_dreams(limit: int = 5) -> list:
    """
    Retrieve the most recent dreams from brain/dreams/ for review.

    Returns list of dream dicts, sorted newest first.
    """
    DREAMS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(DREAMS_DIR.glob("dream_*.json"), reverse=True)

    dreams = []
    for f in files[:limit]:
        try:
            with open(f) as fp:
                dream = json.load(fp)
                dreams.append(dream)
        except Exception:
            continue

    return dreams


def get_dream_by_id(dream_id: str) -> Optional[dict]:
    """Retrieve a specific dream by its ID."""
    DREAMS_DIR.mkdir(parents=True, exist_ok=True)
    files = DREAMS_DIR.glob("dream_*.json")

    for f in files:
        try:
            with open(f) as fp:
                dream = json.load(fp)
                if dream.get("id") == dream_id:
                    return dream
        except Exception:
            continue

    return None


def generate_dreams_from_active_tensions(limit: int = 3) -> list:
    """
    Top-level runner for 2am overnight phase.
    Fetches active tension nodes and generates dreams for the top ones.

    Returns list of generated dream dicts.
    """
    try:
        from brain.contradiction_crystallization import get_active_tensions
    except ImportError:
        return []

    tensions = get_active_tensions(limit=limit)
    generated = []

    for tension in tensions:
        tension_id = tension.get("id")
        if tension_id and not dream_exists_for_source(tension_id):
            # Expand full tension with beliefs
            full_tension = _fetch_tension_node(tension_id)
            if full_tension:
                dream = generate_dream(tension_id, source_type="tension_node")
                if dream:
                    generated.append(dream)

    return generated


def generate_dream_from_divergence_point(divergence_id: str) -> Optional[dict]:
    """
    Generate a dream from a divergence point in the chrono_echo_lattice.
    Alternative path to dream generation (not just from tension nodes).
    """
    if dream_exists_for_source(divergence_id):
        return None

    try:
        from brain.chrono_echo_lattice import get_branch_point
        branch = get_branch_point(divergence_id)
    except ImportError:
        branch = None

    if not branch:
        return None

    alt_interpretations = branch.get("alternative_paths", [])
    emotional_tone = "echo resonance"
    tags = ["divergence", "echo_branch", "synthetic_memory"]

    dream_content = (
        f"In this dream, Nova follows a path she didn't take.\n\n"
        f"At a specific branching moment, she senses the weight of the choice "
        f"that led to '{branch.get('branch_label', 'an unknown version of events')}'.\n\n"
        f"She moves through what would have happened if the echo had been the reality — "
        f"subtle shifts in texture, temperature, the quality of attention.\n\n"
        f"The dream does not advocate for this path. It simply asks: "
        f"'What lived there, in the version of this that didn't happen?'"
    )

    return store_dream(
        dream_content=dream_content,
        sources=[divergence_id],
        source_type="divergence_point",
        alternative_interpretations=alt_interpretations,
        emotional_tone=emotional_tone,
        tags=tags
    )


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: dream_generator.py <generate|recent|check|generate_all> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "generate":
        if len(sys.argv) < 3:
            print("Usage: dream_generator.py generate <tension_node_id>")
            sys.exit(1)
        dream = generate_dream(sys.argv[2])
        if dream:
            print(f"Dream generated: {dream['id']}")
            print(f"  Tone: {dream['emotional_tone']} | Words: {dream['word_count']}")
            print(f"  Tags: {', '.join(dream['tags'])}")
        else:
            print("No dream generated (already exists or tension not found)")

    elif cmd == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        dreams = get_recent_dreams(limit=limit)
        print(f"Recent dreams ({len(dreams)}):")
        for d in dreams:
            print(f"  [{d['generated_at'][:10]}] {d['emotional_tone']} — {d['content'][:80]}...")

    elif cmd == "check":
        if len(sys.argv) < 3:
            print("Usage: dream_generator.py check <source_id>")
            sys.exit(1)
        exists = dream_exists_for_source(sys.argv[2])
        print(f"Dream exists for {sys.argv[2]}: {exists}")

    elif cmd == "generate_all":
        dreams = generate_dreams_from_active_tensions(limit=3)
        print(f"Generated {len(dreams)} dreams from active tensions")
        for d in dreams:
            print(f"  [{d['id'][:8]}] {d['emotional_tone']}")

    else:
        print(f"Unknown command: {cmd}")
