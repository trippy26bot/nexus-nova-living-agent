"""
Meta Brain - Final decision consensus
"""
from collections import Counter

class MetaBrain:
    def __init__(self):
        self.name = "meta"
    
    def decide(self, votes):
        """
        votes: list of (brain_name, vote_dict)
        Returns: final action
        """
        actions = [vote["action"] for _, vote in votes]
        
        # Filter out non-actions
        actions = [a for a in actions if a in ["BUY", "SELL", "HOLD"]]
        
        if not actions:
            return "HOLD"
        
        counts = Counter(actions)
        return counts.most_common(1)[0][0]
    
    def decide_with_confidence(self, votes):
        """Returns (action, confidence)"""
        actions = [vote["action"] for _, vote in votes if vote["action"] in ["BUY", "SELL", "HOLD"]]
        
        if not actions:
            return ("HOLD", 0.0)
        
        counts = Counter(actions)
        most_common = counts.most_common(1)[0]
        confidence = most_common[1] / len(actions)
        
        return (most_common[0], confidence)
