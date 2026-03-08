"""
Portfolio Brain - Exposure management
"""
from .base_brain import BaseBrain

class PortfolioBrain(BaseBrain):
    def __init__(self):
        super().__init__("portfolio")
    
    def analyze(self, market_data, memory):
        exposure = memory.get("portfolio_exposure", 0)
        
        if exposure > 0.8:
            return {"action": "SELL", "confidence": 0.6, "reason": "overexposed"}
        return {"action": "HOLD", "confidence": 0.5, "reason": "exposure okay"}
