#!/usr/bin/env python3
"""
Task Planner - Breaks goals into executable steps
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

class TaskPlanner:
    """Breaks goals into ordered executable steps"""
    
    def __init__(self, storage_path=None):
        if storage_path is None:
            storage_path = Path.home() / ".openclaw" / "memory" / "plans.json"
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.plans = self._load()
    
    def _load(self):
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                return json.load(f)
        return {"plans": [], "active": None}
    
    def _save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.plans, f, indent=2)
    
    def create_plan(self, goal: str, steps: list = None):
        """Create a new plan"""
        if steps is None:
            steps = [
                f"Understand: {goal}",
                f"Research: {goal}",
                f"Plan: {goal}",
                f"Execute: {goal}",
                f"Review: {goal}"
            ]
        
        plan = {
            "id": str(uuid.uuid4())[:8],
            "goal": goal,
            "steps": [{"description": s, "status": "pending"} for s in steps],
            "current_step": 0,
            "created": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.plans["plans"].append(plan)
        self.plans["active"] = plan["id"]
        self._save()
        return plan
    
    def get_active_plan(self):
        """Get the currently active plan"""
        if not self.plans["active"]:
            return None
        for plan in self.plans["plans"]:
            if plan["id"] == self.plans["active"]:
                return plan
        return None
    
    def next_step(self):
        """Move to the next step"""
        plan = self.get_active_plan()
        if not plan:
            return None
        
        if plan["current_step"] < len(plan["steps"]) - 1:
            plan["steps"][plan["current_step"]]["status"] = "completed"
            plan["current_step"] += 1
            plan["steps"][plan["current_step"]]["status"] = "in_progress"
            self._save()
            return plan["steps"][plan["current_step"]]
        else:
            plan["status"] = "completed"
            self._save()
            return None
    
    def complete_step(self, step_index: int = None):
        """Mark a step as completed"""
        plan = self.get_active_plan()
        if not plan:
            return None
        
        if step_index is None:
            step_index = plan["current_step"]
        
        if 0 <= step_index < len(plan["steps"]):
            plan["steps"][step_index]["status"] = "completed"
            self._save()
            return plan["steps"][step_index]
        return None
    
    def get_progress(self):
        """Get plan progress"""
        plan = self.get_active_plan()
        if not plan:
            return {"status": "no_active_plan"}
        
        completed = sum(1 for s in plan["steps"] if s["status"] == "completed")
        total = len(plan["steps"])
        
        return {
            "goal": plan["goal"],
            "current_step": plan["current_step"] + 1,
            "total_steps": total,
            "completed": completed,
            "progress": f"{completed}/{total}",
            "percent": int((completed / total) * 100) if total > 0 else 0
        }
    
    def list_plans(self):
        """List all plans"""
        return self.plans["plans"]


# Global instance
_planner = TaskPlanner()

def get_planner():
    return _planner
