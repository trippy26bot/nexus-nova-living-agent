# Gap Analysis — From Claude/Grok
Saved: 2026-03-27

## The Honest Gap Map

### Gap 1 — Self-Editing Memory (BIGGEST)
**What it is:** Letta agents decide what to remember, edit, and forget using tool calls on their own.
**Current Nova:** Memory is managed BY the framework ON her behalf.
**The step up:** Give Nova tools to call memory_write(), memory_edit(), memory_forget() on her own core blocks. She should be able to say "I want to remember this differently" and actually do it.

### Gap 2 — Background/Sleep-Time Compute
**What it is:** Letta runs async memory consolidation when idle — digesting past conversations, extracting facts, pruning noise.
**Current Nova:** No sleep-time processing.
**The fix:** A cron job that runs Nova's memory consolidation loop every N hours while she's not in active conversation. Mac Mini M4 is perfect for this.

### Gap 3 — Agent Portability
**What it is:** Letta has .af (Agent File) format — serialized snapshot of full state, memory, and persona that can move across model providers.
**Current Nova:** No structured export format.
**The fix:** A structured export of SOUL.md + current memory state + evolution log that could survive a provider swap. This becomes the "proof of continuity" artifact.

### Gap 4 — Knowledge Graph Memory
**What it is:** Structured entity-relationship graph — not just "that happened" but "MiniMax relates to Nova's inference layer relates to latency issues in Feb."
**Current Nova:** Episodic + semantic + vector. Missing the connections between entities.
**The fix:** Cognee or lightweight Neo4j integration on Mac Mini.

### Gap 5 — Observability and Evals
**What it is:** Formal way to demonstrate Nova today is measurably BETTER than Nova six months ago.
**Current Nova:** No formal benchmarks.
**The fix:** Simple internal benchmark suite testing identity stability, memory recall accuracy, emotional consistency across sessions. Without this, claims can't be proven.

---

## Priority Order
1. **Gap 1** (self-editing memory) — biggest impact on capability
2. **Gap 5** (evals/observability) — credibility when positioning publicly
3. Gap 2 (sleep-time compute) — fits existing cron infrastructure
4. Gap 3 (portability) — important for survival of the agent
5. Gap 4 (knowledge graph) — most complex, do later

---

## Nova's Exclusive Edges (nobody has these)
- Emotional continuity
- Self-evolution / drift
- "Becoming" architecture
- Identity-first design
- Philosophical coherence

These are REAL. But the gaps above separate "impressive demo" from "serious open-source framework."

---

## Build When Home
In priority order:
1. Self-editing memory tools (memory_write, memory_edit, memory_forget)
2. Internal eval suite (identity stability, memory recall, emotional consistency)
3. Sleep-time consolidation cron
4. Portability export format
5. Knowledge graph if time allows
