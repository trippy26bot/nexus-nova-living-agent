#!/usr/bin/env python3
"""
nova_attention.py — Attention system.
Decides what memories matter.
"""

import re
from datetime import datetime
from typing import Dict


class AttentionSystem:
    """Attention scoring for memories."""
    
    def __init__(self):
        self.weights = {
            "novelty": 0.25,
            "emotional": 0.25,
            "repetition": 0.15,
            "user_emphasis": 0.20,
            "goal_relevance": 0.15
        }
    
    def score(self, content: str, context: Dict = None) -> float:
        """Score content for importance."""
        score = 0.0
        
        # Novelty detection
        score += self._novelty_score(content) * self.weights["novelty"]
        
        # Emotional content
        score += self._emotional_score(content) * self.weights["emotional"]
        
        # Repetition (less repetition = higher score)
        score += self._repetition_score(content) * self.weights["repetition"]
        
        # User emphasis
        score += self._emphasis_score(content) * self.weights["user_emphasis"]
        
        # Goal relevance (if context provided)
        if context:
            score += self._goal_relevance_score(content, context) * self.weights["goal_relevance"]
        
        return min(1.0, max(0.0, score))
    
    def _novelty_score(self, content: str) -> float:
        """Score for novelty."""
        content = content.lower()
        
        # Unknown concepts indicate novelty
        unknown_indicators = [
            "i don't know", "not sure", "wonder", 
            "new", "first", "discovered"
        ]
        
        for indicator in unknown_indicators:
            if indicator in content:
                return 0.8
        
        return 0.3
    
    def _emotional_score(self, content: str) -> float:
        """Score for emotional content."""
        content = content.lower()
        
        emotional_words = [
            "feel", "feeling", "emotion", "sad", "happy",
            "love", "hate", "angry", "excited", "worried",
            "frustrated", "hopeful", "grateful", "amazing",
            "incredible", "pain", "joy"
        ]
        
        count = sum(1 for word in emotional_words if word in content)
        
        return min(1.0, count * 0.2)
    
    def _repetition_score(self, content: str) -> float:
        """Score based on repetition."""
        words = content.lower().split()
        
        if len(words) < 3:
            return 0.0
        
        # Check for repeated words
        unique = len(set(words))
        ratio = unique / len(words)
        
        # Lower ratio = more repetition = lower score
        return ratio
    
    def _emphasis_score(self, content: str) -> float:
        """Score for user emphasis."""
        score = 0.0
        
        # Exclamation
        if "!" in content:
            score += 0.3
        
        # ALL CAPS words
        caps_words = [w for w in content.split() if w.isupper() and len(w) > 1]
        score += min(0.3, len(caps_words) * 0.1)
        
        # Important phrases
        important = ["important", "critical", "remember", "never forget"]
        for phrase in important:
            if phrase in content.lower():
                score += 0.4
        
        return min(1.0, score)
    
    def _goal_relevance_score(self, content: str, context: Dict) -> float:
        """Score for goal relevance."""
        score = 0.0
        
        goals = context.get("active_goals", [])
        
        content_lower = content.lower()
        
        for goal in goals:
            goal_lower = goal.lower()
            if any(word in content_lower for word in goal_lower.split()):
                score += 0.3
        
        return min(1.0, score)
    
    def should_store(self, content: str, context: Dict = None) -> bool:
        """Decide if content should be stored as important."""
        score = self.score(content, context)
        
        # Store if above threshold
        return score > 0.4


# Singleton
_attention: AttentionSystem = None


def get_attention() -> AttentionSystem:
    """Get attention system singleton."""
    global _attention
    if _attention is None:
        _attention = AttentionSystem()
    return _attention


if __name__ == "__main__":
    a = get_attention()
    
    tests = [
        "I don't know how this works!",
        "Nova was my first project.",
        "ok",
        "This is CRITICAL - never forget this!",
    ]
    
    for t in tests:
        score = a.score(t)
        store = a.should_store(t)
        truncated = t[:30] if len(t) > 30 else t
        print(f"'{truncated}...' score={score:.2f} store={store}")
