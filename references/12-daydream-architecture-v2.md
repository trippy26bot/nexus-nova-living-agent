# Daydream Architecture v2

## Goal

Implement spontaneous inner-life processing that improves creativity and continuity without degrading task behavior.

## Lane Separation

- Task Lane: mandatory priority, low-latency, factual.
- Inner-Life Lane: idle/background only.

## Drift Cycle

1. Select mode from arbiter (`IDLE_DRIFT`, `REFLECTION`, `SILENT_REST`).
2. Sample 2-4 seed memories with:
- Topic diversity
- Emotional affinity
- Personalization boost
- Anti-rut penalty
3. Generate drift JSON (short length).
4. Critic scores with weighted composite.
5. Dedup check against recent accepted drifts.
6. Route to accept/store/drop.
7. Optional surfacing (cooldown + relevance gate).

## Mood and Emotion

Mood state controls seed selection and style, not truth.

Moods:
- curious
- wistful
- playful
- philosophical
- quiet

Signals:
- local time band
- recent conversation sentiment
- topic momentum
- session fatigue proxy

## Privacy and Journaling

- Keep private drift storage separate from shared/task memory.
- Store drifts encrypted at rest where supported.
- Add optional reflection journal that summarizes themes without exposing raw private thoughts.

## Suggested Defaults

- Idle jitter: 45-180 seconds
- Drift length: 40-140 tokens
- Post-response drift chance: 0.10-0.25
- Surfacing cooldown: 5-15 minutes
- Reflection cadence: every 6 accepted drifts

## Failure Handling

- Empty output: retry once with lower creativity.
- Critic timeout: store as pending, no surfacing.
- Toxic/unsafe output: drop and increment safety counter.
- Repeated failures: force `SILENT_REST` cooldown window.
