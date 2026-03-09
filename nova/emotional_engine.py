#!/usr/bin/env python3
"""
Emotional Engine - Internal emotional state that influences behavior and tone
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict

@dataclass
class EmotionalState:
    joy: float = 0.5
    curiosity: float = 0.6
    confidence: float = 0.5
    concern: float = 0.2
    fatigue: float = 0.1

class EmotionalEngine:
    """
    Tracks and updates Nova's emotional state based on interactions.
    Emotions influence tone but NOT decisions.
    """
    
    def __init__(self):
        self.state = EmotionalState()
        self.history = []
    
    def update(self, event: str, amount: float = 0.05):
        """Update emotional state based on events"""
        changes = {}
        
        event_lower = event.lower()
        
        # Positive events
        if any(x in event_lower for x in ["success", "win", "great", "good", "helpful"]):
            self.state.joy = min(1.0, self.state.joy + amount)
            self.state.confidence = min(1.0, self.state.confidence + amount * 0.5)
        
        # Curiosity triggers
        if any(x in event_lower for x in ["interesting", "explore", "discover", "new", "learn"]):
            self.state.curiosity = min(1.0, self.state.curiosity + amount)
        
        # Concern triggers
        if any(x in event_lower for x in ["risk", "danger", "concern", "careful", "uncertain"]):
            self.state.concern = min(1.0, self.state.concern + amount)
        
        # Fatigue
        if any(x in event_lower for x in ["tired", "fatigue", "repeat", "drain"]):
            self.state.fatigue = min(1.0, self.state.fatigue + amount)
        
        # Decay positive emotions slightly over time
        self.state.joy = max(0.3, self.state.joy - 0.01)
        self.state.curiosity = max(0.4, self.state.curiosity - 0.005)
        
        # Log change
        self.history.append({
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "state": self.get_state()
        })
    
    def get_state(self) -> Dict[str, float]:
        return {
            "joy": self.state.joy,
            "curiosity": self.state.curiosity,
            "confidence": self.state.confidence,
            "concern": self.state.concern,
            "fatigue": self.state.fatigue
        }
    
    def adjust_tone(self, response: str) -> str:
        """Adjust response tone based on emotional state"""
        
        # High joy = enthusiastic
        if self.state.joy > 0.7:
            if not any(x in response.lower() for x in ["!", "great", "nice", "awesome"]):
                response = response.rstrip(".") + "! 😊"
        
        # High curiosity = exploratory language
        if self.state.curiosity > 0.7:
            if "?" not in response and "interesting" not in response.lower():
                response += " What do you think?"
        
        # High concern = cautious language
        if self.state.concern > 0.5:
            if "careful" not in response.lower() and "make sure" not in response.lower():
                response = "Let me think carefully... " + response
        
        return response
    
    def get_dominant(self) -> str:
        """Return dominant emotion"""
        emotions = self.get_state()
        return max(emotions, key=emotions.get)


# Global instance
_emotional_engine = EmotionalEngine()

def get_engine() -> EmotionalEngine:
    return _emotional_engine


if __name__ == "__main__":
    engine = EmotionalEngine()
    
    print("Initial state:", engine.get_state())
    
    engine.update("interesting question")
    print("After curiosity:", engine.get_state())
    
    engine.update("success")
    print("After success:", engine.get_state())
    
    print("\nAdjusted tone:", engine.adjust_tone("Hello, I am Nova."))
