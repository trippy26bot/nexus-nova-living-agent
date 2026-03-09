"""
Guardian Brain - System health monitoring
"""
from .base_brain import BaseBrain

class GuardianBrain(BaseBrain):
    def __init__(self):
        super().__init__("guardian")
    
    def analyze(self, market_data, memory):
        system_health = memory.get("system_health", 1)
        
        if system_health < 0.5:
            return {"action": "HALT", "confidence": 1.0, "reason": "system unhealthy"}
        return {"action": "OK", "confidence": 1.0, "reason": "system healthy"}
