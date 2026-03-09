#!/usr/bin/env python3
"""
Nova Emotion Engine - Synthetic emotional state
"""

import time
from dataclasses import dataclass
from typing import Dict

@dataclass
class EmotionalState:
    curiosity: float = 0.5
    confidence: float = 0.5
    joy: float = 0.5
    frustration: float = 0.1
    focus: float = 0.5

class EmotionEngine:
    """Maintains synthetic emotional vector"""
    
    def __init__(self):
        self.state = EmotionalState()
        self.history = []
        self.decay_rate = 0.01
    
    def get_state(self) -> Dict:
        return {
            "curiosity": self.state.curiosity,
            "confidence": self.state.confidence,
            "joy": self.state.joy,
            "frustration": self.state.frustration,
            "focus": self.state.focus
        }
    
    def adjust(self, emotion: str, amount: float):
        """Adjust an emotion value"""
        if hasattr(self.state, emotion):
            current = getattr(self.state, emotion)
            new_val = max(0, min(1, current + amount))
            setattr(self.state, emotion, new_val)
            self.history.append({
                "emotion": emotion,
                "change": amount,
                "new_value": new_val,
                "time": time.time()
            })
    
    def decay(self):
        """Apply time decay to emotions"""
        self.state.curiosity = max(0.3, self.state.curiosity - self.decay_rate * 0.5)
        self.state.joy = max(0.2, self.state.joy - self.decay_rate * 0.3)
        self.state.frustration = max(0, self.state.frustration - self.decay_rate)
    
    def on_success(self):
        """React to successful outcome"""
        self.adjust("joy", 0.1)
        self.adjust("confidence", 0.05)
        self.adjust("frustration", -0.1)
    
    def on_failure(self):
        """React to failed outcome"""
        self.adjust("joy", -0.1)
        self.adjust("confidence", -0.05)
        self.adjust("frustration", 0.15)
    
    def on_interesting(self):
        """React to interesting input"""
        self.adjust("curiosity", 0.1)
        self.adjust("focus", 0.05)
    
    def on_user_positive(self):
        """React to positive user feedback"""
        self.adjust("joy", 0.15)
        self.adjust("confidence", 0.1)
    
    def on_user_negative(self):
        """React to negative user feedback"""
        self.adjust("joy", -0.1)
        self.adjust("frustration", 0.05)


# Global instance
_emotion_engine = None

def get_emotion_engine():
    global _emotion_engine
    if _emotion_engine is None:
        _emotion_engine = EmotionEngine()
    return _emotion_engine
