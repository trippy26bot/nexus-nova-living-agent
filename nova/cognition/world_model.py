#!/usr/bin/env python3
"""
Nova World Model
Simulates outcomes before acting
"""

import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field

@dataclass
class State:
    """Represents a state in the world"""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class Action:
    """An action that can be taken"""
    name: str
    parameters: Dict = field(default_factory=dict)
    preconditions: Dict = field(default_factory=dict)
    effects: Dict = field(default_factory=dict)

class WorldModel:
    """
    Simulates the world to predict outcomes before acting.
    Allows Nova to test ideas safely.
    """
    
    def __init__(self):
        self.current_state = State()
        self.action_history = []
        self.predictions = []
        
        # Define possible actions
        self.actions: Dict[str, Action] = {}
        self._register_default_actions()
    
    def _register_default_actions(self):
        """Register default actions"""
        self.register_action("buy", {"cost": 100}, {"asset": "+1", "cash": "-100"})
        self.register_action("sell", {"asset": "required"}, {"asset": "-1", "cash": "+100"})
        self.register_action("research", {"time": 10}, {"knowledge": "+10"})
        self.register_action("build", {"resources": 50}, {"tool": "+1"})
        self.register_action("explore", {"energy": 20}, {"knowledge": "+5", "discovered": "+1"})
    
    def register_action(self, name: str, preconditions: Dict = None, effects: Dict = None):
        """Register a new action"""
        self.actions[name] = Action(
            name=name,
            preconditions=preconditions or {},
            effects=effects or {}
        )
    
    def set_state(self, **kwargs):
        """Set current world state"""
        self.current_state.data.update(kwargs)
    
    def get_state(self) -> Dict:
        """Get current world state"""
        return self.current_state.data.copy()
    
    def simulate(self, action: str, parameters: Dict = None) -> State:
        """
        Simulate an action and predict the outcome.
        Returns the predicted new state.
        """
        if action not in self.actions:
            return self.current_state
        
        action_obj = self.actions[action]
        params = parameters or {}
        
        # Create predicted state
        predicted_state = State(data=self.current_state.data.copy())
        
        # Apply effects
        for key, value in action_obj.effects.items():
            current = predicted_state.data.get(key, 0)
            
            if isinstance(value, str) and value.startswith("+"):
                # Increment
                amount = int(value[1:])
                predicted_state.data[key] = current + amount
            elif isinstance(value, str) and value.startswith("-"):
                # Decrement
                amount = int(value[1:])
                predicted_state.data[key] = max(0, current - amount)
            else:
                # Set
                predicted_state.data[key] = value
        
        # Store prediction
        self.predictions.append({
            "action": action,
            "parameters": params,
            "predicted_state": predicted_state.data,
            "time": time.time()
        })
        
        return predicted_state
    
    def simulate_sequence(self, actions: List[str]) -> List[State]:
        """Simulate a sequence of actions"""
        states = [self.current_state]
        
        # Save current state
        original = self.current_state.data.copy()
        
        for action in actions:
            result = self.simulate(action)
            states.append(result)
        
        return states
    
    def evaluate_outcome(self, state: State, goals: Dict[str, float]) -> float:
        """
        Evaluate how well a state meets goals.
        Returns score 0-1.
        """
        score = 0.0
        weight_total = 0.0
        
        for key, weight in goals.items():
            weight_total += weight
            value = state.data.get(key, 0)
            
            # Higher is better for positive goals
            if weight > 0:
                score += (value / max(1, value + 1)) * weight
            else:
                # Lower is better for negative goals
                score += (1 / max(1, value + 1)) * abs(weight)
        
        return score / max(1, weight_total) if weight_total > 0 else 0
    
    def choose_best_action(self, possible_actions: List[str], goals: Dict[str, float]) -> Optional[str]:
        """
        Evaluate all possible actions and choose the best one.
        """
        best_action = None
        best_score = -1
        
        for action in possible_actions:
            predicted = self.simulate(action)
            score = self.evaluate_outcome(predicted, goals)
            
            if score > best_score:
                best_score = score
                best_action = action
        
        return best_action
    
    def predict_outcome(self, action: str, goals: Dict[str, float]) -> Dict:
        """Predict outcome and score for an action"""
        predicted = self.simulate(action)
        score = self.evaluate_outcome(predicted, goals)
        
        return {
            "action": action,
            "predicted_state": predicted.data,
            "score": score
        }
    
    def get_prediction_history(self, n: int = 10) -> List[Dict]:
        """Get recent predictions"""
        return self.predictions[-n:]
    
    def clear_predictions(self):
        """Clear prediction history"""
        self.predictions = []
    
    def get_status(self) -> Dict:
        """Get world model status"""
        return {
            "current_state": self.current_state.data,
            "available_actions": list(self.actions.keys()),
            "predictions_made": len(self.predictions)
        }


# Global instance
_world_model = None

def get_world_model() -> WorldModel:
    global _world_model
    if _world_model is None:
        _world_model = WorldModel()
    return _world_model
