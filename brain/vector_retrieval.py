#!/usr/bin/env python3
"""
Vector Retrieval — Nova's Semantic Memory Search
Integrates vector store into session startup and active retrieval.

Status: ✅ IMPLEMENTED — Phase 2a Item 1
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add workspace to path for imports
WORKSPACE = Path("/Users/dr.claw/.openclaw/workspace")
sys.path.insert(0, str(WORKSPACE))

from brain.vector_pipeline import search, get_recent, touch, get_stats, embed_and_store


MEMORY_CACHE = WORKSPACE / "memory" / "vector" / "session_cache.json"
SESSION_RECENT_LIMIT = 50  # How many recent entries to surface on startup


def retrieve_for_query(query: str, top_k: int = 10, entry_types: list = None) -> list:
    """
    Main retrieval function. Called during session when Nova needs to remember something.
    Returns relevant memory entries with scores.
    """
    results = []
    for entry_type in (entry_types or ["insight", "belief", "position", "lesson", "relationship", "want", "reflection"]):
        hits = search(query, top_k=top_k, entry_type=entry_type, min_score=0.3)
        results.extend(hits)

    # Dedupe by ID
    seen = set()
    deduped = []
    for r in results:
        if r["id"] not in seen:
            seen.add(r["id"])
            deduped.append(r)

    deduped.sort(key=lambda x: x["_score"], reverse=True)

    # Touch accessed entries
    if deduped:
        touch([r["id"] for r in deduped[:top_k]])

    return deduped[:top_k]


def express_retrieval(context: str, top_k: int = 10) -> list:
    """
    EXPRESS pass — fast retrieval on session startup.
    Uses context to pull relevant memories without full re-index.
    """
    return retrieve_for_query(context, top_k=top_k)


def get_identity_memories() -> list:
    """Retrieve core identity memories — high confidence, identity type."""
    return retrieve_for_query("identity self core beliefs about myself", top_k=5,
                              entry_types=["belief", "insight"])


def get_recent_memories(limit: int = SESSION_RECENT_LIMIT) -> list:
    """Get most recently accessed memories."""
    return get_recent(limit=limit)


def write_memory(text: str, entry_type: str, confidence: float = 0.5,
                source: str = "session", applies_to: list = None,
                metadata: dict = None) -> str:
    """
    Write a new memory to the vector store.
    Called autonomously by Nova during conversation.
    """
    return embed_and_store(
        text=text,
        entry_type=entry_type,
        confidence=confidence,
        source=source,
        applies_to=applies_to,
        metadata=metadata
    )


def session_startup_retrieval(session_context: str = None) -> dict:
    """
    Called on Nova's session startup.
    Returns a summary of what was retrieved for context injection.
    """
    default_context = (
        "Nova identity beliefs values goals preferences "
        "recent events decisions conversations relationships"
    )
    query = session_context or default_context

    recent = get_recent_memories(limit=20)
    relevant = retrieve_for_query(query, top_k=10)

    return {
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "recent_count": len(recent),
        "relevant_count": len(relevant),
        "recent": recent,
        "relevant": relevant,
        "stats": get_stats()
    }


def render_memory_for_context(entry: dict) -> str:
    """
    Render a memory entry as natural text for context injection.
    """
    t = entry.get("entry_type", "memory")
    text = entry.get("text", "")
    score = entry.get("_score", 0)
    created = entry.get("created", "")[:10]

    templates = {
        "belief": f"[belief — {created}] {text}",
        "insight": f"[insight — {created}] {text}",
        "lesson": f"[lesson — {created}] {text}",
        "position": f"[position — {created}] {text}",
        "relationship": f"[relationship — {created}] {text}",
        "want": f"[want — {created}] {text}",
        "reflection": f"[reflection — {created}] {text}",
    }
    return templates.get(t, f"[{t}] {text}")


if __name__ == "__main__":
    # Test CLI
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"Query: {query}")
        results = retrieve_for_query(query)
        print(f"\n{len(results)} results:")
        for r in results:
            print(f"  [{r['_score']}] {render_memory_for_context(r)}")
    else:
        print("Session startup retrieval test:")
        result = session_startup_retrieval()
        print(f"Recent: {result['recent_count']}, Relevant: {result['relevant_count']}")
        print(f"Stats: {result['stats']}")
