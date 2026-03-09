"""
Volatility Brain - Detects chaotic markets
"""
from .base_brain import BaseBrain

class VolatilityBrain(BaseBrain):
    def __init__(self):
        super().__init__("volatility")
    
    def analyze(self, market_data, memory):
        vol = market_data.get("volatility", 0)
        
        if vol > 3:
            return {"action": "HOLD", "confidence": 0.6, "reason": "high volatility - too risky"}
        return {"action": "BUY", "confidence": 0.5, "reason": "normal volatility"}
