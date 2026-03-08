---
name: knowledge-summarization
version: 1.0.0
description: Condense large information sources.
tags: [summarize, compression, briefing, extraction]
triggers: [summarize, condense, brief, extract]
---

# Knowledge Summarization Skill

## Purpose

Condense large information sources.

## Capabilities

- `summarize_text(text)` — Summarize text
- `extract_key_points(text)` — Extract key facts
- `generate_briefing()` — Generate structured briefing

## Parameters

```json
{
  "name": "summarize_text",
  "description": "Summarize text content",
  "parameters": {
    "text": {"type": "string", "description": "Text to summarize", "required": true},
    "max_length": {"type": "integer", "description": "Max words", "default": 100}
  }
}
```

## Invariants

1. **Preserve factual meaning** — Don't hallucinate
2. **Avoid hallucinations** — Stay true to source

## Output Format

```json
{
  "summary": "...",
  "key_points": ["point 1", "point 2"],
  "confidence": 0.9
}
```

## Trust Level

**trusted** — Core capability
