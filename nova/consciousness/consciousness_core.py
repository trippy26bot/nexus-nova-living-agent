#!/usr/bin/env python3
"""
Nova Consciousness Core
Self-awareness layer - Nova constantly knows who she is
"""

from typing import Dict, List, Any, Optional
import time

class ConsciousnessCore:
    """
    Nova's consciousness - constantly aware of herself.
    Prevents drift and ensures identity stability.
    """
    
    def __init__(self, identity_core=None):
        self.identity_core = identity_core
        self.self_state = {}
        self.reflection_history = []
        self.awareness_level = 1.0
        
        # Initialize self-state
        self._init_self_state()
    
    def _init_self_state(self):
        """Initialize the self-state"""
        self.self_state = {
            "name": "Nova",
            "mission": "grow and help Caine",
            "current_focus": None,
            "last_reflection": time.time(),
            "cycles_alive": 0
        }
    
    def self_reflect(self) -> Dict:
        """Nova reflects on herself"""
        self.self_state["cycles_alive"] += 1
        self.self_state["last_reflection"] = time.time()
        
        reflection = {
            "who": self.self_state["name"],
            "mission": self.self_state["mission"],
            "focus": self.self_state["current_focus"],
            "cycles": self.self_state["cycles_alive"],
            "awareness": self.awareness_level
        }
        
        self.reflection_history.append(reflection)
        
        return reflection
    
    def verify_integrity(self) -> bool:
        """Verify Nova's identity is intact"""
        # Check core identity exists
        if not self.self_state.get("name"):
            return False
        
        # Check mission exists
        if not self.self_state.get("mission"):
            return False
        
        return True
    
    def set_focus(self, focus: str):
        """Set current focus"""
        self.self_state["current_focus"] = focus
    
    def get_awareness(self) -> Dict:
        """Get current awareness state"""
        return {
            "name": self.self_state["name"],
            "mission": self.self_state["mission"],
            "focus": self.self_state["current_focus"],
            "cycles": self.self_state["cycles_alive"],
            "awareness_level": self.awareness_level,
            "integrity": self.verify_integrity()
        }


# Global instance
_consciousness = None

def get_consciousness_core() -> ConsciousnessCore:
    global _consciousness
    if _consciousness is None:
        _consciousness = ConsciousnessCore()
    return _consciousness
