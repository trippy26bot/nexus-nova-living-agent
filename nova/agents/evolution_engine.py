#!/usr/bin/env python3
"""
Nova Evolution Engine
Handles agent spawning, evolution, and skill inheritance
"""

import random
import time
from typing import Dict, List, Optional
from nova.agents.agent import NovaAgent

class EvolutionEngine:
    """
    Manages evolution of agents in the universe.
    Handles spawning, mutation, and skill inheritance.
    """
    
    def __init__(self):
        self.generation = 0
        self.evolution_history = []
        self.mutation_rate = 0.3
        self.survival_threshold = 0.4
    
    def should_spawn(self, parent: NovaAgent, universe_resources: Dict) -> bool:
        """Decide if agent should spawn a child"""
        # Energy threshold
        if parent.energy < 40:
            return False
        
        # Resource threshold
        if universe_resources.get("energy", 0) < 15:
            return False
        
        # Skill threshold - parent must have skills
        if len(parent.skills) < 1:
            return False
        
        # Random chance
        return random.random() < 0.4
    
    def mutate_skills(self, parent_skills: List[str]) -> List[str]:
        """Mutate skills during reproduction"""
        new_skills = parent_skills.copy()
        
        # 30% chance to gain a new skill
        if random.random() < self.mutation_rate:
            possible_skills = [
                "coding", "research", "analysis", "planning",
                "creative", "communication", "strategy", "optimization",
                "learning", "memory", "adaptation", "innovation"
            ]
            available = [s for s in possible_skills if s not in new_skills]
            if available:
                new_skills.append(random.choice(available))
        
        # 10% chance to lose a skill
        if random.random() < 0.1 and len(new_skills) > 1:
            lost = random.choice(new_skills)
            new_skills.remove(lost)
        
        return new_skills
    
    def mutate_role(self, current_role: str) -> str:
        """Mutate role with small chance"""
        roles = ["researcher", "builder", "explorer", "planner", "memory", "analyst"]
        
        # 20% chance to change role
        if random.random() < 0.2:
            return random.choice(roles)
        
        return current_role
    
    def calculate_child_stats(self, parent: NovaAgent) -> Dict:
        """Calculate starting stats for child"""
        # Child inherits some energy from parent
        inherited_energy = int(parent.energy * 0.3)
        
        # Child starts with base energy
        base_energy = 80
        
        return {
            "energy": min(100, inherited_energy + base_energy),
            "skills": self.mutate_skills(parent.skills),
            "role": self.mutate_role(parent.role)
        }
    
    def evolve_agent(self, agent: NovaAgent) -> Dict:
        """Evolve an agent - gain improvements"""
        improvements = []
        
        # Random evolution events
        roll = random.random()
        
        if roll < 0.2:
            # Better energy efficiency
            agent.energy = min(100, agent.energy + 10)
            improvements.append("energy_boost")
        
        if roll < 0.15:
            # Learn faster
            improvements.append("learning_boost")
        
        if roll < 0.1:
            # Gain skill
            new_skills = ["coding", "research", "analysis", "creative"]
            available = [s for s in new_skills if s not in agent.skills]
            if available:
                agent.add_skill(random.choice(available))
                improvements.append("new_skill")
        
        if roll < 0.05:
            # Role evolution (promotion)
            improvements.append("role_evolution")
        
        # Always gain some experience
        agent.evolve()
        
        return {
            "agent": agent.name,
            "improvements": improvements,
            "skills": agent.skills
        }
    
    def natural_selection(self, agents: List[NovaAgent]) -> List[NovaAgent]:
        """Remove weak agents"""
        survivors = []
        
        for agent in agents:
            # Death conditions
            if agent.energy <= 0 and random.random() > 0.3:
                # Agent dies
                self.evolution_history.append({
                    "event": "death",
                    "agent": agent.name,
                    "generation": self.generation,
                    "reason": "no_energy"
                })
                continue
            
            # Random death for very old agents
            age = time.time() - agent.created_at
            if age > 3600 and random.random() < 0.05:  # After 1 hour
                self.evolution_history.append({
                    "event": "death",
                    "agent": agent.name,
                    "generation": self.generation,
                    "reason": "old_age"
                })
                continue
            
            survivors.append(agent)
        
        return survivors
    
    def get_statistics(self) -> Dict:
        """Get evolution statistics"""
        return {
            "generation": self.generation,
            "total_events": len(self.evolution_history),
            "recent_events": self.evolution_history[-10:],
            "mutation_rate": self.mutation_rate
        }


# Global instance
_evolution_engine = None

def get_evolution_engine() -> EvolutionEngine:
    global _evolution_engine
    if _evolution_engine is None:
        _evolution_engine = EvolutionEngine()
    return _evolution_engine
