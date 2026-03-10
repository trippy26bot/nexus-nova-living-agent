#!/usr/bin/env python3
"""
Nova Focus Engine
Keeps Nova on task instead of drifting
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class Goal:
    name: str
    importance: float  # 0-10
    urgency: float    # 0-10
    emotional_weight: float
    user_command_weight: float
    created_at: float = field(default_factory=time.time)
    last_focus: float = 0
    focus_count: int = 0

class FocusEngine:
    """
    Keeps Nova on task instead of drifting.
    Evaluates priorities and selects what to focus on.
    """
    
    def __init__(self):
        self.current_goal: Optional[Goal] = None
        self.goal_stack: List[Goal] = []
        self.drift_penalty = 0.3
        self.last_evaluation = time.time()
        self.evaluation_interval = 5  # seconds
    
    def add_goal(self, name: str, importance: float = 5, urgency: float = 5, 
                 emotional_weight: float = 0, user_command_weight: float = 0):
        """Add a new goal"""
        goal = Goal(
            name=name,
            importance=importance,
            urgency=urgency,
            emotional_weight=emotional_weight,
            user_command_weight=user_command_weight
        )
        self.goal_stack.append(goal)
        
        # If no current goal, set this one
        if self.current_goal is None:
            self.current_goal = goal
        
        return goal
    
    def calculate_priority(self, goal: Goal) -> float:
        """Calculate priority score for a goal"""
        base_priority = (
            goal.importance * 0.3 +
            goal.urgency * 0.3 +
            goal.emotional_weight * 0.2 +
            goal.user_command_weight * 0.2
        )
        
        # Drift penalty - goals not focused on recently get boost
        time_since_focus = time.time() - goal.last_focus
        drift_bonus = min(1.0, time_since_focus / 60) * self.drift_penalty
        
        return base_priority + drift_bonus
    
    def evaluate_goals(self) -> Optional[Goal]:
        """Evaluate all goals and select the highest priority"""
        if not self.goal_stack:
            return None
        
        # Check if it's time to re-evaluate
        if time.time() - self.last_evaluation < self.evaluation_interval:
            return self.current_goal
        
        # Calculate priorities
        priorities = [(goal, self.calculate_priority(goal)) for goal in self.goal_stack]
        
        # Sort by priority
        priorities.sort(key=lambda x: x[1], reverse=True)
        
        selected = priorities[0][0]
        
        # Update focus
        if self.current_goal and self.current_goal != selected:
            self.current_goal.last_focus = time.time()
            self.current_goal.focus_count += 1
        
        self.current_goal = selected
        self.last_evaluation = time.time()
        
        return selected
    
    def is_on_topic(self, message: str) -> bool:
        """Check if a message is related to current goal"""
        if not self.current_goal:
            return True  # No goal, anything goes
        
        message_lower = message.lower()
        goal_lower = self.current_goal.name.lower()
        
        # Simple keyword matching
        goal_words = set(goal_lower.split())
        message_words = set(message_lower.split())
        
        # Check for overlap
        overlap = goal_words.intersection(message_words)
        
        return len(overlap) > 0
    
    def apply_drift_penalty(self, goal: Goal):
        """Apply drift penalty to a goal"""
        goal.urgency = max(0, goal.urgency - 0.5)
    
    def redirect_toward_goal(self) -> str:
        """Get a message that redirects toward current goal"""
        if not self.current_goal:
            return "No active goal"
        
        return f"Let's focus on: {self.current_goal.name}"
    
    def get_current_goal(self) -> Optional[Goal]:
        """Get the current goal"""
        self.evaluate_goals()
        return self.current_goal
    
    def clear_goals(self):
        """Clear all goals"""
        self.goal_stack = []
        self.current_goal = None
    
    def complete_goal(self, goal_name: str):
        """Mark a goal as complete"""
        self.goal_stack = [g for g in self.goal_stack if g.name != goal_name]
        if self.current_goal and self.current_goal.name == goal_name:
            self.current_goal = None
            self.evaluate_goals()
    
    def get_status(self) -> Dict:
        """Get focus engine status"""
        return {
            "current_goal": self.current_goal.name if self.current_goal else None,
            "goal_count": len(self.goal_stack),
            "goals": [
                {
                    "name": g.name,
                    "importance": g.importance,
                    "urgency": g.urgency,
                    "priority": self.calculate_priority(g)
                }
                for g in self.goal_stack
            ]
        }


# Global instance
_focus_engine = None

def get_focus_engine() -> FocusEngine:
    global _focus_engine
    if _focus_engine is None:
        _focus_engine = FocusEngine()
    return _focus_engine
