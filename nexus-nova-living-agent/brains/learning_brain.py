"""
Learning Brain - Performance tracking and adaptation
"""
from .base_brain import BaseBrain

class LearningBrain(BaseBrain):
    def __init__(self):
        super().__init__("learning")
    
    def analyze(self, market_data, memory):
        # This brain triggers learning updates
        return {"action": "LEARN", "confidence": 0.5, "reason": "update brain weights"}
