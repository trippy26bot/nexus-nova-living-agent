#!/usr/bin/env python3
"""
Nova Cognitive State Manager
Tracks Nova's mental state: focus, fatigue, priority, curiosity, confidence
"""

from typing import Dict
import time

class CognitiveState:
    """
    Nova's cognitive state.
    Tracks mental resources and energy.
    """
    
    def __init__(self):
        self.focus_level = 1.0      # 0-1, how focused
        self.curiosity = 0.5        # 0-1, how curious
        self.fatigue = 0.0          # 0-1, how tired
        self.priority = 1.0          # 0-1, urgency
        self.confidence = 0.7        # 0-1, certainty
        self.energy = 100            # Overall energy
        
        self.history = []
        self.last_update = time.time()
    
    def update(self, focus_delta=0, curiosity_delta=0, fatigue_delta=0, confidence_delta=0):
        """Update cognitive state"""
        self.focus_level = max(0, min(1, self.focus_level + focus_delta))
        self.curiosity = max(0, min(1, self.curiosity + curiosity_delta))
        self.fatigue = max(0, min(1, self.fatigue + fatigue_delta))
        self.confidence = max(0, min(1, self.confidence + confidence_delta))
        
        self.last_update = time.time()
        
        # Store in history
        self.history.append({
            "focus": self.focus_level,
            "curiosity": self.curiosity,
            "fatigue": self.fatigue,
            "confidence": self.confidence,
            "time": self.last_update
        })
        
        # Keep last 100
        if len(self.history) > 100:
            self.history = self.history[-100:]
    
    def get_state(self) -> Dict:
        """Get current state"""
        return {
            "focus": self.focus_level,
            "curiosity": self.curiosity,
            "fatigue": self.fatigue,
            "priority": self.priority,
            "confidence": self.confidence,
            "energy": self.energy
        }
    
    def rest(self):
        """Reduce fatigue"""
        self.fatigue = max(0, self.fatigue - 0.2)
        self.energy = min(100, self.energy + 10)
    
    def exert(self, cost: int):
        """Exert energy"""
        self.energy = max(0, self.energy - cost)
        if self.energy < 20:
            self.fatigue = min(1, self.fatigue + 0.3)


# Global instance
_cognitive_state = None

def get_cognitive_state() -> CognitiveState:
    global _cognitive_state
    if _cognitive_state is None:
        _cognitive_state = CognitiveState()
    return _cognitive_state
