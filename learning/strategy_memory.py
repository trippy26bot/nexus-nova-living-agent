"""
Strategy Memory - Tracks which strategies work
"""
import json
from pathlib import Path

STRATEGIES_FILE = Path.home() / ".nova/learning/strategies.json"

class StrategyMemory:
    def __init__(self):
        STRATEGIES_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not STRATEGIES_FILE.exists():
            self.save({})
    
    def save(self, data):
        with open(STRATEGIES_FILE, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        with open(STRATEGIES_FILE) as f:
            return json.load(f)
    
    def update(self, strategy_name, result):
        """Record strategy performance"""
        strategies = self.load()
        
        if strategy_name not in strategies:
            strategies[strategy_name] = {"wins": 0, "losses": 0, "total_pnl": 0}
        
        if result > 0:
            strategies[strategy_name]["wins"] += 1
        else:
            strategies[strategy_name]["losses"] += 1
        
        strategies[strategy_name]["total_pnl"] += result
        
        self.save(strategies)
    
    def performance(self, strategy_name):
        """Get performance stats for a strategy"""
        strategies = self.load()
        s = strategies.get(strategy_name)
        
        if not s:
            return {"win_rate": 0, "total_pnl": 0, "total_trades": 0}
        
        total = s["wins"] + s["losses"]
        return {
            "win_rate": s["wins"] / total if total > 0 else 0,
            "total_pnl": s["total_pnl"],
            "total_trades": total
        }
    
    def best_strategies(self, limit=5):
        """Get top performing strategies"""
        strategies = self.load()
        ranked = []
        
        for name, stats in strategies.items():
            total = stats["wins"] + stats["losses"]
            if total > 0:
                pnl = stats["total_pnl"]
                win_rate = stats["wins"] / total
                ranked.append((name, win_rate, pnl, total))
        
        return sorted(ranked, key=lambda x: x[2], reverse=True)[:limit]
