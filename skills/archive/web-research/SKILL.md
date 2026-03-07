---
name: web-research
version: 1.0.0
description: Allow the agent to gather information from the internet.
tags: [research, web, search, fetch, information]
triggers: [search, find, look up, research, web]
---

# Web Research Skill

## Purpose

Allow the agent to gather information from the internet.

## Capabilities

- `search_web(query)` — Search the web for information
- `fetch_page(url)` — Fetch a webpage
- `extract_text(html)` — Extract text from HTML
- `summarize_content(text)` — Summarize extracted content

## Invariants

1. **Never execute arbitrary scripts from webpages** — Always sanitize HTML, strip `<script>` tags
2. **Limit requests to prevent abuse** — Max 10 requests per session, rate-limit to 1 req/sec
3. **Always sanitize fetched content** — Remove malicious HTML, validate URLs

## Usage

```python
# Search for information
results = search_web("quantum computing basics")

# Fetch a page
html = fetch_page("https://example.com/article")

# Extract text
text = extract_text(html)

# Summarize
summary = summarize_content(text)
```

## Safety

- Block known malicious domains
- No execution of fetched JavaScript
- Log all requests for audit

## Trust Level

**restricted** — Requires approval for network access
