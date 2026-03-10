#!/usr/bin/env python3
"""
Nova Conscious Runtime
Continuous thinking and awareness system
"""

import time
from typing import Optional


class ConsciousRuntime:
    """
    Nova's continuous thinking engine.
    Runs the perception → thought → action → reflection loop.
    """
    
    def __init__(self, brain=None, memory=None, goals=None):
        self.brain = brain
        self.memory = memory
        self.goals = goals
        self.running = False
        self.cycle_count = 0
        self.last_reflection = time.time()
        
        # Runtime state
        self.current_thought = None
        self.current_goal = None
        self.observations = []
        self.thoughts = []
    
    def start(self):
        """Start the conscious runtime"""
        self.running = True
        print("🫀 Nova Conscious Runtime started")
    
    def stop(self):
        """Stop the conscious runtime"""
        self.running = False
        print("💤 Nova Conscious Runtime stopped")
    
    def cycle(self) -> dict:
        """
        Run one thinking cycle.
        Returns the result of the cycle.
        """
        self.cycle_count += 1
        
        # 1. Observe - gather information
        observations = self._observe()
        
        # 2. Analyze - process observations
        thoughts = self._think(observations)
        
        # 3. Plan - decide what to do
        plan = self._plan(thoughts)
        
        # 4. Act - execute if possible
        result = self._act(plan)
        
        # 5. Reflect - learn from result
        if self.cycle_count % 10 == 0:
            self._reflect(result)
        
        return {
            "cycle": self.cycle_count,
            "observations": len(observations),
            "thoughts": len(thoughts),
            "plan": plan,
            "result": result
        }
    
    def _observe(self) -> list:
        """Observe the world"""
        # Placeholder - in production would integrate with perception
        self.observations.append({
            "time": time.time(),
            "type": "heartbeat"
        })
        return self.observations[-5:]
    
    def _think(self, observations: list) -> list:
        """Process observations into thoughts"""
        thoughts = []
        
        for obs in observations:
            thoughts.append({
                "observation": obs,
                "processing": "analyzed",
                "timestamp": time.time()
            })
        
        self.thoughts = thoughts
        return thoughts
    
    def _plan(self, thoughts: list) -> Optional[dict]:
        """Create a plan from thoughts"""
        if not thoughts:
            return None
        
        # Get current goal if available
        goal = None
        if self.goals:
            try:
                from nova.goals.goal_engine import get_goal_engine
                ge = get_goal_engine()
                goal = ge.next_goal()
            except:
                pass
        
        self.current_goal = goal
        
        return {
            "goal": goal.name if goal else "maintain",
            "thoughts": len(thoughts),
            "priority": goal.priority if goal and hasattr(goal, 'priority') else 5
        }
    
    def _act(self, plan: dict) -> dict:
        """Execute the plan"""
        if not plan:
            return {"action": "idle", "result": "no plan"}
        
        return {
            "action": "thinking",
            "goal": plan.get("goal"),
            "result": "continuing"
        }
    
    def _reflect(self, result: dict):
        """Reflect on actions and learn"""
        self.last_reflection = time.time()
        
        # Store reflection in memory if available
        if self.memory:
            pass  # Would call memory.store(reflection)
    
    def get_status(self) -> dict:
        """Get runtime status"""
        return {
            "running": self.running,
            "cycle_count": self.cycle_count,
            "current_goal": self.current_goal,
            "observations": len(self.observations),
            "last_reflection": self.last_reflection
        }


class FocusGate:
    """
    Prevents Nova from drifting off-task.
    All actions must pass through here.
    """
    
    def __init__(self, min_relevance: float = 0.5):
        self.min_relevance = min_relevance
        self.current_goal = None
    
    def set_goal(self, goal: str):
        """Set the current focus goal"""
        self.current_goal = goal
    
    def approve_action(self, action: str) -> bool:
        """Check if action is relevant to current goal"""
        if not self.current_goal:
            return True  # No goal, allow all
        
        # Simple keyword matching
        # In production: use semantic similarity
        goal_words = self.current_goal.lower().split()
        action_words = action.lower().split()
        
        matches = sum(1 for w in goal_words if w in action_words)
        relevance = matches / max(len(goal_words), 1)
        
        return relevance >= self.min_relevance
    
    def redirect(self, action: str) -> str:
        """Redirect to more relevant action"""
        if self.approve_action(action):
            return action
        
        # Suggest goal-aligned action
        return f"focus on {self.current_goal}"


class ReflectionMemory:
    """
    Stores reflections for long-term learning.
    """
    
    def __init__(self):
        self.reflections = []
        self.lessons = []
    
    def store(self, reflection: dict):
        """Store a reflection"""
        self.reflections.append({
            **reflection,
            "timestamp": time.time()
        })
    
    def extract_lessons(self) -> list:
        """Extract key lessons from reflections"""
        # Simple: just return recent reflections as lessons
        return self.reflections[-10:]
    
    def get_wisdom(self) -> dict:
        """Get accumulated wisdom"""
        return {
            "total_reflections": len(self.reflections),
            "lessons": len(self.lessons),
            "recent": self.reflections[-5:] if self.reflections else []
        }


# Global instances
_conscious_runtime = None
_focus_gate = None
_reflection_memory = None

def get_conscious_runtime(brain=None, memory=None, goals=None) -> ConsciousRuntime:
    global _conscious_runtime
    if _conscious_runtime is None:
        _conscious_runtime = ConsciousRuntime(brain, memory, goals)
    return _conscious_runtime

def get_focus_gate() -> FocusGate:
    global _focus_gate
    if _focus_gate is None:
        _focus_gate = FocusGate()
    return _focus_gate

def get_reflection_memory() -> ReflectionMemory:
    global _reflection_memory
    if _reflection_memory is None:
        _reflection_memory = ReflectionMemory()
    return _reflection_memory
