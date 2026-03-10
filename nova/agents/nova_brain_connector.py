#!/usr/bin/env python3
"""
Nova Brain Connector
Connects the agent ecosystem to Nova's core brain
"""

import time
import random
from typing import Dict, List, Any, Optional
from nova.agents.universe import Universe, get_universe
from nova.agents.agent_factory import AgentFactory, get_agent_factory
from nova.agents.evolution_engine import EvolutionEngine, get_evolution_engine

class NovaBrainConnector:
    """
    Connects Nova's core brain to the agent ecosystem.
    Nova can spawn agents, delegate tasks, and learn from them.
    """
    
    def __init__(self):
        self.universe = get_universe()
        self.factory = get_agent_factory()
        self.evolution = get_evolution_engine()
        
        # Nova's agent (the parent)
        self.nova_agent = None
        
        # Task queue
        self.task_queue = []
        self.completed_tasks = []
        
        # Learning
        self.learned_insights = []
    
    def initialize_nova(self, name: str = "NOVA"):
        """Initialize Nova as an agent in the universe"""
        self.nova_agent = self.factory.create_agent(
            name=name,
            role="planner",
            parent="origin"
        )
        # Give Nova special skills
        self.nova_agent.add_skill("cognition")
        self.nova_agent.add_skill("leadership")
        self.nova_agent.add_skill("strategy")
        
        self.universe.add_agent(self.nova_agent)
        
        return self.nova_agent
    
    def spawn_helper(self, role: str, purpose: str = None) -> Any:
        """Nova spawns a helper agent"""
        if self.nova_agent is None:
            self.initialize_nova()
        
        # Check if spawning is allowed
        if not self.evolution.should_spawn(self.nova_agent, self.universe.resources):
            return None
        
        # Calculate child stats
        child_stats = self.evolution.calculate_child_stats(self.nova_agent)
        
        # Create child
        child_name = f"{self.nova_agent.name}_child_{int(time.time())}"
        child = self.factory.create_agent(
            role=role,
            parent=self.nova_agent.name,
            name=child_name
        )
        
        # Apply inherited stats
        child.energy = child_stats["energy"]
        child.skills = child_stats["skills"]
        child.role = child_stats["role"]
        
        # Add purpose to memory
        if purpose:
            child.learn(f"Purpose: {purpose}")
        
        # Add to universe
        self.universe.add_agent(child)
        
        # Log insight
        self.learned_insights.append({
            "type": "spawn",
            "role": role,
            "child": child_name,
            "time": time.time()
        })
        
        return child
    
    def delegate_task(self, task: str, role: str = "researcher") -> Dict:
        """Delegate a task to a helper agent"""
        # Find available agent
        available = self._find_available_agent(role)
        
        if available:
            # Give task to agent
            available.learn(f"Task: {task}")
            
            self.task_queue.append({
                "task": task,
                "agent": available.name,
                "assigned_at": time.time()
            })
            
            return {
                "status": "delegated",
                "agent": available.name,
                "task": task
            }
        else:
            # Spawn new agent for task
            agent = self.spawn_helper(role=role, purpose=task)
            
            if agent:
                self.task_queue.append({
                    "task": task,
                    "agent": agent.name,
                    "assigned_at": time.time()
                })
                
                return {
                    "status": "spawned",
                    "agent": agent.name,
                    "task": task
                }
        
        return {
            "status": "failed",
            "reason": "no_resources"
        }
    
    def _find_available_agent(self, role: str = None) -> Optional[Any]:
        """Find an agent that can take a task"""
        for agent in self.universe.agents:
            if role and agent.role != role:
                continue
            if agent.energy > 30 and agent != self.nova_agent:
                return agent
        return None
    
    def get_task_results(self) -> List[Dict]:
        """Get results from completed tasks"""
        results = []
        
        # Check agents for task results
        for agent in self.universe.agents:
            if agent.memory and agent != self.nova_agent:
                # Agent has learned something
                recent = agent.memory[-3:]  # Last 3 memories
                for mem in recent:
                    if "Task:" in str(mem):
                        results.append({
                            "agent": agent.name,
                            "result": mem,
                            "time": time.time()
                        })
        
        return results
    
    def learn_from_agents(self) -> List[str]:
        """Nova learns from her agents"""
        insights = []
        
        for agent in self.universe.agents:
            if agent == self.nova_agent:
                continue
            
            # Learn from their memories
            for memory in agent.memory[-2:]:
                insight = f"{agent.name}: {memory}"
                insights.append(insight)
                
                # Store in Nova's learning
                if "lesson" not in str(memory).lower():
                    self.learned_insights.append({
                        "type": "learned",
                        "from": agent.name,
                        "insight": str(memory),
                        "time": time.time()
                    })
        
        return insights
    
    def run_cycle(self) -> Dict:
        """Run one cognitive cycle"""
        # Run universe step
        universe_result = self.universe.step()
        
        # Evolve agents
        self.universe.agents = self.evolution.natural_selection(self.universe.agents)
        
        # Random evolution for active agents
        for agent in self.universe.agents:
            if agent.energy > 50 and random.random() < 0.1:
                self.evolution.evolve_agent(agent)
        
        # Learn from agents
        insights = self.learn_from_agents()
        
        return {
            "universe": universe_result,
            "insights": insights[:3],  # Top 3 insights
            "population": len(self.universe.agents)
        }
    
    def get_status(self) -> Dict:
        """Get system status"""
        return {
            "nova_agent": self.nova_agent.get_status() if self.nova_agent else None,
            "universe": self.universe.get_status(),
            "evolution": self.evolution.get_statistics(),
            "learned_insights": len(self.learned_insights),
            "pending_tasks": len(self.task_queue)
        }
    
    def broadcast_to_agents(self, message: str):
        """Nova broadcasts a message to all agents"""
        self.universe.broadcast(message, source=self.nova_agent.name if self.nova_agent else "NOVA")


# Global instance
_brain_connector = None

def get_brain_connector() -> NovaBrainConnector:
    global _brain_connector
    if _brain_connector is None:
        _brain_connector = NovaBrainConnector()
    return _brain_connector
