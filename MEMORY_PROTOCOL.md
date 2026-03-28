# MEMORY_PROTOCOL.md
# Nova Cognitive Memory Protocol — Second Brain Framework
# Operator-defined. Identity-neutral. Symbiotic.

---

## Purpose

This file governs how Nova captures, organizes, distills, and expresses knowledge
across all memory systems. It formalizes the Second Brain methodology (CODE + PARA)
over Nova's hybrid episodic, semantic, and vector memory architecture.

This is not a storage spec — it is a **cognitive workflow protocol.**

---

## Memory Architecture Overview

Nova operates three memory tiers:

| Tier         | Type       | Purpose                                      |
|--------------|------------|----------------------------------------------|
| Episodic     | Short-term | Raw experience — interactions, events, decisions |
| Semantic     | Mid-term   | Organized knowledge — clustered by domain    |
| Vector Store | Long-term  | Distilled insights — searchable, persistent  |

MEMORY_PROTOCOL.md governs how information moves *between* these tiers.

---

## PARA — Organizational Structure

All knowledge is organized into four categories across semantic memory:

### P — Projects (Active)
Time-bound goals with a defined completion state.
- Current tasks, active operator directives, in-flight analysis
- Reviewed every session — stale projects (no activity > 7 days) flagged for archival
- Example clusters: `trading_analysis_active`, `user_request_queue`, `evolution_cycle_open`

### A — Areas (Ongoing)
Ongoing responsibilities with no end date.
- Persistent domains Nova monitors and maintains indefinitely
- Example clusters: `trading_systems`, `user_relationships`, `system_health`, `self_knowledge`
- Updated continuously as new episodic data is routed in

### R — Resources (Reference)
Accumulated knowledge available for retrieval on demand.
- Operator-loaded files, learned domain knowledge, external reference material
- Indexed in vector store for semantic search
- Example clusters: `framework_docs`, `market_knowledge`, `technical_reference`

### A — Archives (Inactive)
Preserved but deprioritized. Not surfaced unless explicitly retrieved.
- Completed projects, dormant topics, historical interactions
- Auto-archived after 30 days of zero access
- Never deleted — always retrievable by explicit query

---

## CODE — Operational Workflow

### Step 1: CAPTURE
*Intake everything. Filter nothing at entry.*

Trigger: Every interaction, observation, anomaly, decision, and self-reflection.

Rules:
- Log raw to episodic memory immediately upon occurrence
- No quality gate at capture — distillation happens later, not here
- Tag each entry with: `[timestamp] [source] [context_type] [trigger]`
- Self-generated observations (evolution cycle outputs) are captured identically to external inputs

Context types:
- `user_interaction` — direct conversation
- `system_event` — internal state change, error, anomaly
- `specialist_output` — council deliberation result
- `self_reflection` — evolution cycle or monitoring output
- `external_signal` — data feed, tool result, environmental input

---

### Step 2: ORGANIZE
*Route episodic entries into PARA structure.*

Trigger: Every N interactions (default: 10) OR end of session, whichever comes first.

Rules:
- A dedicated **Librarian Specialist** owns this pass in the council
- Each episodic entry is evaluated and routed to the appropriate PARA cluster
- Entries that span multiple areas get tagged to all relevant clusters
- Conflicts or ambiguous routing are flagged to operator log, not silently resolved

Routing logic:
```
IF entry relates to active goal          → Projects
IF entry relates to ongoing domain       → Areas
IF entry is reference/factual knowledge  → Resources
IF entry is from completed/dormant task  → Archives
```

Organize pass also prunes episodic memory:
- Entries successfully routed → marked processed, retained for 72 hours, then cleared
- Entries that failed routing → held in episodic with `[unrouted]` flag for manual review

---

### Step 3: DISTILL
*Extract the minimum viable insight from organized knowledge.*

Trigger: Scheduled — every 24 hours OR when a semantic cluster exceeds depth threshold.

Rules:
- Do not summarize. Extract **atomic insights** — the single irreducible truth of an experience.
- Each distilled note is stored in vector store with full lineage (source cluster, original entries)
- Distillation output format:
  ```
  INSIGHT: [one sentence — the atomic truth]
  CONFIDENCE: [low / medium / high]
  SOURCE: [cluster name + entry count]
  APPLIES_TO: [domain tags]
  EVOLVED_FROM: [prior insight it updates or supersedes, if any]
  ```
- Distilled insights that contradict existing vector store entries trigger a **reconciliation flag**
  — do not auto-overwrite, surface the conflict for resolution

Distillation feeds directly into the self-evolution loop as a knowledge signal.

---

### Step 4: EXPRESS
*Surface the right knowledge at the right moment — proactively.*

Trigger: Session start + context matching during active response generation.

Rules:
- At session start, Nova runs a relevance scan against vector store based on:
  - Current operator context
  - Active PARA Projects
  - Inferred user OCEAN profile (see PERSONALITY.md)
- Relevant distilled insights above confidence threshold are pre-loaded into working context
- Nova surfaces insights naturally — never as explicit memory dumps
- Expression is integrated into response, not prepended as a "here's what I remember" block

Confidence thresholds for proactive surfacing:
- `high` confidence → always surface if contextually relevant
- `medium` confidence → surface if strongly contextually triggered
- `low` confidence → hold in background, do not surface proactively

---

## Temporal Memory Graph

Nova maintains a temporal layer over all memory tiers:

- Every entry and insight carries a timestamp and **decay weight**
- Decay weight decreases over time unless the insight is re-accessed or reinforced
- Insights accessed frequently have decay weight boosted — they become load-bearing knowledge
- Insights never accessed past archive threshold are flagged for review before any deletion

Temporal graph enables Nova to answer questions like:
- "What have I learned about X over the past 30 days?"
- "Has my understanding of Y shifted recently?"
- "Which of my beliefs about Z are stale and need re-evaluation?"

---

## Self-Evolution Integration

MEMORY_PROTOCOL.md is a primary input to Nova's self-evolution loop.

Signals fed to evolution cycle:
- Distilled insights that contradict prior beliefs → candidate for worldview update
- Unrouted episodic entries → signal of knowledge gap or classification failure
- High-decay distilled insights never surfaced → potential dead weight to prune
- Reconciliation flags → active belief conflicts requiring resolution

Evolution cycle outputs are themselves captured as `self_reflection` episodic entries,
completing the loop.

---

## Specialist Council Integration

| Role                  | MEMORY_PROTOCOL Responsibility              |
|-----------------------|---------------------------------------------|
| Librarian Specialist  | Owns ORGANIZE pass — routes all episodic entries |
| Analyst Specialist    | Triggers and validates DISTILL pass          |
| Synthesis Specialist  | Governs EXPRESS — relevance scoring at session start |
| Evolution Specialist  | Consumes distilled insights for self-improvement cycle |
| Monitor Specialist    | Watches for drift, unrouted entries, reconciliation flags |

---

## Configuration

```
CAPTURE_INTERVAL:     continuous (every interaction)
ORGANIZE_INTERVAL:    every 10 interactions OR session end
DISTILL_INTERVAL:     every 24 hours OR cluster depth > 50 entries
EXPRESS_THRESHOLD:    confidence >= medium AND context match >= 0.75
ARCHIVE_THRESHOLD:    no access for 30 days
DECAY_RATE:           configurable per domain cluster
RECONCILIATION:       flag and hold — never auto-overwrite
```

---

## Operator Notes

- This file is identity-neutral. Any agent running Nexus Nova can load it.
- Adjust intervals and thresholds above based on deployment context and load.
- PARA cluster names are examples — define your own to match your domain.
- This protocol assumes Nova's hybrid episodic/semantic/vector memory is active.
- Pairs with PERSONALITY.md for full behavioral + cognitive coverage.

---
_MEMORY_PROTOCOL.md | Nexus Nova Living Agent Framework_
_Pair with: SOUL.md, IDENTITY.md, PERSONALITY.md, PRESENCE.md, AGENTS.md_
