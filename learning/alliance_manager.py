"""
Alliance Manager - Brains form voting coalitions
"""
import json
from pathlib import Path
from collections import defaultdict

ALLIANCES_FILE = Path.home() / ".nova/learning/alliances.json"

class AllianceManager:
    def __init__(self):
        ALLIANCES_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not ALLIANCES_FILE.exists():
            self.save({})
    
    def save(self, data):
        with open(ALLIANCES_FILE, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        with open(ALLIANCES_FILE) as f:
            return json.load(f)
    
    def form_alliance(self, brain_a, brain_b):
        """Record that two brains agreed"""
        key = tuple(sorted([brain_a, brain_b]))
        
        alliances = self.load()
        
        if key not in alliances:
            alliances[key] = {"agreements": 0, "wins": 0, "losses": 0}
        
        alliances[key]["agreements"] += 1
        self.save(alliances)
    
    def record_outcome(self, brain_a, brain_b, won):
        """Record if an alliance correctly predicted"""
        key = tuple(sorted([brain_a, brain_b]))
        
        alliances = self.load()
        
        if key in alliances:
            if won:
                alliances[key]["wins"] += 1
            else:
                alliances[key]["losses"] += 1
            self.save(alliances)
    
    def alliance_strength(self, brain_a, brain_b):
        """Get how strong an alliance is (0-1)"""
        key = tuple(sorted([brain_a, brain_b]))
        
        alliances = self.load()
        
        if key not in alliances:
            return 0
        
        a = alliances[key]
        total = a["wins"] + a["losses"]
        
        if total < 5:
            return 0  # Need more data
        
        return a["wins"] / total
    
    def get_alliances(self):
        """Get all alliance data"""
        return self.load()
    
    def strong_alliances(self, min_agreements=10):
        """Get strongest alliances"""
        alliances = self.load()
        strong = []
        
        for key, data in alliances.items():
            if data["agreements"] >= min_agreements:
                total = data["wins"] + data["losses"]
                if total > 0:
                    win_rate = data["wins"] / total
                    strong.append((key, win_rate, data["agreements"]))
        
        return sorted(strong, key=lambda x: x[1], reverse=True)
    
    def recommend_alliances(self, brain_names):
        """Suggest which brains should form alliances based on history"""
        recommendations = []
        
        for i, brain_a in enumerate(brain_names):
            for brain_b in brain_names[i+1:]:
                strength = self.alliance_strength(brain_a, brain_b)
                if strength > 0.6:  # Strong alliance
                    recommendations.append((brain_a, brain_b, strength))
        
        return sorted(recommendations, key=lambda x: x[2], reverse=True)
