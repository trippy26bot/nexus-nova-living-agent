#!/usr/bin/env python3
"""
nova_goal_engine.py — goal management for living-agent loops.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict


@dataclass
class GoalSet:
    short_term: List[str] = field(default_factory=list)
    long_term: List[str] = field(default_factory=list)
    emergent: List[str] = field(default_factory=list)


class GoalEngine:
    def __init__(self, path: Path = None):
        base_dir = Path(os.environ.get("NOVA_DATA_DIR", ".nova")).expanduser().resolve()
        self.path = path or (base_dir / "goals_state.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> GoalSet:
        if not self.path.exists():
            return GoalSet(
                short_term=["maintain_task_reliability"],
                long_term=["improve_memory_continuity"],
                emergent=[],
            )
        data = json.loads(self.path.read_text(encoding="utf-8"))
        goals = data.get("goals", {})
        return GoalSet(
            short_term=goals.get("short_term", ["maintain_task_reliability"]),
            long_term=goals.get("long_term", ["improve_memory_continuity"]),
            emergent=goals.get("emergent", []),
        )

    def save(self, goals: GoalSet):
        payload = {
            "updated_at": datetime.now().isoformat(),
            "goals": {
                "short_term": goals.short_term,
                "long_term": goals.long_term,
                "emergent": goals.emergent,
            },
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def evolve_from_reflection(self, goals: GoalSet, reflection: Dict) -> GoalSet:
        """Minimal goal evolution heuristic."""
        lessons = reflection.get("lessons", []) if isinstance(reflection, dict) else []
        if any("reliability" in str(x).lower() for x in lessons):
            if "maintain_task_reliability" not in goals.short_term:
                goals.short_term.insert(0, "maintain_task_reliability")
        if any("memory" in str(x).lower() for x in lessons):
            if "improve_memory_continuity" not in goals.long_term:
                goals.long_term.append("improve_memory_continuity")
        return goals
