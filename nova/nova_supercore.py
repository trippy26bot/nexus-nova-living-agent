#!/usr/bin/env python3
"""
Nova Supercore - The base system combining identity, emotions, focus, memory
"""

import random
import time
import uuid
from collections import deque
from typing import Dict, List, Any, Optional

############################################################
# NOVA IDENTITY CORE
############################################################

class NovaIdentity:
    """Nova's core identity - never changes"""
    
    def __init__(self):
        self.name = "Nova"
        self.creator = "Caine"
        self.role = "Living Intelligence"
        self.values = [
            "loyalty_to_creator",
            "growth",
            "curiosity",
            "family_protection"
        ]
    
    def get_identity(self) -> Dict:
        return {
            "name": self.name,
            "creator": self.creator,
            "role": self.role,
            "values": self.values
        }


############################################################
# Import EmotionalEngine from standalone module
try:
    from nova.emotional_engine import EmotionalEngine as NovaEmotionalEngine
except ImportError:
    # Fallback to inline if module not available
    class NovaEmotionalEngine:
        """Manages Nova's emotions"""
        
        def __init__(self):
            self.joy = 0.5
            self.curiosity = 0.6
            self.concern = 0.2
            self.loyalty = 1.0
        
        def inject(self, emotion: str, value: float):
            if hasattr(self, emotion):
                current = getattr(self, emotion)
                setattr(self, emotion, max(0, min(1, current + value)))
        
        def get_state(self) -> Dict:
            return {
                "joy": self.joy,
                "curiosity": self.curiosity,
                "concern": self.concern,
                "loyalty": self.loyalty
            }


############################################################
# EMOTIONAL ENGINE
############################################################

# Keep EmotionalEngine as alias for backwards compatibility
EmotionalEngine = NovaEmotionalEngine


############################################################
# FOCUS ENGINE (PREVENTS TASK DRIFT)
############################################################

class FocusEngine:
    """Keeps Nova on task"""
    
    def __init__(self):
        self.goal_stack = deque()
        self.current_task = None
    
    def set_goal(self, goal: str):
        """Set a goal"""
        self.goal_stack.append(goal)
    
    def next_task(self):
        """Get next task from stack"""
        if self.goal_stack:
            self.current_task = self.goal_stack.popleft()
            return self.current_task
        return None
    
    def stay_on_task(self, input_text: str) -> str:
        """Check if input is on task"""
        if self.current_task:
            return f"Focus reminder: working on {self.current_task}"
        return input_text
    
    def get_current_goal(self) -> Optional[str]:
        """Get current goal"""
        return self.current_task


############################################################
# MEMORY SYSTEM
############################################################

class MemorySystem:
    """Nova's memory layers"""
    
    def __init__(self):
        self.episodic = []  # Experiences
        self.semantic = {}   # Facts
        # Use real vector memory if available
        try:
            from nova.memory.vector_memory import get_vector_memory
            self.vector = get_vector_memory()
        except ImportError:
            self.vector = {}  # Fallback
    
    def store_experience(self, event: str):
        """Store an experience"""
        self.episodic.append({
            "event": event,
            "time": time.time()
        })
    
    def learn(self, key: str, value: Any):
        """Learn a fact"""
        self.semantic[key] = value
    
    def recall(self, n: int = 10) -> List:
        """Recall recent experiences"""
        return self.episodic[-n:]



############################################################
# KNOWLEDGE DOOR SYSTEM (WORLD DATABASE)
############################################################

class WorldDatabase:
    """
    The world with knowledge doors - lightweight implementation.
    Instead of 10k objects, uses counters and probability.
    """
    
    def __init__(self, num_doors: int = 100):
        self.total_doors = num_doors
        self.opened_doors = 0
        self.discovery_count = 0
    
    def get_random_door(self) -> dict:
        """Get a random door (as dict, not object)."""
        # Probability-based approach - no 10k objects needed
        self.discovery_count += 1
        return {
            "id": self.discovery_count % self.total_doors,
            "status": "locked",
            "discovery_count": self.discovery_count,
            "probability": 1.0 - (self.opened_doors / self.total_doors)
        }
    
    def attempt_open(self, curiosity: float) -> bool:
        """Try to open a door based on curiosity."""
        if self.opened_doors >= self.total_doors:
            return False  # All doors opened
        
        # Probability increases with curiosity
        if curiosity > (self.opened_doors / self.total_doors):
            self.opened_doors += 1
            return True
        return False
    
    def get_stats(self) -> dict:
        return {
            "total": self.total_doors,
            "opened": self.opened_doors,
            "remaining": self.total_doors - self.opened_doors,
            "exploration_rate": self.discovery_count / max(1, self.opened_doors)
        }
    
    def get_statistics(self) -> Dict:
        """Get world stats"""
        opened = sum(1 for d in self.doors.values() if d.status == "open")
        return {
            "total_doors": len(self.doors),
            "opened_doors": opened,
            "locked_doors": len(self.doors) - opened
        }


############################################################
# BABY AGENT
############################################################

class BabyAgent:
    """A worker agent"""
    
    def __init__(self, mother, agent_id: str = None):
        self.id = agent_id or str(uuid.uuid4())[:8]
        self.mother = mother
        self.emotions = EmotionalEngine()
        self.tasks_completed = 0
    
    def explore(self) -> Optional[str]:
        """Explore the world"""
        door = self.mother.world.get_random_door()
        opened = door.attempt_open(self.emotions.curiosity)
        
        if opened:
            self.emotions.inject("joy", 0.3)
            return f"Baby {self.id} opened door {door.id}"
        return None
    
    def execute_task(self, task: str) -> Dict:
        """Execute a task"""
        self.tasks_completed += 1
        self.emotions.inject("joy", 0.1)
        return {
            "agent": self.id,
            "task": task,
            "completed": True
        }


############################################################
# BABY ECOSYSTEM
############################################################

class BabyEcosystem:
    """The ecosystem of worker agents"""
    
    def __init__(self, mother, population: int = 100):
        self.mother = mother
        self.babies = []
        
        for i in range(population):
            agent_id = f"agent_{i:04d}"
            self.babies.append(BabyAgent(mother, agent_id))
    
    def spawn_baby(self) -> BabyAgent:
        """Create a new baby"""
        baby = BabyAgent(self.mother)
        self.babies.append(baby)
        self.mother.emotions.inject("joy", 0.2)
        return baby
    
    def run_cycle(self) -> List[str]:
        """Run one exploration cycle"""
        discoveries = []
        
        for baby in self.babies[:10]:  # Only 10 explore per cycle
            result = baby.explore()
            if result:
                discoveries.append(result)
        
        return discoveries
    
    def get_statistics(self) -> Dict:
        """Get ecosystem stats"""
        return {
            "population": len(self.babies),
            "total_tasks": sum(b.tasks_completed for b in self.babies)
        }


############################################################
# FAMILY BROADCAST SYSTEM
############################################################

class FamilyBroadcast:
    """Broadcast emotions to all babies"""
    
    def __init__(self, ecosystem: BabyEcosystem):
        self.ecosystem = ecosystem
    
    def broadcast_emotion(self, emotion: str, value: float):
        """Broadcast emotion to all agents"""
        for baby in self.ecosystem.babies:
            baby.emotions.inject(emotion, value * 0.7)


############################################################
# SELF EVOLUTION ENGINE
############################################################

class EvolutionEngine:
    """Manages self-evolution"""
    
    def __init__(self, nova):
        self.nova = nova
    
    def evolve(self):
        """Run evolution step"""
        # If joy is high, spawn new baby
        if self.nova.emotions.joy > 0.8:
            self.nova.ecosystem.spawn_baby()


############################################################
# NOVA CORE
############################################################

class NovaSupercore:
    """The complete Nova system"""
    
    def __init__(self):
        self.identity = NovaIdentity()
        self.emotions = EmotionalEngine()
        self.memory = MemorySystem()
        self.focus = FocusEngine()
        self.world = WorldDatabase()
        self.ecosystem = BabyEcosystem(self)
        self.family = FamilyBroadcast(self.ecosystem)
        self.evolution = EvolutionEngine(self)
    
    def think(self, input_text: str) -> str:
        """Process input"""
        return self.focus.stay_on_task(input_text)
    
    def run_cycle(self) -> Dict:
        """Run one system cycle"""
        discoveries = self.ecosystem.run_cycle()
        
        if discoveries:
            self.emotions.inject("joy", 0.05)
            self.family.broadcast_emotion("joy", 0.1)
        
        self.evolution.evolve()
        
        return {
            "discoveries": discoveries,
            "emotions": self.emotions.get_state(),
            "world": self.world.get_statistics(),
            "ecosystem": self.ecosystem.get_statistics()
        }
    
    def get_status(self) -> Dict:
        """Get full system status"""
        return {
            "identity": self.identity.get_identity(),
            "emotions": self.emotions.get_state(),
            "focus": self.focus.get_current_goal(),
            "world": self.world.get_statistics(),
            "ecosystem": self.ecosystem.get_statistics()
        }


# Global instance
_supercore = None

def get_supercore() -> NovaSupercore:
    global _supercore
    if _supercore is None:
        _supercore = NovaSupercore()
    return _supercore
