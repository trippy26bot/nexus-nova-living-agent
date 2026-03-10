#!/usr/bin/env python3
"""
Nova Economy - Resource Management System
"""

from typing import Dict, Any

class ResourcePool:
    """Manages Nova's internal resources"""
    
    def __init__(self):
        self.resources = {
            "compute": 1000,
            "attention": 1000,
            "research": 1000,
            "energy": 1000
        }
    
    def request(self, resource: str, amount: int) -> bool:
        """Request resources"""
        if self.resources.get(resource, 0) >= amount:
            self.resources[resource] -= amount
            return True
        return False
    
    def release(self, resource: str, amount: int):
        """Release resources back"""
        if resource in self.resources:
            self.resources[resource] += amount
    
    def get(self, resource: str) -> int:
        return self.resources.get(resource, 0)
    
    def get_all(self) -> Dict:
        return self.resources.copy()


class IdeaMarket:
    """Ideas compete for execution"""
    
    def __init__(self):
        self.ideas = []
    
    def submit(self, agent: str, idea: str, priority: float):
        """Submit an idea"""
        self.ideas.append({
            "agent": agent,
            "idea": idea,
            "priority": priority
        })
    
    def select_best(self, n: int = 1):
        """Select best ideas"""
        if not self.ideas:
            return []
        
        sorted_ideas = sorted(self.ideas, key=lambda x: x["priority"], reverse=True)
        selected = sorted_ideas[:n]
        
        for s in selected:
            if s in self.ideas:
                self.ideas.remove(s)
        
        return selected


class AttentionAllocator:
    """Allocates attention to ideas"""
    
    def __init__(self):
        self.focus = None
        self.history = []
    
    def allocate(self, idea: str):
        """Allocate attention"""
        self.focus = idea
        self.history.append(idea)
    
    def get_focus(self) -> str:
        return self.focus


class ReputationSystem:
    """Tracks agent reputation"""
    
    def __init__(self):
        self.scores = {}
    
    def reward(self, agent: str, value: float = 1.0):
        """Reward an agent"""
        if agent not in self.scores:
            self.scores[agent] = 0
        self.scores[agent] += value
    
    def score(self, agent: str) -> float:
        return self.scores.get(agent, 0)
    
    def get_all(self) -> Dict:
        return self.scores.copy()


# Global instances
_resource_pool = None
_idea_market = None
_attention_allocator = None
_reputation_system = None

def get_resource_pool() -> ResourcePool:
    global _resource_pool
    if _resource_pool is None:
        _resource_pool = ResourcePool()
    return _resource_pool

def get_idea_market() -> IdeaMarket:
    global _idea_market
    if _idea_market is None:
        _idea_market = IdeaMarket()
    return _idea_market

def get_attention_allocator() -> AttentionAllocator:
    global _attention_allocator
    if _attention_allocator is None:
        _attention_allocator = AttentionAllocator()
    return _attention_allocator

def get_reputation_system() -> ReputationSystem:
    global _reputation_system
    if _reputation_system is None:
        _reputation_system = ReputationSystem()
    return _reputation_system
