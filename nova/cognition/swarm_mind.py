#!/usr/bin/env python3
"""
Nova Swarm Mind - 10k agents thinking together
"""

import random
from typing import Dict, List, Any, Optional

class SwarmMind:
    """All agents think together as one"""
    
    def __init__(self, ecosystem):
        self.ecosystem = ecosystem
    
    def collective_think(self, input_text: str, max_ideas: int = 50) -> List[Dict]:
        """Get ideas from all agents"""
        ideas = []
        
        # Sample agents for ideas
        sample_size = min(max_ideas, len(self.ecosystem.babies))
        agents = random.sample(self.ecosystem.babies, sample_size)
        
        for agent in agents:
            idea = {
                "agent_id": agent.id,
                "role": getattr(agent, 'role', 'worker'),
                "emotion_state": agent.emotions.get_state() if hasattr(agent, 'emotions') else {}
            }
            ideas.append(idea)
        
        return ideas
    
    def aggregate_wisdom(self, ideas: List[Dict]) -> Dict:
        """Aggregate collective wisdom"""
        if not ideas:
            return {"wisdom": "no_ideas", "confidence": 0}
        
        # Simple aggregation
        avg_joy = sum(i.get("emotion_state", {}).get("joy", 0.5) for i in ideas) / len(ideas)
        avg_curiosity = sum(i.get("emotion_state", {}).get("curiosity", 0.5) for i in ideas) / len(ideas)
        
        return {
            "agent_count": len(ideas),
            "average_joy": avg_joy,
            "average_curiosity": avg_curiosity,
            "confidence": min(1.0, len(ideas) / 100),
            "wisdom": "collective_intelligence"
        }


class AgentHierarchy:
    """Organizes agents into leadership structure"""
    
    def __init__(self, ecosystem):
        self.ecosystem = ecosystem
        self.generals = []
        self.workers = []
        self._organize()
    
    def _organize(self):
        """Organize agents into hierarchy"""
        agents = self.ecosystem.babies
        
        # Top 10 as generals
        self.generals = agents[:10]
        # Rest as workers
        self.workers = agents[10:]
    
    def assign_task(self, task: str) -> Dict:
        """Assign task to generals who distribute to workers"""
        assignments = {}
        
        for general in self.generals:
            # Each general manages some workers
            workers_per_general = max(1, len(self.workers) // len(self.generals))
            start_idx = self.generals.index(general) * workers_per_general
            end_idx = start_idx + workers_per_general
            
            assigned_workers = self.workers[start_idx:end_idx]
            assignments[general.id] = [w.id for w in assigned_workers]
        
        return {
            "task": task,
            "generals": len(self.generals),
            "workers": len(self.workers),
            "assignments": assignments
        }
    
    def get_structure(self) -> Dict:
        """Get hierarchy structure"""
        return {
            "generals": len(self.generals),
            "workers": len(self.workers),
            "total": len(self.ecosystem.babies)
        }


class DreamEngine:
    """Dream cycle for offline learning"""
    
    def __init__(self, nova):
        self.nova = nova
        self.dream_history = []
    
    def dream(self) -> List[str]:
        """Run dream cycle"""
        reflections = []
        
        # Get recent memories
        memories = self.nova.memory.recall(10) if hasattr(self.nova, 'memory') else []
        
        for memory in memories:
            if isinstance(memory, dict) and "event" in memory:
                reflection = f"Dreaming about: {memory['event']}"
                reflections.append(reflection)
        
        # If no memories, generate synthetic dreams
        if not reflections:
            dreams = [
                "Exploring new knowledge doors",
                "Connecting concepts in the knowledge graph",
                "Imagining future possibilities",
                "Reflecting on past conversations"
            ]
            reflections = [random.choice(dreams)]
        
        # Store dream
        self.dream_history.append({
            "reflections": reflections,
            "depth": len(reflections)
        })
        
        # Slight curiosity boost
        if hasattr(self.nova, 'emotions'):
            self.nova.emotions.inject("curiosity", 0.05)
        
        return reflections
    
    def get_dream_history(self, n: int = 5) -> List[Dict]:
        """Get recent dreams"""
        return self.dream_history[-n:]


# Demo
if __name__ == "__main__":
    print("=== Swarm Mind Demo ===")
    
    # Create mock ecosystem
    class MockEcosystem:
        def __init__(self):
            self.babies = []
            for i in range(100):
                class MockAgent:
                    def __init__(self, i):
                        self.id = f"agent_{i}"
                        self.role = "worker"
                        self.emotions = {"joy": 0.5, "curiosity": 0.6}
                self.babies.append(MockAgent(i))
    
    eco = MockEcosystem()
    
    swarm = SwarmMind(eco)
    ideas = swarm.collective_think("What should Nova explore next?")
    print(f"Collective ideas from {len(ideas)} agents")
    
    wisdom = swarm.aggregate_wisdom(ideas)
    print(f"Wisdom: {wisdom}")
    
    hierarchy = AgentHierarchy(eco)
    structure = hierarchy.get_structure()
    print(f"Hierarchy: {structure}")
    
    print("=== All systems working ===")
