# Skills Audit Report

_Run this audit after any major update or skill installation._

---

## Classification Summary

| Category | Count |
|----------|-------|
| **Active** | 0 |
| **Archived** | 0 |
| **Deleted** | 0 |

_Update counts as skills are installed and audited._

---

## Active Skills

| Skill | Trust Level | Rationale |
|-------|-------------|-----------|
| core-memory | trusted | Core cognitive component |
| task-persistence | restricted | Task continuity |

---

## Archived Skills

| Skill | Rationale |
|-------|-----------|
| memory-management | Duplicates core memory module |
| self-improvement | Duplicates core evolution module |
| task-planning | Duplicates core planner |

---

## Core Separation

The framework keeps core functions in dedicated modules:

| Component | Location | Purpose |
|-----------|----------|---------|
| Planner | agents.py | Router, Planner, Executor |
| Memory | memory.py | Episodic, Semantic, Working |
| Reflection | daemon.py | Reflection cycles |
| Emotion | emotion.py | Emotion Engine |
| Goals | goal_engine.py | Goal management |
| Evolution | evolution.py | Self-improvement |

---

## Registry Enforcement

Skills are activated via the skills system:

```python
from skills.dispatcher import dispatch_skill

result = dispatch_skill("skill-name")
if result["allowed"]:
    # Execute skill
else:
    # Rejected - archived or not verified
```

---

## Trust Levels

| Level | Description |
|-------|-------------|
| trusted | Full access to memory and context |
| restricted | Limited access, requires approval for sensitive ops |
| approval_required | Must be explicitly approved per-use |

---

_Run a fresh audit after installing any new skills._
