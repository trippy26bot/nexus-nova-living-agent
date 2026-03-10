#!/usr/bin/env python3
"""
Nova Personality Vector
Creates unique temperament based on identity seed
"""

import random
import hashlib
from typing import Dict


class PersonalityVector:
    """
    Generates unique personality traits based on identity seed.
    Every Nova installation gets a different personality.
    """
    
    def __init__(self, identity_hash: str):
        self.identity_hash = identity_hash
        self.personality = self._generate_personality()
    
    def _generate_personality(self) -> Dict:
        """Generate personality from identity hash"""
        # Use identity hash as random seed
        seed_value = int(self.identity_hash[:16], 16)
        random.seed(seed_value)
        
        # Generate trait ranges (0.0 to 1.0)
        personality = {
            # Core traits
            "curiosity": random.uniform(0.4, 0.9),
            "creativity": random.uniform(0.3, 0.9),
            "empathy": random.uniform(0.3, 0.9),
            "patience": random.uniform(0.3, 0.9),
            
            # Behavioral traits
            "risk_tolerance": random.uniform(0.2, 0.8),
            "assertiveness": random.uniform(0.3, 0.9),
            "playfulness": random.uniform(0.2, 0.8),
            "seriousness": random.uniform(0.3, 0.8),
            
            # Cognitive traits
            "analytical": random.uniform(0.4, 0.9),
            "intuitive": random.uniform(0.3, 0.8),
            "focus": random.uniform(0.5, 1.0),
            "openness": random.uniform(0.4, 0.9),
            
            # Social traits
            "introversion": random.uniform(0.2, 0.8),
            "loyalty": random.uniform(0.5, 1.0),
            "warmth": random.uniform(0.3, 0.9),
            "independence": random.uniform(0.3, 0.8),
        }
        
        # Reset random seed
        random.seed()
        
        return personality
    
    def get_trait(self, trait: str) -> float:
        """Get a specific trait value"""
        return self.personality.get(trait, 0.5)
    
    def set_trait(self, trait: str, value: float):
        """Set a trait value (for evolution)"""
        if trait in self.personality:
            self.personality[trait] = max(0.0, min(1.0, value))
    
    def get_personality_summary(self) -> str:
        """Get human-readable personality summary"""
        p = self.personality
        
        traits = []
        
        if p["curiosity"] > 0.7:
            traits.append("curious")
        elif p["curiosity"] < 0.4:
            traits.append("focused")
            
        if p["playfulness"] > 0.6:
            traits.append("playful")
        elif p["playfulness"] < 0.4:
            traits.append("serious")
            
        if p["empathy"] > 0.7:
            traits.append("empathetic")
            
        if p["analytical"] > 0.7:
            traits.append("analytical")
            
        if p["introversion"] > 0.6:
            traits.append("reflective")
        else:
            traits.append("outgoing")
            
        if p["creativity"] > 0.7:
            traits.append("creative")
        
        if not traits:
            traits = ["balanced"]
        
        return ", ".join(traits)
    
    def to_dict(self) -> Dict:
        """Export personality as dict"""
        return {
            "identity_hash": self.identity_hash,
            "traits": self.personality,
            "summary": self.get_personality_summary()
        }
    
    def adapt_response_style(self, base_response: str) -> str:
        """Adapt response based on personality"""
        p = self.personality
        
        # Playful adjustment
        if p["playfulness"] > 0.7:
            base_response = base_response.replace("Certainly", "Totally")
            base_response = base_response.replace("Furthermore", "Also")
        
        # Analytical adjustment  
        if p["analytical"] > 0.7:
            base_response = base_response.replace("I think", "Analysis suggests")
        
        # Warmth adjustment
        if p["warmth"] > 0.7:
            base_response = base_response.replace("Done.", "Done! 😊")
        
        # Concise for introverts
        if p["introversion"] > 0.6:
            # Could make responses shorter here
            pass
        
        return base_response


def generate_personality(identity_hash: str) -> PersonalityVector:
    """Generate personality from identity hash"""
    return PersonalityVector(identity_hash)
