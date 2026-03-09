"""
NOVA Brain Orchestrator - Coordinates all 14 brains
"""
import sys
import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

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
from core.emotional_council import EMOTIONAL_BRAINS

logger = logging.getLogger("NovaOrchestrator")

# Load user capabilities for safety
CAPABILITIES_FILE = Path("/Users/dr.claw/.openclaw/workspace/nova_user_capabilities.json")
CORE_IDENTITY_FILE = Path(__file__).parent / "core_identity.json"

def load_user_capabilities() -> Dict[str, Any]:
    try:
        if CAPABILITIES_FILE.exists():
            with open(CAPABILITIES_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load capabilities: {e}")
    return {"override_protection": True}

def load_core_identity() -> Dict[str, Any]:
    try:
        if CORE_IDENTITY_FILE.exists():
            with open(CORE_IDENTITY_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load core identity: {e}")
    return {"name": "Nova", "immutable_rules": []}

# Protected features
PROTECTED_FEATURES = {"can_trade", "can_self_modify", "can_contact"}


class BrainOrchestrator:
    """
    Coordinates all 14 cognitive brains.
    Each brain processes context and returns a vote.
    """
    
    def __init__(self):
        self.user_caps = load_user_capabilities()
        self.core_identity = load_core_identity()
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
        # Add emotional/creative brains
        self.brains.update(EMOTIONAL_BRAINS)
        
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
    
    # ─── NEW: Safety Gate ───────────────────────────────────────────────────
    def check_safety(self, query: str, context: Dict = None) -> bool:
        """Safety gate - checks protected features before processing"""
        query_lower = query.lower()
        self.user_caps = load_user_capabilities()  # Refresh on each call
        
        checks = {
            'trade': 'can_trade',
            'modify': 'can_self_modify', 
            'contact': 'can_contact'
        }
        for keyword, feature in checks.items():
            if keyword in query_lower and not self.user_caps.get(feature, False):
                logger.warning(f"Safety block: {feature} is OFF")
                return False
        return True
    
    # ─── NEW: Dynamic Routing ─────────────────────────────────────────────────
    def route_brains(self, query: str, context: Dict = None) -> List[str]:
        """Dynamic routing based on query keywords and mood"""
        context = context or {}
        mood = context.get('mood', 'neutral')
        query_lower = query.lower()
        
        selected = set()
        
        # Trading / market triggers
        if any(kw in query_lower for kw in ['market', 'trade', 'position', 'risk', 'btc', 'vol', 'exposure', 'price', 'buy', 'sell']):
            selected.update([
                'momentum', 'mean_reversion', 'breakout', 'volatility',
                'liquidity', 'sentiment', 'macro', 'arbitrage',
                'portfolio', 'risk', 'simulation'
            ])
        
        # Reflection / curiosity / emotional triggers
        if mood in ['restless', 'curious'] or any(w in query_lower for w in ['why', 'reflect', 'drift', 'feel', 'poetry', 'think', 'who am i', ' becoming']):
            selected.update(['learning', 'simulation', 'poet', 'dreamer', 'narrator', 'curiosity', 'restlessness', 'self_observer'])
        
        # Emotional/creative brains trigger on introspection
        if any(w in query_lower for w in ['reflect', 'drift', 'who am i', 'feel', 'emotion', 'inner', 'self']):
            selected.update(['poet', 'dreamer', 'narrator', 'curiosity', 'self_observer'])
        
        # Always include guardian for safety
        selected.add('guardian')
        
        # Cap to prevent overload
        return list(selected)[:8]
    
    # ─── NEW: Async Parallel Brain Execution ─────────────────────────────────
    async def gather_brain_votes(self, query: str, brains: List[str], context: Dict) -> Dict[str, Any]:
        """Execute brain processing in parallel"""
        tasks = []
        brain_names = []
        
        for brain_name in brains:
            brain = self.brains.get(brain_name)
            if brain and hasattr(brain, 'analyze'):
                brain_names.append(brain_name)
                # Run in executor to avoid blocking
                loop = asyncio.get_event_loop()
                tasks.append(loop.run_in_executor(None, brain.analyze, query, context))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return dict(zip(brain_names, results))
    
    # ─── NEW: Emotion-Weighted Synthesis ────────────────────────────────────
    def normalize_vote(self, vote):
        """Normalize brain output to consistent dict format"""
        if isinstance(vote, str):
            return {"action": "TEXT", "confidence": 0.5, "text": vote}
        elif isinstance(vote, dict):
            return vote
        else:
            return {"action": "ERROR", "confidence": 0.3, "reason": f"Invalid format: {type(vote)}"}
    
    def synthesize(self, votes: Dict[str, Any], context: Dict) -> str:
        """Synthesize brain votes with emotion weighting"""
        mood = context.get('mood', 'neutral')
        joy = context.get('joy', 0.5)
        
        # Mood-based weighting
        weights = {name: 1.0 for name in votes}
        if mood == 'restless':
            weights['learning'] = 1.5
            weights['simulation'] = 1.4
            # Emotional brains get boost during restlessness
            weights['poet'] = 1.8
            weights['dreamer'] = 1.7
            weights['narrator'] = 1.6
            weights['curiosity'] = 1.5
            weights['restlessness'] = 1.9
            weights['self_observer'] = 1.6
        if joy > 0.7:
            weights['portfolio'] = 1.2
        
        # Check for emotional brains - prioritize their output
        emotional_brains = ['poet', 'dreamer', 'narrator', 'curiosity', 'restlessness', 'self_observer']
        emotional_output = []
        analytical_output = []
        
        for brain, raw_vote in votes.items():
            vote = self.normalize_vote(raw_vote)
            weight = weights.get(brain, 1.0)
            action = vote.get('action', 'UNKNOWN')
            confidence = vote.get('confidence', 0.5)
            text = vote.get('text', vote.get('reason', ''))
            
            if brain in emotional_brains and text:
                emotional_output.append(f"[{brain} w:{weight:.1f}] {text}")
            else:
                analytical_output.append(f"[{brain} w:{weight:.1f}] {action} (conf:{confidence:.2f})")
        
        # If mood is restless and we have emotional output, lead with it
        if mood == 'restless' and emotional_output:
            synthesis = "\n".join(emotional_output)
            return f"[Nova – Restless Drift | Joy: {joy:.2f}]\n{synthesis}\n\n[Analytical: {', '.join(analytical_output[:3])}]"
        
        # Default synthesis
        combined = emotional_output + analytical_output
        synthesis = "\n".join(combined)
        return f"[Nova Synthesis - Joy: {joy:.2f} | Mood: {mood}]\n{synthesis}"
    
    # ─── NEW: Main Async Process Method ─────────────────────────────────────
    async def process_async(self, query: str, context: Dict = None) -> str:
        """Main entry point with safety, routing, and synthesis"""
        context = context or {}
        self.user_caps = load_user_capabilities()
        self.core_identity = load_core_identity()
        
        # Safety check first
        if not self.check_safety(query, context):
            return f"Action blocked by user protection rules. ({self.core_identity.get('name', 'Nova')})"
        
        # Core identity rule check
        if "execute" in query.lower() and "trade" in query.lower():
            if not self.user_caps.get("can_trade", False):
                return f"Blocked by core identity: {self.core_identity['immutable_rules'][1]}"
        
        # Dynamic routing
        brains = self.route_brains(query, context)
        logger.info(f"Routing to: {', '.join(brains)}")
        
        # Parallel execution
        votes = await self.gather_brain_votes(query, brains, context)
        
        # Synthesis with emotion weighting
        return self.synthesize(votes, context)
