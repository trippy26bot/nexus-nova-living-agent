"""
NOVA World Model - Simulates outcomes before acting
"""
import random
from datetime import datetime


class WorldState:
    """
    Tracks the current state of reality for NOVA.
    """
    
    def __init__(self):
        self.environment = {}
        self.market_state = {}
        self.system_state = {}
        self.last_update = None
    
    def update(self, updates):
        """Update world state with new information"""
        if "market" in updates:
            self.market_state.update(updates["market"])
        if "environment" in updates:
            self.environment.update(updates["environment"])
        if "system" in updates:
            self.system_state.update(updates["system"])
        
        self.last_update = datetime.utcnow().isoformat()
    
    def get_market_state(self):
        return self.market_state
    
    def get_environment(self):
        return self.environment
    
    def get_full_state(self):
        return {
            "market": self.market_state,
            "environment": self.environment,
            "system": self.system_state,
            "last_update": self.last_update
        }
    
    def snapshot(self):
        """Create a snapshot of current state"""
        return {
            "market": self.market_state.copy(),
            "environment": self.environment.copy(),
            "system": self.system_state.copy(),
            "timestamp": datetime.utcnow().isoformat()
        }


class OutcomeSimulator:
    """
    Tests possible futures before acting.
    NOVA simulates outcomes internally.
    """
    
    def __init__(self, world_state):
        self.world = world_state
    
    def simulate_action(self, action, context):
        """
        Simulate the outcome of an action.
        Returns: simulated future state
        """
        current_state = self.world.snapshot()
        
        # Simulate based on action type
        if action == "buy":
            return self._simulate_buy(current_state, context)
        elif action == "sell":
            return self._simulate_sell(current_state, context)
        elif action == "hold":
            return self._simulate_hold(current_state, context)
        else:
            return current_state
    
    def _simulate_buy(self, state, context):
        """Simulate buying"""
        # Add position to state
        sim_state = state.copy()
        sim_state["position"] = "long"
        sim_state["action"] = "buy"
        
        # Simulate price movement (randomized based on context)
        volatility = context.get("volatility", 1)
        price_change = random.uniform(-volatility, volatility)
        
        sim_state["simulated_price_change"] = price_change
        sim_state["simulated_profit"] = price_change if price_change > 0 else 0
        sim_state["simulated_loss"] = abs(price_change) if price_change < 0 else 0
        
        return sim_state
    
    def _simulate_sell(self, state, context):
        """Simulate selling"""
        sim_state = state.copy()
        sim_state["position"] = "short"
        sim_state["action"] = "sell"
        
        volatility = context.get("volatility", 1)
        price_change = random.uniform(-volatility, volatility)
        
        # Short profits when price drops
        sim_state["simulated_price_change"] = -price_change
        sim_state["simulated_profit"] = abs(price_change) if price_change < 0 else 0
        sim_state["simulated_loss"] = price_change if price_change > 0 else 0
        
        return sim_state
    
    def _simulate_hold(self, state, context):
        """Simulate holding"""
        sim_state = state.copy()
        sim_state["position"] = state.get("position", "none")
        sim_state["action"] = "hold"
        
        volatility = context.get("volatility", 1)
        price_change = random.uniform(-volatility * 0.5, volatility * 0.5)
        
        sim_state["simulated_price_change"] = price_change
        sim_state["simulated_profit"] = 0
        sim_state["simulated_loss"] = 0
        
        return sim_state
    
    def simulate_multiple(self, actions, context):
        """Simulate multiple possible actions"""
        results = {}
        
        for action in actions:
            results[action] = self.simulate_action(action, context)
        
        return results


class OutcomePredictor:
    """
    Evaluates simulated outcomes and predicts best result.
    """
    
    def __init__(self):
        self.prediction_history = []
    
    def evaluate(self, simulated_state, context):
        """
        Evaluate a simulated state.
        Returns: score and reasoning
        """
        score = 0
        reasons = []
        
        # Evaluate profit potential
        profit = simulated_state.get("simulated_profit", 0)
        loss = simulated_state.get("simulated_loss", 0)
        
        # Risk-adjusted score
        if profit > 0:
            score += profit * 10
            reasons.append(f"potential profit: {profit:.2f}")
        
        if loss > 0:
            risk_penalty = min(loss * 5, 20)  # Cap risk penalty
            score -= risk_penalty
            reasons.append(f"potential loss: {loss:.2f}")
        
        # Consider current market state
        volatility = context.get("volatility", 1)
        if volatility > 2:
            score -= 5
            reasons.append("high volatility risk")
        
        # Consider position size
        current_position = context.get("open_positions", 0)
        if current_position > 3:
            score -= 3
            reasons.append("already have positions")
        
        # Confidence based on how many simulations
        confidence = 0.5 + (0.1 * len(reasons))
        
        return {
            "score": max(-100, min(100, score)),
            "confidence": min(confidence, 0.95),
            "reasons": reasons,
            "action": simulated_state.get("action", "hold")
        }
    
    def rank_actions(self, simulated_results, context):
        """
        Rank multiple possible actions by predicted outcome.
        """
        ranked = []
        
        for action, state in simulated_results.items():
            evaluation = self.evaluate(state, context)
            ranked.append({
                "action": action,
                "score": evaluation["score"],
                "confidence": evaluation["confidence"],
                "reasons": evaluation["reasons"]
            })
        
        # Sort by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        
        return ranked
    
    def predict(self, action, context, world_state):
        """
        Full prediction for an action.
        """
        # Simulate
        simulator = OutcomeSimulator(world_state)
        simulated = simulator.simulate_action(action, context)
        
        # Evaluate
        evaluation = self.evaluate(simulated, context)
        
        # Store in history
        self.prediction_history.append({
            "action": action,
            "evaluation": evaluation,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return evaluation


class WorldModel:
    """
    Combines world state, simulation, and prediction.
    This is NOVA's internal model of reality.
    """
    
    def __init__(self):
        self.world_state = WorldState()
        self.simulator = OutcomeSimulator(self.world_state)
        self.predictor = OutcomePredictor()
    
    def observe(self, data):
        """Update world model with new observations"""
        self.world_state.update(data)
    
    def simulate_before_act(self, possible_actions, context):
        """
        Main world model reasoning:
        1. Get current state
        2. Simulate each possible action
        3. Predict outcomes
        4. Rank by expected value
        """
        # Get current state
        state = self.world_state.get_full_state()
        
        # Simulate all actions
        simulations = self.simulator.simulate_multiple(possible_actions, context)
        
        # Rank them
        ranked = self.predictor.rank_actions(simulations, context)
        
        return {
            "ranked_actions": ranked,
            "best_action": ranked[0] if ranked else None,
            "current_state": state
        }
    
    def predict_outcome(self, action, context):
        """Predict outcome for a single action"""
        return self.predictor.predict(action, context, self.world_state)
    
    def get_world_state(self):
        """Get current world state"""
        return self.world_state.get_full_state()
