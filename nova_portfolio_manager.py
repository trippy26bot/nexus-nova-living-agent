#!/usr/bin/env python3
"""
nova_portfolio_manager.py — Multi-Strategy Portfolio Manager.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class PortfolioManager:
    """Manages multiple strategies simultaneously."""
    
    def __init__(self):
        self.strategies = {}
        self.allocations = {}
        self.positions = {}
    
    def add_strategy(self, name: str, allocation_pct: float):
        """Add strategy with allocation."""
        self.strategies[name] = {
            "allocation": allocation_pct,
            "active": True,
            "added_at": datetime.now().isoformat()
        }
        self.allocations[name] = allocation_pct
    
    def rebalance(self, total_capital: float) -> Dict:
        """Rebalance capital across strategies."""
        
        if not self.allocations:
            return {"error": "No strategies"}
        
        rebalance_plan = {}
        
        for name, pct in self.allocations.items():
            capital = total_capital * (pct / 100)
            rebalance_plan[name] = {
                "allocation_pct": pct,
                "capital": capital
            }
        
        return {
            "total_capital": total_capital,
            "plan": rebalance_plan,
            "timestamp": datetime.now().isoformat()
        }
    
    def record_performance(self, strategy: str, pnl: float):
        """Record strategy performance."""
        if strategy not in self.strategies:
            self.strategies[strategy] = {"pnl": 0, "trades": 0}
        
        self.strategies[strategy]["pnl"] = pnl
        self.strategies[strategy]["trades"] = self.strategies[strategy].get("trades", 0) + 1
    
    def auto_rebalance(self, total_capital: float, lookback_trades: int = 20) -> Dict:
        """Auto-rebalance based on performance."""
        
        # Calculate performance scores
        scores = {}
        
        for name, data in self.strategies.items():
            trades = data.get("trades", 0)
            pnl = data.get("pnl", 0)
            
            if trades >= 5:
                avg_pnl = pnl / trades
                scores[name] = max(0, avg_pnl + 50)  # Normalize to 0-100
            else:
                scores[name] = 50  # Default for new strategies
        
        if not scores:
            return self.rebalance(total_capital)
        
        # Rebalance toward better performers
        total_score = sum(scores.values())
        
        new_allocations = {}
        for name, score in scores.items():
            new_pct = (score / total_score) * 100
            new_allocations[name] = round(new_pct, 1)
            self.allocations[name] = new_pct
        
        return {
            "action": "AUTO_REBALANCE",
            "old_allocations": self.allocations,
            "new_allocations": new_allocations,
            "total_capital": total_capital
        }
    
    def get_status(self) -> Dict:
        """Get portfolio status."""
        return {
            "strategies": self.strategies,
            "allocations": self.allocations,
            "positions": self.positions
        }


_portfolio: Optional[PortfolioManager] = None

def get_portfolio_manager() -> PortfolioManager:
    global _portfolio
    if _portfolio is None:
        _portfolio = PortfolioManager()
    return _portfolio


if __name__ == "__main__":
    pm = get_portfolio_manager()
    pm.add_strategy("momentum", 30)
    pm.add_strategy("mean_reversion", 20)
    pm.add_strategy("whale_follow", 25)
    print(json.dumps(pm.rebalance(10000), indent=2))
