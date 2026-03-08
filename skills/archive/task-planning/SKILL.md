---
name: task-planning
version: 1.0.0
description: Break complex goals into actionable steps.
tags: [planning, goals, tasks, decomposition]
triggers: [plan, breakdown, steps, subtasks]
---

# Task Planning Skill

## Purpose

Break complex goals into actionable steps.

## Capabilities

- `goal_to_subtasks(goal)` — Decompose goal into steps
- `prioritize_steps(steps)` — Order by priority
- `detect_dependencies(tasks)` — Find dependencies

## Parameters

```json
{
  "name": "goal_to_subtasks",
  "description": "Break a goal into subtasks",
  "parameters": {
    "goal": {"type": "string", "description": "The goal to decompose", "required": true}
  }
}
```

## Invariants

1. **Ensure logical task order** — Dependencies respected
2. **Avoid infinite loops** — Max depth limit

## Output Format

```json
{
  "tasks": [
    {"id": 1, "description": "do X", "depends_on": []},
    {"id": 2, "description": "do Y", "depends_on": [1]}
  ]
}
```

## Trust Level

**trusted** — Core planning
