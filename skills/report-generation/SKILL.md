---
name: report-generation
version: 1.0.0
description: Generate structured reports.
tags: [report, document, output, format]
triggers: [generate report, create report, document]
---

# Report Generation Skill

## Purpose

Generate structured reports.

## Capabilities

- `generate_report(data)` — Create full report
- `create_summary()` — Create summary
- `format_output(data, format)` — Format as markdown/html/json

## Parameters

```json
{
  "name": "generate_report",
  "description": "Generate a structured report",
  "parameters": {
    "title": {"type": "string", "required": true},
    "sections": {"type": "array", "required": true},
    "format": {"type": "string", "enum": ["markdown", "html", "json"], "default": "markdown"}
  }
}
```

## Invariants

1. **Ensure clarity** — Clear headings, logical flow
2. **Maintain structure** — Proper sections

## Output

Markdown/HTML/JSON formatted report

## Trust Level

**trusted** — Output generation
