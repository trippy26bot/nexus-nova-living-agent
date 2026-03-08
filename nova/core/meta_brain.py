"""
NOVA Meta Brain - Executive decision maker
Sits above all other brains and makes final decisions
"""
from collections import Counter


class MetaBrain:
    """
    The executive brain that resolves conflicts and makes final decisions.
    Acts like the prefrontal cortex - the "executive function" of NOVA.
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.decision_history = []
    
    def decide(self, context, memory=None):
        """
        Make a decision based on all brain inputs.
        Returns: final decision dict
        """
        # Get all brain outputs
        results = self.orchestrator.process(context, memory)
        
        # Check for system halt first (guardian always has final say)
        if "guardian" in results:
            guardian_vote = results["guardian"]
            if guardian_vote.get("action") == "HALT":
                return {
                    "action": "HALT",
                    "confidence": 1.0,
                    "reason": "System guardian halted: " + guardian_vote.get("reason", ""),
                    "votes": results
                }
        
        # Get weighted votes
        votes = self._weighted_vote(results, context)
        
        # Determine final action
        action = self._resolve_action(votes)
        
        # Calculate confidence
        confidence = self._calculate_confidence(votes, action)
        
        # Build decision
        decision = {
            "action": action,
            "confidence": confidence,
            "votes": results,
            "vote_counts": votes
        }
        
        # Store in history
        self.decision_history.append(decision)
        
        return decision
    
    def _weighted_vote(self, results, context):
        """Calculate weighted votes from all brains"""
        # Get brain activity weights
        brain_weights = self.orchestrator.get_active_brains(context)
        
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
        
        for brain_name, vote in results.items():
            action = vote.get("action", "HOLD")
            if action not in votes:
                continue
            
            confidence = vote.get("confidence", 0.5)
            weight = brain_weights.get(brain_name, 1.0)
            
            votes[action] += confidence * weight
        
        return votes
    
    def _resolve_action(self, votes):
        """Resolve final action from weighted votes"""
        # Must have significant margin to override HOLD
        buy_score = votes["BUY"]
        sell_score = votes["SELL"]
        hold_score = votes["HOLD"]
        
        total = buy_score + sell_score + hold_score
        
        if total == 0:
            return "HOLD"
        
        # Require significant lead to overcome HOLD bias
        if buy_score > sell_score + 0.5 and buy_score > hold_score * 0.7:
            return "BUY"
        
        if sell_score > buy_score + 0.5 and sell_score > hold_score * 0.7:
            return "SELL"
        
        return "HOLD"
    
    def _calculate_confidence(self, votes, action):
        """Calculate confidence in the decision"""
        total = votes["BUY"] + votes["SELL"] + votes["HOLD"]
        
        if total == 0:
            return 0
        
        action_score = votes.get(action, 0)
        
        # Confidence is ratio of action score to total
        confidence = action_score / total
        
        return min(confidence, 1.0)
    
    def get_decision_summary(self):
        """Get summary of recent decisions"""
        if not self.decision_history:
            return "No decisions yet"
        
        recent = self.decision_history[-10:]
        
        summary = {
            "total_decisions": len(self.decision_history),
            "recent_actions": [d["action"] for d in recent],
            "average_confidence": sum(d["confidence"] for d in recent) / len(recent)
        }
        
        return summary
    
    def reflect(self):
        """Self-reflection on recent decisions"""
        if len(self.decision_history) < 5:
            return "Not enough history for reflection"
        
        recent = self.decision_history[-5:]
        
        # Count patterns
        actions = [d["action"] for d in recent]
        confidences = [d["confidence"] for d in recent]
        
        # Simple reflection logic
        if sum(confidences) / len(confidences) < 0.4:
            return "LOW_CONFIDENCE - Consider gathering more information"
        
        if actions.count("HOLD") > 3:
            return "HESITANT - Market conditions unclear"
        
        return "BALANCED - Decision making stable"
