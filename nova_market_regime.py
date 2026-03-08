#!/usr/bin/env python3
"""
nova_market_regime.py — Market Regime Detector.
Detects bull/bear/low-liquidity markets and adapts strategy.
"""

import json
from datetime import datetime
from typing import Dict, Optional


class MarketRegime:
    """Detects market conditions and adapts trading."""
    
    def __init__(self):
        self.current_regime = "unknown"
        self.last_update = None
        
    def analyze(self, market_data: Dict) -> Dict:
        """Analyze market conditions."""
        
        # Input data
        btc_trend = market_data.get("btc_trend", "sideways")  # up/down/sideways
        btc_change = market_data.get("btc_change_24h", 0)
        volume = market_data.get("volume", 0)
        liquidity = market_data.get("liquidity", 0)
        memecoin_momentum = market_data.get("memecoin_momentum", 0)
        
        # Determine regime
        regime = "neutral"
        confidence = 0
        adjustments = {}
        
        # Bull market
        if btc_trend == "up" and btc_change > 5:
            regime = "bull"
            confidence = 80
            adjustments = {
                "position_size_mult": 1.5,
                "stop_loss": 15,
                "take_profit": 50
            }
        
        # Bear market
        elif btc_trend == "down" and btc_change < -5:
            regime = "bear"
            confidence = 80
            adjustments = {
                "position_size_mult": 0.5,
                "stop_loss": 10,
                "take_profit": 25
            }
        
        # Low liquidity
        elif liquidity < 50000:
            regime = "low_liquidity"
            confidence = 70
            adjustments = {
                "position_size_mult": 0.3,
                "min_liquidity": 100000
            }
        
        # Memecoin season
        elif memecoin_momentum > 70:
            regime = "memecoin_season"
            confidence = 75
            adjustments = {
                "position_size_mult": 1.3,
                "focus": "memecoins"
            }
        
        # Neutral
        else:
            regime = "neutral"
            confidence = 50
            adjustments = {
                "position_size_mult": 1.0,
                "stop_loss": 12,
                "take_profit": 35
            }
        
        self.current_regime = regime
        self.last_update = datetime.now()
        
        return {
            "regime": regime,
            "confidence": confidence,
            "adjustments": adjustments,
            "indicators": {
                "btc_trend": btc_trend,
                "btc_change": btc_change,
                "liquidity": liquidity,
                "memecoin_momentum": memecoin_momentum
            }
        }
    
    def get_current_regime(self) -> str:
        """Get current regime."""
        return self.current_regime
    
    def get_adapted_params(self, base_params: Dict) -> Dict:
        """Get parameters adapted to current regime."""
        if not self.last_update or (datetime.now() - self.last_update).total_seconds() > 300:
            # Re-analyze if stale
            self.analyze({})
        
        analysis = self.analyze({})
        adjustments = analysis.get("adjustments", {})
        
        # Apply adjustments
        adapted = base_params.copy()
        
        if "position_size_mult" in adjustments:
            adapted["position_size"] = base_params.get("position_size", 2) * adjustments["position_size_mult"]
        
        if "stop_loss" in adjustments:
            adapted["stop_loss"] = adjustments["stop_loss"]
        
        if "take_profit" in adjustments:
            adapted["take_profit"] = adjustments["take_profit"]
        
        return adapted


# Singleton
_market_regime: Optional[MarketRegime] = None


def get_market_regime() -> MarketRegime:
    """Get market regime singleton."""
    global _market_regime
    if _market_regime is None:
        _market_regime = MarketRegime()
    return _market_regime


if __name__ == "__main__":
    regime = get_market_regime()
    
    test_data = {
        "btc_trend": "up",
        "btc_change_24h": 8,
        "volume": 1000000,
        "liquidity": 200000,
        "memecoin_momentum": 30
    }
    
    result = regime.analyze(test_data)
    print(json.dumps(result, indent=2))
