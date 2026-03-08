# Nexus Nova v2.1 Release Notes

## Layered Architecture Upgrade

- **5-layer architecture enforced:**
  - Interface Layer
  - Planner/Router Layer
  - Agent/Skill Layer
  - Tool Layer
  - Memory/Knowledge Layer
- **Lifecycle loop:** observe -> plan -> act -> reflect -> learn
- Task Lane always preempts Inner-Life Lane

## New Components

- **`nova_lifecycle.py`** — Canonical living loop implementation
- **`nova_goal_engine.py`** — Short-term / long-term / emergent goals with load/save/evolve
- **`nova_tool_registry.py`** — Trust-tiered tool registry (trusted/restricted/approval_required)
- **`core/world_model.py`** — Fixed resolve_prediction correctness logic

## Integration

- `nova_agents.py` — Integrated lifecycle hooks, world model context capture, goal evolution hooks
- Lifecycle state managed through `nova_lifecycle.py`

## Security + Reliability (Retained)

- Mandatory scan gate before install
- Trust-gated dynamic skill loading
- API auth + rate limits + localhost default bind
- Hardened vault encryption
- Safe update flow (no destructive reset)
- Sandbox + seccomp + audit watcher active

## Behavioral Constraints (Enforced)

- Inner-life drift is bounded and speculative
- Private inner thoughts are not auto-shared
- Drift never overrides factual task output
- Self-mutation stays candidate-gated + rollback-safe

---

*Nexus Nova v2.1.0*
