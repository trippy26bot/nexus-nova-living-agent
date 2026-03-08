#!/usr/bin/env python3
"""
nova_strategy_optimizer.py — Adaptive Strategy Optimizer.
Learns optimal entry/exit/position sizing over time.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class StrategyOptimizer:
    """Optimizes trading strategy based on results."""
    
    def __init__(self):
        self.trades = []
        self.strategies = defaultdict(lambda: {
            "signals": 0,
            "wins": 0,
            "losses": 0,
            "total_pnl": 0.0,
            "entry_timings": [],  # seconds after signal
            "exit_timings": [],   # minutes held
            "position_sizes": []
        })
        self.path = Path(__file__).parent
        self._load()
    
    def _load(self):
        """Load saved data."""
        file_path = self.path / "strategy_optimizer.json"
        if file_path.exists():
            try:
                data = json.loads(file_path.read_text())
                self.trades = data.get("trades", [])
                self.strategies = defaultdict(lambda: {
                    "signals": 0, "wins": 0, "losses": 0,
                    "total_pnl": 0.0, "entry_timings": [], "exit_timings": [], "position_sizes": []
                })
                for k, v in data.get("strategies", {}).items():
                    self.strategies[k] = v
            except:
                pass
    
    def _save(self):
        """Save data."""
        file_path = self.path / "strategy_optimizer.json"
        file_path.write_text(json.dumps({
            "trades": self.trades,
            "strategies": dict(self.strategies)
        }, indent=2, default=str))
    
    def record_signal(self, signal_type: str, token: str):
        """Record a signal generated."""
        self.trades.append({
            "signal_type": signal_type,
            "token": token,
            "signaled_at": datetime.now().isoformat(),
            "entered": False,
            "exited": False
        })
    
    def record_entry(self, signal_type: str, token: str, entry_price: float, 
                   position_size: float, entry_delay: int):
        """Record trade entry."""
        # Find matching signal
        for trade in reversed(self.trades):
            if (trade.get("signal_type") == signal_type and 
                trade.get("token") == token and
                not trade.get("entered")):
                
                trade["entered"] = True
                trade["entry_price"] = entry_price
                trade["position_size"] = position_size
                trade["entry_delay"] = entry_delay
                trade["entered_at"] = datetime.now().isoformat()
                
                # Update strategy stats
                self.strategies[signal_type]["signals"] += 1
                self.strategies[signal_type]["position_sizes"].append(position_size)
                self.strategies[signal_type]["entry_timings"].append(entry_delay)
                
                self._save()
                return True
        
        return False
    
    def record_exit(self, signal_type: str, token: str, exit_price: float):
        """Record trade exit."""
        for trade in reversed(self.trades):
            if (trade.get("signal_type") == signal_type and 
                trade.get("token") == token and
                trade.get("entered") and
                not trade.get("exited")):
                
                entry_price = trade.get("entry_price", exit_price)
                pnl = (exit_price - entry_price) / entry_price
                
                trade["exited"] = True
                trade["exit_price"] = exit_price
                trade["pnl"] = pnl
                trade["exited_at"] = datetime.now().isoformat()
                
                # Calculate hold time
                entered = datetime.fromisoformat(trade["entered_at"])
                exited = datetime.fromisoformat(trade["exited_at"])
                hold_minutes = (exited - entered).total_seconds() / 60
                
                # Update strategy stats
                self.strategies[signal_type]["exit_timings"].append(hold_minutes)
                
                if pnl > 0:
                    self.strategies[signal_type]["wins"] += 1
                else:
                    self.strategies[signal_type]["losses"] += 1
                
                self.strategies[signal_type]["total_pnl"] += pnl
                
                self._save()
                return True
        
        return False
    
    def get_optimal_entry_delay(self, signal_type: str) -> int:
        """Get optimal entry delay for signal type."""
        strategy = self.strategies.get(signal_type, {})
        timings = strategy.get("entry_timings", [])
        
        if not timings:
            return 60  # Default 60 seconds
        
        # Find timing with best results
        # This is simplified - real version would analyze by outcome
        return int(sum(timings) / len(timings))
    
    def get_optimal_exit_time(self, signal_type: str) -> int:
        """Get optimal exit time (minutes) for signal type."""
        strategy = self.strategies.get(signal_type, {})
        timings = strategy.get("exit_timings", [])
        
        if not timings:
            return 30  # Default 30 minutes
        
        # Return average
        return int(sum(timings) / len(timings))
    
    def get_optimal_position_size(self, signal_type: str) -> float:
        """Get optimal position size for signal type."""
        strategy = self.strategies.get(signal_type, {})
        sizes = strategy.get("position_sizes", [])
        
        if not sizes:
            return 2.0  # Default 2%
        
        return round(sum(sizes) / len(sizes), 2)
    
    def get_strategy_stats(self, signal_type: str) -> Dict:
        """Get statistics for a signal type."""
        strategy = self.strategies.get(signal_type, {})
        
        signals = strategy.get("signals", 0)
        wins = strategy.get("wins", 0)
        losses = strategy.get("losses", 0)
        
        win_rate = (wins / signals * 100) if signals > 0 else 0
        avg_pnl = (strategy.get("total_pnl", 0) / signals) if signals > 0 else 0
        
        return {
            "signal_type": signal_type,
            "total_signals": signals,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 1),
            "avg_pnl": round(avg_pnl * 100, 1),
            "optimal_entry_delay": self.get_optimal_entry_delay(signal_type),
            "optimal_exit_time": self.get_optimal_exit_time(signal_type),
            "optimal_position_size": self.get_optimal_position_size(signal_type)
        }
    
    def get_all_stats(self) -> Dict:
        """Get all strategy statistics."""
        return {
            signal_type: self.get_strategy_stats(signal_type)
            for signal_type in self.strategies.keys()
        }
    
    def get_recommended_strategy(self) -> Dict:
        """Get the best performing strategy."""
        best = None
        best_pnl = -float("inf")
        
        for signal_type, strategy in self.strategies.items():
            pnl = strategy.get("total_pnl", 0)
            if pnl > best_pnl and strategy.get("signals", 0) >= 3:
                best_pnl = pnl
                best = signal_type
        
        if best:
            return self.get_strategy_stats(best)
        
        return {"recommendation": "insufficient_data"}
    
    def get_adjusted_params(self, signal_type: str) -> Dict:
        """Get adjusted parameters based on historical performance."""
        stats = self.get_strategy_stats(signal_type)
        
        win_rate = stats.get("win_rate", 0)
        
        # Adjust based on performance
        if win_rate >= 70:
            # High win rate - can use larger positions
            position_mult = 1.5
        elif win_rate >= 50:
            position_mult = 1.0
        else:
            position_mult = 0.5
        
        return {
            "entry_delay": stats.get("optimal_entry_delay", 60),
            "exit_time": stats.get("optimal_exit_time", 30),
            "position_size": stats.get("optimal_position_size", 2.0) * position_mult,
            "stop_loss": 15 if win_rate < 50 else 10
        }


# Singleton
_strategy_optimizer: Optional[StrategyOptimizer] = None


def get_strategy_optimizer() -> StrategyOptimizer:
    """Get strategy optimizer singleton."""
    global _strategy_optimizer
    if _strategy_optimizer is None:
        _strategy_optimizer = StrategyOptimizer()
    return _strategy_optimizer


if __name__ == "__main__":
    opt = get_strategy_optimizer()
    
    # Test
    opt.record_signal("whale_cluster", "TOKEN_A")
    opt.record_entry("whale_cluster", "TOKEN_A", 0.001, 2.0, 30)
    opt.record_exit("whale_cluster", "TOKEN_A", 0.0012)
    
    print(json.dumps(opt.get_all_stats(), indent=2))
