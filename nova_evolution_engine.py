#!/usr/bin/env python3
"""
nova_evolution_engine.py — Strategy Evolution Engine.
Mutates and evolves trading strategies.
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class EvolutionEngine:
    """Evolves trading strategies through mutation."""
    
    def __init__(self):
        self.strategies = {}  # strategy_id -> strategy config
        self.results = {}  # strategy_id -> performance
        self.generation = 0
        self.path = Path(__file__).parent
        self._load()
    
    def _load(self):
        """Load saved data."""
        file_path = self.path / "evolution.json"
        if file_path.exists():
            try:
                data = json.loads(file_path.read_text())
                self.strategies = data.get("strategies", {})
                self.results = data.get("results", {})
                self.generation = data.get("generation", 0)
            except:
                pass
    
    def _save(self):
        """Save data."""
        file_path = self.path / "evolution.json"
        file_path.write_text(json.dumps({
            "strategies": self.strategies,
            "results": self.results,
            "generation": self.generation
        }, indent=2))
    
    def create_strategy(self, name: str, params: Dict) -> str:
        """Create a new strategy."""
        strategy_id = f"gen{self.generation}_{name}_{len(self.strategies)}"
        
        self.strategies[strategy_id] = {
            "name": name,
            "params": params,
            "created_at": datetime.now().isoformat(),
            "generation": self.generation
        }
        
        self._save()
        return strategy_id
    
    def mutate(self, strategy_id: str) -> str:
        """Create a mutated copy of a strategy."""
        if strategy_id not in self.strategies:
            return None
        
        original = self.strategies[strategy_id]
        params = original["params"].copy()
        
        # Mutate parameters
        mutations = 0
        for key in params:
            if random.random() < 0.3:  # 30% chance per param
                mutation = params[key] * random.uniform(0.8, 1.2)  # ±20%
                params[key] = round(mutation, 3)
                mutations += 1
        
        # Create new strategy
        new_id = self.create_strategy(
            f"{original['name']}_mut",
            params
        )
        
        return new_id
    
    def crossover(self, strategy_id_a: str, strategy_id_b: str) -> str:
        """Create offspring from two strategies."""
        if strategy_id_a not in self.strategies or strategy_id_b not in self.strategies:
            return None
        
        params_a = self.strategies[strategy_id_a]["params"]
        params_b = self.strategies[strategy_id_b]["params"]
        
        # Mix parameters
        child_params = {}
        for key in params_a:
            if random.random() < 0.5:
                child_params[key] = params_a[key]
            else:
                child_params[key] = params_b[key]
        
        new_id = self.create_strategy("crossover", child_params)
        return new_id
    
    def record_result(self, strategy_id: str, result: Dict):
        """Record performance result for a strategy."""
        if strategy_id not in self.results:
            self.results[strategy_id] = []
        
        self.results[strategy_id].append({
            **result,
            "tested_at": datetime.now().isoformat()
        })
        
        self._save()
    
    def get_fitness(self, strategy_id: str) -> float:
        """Calculate fitness score for a strategy."""
        if strategy_id not in self.results or not self.results[strategy_id]:
            return 0.0
        
        results = self.results[strategy_id]
        
        # Calculate fitness components
        wins = sum(1 for r in results if r.get("profit", 0) > 0)
        total = len(results)
        win_rate = wins / total if total > 0 else 0
        
        avg_profit = sum(r.get("profit", 0) for r in results) / total if total > 0 else 0
        
        max_drawdown = min([r.get("drawdown", 0) for r in results], default=0)
        
        # Fitness formula
        fitness = (
            win_rate * 40 +
            min(avg_profit, 100) * 0.4 +
            max(0, 30 + max_drawdown) * 0.2
        )
        
        return fitness
    
    def get_best_strategies(self, limit: int = 5) -> List[Dict]:
        """Get top performing strategies."""
        scored = []
        
        for strategy_id in self.strategies:
            fitness = self.get_fitness(strategy_id)
            scored.append({
                "id": strategy_id,
                "name": self.strategies[strategy_id]["name"],
                "fitness": fitness,
                "tests": len(self.results.get(strategy_id, []))
            })
        
        scored.sort(key=lambda x: x["fitness"], reverse=True)
        return scored[:limit]
    
    def evolve_next_generation(self) -> int:
        """Create next generation through evolution."""
        self.generation += 1
        
        # Get top strategies
        best = self.get_best_strategies(5)
        
        if not best:
            return 0
        
        # Create mutations of top performers
        new_count = 0
        for top in best[:3]:
            for _ in range(3):  # 3 mutations each
                new_id = self.mutate(top["id"])
                if new_id:
                    new_count += 1
        
        # Create crossovers
        for i in range(len(best) - 1):
            new_id = self.crossover(best[i]["id"], best[i+1]["id"])
            if new_id:
                new_count += 1
        
        self._save()
        return new_count
    
    def get_status(self) -> Dict:
        """Get evolution status."""
        return {
            "generation": self.generation,
            "total_strategies": len(self.strategies),
            "total_tests": sum(len(r) for r in self.results.values()),
            "best_strategies": self.get_best_strategies(3)
        }


# Singleton
_evolution_engine: Optional[EvolutionEngine] = None


def get_evolution_engine() -> EvolutionEngine:
    """Get evolution engine singleton."""
    global _evolution_engine
    if _evolution_engine is None:
        _evolution_engine = EvolutionEngine()
    return _evolution_engine


if __name__ == "__main__":
    engine = get_evolution_engine()
    
    # Create initial strategy
    sid = engine.create_strategy("whale_cluster", {
        "whale_weight": 0.35,
        "cluster_weight": 0.30,
        "momentum_weight": 0.20,
        "liquidity_weight": 0.15
    })
    
    # Record some results
    for _ in range(10):
        engine.record_result(sid, {
            "profit": random.uniform(-5, 25),
            "drawdown": random.uniform(-20, 0)
        })
    
    print(json.dumps(engine.get_status(), indent=2))
