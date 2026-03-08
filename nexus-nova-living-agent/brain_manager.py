"""
Brain Manager - Loads and runs all brains
"""
from brains.momentum_brain import MomentumBrain
from brains.mean_reversion_brain import MeanReversionBrain
from brains.breakout_brain import BreakoutBrain
from brains.volatility_brain import VolatilityBrain
from brains.liquidity_brain import LiquidityBrain
from brains.sentiment_brain import SentimentBrain
from brains.macro_brain import MacroBrain
from brains.arbitrage_brain import ArbitrageBrain
from brains.portfolio_brain import PortfolioBrain
from brains.risk_brain import RiskBrain
from brains.guardian_brain import GuardianBrain
from brains.simulation_brain import SimulationBrain
from brains.learning_brain import LearningBrain
from brains.meta_brain import MetaBrain


class BrainManager:
    def __init__(self):
        self.brains = [
            MomentumBrain(),
            MeanReversionBrain(),
            BreakoutBrain(),
            VolatilityBrain(),
            LiquidityBrain(),
            SentimentBrain(),
            MacroBrain(),
            ArbitrageBrain(),
            PortfolioBrain(),
            RiskBrain(),
            GuardianBrain(),
            SimulationBrain(),
            LearningBrain()
        ]
        self.meta_brain = MetaBrain()
    
    def evaluate(self, market_data, memory):
        """
        Run all brains and return votes.
        Returns: list of (brain_name, vote_dict)
        """
        votes = []
        for brain in self.brains:
            vote = brain.analyze(market_data, memory)
            votes.append((brain.name, vote))
        return votes
    
    def decide(self, votes):
        """Get final decision from votes"""
        # Check for halt first
        for _, vote in votes:
            if vote["action"] == "HALT":
                return {"action": "HALT", "confidence": 1.0, "reason": "system halt"}
        
        return self.meta_brain.decide_with_confidence(votes)
    
    def run(self, market_data, memory):
        """
        Full brain cycle: evaluate -> decide
        Returns: final decision dict
        """
        votes = self.evaluate(market_data, memory)
        action, confidence = self.decide(votes)
        return {"action": action, "confidence": confidence, "votes": votes}
