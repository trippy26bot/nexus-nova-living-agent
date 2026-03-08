"""
Base Brain Class
All 14 brains inherit from this.
"""
from abc import ABC, abstractmethod

class BaseBrain(ABC):
    def __init__(self, name):
        self.name = name
    
    @abstractmethod
    def analyze(self, market_data, memory):
        """
        Each brain must return a vote.
        Returns: {"action": "BUY"|"SELL"|"HOLD"|"HALT", "confidence": 0.0-1.0, "reason": "..."}
        """
        pass
