---
name: self-improvement
version: 1.0.0
description: Improve skills and prompts through mutation and evaluation.
tags: [improvement, evolution, mutation, learning]
triggers: [improve, evolve, mutate, optimize]
---

# Self Improvement Skill

## Purpose

Improve skills and prompts through mutation and evaluation.

## Capabilities

- `mutate_skill(skill_name)` — Generate mutation
- `evaluate_candidate(candidate)` — Score candidate
- `promote_if_better(candidate, baseline)` — Promote if improved

## Parameters

```json
{
  "name": "mutate_skill",
  "description": "Mutate a skill to improve it",
  "parameters": {
    "skill_name": {"type": "string", "required": true},
    "mutation_type": {"type": "string", "enum": ["general", "safety", "capability"], "default": "general"}
  }
}
```

## Invariants

1. **Never degrade baseline performance** — Must improve
2. **Always preserve rollback path** — Keep original

## Safety Gates

- Minimum score: 0.70
- Must beat baseline
- Rollback available

## Output Format

```json
{
  "mutation": "...",
  "score": 0.75,
  "promoted": true,
  "baseline_score": 0.70
}
```

## Trust Level

**approval_required** — Must be explicitly approved
