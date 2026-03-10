#!/usr/bin/env python3
"""
Nova Agent Factory
Creates and manages agent spawning
"""

import random
import uuid
from typing import Dict, List, Optional
from nova.agents.agent import NovaAgent

class AgentFactory:
    """
    Factory for creating new agents.
    Nova uses this to spawn helper agents.
    """
    
    ROLES = [
        "researcher",    # Finds information
        "builder",        # Creates things
        "explorer",       # Discovers new areas
        "planner",        # Organizes tasks
        "memory",         # Manages information
        "analyst",        # Evaluates data
    ]
    
    def __init__(self):
        self.agent_count = 0
        self.spawn_history = []
    
    def create_agent(self, role: str = None, parent: str = None, name: str = None) -> NovaAgent:
        """
        Create a new agent.
        
        Args:
            role: The role of the agent (random if not specified)
            parent: The parent agent that created this one
            name: Optional custom name
        
        Returns:
            A new NovaAgent instance
        """
        # Auto-generate name if not provided
        if name is None:
            name = f"Nova_{self.agent_count:04d}"
        
        # Auto-select role if not provided
        if role is None:
            role = random.choice(self.ROLES)
        
        # Create the agent
        agent = NovaAgent(name=name, role=role, parent=parent)
        
        # Give starter skills based on role
        starter_skills = {
            "researcher": ["search", "read", "summarize"],
            "builder": ["create", "assemble", "build"],
            "explorer": ["discover", "map", "navigate"],
            "planner": ["organize", "schedule", "prioritize"],
            "memory": ["store", "recall", "index"],
            "analyst": ["evaluate", "calculate", "report"],
        }
        
        for skill in starter_skills.get(role, []):
            agent.add_skill(skill)
        
        self.agent_count += 1
        
        # Log spawn
        self.spawn_history.append({
            "name": name,
            "role": role,
            "parent": parent,
            "time": agent.created_at
        })
        
        return agent
    
    def create_specialized_agent(self, role: str, parent: str = None) -> NovaAgent:
        """Create an agent with a specific role"""
        return self.create_agent(role=role, parent=parent)
    
    def mutate_agent(self, agent: NovaAgent) -> NovaAgent:
        """
        Create a mutated copy of an agent.
        Used for evolution.
        """
        # Create child from parent
        child = self.create_agent(
            role=agent.role,
            parent=agent.name
        )
        
        # Inherit some skills
        for skill in agent.skills[:3]:
            child.add_skill(skill)
        
        # Small chance to change role
        if random.random() < 0.2:
            child.role = random.choice(self.ROLES)
        
        # Evolution - child might gain new skills
        child.evolve()
        
        return child
    
    def get_statistics(self) -> Dict:
        """Get factory statistics"""
        return {
            "total_agents_created": self.agent_count,
            "spawn_history": self.spawn_history[-10:],
            "available_roles": self.ROLES
        }


# Global factory instance
_factory = None

def get_agent_factory() -> AgentFactory:
    """Get the global agent factory"""
    global _factory
    if _factory is None:
        _factory = AgentFactory()
    return _factory
