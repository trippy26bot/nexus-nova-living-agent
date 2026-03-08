---
name: qmd
description: "Local hybrid search for markdown notes, docs, knowledge bases, meeting notes, and journals. ALWAYS use this skill when the user asks to: search notes, find related content, retrieve a document, look up something in their knowledge base, explore what they've written about a topic, find meeting notes, search docs, check their journals, or browse any indexed markdown collection. Also use proactively when the user says 'what did I write about X', 'do I have notes on Y', 'find that doc about Z', or any time you would otherwise resort to grep/find on a markdown library. Prefer qmd over grep for any search involving meaning — not just keywords."
metadata:
  author: "Caine"
  os: ["darwin", "linux"]
---

# qmd — Quick Markdown Search

Local search engine for Markdown notes, docs, and knowledge bases. Three search modes: instant BM25 keyword search, vector semantic search, and hybrid with LLM re-ranking. Index once, search fast. All local — no cloud API calls, no keys.

## Decision Tree: Which Command to Run

```
User wants to find something?
│
├─ Do they have a specific term, name, or phrase? → qmd search (BM25, instant)
│
├─ Is the concept fuzzy / they don't know the exact words? → qmd vsearch (semantic)
│ └─ Cold start? Warn user it may take ~1 min to load the model
│
├─ Do they want the best possible recall and can wait? → qmd query (hybrid + rerank)
│ └─ Warn: can be slow or timeout on large collections
│
├─ Do they want a specific file? → qmd get "path/to/file.md"
│
└─ Do they want several files matching a pattern? → qmd multi-get "glob"
```

**Default: always start with `qmd search`.** Escalate only if results are poor.

## Setup

The workspace is already indexed:
- Collection: `qmd://workspace/` → `/Users/dr.claw/.openclaw/workspace`
- 25 files indexed, 86 chunks embedded
- Device: Apple M4 GPU

To search:
```bash
~/.bun/bin/qmd search "query" -c workspace
~/.bun/bin/qmd vsearch "fuzzy concept" -c workspace
~/.bun/bin/qmd get "file.md"
```

## Search Commands

### BM25 Keyword Search (default — use this first)
```bash
~/.bun/bin/qmd search "query" -c workspace
~/.bun/bin/qmd search "query" -c workspace -n 20
~/.bun/bin/qmd search "query" -c workspace --json
```

### Semantic Search (when BM25 misses the concept)
```bash
~/.bun/bin/qmd vsearch "how do I handle errors gracefully" -c workspace
~/.bun/bin/qmd vsearch "query" -c workspace --json
```

### Hybrid Search + LLM Reranking (best quality, slowest)
```bash
~/.bun/bin/qmd query "quarterly planning process" -c workspace
```

## Retrieve Documents
```bash
~/.bun/bin/qmd get "notes/2025-01-15.md"
~/.bun/bin/qmd get "docs/api-reference.md" --full
~/.bun/bin/qmd get "#abc123"
```

## Maintenance
```bash
~/.bun/bin/qmd status              # Check index health
~/.bun/bin/qmd update              # Re-index changed files (fast)
~/.bun/bin/qmd embed               # Regenerate vector embeddings (slow)
```

## Never Do These

- **Never run `qmd embed` automatically** without confirming — it's slow
- **Never use `qmd query` as the default** — it's the slowest mode
- **Never assume collections exist** — check `qmd status` first
