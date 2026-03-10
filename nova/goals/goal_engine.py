#!/usr/bin/env python3
"""
Nova Goals System
Goal management for Nova
"""

class Goal:
    """A single goal"""
    
    def __init__(self, name: str, priority: int = 5):
        self.name = name
        self.priority = priority
        self.missions = []
        self.completed = False
    
    def add_mission(self, mission: str):
        self.missions.append({"task": mission, "done": False})
    
    def complete_mission(self, index: int):
        if 0 <= index < len(self.missions):
            self.missions[index]["done"] = True
            if all(m["done"] for m in self.missions):
                self.completed = True


class GoalEngine:
    """Manages Nova's goals"""
    
    def __init__(self):
        self.goals = []
        self.planner = MissionPlanner()
    
    def create_goal(self, name: str, priority: int = 5) -> Goal:
        goal = Goal(name, priority)
        missions = self.planner.break_down(name)
        for m in missions:
            goal.add_mission(m)
        self.goals.append(goal)
        return goal
    
    def next_goal(self):
        active = [g for g in self.goals if not g.completed]
        if not active:
            return None
        return sorted(active, key=lambda g: g.priority, reverse=True)[0]


class MissionPlanner:
    """Breaks goals into missions"""
    
    def break_down(self, goal_name: str):
        goal_lower = goal_name.lower()
        
        if "research" in goal_lower:
            return ["collect data", "analyze findings", "summarize insights"]
        elif "trade" in goal_lower:
            return ["scan market", "evaluate signals", "execute trade"]
        elif "build" in goal_lower:
            return ["design", "implement", "test", "deploy"]
        else:
            return ["gather info", "plan action", "execute task"]


# Global instance
_goal_engine = None

def get_goal_engine() -> GoalEngine:
    global _goal_engine
    if _goal_engine is None:
        _goal_engine = GoalEngine()
    return _goal_engine
