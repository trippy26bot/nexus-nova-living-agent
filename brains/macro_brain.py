"""
Macro Brain - Economic trend analysis
"""
from .base_brain import BaseBrain

class MacroBrain(BaseBrain):
    def __init__(self):
        super().__init__("macro")
    
    def analyze(self, market_data, memory):
        macro = market_data.get("macro_trend", "neutral")
        
        if macro == "bullish":
            return {"action": "BUY", "confidence": 0.6, "reason": "macro bullish"}
        if macro == "bearish":
            return {"action": "SELL", "confidence": 0.6, "reason": "macro bearish"}
        return {"action": "HOLD", "confidence": 0.5, "reason": "macro neutral"}
