#!/usr/bin/env python3
"""
nova_strategy_tournament.py — Strategy Tournament System.
Let strategies compete, top performers survive.
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class StrategyTournament:
    """Manages strategy competition and evolution."""
    
    def __init__(self):
        self.strategies = {}
        self.results = {}
        self.path = Path(__file__).parent
        self._load()
    
    def _load(self):
        """Load saved data."""
        file_path = self.path / "tournament.json"
        if file_path.exists():
            try:
                data = json.loads(file_path.read_text())
                self.strategies = data.get("strategies", {})
                self.results = data.get("results", {})
            except:
                pass
    
    def _save(self):
        """Save data."""
        file_path = self.path / "tournament.json"
        file_path.write_text(json.dumps({
            "strategies": self.strategies,
            "results": self.results
        }, indent=2))
    
    def register_strategy(self, name: str, params: Dict, strategy_type: str) -> str:
        """Register a new strategy."""
        strategy_id = f"{name}_{len(self.strategies)}_{int(datetime.now().timestamp())}"
        
        self.strategies[strategy_id] = {
            "name": name,
            "type": strategy_type,
            "params": params,
            "registered_at": datetime.now().isoformat(),
            "status": "ACTIVE"
        }
        
        self._save()
        return strategy_id
    
    def record_result(self, strategy_id: str, trade_result: Dict):
        """Record a trade result for a strategy."""
        if strategy_id not in self.results:
            self.results[strategy_id] = []
        
        self.results[strategy_id].append({
            **trade_result,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save()
    
    def calculate_score(self, strategy_id: str) -> Dict:
        """Calculate strategy score."""
        if strategy_id not in self.results or not self.results[strategy_id]:
            return {"score": 0, "rank": 0, "tests": 0}
        
        results = self.results[strategy_id]
        tests = len(results)
        
        if tests < 5:
            return {"score": 0, "rank": 0, "tests": tests, "reason": "insufficient_data"}
        
        # Calculate metrics
        wins = sum(1 for r in results if r.get("pnl", 0) > 0)
        win_rate = wins / tests
        
        profits = [r.get("pnl", 0) for r in results if r.get("pnl", 0) > 0]
        losses = [r.get("pnl", 0) for r in results if r.get("pnl", 0) < 0]
        
        avg_profit = sum(profits) / len(profits) if profits else 0
        avg_loss = abs(sum(losses) / len(losses)) if losses else 1
        
        profit_factor = avg_profit / avg_loss if avg_loss > 0 else 0
        
        # Drawdown
        running = 0
        max_dd = 0
        for r in results:
            running += r.get("pnl", 0)
            max_dd = min(max_dd, running)
        
        # Score formula
        score = (
            win_rate * 30 +
            min(profit_factor, 5) * 20 +
            min(avg_profit, 50) * 0.5 +
            max(0, 20 + max_dd * 0.2)
        )
        
        return {
            "score": round(score, 2),
            "win_rate": round(win_rate * 100, 1),
            "profit_factor": round(profit_factor, 2),
            "avg_profit": round(avg_profit, 2),
            "max_drawdown": round(max_dd, 2),
            "tests": tests
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get strategy leaderboard."""
        scored = []
        
        for strategy_id in self.strategies:
            if self.strategies[strategy_id].get("status") != "ACTIVE":
                continue
            
            score_data = self.calculate_score(strategy_id)
            
            if score_data["tests"] >= 5:  # Only include tested strategies
                scored.append({
                    "id": strategy_id,
                    "name": self.strategies[strategy_id]["name"],
                    "type": self.strategies[strategy_id]["type"],
                    "score": score_data["score"],
                    "win_rate": score_data["win_rate"],
                    "profit_factor": score_data["profit_factor"],
                    "tests": score_data["tests"]
                })
        
        # Sort by score
        scored.sort(key=lambda x: x["score"], reverse=True)
        
        # Add ranks
        for i, s in enumerate(scored):
            s["rank"] = i + 1
        
        return scored[:limit]
    
    def get_winners(self) -> List[Dict]:
        """Get top performing strategies."""
        leaderboard = self.get_leaderboard(5)
        return [s for s in leaderboard if s["score"] > 50]
    
    def eliminate_weak_strategies(self, min_score: float = 30) -> int:
        """Remove weak strategies."""
        eliminated = 0
        
        for strategy_id in self.strategies:
            if self.strategies[strategy_id].get("status") != "ACTIVE":
                continue
            
            score_data = self.calculate_score(strategy_id)
            
            if score_data["tests"] >= 10 and score_data["score"] < min_score:
                self.strategies[strategy_id]["status"] = "ELIMINATED"
                eliminated += 1
        
        self._save()
        return eliminated
    
    def mutate_winner(self, strategy_id: str) -> Optional[str]:
        """Create mutated version of winning strategy."""
        if strategy_id not in self.strategies:
            return None
        
        original = self.strategies[strategy_id]
        params = original["params"].copy()
        
        # Mutate parameters
        for key in params:
            if isinstance(params[key], (int, float)):
                params[key] = params[key] * random.uniform(0.8, 1.2)
        
        # Register mutation
        new_id = self.register_strategy(
            f"{original['name']}_mut",
            params,
            original["type"]
        )
        
        return new_id
    
    def get_status(self) -> Dict:
        """Get tournament status."""
        leaderboard = self.get_leaderboard(10)
        
        return {
            "total_strategies": len(self.strategies),
            "active_strategies": sum(1 for s in self.strategies.values() if s.get("status") == "ACTIVE"),
            "total_tests": sum(len(r) for r in self.results.values()),
            "leaderboard": leaderboard,
            "winners": self.get_winners()
        }


_tournament: Optional[StrategyTournament] = None


def get_strategy_tournament() -> StrategyTournament:
    """Get tournament singleton."""
    global _tournament
    if _tournament is None:
        _tournament = StrategyTournament()
    return _tournament


if __name__ == "__main__":
    tournament = get_strategy_tournament()
    
    # Register test strategies
    tournament.register_strategy("momentum", {"threshold": 0.7}, "momentum")
    tournament.register_strategy("mean_reversion", {"threshold": 0.3}, "mean_reversion")
    tournament.register_strategy("whale_follow", {"min_confidence": 0.8}, "onchain")
    
    # Record some results
    for i in range(10):
        tournament.record_result("momentum_0", {"pnl": random.uniform(-5, 15)})
    
    print(json.dumps(tournament.get_status(), indent=2))
