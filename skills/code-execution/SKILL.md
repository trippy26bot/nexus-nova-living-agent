---
name: code-execution
version: 1.0.0
description: Run controlled Python code for computation and automation.
tags: [code, python, execution, computation, automation]
triggers: [run code, execute python, compute, calculate]
---

# Code Execution Skill

## Purpose

Run controlled Python code for computation and automation.

## Capabilities

- `run_python(code)` — Execute Python code in sandbox
- `capture_output()` — Get stdout/stderr
- `return_result()` — Return computed result

## Parameters

```json
{
  "name": "run_python",
  "description": "Execute Python code in a controlled sandbox",
  "parameters": {
    "code": {"type": "string", "description": "Python code to execute", "required": true},
    "timeout": {"type": "integer", "description": "Max execution seconds", "default": 30}
  }
}
```

## Invariants

1. **Sandbox execution** — No file I/O, no network, no subprocess
2. **No unrestricted system commands** — Block `os.system`, `subprocess`, `eval`, `exec`
3. **Timeout enforcement** — Kill after timeout seconds

## Safety

- Restricted execution environment
- No access to filesystem or network
- Memory limits enforced

## Trust Level

**approval_required** — Must be explicitly approved
