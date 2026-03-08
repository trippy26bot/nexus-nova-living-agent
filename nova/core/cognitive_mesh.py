"""
NOVA Cognitive Mesh - Parallel brain processing network
Instead of linear brain chain, brains think simultaneously
"""
import concurrent.futures
import time
from datetime import datetime


class BrainState:
    """
    Shared brain state - allows brains to communicate during thinking.
    Like short-term working memory.
    """
    
    def __init__(self):
        self.state = {}
        self.history = []
    
    def update(self, key, value):
        """Update shared brain state"""
        self.state[key] = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get(self, key, default=None):
        """Get value from brain state"""
        item = self.state.get(key, {})
        return item.get("value", default)
    
    def get_all(self):
        """Get all brain state"""
        return {k: v["value"] for k, v in self.state.items()}
    
    def snapshot(self):
        """Take a snapshot of current state"""
        snapshot = {
            "state": self.get_all(),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.history.append(snapshot)
        
        # Keep history bounded
        if len(self.history) > 100:
            self.history = self.history[-50:]
        
        return snapshot
    
    def clear(self):
        """Clear brain state"""
        self.state = {}


class CognitiveMesh:
    """
    The Cognitive Mesh - brains process in parallel and share results.
    This is NOVA's neural-like thinking network.
    """
    
    def __init__(self, brain_manager):
        self.brain_manager = brain_manager
        self.brain_state = BrainState()
        self.use_parallel = True
    
    def process(self, context):
        """
        Process context through parallel brain network.
        Returns: mesh decision with reasoning traces
        """
        start_time = time.time()
        
        if self.use_parallel:
            result = self._process_parallel(context)
        else:
            result = self._process_sequential(context)
        
        # Add processing metadata
        result["processing_time"] = time.time() - start_time
        result["brain_state"] = self.brain_state.get_all()
        
        return result
    
    def _process_parallel(self, context):
        """
        Process multiple brain functions simultaneously.
        This is the key innovation - parallel cognition.
        """
        # Define brain function groups
        perception_funcs = [
            ("volatility", lambda: self._brain_vote("volatility", context)),
            ("liquidity", lambda: self._brain_vote("liquidity", context)),
            ("sentiment", lambda: self._brain_vote("sentiment", context))
        ]
        
        strategy_funcs = [
            ("momentum", lambda: self._brain_vote("momentum", context)),
            ("mean_reversion", lambda: self._brain_vote("mean_reversion", context)),
            ("breakout", lambda: self._brain_vote("breakout", context)),
            ("macro", lambda: self._brain_vote("macro", context))
        ]
        
        risk_funcs = [
            ("risk", lambda: self._brain_vote("risk", context)),
            ("guardian", lambda: self._brain_vote("guardian", context)),
            ("portfolio", lambda: self._brain_vote("portfolio", context))
        ]
        
        # Execute perception brains in parallel
        perception_results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(func): name for name, func in perception_funcs}
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                try:
                    perception_results[name] = future.result()
                    # Share in brain state
                    self.brain_state.update(f"perception_{name}", perception_results[name])
                except Exception as e:
                    perception_results[name] = {"error": str(e)}
        
        # Execute strategy brains in parallel
        strategy_results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(func): name for name, func in strategy_funcs}
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                try:
                    strategy_results[name] = future.result()
                    self.brain_state.update(f"strategy_{name}", strategy_results[name])
                except Exception as e:
                    strategy_results[name] = {"error": str(e)}
        
        # Execute risk brains in parallel
        risk_results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(func): name for name, func in risk_funcs}
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                try:
                    risk_results[name] = future.result()
                    self.brain_state.update(f"risk_{name}", risk_results[name])
                except Exception as e:
                    risk_results[name] = {"error": str(e)}
        
        # Synthesize results through meta brain
        decision = self._synthesize(
            perception_results,
            strategy_results,
            risk_results
        )
        
        return {
            "decision": decision,
            "perception": perception_results,
            "strategy": strategy_results,
            "risk": risk_results,
            "mode": "parallel"
        }
    
    def _process_sequential(self, context):
        """Fallback sequential processing"""
        perception = {
            "volatility": self._brain_vote("volatility", context),
            "liquidity": self._brain_vote("liquidity", context),
            "sentiment": self._brain_vote("sentiment", context)
        }
        
        strategy = {
            "momentum": self._brain_vote("momentum", context),
            "mean_reversion": self._brain_vote("mean_reversion", context),
            "breakout": self._brain_vote("breakout", context)
        }
        
        risk = {
            "risk": self._brain_vote("risk", context),
            "guardian": self._brain_vote("guardian", context)
        }
        
        decision = self._synthesize(perception, strategy, risk)
        
        return {
            "decision": decision,
            "perception": perception,
            "strategy": strategy,
            "risk": risk,
            "mode": "sequential"
        }
    
    def _brain_vote(self, brain_name, context):
        """Get a brain's vote"""
        # Map brain names to actual brain modules
        brain_map = {
            "volatility": lambda: self.brain_manager.brains.get("volatility"),
            "liquidity": lambda: self.brain_manager.brains.get("liquidity"),
            "sentiment": lambda: self.brain_manager.brains.get("sentiment"),
            "momentum": lambda: self.brain_manager.brains.get("momentum"),
            "mean_reversion": lambda: self.brain_manager.brains.get("mean_reversion"),
            "breakout": lambda: self.brain_manager.brains.get("breakout"),
            "macro": lambda: self.brain_manager.brains.get("macro"),
            "risk": lambda: self.brain_manager.brains.get("risk"),
            "guardian": lambda: self.brain_manager.brains.get("guardian"),
            "portfolio": lambda: self.brain_manager.brains.get("portfolio")
        }
        
        brain_func = brain_map.get(brain_name)
        
        if brain_func:
            brain = brain_func()
            if brain:
                try:
                    return brain.analyze(context, {})
                except:
                    return {"action": "HOLD", "confidence": 0.5}
        
        return {"action": "HOLD", "confidence": 0.5}
    
    def _synthesize(self, perception, strategy, risk):
        """
        Synthesize results from all brain groups into final decision.
        """
        # Check guardian first - always has final say
        guardian_vote = risk.get("guardian", {})
        if guardian_vote.get("action") == "HALT":
            return {
                "action": "HALT",
                "confidence": 1.0,
                "reason": "guardian halt"
            }
        
        # Count votes from each group - only valid actions
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
        
        # Map actions to valid ones
        def normalize_action(action):
            if action in ["BUY", "SELL", "HOLD"]:
                return action
            return "HOLD"  # Default unknown actions to HOLD
        
        # Weight votes by group
        group_weights = {
            "perception": 0.2,
            "strategy": 0.5,
            "risk": 0.3
        }
        
        for brain_name, result in perception.items():
            action = normalize_action(result.get("action", "HOLD"))
            confidence = result.get("confidence", 0.5)
            votes[action] += confidence * group_weights["perception"]
        
        for brain_name, result in strategy.items():
            action = normalize_action(result.get("action", "HOLD"))
            confidence = result.get("confidence", 0.5)
            votes[action] += confidence * group_weights["strategy"]
        
        for brain_name, result in risk.items():
            action = normalize_action(result.get("action", "HOLD"))
            confidence = result.get("confidence", 0.5)
            votes[action] += confidence * group_weights["risk"]
        
        # Determine winner
        total = sum(votes.values())
        if total == 0:
            return {"action": "HOLD", "confidence": 0}
        
        # Require significant margin to overcome HOLD bias
        buy_score = votes["BUY"]
        sell_score = votes["SELL"]
        hold_score = votes["HOLD"]
        
        if buy_score > sell_score + 0.3 and buy_score > hold_score * 0.6:
            confidence = buy_score / total
            return {"action": "BUY", "confidence": confidence, "reason": "strategy + perception"}
        
        if sell_score > buy_score + 0.3 and sell_score > hold_score * 0.6:
            confidence = sell_score / total
            return {"action": "SELL", "confidence": confidence, "reason": "risk signals"}
        
        return {"action": "HOLD", "confidence": hold_score / total, "reason": "no clear consensus"}
    
    def get_brain_state(self):
        """Get current shared brain state"""
        return self.brain_state.get_all()
    
    def enable_parallel(self):
        """Enable parallel processing"""
        self.use_parallel = True
    
    def disable_parallel(self):
        """Disable parallel processing (sequential fallback)"""
        self.use_parallel = False
