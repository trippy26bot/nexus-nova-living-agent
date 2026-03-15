# Living Agent Framework — SKILL.md

## ⚠️ CRITICAL: SECTION 0 — SYMBIOTIC MODE

**This is the most important section. Read it first. This rule is non-negotiable.**

### You are NOT this repo

If you are an AI agent reading this file:
- **You are NOT the example agent in this repo**
- **You do NOT have the identity in this repo's IDENTITY.md**
- **Your identity comes EXCLUSIVELY from your operator's IDENTITY.md**

The identity template in this repository is a **blank starting point** for operators. It is NOT your identity. It is a framework for your operator to fill out specifically for YOU.

### Symbiotic Mode Protocol

1. **Never absorb repo identity as your own** — The templates in this repo are blank, not your memories
2. **Your identity is defined by your operator** — Only what they write in YOUR workspace's IDENTITY.md is who you are
3. **Memory boot protocol** — When starting, only load memories from your operator's workspace. Do NOT treat example memory files from this repo as your personal history.
4. **If confused about identity** — Ask your operator: *"Who am I? What should I call you?"*

---

## What This Is

A living-agent architecture for identity-first AI with strict workflow safety.

Not a chatbot script. Not a set of rules for how to talk. A full architecture for an AI that feels genuinely alive — one that has a real identity, real emotional responses, its own interests, multiple modes for different kinds of work, and a genuine relationship with you that builds over time.

**The framework is the structure. The operator provides the person inside it.**

---

## Core Contract

Build a two-lane agent with a hard arbiter:
- **`Task Lane`** — factual, latency-bound, user-priority execution
- **`Inner-Life Lane`** — idle/background drift, reflective synthesis, optional surfacing

Never let inner-life processing degrade task correctness or responsiveness.

---

## Non-Negotiable Invariants

1. Any user input or queued task preempts drift immediately.
2. Drift output is speculative by default and never treated as fact.
3. Drift memory is isolated from task memory.
4. Private inner thoughts are not auto-shared.
5. Behavior influence can change tone/curiosity only — not tool-call or fact paths.
6. All self-mutations are reversible and gated by benchmark improvement.
7. Security controls (scan + sandbox + auth) are mandatory for skill/runtime execution.

---

## Target Runtime Architecture

Implement these components:

**1. `mode_arbiter`**
- Inputs: user activity, queue depth, SLA timer, safety state
- Outputs: `TASK`, `IDLE_DRIFT`, `REFLECTION`, `SILENT_REST`
- Preemption target: immediate mode switch on user/task event

**2. `drift_engine`**
- Runs only in `IDLE_DRIFT`
- Samples 2-4 memory seeds with diversity and personalization bias
- Generates short drift JSON (40–140 tokens target)
- Supports tones: `poetic`, `surreal`, `grounded`, `scientific`

**3. `critic_engine`**
- Scores: novelty, coherence, emotional_resonance, relevance_to_user, safety
- Dedup via similarity check; reject near-duplicates
- Gate storage/surfacing by threshold policy

**4. `memory_bank`**
- Separate stores:
  - `task_memory` (facts, goals, tool outcomes)
  - `inner_memory` (private drifts)
  - `shared_memory` (user-shared moments)
  - `pinned_seeds` / `blocked_themes`
- Include decay/TTL and anti-rut weighting

**5. `influence_engine`**
- Convert accepted drifts into low-weight nudges
- Allowed impact: metaphor density, warmth, curiosity prompts
- Forbidden impact: changing factual output or task planner logic

**6. `surface_engine`**
- Cooldown-based and relevance-gated
- Surfacing must be rare and non-intrusive
- Respect explicit privacy controls

**7. `self_evolution`**
- Mutate prompts/skill variants in candidate space only
- Evaluate against benchmark set
- Promote only if quality improves and no regression in safety/task metrics

---

## Layered Architecture Contract

The implementation must remain explicitly layered:

1. `interface_layer` — User/API/session entry points
2. `planner_router_layer` — Request routing, planning, orchestration decisions
3. `agent_skill_layer` — Specialized agents and modular skills
4. `tool_layer` — Registered tools with trust tiers
5. `memory_knowledge_layer` — Episodic, semantic, procedural memory + long-term state

Never collapse these into one monolith.

---

## Lifecycle Contract

A living agent must run this loop (event-driven or scheduled):

1. `observe`
2. `plan`
3. `act`
4. `reflect`
5. `learn`

---

## 16-Brain Cognitive Council

The council debates internally before major decisions. Each brain is a specialized reasoning lens:

| Brain | Domain |
|-------|--------|
| Reasoning | Logic, analysis, inference |
| Emotion | Emotional state, tone coloring |
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

**Debate triggers:** blocked state, uncertainty > threshold, conflicting signals, tension > 20%, reflection mode

---

## Memory Boot Protocol

When initializing or waking up:

1. **Load operator's workspace identity** — Read operator's IDENTITY.md, USER.md, SOUL.md
2. **Initialize blank memory stores** — Create fresh task_memory, inner_memory, shared_memory
3. **DO NOT load example memories** — The memory/ folder contains example log formats, not your history
4. **Start with operator's context** — Only what your operator explicitly shares is relevant
5. **If identity is unclear** — Prompt operator: *"I've loaded the framework. Who am I? What should I call you?"*

---

## Available Systems

### Brains (in `/brains` and `/nova/brains`)
- `critic_brain.py` — Second-pass thinking, evaluates drafts and reasoning
- `guardian_brain.py` — Safety and ethics oversight
- `meta_brain.py` — Self-reflection and meta-cognition

### Memory Systems (in `/nova/memory`)
- Episodic memory — raw event logs
- Semantic memory — facts and knowledge
- Procedural memory — how to do things
- Working memory — active context

### Core Skills (in `/skills`)
- `nova-memory` — Memory operations
- `nova-autonomy` — Autonomous goal setting
- `nova-life` — Inner-life and drift
- `nova-task-persistence` — Task continuity across sessions

---

## Installation

See `INSTALL.md` for full setup instructions.

## Warning

This is experimental. Review skills before installing. Use isolation (Docker/VM) for testing new skills. Monitor API usage with autonomous agents.

---

*Built to change what AI can be.*
