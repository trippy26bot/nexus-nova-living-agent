#!/usr/bin/env python3
"""
nova_exit_detector.py — Exit Detection.
Detects when to exit positions.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class ExitDetector:
    """Detects exit signals for positions."""
    
    def __init__(self):
        self.positions = {}  # token -> position data
        self.exit_signals = []
        
    def add_position(self, token: str, entry_price: float, size: float, 
                     entry_time: datetime = None):
        """Add a position to track."""
        self.positions[token] = {
            "entry_price": entry_price,
            "size": size,
            "entry_time": entry_time or datetime.now(),
            "entry_iso": (entry_time or datetime.now()).isoformat(),
            "stop_loss": entry_price * 0.85,  # 15% stop
            "take_profit_1": entry_price * 1.40,  # 40% target
            "take_profit_2": entry_price * 1.80,  # 80% target
            "trailing_stop": entry_price
        }
    
    def update_price(self, token: str, current_price: float):
        """Update current price and check exits."""
        if token not in self.positions:
            return {"has_position": False}
        
        position = self.positions[token]
        entry = position["entry_price"]
        
        # Calculate PnL
        pnl_pct = ((current_price - entry) / entry) * 100
        pnl_usd = (current_price - entry) * position["size"]
        
        # Update trailing stop
        if current_price > position["trailing_stop"]:
            position["trailing_stop"] = current_price * 0.90  # 10% trailing
        
        # Check exit signals
        signals = []
        
        # Stop loss
        if current_price <= position["stop_loss"]:
            signals.append({
                "type": "stop_loss",
                "reason": "Price hit stop loss",
                "pnl_pct": round(pnl_pct, 1),
                "action": "EXIT"
            })
        
        # Take profit 1
        if current_price >= position["take_profit_1"] and not position.get("tp1_hit"):
            signals.append({
                "type": "take_profit_1",
                "reason": "First profit target hit - exit 50%",
                "pnl_pct": round(pnl_pct, 1),
                "action": "EXIT_50%"
            })
            position["tp1_hit"] = True
        
        # Take profit 2
        if current_price >= position["take_profit_2"] and not position.get("tp2_hit"):
            signals.append({
                "type": "take_profit_2",
                "reason": "Second profit target hit - exit all",
                "pnl_pct": round(pnl_pct, 1),
                "action": "EXIT_ALL"
            })
            position["tp2_hit"] = True
        
        # Trailing stop hit
        if current_price <= position["trailing_stop"]:
            signals.append({
                "type": "trailing_stop",
                "reason": "Trailing stop triggered",
                "pnl_pct": round(pnl_pct, 1),
                "action": "EXIT"
            })
        
        # Time-based exit
        hours_held = (datetime.now() - position["entry_time"]).total_seconds() / 3600
        if hours_held > 48 and pnl_pct > 10:
            signals.append({
                "type": "time_exit",
                "reason": f"Held for {hours_held:.0f}h with profit",
                "pnl_pct": round(pnl_pct, 1),
                "action": "TAKE_PROFIT"
            })
        
        # Record signals
        for signal in signals:
            signal["token"] = token
            signal["current_price"] = current_price
            signal["entry_price"] = entry
            signal["timestamp"] = datetime.now().isoformat()
            self.exit_signals.append(signal)
        
        return {
            "has_position": True,
            "current_price": current_price,
            "entry_price": entry,
            "pnl_pct": round(pnl_pct, 1),
            "pnl_usd": round(pnl_usd, 2),
            "signals": signals,
            "should_exit": len(signals) > 0
        }
    
    def check_whale_exit(self, token: str, whale_sells: List[Dict]) -> Dict:
        """Check if whales are exiting."""
        if token not in self.positions:
            return {"has_position": False}
        
        if not whale_sells:
            return {"whale_exit_detected": False}
        
        # Large whale sells detected
        total_sell_value = sum(s.get("value", 0) for s in whale_sells)
        position_value = self.positions[token]["entry_price"] * self.positions[token]["size"]
        
        # If whale sells > 20% of position value
        if total_sell_value > position_value * 0.2:
            return {
                "whale_exit_detected": True,
                "reason": "Large whale sells detected",
                "whale_sell_value": total_sell_value,
                "position_value": position_value,
                "action": "EXIT"
            }
        
        return {"whale_exit_detected": False}
    
    def check_liquidity_exit(self, token: str, liquidity_change_pct: float) -> Dict:
        """Check liquidity for exit signal."""
        if token not in self.positions:
            return {"has_position": False}
        
        # Large liquidity drop = danger
        if liquidity_change_pct < -30:
            return {
                "liquidity_exit": True,
                "reason": "Liquidity collapsed",
                "change_pct": liquidity_change_pct,
                "action": "EXIT"
            }
        
        return {"liquidity_exit": False}
    
    def close_position(self, token: str) -> Dict:
        """Manually close a position."""
        if token in self.positions:
            position = self.positions[token]
            del self.positions[token]
            return {
                "closed": True,
                "position": position
            }
        
        return {"closed": False, "reason": "no_position"}
    
    def get_positions(self) -> List[Dict]:
        """Get all open positions."""
        return [
            {**pos, "token": token}
            for token, pos in self.positions.items()
        ]
    
    def get_exit_signals(self, limit: int = 10) -> List[Dict]:
        """Get recent exit signals."""
        return self.exit_signals[-limit:]
    
    def get_status(self) -> Dict:
        """Get detector status."""
        return {
            "open_positions": len(self.positions),
            "total_exit_signals": len(self.exit_signals)
        }


# Singleton
_exit_detector: Optional[ExitDetector] = None


def get_exit_detector() -> ExitDetector:
    """Get exit detector singleton."""
    global _exit_detector
    if _exit_detector is None:
        _exit_detector = ExitDetector()
    return _exit_detector


if __name__ == "__main__":
    import json
    detector = get_exit_detector()
    
    # Test
    detector.add_position("BONK", 0.0001, 1000000)
    result = detector.update_price("BONK", 0.00015)
    print(json.dumps(result, indent=2))
