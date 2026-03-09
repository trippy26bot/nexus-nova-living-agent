"""
Simulation Brain - Scenario testing
"""
from .base_brain import BaseBrain

class SimulationBrain(BaseBrain):
    def __init__(self):
        super().__init__("simulation")
    
    def analyze(self, market_data, memory):
        # This brain triggers simulation before trades
        return {"action": "SIMULATE", "confidence": 0.5, "reason": "run scenario test"}
