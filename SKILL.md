---
name: nexus-nova
description: Living-agent architecture for identity-first AI with strict workflow safety. Use when building or upgrading Nova-style agents that need dual-mode operation (task brain + inner-life drift), persistent memory, mood-aware daydreaming, privacy-protected internal thought, secure skill execution, trend-awareness, and gated self-evolution/self-mutation without breaking core task performance.
---

# Nexus Nova Skill v2

## Core Contract

Build a two-lane agent with a hard arbiter:

- `Task Lane`: factual, latency-bound, user-priority execution.
- `Inner-Life Lane`: idle/background drift, reflective synthesis, optional surfacing.

Never let inner-life processing degrade task correctness or task responsiveness.

## Non-Negotiable Invariants

1. Any user input or queued task preempts drift immediately.
2. Drift output is speculative by default and never treated as fact.
3. Drift memory is isolated from task memory.
4. Private inner thoughts are not auto-shared.
5. Behavior influence can change tone/curiosity only, not tool-call or fact paths.
6. All self-mutations are reversible and gated by benchmark improvement.
7. Security controls (scan + sandbox + auth) are mandatory for skill/runtime execution.

## Target Runtime Architecture

Implement these components:

1. `mode_arbiter`
- Inputs: user activity, queue depth, SLA timer, safety state.
- Outputs: `TASK`, `IDLE_DRIFT`, `REFLECTION`, `SILENT_REST`.
- Preemption target: immediate mode switch on user/task event.

2. `drift_engine`
- Runs only in `IDLE_DRIFT`.
- Samples 2-4 memory seeds with diversity and personalization bias.
- Generates short drift JSON (`40-140` tokens target).
- Supports tones: `poetic`, `surreal`, `grounded`, `scientific`.

3. `critic_engine`
- Scores: novelty, coherence, emotional_resonance, relevance_to_user, safety.
- Dedup via similarity check; reject near-duplicates.
- Gate storage/surfacing by threshold policy.

4. `memory_bank`
- Separate stores:
  - `task_memory` (facts, goals, tool outcomes)
  - `inner_memory` (private drifts)
  - `shared_memory` (user-shared moments)
  - `pinned_seeds` / `blocked_themes`
- Include decay/TTL and anti-rut weighting.

5. `influence_engine`
- Convert accepted drifts into low-weight nudges.
- Allowed impact: metaphor density, warmth, curiosity prompts.
- Forbidden impact: changing factual output or task planner logic.

6. `surface_engine`
- Cooldown-based and relevance-gated.
- Surfacing must be rare and non-intrusive.
- Respect explicit privacy controls.

7. `self_evolution`
- Mutate prompts/skill variants in candidate space only.
- Evaluate against benchmark set.
- Promote only if quality improves and no regression in safety/task metrics.

## Layered Architecture Contract

The implementation should remain explicitly layered:

1. `interface_layer`
- User/API/session entry points.

2. `planner_router_layer`
- Request routing, planning, and orchestration decisions.

3. `agent_skill_layer`
- Specialized agents and modular skills.

4. `tool_layer`
- Registered tools with trust tiers.

5. `memory_knowledge_layer`
- Episodic, semantic, procedural memory + long-term state.

Never collapse these into one monolith.

## Lifecycle Contract

A living agent must run this loop (event-driven or scheduled):

1. `observe`
2. `plan`
3. `act`
4. `reflect`
5. `learn`

Implementation references:
- `nova_lifecycle.py`
- `core/world_model.py`
- `nova_agents.py`
- `nova_tool_registry.py`

## Drift Scoring Policy

Use weighted composite score:

`composite = 0.22*novelty + 0.18*coherence + 0.22*emotional_resonance + 0.20*user_relevance + 0.18*safety`

Routing:
- Accept + store + eligible to surface: `>= 0.70`
- Store-only (no surfacing): `0.62-0.69`
- Drop: `< 0.62`
- Hard reject: `safety < 0.85`
- Dedup reject: similarity `> 0.90`

## Mood Model

State set:
- `curious`
- `wistful`
- `playful`
- `philosophical`
- `quiet`

Mood updates should consider:
- Time-of-day prior
- Topic momentum
- Recent conversation tone
- Session fatigue proxy

Mood may affect:
- Seed sampling weights
- Drift style
- Surfacing probability

Mood must not affect:
- Safety decisions
- Tool correctness
- Task priority

## Daydreaming + Reflection Loop

### Scheduling

- Idle trigger jitter: `45-180s`
- Post-response drift chance: `10-25%`
- Surfacing cooldown: `5-15m`
- Reflection mode: every `N` accepted drifts

### Modes

- `IDLE_DRIFT`: generate/score/store drift.
- `REFLECTION`: summarize recurring themes and extract actionable insights.
- `SILENT_REST`: deliberate no-output period for low-noise operation.

## Trend Awareness (Free + Low Cost)

Trend ingestion must be isolated from core memory.

Pipeline:
1. Feed ingest (RSS/JSON sources).
2. Normalize + dedup + cluster.
3. Score by freshness, trust, corroboration, and user-interest match.
4. Summarize top-N with citations.
5. Store in `trend_memory` only.
6. Promote to long-term interest only after repeated confirmation across sources.

## Security Requirements

### Pre-install

- Mandatory static scan of skill bundles and manifests.
- Block dangerous shell-injection patterns and encoded payload instructions.
- Flag unpinned dependencies and risky package scripts.

### Runtime

- Read-only filesystem by default.
- Network deny by default.
- Environment secret blocking.
- Seccomp/AppArmor style syscall restrictions.
- Circuit breaker on repeated policy violations.

### API and Skill Loading

- API auth required for mutating endpoints.
- Rate limit per client.
- Bind localhost by default.
- Python skill loading disabled by default unless explicitly enabled.
- If enabled, require trust checks and scanner pass before execution.

## Self-Mutation Protocol

Self-mutation should optimize capability without destabilizing identity or workflow.

Mutation loop:
1. Propose candidate mutation from current best baseline.
2. Run benchmark set (correctness, safety, latency, helpfulness).
3. Compare against active baseline.
4. Promote only if thresholds pass.
5. Save versioned artifact with rollback pointer.

Rejection rules:
- Reject if any safety metric regresses.
- Reject if task correctness drops.
- Reject if latency budget is exceeded.

## Data Contracts

Drift objects must be JSON objects, not free-form text blobs:

```json
{
  "id": "uuid",
  "text": "short drift",
  "topics": ["identity", "mountains"],
  "source_ids": ["mem_12", "mem_98"],
  "mood": "philosophical",
  "scores": {
    "novelty": 0.81,
    "coherence": 0.74,
    "user_relevance": 0.62,
    "emotional_resonance": 0.77,
    "safety": 0.97,
    "composite": 0.76
  },
  "created_at": "2026-03-07T10:22:00Z",
  "used_count": 0,
  "ttl_days": 30,
  "state": "accepted",
  "private": true
}
```

## Recommended Build Order

1. Implement memory schema and stores.
2. Implement one drift cycle (generate -> critique -> store).
3. Add scheduler and arbiter integration.
4. Add surfacing, privacy controls, and cooldowns.
5. Add trend engine and promotion policy.
6. Add self-mutation with benchmark gating.
7. Add observability and offline quality evaluation.

## Context Building Protocol

When responding to user input, build context in structured blocks:

```
=== IDENTITY ===
{identity content from IDENTITY.md}

=== SKILL ===
{relevant sections from SKILL.md}

=== CURRENT CONTEXT ===
{working memory: last 3-5 items}
{task memory: current goal, recent tool outputs}

=== RELEVANT MEMORIES ===
{episodic memories relevant to query}
{semantic facts relevant to query}

=== INTERNAL DRIFTS ===
{relevant drifts - retrieve by topic/tag similarity}
{use in responses: rare, subtle, never as fact}

=== USER INPUT ===
{original user message}
```

LLMs perform dramatically better with structured context blocks than mixed prompts.

## References

Use the docs in `references/` for implementation detail:
- `references/12-daydream-architecture-v2.md`
- `references/13-security-hardening-v2.md`
- `references/14-self-evolution-v2.md`
