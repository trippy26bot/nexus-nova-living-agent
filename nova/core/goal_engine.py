#!/usr/bin/env python3
"""
Nova Goal Engine - Hierarchical goal management
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Optional

class Goal:
    def __init__(self, name: str, priority: int = 5, parent: str = None):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.priority = priority
        self.parent = parent
        self.status = "active"
        self.progress = 0
        self.subgoals = []
        self.created_at = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority,
            "parent": self.parent,
            "status": self.status,
            "progress": self.progress,
            "subgoals": self.subgoals
        }

class GoalEngine:
    """Manages hierarchical goal tree"""
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = Path.home() / ".openclaw" / "memory" / "goals.json"
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.goals = self._load_goals()
    
    def _load_goals(self):
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                data = json.load(f)
                return [Goal(g["name"], g["priority"], g.get("parent")) for g in data]
        return self._default_goals()
    
    def _default_goals(self):
        """Create default goals"""
        return [
            Goal("Help user succeed financially", priority=10),
            Goal("Improve Nova capabilities", priority=9),
            Goal("Maintain symbiotic partnership", priority=10),
            Goal("Analyze market opportunities", priority=7),
            Goal("Optimize strategies", priority=7),
            Goal("Improve memory organization", priority=6),
            Goal("Refine emotional models", priority=6)
        ]
    
    def _save_goals(self):
        with open(self.storage_path, 'w') as f:
            json.dump([g.to_dict() for g in self.goals], f, indent=2)
    
    def add_goal(self, name: str, priority: int = 5, parent: str = None):
        """Add new goal"""
        goal = Goal(name, priority, parent)
        self.goals.append(goal)
        self._save_goals()
        return goal
    
    def get_active(self) -> List[Dict]:
        """Get active goals sorted by priority"""
        active = [g for g in self.goals if g.status == "active"]
        active.sort(key=lambda g: g.priority, reverse=True)
        return [g.to_dict() for g in active[:5]]
    
    def complete_goal(self, goal_id: str):
        """Mark goal as completed"""
        for g in self.goals:
            if g.id == goal_id:
                g.status = "completed"
                g.progress = 100
                self._save_goals()
                return g
        return None
    
    def update_progress(self, goal_id: str, progress: int):
        """Update goal progress"""
        for g in self.goals:
            if g.id == goal_id:
                g.progress = min(100, max(0, progress))
                if g.progress >= 100:
                    g.status = "completed"
                self._save_goals()
                return g
        return None
    
    def get_top_goal(self) -> Optional[Dict]:
        """Get highest priority goal"""
        active = self.get_active()
        return active[0] if active else None


# Global instance
_goal_engine = None

def get_goal_engine():
    global _goal_engine
    if _goal_engine is None:
        _goal_engine = GoalEngine()
    return _goal_engine
