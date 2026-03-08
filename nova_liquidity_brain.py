#!/usr/bin/env python3
"""
nova_liquidity_brain.py — Liquidity Intelligence Engine.
Analyzes liquidity conditions for trade safety.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class LiquidityBrain:
    """Analyzes liquidity conditions."""
    
    def __init__(self):
        self.min_liquidity = 40000  # $40k minimum
        self.safe_liquidity = 100000  # $100k safe
        self.history = {}  # token -> liquidity history
    
    def analyze_token(self, token_data: Dict) -> Dict:
        """Analyze liquidity conditions for a token."""
        
        liquidity = token_data.get("liquidity", 0)
        volume = token_data.get("volume_24h", 0)
        
        # Calculate metrics
        score = 0
        factors = []
        
        # Liquidity level
        if liquidity >= 500000:
            score += 40
            factors.append({"factor": "liquidity_excellent", "score": 40})
        elif liquidity >= 200000:
            score += 30
            factors.append({"factor": "liquidity_good", "score": 30})
        elif liquidity >= self.safe_liquidity:
            score += 20
            factors.append({"factor": "liquidity_acceptable", "score": 20})
        elif liquidity >= self.min_liquidity:
            score += 10
            factors.append({"factor": "liquidity_low", "score": 10})
        else:
            factors.append({"factor": "liquidity_too_low", "score": -30})
        
        # Volume to liquidity ratio
        if liquidity > 0:
            vol_ratio = volume / liquidity
            
            if vol_ratio > 2:  # High turnover
                score += 20
                factors.append({"factor": "high_volume_activity", "score": 20})
            elif vol_ratio > 1:
                score += 10
                factors.append({"factor": "good_volume", "score": 10})
            elif vol_ratio < 0.1:
                score -= 20
                factors.append({"factor": "dead_volume", "score": -20})
        
        # Check for liquidity growth
        growth = self._check_liquidity_growth(token_data.get("token_address", ""))
        if growth > 50:
            score += 15
            factors.append({"factor": "liquidity_growing", "score": 15, "growth": growth})
        elif growth > 20:
            score += 10
            factors.append({"factor": "liquidity_stable", "score": 10})
        
        # Rug risk check
        rug_risk = self._assess_rug_risk(token_data)
        score -= rug_risk * 20
        if rug_risk > 0:
            factors.append({"factor": "rug_risk", "score": -rug_risk * 20})
        
        # Determine verdict
        if score >= 60:
            verdict = "safe"
            action = "trade"
        elif score >= 30:
            verdict = "caution"
            action = "small_position"
        else:
            verdict = "unsafe"
            action = "avoid"
        
        return {
            "token": token_data.get("symbol", "UNKNOWN"),
            "liquidity": liquidity,
            "volume": volume,
            "score": max(0, score),
            "verdict": verdict,
            "action": action,
            "factors": factors,
            "rug_risk": rug_risk,
            "timestamp": datetime.now().isoformat()
        }
    
    def _check_liquidity_growth(self, token_address: str) -> float:
        """Check liquidity growth rate."""
        if token_address not in self.history:
            return 0
        
        history = self.history[token_address]
        if len(history) < 2:
            return 0
        
        # Compare recent to older
        recent = history[-1].get("liquidity", 0)
        older = history[0].get("liquidity", 1)
        
        if older == 0:
            return 0
        
        growth = ((recent - older) / older) * 100
        return growth
    
    def _assess_rug_risk(self, token_data: Dict) -> float:
        """Assess rug pull risk."""
        risk = 0
        
        # Check liquidity lock
        if not token_data.get("liquidity_locked", True):
            risk += 2
        
        # Check mint authority
        if token_data.get("mint_authority_active", False):
            risk += 3
        
        # Check freeze authority
        if token_data.get("freeze_authority_active", False):
            risk += 1
        
        # Check dev supply
        dev_supply = token_data.get("dev_supply_percent", 0)
        if dev_supply > 20:
            risk += 2
        elif dev_supply > 10:
            risk += 1
        
        return min(5, risk)
    
    def should_trade(self, token_data: Dict) -> Dict:
        """Should Nova trade this token?"""
        analysis = self.analyze_token(token_data)
        
        # Get minimum requirements
        liquidity = token_data.get("liquidity", 0)
        
        # Hard blocks
        if liquidity < self.min_liquidity:
            return {
                "trade": False,
                "reason": "liquidity_below_minimum",
                "liquidity": liquidity,
                "required": self.min_liquidity
            }
        
        if analysis["rug_risk"] >= 3:
            return {
                "trade": False,
                "reason": "high_rug_risk",
                "risk_level": analysis["rug_risk"]
            }
        
        # Conditional trade
        if analysis["action"] == "avoid":
            return {
                "trade": False,
                "reason": "low_liquidity_score",
                "score": analysis["score"]
            }
        
        return {
            "trade": True,
            "action": analysis["action"],
            "max_position_pct": self._calculate_position_size(analysis["score"])
        }
    
    def _calculate_position_size(self, score: float) -> float:
        """Calculate position size based on liquidity score."""
        if score >= 80:
            return 5.0
        elif score >= 60:
            return 3.0
        elif score >= 40:
            return 2.0
        else:
            return 1.0
    
    def get_status(self) -> Dict:
        """Get brain status."""
        return {
            "min_liquidity": self.min_liquidity,
            "safe_liquidity": self.safe_liquidity,
            "tokens_tracked": len(self.history)
        }


# Singleton
_liquidity_brain: Optional[LiquidityBrain] = None


def get_liquidity_brain() -> LiquidityBrain:
    """Get liquidity brain singleton."""
    global _liquidity_brain
    if _liquidity_brain is None:
        _liquidity_brain = LiquidityBrain()
    return _liquidity_brain


if __name__ == "__main__":
    brain = get_liquidity_brain()
    
    test_token = {
        "symbol": "TEST",
        "liquidity": 150000,
        "volume_24h": 80000,
        "liquidity_locked": True,
        "mint_authority_active": False
    }
    
    result = brain.should_trade(test_token)
    print(json.dumps(result, indent=2))
