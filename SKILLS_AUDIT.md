# Skills Audit Report

**Date:** 2026-03-07
**Branch:** codex/nova-v6-all-in
**Version:** 1.0.0

---

## Classification Summary

| Category | Count |
|----------|-------|
| **Active** | 2 |
| **Archived** | 12 |
| **Deleted** | 0 |

---

## Active Skills

| Skill | Trust Level | Rationale |
|-------|-------------|-----------|
| nova-memory | trusted | Core cognitive component - memory essential |
| nova-task-persistence | restricted | Useful for task continuity |

---

## Archived Skills

| Skill | Rationale |
|-------|-----------|
| api-interaction | SKILL.md spec only, no runtime code |
| code-execution | SKILL.md spec only, security-sensitive |
| data-analysis | SKILL.md spec only |
| file-system | SKILL.md spec only, security-sensitive |
| knowledge-summarization | SKILL.md spec only |
| memory-management | Duplicates core nova_memory.py |
| report-generation | SKILL.md spec only |
| self-analysis | Duplicates reflection |
| self-improvement | Duplicates nova_evolution.py |
| skill-discovery | SKILL.md spec only |
| task-planning | Duplicates core planner (nova_agents.py) |
| web-research | SKILL.md spec only |

---

## Core Separation

Nova's cognitive architecture keeps core functions in dedicated modules:

| Component | Location | Purpose |
|----------|----------|---------|
| Planner | nova_agents.py | RouterAgent, PlannerAgent, ExecutorAgent |
| Memory | nova_memory.py | EpisodicMemory, SemanticMemory, WorkingMemory |
| Reflection | nova_daemon.py | cycle_reflect() |
| Emotion | nova_emotion.py | EmotionEngine |
| Goals | nova_goal_engine.py | GoalEngine |
| Evolution | nova_evolution.py | SkillMutationEngine |

---

## Registry Enforcement

Skills are activated via `skills/dispatcher.py`:

```python
from skills.dispatcher import dispatch_skill

result = dispatch_skill("nova-memory")
if result["allowed"]:
    # Execute skill
else:
    # Rejected - archived or deleted
```

---

## Trust Levels

| Level | Description |
|-------|-------------|
| trusted | Full access to memory and context |
| restricted | Limited access, requires approval for sensitive ops |
| approval_required | Must be explicitly approved per-use |

---

*Audit conducted by Nova - Phase 9 Complete*
