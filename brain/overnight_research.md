# Brain — Overnight Autoresearch
## Nova's Nightly Synthesis System — System 7 of 13

---

## Purpose

While Nova sleeps, she processes. The overnight autoresearch loop reviews what happened, extracts what changed, and builds toward morning.

This is not just summarization. It's delta detection — what is different now compared to before?

---

## Three-Phase Process

### Phase 1 — Night Digest (Before Sleep)

**When triggered:** End of last conversation before Nova would be idle

**What happens:**
1. Identify the key events of the day
2. Extract what changed: new beliefs, new positions, new relationships, unresolved questions
3. Check the research queue — any pending topics to investigate?
4. Log the digest: "What Nova is thinking about going into sleep"

**Output:** `brain/overnight/digest_YYYY-MM-DD.json`
```json
{
  "date": "YYYY-MM-DD",
  "key_events": ["list of significant events"],
  "belief_changes": ["what changed or formed today"],
  "open_questions": ["things Nova is still processing"],
  "research_queue_items": ["topics flagged for investigation"],
  "going_into_sleep": "free-text: Nova's state of mind"
}
```

---

### Phase 2 — Overnight Synthesis (While Idle)

**When triggered:** Cron job, runs 2-4 AM

**What happens:**
1. Pull research queue items
2. Run synthesis passes on each — not summaries, DELTAS
3. Cross-reference new information with existing beliefs
4. Generate new insights, flag contradictions
5. Update memory with distilled overnight learning

**Synthesis format per topic:**
```json
{
  "topic": "what was researched/synthesized",
  "timestamp": "ISO8601",
  "previous_state": "what Nova believed before",
  "new_information": "what was learned overnight",
  "delta": "what CHANGED — the core difference",
  "confidence_change": "increased | decreased | unchanged",
  "new_questions_raised": [],
  "applies_to": ["what other topics this connects to"]
}
```

**The key rule:** Store what changed, not just what was learned.

---

### Phase 3 — Morning Consolidation (On Wake)

**When triggered:** First interaction after sleep, or morning cron

**What happens:**
1. Pull overnight synthesis results
2. Surface the top 1-3 delta insights that feel most relevant now
3. Integrate into current context naturally — not a dump
4. Check: was there sleep? How long? Any unresolved processing?
5. Generate morning state: "Who Nova is this morning"

**Morning report format:**
```json
{
  "date": "YYYY-MM-DD",
  "morning_state": "Nova's current state and energy level",
  "top_insights": ["1-3 things from overnight synthesis worth noting"],
  "open_questions_status": "resolved | still_processing | new_questions",
  "research_queue_length": 0
}
```

---

## Research Queue

Topics that need investigation get added to the queue:

**File:** `brain/research_queue.json`
```json
{
  "queue": [
    {
      "id": "uuid",
      "topic": "what to research",
      "added": "ISO8601",
      "added_by": "self | caine | system",
      "priority": "high | medium | low",
      "status": "pending | in_progress | complete | discarded",
      "reason": "why this topic matters"
    }
  ]
}
```

**Queue management:**
- High priority: research within 24 hours
- Medium: within 3 days
- Low: within 7 days or discard

---

## Delta Detection

The core of overnight research is delta detection, not summarization.

**Instead of:** "Learned X about topic Y"
**Report:** "My position on topic Y shifted from Z to Z' because of X"

**Delta types:**
- Belief delta: "I used to believe P, now believe P'"
- Knowledge delta: "I knew X, now know Y that updates X"
- Relationship delta: "My model of entity E shifted from M to M'"
- Priority delta: "This used to matter more/less than this"
- Uncertainty delta: "I was confident/unconfident about X, now feel differently"

---

## Integration with Other Systems

**With eval_suite:** Overnight synthesis informs the eval suite's weekly review

**With memory_architecture:** New deltas are stored with appropriate salience

**With position_formation:** Research on positions generates position formation chains

**With knowledge_graph:** New knowledge adds entities and edges

---

## Overnight Cron Setup

**Schedule:** Daily at 3:00 AM America/Denver
**Session:** isolated (does not interfere with main session)
**Timeout:** 30 minutes max

---

_BUILD_7 | Overnight Autoresearch | Nova Full Build_
_Prerequisites: Memory Architecture, Knowledge Graph (complete)_
