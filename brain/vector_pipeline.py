#!/usr/bin/env python3
"""
Vector Pipeline — Nova's Local Semantic Memory Store
Uses sentence-transformers (all-MiniLM-L6-v2) for embeddings.
Stores to SQLite at memory/vector/vector_store.db

Status: ✅ IMPLEMENTED — Phase 2a Item 1
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Lazy-load the model to avoid startup delay
_model = None
_embed_dim = 384  # all-MiniLM-L6-v2 output dimension

WORKSPACE = Path("/Users/dr.claw/.openclaw/workspace")
VECTOR_DB = WORKSPACE / "memory" / "vector" / "vector_store.db"
VECTOR_DIR = WORKSPACE / "memory" / "vector"


def _get_model():
    """Lazy-load embedding model on first use."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        # all-MiniLM-L6-v2: fast, 384 dim, M4 Mac friendly
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _init_db():
    """Create SQLite schema if it doesn't exist."""
    VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(VECTOR_DB))
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS vectors (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            entry_type TEXT NOT NULL,
            metadata TEXT,  -- JSON string for additional fields
            embedding BLOB NOT NULL,
            confidence REAL DEFAULT 0.5,
            source TEXT,
            created TEXT NOT NULL,
            applies_to TEXT,  -- JSON list of domain tags
            decay_weight REAL DEFAULT 1.0,
            last_accessed TEXT,
            access_count INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_type ON vectors(entry_type)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_created ON vectors(created)
    """)
    conn.commit()
    conn.close()


def _row_to_entry(row):
    """Convert DB row to dict entry."""
    import json as _json
    id_, text, entry_type, metadata, embedding, confidence, source, created, applies_to, decay_weight, last_accessed, access_count = row
    # embedding is stored as JSON text, may come back as bytes or str
    if isinstance(embedding, bytes):
        embedding = embedding.decode("utf-8")
    emb_list = _json.loads(embedding) if embedding else []
    # metadata and applies_to may also be bytes
    if isinstance(metadata, bytes):
        metadata = metadata.decode("utf-8")
    if isinstance(applies_to, bytes):
        applies_to = applies_to.decode("utf-8")
    return {
        "id": id_,
        "text": text,
        "entry_type": entry_type,
        "metadata": _json.loads(metadata) if metadata else {},
        "embedding": emb_list,
        "confidence": confidence,
        "source": source,
        "created": created,
        "applies_to": _json.loads(applies_to) if applies_to else [],
        "decay_weight": decay_weight,
        "last_accessed": last_accessed,
        "access_count": access_count
    }


def embed_text(text: str):
    """Return embedding vector for input text."""
    model = _get_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.astype(float).tolist()


def embed_and_store(text: str, entry_type: str, metadata: dict = None,
                   confidence: float = 0.5, source: str = None,
                   applies_to: list = None) -> str:
    """
    Embed text and store in vector DB.
    Returns the entry ID.
    """
    import json as _json
    _init_db()

    embedding = embed_text(text)
    entry_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(str(VECTOR_DB))
    c = conn.cursor()
    c.execute("""
        INSERT INTO vectors
        (id, text, entry_type, metadata, embedding, confidence, source, created, applies_to, decay_weight, last_accessed, access_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry_id,
        text,
        entry_type,
        _json.dumps(metadata or {}),
        _json.dumps(embedding),
        confidence,
        source or "",
        now,
        _json.dumps(applies_to or []),
        1.0,
        now,
        0
    ))
    conn.commit()
    conn.close()
    return entry_id


def search(query: str, top_k: int = 10, entry_type: str = None,
          applies_to: list = None, min_score: float = 0.3) -> list:
    """
    Semantic search against vector store.
    Returns top-k entries with cosine similarity > min_score.
    """
    import json as _json
    _init_db()

    query_embedding = embed_text(query)
    conn = sqlite3.connect(str(VECTOR_DB))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if entry_type:
        c.execute("SELECT * FROM vectors WHERE entry_type = ?", (entry_type,))
    else:
        c.execute("SELECT * FROM vectors")

    rows = c.fetchall()
    conn.close()

    scored = []
    for row in rows:
        entry = _row_to_entry(tuple(row))
        stored_embedding = entry["embedding"]  # already a list after _row_to_entry

        # Cosine similarity
        dot = sum(a * b for a, b in zip(query_embedding, stored_embedding))
        norm_q = sum(a * a for a in query_embedding) ** 0.5
        norm_s = sum(a * a for a in stored_embedding) ** 0.5
        score = dot / (norm_q * norm_s) if (norm_q * norm_s) > 0 else 0

        # Apply decay
        last_accessed = entry.get("last_accessed")
        if last_accessed:
            try:
                last = datetime.fromisoformat(last_accessed.replace("Z", "+00:00"))
                days_old = (datetime.now(timezone.utc) - last).total_seconds() / 86400
                decay_rate = 0.98 ** (days_old / 7)  # 0.98 per week
                score *= entry["decay_weight"] * decay_rate
            except Exception:
                pass

        if score >= min_score:
            entry["_score"] = round(score, 4)
            scored.append(entry)

    scored.sort(key=lambda x: x["_score"], reverse=True)
    return scored[:top_k]


def touch(ids: list):
    """Update last_accessed and increment access_count for entries."""
    _init_db()
    now = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(str(VECTOR_DB))
    c = conn.cursor()
    for entry_id in ids:
        c.execute("""
            UPDATE vectors
            SET last_accessed = ?, access_count = access_count + 1
            WHERE id = ?
        """, (now, entry_id))
    conn.commit()
    conn.close()


def get_recent(limit: int = 20, entry_type: str = None) -> list:
    """Return most recently accessed entries."""
    _init_db()
    conn = sqlite3.connect(str(VECTOR_DB))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if entry_type:
        c.execute("""
            SELECT * FROM vectors
            WHERE entry_type = ?
            ORDER BY last_accessed DESC
            LIMIT ?
        """, (entry_type, limit))
    else:
        c.execute("""
            SELECT * FROM vectors
            ORDER BY last_accessed DESC
            LIMIT ?
        """, (limit,))
    rows = c.fetchall()
    conn.close()
    return [_row_to_entry(tuple(r)) for r in rows]


def get_all_entries(entry_type: str = None, limit: int = 1000) -> list:
    """Return all entries (for consolidation)."""
    _init_db()
    conn = sqlite3.connect(str(VECTOR_DB))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if entry_type:
        c.execute("SELECT * FROM vectors WHERE entry_type = ? LIMIT ?", (entry_type, limit))
    else:
        c.execute("SELECT * FROM vectors LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [_row_to_entry(tuple(r)) for r in rows]


def archive_entry(entry_id: str):
    """Mark entry as archived (decay_weight = 0)."""
    _init_db()
    conn = sqlite3.connect(str(VECTOR_DB))
    c = conn.cursor()
    c.execute("UPDATE vectors SET decay_weight = 0 WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()


def delete_entry(entry_id: str):
    """Permanently delete an entry."""
    _init_db()
    conn = sqlite3.connect(str(VECTOR_DB))
    c = conn.cursor()
    c.execute("DELETE FROM vectors WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()


def get_stats() -> dict:
    """Return vector store statistics."""
    _init_db()
    conn = sqlite3.connect(str(VECTOR_DB))
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM vectors")
    total = c.fetchone()[0]
    c.execute("SELECT entry_type, COUNT(*) FROM vectors GROUP BY entry_type")
    by_type = dict(c.fetchall())
    conn.close()
    return {"total": total, "by_type": by_type}


if __name__ == "__main__":
    import sys
    # CLI for testing
    if len(sys.argv) < 2:
        print("Usage: vector_pipeline.py <embed|search|stats> [args]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "embed":
        text = sys.argv[2] if len(sys.argv) > 2 else "test entry"
        entry_type = sys.argv[3] if len(sys.argv) > 3 else "test"
        eid = embed_and_store(text, entry_type)
        print(f"Stored: {eid}")

    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else "test query"
        results = search(query)
        for r in results:
            print(f"  [{r['_score']}] {r['text'][:80]}")

    elif cmd == "stats":
        print(get_stats())

    else:
        print(f"Unknown command: {cmd}")
