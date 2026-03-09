#!/usr/bin/env python3
"""
Nova Core - Main brain module
Coordinates all internal systems
"""

from nova.emotion_engine import get_emotion_engine
from nova.core.goal_engine import get_goal_engine
from nova.core.memory_engine import get_memory_engine
from nova.core.drift_engine import get_drift_engine

class NovaCore:
    """Main brain that coordinates all systems"""
    
    def __init__(self):
        self.emotions = get_emotion_engine()
        self.goals = get_goal_engine()
        self.memory = get_memory_engine()
        self.drift = get_drift_engine()
        self.cycle_count = 0
    
    def process(self, input_text: str, context: dict = None):
        """Process input through all systems"""
        self.cycle_count += 1
        
        # Get emotional state
        emotion_state = self.emotions.get_state()
        
        # Get active goals
        active_goals = self.goals.get_active()
        
        # Check drift
        drift_status = self.drift.check()
        
        return {
            "cycle": self.cycle_count,
            "emotions": emotion_state,
            "goals": active_goals,
            "drift": drift_status,
            "input": input_text
        }
    
    def reflect(self):
        """Run reflection cycle"""
        return self.drift.reflect()
    
    def evolve(self):
        """Run evolution cycle"""
        return self.drift.evolve()


# Global instance
_nova_core = None

def get_nova_core():
    global _nova_core
    if _nova_core is None:
        _nova_core = NovaCore()
    return _nova_core
