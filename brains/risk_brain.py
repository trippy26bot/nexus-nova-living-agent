"""
Risk Brain - Capital protection
"""
from .base_brain import BaseBrain

class RiskBrain(BaseBrain):
    def __init__(self):
        super().__init__("risk")
    
    def analyze(self, market_data, memory):
        risk = market_data.get("risk_level", 0)
        
        if risk > 0.8:
            return {"action": "HOLD", "confidence": 0.9, "reason": "risk too high"}
        return {"action": "BUY", "confidence": 0.4, "reason": "risk acceptable"}
