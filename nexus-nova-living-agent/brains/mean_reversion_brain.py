"""
Mean Reversion Brain - Fades extremes
"""
from .base_brain import BaseBrain

class MeanReversionBrain(BaseBrain):
    def __init__(self):
        super().__init__("mean_reversion")
    
    def analyze(self, market_data, memory):
        deviation = market_data.get("mean_deviation", 0)
        
        if deviation > 2:
            return {"action": "SELL", "confidence": 0.6, "reason": "price above mean - reversion expected"}
        if deviation < -2:
            return {"action": "BUY", "confidence": 0.6, "reason": "price below mean - reversion expected"}
        return {"action": "HOLD", "confidence": 0.4, "reason": "price near mean"}
