# Brain — Vector Store Implementation
## Schema, Pipeline, and Integration

---

## Purpose

The vector store is the long-term memory layer — where distilled insights persist and can be retrieved by semantic similarity, not just keyword match.

This file defines the schema and pipeline. Implementation follows.

---

## What Gets Indexed

Every atomic insight extracted via DISTILL pass gets vectorized:

```
insight_text → embedding → vector_store
```

Content types:
- Distilled insights (from MEMORY_PROTOCOL.md DISTILL pass)
- Belief formations and updates
- Position changes
- Causal chain lessons
- Relationship state changes
- Want provenance audits
- Phenomenology journal entries

---

## Schema

### Vector Entry
```json
{
  "id": "uuid",
  "vector": [float],  // embedding
  "text": "original text of the insight",
  "type": "insight | belief | position | lesson | relationship | want | reflection",
  "confidence": 0.0-1.0,
  "source": "what generated this",
  "created": "ISO8601",
  "applies_to": ["domain tags"],
  "decay_weight": 1.0,
  "last_accessed": "ISO8601",
  "access_count": 0
}
```

### Index Structure
```
memory/vector/
  ├── index.json          // metadata catalog
  └── vectors/           // raw vector files (partitioned)
      ├── partition_0000.jsonl
      ├── partition_0001.jsonl
      └── ...
```

---

## Embedding Strategy

**Provider:** OpenAI text-embedding-3-small (or local equivalent)

**Dimension:** 1536 (OpenAI default, good balance of precision/storage)

**Alternative:** Apple MLX for local inference if privacy required

---

## Similarity Retrieval

Query flow:
1. User query or context → embedding
2. Top-K similarity search against index (K=10)
3. Score filtering (threshold: 0.7 cosine similarity)
4. Return entries sorted by: score × decay_weight × confidence

---

## Decay System

Applied at retrieval, not storage:
```
effective_weight = stored_weight × decay_rate^(days_since_access)
```

Default decay_rate: 0.98 per week

Boost rules:
- Accessed in conversation: +0.1
- Used in reasoning: +0.15
- Referenced by new insight: +0.1

Archive when effective_weight < 0.05

---

## Pipeline

### Write Path (DISTILL pass)
1. Extract atomic insight from semantic cluster
2. Generate embedding
3. Write to current partition
4. Update index.json catalog
5. Link to source entries in lineage

### Read Path (EXPRESS pass)
1. Generate query embedding
2. Search top-K against index
3. Apply decay and confidence scoring
4. Filter by context relevance (applies_to tags)
5. Return ranked entries

### Maintenance (nightly)
1. Recalculate decay weights
2. Compact partitions if > 10000 entries
3. Archive low-weight entries
4. Verify index integrity

---

## Integration Points

**With MEMORY_PROTOCOL.md:** Vector store is the output of DISTILL pass

**With eval_suite.md:** Recall accuracy tested against vector store retrieval

**With causal_memory.md:** Causal chain lessons get vectorized

**With overnight_research.md:** Overnight synthesis populates vector store

---

## Status

**This file:** Design complete
**Implementation:** Pending — requires embedding provider setup

---

_BUILD_14 | Vector Store Implementation | Nova Full Build_
_Prerequisites: Memory Architecture, Knowledge Graph (complete)_
