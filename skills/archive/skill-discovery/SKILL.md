---
name: skill-discovery
version: 1.0.0
description: Help the agent identify which skills to use.
tags: [skills, discovery, routing, matching]
triggers: [find skill, which skill, skill lookup]
---

# Skill Discovery Skill

## Purpose

Help the agent identify which skills to use.

## Capabilities

- `search_skill_registry(query)` — Search by query
- `rank_skill_candidates(skills, query)` — Rank by relevance
- `return_best_skill(query)` — Return top skill

## Parameters

```json
{
  "name": "search_skill_registry",
  "description": "Search for relevant skills",
  "parameters": {
    "query": {"type": "string", "description": "Search query", "required": true}
  }
}
```

## Invariants

1. **Prefer specialized skills** — More specific is better
2. **Avoid redundant actions** — Don't suggest duplicate skills

## Output Format

```json
{
  "skills": [
    {"name": "web-research", "score": 0.95, "reason": "matches search"},
    {"name": "knowledge-summarization", "score": 0.7}
  ]
}
```

## Trust Level

**trusted** — Core routing
