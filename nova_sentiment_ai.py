#!/usr/bin/env python3
"""
nova_sentiment_ai.py — Market Sentiment Analysis.
"""

import json
from datetime import datetime
from typing import Dict, Optional


class SentimentAI:
    """Analyzes market sentiment from multiple sources."""
    
    def __init__(self):
        self.sentiment_history = []
    
    def analyze_sentiment(self, data: Dict) -> Dict:
        """Analyze sentiment from available data."""
        
        # In production: analyze Twitter, Reddit, News
        # For now: use available signals
        
        fear_greed = data.get("fear_greed_index", 50)
        volume = data.get("volume_change", 0)
        price_change = data.get("price_change_24h", 0)
        
        # Calculate sentiment score
        score = 50  # neutral
        
        # Fear & Greed
        if fear_greed < 25:
            score -= 20
            sentiment = "EXTREME_FEAR"
        elif fear_greed < 40:
            score -= 10
            sentiment = "FEAR"
        elif fear_greed > 75:
            score += 20
            sentiment = "EXTREME_GREED"
        elif fear_greed > 60:
            score += 10
            sentiment = "GREED"
        else:
            sentiment = "NEUTRAL"
        
        # Volume
        if volume > 50:
            score += 15 * (volume / 100)
        
        # Price
        if price_change > 10:
            score += 15
        elif price_change > 5:
            score += 10
        elif price_change < -10:
            score -= 15
        elif price_change < -5:
            score -= 10
        
        score = max(0, min(100, score))
        
        result = {
            "sentiment": sentiment,
            "score": round(score, 1),
            "fear_greed": fear_greed,
            "volume_change": volume,
            "price_change_24h": price_change,
            "interpretation": self._interpret(score),
            "timestamp": datetime.now().isoformat()
        }
        
        self.sentiment_history.append(result)
        
        return result
    
    def _interpret(self, score: float) -> str:
        """Interpret sentiment score."""
        if score >= 80:
            return "Euphoria - caution advised"
        elif score >= 65:
            return "Bullish - momentum likely"
        elif score >= 45:
            return "Neutral - balanced market"
        elif score >= 30:
            return "Bearish - selling pressure"
        else:
            return "Panic - potential bottom"
    
    def detect_spike(self) -> Dict:
        """Detect sentiment spike."""
        if len(self.sentiment_history) < 2:
            return {"spike": False}
        
        recent = self.sentiment_history[-1]["score"]
        previous = self.sentiment_history[-2]["score"]
        
        change = abs(recent - previous)
        
        if change > 30:
            return {
                "spike": True,
                "type": "BULLISH" if recent > previous else "BEARISH",
                "change": change,
                "from": previous,
                "to": recent
            }
        
        return {"spike": False}


_sentiment: Optional[SentimentAI] = None

def get_sentiment_ai() -> SentimentAI:
    global _sentiment
    if _sentiment is None:
        _sentiment = SentimentAI()
    return _sentiment


if __name__ == "__main__":
    ai = get_sentiment_ai()
    result = ai.analyze_sentiment({"fear_greed_index": 70, "volume_change": 30, "price_change_24h": 5})
    print(json.dumps(result, indent=2))
