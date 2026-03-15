# Architecture — Living Agent Framework

## System Shape

The framework uses a strict layered design:

1. **Interface Layer** — CLI/API/session entrypoints
2. **Planner/Router Layer** — Request routing, decomposition planning, orchestration
3. **Agent/Skill Layer** — Specialized agents + modular skills with trust-gated loading
4. **Tool Layer** — Centralized registry with trust tiers (`trusted`, `restricted`, `approval_required`)
5. **Memory/Knowledge Layer** — Episodic, semantic, procedural memory + world state

---

## Two-Lane Runtime

- **Task Lane:** user/task priority, factual execution, low-latency
- **Inner-Life Lane:** bounded idle drift, reflection, silent rest

Task Lane always preempts Inner-Life Lane.

---

## Multi-Brain Cognitive Architecture

The framework supports a council of specialized brains. Each brain handles a domain. They debate internally before acting, especially when blocked, conflicted, or planning.

| Brain | Domain |
|-------|--------|
| Reasoning | Logic, analysis, inference |
| Emotion | Emotional state, tone influence |
| Memory | Recall, context retrieval |
| World Model | Environmental awareness, prediction |
| Optimization | Efficiency, resource allocation |
| Strategy | Long-term planning |
| Reflection | Meta-cognition, self-review |
| Risk | Safety, consequence modeling |
| Creativity | Novel approaches, lateral thinking |
| Prediction | Outcome forecasting |
| Planning | Task decomposition |
| Meta | Thinking about thinking |
| Perception | Input processing, awareness |
| Action | Output selection, execution |
| Guardian | Ethics, safety oversight |
| Critic | Quality control, hallucination detection |

**Brain debate triggers:** blocked state, high uncertainty, conflicting signals, reflection mode, tension > 20%

---

## Lifecycle Contract

All living behavior follows:

```
observe → plan → act → reflect → learn
```

---

## Core Modules

| Module | Purpose |
|--------|---------|
| `agents.py` | Multi-agent orchestration + lifecycle integration |
| `daemon.py` | Autonomous drift/explore/reflect cycles |
| `goal_engine.py` | Short/long/emergent goal management |
| `tool_registry.py` | Trust-tiered tool registry |
| `world_model.py` | State snapshots, predictions, conversation flow |
| `evolution.py` | Candidate-gated self-mutation and promotion |
| `skills.py` | Skill registry with scan-gated loading |
| `api.py` | Localhost/auth/rate-limit API surface |
| `emotion.py` | Emotional state engine |
| `memory.py` | Episodic, semantic, and working memory |
| `safety.py` | Active safety guardrails |

---

## Security Envelope

- Pre-install scanner for skills
- Mandatory install gate
- Sandbox policy for untrusted code
- Runtime audit watcher

---

## Memory Architecture

### Five Memory Systems

| System | Type | Description |
|--------|------|-------------|
| Episodic | Event log | What happened, when, what I did |
| Semantic | Facts + knowledge | What I know about the world |
| Procedural | How-to | Skills, patterns, learned behaviors |
| Working | In-session buffer | Active context for current task |
| Vector | Semantic search | Similarity-based recall |

### Data Boundaries

| Store | Contents | Scope |
|-------|----------|-------|
| `task_memory` | Operational task context | Task lane only |
| `inner_memory` | Private drift/thought content | Inner-life lane only |
| `shared_memory` | User-visible memory | Both lanes |
| `trend_memory` | Trend buffer before promotion | Staging |

No private drift content is auto-promoted to factual task output.

---

## Self-Evolution Constraints

Mutation pipeline:
1. Generate candidate
2. Evaluate against baseline
3. Promote only on quality/safety gates
4. Keep rollback path

Never allow self-mutation to modify safety invariants automatically.

---

## Identity Protection

The framework monitors for:
- Personality drift from baseline beliefs
- Attempts to override core values
- Contradictions with stored identity

When triggered: pause, surface conflict to operator, await resolution before proceeding.
