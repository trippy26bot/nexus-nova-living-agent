#!/usr/bin/env python3
"""
Nova Imagination Engine
Simulates possible futures before acting
"""

import random
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime


class ScenarioGenerator:
    """Generates possible future scenarios"""
    
    def __init__(self):
        self.modifiers = {
            "optimistic": (1.1, 1.4),
            "hopeful": (1.05, 1.2),
            "neutral": (0.95, 1.05),
            "pessimistic": (0.7, 0.9),
            "disaster": (0.3, 0.6)
        }
    
    def generate(self, situation: str, num_scenarios: int = 5) -> List[Dict]:
        """Generate possible scenarios"""
        scenarios = []
        
        scenario_types = list(self.modifiers.keys())
        
        for i in range(num_scenarios):
            scenario_type = scenario_types[i % len(scenario_types)]
            low, high = self.modifiers[scenario_type]
            
            scenarios.append({
                "id": f"scenario_{i}",
                "type": scenario_type,
                "modifier": random.uniform(low, high),
                "description": f"{scenario_type.capitalize()} outcome for: {situation[:50]}"
            })
        
        return scenarios
    
    def generate_custom(self, situation: str, modifiers: List[float]) -> List[Dict]:
        """Generate with custom modifiers"""
        scenarios = []
        
        for i, mod in enumerate(modifiers):
            scenarios.append({
                "id": f"scenario_{i}",
                "type": "custom",
                "modifier": mod,
                "description": f"Custom scenario {i+1} for: {situation[:50]}"
            })
        
        return scenarios


class SimulationRunner:
    """Runs scenario simulations"""
    
    def __init__(self):
        self.simulations = []
    
    def run(self, scenario: Dict, base_value: Any, simulator: Callable = None) -> Dict:
        """Run a single simulation"""
        if simulator:
            result = simulator(scenario, base_value)
        else:
            # Default simulation
            modifier = scenario.get("modifier", 1.0)
            
            if isinstance(base_value, (int, float)):
                simulated_value = base_value * modifier
                result = {
                    "outcome": simulated_value,
                    "change": (modifier - 1.0) * 100,
                    "scenario": scenario["type"]
                }
            else:
                # Non-numeric - just apply scenario type
                result = {
                    "outcome": base_value,
                    "scenario": scenario["type"],
                    "note": f"Would be affected by {scenario['type']} scenario"
                }
        
        self.simulations.append({
            "scenario": scenario,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result


class OutcomeEvaluator:
    """Evaluates and chooses best outcomes"""
    
    def __init__(self):
        self.weights = {
            "success_probability": 0.4,
            "risk": -0.3,
            "value": 0.3
        }
    
    def evaluate(self, prediction: Dict, scenario: Dict) -> float:
        """Score an outcome"""
        # Extract metrics
        success_prob = prediction.get("success_probability", 0.5)
        risk = prediction.get("risk", 0.5)
        value = prediction.get("value", prediction.get("outcome", 0.5))
        
        # Normalize value if numeric
        if isinstance(value, (int, float)):
            value = max(0, min(1, value / 100))
        
        # Calculate score
        score = (
            self.weights["success_probability"] * success_prob +
            self.weights["risk"] * (1 - risk) +
            self.weights["value"] * value
        )
        
        # Penalize extreme scenarios
        scenario_type = scenario.get("type", "neutral")
        if scenario_type in ["disaster", "optimistic"]:
            score *= 0.9
        
        return score
    
    def rank(self, predictions: List[Dict], scenarios: List[Dict]) -> List[Dict]:
        """Rank all outcomes"""
        ranked = []
        
        for pred, scen in zip(predictions, scenarios):
            score = self.evaluate(pred, scen)
            ranked.append({
                "scenario": scen,
                "prediction": pred,
                "score": score
            })
        
        # Sort by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        
        return ranked


class ImaginationEngine:
    """
    Nova imagines futures before acting
    """
    
    def __init__(self):
        self.generator = ScenarioGenerator()
        self.runner = SimulationRunner()
        self.evaluator = OutcomeEvaluator()
        self.imagination_history = []
    
    def imagine(self, situation: str, base_value: Any = 100, simulator: Callable = None) -> Dict:
        """Imagine possible futures"""
        # Generate scenarios
        scenarios = self.generator.generate(situation)
        
        # Run simulations
        predictions = []
        for scenario in scenarios:
            pred = self.runner.run(scenario, base_value, simulator)
            predictions.append(pred)
        
        # Evaluate and rank
        ranked = self.evaluator.rank(predictions, scenarios)
        
        # Choose best
        best = ranked[0] if ranked else None
        
        result = {
            "situation": situation,
            "scenarios_tested": len(scenarios),
            "best_scenario": best["scenario"]["type"] if best else None,
            "best_score": best["score"] if best else 0,
            "best_outcome": best["prediction"] if best else None,
            "all_rankings": ranked,
            "timestamp": datetime.now().isoformat()
        }
        
        self.imagination_history.append(result)
        
        return result
    
    def compare_options(self, options: List[str], evaluator: Callable = None) -> Dict:
        """Compare multiple options"""
        results = []
        
        for option in options:
            result = self.imagine(option, simulator=evaluator)
            results.append(result)
        
        # Find best option
        best = max(results, key=lambda x: x["best_score"])
        
        return {
            "options": options,
            "results": results,
            "recommended": best["situation"],
            "confidence": best["best_score"]
        }
    
    def simulate_decision(self, decision: str, context: Dict, outcomes: Dict) -> Dict:
        """Simulate a specific decision"""
        scenario_modifiers = []
        
        # Map outcomes to modifiers
        outcome_map = {
            "best": 1.3,
            "good": 1.1,
            "neutral": 1.0,
            "bad": 0.7,
            "worst": 0.4
        }
        
        for outcome_name, outcome_data in outcomes.items():
            modifier = outcome_map.get(outcome_name, 1.0)
            scenario = {
                "id": outcome_name,
                "type": outcome_name,
                "modifier": modifier,
                "description": f"If {decision} → {outcome_name}"
            }
            scenario_modifiers.append(scenario)
        
        # Run with custom modifiers
        scenarios = self.generator.generate_custom(decision, [s["modifier"] for s in scenario_modifiers])
        
        predictions = []
        for scenario in scenarios:
            # Use outcome data as prediction
            pred = outcomes.get(scenario["type"], {})
            predictions.append(pred)
        
        ranked = self.evaluator.rank(predictions, scenarios)
        
        return {
            "decision": decision,
            "context": context,
            "ranked_outcomes": ranked,
            "recommended_outcome": ranked[0]["scenario"]["type"] if ranked else None
        }
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get imagination history"""
        return self.imagination_history[-limit:]
    
    def get_stats(self) -> Dict:
        """Get imagination statistics"""
        return {
            "total_imaginations": len(self.imagination_history),
            "scenarios_tested": sum(r["scenarios_tested"] for r in self.imagination_history)
        }


# Global instance
_imagination_engine = None

def get_imagination_engine() -> ImaginationEngine:
    global _imagination_engine
    if _imagination_engine is None:
        _imagination_engine = ImaginationEngine()
    return _imagination_engine
