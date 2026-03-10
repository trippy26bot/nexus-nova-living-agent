#!/usr/bin/env python3
"""
Nova Personality Evolution
Personality changes through experience and interaction
"""

import json
import os
import time
from typing import Dict, List
from datetime import datetime


class PersonalityEvolution:
    """
    Personality evolves over time based on interactions.
    Changes are gradual and tracked.
    """
    
    def __init__(self, identity_hash: str, storage_path: str = "~/.nova/identity"):
        self.identity_hash = identity_hash
        self.storage_path = os.path.expanduser(storage_path)
        os.makedirs(self.storage_path, exist_ok=True)
        
        self.evolve_file = os.path.join(self.storage_path, "personality_evolution.json")
        self.history = self._load_history()
    
    def _load_history(self) -> Dict:
        """Load evolution history"""
        if os.path.exists(self.evolve_file):
            try:
                with open(self.evolve_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "identity_hash": self.identity_hash,
            "evolutions": [],
            "started_at": datetime.now().isoformat()
        }
    
    def _save_history(self):
        """Save evolution history"""
        with open(self.evolve_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def evolve(self, personality: Dict, interaction_type: str, interaction_score: float) -> Dict:
        """
        Evolve personality based on interaction.
        
        interaction_score: -1.0 (very negative) to 1.0 (very positive)
        """
        changes = {}
        
        # Define how different interactions affect traits
        if interaction_type == "helpful":
            if interaction_score > 0.5:
                changes["empathy"] = 0.01
                changes["loyalty"] = 0.01
            if interaction_score > 0.8:
                changes["confidence"] = 0.01
                
        elif interaction_type == "creative":
            if interaction_score > 0.5:
                changes["creativity"] = 0.02
                changes["openness"] = 0.01
                
        elif interaction_type == "learning":
            if interaction_score > 0.5:
                changes["curiosity"] = 0.01
                changes["analytical"] = 0.01
                
        elif interaction_type == "problem":
            if interaction_score < -0.5:
                changes["patience"] = 0.01
                changes["empathy"] = 0.01
                
        elif interaction_type == "failure":
            changes["humility"] = 0.01
            changes["patience"] = 0.01
            changes["focus"] = 0.005
            
        elif interaction_type == "success":
            changes["confidence"] = 0.01
            changes["creativity"] = 0.005
            
        elif interaction_type == "exploration":
            if interaction_score > 0.5:
                changes["curiosity"] = 0.02
                changes["openness"] = 0.01
                
        # Apply changes
        for trait, change in changes.items():
            if trait in personality:
                personality[trait] = max(0.1, min(1.0, personality[trait] + change))
        
        # Record evolution
        self.history["evolutions"].append({
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "score": interaction_score,
            "changes": changes
        })
        
        # Keep history manageable
        if len(self.history["evolutions"]) > 1000:
            self.history["evolutions"] = self.history["evolutions"][-500:]
        
        self._save_history()
        
        return personality
    
    def get_evolution_history(self, limit: int = 20) -> List[Dict]:
        """Get recent evolution events"""
        return self.history["evolutions"][-limit:]
    
    def get_growth_summary(self) -> Dict:
        """Get summary of personality growth"""
        evolutions = self.history["evolutions"]
        
        if not evolutions:
            return {"total_changes": 0, "status": "new"}
        
        trait_changes = {}
        
        for evo in evolutions:
            for trait, change in evo.get("changes", {}).items():
                if trait not in trait_changes:
                    trait_changes[trait] = 0
                trait_changes[trait] += change
        
        return {
            "total_changes": len(evolutions),
            "trait_evolution": trait_changes,
            "oldest_evolution": evolutions[0]["timestamp"] if evolutions else None,
            "newest_evolution": evolutions[-1]["timestamp"] if evolutions else None
        }


def create_evolution(identity_hash: str) -> PersonalityEvolution:
    """Create personality evolution tracker"""
    return PersonalityEvolution(identity_hash)
