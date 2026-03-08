#!/usr/bin/env python3
"""
nova_trading_brain.py — Nova's unified trading brain.
Combines market scanning, strategy, risk management, and execution.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum


class Signal(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    WATCH = "watch"


class TradingBrain:
    """Unified trading brain for Nova."""
    
    def __init__(self, config_path: str = None):
        self.base_dir = Path(__file__).parent
        self.config = self._load_config(config_path)
        self.strategies = {}
        self.trade_history = []
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load trading configuration."""
        if config_path and Path(config_path).exists():
            return json.loads(Path(config_path).read_text())
        
        # Default config
        return {
            "max_position_pct": 10,      # 10% max per trade
            "max_daily_loss_pct": 5,       # 5% max daily loss
            "max_open_trades": 6,
            "stop_loss_pct": 15,
            "take_profit_pct": 40,
            "min_liquidity": 100000,      # $100k min liquidity
            "min_volume_24h": 50000,       # $50k min volume
            "scanner_interval": 60,        # seconds
            "enabled_markets": ["solana", "polymarket"]
        }
    
    def evaluate(self, market_data: Dict) -> Dict:
        """Evaluate market data and return trading decision."""
        signal = Signal.HOLD
        confidence = 0.0
        reasoning = []
        
        # Run each strategy
        for name, strategy in self.strategies.items():
            result = strategy.evaluate(market_data)
            if result["signal"] != Signal.HOLD.value:
                reasoning.append(f"{name}: {result['signal']} ({result['confidence']})")
                confidence += result["confidence"]
        
        if confidence > 0:
            confidence = min(1.0, confidence / len(self.strategies))
            signal = Signal.BUY if confidence > 0.6 else Signal.WATCH
        
        return {
            "signal": signal.value,
            "confidence": confidence,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat()
        }
    
    def add_strategy(self, name: str, strategy):
        """Add a trading strategy."""
        self.strategies[name] = strategy
    
    def record_trade(self, trade: Dict):
        """Record a completed trade for learning."""
        self.trade_history.append({
            **trade,
            "recorded_at": datetime.now().isoformat()
        })
        
        # Save to disk
        self._save_trade_log()
    
    def _save_trade_log(self):
        """Save trade history to disk."""
        log_path = self.base_dir / "trading_log.json"
        log_path.write_text(json.dumps(self.trade_history, indent=2))
    
    def get_performance_stats(self) -> Dict:
        """Get trading performance statistics."""
        if not self.trade_history:
            return {"trades": 0, "win_rate": 0.0, "total_pnl": 0.0}
        
        wins = sum(1 for t in self.trade_history if t.get("pnl", 0) > 0)
        total_pnl = sum(t.get("pnl", 0) for t in self.trade_history)
        
        return {
            "trades": len(self.trade_history),
            "wins": wins,
            "losses": len(self.trade_history) - wins,
            "win_rate": wins / len(self.trade_history) if self.trade_history else 0,
            "total_pnl": total_pnl
        }


class TradingStrategy:
    """Base class for trading strategies."""
    
    def evaluate(self, market_data: Dict) -> Dict:
        """Evaluate and return signal."""
        raise NotImplementedError


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
    print("Trading brain initialized")
    print(f"Config: {brain.config}")
