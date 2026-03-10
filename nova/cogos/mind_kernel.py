#!/usr/bin/env python3
"""
Nova Mind Kernel (CogOS)
The OS that runs all minds
"""

from typing import Dict, List, Any, Optional
import time

class Mind:
    """A single mind in the system"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.active = True
        self.energy = 100
        self.tasks_completed = 0
        self.created_at = time.time()
    
    def run(self, task: str) -> Dict:
        """Run a task"""
        if not self.active or self.energy <= 0:
            return {"error": "Mind inactive or no energy"}
        
        self.energy -= 10
        self.tasks_completed += 1
        
        return {
            "mind": self.name,
            "role": self.role,
            "task": task,
            "completed": True
        }
    
    def get_status(self) -> Dict:
        return {
            "name": self.name,
            "role": self.role,
            "active": self.active,
            "energy": self.energy,
            "tasks": self.tasks_completed
        }


class MindKernel:
    """
    The CogOS kernel.
    Runs and coordinates all minds.
    """
    
    def __init__(self):
        self.minds = {}
        self.task_queue = []
        self.results = []
        
        # Register default minds
        self._register_default_minds()
    
    def _register_default_minds(self):
        """Register default minds"""
        default_minds = [
            ("research", "ResearchMind", "gathers information"),
            ("strategy", "StrategyMind", "plans and decides"),
            ("builder", "BuilderMind", "creates solutions"),
            ("creative", "CreativeMind", "generates ideas"),
            ("guardian", "GuardianMind", "protects and safety checks"),
        ]
        
        for role, name, desc in default_minds:
            mind = Mind(name, role)
            self.minds[role] = mind
    
    def register_mind(self, name: str, role: str):
        """Register a new mind"""
        if role not in self.minds:
            self.minds[role] = Mind(name, role)
    
    def get_mind(self, role: str) -> Optional[Mind]:
        """Get a mind by role"""
        return self.minds.get(role)
    
    def run_mind(self, role: str, task: str) -> Dict:
        """Run a specific mind"""
        mind = self.get_mind(role)
        if mind:
            return mind.run(task)
        return {"error": f"Mind {role} not found"}
    
    def run_all(self, task: str) -> Dict:
        """Run all minds on a task"""
        results = {}
        for role, mind in self.minds.items():
            if mind.active:
                results[role] = mind.run(task)
        return results
    
    def assign_task(self, role: str, task: str) -> Dict:
        """Assign task to appropriate mind"""
        return self.run_mind(role, task)
    
    def get_all_status(self) -> List[Dict]:
        """Get status of all minds"""
        return [mind.get_status() for mind in self.minds.values()]
    
    def spawn_specialized_mind(self, role: str, name: str = None) -> Mind:
        """Create a specialized mind"""
        name = name or f"{role.title()}Mind"
        mind = Mind(name, role)
        self.minds[role] = mind
        return mind
    
    def shutdown_mind(self, role: str) -> bool:
        """Deactivate a mind"""
        if role in self.minds:
            self.minds[role].active = False
            return True
        return False


# Global instance
_mind_kernel = None

def get_mind_kernel() -> MindKernel:
    global _mind_kernel
    if _mind_kernel is None:
        _mind_kernel = MindKernel()
    return _mind_kernel
