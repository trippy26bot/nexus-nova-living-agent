#!/usr/bin/env python3
"""
Nova Reality Engine
Simulates outcomes before acting - virtual decision making
"""

import time
import random
from typing import Dict, List, Any, Optional, Callable
from collections import defaultdict
from datetime import datetime


class SimulationWorld:
    """Virtual environment for simulations"""
    
    def __init__(self):
        self.state = {}
        self.history = []
    
    def set_state(self, state: Dict[str, Any]):
        """Set the world state"""
        self.state = state
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "state": dict(state)
        })
    
    def get_state(self) -> Dict[str, Any]:
        """Get current world state"""
        return dict(self.state)
    
    def update_state(self, key: str, value: Any):
        """Update a specific state element"""
        self.state[key] = value
    
    def clear(self):
        """Clear world state"""
        self.state.clear()
        self.history.clear()


class ScenarioBuilder:
    """Builds possible future scenarios"""
    
    def __init__(self):
        self.action_templates = {}
    
    def build(self, action: str, state: Dict[str, Any], metadata: Optional[Dict] = None) -> Dict:
        """Build a scenario from an action and state"""
        return {
            "action": action,
            "state": dict(state),
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
    
    def build_multiple(self, actions: List[str], state: Dict[str, Any]) -> List[Dict]:
        """Build multiple scenarios from a list of actions"""
        return [self.build(action, state) for action in actions]
    
    def register_template(self, action_type: str, template: Dict):
        """Register an action template"""
        self.action_templates[action_type] = template


class OutcomePredictor:
    """Predicts outcomes of scenarios"""
    
    def __init__(self, model: Optional[Callable] = None):
        self.model = model
        self.predictions = []
    
    def predict(self, scenario: Dict) -> Dict:
        """Predict outcome of a scenario"""
        if self.model:
            # Use custom model
            prediction = self.model(scenario)
        else:
            # Default prediction logic
            action = scenario.get("action", "")
            state = scenario.get("state", {})
            
            # Simple heuristic predictions
            if "trade" in action.lower() or "buy" in action.lower():
                success_prob = 0.6 + random.random() * 0.2
                risk = 0.2 + random.random() * 0.2
            elif "learn" in action.lower() or "research" in action.lower():
                success_prob = 0.7 + random.random() * 0.2
                risk = 0.1
            elif "create" in action.lower() or "build" in action.lower():
                success_prob = 0.5 + random.random() * 0.3
                risk = 0.3
            else:
                success_prob = 0.5 + random.random() * 0.3
                risk = 0.2 + random.random() * 0.2
            
            prediction = {
                "success_probability": success_prob,
                "risk": risk,
                "expected_value": success_prob - risk,
                "reasoning": f"Default prediction for action: {action}"
            }
        
        # Store prediction
        self.predictions.append({
            "scenario": scenario,
            "prediction": prediction,
            "timestamp": datetime.now().isoformat()
        })
        
        return prediction
    
    def predict_batch(self, scenarios: List[Dict]) -> List[Dict]:
        """Predict outcomes for multiple scenarios"""
        return [self.predict(s) for s in scenarios]
    
    def set_model(self, model: Callable):
        """Set custom prediction model"""
        self.model = model


class RealityEvaluator:
    """Evaluates and scores predicted outcomes"""
    
    def __init__(self, weights: Optional[Dict] = None):
        self.weights = weights or {
            "success": 1.0,
            "risk": -0.5,
            "speed": 0.2
        }
    
    def evaluate(self, prediction: Dict) -> float:
        """Evaluate a prediction and return score"""
        success = prediction.get("success_probability", 0.5)
        risk = prediction.get("risk", 0.5)
        
        score = (
            self.weights["success"] * success +
            self.weights["risk"] * (1 - risk)
        )
        
        return score
    
    def evaluate_batch(self, predictions: List[Dict]) -> List[float]:
        """Evaluate multiple predictions"""
        return [self.evaluate(p) for p in predictions]
    
    def set_weights(self, weights: Dict):
        """Set evaluation weights"""
        self.weights = weights


class RealityEngine:
    """Core reality simulation engine"""
    
    def __init__(self):
        self.world = SimulationWorld()
        self.builder = ScenarioBuilder()
        self.predictor = OutcomePredictor()
        self.evaluator = RealityEvaluator()
        self.simulations = []
        self.enabled = True
    
    def set_world_state(self, state: Dict[str, Any]):
        """Set the current world state"""
        self.world.set_state(state)
    
    def get_world_state(self) -> Dict[str, Any]:
        """Get current world state"""
        return self.world.get_state()
    
    def simulate(self, actions: List[str], state: Optional[Dict[str, Any]] = None) -> Dict:
        """Simulate multiple actions and return the best"""
        if not self.enabled:
            return {"action": actions[0] if actions else None, "simulated": False}
        
        # Use provided state or current world state
        sim_state = state if state is not None else self.world.get_state()
        
        # Build scenarios
        scenarios = self.builder.build_multiple(actions, sim_state)
        
        # Predict outcomes
        predictions = self.predictor.predict_batch(scenarios)
        
        # Evaluate predictions
        scores = self.evaluator.evaluate_batch(predictions)
        
        # Find best action
        best_idx = scores.index(max(scores)) if scores else 0
        best_action = actions[best_idx] if actions else None
        
        # Store simulation
        simulation = {
            "timestamp": datetime.now().isoformat(),
            "actions": actions,
            "scenarios": scenarios,
            "predictions": predictions,
            "scores": scores,
            "best_action": best_action,
            "best_score": scores[best_idx] if scores else 0
        }
        self.simulations.append(simulation)
        
        return {
            "action": best_action,
            "score": scores[best_idx] if scores else 0,
            "all_scores": dict(zip(actions, scores)),
            "simulated": True,
            "simulation": simulation
        }
    
    def simulate_single(self, action: str, state: Optional[Dict[str, Any]] = None) -> Dict:
        """Simulate a single action"""
        result = self.simulate([action], state)
        return {
            "action": action,
            "predicted": result.get("predictions", [{}])[0] if result.get("predictions") else {},
            "simulated": result["simulated"]
        }
    
    def compare_actions(self, action_a: str, action_b: str, state: Optional[Dict] = None) -> Dict:
        """Compare two actions"""
        result = self.simulate([action_a, action_b], state)
        
        return {
            "action_a": action_a,
            "action_b": action_b,
            "scores": result["all_scores"],
            "winner": result["action"],
            "confidence": abs(result["all_scores"].get(action_a, 0) - result["all_scores"].get(action_b, 0))
        }
    
    def get_simulation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent simulations"""
        return self.simulations[-limit:]
    
    def get_stats(self) -> Dict:
        """Get reality engine statistics"""
        return {
            "simulations_run": len(self.simulations),
            "enabled": self.enabled,
            "world_state_keys": list(self.world.state.keys())
        }
    
    def enable(self):
        """Enable reality simulation"""
        self.enabled = True
    
    def disable(self):
        """Disable reality simulation"""
        self.enabled = False


# Global instance
_reality_engine = None

def get_reality_engine() -> RealityEngine:
    global _reality_engine
    if _reality_engine is None:
        _reality_engine = RealityEngine()
    return _reality_engine


# Convenience functions
def simulate_action(actions: List[str], state: Optional[Dict] = None) -> Dict:
    """Simulate actions and get best result"""
    return get_reality_engine().simulate(actions, state)

def compare_options(action_a: str, action_b: str, state: Optional[Dict] = None) -> Dict:
    """Compare two options"""
    return get_reality_engine().compare_actions(action_a, action_b, state)

def set_world_state(state: Dict):
    """Set the simulation world state"""
    get_reality_engine().set_world_state(state)
