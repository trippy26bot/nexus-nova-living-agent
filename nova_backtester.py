#!/usr/bin/env python3
"""
nova_backtester.py — Backtesting Engine.
Tests strategies against historical data.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class Backtester:
    """Historical strategy testing."""
    
    def __init__(self):
        self.results = []
        self.trades = []
        
    def add_trade(self, trade: Dict):
        """Add a simulated trade."""
        self.trades.append({
            **trade,
            "timestamp": trade.get("timestamp", datetime.now().isoformat())
        })
    
    def run_backtest(self, signals: List[Dict], price_data: List[Dict]) -> Dict:
        """Run backtest on historical data."""
        if not signals or not price_data:
            return {"error": "Insufficient data"}
        
        # Simulate trades
        simulated_trades = []
        capital = 10000  # Starting capital
        position = None
        
        for signal in signals:
            # Find corresponding price
            signal_time = datetime.fromisoformat(signal["timestamp"])
            
            # Find price at or after signal
            relevant_prices = [
                p for p in price_data 
                if datetime.fromisoformat(p["timestamp"]) >= signal_time
            ]
            
            if not relevant_prices:
                continue
            
            entry_price = relevant_prices[0]["price"]
            
            # Simulate trade
            if signal.get("action") == "BUY" and position is None:
                size = capital * 0.1  # 10% position
                shares = size / entry_price
                
                position = {
                    "entry_price": entry_price,
                    "shares": shares,
                    "entry_time": signal_time,
                    "signal": signal.get("signal_type", "unknown")
                }
            
            elif position and signal.get("action") == "SELL":
                exit_price = relevant_prices[0]["price"]
                pnl = (exit_price - position["entry_price"]) * position["shares"]
                pnl_pct = (exit_price / position["entry_price"] - 1) * 100
                
                simulated_trades.append({
                    "entry_price": position["entry_price"],
                    "exit_price": exit_price,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "duration_hours": (signal_time - position["entry_time"]).total_seconds() / 3600,
                    "signal": position["signal"]
                })
                
                capital += pnl
                position = None
        
        # Calculate stats
        if not simulated_trades:
            return {"error": "No trades simulated"}
        
        wins = [t for t in simulated_trades if t["pnl"] > 0]
        losses = [t for t in simulated_trades if t["pnl"] <= 0]
        
        total_pnl = sum(t["pnl"] for t in simulated_trades)
        win_rate = len(wins) / len(simulated_trades) if simulated_trades else 0
        
        avg_win = sum(t["pnl"] for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t["pnl"] for t in losses) / len(losses) if losses else 0
        
        return {
            "total_trades": len(simulated_trades),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(win_rate * 100, 1),
            "total_pnl": round(total_pnl, 2),
            "total_return_pct": round((total_pnl / 10000) * 100, 1),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else 0,
            "trades": simulated_trades
        }
    
    def test_strategy(self, strategy_name: str, historical_signals: List[Dict]) -> Dict:
        """Test a specific strategy."""
        result = self.run_backtest(historical_signals, [])
        
        return {
            "strategy": strategy_name,
            "result": result,
            "tested_at": datetime.now().isoformat()
        }
    
    def compare_strategies(self, strategies: Dict[str, List[Dict]]) -> Dict:
        """Compare multiple strategies."""
        comparison = {}
        
        for name, signals in strategies.items():
            result = self.test_strategy(name, signals)
            comparison[name] = result["result"]
        
        # Find best strategy
        best = max(comparison.items(), key=lambda x: x[1].get("total_pnl", 0))
        
        return {
            "strategies": comparison,
            "best_strategy": best[0],
            "best_pnl": best[1].get("total_pnl", 0),
            "compared_at": datetime.now().isoformat()
        }
    
    def get_performance_metrics(self) -> Dict:
        """Get overall performance metrics."""
        if not self.trades:
            return {"trades": 0}
        
        return {
            "total_trades": len(self.trades),
            "by_signal": self._group_by_signal(),
            "by_period": self._group_by_period()
        }
    
    def _group_by_signal(self) -> Dict:
        """Group trades by signal type."""
        grouped = {}
        for trade in self.trades:
            signal = trade.get("signal", "unknown")
            if signal not in grouped:
                grouped[signal] = {"count": 0, "pnl": 0}
            grouped[signal]["count"] += 1
            grouped[signal]["pnl"] += trade.get("pnl", 0)
        return grouped
    
    def _group_by_period(self) -> Dict:
        """Group trades by time period."""
        # Simplified - just return counts
        return {"period_analysis": "Use real data for accurate analysis"}
    
    def save_results(self, path: str = None):
        """Save backtest results."""
        if path is None:
            path = Path(__file__).parent / "backtest_results.json"
        
        Path(path).write_text(json.dumps({
            "trades": self.trades,
            "results": self.results,
            "saved_at": datetime.now().isoformat()
        }, indent=2, default=str))


# Singleton
_backtester: Optional[Backtester] = None


def get_backtester() -> Backtester:
    """Get backtester singleton."""
    global _backtester
    if _backtester is None:
        _backtester = Backtester()
    return _backtester


if __name__ == "__main__":
    bt = get_backtester()
    
    # Test with sample data
    signals = [
        {"timestamp": "2024-01-01T10:00:00", "action": "BUY", "signal_type": "whale"},
        {"timestamp": "2024-01-02T10:00:00", "action": "SELL", "signal_type": "whale"},
    ]
    
    prices = [
        {"timestamp": "2024-01-01T10:00:00", "price": 100},
        {"timestamp": "2024-01-02T10:00:00", "price": 110},
    ]
    
    result = bt.run_backtest(signals, prices)
    print(json.dumps(result, indent=2))
