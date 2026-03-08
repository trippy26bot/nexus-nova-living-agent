#!/usr/bin/env python3
"""
nova_risk_engine.py — Risk management for Nova's trading.
Enforces position limits, stop losses, and safety rules.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class RiskEngine:
    """Risk management engine for trading."""
    
    def __init__(self, config: Dict = None):
        # Default limits
        self.limits = {
            "max_position_pct": 10,        # 10% of portfolio per trade
            "max_daily_loss_pct": 5,       # 5% max daily loss
            "max_open_trades": 6,          # Max concurrent trades
            "stop_loss_pct": 15,           # 15% stop loss
            "take_profit_pct": 40,         # 40% take profit
            "max_single_trade_usd": 1000,  # $1000 max per trade
            "min_trade_size_usd": 10,      # $10 min trade
            "cooldown_minutes": 15,        # Cooldown after loss
            "max_trades_per_hour": 10,     # Rate limiting
        }
        
        if config:
            self.limits.update(config)
        
        # State
        self.daily_loss = 0.0
        self.daily_trades = 0
        self.open_positions = []
        self.trade_timestamps = []
        self.last_loss_time = None
        self.last_reset = datetime.now()
    
    def can_trade(self, trade: Dict, portfolio_value: float) -> Dict:
        """Check if a trade passes risk checks."""
        checks = {}
        
        # Check 1: Daily loss limit
        if self.daily_loss > 0:
            loss_pct = (self.daily_loss / portfolio_value) * 100
            checks["daily_loss"] = {
                "passed": loss_pct < self.limits["max_daily_loss_pct"],
                "current": f"{loss_pct:.1f}%",
                "limit": f"{self.limits['max_daily_loss_pct']}%"
            }
        
        # Check 2: Max open positions
        checks["open_positions"] = {
            "passed": len(self.open_positions) < self.limits["max_open_trades"],
            "current": len(self.open_positions),
            "limit": self.limits["max_open_trades"]
        }
        
        # Check 3: Position size
        trade_value = trade.get("value_usd", 0)
        position_pct = (trade_value / portfolio_value) * 100 if portfolio_value > 0 else 100
        
        checks["position_size"] = {
            "passed": position_pct <= self.limits["max_position_pct"] and trade_value <= self.limits["max_single_trade_usd"],
            "current": f"${trade_value:.0f} ({position_pct:.1f}%)",
            "limit": f"{self.limits['max_position_pct']}% or ${self.limits['max_single_trade_usd']}"
        }
        
        # Check 4: Minimum trade size
        checks["min_size"] = {
            "passed": trade_value >= self.limits["min_trade_size_usd"],
            "current": f"${trade_value:.0f}",
            "limit": f"${self.limits['min_trade_size_usd']}"
        }
        
        # Check 5: Rate limiting
        self._clean_timestamps()
        recent_trades = len(self.trade_timestamps)
        checks["rate_limit"] = {
            "passed": recent_trades < self.limits["max_trades_per_hour"],
            "current": recent_trades,
            "limit": self.limits["max_trades_per_hour"]
        }
        
        # Check 6: Cooldown after loss
        if self.last_loss_time:
            cooldown_end = self.last_loss_time + timedelta(minutes=self.limits["cooldown_minutes"])
            checks["cooldown"] = {
                "passed": datetime.now() > cooldown_end,
                "remaining": str(cooldown_end - datetime.now()).split('.')[0] if datetime.now() < cooldown_end else "ready"
            }
        
        # Overall pass/fail
        all_passed = all(
            check.get("passed", False) 
            for check in checks.values() 
            if "passed" in check
        )
        
        return {
            "approved": all_passed,
            "checks": checks,
            "timestamp": datetime.now().isoformat()
        }

    def evaluate(self, trade: Dict, portfolio_value: float = 10000.0) -> Dict:
        """Compatibility wrapper used by older callers."""
        return self.can_trade(trade, portfolio_value)
    
    def check_exit(self, position: Dict, current_price: float) -> Dict:
        """Check if position should exit."""
        entry_price = position.get("entry_price", 0)
        if entry_price == 0:
            return {"should_exit": False, "reason": "no entry price"}
        
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        
        # Stop loss check
        if pnl_pct <= -self.limits["stop_loss_pct"]:
            return {
                "should_exit": True,
                "reason": "stop_loss",
                "pnl_pct": pnl_pct,
                "limit": -self.limits["stop_loss_pct"]
            }
        
        # Take profit check
        if pnl_pct >= self.limits["take_profit_pct"]:
            return {
                "should_exit": True,
                "reason": "take_profit",
                "pnl_pct": pnl_pct,
                "limit": self.limits["take_profit_pct"]
            }
        
        return {"should_exit": False, "reason": "within_limits", "pnl_pct": pnl_pct}
    
    def open_position(self, position: Dict):
        """Record opening a position."""
        self.open_positions.append({
            **position,
            "opened_at": datetime.now().isoformat()
        })
        self._add_trade_timestamp()
    
    def close_position(self, position_id: str, pnl: float):
        """Record closing a position."""
        self.open_positions = [
            p for p in self.open_positions 
            if p.get("id") != position_id
        ]
        
        self.daily_loss += pnl if pnl < 0 else 0
        self._add_trade_timestamp()
        
        if pnl < 0:
            self.last_loss_time = datetime.now()
    
    def reset_daily(self):
        """Reset daily counters."""
        now = datetime.now()
        if now.date() > self.last_reset.date():
            self.daily_loss = 0.0
            self.daily_trades = 0
            self.last_reset = now
    
    def _add_trade_timestamp(self):
        """Add current timestamp to trade log."""
        self.trade_timestamps.append(datetime.now())
    
    def _clean_timestamps(self):
        """Remove timestamps older than 1 hour."""
        cutoff = datetime.now() - timedelta(hours=1)
        self.trade_timestamps = [
            ts for ts in self.trade_timestamps 
            if ts > cutoff
        ]
    
    def get_status(self) -> Dict:
        """Get current risk status."""
        return {
            "daily_loss": self.daily_loss,
            "open_positions": len(self.open_positions),
            "recent_trades_1h": len(self.trade_timestamps),
            "limits": self.limits,
            "in_cooldown": self.last_loss_time is not None and 
                          datetime.now() < self.last_loss_time + timedelta(minutes=self.limits["cooldown_minutes"])
        }
    
    def save_state(self, path: Path):
        """Save risk state to disk."""
        state = {
            "daily_loss": self.daily_loss,
            "open_positions": self.open_positions,
            "last_reset": self.last_reset.isoformat(),
            "last_loss_time": self.last_loss_time.isoformat() if self.last_loss_time else None
        }
        path.write_text(json.dumps(state, indent=2))
    
    def load_state(self, path: Path):
        """Load risk state from disk."""
        if not path.exists():
            return
        
        try:
            state = json.loads(path.read_text())
            self.daily_loss = state.get("daily_loss", 0)
            self.open_positions = state.get("open_positions", [])
            self.last_reset = datetime.fromisoformat(state.get("last_reset", datetime.now().isoformat()))
            if state.get("last_loss_time"):
                self.last_loss_time = datetime.fromisoformat(state["last_loss_time"])
        except Exception as e:
            print(f"Error loading risk state: {e}")


# Singleton
_risk_engine: Optional[RiskEngine] = None


def get_risk_engine(config: Dict = None) -> RiskEngine:
    """Get risk engine singleton."""
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = RiskEngine(config)
    return _risk_engine


if __name__ == "__main__":
    engine = get_risk_engine()
    print("Risk engine initialized")
    print(json.dumps(engine.get_status(), indent=2))
