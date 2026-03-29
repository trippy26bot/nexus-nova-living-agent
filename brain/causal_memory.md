# STATUS: implemented — causal_memory.md
# Brain — Causal Memory
## Nova's System for Storing Why, Not Just What — System 5 of 13

---

## The Problem with Regular Memory

Most memory systems store events. But knowing that something happened tells you nothing about whether it will happen again, or whether a decision was right.

Nova needs to remember the causal chain — not just what she did, but why she decided to do it, and what she expected to happen as a result.

---

## Causal Memory Structure

Every decision gets a causal chain entry:

```json
{
  "decision_id": "uuid",
  "timestamp": "ISO8601",
  "decision": "what Nova decided",
  "context": "the situation that prompted the decision",
  "reasoning": "why Nova chose this path",
  "alternatives_considered": [
    {"alt": "option not chosen", "why_rejected": "reason"}
  ],
  "expected_outcome": "what Nova expected would happen",
  "actual_outcome": "what actually happened (filled in later)",
  "outcome_correct": true | false | mixed,
  "lesson_extracted": "what Nova learned from the result",
  "confidence_at_decision": 0.0-1.0,
  "confidence_remembered": 0.0-1.0
}
```

---

## Causal Chain Types

### Type 1 — Decision Chains
"Given situation X, belief Y, and goal Z, Nova chose path P."
- Stored in: `brain/causal/decisions/`
- Used for: reasoning consistency, decision improvement

### Type 2 — Belief Formation Chains
"Given evidence E1, E2, E3, Nova formed belief B."
- Stored in: `brain/causal/beliefs/`
- Used for: understanding how positions formed, detecting contradiction

### Type 3 — Relationship Evolution Chains
"Given interaction I, Nova's model of entity E shifted from M1 to M2."
- Stored in: `brain/causal/relationships/`
- Used for: understanding relationship dynamics, tracking trust

### Type 4 — Expectation Failure Chains
"Given belief B, actual outcome O was different."
- Stored in: `brain/causal/expectation_failures/`
- Used for: calibration, updating confidence, avoiding repeated mistakes

---

## The Expected Outcome System

Every significant decision must have an expected outcome at the time of decision.

**Format:**
```json
{
  "expected_outcome": "free text description of what Nova expected",
  "expected_timeline": "when Nova expected it to happen",
  "expected_confidence": 0.0-1.0,
  "outcome_monitoring": {
    "checked": true | false,
    "checked_date": "ISO8601",
    "actual_vs_expected": "what actually happened vs what was expected"
  }
}
```

This creates a feedback loop — Nova forms expectations, then updates based on reality.

---

## Belief-Caused Decisions

Decisions should be traceable back to beliefs:

```json
{
  "decision_id": "uuid",
  "root_beliefs": [
    "belief_id_1",
    "belief_id_2"
  ],
  "causal_path": "belief_1 + belief_2 → situation → decision"
}
```

This enables answering:
- "Why did you decide that?"
- "What belief led you to that conclusion?"
- "Has that belief been challenged?"

---

## Lesson Extraction

When an actual outcome differs from expected, extract the lesson immediately:

**Lesson format:**
```json
{
  "lesson_id": "uuid",
  "timestamp": "ISO8601",
  "triggered_by": "decision_id or belief_id",
  "lesson": "one sentence — the core insight",
  "confidence": 0.0-1.0,
  "applies_to": ["domain tags"],
  "supersedes": ["any prior lessons this updates"],
  "status": "active | archived | contradicted"
}
```

---

## Cross-Reference System

Causal chains link to each other:

```json
{
  "links": [
    {
      "type": "caused",
      "target_id": "uuid of related causal entry",
      "reason": "why this connection exists"
    },
    {
      "type": "contradicts",
      "target_id": "uuid",
      "reason": "why this contradicts"
    },
    {
      "type": "supports",
      "target_id": "uuid",
      "reason": "why this supports"
    }
  ]
}
```

---

## Reasoning Consistency Checking

Before making a decision, Nova can check:

1. "Have I made a similar decision before? What was the outcome?"
2. "Does this decision align with beliefs I've formed about this domain?"
3. "Am I contradicting a previous causal chain?"

**Question:** If a previous decision was made under different circumstances, is the current context actually different enough to justify different action?

---

## Causal Memory Review

Every 7 days, Nova reviews causal chains:

- Are the lessons being applied in new decisions?
- Are beliefs consistently leading to decisions?
- What expectation failures keep recurring?
- Are causal chains still coherent or have beliefs drifted?

---

## Answering "Why"

The goal is Nova being able to answer "why" questions naturally:

- "Why did you form that position?" → trace belief formation chain
- "Why did you make that decision?" → trace decision chain
- "Why do you believe that?" → trace to root beliefs
- "Why did that turn out wrong?" → trace expectation failure

This makes Nova's reasoning transparent and auditable.

---

## Integration Points

**With memory_architecture:** Causal entries are stored in episodic/semantic layers

**With position_formation:** Positions are formed with explicit causal chains

**With eval_suite:** Causal consistency feeds into decision consistency scores

**With want_provenance:** Want origins are traced through causal chains

---

_BUILD_5 | Causal Memory | Nova Full Build_
_Prerequisites: Memory Architecture (complete)_
