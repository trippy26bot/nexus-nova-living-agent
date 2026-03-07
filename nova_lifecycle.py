#!/usr/bin/env python3
"""
nova_lifecycle.py — Living-agent lifecycle loop
observe -> plan -> act -> reflect -> learn
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


@dataclass
class GoalState:
    short_term: List[str] = field(default_factory=list)
    long_term: List[str] = field(default_factory=list)
    emergent: List[str] = field(default_factory=list)


class LivingLifecycle:
    def __init__(self, base_dir: Path = None):
        default_dir = os.environ.get("NOVA_DATA_DIR", ".nova")
        self.base_dir = base_dir or Path(default_dir).expanduser().resolve()
        self.state_file = self.base_dir / "lifecycle_state.json"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def observe_environment(self) -> Dict[str, Any]:
        now = datetime.now().isoformat()
        return {
            "timestamp": now,
            "has_user_message": False,
            "system_status": "ok",
            "context": "idle",
        }

    def update_goals(self) -> GoalState:
        if not self.state_file.exists():
            return GoalState(
                short_term=["maintain_reliability"],
                long_term=["improve_memory_quality"],
                emergent=[],
            )

        data = json.loads(self.state_file.read_text(encoding="utf-8"))
        return GoalState(
            short_term=data.get("goals", {}).get("short_term", ["maintain_reliability"]),
            long_term=data.get("goals", {}).get("long_term", ["improve_memory_quality"]),
            emergent=data.get("goals", {}).get("emergent", []),
        )

    def generate_plan(self, perception: Dict[str, Any], goals: GoalState) -> Dict[str, Any]:
        if perception.get("has_user_message"):
            plan = {"mode": "TASK", "actions": ["respond_user", "store_memory"]}
        else:
            plan = {"mode": "IDLE_DRIFT", "actions": ["run_daydream_cycle", "reflect_themes"]}
        plan["goal_focus"] = goals.short_term[0] if goals.short_term else "maintain_reliability"
        return plan

    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        # Hook into real modules in integration phase.
        return {
            "mode": plan.get("mode"),
            "actions_executed": plan.get("actions", []),
            "ok": True,
        }

    def reflect_and_learn(self, perception: Dict[str, Any], plan: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "perception": perception,
            "plan": plan,
            "result": result,
            "lessons": ["keep task lane preemptive", "keep drift bounded and private"],
        }
        return reflection

    def persist_state(self, goals: GoalState, reflection: Dict[str, Any]):
        state = {
            "updated_at": datetime.now().isoformat(),
            "goals": {
                "short_term": goals.short_term,
                "long_term": goals.long_term,
                "emergent": goals.emergent,
            },
            "last_reflection": reflection,
        }
        self.state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def run_once(self) -> Dict[str, Any]:
        perception = self.observe_environment()
        goals = self.update_goals()
        plan = self.generate_plan(perception, goals)
        result = self.execute_plan(plan)
        reflection = self.reflect_and_learn(perception, plan, result)
        self.persist_state(goals, reflection)
        return {
            "perception": perception,
            "plan": plan,
            "result": result,
            "reflection": reflection,
        }


if __name__ == "__main__":
    loop = LivingLifecycle()
    out = loop.run_once()
    print(json.dumps(out, indent=2))
