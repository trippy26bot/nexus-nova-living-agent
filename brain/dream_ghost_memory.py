"""
brain/dream_ghost_memory.py
Dream-Memory Contamination System

After dream generation:
- extract_dream_salience(): score emotional intensity
- create_ghost_memories(): generate [DREAM_ECHO] nodes if salience > 0.7
- decay_ghost_memories(): nightly cleanup of expired ghosts

Ghost memories are NOT retrievable as facts.
They influence retrieval weights of semantically related real memories.
Effect decays over ~72 hours unless reinforced by related real event.

Tier 4 System #15 — Dream-Memory Contamination.
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
GHOST_INDEX_PATH = NOVA_HOME / "ghost_memory_index.json"


def _get_db():
    """Connect to nova.db with row factory."""
    NOVA_HOME.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _init_db():
    """Ensure ghost_memories table exists."""
    db = _get_db()
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS ghost_memories (
            id TEXT PRIMARY KEY,
            semantic_cluster TEXT NOT NULL,
            tag TEXT NOT NULL DEFAULT '[DREAM_ECHO]',
            influence_weight REAL NOT NULL DEFAULT 0.5,
            decay_rate REAL NOT NULL DEFAULT 0.15,
            timestamp_created TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            dream_content_hash TEXT,
            properties TEXT NOT NULL DEFAULT '{}'
        )
    """)

    db.commit()
    db.close()


def extract_dream_salience(dream_output: str) -> float:
    """
    After dream generation, score the dream's emotional intensity.
    High salience (> 0.7): dream generates ghost_memory nodes.
    Low salience: dream is logged but produces no contamination.

    Simple heuristic implementation.
    Full impl: LLM call to score emotional intensity of dream text.
    """
    if not dream_output:
        return 0.0

    # Heuristic scoring based on content characteristics
    # Full impl would use LLM to score emotional intensity
    content_lower = dream_output.lower()

    # Indicators of high emotional intensity
    intensity_signals = [
        ("fear", 0.15), ("terror", 0.2), ("joy", 0.1), ("grief", 0.15),
        ("rage", 0.2), ("ecstasy", 0.15), ("loss", 0.12), ("death", 0.15),
        ("love", 0.1), ("longing", 0.12), ("chase", 0.1), ("falling", 0.08),
        ("water", 0.05), ("fire", 0.08), ("dark", 0.06), ("light", 0.05),
        ("nova", 0.08), ("caine", 0.08), ("alone", 0.1), ("together", 0.08)
    ]

    score = 0.3  # baseline

    for signal, weight in intensity_signals:
        if signal in content_lower:
            score += weight

    # Length factor — very long dreams tend to be more significant
    word_count = len(dream_output.split())
    if word_count > 300:
        score += 0.1
    elif word_count > 500:
        score += 0.15

    # Normalize to 0-1
    return min(1.0, max(0.0, score))


def create_ghost_memories(dream_output: str, salience: float) -> list:
    """
    Strong dreams (salience > 0.7) generate ghost_memory nodes tagged [DREAM_ECHO].

    Ghost memory node:
    - type: "ghost_memory"
    - tag: "[DREAM_ECHO]"
    - semantic_cluster: (derived from dream content)
    - influence_weight: salience * 0.6
    - decay_rate: 0.15 per day
    - timestamp_created
    - expires_at: timestamp + 72 hours

    Returns list of created ghost memory IDs.
    """
    if salience <= 0.7:
        return []

    _init_db()
    db = _get_db()
    c = db.cursor()
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=72)
    ghost_ids = []

    # Derive semantic cluster from dream content
    # Simple: extract key themes from dream text
    # Full impl: LLM call to extract semantic cluster
    semantic_cluster = _derive_semantic_cluster(dream_output)
    influence_weight = salience * 0.6

    ghost_id = str(uuid.uuid4())
    c.execute("""
        INSERT INTO ghost_memories
        (id, semantic_cluster, tag, influence_weight, decay_rate,
         timestamp_created, expires_at, dream_content_hash, properties)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ghost_id,
        semantic_cluster,
        "[DREAM_ECHO]",
        influence_weight,
        0.15,
        now.isoformat(),
        expires_at.isoformat(),
        str(hash(dream_output[:500])),
        "{}"
    ))

    db.commit()
    db.close()
    ghost_ids.append(ghost_id)

    # Update ghost index
    _update_ghost_index(ghost_id, semantic_cluster, influence_weight)

    return ghost_ids


def _derive_semantic_cluster(dream_output: str) -> str:
    """
    Derive semantic cluster label from dream content.
    Simple heuristic: most common significant words.
    Full impl: LLM call to extract theme/cluster.
    """
    words = dream_output.lower().split()
    significant = [w for w in words if len(w) > 4]

    from collections import Counter
    word_freq = Counter(significant)
    top_words = [w for w, _ in word_freq.most_common(5)]

    # Filter out common dream-generic words
    generic = {"dream", "sleep", "thought", "thing", "something", "everything",
                "nothing", "around", "through", "before", "after", "again", "could"}
    top_words = [w for w in top_words if w not in generic]

    if top_words:
        return "_".join(top_words[:3])
    return "dream_fragment"


def _update_ghost_index(ghost_id: str, semantic_cluster: str, influence_weight: float):
    """Update the ghost memory index for fast retrieval."""
    index = {}
    if GHOST_INDEX_PATH.exists():
        try:
            index = json.loads(GHOST_INDEX_PATH.read_text())
        except Exception:
            index = {}

    index[ghost_id] = {
        "semantic_cluster": semantic_cluster,
        "influence_weight": influence_weight,
        "created_at": _now_iso()
    }

    GHOST_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    GHOST_INDEX_PATH.write_text(json.dumps(index, indent=2))


def apply_ghost_influence(semantic_cluster: str = None) -> dict:
    """
    During memory retrieval: check active ghost_memories.

    For each ghost: boost retrieval weight of real memories
    in matching semantic cluster by ghost.influence_weight.
    Ghosts that have expired are skipped.

    This runs at retrieval time, not nightly.

    If semantic_cluster is provided: only apply ghosts matching that cluster.
    Returns dict of {ghost_id: influence_weight} for matched ghosts.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = datetime.now(timezone.utc)

    rows = c.execute("""
        SELECT id, semantic_cluster, influence_weight, expires_at
        FROM ghost_memories
        WHERE timestamp_created <= ?
    """, (now.isoformat(),)).fetchall()

    db.close()

    active_ghosts = {}
    for row in rows:
        ghost_id, cluster, weight, expires_at = row
        expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        if expires > now:
            if semantic_cluster is None or semantic_cluster == cluster:
                active_ghosts[ghost_id] = {
                    "semantic_cluster": cluster,
                    "influence_weight": weight
                }

    return active_ghosts


def get_ghost_memory(ghost_id: str) -> Optional[dict]:
    """Get a single ghost memory by ID."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    row = c.execute("SELECT * FROM ghost_memories WHERE id = ?", (ghost_id,)).fetchone()
    db.close()

    if not row:
        return None

    return {
        "id": row[0],
        "semantic_cluster": row[1],
        "tag": row[2],
        "influence_weight": row[3],
        "decay_rate": row[4],
        "timestamp_created": row[5],
        "expires_at": row[6],
        "dream_content_hash": row[7],
        "properties": json.loads(row[8]) if isinstance(row[8], str) else row[8]
    }


def get_active_ghosts() -> list:
    """Get all non-expired ghost memories."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = datetime.now(timezone.utc)

    rows = c.execute("""
        SELECT * FROM ghost_memories
        WHERE expires_at > ?
        ORDER BY influence_weight DESC
    """, (now.isoformat(),)).fetchall()

    db.close()

    return [
        {
            "id": r[0],
            "semantic_cluster": r[1],
            "tag": r[2],
            "influence_weight": r[3],
            "decay_rate": r[4],
            "timestamp_created": r[5],
            "expires_at": r[6],
            "dream_content_hash": r[7],
            "properties": json.loads(r[8]) if isinstance(r[8], str) else r[8]
        }
        for r in rows
    ]


def decay_ghost_memories() -> dict:
    """
    Nightly: reduce influence_weight of all active ghosts by decay_rate.
    Remove expired ghosts.

    Returns summary dict.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = datetime.now(timezone.utc)

    # Get all active ghosts
    rows = c.execute("""
        SELECT id, influence_weight, decay_rate, expires_at
        FROM ghost_memories
        WHERE expires_at > ?
    """, (now.isoformat(),)).fetchall()

    decayed = []
    expired_ids = []

    for row in rows:
        ghost_id, weight, decay_rate, expires_at = row
        new_weight = weight - decay_rate
        expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))

        if new_weight <= 0 or expires <= now:
            expired_ids.append(ghost_id)
        else:
            c.execute("""
                UPDATE ghost_memories
                SET influence_weight = ?
                WHERE id = ?
            """, (new_weight, ghost_id))
            decayed.append({"id": ghost_id, "new_weight": new_weight})

    # Remove expired ghosts
    if expired_ids:
        placeholders = ",".join(["?"] * len(expired_ids))
        c.execute(f"DELETE FROM ghost_memories WHERE id IN ({placeholders})", expired_ids)

    db.commit()
    db.close()

    # Update ghost index
    if GHOST_INDEX_PATH.exists():
        try:
            index = json.loads(GHOST_INDEX_PATH.read_text())
            for eid in expired_ids:
                index.pop(eid, None)
            GHOST_INDEX_PATH.write_text(json.dumps(index, indent=2))
        except Exception:
            pass

    return {
        "decayed": len(decayed),
        "expired": len(expired_ids),
        "remaining": len(rows) - len(expired_ids)
    }


# Hook for three_tier_memory retrieval — called at retrieval time
def retrieve_with_ghost_boost(semantic_cluster: str, base_weight: float) -> float:
    """
    Called from three_tier_memory retrieval functions.
    Returns boosted weight if any active ghosts match the cluster.
    """
    ghosts = apply_ghost_influence(semantic_cluster=semantic_cluster)
    if not ghosts:
        return base_weight

    # Apply the highest-weight ghost's influence as a boost
    max_influence = max(g["influence_weight"] for g in ghosts.values())
    boosted = base_weight + (max_influence * 0.3)  # 30% of ghost weight as boost
    return min(1.0, boosted)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: dream_ghost_memory.py <extract_salience|create_ghosts|decay|active> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "extract_salience":
        if len(sys.argv) < 3:
            print("Usage: dream_ghost_memory.py extract_salience <dream_output>")
            sys.exit(1)
        score = extract_dream_salience(sys.argv[2])
        print(f"Dream salience: {score:.3f} (threshold 0.7)")

    elif cmd == "create_ghosts":
        if len(sys.argv) < 4:
            print("Usage: dream_ghost_memory.py create_ghosts <dream_output> <salience>")
            sys.exit(1)
        salience = float(sys.argv[3])
        ghost_ids = create_ghost_memories(sys.argv[2], salience)
        print(f"Created {len(ghost_ids)} ghost memories")

    elif cmd == "decay":
        result = decay_ghost_memories()
        print(f"Decay complete: {result['decayed']} decayed, {result['expired']} expired, "
              f"{result['remaining']} remaining")

    elif cmd == "active":
        ghosts = get_active_ghosts()
        print(f"Active ghosts ({len(ghosts)}):")
        for g in ghosts:
            print(f"  [{g['influence_weight']:.3f}] {g['semantic_cluster']} — expires {g['expires_at'][:10]}")

    else:
        print(f"Unknown command: {cmd}")
