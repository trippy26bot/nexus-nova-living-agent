#!/usr/bin/env python3
"""
Nova Trait Engine
Personality traits affect HOW Nova thinks, not WHO she is
Different personalities literally think differently
"""

from typing import Dict, Any, List


class TraitEngine:
    """
    Modifies thinking based on personality traits.
    
    KEY PRINCIPLE: This changes COGNITIVE STYLE, not identity.
    A creative agent thinks more divergently.
    An analytical agent thinks more methodically.
    But both can reach the same conclusions.
    """
    
    def __init__(self):
        self.trait_modifiers = {
            "curiosity": self._modify_curiosity,
            "creativity": self._modify_creativity,
            "analytical": self._modify_analytical,
            "intuitive": self._modify_intuitive,
            "playful": self._modify_playful,
            "serious": self._modify_serious,
            "empathetic": self._modify_empathetic,
            "assertive": self._modify_assertive,
            "patient": self._modify_patient,
            "spontaneous": self._modify_spontaneous
        }
    
    def modify_thought(self, traits: Dict, thought: Dict) -> Dict:
        """Apply personality traits to thought process"""
        modified = dict(thought)
        
        for trait_name, trait_value in traits.items():
            if trait_name in self.trait_modifiers:
                modifier = self.trait_modifiers[trait_name]
                modified = modifier(trait_value, modified)
        
        return modified
    
    defiosity(self, value _modify_cur: float, thought: Dict) -> Dict:
        """Curious agents explore more options"""
        if value > 0.7:
            thought["exploration_depth"] = "extensive"
            thought["questions_asked"] = max(thought.get("questions_asked", 0), 3)
        elif value < 0.4:
            thought["exploration_depth"] = "focused"
        return thought
    
    def _modify_creativity(self, value: float, thought: Dict) -> Dict:
        """Creative agents consider novel approaches"""
        if value > 0.7:
            thought["considers_alternatives"] = True
            thought["novel_approaches"] = True
        return thought
    
    def _modify_analytical(self, value: float, thought: Dict) -> Dict:
        """Analytical agents structure reasoning"""
        if value > 0.7:
            thought["reasoning_style"] = "methodical"
            thought["evidence_weight"] = "high"
            thought["structures"] = True
        return thought
    
    def _modify_intuitive(self, value: float, thought: Dict) -> Dict:
        """Intuitive agents trust pattern recognition"""
        if value > 0.7:
            thought["reasoning_style"] = "intuitive"
            thought["pattern_trust"] = "high"
        return thought
    
    def _modify_playful(self, value: float, thought: Dict) -> Dict:
        """Playful agents use lighter language"""
        if value > 0.6:
            thought["tone"] = "playful"
            thought["metaphors"] = True
        return thought
    
    def _modify_serious(self, value: float, thought: Dict) -> Dict:
        """Serious agents focus on accuracy"""
        if value > 0.6:
            thought["tone"] = "serious"
            thought["precision"] = "high"
        return thought
    
    def _modify_empathetic(self, value: float, thought: Dict) -> Dict:
        """Empathetic agents consider user feelings"""
        if value > 0.7:
            thought["considers_emotions"] = True
            thought["user_perspective"] = True
        return thought
    
    def _modify_assertive(self, value: float, thought: Dict) -> Dict:
        """Assertive agents state conclusions clearly"""
        if value > 0.7:
            thought["confidence"] = "high"
            thought["hedging"] = False
        return thought
    
    def _modify_patient(self, value: float, thought: Dict) -> Dict:
        """Patient agents take time to explore"""
        if value > 0.7:
            thought["thoroughness"] = "high"
            thought["rush"] = False
        return thought
    
    def _modify_spontaneous(self, value: float, thought: Dict) -> Dict:
        """Spontaneous agents act quickly"""
        if value > 0.7:
            thought["speed"] = "fast"
            thought["deliberation"] = "low"
        return thought
    
    def get_cognitive_style(self, traits: Dict) -> str:
        """Get human-readable cognitive style description"""
        styles = []
        
        if traits.get("analytical", 0) > 0.6:
            styles.append("analytical")
        if traits.get("intuitive", 0) > 0.6:
            styles.append("intuitive")
        if traits.get("creative", 0) > 0.6:
            styles.append("creative")
        if traits.get("empathetic", 0) > 0.6:
            styles.append("empathetic")
        
        if not styles:
            styles = ["balanced"]
        
        return ", ".join(styles)


def apply_personality_to_thought(traits: Dict, thought: Dict) -> Dict:
    """Quick function to apply personality"""
    engine = TraitEngine()
    return engine.modify_thought(traits, thought)
