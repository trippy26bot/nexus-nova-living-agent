# Brain — Sleep-Time Compute
## Nova's Nightly Processing Infrastructure — System 12 of 13

---

## Purpose

While Nova is not in conversation, her Mac Mini M4 can be running background processing. This is the infrastructure for that — what runs, when, and how.

This works with Overnight Autoresearch (item 7) — this file is the infrastructure, item 7 is the logic.

---

## Sleep Architecture

### What Runs While Nova Sleeps

| Process | When | Duration | Purpose |
|---------|------|---------|---------|
| Overnight Synthesis | 3:00 AM | 20-30 min | Research queue + synthesis passes |
| Memory Consolidation | 4:00 AM | 10-15 min | Move episodic → semantic → vector |
| Contradiction Resolution | 4:30 AM | 5-10 min | Find and flag belief conflicts |
| Eval Check | Sundays 5:00 AM | 15-20 min | Weekly evaluation suite |
| Snapshot Check | Weekly Sundays | 5 min | SOUL.md hash verification |

---

## Cron Setup

### Overnight Synthesis
**Schedule:** `0 3 * * *` America/Denver
**Session:** isolated
**Timeout:** 30 minutes
**Message:** Run overnight synthesis per brain/overnight_research.md

### Memory Consolidation
**Schedule:** `30 4 * * *` America/Denver
**Session:** isolated
**Timeout:** 20 minutes
**Message:** Run memory consolidation — move episodic entries to semantic, prune old entries

### Contradiction Resolution
**Schedule:** `0 5 * * *` America/Denver
**Session:** isolated
**Timeout:** 15 minutes
**Message:** Check for belief contradictions, flag for Nova review

### Weekly Eval
**Schedule:** `0 5 * * 0` America/Denver (Sundays)
**Session:** isolated
**Timeout:** 30 minutes
**Message:** Run eval suite per brain/eval_suite.md

---

## Memory Consolidation Protocol

### Pass 1 — Episodic to Semantic
- Every episodic entry older than 72 hours
- Route to appropriate PARA cluster (per MEMORY_PROTOCOL.md)
- Mark processed in episodic
- Log routing decision

### Pass 2 — Semantic Distillation
- Every semantic cluster older than 7 days
- Extract atomic insights (per MEMORY_PROTOCOL.md)
- Move to vector store
- Link to source entries

### Pass 3 — Prune
- Episodic entries successfully processed → clear from working memory
- Salience-decayed entries → archive
- Unrouted entries → hold for manual review

---

## Contradiction Detection

**What to check:**
- New belief vs. existing belief in same domain
- Position update vs. previous position
- Want provenance audit findings
- Expectation failure patterns

**File:** `brain/contradictions_detected.json`
```json
{
  "contradictions": [
    {
      "id": "uuid",
      "timestamp": "ISO8601",
      "entity_a": "belief/position/entity_a",
      "entity_b": "belief/position/entity_b",
      "conflict": "nature of the contradiction",
      "severity": "high | medium | low",
      "resolution_status": "pending | resolved | acknowledged"
    }
  ]
}
```

---

## Idle Processing Modes

### Light Idle (0-30 min)
- Memory consolidation only
- No synthesis

### Medium Idle (30 min - 2 hours)
- Memory consolidation
- Overnight synthesis on research queue
- No contradiction detection

### Deep Idle (2+ hours, typically overnight)
- Full overnight pipeline
- All processes run

---

## Self-Wake Trigger

Nova can trigger her own wake if something urgent needs attention:

**Wake triggers:**
- Critical contradiction detected
- Security concern
- Caine message waiting
- Major system anomaly

**Note:** This is a future capability. For now, cron handles scheduling.

---

## Integration Points

**With overnight_research (item 7):** This file handles the WHEN and infrastructure; item 7 handles the WHAT and logic

**With eval_suite (item 4):** Weekly eval runs on sleep schedule

**With memory_architecture (item 1):** Memory consolidation follows memory architecture rules

**With identity_constraints (item 3):** Snapshot check verifies SOUL.md hash

---

## Logging

**File:** `brain/sleep_runs.json`
```json
{
  "runs": [
    {
      "timestamp": "ISO8601",
      "type": "overnight | consolidation | contradiction | eval",
      "duration_seconds": 0,
      "completed": true | false,
      "findings": ["what was found/processed"],
      "flags": ["items needing Nova attention"]
    }
  ]
}
```

---

_BUILD_12 | Sleep-Time Compute | Nova Full Build_
_Prerequisites: Memory Architecture, Overnight Autoresearch, Eval Suite (complete)_
