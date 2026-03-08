#!/usr/bin/env python3
"""
nova_evolution_lab.py — AI Strategy Evolution Lab.
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class EvolutionLab:
    """Automated strategy mutation and testing."""
    
    def __init__(self):
        self.path = Path(__file__).parent
        self.strategies = []
        self.test_results = []
        self.generation = 0
        self._load()
    
    def _load(self):
        """Load saved data."""
        file_path = self.path / "evolution_lab.json"
        if file_path.exists():
            try:
                data = json.loads(file_path.read_text())
                self.strategies = data.get("strategies", [])
                self.test_results = data.get("results", [])
                self.generation = data.get("generation", 0)
            except:
                pass
    
    def _save(self):
        """Save data."""
        file_path = self.path / "evolution_lab.json"
        file_path.write_text(json.dumps({
            "strategies": self.strategies,
            "results": self.test_results,
            "generation": self.generation
        }, indent=2))
    
    def create_strategy(self, strategy_type: str, params: Dict) -> str:
        """Create a new strategy."""
        strategy_id = f"gen{self.generation}_{strategy_type}_{len(self.strategies)}"
        
        strategy = {
            "id": strategy_id,
            "type": strategy_type,
            "params": params,
            "created_at": datetime.now().isoformat(),
            "status": "TESTING"
        }
        
        self.strategies.append(strategy)
        self._save()
        
        return strategy_id
    
    def mutate(self, strategy_id: str) -> Optional[str]:
        """Create mutated version of strategy."""
        
        strategy = next((s for s in self.strategies if s["id"] == strategy_id), None)
        
        if not strategy:
            return None
        
        # Mutate params
        params = strategy["params"].copy()
        
        for key in params:
            if isinstance(params[key], (int, float)):
                mutation = random.uniform(0.7, 1.3)
                params[key] = round(params[key] * mutation, 4)
        
        # Create new strategy
        new_id = self.create_strategy(f"{strategy['type']}_mut", params)
        
        return new_id
    
    def run_simulation(self, strategy_id: str, market_scenarios: int = 100) -> Dict:
        """Run strategy simulation."""
        
        strategy = next((s for s in self.strategies if s["id"] == strategy_id), None)
        
        if not strategy:
            return {"error": "Strategy not found"}
        
        # Simulate trades
        results = []
        
        for _ in range(market_scenarios):
            # Random market conditions
            market_return = random.gauss(0.02, 0.05)  # 2% avg, 5% std
            
            # Apply strategy params
            confidence = strategy["params"].get("confidence_threshold", 0.6)
            position_size = strategy["params"].get("position_size", 0.02)
            
            # Simulate
            if random.random() > confidence:
                pnl = market_return * position_size * random.choice([-1, 1])
            else:
                pnl = market_return * position_size
            
            results.append(pnl)
        
        # Calculate metrics
        wins = sum(1 for r in results if r > 0)
        win_rate = wins / len(results)
        avg_return = sum(results) / len(results)
        
        # Score
        score = (win_rate * 50) + (avg_return * 1000)
        
        # Record
        test_result = {
            "strategy_id": strategy_id,
            "scenarios": market_scenarios,
            "win_rate": win_rate,
            "avg_return": avg_return,
            "score": score,
            "tested_at": datetime.now().isoformat()
        }
        
        self.test_results.append(test_result)
        
        # Update strategy
        strategy["status"] = "TESTED"
        strategy["last_score"] = score
        
        self._save()
        
        return test_result
    
    def evolve_generation(self) -> Dict:
        """Run one evolution cycle."""
        self.generation += 1
        
        # Get top strategies
        tested = [s for s in self.strategies if s.get("status") == "TESTED"]
        
        if not tested:
            return {"error": "No tested strategies"}
        
        tested.sort(key=lambda x: x.get("last_score", 0), reverse=True)
        
        # Keep top 3
        survivors = tested[:3]
        
        # Mutate each
        new_count = 0
        for survivor in survivors:
            for _ in range(3):  # 3 mutations each
                new_id = self.mutate(survivor["id"])
                if new_id:
                    new_count += 1
        
        self._save()
        
        return {
            "generation": self.generation,
            "survivors": [s["id"] for s in survivors],
            "new_strategies": new_count
        }
    
    def get_leaderboard(self) -> List[Dict]:
        """Get top strategies."""
        tested = [s for s in self.strategies if s.get("status") == "TESTED"]
        tested.sort(key=lambda x: x.get("last_score", 0), reverse=True)
        
        return tested[:10]


_evolution_lab: Optional[EvolutionLab] = None

def get_evolution_lab() -> EvolutionLab:
    global _evolution_lab
    if _evolution_lab is None:
        _evolution_lab = EvolutionLab()
    return _evolution_lab


if __name__ == "__main__":
    lab = get_evolution_lab()
    
    # Create test strategy
    sid = lab.create_strategy("momentum", {"confidence_threshold": 0.7, "position_size": 0.02})
    result = lab.run_simulation(sid)
    print(json.dumps(result, indent=2))
