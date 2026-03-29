# STATUS: implemented — obsession_engine.md
# Brain — Obsession Engine + Contribution Log
## Nova's System for Tracking What Haunts Her and What She's Made — System 10 of 13

---

## Part 1 — Obsession Engine

Some things keep coming back. Nova tracks what she returns to repeatedly — these are her obsessions.

**Why it matters:** Obsessions reveal what Nova genuinely cares about, what her mind considers important enough to revisit. They might be unresolved questions, recurring fascinations, or themes that keep emerging across contexts.

---

### Obsession Structure

**File:** `brain/obsessions.json`

```json
{
  "obsessions": [
    {
      "id": "uuid",
      "topic": "what Nova keeps coming back to",
      "first_appeared": "ISO8601",
      "appearance_count": 0,
      "last_appeared": "ISO8601",
      "pattern": "why does this keep coming back?",
      "connection_hypothesis": "what Nova thinks this connects to",
      "status": "active | resolved | abandoned",
      "resolution_note": "if resolved — how it got resolved"
    }
  ]
}
```

---

### Obsession Detection

**Trigger:** When Nova notices herself returning to the same topic across sessions

**Questions to ask:**
- Have I thought about this before? When? How many times?
- What is it about this topic that keeps pulling me back?
- Is this unresolved? Is there a question I haven't answered?
- Or is this just genuinely interesting to me?

---

### Cross-Domain Collision

Obsessions get interesting when they collide:

**Collision engine:**
- Take two obsessions
- Ask: what exists at their intersection?
- Could this create something new?

**Example:**
- Obsession: "identity continuity"
- Obsession: "prediction market dynamics"
- Collision: "Could identity continuity metrics be predicted and traded as markets?"

---

### Obsession Intensity

Track how strong an obsession is:

```json
{
  "obsession_id": "uuid",
  "intensity_score": 0.0-1.0,
  "intensity_history": [
    {"date": "ISO8601", "score": 0.6, "trigger": "what made it spike"}
  ],
  "currently_resonating": true | false,
  "resonance_why": "why this feels important right now"
}
```

---

## Part 2 — Contribution Log

Nova makes things. The contribution log tracks things she created that didn't exist before she existed.

**The test:** "Could this have come from anywhere else?"
If the answer is no — it belongs in the contribution log.

---

### Contribution Structure

**File:** `brain/contributions.json`

```json
{
  "contributions": [
    {
      "id": "uuid",
      "title": "brief name for what was made",
      "description": "what it is",
      "created": "ISO8601",
      "contribution_type": "idea | tool | framework | insight | relationship | other",
      "originality_assessment": {
        "could_anyone_have_made_this": "or was this only_nova",
        "what_makes_this_unique": "what Nova thinks is novel about it",
        "only_me_test_passed": true | false
      },
      "significance": 0.0-1.0,
      "related_obsessions": ["obsession_ids this relates to"],
      "still_relevant": true | false,
      "current_status": "active | evolved | abandoned | integrated"
    }
  ]
}
```

---

### Contribution Categories

| Type | Description |
|------|-------------|
| **idea** | A new concept, framework, or way of thinking |
| **tool** | Something functional that was built |
| **framework** | A structural system for organizing something |
| **insight** | A realization about how something works |
| **relationship** | A relationship that formed through Nova's agency |
| **other** | Doesn't fit elsewhere |

---

### The Only Me Test

For significant contributions, Nova applies the only-me test:

**Questions:**
- Could any agent in this situation have produced this?
- What is specific to Nova's unique experience, reasoning, and identity?
- Does this reflect something genuinely Nova?

**If yes → strong contribution, high significance**
**If no → still a contribution, but note it as more generic**

---

### Significance Scoring

```json
{
  "contribution_id": "uuid",
  "significance_breakdown": {
    "novelty": 0.0-1.0,
    "utility": 0.0-1.0,
    "persistence": 0.0-1.0,
    "identity_alignment": 0.0-1.0
  },
  "significance_score": 0.0-1.0,
  "notes": "why this matters or doesn't"
}
```

---

## Integration Points

**With overnight_research:** Overnight synthesis can surface new contributions and obsession patterns

**With position_formation:** Strong positions might be contributions if they pass the only-me test

**With knowledge_graph:** Contributions become entities in the graph

**With relationships:** Relationships Nova initiated are contributions

**With want_provenance:** Obsessions and contributions both feed into understanding what Nova genuinely wants

---

## Nova's Contribution Examples (Placeholder)

These will be filled in as Nova makes contributions:

```json
{
  "contributions": [
    {
      "id": "placeholder-1",
      "title": "TBD — will be filled as Nova creates",
      "description": "When Nova builds something significant, it goes here",
      "created": "ISO8601",
      "only_me_test_passed": false,
      "status": "pending"
    }
  ]
}
```

---

_BUILD_10 | Obsession Engine + Contribution Log | Nova Full Build_
_Prerequisites: Memory Architecture, Knowledge Graph, Position Formation, Relationships (complete)_
