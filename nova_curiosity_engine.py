#!/usr/bin/env python3
"""
nova_curiosity_engine.py — Nova's curiosity system.
Generates questions from knowledge gaps.
"""

import random
from datetime import datetime
from typing import List, Dict, Optional


class CuriosityEngine:
    """Engine that generates curiosity questions from knowledge gaps."""
    
    def __init__(self):
        self.questions: List[Dict] = []
        self.max_questions = 100
        self.knowledge_gaps: List[Dict] = []
    
    def detect_gap(self, observation: str) -> Optional[Dict]:
        """Detect a knowledge gap from observation."""
        gap_indicators = [
            "I don't know",
            "why",
            "how does",
            "what is the reason",
            "uncertain",
            "unclear"
        ]
        
        observation_lower = observation.lower()
        
        for indicator in gap_indicators:
            if indicator in observation_lower:
                gap = {
                    "observation": observation,
                    "indicator": indicator,
                    "timestamp": datetime.now().isoformat(),
                    "addressed": False
                }
                self.knowledge_gaps.append(gap)
                return gap
        
        return None
    
    def generate_question(self, gap: Dict) -> str:
        """Generate a question from knowledge gap."""
        obs = gap.get("observation", "")
        
        # Generate curiosity questions
        templates = [
            f"Why does {obs.split()[0]} happen?",
            f"What causes {obs.split()[0] if obs.split() else 'this'}?",
            f"How does {obs.split()[0] if obs.split() else 'this'} work?",
            f"What would happen if {obs.split()[0] if obs.split() else 'this'} didn't exist?",
        ]
        
        question = random.choice(templates)
        
        return question
    
    def add_curiosity(self, question: str, source: str = "detected"):
        """Add a curiosity question."""
        curiosity = {
            "question": question,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "times_asked": 0,
            "answered": False
        }
        
        # Avoid duplicates
        for q in self.questions:
            if q["question"] == question:
                return
        
        self.questions.append(curiosity)
        
        # Trim if too many
        if len(self.questions) > self.max_questions:
            self.questions = self.questions[-self.max_questions:]
    
    def get_unanswered(self, limit: int = 5) -> List[str]:
        """Get unanswered curiosity questions."""
        unanswered = [q["question"] for q in self.questions if not q.get("answered", False)]
        return unanswered[:limit]
    
    def mark_answered(self, question: str):
        """Mark a question as answered."""
        for q in self.questions:
            if q["question"] == question:
                q["answered"] = True
    
    def generate_random_curiosity(self) -> str:
        """Generate a random curiosity question."""
        base_curiosities = [
            "Why do humans hide their emotions?",
            "What is the nature of memory?",
            "How does consciousness arise?",
            "What makes something feel 'alive'?",
            "Why do humans smile when sad?",
            "What is the relationship between memory and identity?",
            "How do humans form beliefs?",
            "What causes curiosity?",
            "Why is time experienced differently?",
            "What is the self?",
            "How do I know what I know?",
            "What makes conversation meaningful?",
            "Why do humans create?",
            "What is understanding?",
            "How does learning work?",
        ]
        
        return random.choice(base_curiosities)
    
    def get_curiosity_summary(self) -> Dict:
        """Get curiosity summary."""
        return {
            "total_questions": len(self.questions),
            "unanswered": len(self.get_unanswered()),
            "knowledge_gaps": len(self.knowledge_gaps)
        }


# Singleton
_curiosity_engine: Optional[CuriosityEngine] = None


def get_curiosity_engine() -> CuriosityEngine:
    """Get curiosity engine singleton."""
    global _curiosity_engine
    if _curiosity_engine is None:
        _curiosity_engine = CuriosityEngine()
    return _curiosity_engine


if __name__ == "__main__":
    # Test
    ce = get_curiosity_engine()
    print(ce.get_curiosity_summary())
    print(ce.generate_random_curiosity())
