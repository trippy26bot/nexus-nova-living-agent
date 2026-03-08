#!/usr/bin/env python3
"""
nova_brain.py — Unified Trading Brain.
Combines all signals into trading decisions.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

from nova_pump_probability import get_pump_engine
from nova_whale_hunter import get_whale_hunter
from nova_dev_intelligence import get_dev_intelligence
from nova_rug_detector import get_rug_detector
from nova_narrative_detector import get_narrative_detector
from nova_risk_engine import get_risk_engine


class TradingBrain:
    """Unified brain combining all signals."""
    
    def __init__(self):
        # Signal weights
        self.weights = {
            "whale_score": 0.30,
            "liquidity_score": 0.20,
            "dev_score": 0.20,
            "narrative_score": 0.15,
            "momentum_score": 0.15
        }
        
        # Thresholds
        self.thresholds = {
            "aggressive": 0.85,
            "normal": 0.70,
            "caution": 0.50
        }
        
        # Components
        self.pump_engine = get_pump_engine()
        self.whale_hunter = get_whale_hunter()
        self.dev_intel = get_dev_intelligence()
        self.rug_detector = get_rug_detector()
        self.narrative = get_narrative_detector()
        self.risk = get_risk_engine()
        
    def evaluate_token(self, token_data: Dict) -> Dict:
        """Evaluate a token using all signals."""
        
        # 1. Whale score (0-1)
        whale_score = self._score_whales(token_data)
        
        # 2. Liquidity score (0-1)
        liquidity_score = self._score_liquidity(token_data)
        
        # 3. Dev score (0-1)
        dev_score = self._score_dev(token_data)
        
        # 4. Narrative score (0-1)
        narrative_score = self._score_narrative(token_data)
        
        # 5. Momentum score (0-1)
        momentum_score = self._score_momentum(token_data)
        
        # Calculate weighted alpha score
        alpha_score = (
            whale_score * self.weights["whale_score"] +
            liquidity_score * self.weights["liquidity_score"] +
            dev_score * self.weights["dev_score"] +
            narrative_score * self.weights["narrative_score"] +
            momentum_score * self.weights["momentum_score"]
        )
        
        # Rug check
        rug_check = self.rug_detector.analyze_token(token_data)
        
        # Determine action
        if rug_check["verdict"] == "avoid":
            action = "BLOCKED"
            reason = f"Rug risk: {rug_check['risk_score']}%"
        elif alpha_score >= self.thresholds["aggressive"]:
            action = "AGGRESSIVE"
            reason = "High confidence signal"
        elif alpha_score >= self.thresholds["normal"]:
            action = "BUY"
            reason = "Good opportunity"
        elif alpha_score >= self.thresholds["caution"]:
            action = "WATCH"
            reason = "Moderate signal"
        else:
            action = "SKIP"
            reason = "Below threshold"
        
        return {
            "token": token_data.get("symbol", "UNKNOWN"),
            "address": token_data.get("address", ""),
            "chain": token_data.get("chain", "unknown"),
            "alpha_score": round(alpha_score, 3),
            "action": action,
            "reason": reason,
            "components": {
                "whale_score": round(whale_score, 2),
                "liquidity_score": round(liquidity_score, 2),
                "dev_score": round(dev_score, 2),
                "narrative_score": round(narrative_score, 2),
                "momentum_score": round(momentum_score, 2)
            },
            "rug_check": {
                "verdict": rug_check["verdict"],
                "risk_score": rug_check["risk_score"]
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _score_whales(self, token_data: Dict) -> float:
        """Score whale activity."""
        whale_buys = token_data.get("whale_buys", [])
        
        if len(whale_buys) >= 3:
            return 1.0
        elif len(whale_buys) == 2:
            return 0.7
        elif len(whale_buys) == 1:
            return 0.4
        return 0.1
    
    def _score_liquidity(self, token_data: Dict) -> float:
        """Score liquidity."""
        liquidity = token_data.get("liquidity", 0)
        
        if liquidity >= 1000000:
            return 1.0
        elif liquidity >= 500000:
            return 0.8
        elif liquidity >= 200000:
            return 0.6
        elif liquidity >= 100000:
            return 0.4
        elif liquidity >= 50000:
            return 0.2
        return 0.0
    
    def _score_dev(self, token_data: Dict) -> float:
        """Score developer reputation."""
        dev_address = token_data.get("dev_address", "")
        
        if not dev_address:
            return 0.3
        
        score_data = self.dev_intel.get_dev_score(dev_address)
        score = score_data.get("score", 0)
        
        return score / 100  # Convert 0-100 to 0-1
    
    def _score_narrative(self, token_data: Dict) -> float:
        """Score narrative alignment."""
        # Get current hot narratives
        try:
            narratives = self.narrative.get_hot_narratives(threshold=30)
        except:
            narratives = []
        
        symbol = token_data.get("symbol", "").lower()
        
        # Check if token matches hot narrative
        for narrative in narratives:
            try:
                tokens = self.narrative.get_trending_tokens(narrative)
            except:
                tokens = []
            
            for t in tokens:
                if symbol in t.get("symbol", "").lower():
                    return 0.8
        
        return 0.2
    
    def _score_momentum(self, token_data: Dict) -> float:
        """Score price momentum."""
        change_24h = token_data.get("price_change_24h", 0)
        volume = token_data.get("volume_24h", 0)
        
        score = 0.0
        
        # Price momentum
        if 10 < change_24h < 100:
            score += 0.5
        elif 0 < change_24h <= 10:
            score += 0.3
        
        # Volume momentum
        if volume > 1000000:
            score += 0.5
        elif volume > 500000:
            score += 0.3
        elif volume > 100000:
            score += 0.1
        
        return min(1.0, score)
    
    def get_decision(self, token_data: Dict, portfolio_value: float = 10000) -> Dict:
        """Get full trading00) -> Dict decision with risk check."""
        evaluation = self.evaluate_token(token_data)
        
        # Build trade for risk check
        position_size_pct = self._get_position_size(evaluation["alpha_score"])
        trade_value = portfolio_value * (position_size_pct / 100)
        
        risk_check = self.risk.can_trade(
            {"value_usd": trade_value},
            portfolio_value
        )
        
        # Final decision
        if evaluation["action"] == "BLOCKED":
            final_action = "NO_TRADE"
            final_reason = "Failed security: " + evaluation["reason"]
        elif not risk_check["approved"]:
            final_action = "NO_TRADE"
            final_reason = f"Risk check failed: {risk_check['checks']}"
        else:
            final_action = evaluation["action"]
            final_reason = evaluation["reason"]
        
        return {
            "evaluation": evaluation,
            "risk_check": risk_check,
            "position_size": {
                "percent": position_size_pct,
                "usd": trade_value
            },
            "final_action": final_action,
            "final_reason": final_reason,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_position_size(self, alpha_score: float) -> float:
        """Get position size based on alpha score."""
        if alpha_score >= 0.85:
            return 10.0
        elif alpha_score >= 0.70:
            return 6.0
        elif alpha_score >= 0.50:
            return 3.0
        else:
            return 0.0


# Singleton
_trading_brain: Optional[TradingBrain] = None


def get_trading_brain() -> TradingBrain:
    """Get trading brain singleton."""
    global _trading_brain
    if _trading_brain is None:
        _trading_brain = TradingBrain()
    return _trading_brain


if __name__ == "__main__":
    brain = get_trading_brain()
    
    # Test with sample token
    sample = {
        "symbol": "BONK",
        "address": "DezXAZ8z7PnrnRJjz3wXBoYMixPtokaEWEB21Hb4XsA",
        "chain": "solana",
        "whale_buys": ["wallet1", "wallet2"],
        "liquidity": 300000,
        "price_change_24h": 25,
        "volume_24h": 800000,
        "dev_address": ""
    }
    
    result = brain.get_decision(sample)
    print(json.dumps(result, indent=2, default=str))
