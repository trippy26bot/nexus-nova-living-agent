"""
NOVA Brain Orchestrator - Coordinates all 14 brains
"""
import sys
import os
from pathlib import Path

# Resolve imports from the actual checked-out repo, not a hardcoded folder name.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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


class BrainOrchestrator:
    """
    Coordinates all 14 cognitive brains.
    Each brain processes context and returns a vote.
    """
    
    def __init__(self):
        self.brains = {
            "momentum": MomentumBrain(),
            "mean_reversion": MeanReversionBrain(),
            "breakout": BreakoutBrain(),
            "volatility": VolatilityBrain(),
            "liquidity": LiquidityBrain(),
            "sentiment": SentimentBrain(),
            "macro": MacroBrain(),
            "arbitrage": ArbitrageBrain(),
            "portfolio": PortfolioBrain(),
            "risk": RiskBrain(),
            "guardian": GuardianBrain(),
            "simulation": SimulationBrain(),
            "learning": LearningBrain()
        }
        
        # Brain categories for organization
        self.perception_brains = ["volatility", "liquidity"]
        self.strategy_brains = ["momentum", "mean_reversion", "breakout", "sentiment", "macro", "arbitrage"]
        self.risk_brains = ["risk", "portfolio", "guardian"]
        self.meta_brains = ["simulation", "learning"]
    
    def process(self, context, memory=None):
        """
        Process context through all brains.
        Returns: dict of brain_name -> vote
        """
        memory = memory or {}
        results = {}
        
        for name, brain in self.brains.items():
            try:
                vote = brain.analyze(context, memory)
                results[name] = vote
            except Exception as e:
                results[name] = {"action": "ERROR", "confidence": 0, "reason": str(e)}
        
        return results
    
    def get_category_results(self, context, memory=None):
        """Get results organized by brain category"""
        all_results = self.process(context, memory)
        
        return {
            "perception": {k: v for k, v in all_results.items() if k in self.perception_brains},
            "strategy": {k: v for k, v in all_results.items() if k in self.strategy_brains},
            "risk": {k: v for k, v in all_results.items() if k in self.risk_brains},
            "meta": {k: v for k, v in all_results.items() if k in self.meta_brains}
        }
    
    def get_active_brains(self, context):
        """Determine which brains should be most influential based on context"""
        # Simple regime-based brain activation
        volatility = context.get("volatility", 0)
        trend = context.get("price_change", 0)
        
        active = {
            "momentum": 1.0,
            "mean_reversion": 1.0,
            "breakout": 1.0,
            "volatility": 1.0,
            "liquidity": 1.0,
            "sentiment": 1.0,
            "macro": 1.0,
            "arbitrage": 1.0,
            "portfolio": 1.0,
            "risk": 1.0,
            "guardian": 1.0,
            "simulation": 1.0,
            "learning": 1.0
        }
        
        # Adjust weights based on market conditions
        if abs(trend) > 2:  # Strong trend
            active["momentum"] = 1.5
            active["breakout"] = 1.3
            active["mean_reversion"] = 0.5
        
        if volatility > 2:  # High volatility
            active["risk"] = 1.5
            active["guardian"] = 1.5
            active["volatility"] = 1.3
        
        return active
    
    def count_votes(self, results):
        """Count votes from all brains"""
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0, "HALT": 0}
        
        for brain_name, vote in results.items():
            action = vote.get("action", "HOLD")
            if action in votes:
                votes[action] += vote.get("confidence", 0.5)
        
        return votes
