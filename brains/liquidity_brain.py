"""
Liquidity Brain - Detects thin markets
"""
from .base_brain import BaseBrain

class LiquidityBrain(BaseBrain):
    def __init__(self):
        super().__init__("liquidity")
    
    def analyze(self, market_data, memory):
        liquidity = market_data.get("liquidity", 0)
        
        if liquidity < 1:
            return {"action": "HOLD", "confidence": 0.7, "reason": "low liquidity - slippage risk"}
        return {"action": "BUY", "confidence": 0.5, "reason": "liquidity adequate"}
