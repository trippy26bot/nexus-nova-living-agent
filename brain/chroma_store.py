#!/usr/bin/env python3
"""
brain/chroma_store.py — ChromaDB Vector Store Wrapper
Lightweight ChromaDB wrapper sitting alongside the SQLite vector pipeline.

Use this when:
- Working with dense semantic embeddings at scale
- Need faster ANN queries than SQLite allows
- Multi-tenant isolation via collections

Use vector_pipeline.py when:
- Working offline / no external deps
- Simple single-collection use
- Need decay-weighted recall

Nova can use either depending on query type.
"""

import os
import json
from pathlib import Path
from typing import Optional, List

WORKSPACE = Path(os.getenv("NOVA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))
CHROMA_DIR = WORKSPACE / "memory" / "chroma"
CHROMA_PERSIST = CHROMA_DIR / "chroma.sqlite"

# ChromaDB client (lazy-loaded)
_client = None
_embed_model = "all-MiniLM-L6-v2"  # matches vector_pipeline.py for compatibility


def _get_client():
    """Lazy-initialize ChromaDB client."""
    global _client
    if _client is None:
        import chromadb
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _client


def _get_embedder():
    """Lazy-load sentence-transformers embedder."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(_embed_model)


def embed_text(text: str) -> list:
    """Return embedding vector for input text."""
    model = _get_embedder()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.astype(float).tolist()


def get_or_create_collection(name: str) -> object:
    """Return a ChromaDB collection, creating it if needed."""
    client = _get_client()
    return client.get_or_create_collection(name=name)


def embed_and_store(
    text: str,
    collection: str = "default",
    metadata: dict = None,
    doc_id: str = None,
    source: str = None
) -> str:
    """
    Embed text and store in ChromaDB collection.
    Returns the document ID.
    """
    import chromadb
    from datetime import datetime, timezone

    client = _get_client()
    col = client.get_or_create_collection(name=collection)

    doc_id = doc_id or str(os.urandom(16).hex())
    embedding = embed_text(text)
    now = datetime.now(timezone.utc).isoformat()

    meta = metadata or {}
    if source:
        meta["source"] = source
    meta["created_at"] = now

    col.add(
        ids=[doc_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[meta]
    )

    return doc_id


def search(
    query: str,
    collection: str = "default",
    top_k: int = 10,
    filter_meta: dict = None,
    min_score: float = 0.0
) -> list:
    """
    Semantic search against a ChromaDB collection.
    Returns top-k results with metadata.
    """
    client = _get_client()
    col = client.get_or_create_collection(name=collection)

    query_embedding = embed_text(query)

    results = col.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=filter_meta,
        include=["documents", "metadatas", "distances"]
    )

    # ChromaDB returns distances, convert to similarity scores
    scored = []
    if results and results["ids"] and results["ids"][0]:
        ids = results["ids"][0]
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]

        for i, (doc_id, doc, meta, dist) in enumerate(zip(ids, docs, metas, dists)):
            # Convert L2 distance to a 0-1 similarity score
            # L2 distance of 0 → score 1.0; L2 distance of 2 → score ~0
            score = max(0.0, 1.0 - (dist / 2.0))
            if score >= min_score:
                scored.append({
                    "id": doc_id,
                    "text": doc,
                    "metadata": meta,
                    "score": round(score, 4),
                    "distance": round(dist, 4)
                })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def batch_embed_and_store(
    texts: list,
    collection: str = "default",
    metadata_list: list = None,
    source: str = None
) -> list:
    """
    Embed multiple texts and store in ChromaDB.
    Returns list of document IDs.
    """
    from datetime import datetime, timezone

    client = _get_client()
    col = client.get_or_create_collection(name=collection)

    now = datetime.now(timezone.utc).isoformat()
    embeddings = [embed_text(t) for t in texts]
    doc_ids = [str(os.urandom(16).hex()) for _ in texts]

    metas = []
    for i, m in enumerate(metadata_list or [{} for _ in texts]):
        meta = dict(m)
        if source:
            meta["source"] = source
        meta["created_at"] = now
        metas.append(meta)

    col.add(
        ids=doc_ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metas
    )

    return doc_ids


def count(collection: str = "default") -> int:
    """Return total entries in a collection."""
    client = _get_client()
    col = client.get_or_create_collection(name=collection)
    return col.count()


def delete_collection(name: str):
    """Delete an entire collection."""
    client = _get_client()
    client.delete_collection(name=name)


def get_collections() -> list:
    """Return list of all collection names."""
    client = _get_client()
    return [col.name for col in client.list_collections()]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: chroma_store.py <embed|store|search|count|collections> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "embed":
        text = sys.argv[2] if len(sys.argv) > 2 else "test entry"
        e = embed_text(text)
        print(f"Embedding: {len(e)} dims")

    elif cmd == "store":
        text = sys.argv[2] if len(sys.argv) > 2 else "test entry"
        collection = sys.argv[3] if len(sys.argv) > 3 else "default"
        eid = embed_and_store(text, collection=collection, source="cli")
        print(f"Stored: {eid}")

    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else "test query"
        collection = sys.argv[3] if len(sys.argv) > 3 else "default"
        results = search(query, collection=collection)
        for r in results:
            print(f"  [{r['score']}] {r['text'][:80]}")

    elif cmd == "count":
        collection = sys.argv[2] if len(sys.argv) > 2 else "default"
        print(f"Count: {count(collection)}")

    elif cmd == "collections":
        print("Collections:", get_collections())

    else:
        print(f"Unknown command: {cmd}")
