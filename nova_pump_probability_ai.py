#!/usr/bin/env python3
"""
nova_pump_probability_ai.py — Pump Probability AI.
Outputs 0-100 probability score for pump.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

from nova_whale_cluster_brain import get_whale_cluster_brain
from nova_stealth_accumulation_detector import get_stealth_detector
from nova_liquidity_brain import get_liquidity_brain
from nova_graph_intelligence_engine import get_graph_engine


class PumpProbabilityAI:
    """AI that outputs pump probability score."""
    
    def __init__(self):
        self.whale_brain = get_whale_cluster_brain()
        self.stealth_detector = get_stealth_detector()
        self.liquidity_brain = get_liquidity_brain()
        self.graph_engine = get_graph_engine()
        
    def calculate(self, token: str, data: Dict) -> Dict:
        """Calculate pump probability (0-100)."""
        
        # Weights for final score
        weights = {
            "whale_cluster": 0.30,
            "stealth": 0.20,
            "liquidity": 0.25,
            "network": 0.15,
            "momentum": 0.10
        }
        
        scores = {}
        
        # 1. Whale/Cluster Score (0-100)
        whale_score = self._score_whale_cluster(data)
        scores["whale_cluster"] = whale_score
        
        # 2. Stealth Accumulation Score (0-100)
        stealth_score = self._score_stealth(token, data)
        scores["stealth"] = stealth_score
        
        # 3. Liquidity Score (0-100)
        liquidity_score = self._score_liquidity(token, data)
        scores["liquidity"] = liquidity_score
        
        # 4. Network/Graph Score (0-100)
        network_score = self._score_network(token, data)
        scores["network"] = network_score
        
        # 5. Momentum Score (0-100)
        momentum_score = self._score_momentum(data)
        scores["momentum"] = momentum_score
        
        # Calculate weighted total
        pump_probability = sum(scores[k] * weights[k] for k in weights)
        
        # Determine confidence
        if pump_probability >= 75:
            confidence = "VERY HIGH"
        elif pump_probability >= 60:
            confidence = "HIGH"
        elif pump_probability >= 45:
            confidence = "MEDIUM"
        elif pump_probability >= 30:
            confidence = "LOW"
        else:
            confidence = "VERY LOW"
        
        # Determine action
        if pump_probability >= 80:
            action = "AGGRESSIVE"
        elif pump_probability >= 65:
            action = "BUY"
        elif pump_probability >= 50:
            action = "WATCH"
        else:
            action = "AVOID"
        
        return {
            "token": token,
            "pump_probability": round(pump_probability, 1),
            "confidence": confidence,
            "action": action,
            "scores": {k: round(v, 1) for k, v in scores.items()},
            "weights": weights,
            "timestamp": datetime.now().isoformat()
        }
    
    def _score_whale_cluster(self, data: Dict) -> float:
        """Score whale/cluster activity."""
        trades = data.get("recent_trades", [])
        
        if not trades:
            return 10
        
        # Use whale cluster brain
        result = self.whale_brain.get_confidence_for_signal(data.get("symbol", ""), trades)
        
        return result.get("final_confidence", 0) * 100
    
    def _score_stealth(self, token: str, data: Dict) -> float:
        """Score stealth accumulation."""
        # Record recent buys
        trades = data.get("recent_trades", [])
        for trade in trades:
            self.stealth_detector.record_buy(
                trade.get("wallet", ""),
                token,
                trade.get("amount", 0)
            )
        
        # Check for stealth pattern
        detection = self.stealth_detector.detect_stealth(token)
        
        if detection.get("detected"):
            return detection.get("stealth_score", 0)
        
        return 10
    
    def _score_liquidity(self, token: str, data: Dict) -> float:
        """Score liquidity conditions."""
        token_data = {
            "symbol": token,
            "liquidity": data.get("liquidity", 0),
            "volume_24h": data.get("volume_24h", 0)
        }
        
        analysis = self.liquidity_brain.analyze_token(token_data)
        
        return analysis.get("score", 0)
    
    def _score_network(self, token: str, data: Dict) -> float:
        """Score network/graph relationships."""
        # Detect insider network
        network = self.graph_engine.detect_insider_network(token)
        
        if network.get("detected"):
            return network.get("insider_score", 0)
        
        return 10
    
    def _score_momentum(self, data: Dict) -> float:
        """Score price/volume momentum."""
        score = 0
        
        # Price change
        price_change = data.get("price_change_24h", 0)
        if 10 < price_change < 100:
            score += 40
        elif 5 < price_change <= 10:
            score += 25
        elif 0 < price_change <= 5:
            score += 15
        
        # Volume spike
        volume = data.get("volume_24h", 0)
        if volume > 500000:
            score += 30
        elif volume > 100000:
            score += 20
        elif volume > 50000:
            score += 10
        
        # Buy/sell ratio
        buys = data.get("buys", 0)
        sells = data.get("sells", 0)
        if sells > 0:
            ratio = buys / sells
            if ratio > 3:
                score += 30
            elif ratio > 1.5:
                score += 20
            elif ratio > 1:
                score += 10
        
        return min(100, score)
    
    def get_signal_summary(self, probability_result: Dict) -> str:
        """Get human-readable summary."""
        p = probability_result["pump_probability"]
        action = probability_result["action"]
        confidence = probability_result["confidence"]
        
        return f"""
🚨 PUMP SIGNAL: {probability_result['token']}

Probability: {p}% ({confidence})
Action: {action}

Score Breakdown:
• Whales/Clusters: {probability_result['scores']['whale_cluster']}
• Stealth Accumulation: {probability_result['scores']['stealth']}
• Liquidity: {probability_result['scores']['liquidity']}
• Network: {probability_result['scores']['network']}
• Momentum: {probability_result['scores']['momentum']}
"""


# Singleton
_pump_ai: Optional[PumpProbabilityAI] = None


def get_pump_probability_ai() -> PumpProbabilityAI:
    """Get pump probability AI singleton."""
    global _pump_ai
    if _pump_ai is None:
        _pump_ai = PumpProbabilityAI()
    return _pump_ai


if __name__ == "__main__":
    ai = get_pump_probability_ai()
    
    test_data = {
        "symbol": "TEST",
        "recent_trades": [
            {"wallet": "whale1", "amount": 500},
            {"wallet": "whale2", "amount": 300}
        ],
        "liquidity": 200000,
        "volume_24h": 150000,
        "price_change_24h": 15,
        "buys": 150,
        "sells": 80
    }
    
    result = ai.calculate("TEST", test_data)
    print(json.dumps(result, indent=2))
    print(ai.get_signal_summary(result))
