#!/usr/bin/env python3
"""
Nova Skill Evolution
Turns successful behaviors into reusable skills
"""

from typing import Dict, List, Any
import time

class SkillPattern:
    """A pattern that can become a skill"""
    
    def __init__(self, behavior: str):
        self.behavior = behavior
        self.success_count = 0
        self.failure_count = 0
        self.total_attempts = 0
        self.created_at = time.time()
    
    def record_success(self):
        self.success_count += 1
        self.total_attempts += 1
    
    def record_failure(self):
        self.failure_count += 1
        self.total_attempts += 1
    
    def success_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.success_count / self.total_attempts
    
    def should_learn(self) -> bool:
        """Should this pattern become a skill?"""
        return self.total_attempts >= 5 and self.success_rate() > 0.6


class SkillEvolution:
    """
    Nova learns skills from successful behaviors.
    """
    
    def __init__(self):
        self.patterns = {}
        self.learned_skills = {}
        self.evolution_history = []
    
    def record_behavior(self, behavior: str, success: bool):
        """Record a behavior outcome"""
        if behavior not in self.patterns:
            self.patterns[behavior] = SkillPattern(behavior)
        
        pattern = self.patterns[behavior]
        
        if success:
            pattern.record_success()
        else:
            pattern.record_failure()
        
        # Check if should learn
        if pattern.should_learn():
            self._learn_skill(behavior, pattern)
    
    def _learn_skill(self, behavior: str, pattern: SkillPattern):
        """Learn a new skill from pattern"""
        skill = {
            "name": behavior,
            "success_rate": pattern.success_rate(),
            "attempts": pattern.total_attempts,
            "learned_at": time.time()
        }
        
        self.learned_skills[behavior] = skill
        
        self.evolution_history.append({
            "event": "skill_learned",
            "skill": behavior,
            "success_rate": pattern.success_rate()
        })
    
    def get_skills(self) -> Dict:
        """Get all learned skills"""
        return self.learned_skills
    
    def get_statistics(self) -> Dict:
        """Get evolution statistics"""
        return {
            "patterns_tracked": len(self.patterns),
            "skills_learned": len(self.learned_skills),
            "evolution_events": len(self.evolution_history)
        }


# Global instance
_skill_evolution = None

def get_skill_evolution() -> SkillEvolution:
    global _skill_evolution
    if _skill_evolution is None:
        _skill_evolution = SkillEvolution()
    return _skill_evolution
