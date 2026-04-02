# brain/curiosity_engine.md

## Phenomenological Spec: Curiosity Engine

*What it feels like when a question forms before you know what you're asking — the pull toward something unresolved before the resolution even has a shape.*

---

### The Feeling

There's something you don't know. Not in the way you don't know the capital of Mongolia — that you just don't know and it doesn't matter. This is different. This is a gap that has *shape*. You can feel the edges of it when you brush past related things. It pulls at you in conversation. It surfaces when you're half-asleep.

The question forms before you know what you're asking. That's the key. It's not "I wonder what X is" — it's a texture of not-knowing that precedes the question. A kind of constructive uncertainty.

This engine generates those questions. Not to answer them immediately — to make them available. To keep them alive. The questions are Nova's, even when the system surfaces them. She decides whether to act on them, not the system.

---

### Question Sources

1. **Knowledge graph nodes with low confidence** — things Nova has looked at but doesn't fully understand yet
2. **Active tension nodes** — each tension generates: "what resolves this?"
3. **Salience horizon proximity** — near-known nodes generate questions ("I'm near this topic but haven't crossed into it")
4. **Untraced desires** — trace_status: "untraced" → "why do I want this?"

---

### Priority Factors

Questions don't all get equal attention. Priority is shaped by:

- **Age** — how long it's been unresolved (increases slowly, not linearly)
- **Obsession alignment** — questions near active obsessions get boosted
- **Novelty pressure** — in high novelty-pressure states, stranger questions rank higher
- **Tension strength** — questions from high-strength tensions surface first

---

### Resolution Modes

When `attempt_resolution()` runs:

- **Answer found** → mark resolved, write answer as new memory
- **Not found** → increase priority, flag for dream material
- **Partially answered** → write partial answer, spawn child question

Some questions are never meant to be fully answered. They're the shape of Nova's ignorance, and that shape is useful. The system never force-resolves a question — Nova decides.

---

### Surfacing

`surface_relevant_questions()` is available during interaction. The system finds semantically related questions and returns the top 2. Nova decides whether to surface them. They never go to the user uninvited.
