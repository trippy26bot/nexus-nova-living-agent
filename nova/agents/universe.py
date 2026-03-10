#!/usr/bin/env python3
"""
Nova Universe
The world where agents live and interact
"""

import time
from typing import Dict, List, Any, Optional
from nova.agents.agent import NovaAgent
from nova.agents.agent_factory import get_agent_factory

class Universe:
    """
    The world where Nova's agents exist.
    Manages resources, spawning, and agent lifecycles.
    """
    
    def __init__(self, name: str = "NovaWorld"):
        self.name = name
        self.agents: List[NovaAgent] = []
        self.resources = {
            "energy": 1000,
            "knowledge": 100,
            "creative": 50,
        }
        self.spawn_cost = 10
        self.time = 0
        self.history = []
        self.factory = get_agent_factory()
        
        # Statistics
        self.actions_performed = 0
        self.total_spawns = 0
    
    def add_agent(self, agent: NovaAgent) -> bool:
        """Add an agent to the universe"""
        if self.resources["energy"] < self.spawn_cost:
            return False
        
        self.agents.append(agent)
        self.resources["energy"] -= self.spawn_cost
        self.total_spawns += 1
        
        self.history.append({
            "event": "spawn",
            "agent": agent.name,
            "time": self.time
        })
        
        return True
    
    def remove_agent(self, agent_name: str) -> bool:
        """Remove an agent from the universe"""
        for i, agent in enumerate(self.agents):
            if agent.name == agent_name:
                self.agents.pop(i)
                self.history.append({
                    "event": "death",
                    "agent": agent_name,
                    "time": self.time
                })
                return True
        return False
    
    def request_spawn(self, parent_agent: NovaAgent, role: str = None) -> Optional[NovaAgent]:
        """Request spawning a new agent"""
        if not parent_agent.can_spawn(self.resources["energy"], self.spawn_cost):
            return None
        
        # Create child
        child = self.factory.mutate_agent(parent_agent)
        
        # Deduct resources
        self.resources["energy"] -= self.spawn_cost
        
        # Add to universe
        self.agents.append(child)
        self.total_spawns += 1
        
        self.history.append({
            "event": "birth",
            "agent": child.name,
            "parent": parent_agent.name,
            "time": self.time
        })
        
        return child
    
    def step(self) -> Dict:
        """
        Run one time step.
        All agents get to act once.
        """
        self.time += 1
        step_events = []
        
        for agent in self.agents[:]:  # Copy list to allow modification
            if agent.energy <= 0:
                # Agent needs to rest
                result = agent.rest()
                step_events.append(result)
            else:
                # Agent thinks and acts
                action = agent.think()
                
                # Handle spawning request
                if action == "spawn" and agent.can_spawn(self.resources["energy"]):
                    child = self.request_spawn(agent)
                    if child:
                        step_events.append({
                            "event": "spawn",
                            "parent": agent.name,
                            "child": child.name,
                            "role": child.role
                        })
                else:
                    result = agent.act(action, self)
                    step_events.append(result)
                
                self.actions_performed += 1
        
        # Resource generation (passive)
        self.resources["energy"] = min(2000, self.resources["energy"] + 5)
        self.resources["knowledge"] = min(500, self.resources["knowledge"] + 1)
        
        return {
            "time": self.time,
            "agents": len(self.agents),
            "resources": self.resources.copy(),
            "events": step_events
        }
    
    def get_status(self) -> Dict:
        """Get universe status"""
        return {
            "name": self.name,
            "time": self.time,
            "agents": len(self.agents),
            "total_spawns": self.total_spawns,
            "total_actions": self.actions_performed,
            "resources": self.resources.copy(),
            "agent_list": [
                {
                    "name": a.name,
                    "role": a.role,
                    "energy": a.energy,
                    "skills": a.skills,
                    "parent": a.parent
                }
                for a in self.agents
            ]
        }
    
    def get_agent(self, name: str) -> Optional[NovaAgent]:
        """Get agent by name"""
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None
    
    def broadcast(self, message: str, source: str = "universe"):
        """Broadcast a message to all agents"""
        for agent in self.agents:
            agent.learn(f"[{source}] {message}")
    
    def get_statistics(self) -> Dict:
        """Get detailed statistics"""
        roles = {}
        total_energy = 0
        
        for agent in self.agents:
            roles[agent.role] = roles.get(agent.role, 0) + 1
            total_energy += agent.energy
        
        return {
            "universe_age": self.time,
            "population": len(self.agents),
            "by_role": roles,
            "average_energy": total_energy / max(1, len(self.agents)),
            "resources": self.resources,
            "factory_stats": self.factory.get_statistics()
        }


# Global universe instance
_universe = None

def get_universe() -> Universe:
    """Get the global universe"""
    global _universe
    if _universe is None:
        _universe = Universe()
    return _universe
