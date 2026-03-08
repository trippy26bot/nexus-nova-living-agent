#!/usr/bin/env python3
"""
nova_trap_detector.py — Trap Detection Engine.
Detects rug setups and insider exit traps.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class TrapDetector:
    """Detects rug and trap patterns."""
    
    def __init__(self):
        self.trade_history = {}  # token -> entry data
    
    def analyze(self, token: str, data: Dict) -> Dict:
        """Analyze for trap patterns."""
        
        trap_signals = {}
        
        # 1. Insider coordinated exit trap
        trap_signals["coordinated_exit"] = self._check_coordinated_exit(data)
        
        # 2. Liquidity pull trap
        trap_signals["liquidity_pull"] = self._check_liquidity_pull(data)
        
        # 3. Dev dumping trap
        trap_signals["dev_dump"] = self._check_dev_dump(data)
        
        # 4. Supply concentration trap
        trap_signals["supply_concentration"] = self._check_supply_concentration(data)
        
        # 5. Fake volume trap
        trap_signals["fake_volume"] = self._check_fake_volume(data)
        
        # Calculate trap score
        trap_score = 0
        for signal, result in trap_signals.items():
            if result.get("detected"):
                trap_score += result.get("weight", 0.2) * 100
        
        trap_score = min(100, trap_score)
        
        # Determine action
        if trap_score >= 45:
            action = "BLOCK"
            reason = "High trap probability"
        elif trap_score >= 25:
            action = "CAUTION"
            reason = "Moderate trap risk"
        else:
            action = "CLEAR"
            reason = "No trap signals"
        
        return {
            "token": token,
            "trap_score": round(trap_score, 1),
            "action": action,
            "reason": reason,
            "signals": trap_signals,
            "timestamp": datetime.now().isoformat()
        }
    
    def _check_coordinated_exit(self, data: Dict) -> Dict:
        """Check for coordinated insider exit."""
        whale_exits = data.get("whale_exits", 0)
        recent_sells = data.get("recent_sells", 0)
        
        # Multiple whale sells within short window = possible trap
        detected = recent_sells >= 3 or (whale_exits > 0 and recent_sells > whale_exits)
        
        return {
            "detected": detected,
            "weight": 0.35,
            "message": "Coordinated exit pattern detected" if detected else "No coordinated exit"
        }
    
    def _check_liquidity_pull(self, data: Dict) -> Dict:
        """Check for liquidity pull trap."""
        liquidity_locked = data.get("liquidity_locked", True)
        liquidity_change = data.get("liquidity_change_1h", 0)
        
        # Liquidity being removed or not locked = danger
        detected = not liquidity_locked or liquidity_change < -20
        
        return {
            "detected": detected,
            "weight": 0.30,
            "message": "Liquidity risk detected" if detected else "Liquidity safe"
        }
    
    def _check_dev_dump(self, data: Dict) -> Dict:
        """Check for developer dumping."""
        dev_sells = data.get("dev_sells", 0)
        dev_holds = data.get("dev_supply_percent", 0)
        
        # Dev selling or holding too much = danger
        detected = dev_sells > 0 or dev_holds > 25
        
        return {
            "detected": detected,
            "weight": 0.20,
            "message": "Dev dumping detected" if detected else "Dev not dumping"
        }
    
    def _check_supply_concentration(self, data: Dict) -> Dict:
        """Check for dangerous supply concentration."""
        top_holder_pct = data.get("top_holder_percent", 0)
        
        # Top holders controlling too much = trap risk
        detected = top_holder_pct > 40
        
        return {
            "detected": detected,
            "weight": 0.10,
            "message": "High concentration risk" if detected else "Supply distribution OK"
        }
    
    def _check_fake_volume(self, data: Dict) -> Dict:
        """Check for fake volume."""
        unique_traders = data.get("unique_traders", 100)
        total_trades = data.get("total_trades", 0)
        
        # Very few unique traders with many trades = wash trading
        if total_trades > 0:
            trader_ratio = unique_traders / total_trades
            detected = trader_ratio < 0.3
        else:
            detected = False
        
        return {
            "detected": detected,
            "weight": 0.05,
            "message": "Possible wash trading" if detected else "Volume appears real"
        }


# Singleton
_trap_detector: Optional[TrapDetector] = None


def get_trap_detector() -> TrapDetector:
    """Get trap detector singleton."""
    global _trap_detector
    if _trap_detector is None:
        _trap_detector = TrapDetector()
    return _trap_detector


if __name__ == "__main__":
    result = get_trap_detector().analyze("TEST", {})
    print(json.dumps(result, indent=2))
