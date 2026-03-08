"""
Breakout Brain - Catches volatility expansion
"""
from .base_brain import BaseBrain

class BreakoutBrain(BaseBrain):
    def __init__(self):
        super().__init__("breakout")
    
    def analyze(self, market_data, memory):
        breakout = market_data.get("breakout", False)
        
        if breakout:
            return {"action": "BUY", "confidence": 0.75, "reason": "breakout detected"}
        return {"action": "HOLD", "confidence": 0.5, "reason": "no breakout"}
