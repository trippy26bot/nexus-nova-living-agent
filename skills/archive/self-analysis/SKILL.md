---
name: self-analysis
version: 1.0.0
description: Evaluate outputs and detect mistakes.
tags: [analysis, critique, evaluation, feedback]
triggers: [analyze, critique, evaluate, review]
---

# Self Analysis Skill

## Purpose

Evaluate outputs and detect mistakes.

## Capabilities

- `analyze_output(result)` — Analyze output quality
- `detect_errors(result)` — Find errors
- `suggest_improvements()` — Propose fixes

## Parameters

```json
{
  "name": "analyze_output",
  "description": "Analyze output for quality and errors",
  "parameters": {
    "result": {"type": "string", "description": "Output to analyze", "required": true},
    "criteria": {"type": "array", "description": "Evaluation criteria", "default": ["accuracy", "completeness"]}
  }
}
```

## Invariants

1. **Provide objective feedback** — No self-confirmation bias
2. **Be specific** — Point to exact issues

## Output Format

```json
{
  "score": 8,
  "issues": ["issue 1", "issue 2"],
  "suggestions": ["fix 1", "fix 2"]
}
```

## Trust Level

**trusted** — Core evaluation
