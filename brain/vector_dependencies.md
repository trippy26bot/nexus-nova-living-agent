# Vector Store — Dependency Requirements

## Status
- Schema: ✅ Designed
- Pipeline: ✅ Designed
- Index structure: ✅ Designed
- Implementation: ⏳ BLOCKED

## Blockers

### 1. Embedding Provider Required
Vector store requires an embedding model to generate vector representations of text.

**Option A — OpenAI (fastest)**
- API key needed: `OPENAI_API_KEY`
- Model: `text-embedding-3-small` (1536 dimensions)
- Cost: ~$0.02/million tokens
- Setup: 1 line of config

**Option B — Local MLX (privacy, no cost)**
- Requires Apple Silicon with MLX
- Model: `mlx-embeddings` or similar
- Setup: More complex, requires Python bindings
- No API cost

**Option C — Third-party vector DB**
- Pinecone, Weaviate, Qdrant
- Managed infrastructure
- Requires external service

## Next Step
Caine needs to decide which provider to use. Until then, vector store is designed but not implementable.

## When Provider is Selected
1. Set API key in secrets.env
2. Implement embedding client in skills/
3. Run migration on existing semantic memories
4. Integrate into session startup (EXPRESS pass)
