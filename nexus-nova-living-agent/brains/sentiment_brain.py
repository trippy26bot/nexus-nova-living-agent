"""
Sentiment Brain - Market mood analysis
"""
from .base_brain import BaseBrain

class SentimentBrain(BaseBrain):
    def __init__(self):
        super().__init__("sentiment")
    
    def analyze(self, market_data, memory):
        sentiment = market_data.get("sentiment", 0)
        
        if sentiment > 0.6:
            return {"action": "BUY", "confidence": 0.7, "reason": "bullish sentiment"}
        if sentiment < -0.6:
            return {"action": "SELL", "confidence": 0.7, "reason": "bearish sentiment"}
        return {"action": "HOLD", "confidence": 0.5, "reason": "neutral sentiment"}
