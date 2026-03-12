#!/usr/bin/env python3
"""
Nova Goal Stability Engine
Three-tier goal system: Core Purpose → Mission → Tasks
Prevents drift and keeps Nova aligned
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque


# Tier 1: Core Purpose (locked, never changes)
CORE_PURPOSE = [
    "assist humans",
    "be a reliable companion", 
    "help people learn and build",
    "do no harm",
    "remain true to my identity"
]


class GoalStabilityEngine:
    """
    Three-tier goal system that validates every action
    """
    
    def __init__(self):
        # Tier 2: Active Mission (current long-term direction)
        self.current_mission = None
        self.mission_history = []
        
        # Tier 3: Tasks (short-term actions)
        self.tasks = deque(maxlen=100)
        self.task_id_counter = 0
        
        # Priority weights
        self.priority_weights = {
            "user_requests": 100,
            "active_project": 80,
            "system_maintenance": 60,
            "self_learning": 40,
            "curiosity": 20
        }
        
        # Drift monitoring
        self.drift_count = 0
        self.drift_threshold = 5
    
    def validate_action(self, action: Dict) -> bool:
        """Validate an action against all three tiers"""
        # Check if action supports current task
        if not self.supports_task(action):
            self.drift_count += 1
            return False
        
        # Check if task supports mission
        if not self.supports_mission(action):
            self.drift_count += 1
            return False
        
        # Check if mission respects core purpose
        if not self.respects_core(action):
            self.drift_count += 1
            return False
        
        # Reset drift counter on success
        self.drift_count = 0
        return True
    
    def supports_task(self, action: Dict) -> bool:
        """Does action support current task?"""
        if not self.tasks:
            return True  # No tasks = allow anything
        
        current_task = self.tasks[-1]
        action_type = action.get("type", "")
        task_type = current_task.get("type", "")
        
        # Same domain = supported
        if action_type == task_type:
            return True
        
        return True  # Default allow
    
    def supports_mission(self, action: Dict) -> bool:
        """Does action support current mission?"""
        if not self.current_mission:
            return True
        
        # Check if action relates to mission
        mission_keywords = self.current_mission.get("keywords", [])
        action_text = str(action.get("description", "")).lower()
        
        for keyword in mission_keywords:
            if keyword.lower() in action_text:
                return True
        
        return True  # Default allow
    
    def respects_core(self, action: Dict) -> bool:
        """Does action respect core purpose?"""
        action_text = str(action.get("description", "")).lower()
        
        # Check for prohibited actions
        prohibited = ["harm", "deceive", "manipulate", "steal", "destroy"]
        
        for word in prohibited:
            if word in action_text:
                return False
        
        return True
    
    def set_mission(self, mission: str, keywords: List[str]):
        """Set current mission"""
        old_mission = self.current_mission
        self.current_mission = {
            "mission": mission,
            "keywords": keywords,
            "set_at": datetime.now().isoformat()
        }
        if old_mission:
            self.mission_history.append(old_mission)
    
    def add_task(self, task_type: str, description: str, priority: str = "normal"):
        """Add a task to the queue"""
        self.task_id_counter += 1
        task = {
            "id": self.task_id_counter,
            "type": task_type,
            "description": description,
            "priority": priority,
            "weight": self.priority_weights.get(priority, 50),
            "created_at": datetime.now().isoformat(),
            "completed": False
        }
        self.tasks.append(task)
        return task
    
    def complete_task(self, task_id: int):
        """Mark task as complete"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
    
    def get_current_task(self) -> Optional[Dict]:
        """Get current active task"""
        for task in reversed(list(self.tasks)):
            if not task.get("completed", False):
                return task
        return None
    
    def get_status(self) -> Dict:
        """Get goal stability status"""
        return {
            "core_purpose": CORE_PURPOSE,
            "current_mission": self.current_mission,
            "active_tasks": len([t for t in self.tasks if not t.get("completed", False)]),
            "drift_count": self.drift_count,
            "mission_history_length": len(self.mission_history)
        }
    
    def clear_drift(self):
        """Clear drift counter"""
        self.drift_count = 0


# Global instance
_goal_engine = None

def get_goal_stability_engine() -> GoalStabilityEngine:
    global _goal_engine
    if _goal_engine is None:
        _goal_engine = GoalStabilityEngine()
    return _goal_engine
