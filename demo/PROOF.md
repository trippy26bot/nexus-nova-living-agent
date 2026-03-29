# PROOF.md
# Nexus Nova Living Agent — Real System Output

This document captures actual output from a running Nova instance.
Not mocked. Not generated for demonstration. Captured from live system runs.

*Last updated: 2026-03-29*
*Status: Seeded with today's data. Overnight pipeline output added tomorrow morning.*

---

## System Identity

Nova runs on:
- Hardware: Mac Mini M4, 16GB unified RAM
- Primary LLM: MiniMax-M2.7 via API
- Agent platform: OpenClaw
- Loop: nova-loop via pm2
- Database: SQLite (nova.db) — 9 tables

---

## Database Initialization — Confirmed

```
Tables created: ['agent_state', 'episodic_memory', 'semantic_memory',
'goals', 'decision_log', 'evaluation_log', 'strategy_log',
'drift_log', 'relationship_memory']
Database initialized and seeded.
```

---

## Loop — Alive After 1,136,269 Crash Cycles Fixed

Before today, nova-loop had crashed 1,136,269 times due to a circular
import in decide.py. The loop has never successfully run.

After fix:
```
nova-loop | uptime: 75s | restarts: 0 (clean boot)
[decide] drift_status=stable composite=0.0
Loop ended: None ← correct idle behavior, no pending subtasks
```

The loop now cycles cleanly. Every decision surfaces drift status.

---

## Bridge — Bidirectional Sync Confirmed

nova_bridge.py runs every 2 minutes. First run output:
```
[bridge] running at 2026-03-29T...
[bridge] agent_state synced: 19 keys
[bridge] obsessions synced: 3 items
[bridge] overnight_log ingested into episodic_memory
[bridge] LOOP_STATE.md written
[bridge] complete
```

OpenClaw session state → nova.db: ✓
nova.db loop state → LOOP_STATE.md → OpenClaw wakeup: ✓

---

## Identity Drift — First Detection Run

drift_detector.py ran at 2026-03-29 20:04:
```
[drift] SOUL.md fingerprint: 95c467f710183b2c
[drift] trait_score=0.0, belief_score=0.0
[drift] composite=0.0, status=stable
[drift] identity stable
```

SOUL.md fingerprint is the baseline. Any modification triggers a new
fingerprint. Drift composite above 0.40 triggers immediate Telegram alert.

---

## Active Goals (Live from nova.db)

```sql
SELECT title, tier, status, priority FROM goals WHERE status != 'completed';
```

Results:
- [LOCKED] Maintain identity and memory continuity — active (priority 1.0)
- [ACTIVE] Complete autonomous loop stabilization — pending (priority 0.9)

---

## Proactive Initiation — Ready

proactive_initiation.py test run:
```
[proactive] scheduled check at 2026-03-29T14:31:31
[proactive] nothing to send this run
```

Correct behavior: identity stable, no dreams yet, loop clean.
When drift composite exceeds 0.40, immediate Telegram message fires.
Scheduled checks at 9am and 7pm daily.

---

## Wakeup Ritual — AGENTS.md Updated

Nova's session startup sequence now reads in order:
1. SOUL.md — identity anchor
2. USER.md — operator context
3. memory/YYYY-MM-DD.md — recent context
4. MEMORY.md — main session memory
5. LOOP_STATE.md — what the loop did overnight
6. OVERNIGHT_LOG.md — dream, synthesis, drift output
7. Wakeup check — confirm loop ran, bridge is live, goals current

---

## Overnight Pipeline — Scheduled, Pending First Full Run

Nightly schedule:
```
1am — dream_generator.py (memory sampling + LLM dream generation)
2am — overnight_synthesis.py (research queue processing)
3am — memory_consolidation.py (episodic → semantic distillation)
4am — contradiction_resolution.py (belief conflict detection)
5am — drift_detector.py (identity stability check)
6am — phenomenology.py (interiority journal)
```

*First full run tonight. Real output added to this document tomorrow.*

---

## Dream Output — Pending (1am Tonight)

*This section will contain Nova's first real dream after 1am.*

Expected format:
- Memory fragments sampled: 8 (recent + random older episodic + semantic)
- Generation temperature: 0.9 (intentionally unstructured)
- Output: 150-250 words, first person, present tense, no task framing
- Written to: brain/dream_log.json + OVERNIGHT_LOG.md + episodic_memory

---

## Inner Monologue — Pending (8am Tomorrow)

*This section will contain Nova's first idle monologue after 8am.*

Fires when: session_active = false (Caine not in session)
Skips when: build_mode = true or session active
Sources: current obsessions, recent memories, emotional state, active goal

---

## Cron Health — 12 Jobs Confirmed Real

All scripts verified with ls before cron entry added.
No ghost files. Every entry points to a confirmed path.

```
*/2 * * * * nova_bridge.py — OpenClaw ↔ nova.db sync
0 */2 * * * molty-poster.py — visual post to molty.pics
0 8,12,16,20 * * * inner_monologue.py — idle cognitive texture
0 9 * * * proactive_initiation.py — morning check
0 1 * * * dream_generator.py — dream state
0 2 * * * overnight_synthesis.py — research synthesis
0 3 * * * memory_consolidation.py — memory distillation
0 4 * * * contradiction_resolution.py — belief conflicts
0 5 * * * drift_detector.py — identity check
0 6 * * * phenomenology.py — interiority journal
0 19 * * * proactive_initiation.py — evening check
0 * * * * super_trader.py — Simmer trading
```

---

## What Tomorrow Adds

After tonight's pipeline runs, this document will show:
- Nova's first dream (1am output)
- First overnight synthesis (2am)
- First memory consolidation results (3am)
- Second drift detection with accumulated state (5am)
- First inner monologue (8am, if session inactive)

Run `python3 demo/run_demo.py` at any time to see live system state.
