"""
Learning Engine - Ties all learning systems together
"""
from .memory_store import MemoryStore
from .trade_logger import TradeLogger
from .brain_tracker import BrainTracker
from .strategy_memory import StrategyMemory
from .simulation_engine import SimulationEngine
from .alliance_manager import AllianceManager

class LearningEngine:
    def __init__(self):
        self.memory = MemoryStore()
        self.trade_logger = TradeLogger()
        self.brain_tracker = BrainTracker()
        self.strategy_memory = StrategyMemory()
        self.simulation = SimulationEngine()
        self.alliances = AllianceManager()
    
    def learn_from_trade(self, votes, decision, result, market_data=None):
        """
        Main learning entry point after a trade resolves.
        votes: list of (brain_name, vote_dict)
        decision: final decision made
        result: pnl (positive = win, negative = loss)
        market_data: context data
        """
        won = result > 0
        
        # Update each brain's accuracy
        for brain_name, vote in votes:
            if vote.get("action") in ["BUY", "SELL", "HOLD"]:
                correct = vote["action"] == decision
                self.brain_tracker.update(brain_name, correct)
        
        # Log the trade
        self.trade_logger.log(
            symbol=market_data.get("symbol", "unknown") if market_data else "unknown",
            action=decision,
            result=result,
            market_data=market_data,
            brain_votes=votes
        )
        
        # Update alliance performance
        # Find brains that agreed with decision
        agreeing_brains = [name for name, v in votes if v.get("action") == decision]
        
        for i, brain_a in enumerate(agreeing_brains):
            for brain_b in agreeing_brains[i+1:]:
                self.alliances.record_outcome(brain_a, brain_b, won)
        
        # Update strategy memory
        strategy = f"brain_consensus_{decision}"
        self.strategy_memory.update(strategy, result)
    
    def get_brain_weights(self):
        """Get dynamic weights for each brain based on accuracy"""
        weights = {}
        for brain_name in [
            "momentum", "mean_reversion", "breakout", "volatility",
            "liquidity", "sentiment", "macro", "arbitrage",
            "portfolio", "risk", "guardian", "simulation", "learning"
        ]:
            weights[brain_name] = self.brain_tracker.weight(brain_name)
        return weights
    
    def weighted_decision(self, votes):
        """Make decision using brain accuracy weights"""
        weights = self.get_brain_weights()
        
        buy_score = 0
        sell_score = 0
        hold_score = 0
        
        for brain_name, vote in votes:
            action = vote.get("action", "HOLD")
            confidence = vote.get("confidence", 0.5)
            weight = weights.get(brain_name, 1.0)
            
            score = confidence * weight
            
            if action == "BUY":
                buy_score += score
            elif action == "SELL":
                sell_score += score
            else:
                hold_score += score
        
        # Return highest scoring action
        scores = {"BUY": buy_score, "SELL": sell_score, "HOLD": hold_score}
        return max(scores, key=scores.get)
    
    def get_performance_report(self):
        """ report"""
        return {
            "tradeGet comprehensive performance_history": self.trade_logger.get_performance(),
            "brain_scores": self.brain_tracker.all_scores(),
            "brain_leaderboard": self.brain_tracker.leaderboard(),
            "strategy_performance": self.strategy_memory.best_strategies(),
            "strong_alliances": self.alliances.strong_alliances()
        }
    
    def should_trade(self, market_data):
        """Quick check if we should trade based on learning"""
        # Check simulation
        ok, reason = self.simulation.quick_test(market_data, "BUY")
        if not ok:
            return False, reason
        
        # Check brain agreement
        leaderboard = self.brain_tracker.leaderboard()
        if leaderboard:
            top_brain_acc = leaderboard[0][1]
            if top_brain_acc < 0.4:
                return False, "brains not performing well"
        
        return True, "ok"
