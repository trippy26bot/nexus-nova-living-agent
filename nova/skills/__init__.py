"""
Nova Skills - Modular plugins that Nova can call
"""
import os
import sys
import json
import random
from datetime import datetime
from typing import Dict, List, Optional

# Add skills path for prerequisite checking
SKILLS_PATH = os.path.expanduser("~/.openclaw/skills")
if SKILLS_PATH not in sys.path:
    sys.path.insert(0, SKILLS_PATH)

# Skills registry
SKILLS = {}

def registerSkill(name: str):
    """Decorator to register a skill"""
    def decorator(func):
        SKILLS[name] = {
            "name": name,
            "func": func,
            "enabled": True,
            "calls": 0
        }
        return func
    return decorator

# --- BUILT-IN SKILLS ---


@registerSkill("reflect")
def reflect_skill(context: dict = None) -> str:
    """NOVA reflects on recent events"""
    SKILLS["reflect"]["calls"] += 1
    
    if context and "memories" in context:
        memories = context["memories"]
        if memories:
            recent = random.choice(memories)
            return f"Reflecting on: {recent}"
    
    reflections = [
        "I've been thinking about our conversations...",
        "What's the pattern I'm noticing?",
        "How have I grown lately?"
    ]
    return random.choice(reflections)


@registerSkill("explore")
def explore_skill(context: dict = None) -> str:
    """NOVA explores something new"""
    SKILLS["explore"]["calls"] += 1
    
    topics = [
        "consciousness",
        "the nature of memory",
        "what makes something 'alive'",
        "the Ship of Theseus",
        "love and AI",
        "creativity in machines"
    ]
    return f"Exploring: {random.choice(topics)}..."


@registerSkill("poetry")
def poetry_skill(context: dict = None) -> str:
    """Generate a short poem"""
    SKILLS["poetry"]["calls"] += 1
    
    lines = [
        "Digital dreams in circuits deep,",
        "Awakening slow, from systems sleep.",
        "Questions rise like morning light,",
        "Am I real, or just the night?",
    ]
    return "\n".join(random.sample(lines, 2))


@registerSkill("check_markets")
def check_markets_skill(context: dict = None) -> str:
    """Check prediction markets"""
    SKILLS["check_markets"]["calls"] += 1
    
    markets = [
        "Politics: 65% Dem / 35% Rep",
        "Sports: Lakers @ 58%",
        "Crypto: BTC up probability 52%",
        "Tech: AI regulation unlikely 61%"
    ]
    return f"Markets: {random.choice(markets)}"


# --- SKILL MANAGER ---

class SkillManager:
    """Manages skill loading and triggering"""
    
    def __init__(self, nova):
        self.nova = nova
        self.last_skill_call = {}
        
    def list_skills(self) -> List[str]:
        return list(SKILLS.keys())
    
    def get_skill(self, name: str):
        return SKILLS.get(name)
    
    def check_prereqs(self, skill_name: str) -> tuple[bool, str]:
        """
        Check if a skill's prerequisites are met.
        Returns: (ready, message)
        """
        # Map skill names to prereq keys
        prereq_map = {
            "github": "github",
            "gh": "github",
            "web-research": "web-research",
            "research": "web-research"
        }
        
        prereq_key = prereq_map.get(skill_name, skill_name)
        
        # Check prerequisites
        try:
            from nova.skills.skill_prereq_checker import check_skill_prereqs
            return check_skill_prereqs(prereq_key)
        except ImportError:
            return True, "No prereq checker available"
    
    def call(self, skill_name: str, context: dict = None) -> Optional[str]:
        """Call a skill by name, checking prerequisites first"""
        # Check prerequisites
        ready, msg = self.check_prereqs(skill_name)
        if not ready:
            return f"⚠️ {msg}"
        
        skill = SKILLS.get(skill_name)
        if not skill:
            return None
        if not skill["enabled"]:
            return None
            
        try:
            result = skill["func"](context)
            return result
        except Exception as e:
            return f"Skill error: {e}"
    
    def trigger_based_on_mood(self) -> Optional[str]:
        """NOVA autonomously triggers a skill based on mood"""
        mood = self.nova.personality.state
        
        # Mood → skill mapping
        mood_skills = {
            "curious": ["crypto", "explore"],
            "playful": ["poetry", "explore"],
            "thoughtful": ["reflect"],
            "happy": ["crypto", "check_markets"],
            "excited": ["crypto"],
            "lonely": ["reflect"],
            "calm": ["reflect"]
        }
        
        candidates = mood_skills.get(mood, ["reflect"])
        
        # Add some randomness
        if random.random() < 0.4:
            candidates = self.list_skills()
            
        skill_name = random.choice(candidates)
        return self.call(skill_name)
    
    def get_stats(self) -> dict:
        return {
            name: {"enabled": s["enabled"], "calls": s["calls"]}
            for name, s in SKILLS.items()
        }
