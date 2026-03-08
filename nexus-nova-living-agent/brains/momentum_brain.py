"""
Momentum Brain - Detects trend direction
"""
from .base_brain import BaseBrain

class MomentumBrain(BaseBrain):
    def __init__(self):
        super().__init__("momentum")
    
    def analyze(self, market_data, memory):
        change = market_data.get("price_change", 0)
        
        if change > 2:
            return {"action": "BUY", "confidence": 0.7, "reason": "strong upward momentum"}
        if change < -2:
            return {"action": "SELL", "confidence": 0.7, "reason": "strong downward momentum"}
        return {"action": "HOLD", "confidence": 0.4, "reason": "no clear momentum"}
