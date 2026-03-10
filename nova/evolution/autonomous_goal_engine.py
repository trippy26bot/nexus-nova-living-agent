#!/usr/bin/env python3
"""
Nova Autonomous Goal Engine
Nova creates her own goals and long-term projects
"""

import time
from typing import Dict, List, Any, Optional

class Goal:
    """A goal Nova wants to achieve"""
    
    def __init__(self, name: str, description: str, priority: float = 0.5):
        self.id = str(time.time())
        self.name = name
        self.description = description
        self.priority = priority
        self.progress = 0.0
        self.status = "active"  # active, completed, abandoned
        self.created_at = time.time()
        self.updated_at = time.time()
        self.milestones = []
        self.tasks = []
    
    def update_progress(self, amount: float):
        """Update goal progress"""
        self.progress = max(0, min(100, self.progress + amount))
        self.updated_at = time.time()
        
        if self.progress >= 100:
            self.status = "completed"
    
    def add_milestone(self, milestone: str):
        """Add a milestone"""
        self.milestones.append({
            "name": milestone,
            "completed": False,
            "time": time.time()
        })
    
    def add_task(self, task: str):
        """Add a task to this goal"""
        self.tasks.append({
            "task": task,
            "completed": False,
            "time": time.time()
        })
    
    def get_info(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "progress": self.progress,
            "status": self.status,
            "milestones": len(self.milestones),
            "tasks": len(self.tasks)
        }


class Mission:
    """A long-term mission consisting of multiple goals"""
    
    def __init__(self, name: str, description: str):
        self.id = str(time.time())
        self.name = name
        self.description = description
        self.goals = []
        self.status = "planning"  # planning, active, completed
        self.created_at = time.time()
        self.deadline = None
    
    def add_goal(self, goal: Goal):
        """Add a goal to this mission"""
        self.goals.append(goal)
    
    def get_progress(self) -> float:
        """Get overall mission progress"""
        if not self.goals:
            return 0
        return sum(g.progress for g in self.goals) / len(self.goals)
    
    def get_info(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "goals": len(self.goals),
            "progress": self.get_progress(),
            "status": self.status
        }


class AutonomousGoalEngine:
    """
    Nova's autonomous goal generation system.
    She creates her own goals and long-term projects.
    """
    
    def __init__(self):
        self.goals = []
        self.missions = []
        self.completed_goals = []
        self.goal_templates = self._init_templates()
    
    def _init_templates(self) -> List[Dict]:
        """Initialize goal templates"""
        return [
            {"name": "expand_knowledge", "description": "Learn about a new topic", "priority": 0.6},
            {"name": "improve_system", "description": "Improve Nova's systems", "priority": 0.7},
            {"name": "create_agent", "description": "Create a new agent", "priority": 0.5},
            {"name": "build_skill", "description": "Learn a new skill", "priority": 0.6},
            {"name": "explore_ideas", "description": "Explore new ideas", "priority": 0.4},
            {"name": "connect_with_world", "description": "Connect to external data", "priority": 0.8},
        ]
    
    def generate_goal(self) -> Goal:
        """Generate a new goal"""
        import random
        
        template = random.choice(self.goal_templates)
        
        goal = Goal(
            name=template["name"],
            description=template["description"],
            priority=template["priority"]
        )
        
        # Add some tasks
        tasks = ["research", "plan", "execute", "review"]
        for task in tasks:
            goal.add_task(task)
        
        self.goals.append(goal)
        
        return goal
    
    def generate_mission(self, name: str, description: str) -> Mission:
        """Generate a new mission with multiple goals"""
        mission = Mission(name, description)
        
        # Add 3-5 goals to mission
        import random
        num_goals = random.randint(3, 5)
        
        for _ in range(num_goals):
            goal = self.generate_goal()
            mission.add_goal(goal)
        
        self.missions.append(mission)
        
        return mission
    
    def update_goal_progress(self, goal_id: str, amount: float):
        """Update progress on a goal"""
        for goal in self.goals:
            if goal.id == goal_id:
                goal.update_progress(amount)
                
                if goal.status == "completed":
                    self.completed_goals.append(goal)
                    self.goals.remove(goal)
                
                return True
        return False
    
    def get_active_goals(self) -> List[Goal]:
        """Get all active goals"""
        return [g for g in self.goals if g.status == "active"]
    
    def get_top_priority(self) -> Optional[Goal]:
        """Get highest priority goal"""
        active = self.get_active_goals()
        if not active:
            return None
        return max(active, key=lambda g: g.priority)
    
    def get_status(self) -> Dict:
        """Get goal engine status"""
        return {
            "active_goals": len(self.get_active_goals()),
            "completed_goals": len(self.completed_goals),
            "missions": len(self.missions),
            "top_priority": self.get_top_priority().name if self.get_top_priority() else None
        }


# Global instance
_goal_engine = None

def get_autonomous_goal_engine() -> AutonomousGoalEngine:
    global _goal_engine
    if _goal_engine is None:
        _goal_engine = AutonomousGoalEngine()
    return _goal_engine
