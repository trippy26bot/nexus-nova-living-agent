#!/usr/bin/env python3
"""
nova_pump_probability.py — Pump Probability Engine.
Estimates probability of token pump using multiple signals.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class PumpProbabilityEngine:
    """Calculates pump probability for tokens."""
    
    def __init__(self):
        # Signal weights
        self.weights = {
            "dev_reputation": 0.25,
            "whale_activity": 0.25,
            "liquidity_strength": 0.20,
            "volume_momentum": 0.20,
            "social_hype": 0.10
        }
        
        # Thresholds
        self.thresholds = {
            "ignore": 50,
            "monitor": 70,
            "trade": 85
        }
        
    def calculate(self, token_data: Dict) -> Dict:
        """Calculate pump probability score."""
        scores = {}
        
        # 1. Dev Reputation (0-25)
        scores["dev_reputation"] = self._score_dev_reputation(
            token_data.get("dev_history", {})
        )
        
        # 2. Whale Activity (0-25)
        scores["whale_activity"] = self._score_whale_activity(
            token_data.get("whale_activity", [])
        )
        
        # 3. Liquidity Strength (0-20)
        scores["liquidity_strength"] = self._score_liquidity(
            token_data.get("liquidity", 0)
        )
        
        # 4. Volume Momentum (0-20)
        scores["volume_momentum"] = self._score_volume_momentum(
            token_data.get("volume_change_1h", 0),
            token_data.get("volume_change_24h", 0)
        )
        
        # 5. Social Hype (0-10)
        scores["social_hype"] = self._score_social_hype(
            token_data.get("social_mentions", 0)
        )
        
        # Calculate weighted total
        total = sum(
            scores[key] * self.weights[key]
            for key in self.weights
        )
        
        # Determine action
        if total >= self.thresholds["trade"]:
            action = "aggressive_trade"
        elif total >= self.thresholds["monitor"]:
            action = "trade"
        elif total >= self.thresholds["ignore"]:
            action = "monitor"
        else:
            action = "ignore"
        
        return {
            "pump_score": round(total, 1),
            "action": action,
            "scores": {k: round(v, 1) for k, v in scores.items()},
            "position_sizing": self._get_position_size(total),
            "timestamp": datetime.now().isoformat()
        }
    
    def _score_dev_reputation(self, dev_history: Dict) -> float:
        """Score developer reputation."""
        if not dev_history:
            return 5.0  # Unknown dev
        
        avg_roi = dev_history.get("avg_roi", 0)
        launches = dev_history.get("launches", 0)
        rugs = dev_history.get("rugs", 0)
        
        score = 0.0
        
        # Launch count bonus
        if launches >= 5:
            score += 8
        elif launches >= 2:
            score += 5
        
        # ROI bonus
        if avg_roi >= 10:
            score += 12
        elif avg_roi >= 5:
            score += 8
        elif avg_roi >= 2:
            score += 5
        elif avg_roi >= 0.5:
            score += 2
        
        # Rug penalty
        rug_rate = rugs / launches if launches > 0 else 0
        if rug_rate > 0.5:
            score -= 25
        elif rug_rate > 0.3:
            score -= 15
        elif rug_rate > 0.1:
            score -= 5
        
        return max(0, min(25, score))
    
    def _score_whale_activity(self, whale_buys: List) -> float:
        """Score whale activity."""
        count = len(whale_buys)
        
        if count >= 3:
            return 25.0
        elif count == 2:
            return 18.0
        elif count == 1:
            return 10.0
        else:
            return 0.0
    
    def _score_liquidity(self, liquidity: float) -> float:
        """Score liquidity strength."""
        if liquidity >= 500000:  # $500k
            return 20.0
        elif liquidity >= 200000:  # $200k
            return 15.0
        elif liquidity >= 100000:  # $100k
            return 12.0
        elif liquidity >= 50000:  # $50k
            return 8.0
        elif liquidity >= 20000:  # $20k
            return 4.0
        else:
            return 0.0
    
    def _score_volume_momentum(self, change_1h: float, change_24h: float) -> float:
        """Score volume momentum."""
        # Weight recent momentum more heavily
        score = 0.0
        
        if change_1h >= 500:
            score += 12.0
        elif change_1h >= 300:
            score += 8.0
        elif change_1h >= 100:
            score += 5.0
        
        if change_24h >= 300:
            score += 8.0
        elif change_24h >= 100:
            score += 5.0
        elif change_24h >= 50:
            score += 2.0
        
        return min(20.0, score)
    
    def _score_social_hype(self, mentions: int) -> float:
        """Score social hype."""
        if mentions >= 500:
            return 10.0
        elif mentions >= 200:
            return 7.0
        elif mentions >= 100:
            return 5.0
        elif mentions >= 50:
            return 3.0
        elif mentions >= 10:
            return 2.0
        else:
            return 0.0
    
    def _get_position_size(self, score: float) -> Dict:
        """Get recommended position size based on score."""
        if score >= 90:
            return {"pct": 10, "mode": "aggressive"}
        elif score >= 80:
            return {"pct": 6, "mode": "strong"}
        elif score >= 70:
            return {"pct": 3, "mode": "normal"}
        else:
            return {"pct": 0, "mode": "none"}


# Singleton
_pump_engine: Optional[PumpProbabilityEngine] = None


def get_pump_engine() -> PumpProbabilityEngine:
    """Get pump probability engine singleton."""
    global _pump_engine
    if _pump_engine is None:
        _pump_engine = PumpProbabilityEngine()
    return _pump_engine


if __name__ == "__main__":
    engine = get_pump_engine()
    
    # Test with sample data
    sample_token = {
        "dev_history": {"launches": 3, "avg_roi": 8.5, "rugs": 0},
        "whale_activity": ["wallet1", "wallet2"],
        "liquidity": 150000,
        "volume_change_1h": 350,
        "volume_change_24h": 150,
        "social_mentions": 150
    }
    
    result = engine.calculate(sample_token)
    print(json.dumps(result, indent=2))
