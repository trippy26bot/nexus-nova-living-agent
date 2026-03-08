"""
Brain Tracker - Tracks which brains are accurate
"""
import json
from pathlib import Path

SCORES_FILE = Path.home() / ".nova/learning/brain_scores.json"

class BrainTracker:
    def __init__(self):
        SCORES_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not SCORES_FILE.exists():
            self.save({})
    
    def save(self, data):
        with open(SCORES_FILE, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        with open(SCORES_FILE) as f:
            return json.load(f)
    
    def update(self, brain_name, correct):
        """Record if a brain's prediction was correct"""
        scores = self.load()
        
        if brain_name not in scores:
            scores[brain_name] = {"wins": 0, "losses": 0, "total": 0}
        
        scores[brain_name]["total"] += 1
        if correct:
            scores[brain_name]["wins"] += 1
        else:
            scores[brain_name]["losses"] += 1
        
        self.save(scores)
    
    def accuracy(self, brain_name):
        """Get accuracy percentage for a brain"""
        scores = self.load()
        brain = scores.get(brain_name)
        
        if not brain or brain["total"] == 0:
            return 0.5  # Default unknown
        
        return brain["wins"] / brain["total"]
    
    def weight(self, brain_name):
        """Get weight based on accuracy (0.1 to 2.0)"""
        acc = self.accuracy(brain_name)
        # Map 0-1 to 0.1-2.0
        return 0.1 + (acc * 1.9)
    
    def all_scores(self):
        """Get all brain scores"""
        return self.load()
    
    def leaderboard(self):
        """Get brains ranked by accuracy"""
        scores = self.load()
        return sorted(
            [(name, self.accuracy(name)) for name in scores],
            key=lambda x: x[1],
            reverse=True
        )
