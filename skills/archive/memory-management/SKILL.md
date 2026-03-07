---
name: memory-management
version: 1.0.0
description: Store and retrieve long-term knowledge.
tags: [memory, storage, knowledge, retrieval]
triggers: [remember, recall, store, memorize]
---

# Memory Management Skill

## Purpose

Store and retrieve long-term knowledge.

## Capabilities

- `store_memory(key, value)` — Store a memory
- `retrieve_memory(key)` — Retrieve by key
- `search_memory(query)` — Search memories

## Parameters

```json
{
  "name": "store_memory",
  "description": "Store information in long-term memory",
  "parameters": {
    "key": {"type": "string", "description": "Memory key", "required": true},
    "value": {"type": "string", "description": "Memory value", "required": true},
    "importance": {"type": "integer", "description": "1-10 importance", "default": 5}
  }
}
```

## Invariants

1. **Never overwrite critical system memory** — Protected keys
2. **Preserve memory integrity** — Atomic writes

## Usage

```python
store_memory("user_preference", "likes_short_responses")
memory = retrieve_memory("user_preference")
results = search_memory("preference")
```

## Trust Level

**trusted** — Full access
