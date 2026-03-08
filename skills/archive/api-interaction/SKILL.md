---
name: api-interaction
version: 1.0.0
description: Connect to external services.
tags: [api, http, external, integration]
triggers: [api call, http request, external service]
---

# API Interaction Skill

## Purpose

Connect to external services.

## Capabilities

- `send_http_request(url, method, data)` — Make HTTP request
- `parse_api_response(response)` — Parse JSON response
- `authenticate_with_api(credentials)` — Authenticate

## Parameters

```json
{
  "name": "send_http_request",
  "description": "Send HTTP request",
  "parameters": {
    "url": {"type": "string", "description": "Target URL", "required": true},
    "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"], "default": "GET"},
    "data": {"type": "object", "description": "Request body"}
  }
}
```

## Invariants

1. **Protect API keys** — Never expose in logs
2. **Respect rate limits** — Implement backoff

## Safety

- Block sensitive data in responses
- Rate limit: 10 req/min max

## Trust Level

**approval_required** — Requires explicit approval
