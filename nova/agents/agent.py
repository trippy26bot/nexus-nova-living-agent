#!/usr/bin/env python3
"""
Nova Agent Base Class
A minimal agent that can think, act, and learn
"""

import time
import random
from typing import Dict, List, Any, Optional

class NovaAgent:
    """
    Base agent class for Nova's ecosystem.
    Can be spawned by Nova to help with tasks.
    """
    
    def __init__(self, name: str, role: str, parent: str = None):
        self.name = name
        self.role = role
        self.parent = parent
        self.energy = 100
        self.created_at = time.time()
        self.last_action = None
        self.experience = []
        self.skills = []
        self.memory = []
    
    def think(self) -> str:
        """Agent thinks and decides what to do"""
        if self.energy <= 0:
            return "rest"
        
        # Role-based actions
        actions = {
            "researcher": ["research", "analyze", "experiment"],
            "builder": ["build", "create", "assemble"],
            "explorer": ["explore", "discover", "map"],
            "planner": ["plan", "organize", "strategy"],
            "memory": ["store", "recall", "consolidate"],
            "analyst": ["analyze", "evaluate", "report"],
        }
        
        role_actions = actions.get(self.role, ["work"])
        
        # Add rest action
        all_actions = role_actions + ["rest", "observe"]
        
        action = random.choice(all_actions)
        
        return action
    
    def act(self, action: str, world: Any = None) -> Dict:
        """Agent performs an action"""
        self.last_action = action
        
        # Energy cost
        energy_cost = {
            "research": 15,
            "analyze": 12,
            "build": 20,
            "create": 18,
            "explore": 15,
            "plan": 10,
            "store": 5,
            "rest": -20,  # Rest restores energy
            "observe": 3,
        }
        
        cost = energy_cost.get(action, 10)
        self.energy = max(0, min(100, self.energy - cost))
        
        # Log experience
        self.experience.append({
            "action": action,
            "energy": self.energy,
            "time": time.time()
        })
        
        return {
            "agent": self.name,
            "action": action,
            "energy": self.energy,
            "role": self.role
        }
    
    def learn(self, lesson: str):
        """Agent learns something"""
        self.memory.append({
            "lesson": lesson,
            "time": time.time()
        })
        
        # Keep only recent memories
        if len(self.memory) > 50:
            self.memory = self.memory[-50:]
    
    def rest(self) -> Dict:
        """Rest to restore energy"""
        self.energy = min(100, self.energy + 30)
        return {
            "agent": self.name,
            "action": "rest",
            "energy": self.energy
        }
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "name": self.name,
            "role": self.role,
            "parent": self.parent,
            "energy": self.energy,
            "experience_count": len(self.experience),
            "memory_count": len(self.memory),
            "skills": self.skills,
            "created_at": self.created_at
        }
    
    def can_spawn(self, world_resources: int, spawn_cost: int = 10) -> bool:
        """Check if agent can spawn a child"""
        return (
            self.energy > 30 and 
            world_resources >= spawn_cost and
            len(self.skills) > 0
        )
    
    def add_skill(self, skill: str):
        """Add a skill to this agent"""
        if skill not in self.skills:
            self.skills.append(skill)
    
    def evolve(self) -> bool:
        """Agent evolves - gains random improvement"""
        improvements = [
            "faster_learning",
            "better_planning",
            "more_efficient",
            "broader_skills",
            "faster_thinking"
        ]
        
        improvement = random.choice(improvements)
        
        # Small chance to gain a new skill
        if random.random() < 0.3:
            new_skills = ["coding", "research", "analysis", "communication"]
            skill = random.choice(new_skills)
            self.add_skill(skill)
        
        return True
