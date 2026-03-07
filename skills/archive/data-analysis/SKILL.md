---
name: data-analysis
version: 1.0.0
description: Analyze structured data.
tags: [data, statistics, analysis, patterns]
triggers: [analyze data, statistics, patterns, trends]
---

# Data Analysis Skill

## Purpose

Analyze structured data.

## Capabilities

- `analyze_dataset(data)` — Analyze data structure
- `compute_statistics()` — Calculate stats
- `detect_patterns()` — Find patterns

## Parameters

```json
{
  "name": "analyze_dataset",
  "description": "Analyze a dataset",
  "parameters": {
    "data": {"type": "array", "description": "Data to analyze", "required": true}
  }
}
```

## Invariants

1. **Validate data format** — Check structure first
2. **Avoid misleading conclusions** — Be statistically honest

## Output Format

```json
{
  "statistics": {"mean": 5, "median": 5},
  "patterns": ["pattern 1"],
  "confidence": 0.85
}
```

## Trust Level

**restricted** — Requires valid input
