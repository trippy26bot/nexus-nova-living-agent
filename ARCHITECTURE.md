# Architecture — Nexus Nova (v2)

## System Shape

Nexus Nova uses a strict layered design:

1. Interface Layer
- CLI/API/session entrypoints

2. Planner/Router Layer
- Request routing
- decomposition planning
- orchestration

3. Agent/Skill Layer
- specialized agents (`router`, `planner`, `researcher`, `executor`, `critic`, `memory`)
- modular skills with trust-gated loading

4. Tool Layer
- centralized registry with trust tiers (`trusted`, `restricted`, `approval_required`)

5. Memory/Knowledge Layer
- episodic memory
- semantic memory
- procedural memory
- world state and lifecycle state

## Two-Lane Runtime

- Task Lane: user/task priority, factual execution, low-latency.
- Inner-Life Lane: bounded idle drift, reflection, silent rest.

Task Lane always preempts Inner-Life Lane.

## Lifecycle Contract

All living behavior follows:

`observe -> plan -> act -> reflect -> learn`

Implemented by:
- `nova_lifecycle.py`
- `nova_agents.py` (integrated lifecycle hooks)
- `nova_goal_engine.py`
- `core/world_model.py`

## Core Modules

- `nova_agents.py`: multi-agent orchestration + lifecycle integration
- `nova_daemon.py`: autonomous drift/explore/reflect cycles
- `nova_goal_engine.py`: short/long/emergent goal management
- `nova_tool_registry.py`: trust-tiered tool registry
- `core/world_model.py`: state snapshots, predictions, conversation flow
- `nova_evolution.py`: candidate-gated self-mutation and promotion
- `nova_skills.py`: skill registry with scan-gated Python loading
- `nova_api.py`: localhost/auth/rate-limit API surface

## Security Envelope

- Pre-install scanner: `scanner/skill_scanner.py`
- Mandatory install gate: `scanner/secure_install.sh`
- Sandbox policy: `sandbox/skill-sandbox.yaml`
- Seccomp profile: `sandbox/seccomp-policy.json`
- Runtime watcher: `sandbox/audit_watcher.py`

## Data Boundaries

- `task_memory`: operational task context
- `inner_memory`: private drift/thought content
- `shared_memory`: user-visible memory
- `trend_memory`: trend ingest buffer before promotion

No private drift content is auto-promoted to factual task output.

## Self-Evolution Constraints

Mutation pipeline:
1. Generate candidate
2. Evaluate against baseline
3. Promote only on quality/safety gates
4. Keep rollback path

Never allow self-mutation to modify safety invariants automatically.
