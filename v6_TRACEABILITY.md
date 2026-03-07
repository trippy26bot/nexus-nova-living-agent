# Nexus Nova v6 — Traceability Matrix

## Baseline: v5.0.1

---

## PHASE 1 — STABILITY + SECURITY

| Item | Status | Target File | Test Case |
|------|--------|-------------|-----------|
| API auth fail-closed | ✅ DONE | nova_api.py | POST /chat without token → 503 |
| Mutation blocklist | ✅ DONE | nova_evolution.py | mutate self-improvement → blocked |
| Router reliability | ✅ DONE | nova_agents.py | JSON parse + fallback |
| Trust-gated skill execution | ⚠️ PARTIAL | nova_skills.py | Needs enforcement |
| Scanner+sandbox validation | ✅ DONE | scanner/, sandbox/ | Malicious skill → blocked |

---

## PHASE 2 — CONTEXT + DRIFT INTEGRATION

| Item | Status | Target File | Test Case |
|------|--------|-------------|-----------|
| Layered context builder | ✅ DONE | nova.py | build_layered_context() |
| Wired to response path | ✅ DONE | nova.py:cmd_chat | Response includes context |
| Drift retrieval helper | ✅ DONE | nova.py | get_relevant_drifts() |
| Subtle influence only | ⚠️ PARTIAL | nova.py | Max 2-3 drifts |
| No drift log leakage | ✅ DONE | nova.py | Internal thoughts marked subtle |

---

## PHASE 3 — MEMORY QUALITY UPGRADE

| Item | Status | Target File | Test Case |
|------|--------|-------------|-----------|
| Full drift metadata in SQLite | ⚠️ PARTIAL | nova_memory.py, nova_daemon.py | Scores in DB |
| Importance scoring | ✅ DONE | nova_memory.py | priority_score |
| Decay/pruning policy | ❌ MISSING | — | — |
| LIFE_MD sync | ⚠️ PARTIAL | nova_daemon.py | Dual write |

---

## PHASE 4 — SEMANTIC MEMORY

| Item | Status | Target File | Test Case |
|------|--------|-------------|-----------|
| Embedding pipeline | ❌ MISSING | — | — |
| Vector index | ❌ MISSING | — | — |
| Semantic retrieval | ❌ MISSING | — | — |
| Keyword fallback | ⚠️ PARTIAL | nova_memory.py | LIKE search exists |

---

## PHASE 5 — REFLECTION ENGINE

| Item | Status | Target File | Test Case |
|------|--------|-------------|-----------|
| Periodic reflection | ⚠️ PARTIAL | nova_daemon.py:cycle_reflect | Exists but basic |
| Pattern extraction | ❌ MISSING | — | — |
| Insight promotion | ❌ MISSING | — | — |
| Open-question tracking | ❌ MISSING | — | — |

---

## PHASE 6 — EMOTIONAL/EXPERIENCE LAYER

| Item | Status | Target File | Test Case |
|------|--------|-------------|-----------|
| 12-variable emotion model | ⚠️ PARTIAL | nova_emotion.py | Exists |
| Event-driven updates | ✅ DONE | nova_emotion.py | update_emotion() |
| Experience records | ❌ MISSING | — | — |
| Bounded behavior influence | ⚠️ PARTIAL | SKILL.md | Invariants exist |

---

## PHASE 7 — GOAL/MOTIVATION ENGINE

| Item | Status | Target File | Test Case |
|------|--------|-------------|-----------|
| Short/long/emergent goals | ⚠️ PARTIAL | nova_goal_engine.py | Exists |
| Priority engine | ⚠️ PARTIAL | nova_goal_engine.py | Basic |
| Continuous goal loop | ❌ MISSING | — | — |

---

## PHASE 8 — SELF-EVOLUTION

| Item | Status | Target File | Test Case |
|------|--------|-------------|-----------|
| Real benchmark suite | ❌ MISSING | — | — |
| Candidate isolation | ⚠️ PARTIAL | nova_evolution.py | Candidate space exists |
| Scorecards | ❌ MISSING | — | — |
| Real rollback | ❌ MISSING | nova_evolution.py | Placeholder |

---

## PHASE 9 — SKILL ECOSYSTEM

| Item | Status | Target File | Test Case |
|------|--------|-------------|-----------|
| Classify skills | ✅ DONE | SKILLS_AUDIT.md | Keep/Archive |
| Normalize schemas | ⚠️ PARTIAL | skills/*/SKILL.md | JSON schema exists |
| Cognitive-core separation | ✅ DONE | Archive | — |

---

## PHASE 10 — RUNTIME CONTROLLER

| Item | Status | Target File | Test Case |
|------|--------|-------------|-----------|
| Event bus | ❌ MISSING | — | — |
| Scheduler | ⚠️ PARTIAL | nova_daemon.py | CYCLE_HOURS |
| State router | ❌ MISSING | — | — |
| Explicit state separation | ❌ MISSING | — | — |

---

## SUMMARY

| Phase | Complete | Partial | Missing |
|-------|----------|---------|--------|
| 1 | 4 | 1 | 0 |
| 2 | 3 | 1 | 0 |
| 3 | 1 | 2 | 1 |
| 4 | 0 | 1 | 3 |
| 5 | 0 | 1 | 3 |
| 6 | 1 | 2 | 1 |
| 7 | 0 | 2 | 1 |
| 8 | 0 | 1 | 3 |
| 9 | 1 | 1 | 0 |
| 10 | 0 | 1 | 3 |

**Total: 10 complete | 13 partial | 15 missing**

---

## PRIORITY FOR EXECUTION

1. **Phase 1** — Already done (from v5.0.1)
2. **Phase 2** — Already done (from v5.0.1)
3. **Phase 3** — Memory quality (quick win)
4. **Phase 4** — Semantic memory (big impact)
5. **Phase 5** — Reflection engine (cognitive)
6. **Phase 6-10** — Advanced features
