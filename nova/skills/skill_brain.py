#!/usr/bin/env python3
"""
Nova Skill Brain
Learns and manages reusable behaviors
"""

import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field

@dataclass
class Skill:
    """A learnable skill"""
    name: str
    description: str
    category: str  # reasoning, creative, technical, social
    actions: List[str]  # sequence of actions
    success_rate: float = 0.5
    times_used: int = 0
    times_succeeded: int = 0
    created_at: float = field(default_factory=time.time)
    last_used: float = 0
    efficiency: float = 1.0  # How efficient this skill is

class SkillBrain:
    """
    Learns and manages reusable behaviors.
    Nova can learn, improve, and create new skills.
    """
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.skill_history = []
        
        # Initialize with starter skills
        self._register_starter_skills()
    
    def _register_starter_skills(self):
        """Register starter skills"""
        self.register_skill(
            name="research_topic",
            description="Research a given topic thoroughly",
            category="reasoning",
            actions=["search", "read", "summarize", "analyze"]
        )
        
        self.register_skill(
            name="analyze_market",
            description="Analyze market data and trends",
            category="technical",
            actions=["fetch_data", "calculate", "evaluate", "report"]
        )
        
        self.register_skill(
            name="write_code",
            description="Write code for a given task",
            category="technical",
            actions=["understand_requirements", "design", "implement", "test"]
        )
        
        self.register_skill(
            name="plan_project",
            description="Create a project plan",
            category="reasoning",
            actions=["define_goals", "break_tasks", "estimate", "schedule"]
        )
    
    def register_skill(self, name: str, description: str, category: str, actions: List[str]) -> Skill:
        """Register a new skill"""
        if name in self.skills:
            return self.skills[name]
        
        skill = Skill(
            name=name,
            description=description,
            category=category,
            actions=actions
        )
        
        self.skills[name] = skill
        return skill
    
    def learn_from_action(self, action_sequence: List[str], success: bool):
        """Learn from an action sequence"""
        # Check if this pattern already exists
        pattern = tuple(action_sequence)
        
        # Try to find similar skill
        for skill in self.skills.values():
            if set(skill.actions) == set(action_sequence):
                # Update existing skill
                skill.times_used += 1
                if success:
                    skill.times_succeeded += 1
                skill.success_rate = skill.times_succeeded / skill.times_used
                skill.last_used = time.time()
                return
        
        # Create new skill from this pattern
        skill_name = f"skill_{len(self.skills)}"
        self.register_skill(
            name=skill_name,
            description=f"Learned from action sequence",
            category="learned",
            actions=action_sequence
        )
        
        self.skill_history.append({
            "type": "learned",
            "actions": action_sequence,
            "success": success,
            "time": time.time()
        })
    
    def improve_skill(self, skill_name: str) -> bool:
        """Improve a skill's efficiency"""
        if skill_name not in self.skills:
            return False
        
        skill = self.skills[skill_name]
        
        # Improve efficiency
        skill.efficiency = min(2.0, skill.efficiency * 1.1)
        
        # Small chance to add new action
        if len(skill.actions) < 6:
            possible_actions = ["validate", "optimize", "refine", "extend"]
            skill.actions.append(random.choice(possible_actions))
        
        return True
    
    def compose_skill(self, skill_names: List[str], new_name: str, description: str) -> Optional[Skill]:
        """Combine multiple skills into one"""
        combined_actions = []
        
        for name in skill_names:
            if name not in self.skills:
                return None
            combined_actions.extend(self.skills[name].actions)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_actions = []
        for a in combined_actions:
            if a not in seen:
                seen.add(a)
                unique_actions.append(a)
        
        return self.register_skill(
            name=new_name,
            description=description,
            category="composite",
            actions=unique_actions
        )
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name"""
        return self.skills.get(name)
    
    def get_skills_by_category(self, category: str) -> List[Skill]:
        """Get all skills in a category"""
        return [s for s in self.skills.values() if s.category == category]
    
    def get_best_skill(self, category: str = None) -> Optional[Skill]:
        """Get the most successful skill"""
        candidates = self.skills.values() if not category else self.get_skills_by_category(category)
        
        if not candidates:
            return None
        
        return max(candidates, key=lambda s: s.success_rate * s.efficiency)
    
    def use_skill(self, skill_name: str, success: bool) -> Dict:
        """Use a skill and record the result"""
        if skill_name not in self.skills:
            return {"error": "Skill not found"}
        
        skill = self.skills[skill_name]
        skill.times_used += 1
        if success:
            skill.times_succeeded += 1
        
        skill.success_rate = skill.times_succeeded / skill.times_used
        skill.last_used = time.time()
        
        # Occasionally improve
        if success and random.random() < 0.2:
            self.improve_skill(skill_name)
        
        return {
            "skill": skill_name,
            "success": success,
            "new_success_rate": skill.success_rate
        }
    
    def get_statistics(self) -> Dict:
        """Get skill statistics"""
        categories = {}
        total_success = 0
        total_uses = 0
        
        for skill in self.skills.values():
            categories[skill.category] = categories.get(skill.category, 0) + 1
            total_success += skill.times_succeeded
            total_uses += skill.times_used
        
        return {
            "total_skills": len(self.skills),
            "by_category": categories,
            "total_uses": total_uses,
            "overall_success_rate": total_success / max(1, total_uses),
            "best_skill": self.get_best_skill().name if self.get_best_skill() else None
        }


# Need random for skill improvement
import random

# Global instance
_skill_brain = None

def get_skill_brain() -> SkillBrain:
    global _skill_brain
    if _skill_brain is None:
        _skill_brain = SkillBrain()
    return _skill_brain
