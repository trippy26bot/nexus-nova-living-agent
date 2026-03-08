#!/usr/bin/env python3
"""
nova_black_swan.py — Black Swan Risk Monitor.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class BlackSwanMonitor:
    """Detects catastrophic market conditions."""
    
    def __init__(self):
        self.alert_level = "NORMAL"
        self.triggered_events = []
    
    def check_conditions(self, market_data: Dict) -> Dict:
        """Check for black swan conditions."""
        
        alerts = []
        
        # Check price crash
        price_change = market_data.get("price_change_1h", 0)
        if price_change < -15:
            alerts.append({
                "type": "FLASH_CRASH",
                "severity": "CRITICAL",
                "value": price_change,
                "action": "CLOSE_ALL_POSITIONS"
            })
        elif price_change < -10:
            alerts.append({
                "type": "SEVERE_CRASH",
                "severity": "HIGH",
                "value": price_change,
                "action": "STOP_NEW_TRADES"
            })
        
        # Check volatility spike
        volatility = market_data.get("volatility", 0)
        if volatility > 0.10:
            alerts.append({
                "type": "VOLATILITY_SPIKE",
                "severity": "HIGH",
                "value": volatility,
                "action": "REDUCE_POSITION_SIZES"
            })
        
        # Check liquidity collapse
        liquidity_change = market_data.get("liquidity_change_1h", 0)
        if liquidity_change < -50:
            alerts.append({
                "type": "LIQUIDITY_COLLAPSE",
                "severity": "CRITICAL",
                "value": liquidity_change,
                "action": "EXIT_ALL"
            })
        
        # Check exchange failure (simulated)
        exchange_status = market_data.get("exchange_status", "online")
        if exchange_status == "offline":
            alerts.append({
                "type": "EXCHANGE_OFFLINE",
                "severity": "CRITICAL",
                "action": "PAUSE_TRADING"
            })
        
        # Check stablecoin depeg
        stablecoin_price = market_data.get("stablecoin_price", 1.0)
        if stablecoin_price < 0.95:
            alerts.append({
                "type": "STABLECOIN_DEPEG",
                "severity": "CRITICAL",
                "value": stablecoin_price,
                "action": "MOVE_TO_CASH"
            })
        
        # Determine alert level
        if any(a["severity"] == "CRITICAL" for a in alerts):
            self.alert_level = "CRITICAL"
        elif any(a["severity"] == "HIGH" for a in alerts):
            self.alert_level = "HIGH"
        elif alerts:
            self.alert_level = "ELEVATED"
        else:
            self.alert_level = "NORMAL"
        
        result = {
            "alert_level": self.alert_level,
            "alerts": alerts,
            "should_continue_trading": self.alert_level in ["NORMAL", "ELEVATED"],
            "recommended_action": self._get_action(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
        if alerts:
            self.triggered_events.append(result)
        
        return result
    
    def _get_action(self, alerts: List[Dict]) -> str:
        """Get recommended action."""
        if not alerts:
            return "CONTINUE_NORMAL"
        
        severities = [a["severity"] for a in alerts]
        
        if "CRITICAL" in severities:
            return "EMERGENCY_STOP"
        elif "HIGH" in severities:
            return "PAUSE_AND_MONITOR"
        else:
            return "INCREASE_CAUTION"
    
    def get_status(self) -> Dict:
        """Get monitor status."""
        return {
            "alert_level": self.alert_level,
            "total_events": len(self.triggered_events),
            "recent_events": self.triggered_events[-5:]
        }


_black_swan: Optional[BlackSwanMonitor] = None

def get_black_swan_monitor() -> BlackSwanMonitor:
    global _black_swan
    if _black_swan is None:
        _black_swan = BlackSwanMonitor()
    return _black_swan


if __name__ == "__main__":
    monitor = get_black_swan_monitor()
    result = monitor.check_conditions({"price_change_1h": -12, "volatility": 0.08})
    print(json.dumps(result, indent=2))
