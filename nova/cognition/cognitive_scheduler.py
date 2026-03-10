#!/usr/bin/env python3
"""
Nova Cognitive Priority Scheduler
Only uses heavy systems when needed
"""

import time
from typing import Dict, List, Callable
from enum import Enum


class TaskPriority(Enum):
    """How complex is the task?"""
    FAST = 1      # Just look something up
    MEDIUM = 2    # Some thinking needed
    DEEP = 3     # Heavy reasoning


class TaskClassifier:
    """Figure out how much thinking a task needs"""
    
    # Keywords that trigger different levels
    FAST_KEYWORDS = ["check", "get", "what is", "price", "status", "scan"]
    MEDIUM_KEYWORDS = ["analyze", "should I", "evaluate", "compare", "find"]
    DEEP_KEYWORDS = ["design", "create", "strategy", "plan", "build"]
    
    def classify(self, task: str) -> TaskPriority:
        """Determine task complexity"""
        task_lower = task.lower()
        
        # Check for deep first
        if any(kw in task_lower for kw in self.DEEP_KEYWORDS):
            return TaskPriority.DEEP
        
        # Then medium
        if any(kw in task_lower for kw in self.MEDIUM_KEYWORDS):
            return TaskPriority.MEDIUM
        
        # Default to fast
        return TaskPriority.FAST


class CognitiveScheduler:
    """
    Nova's brain - runs only what's needed
    """
    
    def __init__(self):
        self.classifier = TaskClassifier()
        self.last_deep_time = 0
        self.deep_cooldown = 300  # 5 minutes between deep cycles
        
        # Track what's been activated
        self.activations = {
            "fast": 0,
            "medium": 0,
            "deep": 0
        }
    
    def run_cycle(self, task: str) -> Dict:
        """Run cognitive cycle based on task"""
        priority = self.classifier.classify(task)
        
        start = time.time()
        
        if priority == TaskPriority.FAST:
            result = self._run_fast()
        elif priority == TaskPriority.MEDIUM:
            result = self._run_medium()
        else:
            result = self._run_deep()
        
        elapsed = time.time() - start
        
        return {
            "priority": priority.name,
            "elapsed_ms": elapsed * 1000,
            "systems_used": result.get("systems", []),
            "activations": self.activations.copy()
        }
    
    def _run_fast(self) -> Dict:
        """Quick reflex - just basics"""
        self.activations["fast"] += 1
        
        return {
            "systems": ["memory_lookup", "focus"],
            "result": "quick"
        }
    
    def _run_medium(self) -> Dict:
        """Normal thinking"""
        self.activations["medium"] += 1
        
        return {
            "systems": ["focus", "world_model", "knowledge"],
            "result": "reasoned"
        }
    
    def _run_deep(self) -> Dict:
        """Full cognition - but rate limited"""
        now = time.time()
        
        # Don't go deep too often
        if now - self.last_deep_time < self.deep_cooldown:
            return self._run_medium()
        
        self.last_deep_time = now
        self.activations["deep"] += 1
        
        return {
            "systems": ["focus", "world_model", "curiosity", "council", "swarm", "evolution"],
            "result": "deep_thought"
        }
    
    def get_stats(self) -> Dict:
        """Get scheduler stats"""
        total = sum(self.activations.values())
        
        return {
            "total_cycles": total,
            "fast_ratio": self.activations["fast"] / max(total, 1),
            "medium_ratio": self.activations["medium"] / max(total, 1),
            "deep_ratio": self.activations["deep"] / max(total, 1)
        }


# Global
_scheduler = None

def get_scheduler() -> CognitiveScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = CognitiveScheduler()
    return _scheduler
