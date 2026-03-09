"""
Arbitrage Brain - Price inefficiency detection
"""
from .base_brain import BaseBrain

class ArbitrageBrain(BaseBrain):
    def __init__(self):
        super().__init__("arbitrage")
    
    def analyze(self, market_data, memory):
        spread = market_data.get("spread", 0)
        
        if spread > 1:
            return {"action": "BUY", "confidence": 0.65, "reason": "spread opportunity"}
        return {"action": "HOLD", "confidence": 0.4, "reason": "no arbitrage"}
