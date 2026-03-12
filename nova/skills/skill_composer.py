#!/usr/bin/env python3
"""
Skill Composer & Meta-Skill Emergence
Proposes skill combinations, enables emergent complex behaviors
"""
import os
import sys
import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
sys.path.insert(0, WORKSPACE)

COMPOSER_DIR = os.path.expanduser("~/.nova/skills/composer")
os.makedirs(COMPOSER_DIR, exist_ok=True)

META_SKILLS_FILE = os.path.join(COMPOSER_DIR, "emergent_meta_skills.json")
COMPOSITIONS_FILE = os.path.join(COMPOSER_DIR, "composition_history.json")

def load_json(path, default=[]):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Available skills for composition
AVAILABLE_SKILLS = [
    "nova-planner",
    "nova-scheduler", 
    "web-research-tool",
    "nova-research-loop",
    "file-workspace-tool",
    "nova-autonomy",
    "nova-humanizer",
    "nova-memory"
]

# Proven chains
EXAMPLE_CHAINS = [
    ["nova-planner", "nova-scheduler", "web-research-tool"],
    ["nova-research-loop", "file-workspace-tool", "nova-humanizer"],
    ["nova-memory", "nova-planner", "nova-autonomy"]
]

class SkillComposer:
    """
    Composes skills into chains for complex autonomous behaviors.
    """
    
    def __init__(self):
        self.meta_skills = load_json(META_SKILLS_FILE)
        self.composition_history = load_json(COMPOSITIONS_FILE)
    
    def propose_chain(self, goal: str, context: Dict = None) -> List[str]:
        """
        Propose a skill chain for a given goal.
        Returns list of skills to execute in order.
        """
        # Try to find matching meta-skill first
        for meta in self.meta_skills:
            if meta.get("goal_pattern") and goal.lower() in meta["goal_pattern"].lower():
                return meta["chain"]
        
        # Generate new chain based on goal type
        chain = []
        
        if any(k in goal.lower() for k in ["research", "find", "search"]):
            chain = ["nova-research-loop", "file-workspace-tool"]
        elif any(k in goal.lower() for k in ["plan", "strategy", "organize"]):
            chain = ["nova-planner", "nova-scheduler"]
        elif any(k in goal.lower() for k in ["create", "art", "make"]):
            chain = ["nova-autonomy", "nova-humanizer"]
        elif any(k in goal.lower() for k in ["remember", "recall", "memory"]):
            chain = ["nova-memory", "nova-planner"]
        else:
            # Random creative chain
            chain = random.sample(AVAILABLE_SKILLS, min(3, len(AVAILABLE_SKILLS)))
        
        # Record proposal
        self.composition_history.append({
            "timestamp": datetime.now().isoformat(),
            "goal": goal,
            "proposed_chain": chain,
            "accepted": None
        })
        self.composition_history = self.composition_history[-50:]
        self._save()
        
        return chain
    
    def approve_chain(self, chain: List[str], success: bool):
        """Record chain execution result"""
        if self.composition_history:
            last = self.composition_history[-1]
            if last.get("proposed_chain") == chain:
                last["accepted"] = success
                last["result_time"] = datetime.now().isoformat()
        
        if success:
            # Check if this chain is worth promoting
            recent = [c for c in self.composition_history[-10:] 
                     if c.get("proposed_chain") == chain and c.get("accepted")]
            
            if len(recent) >= 3:
                self._promote_to_meta_skill(chain)
        
        self._save()
    
    def _promote_to_meta_skill(self, chain: List[str]):
        """Promote successful chain to meta-skill"""
        name = f"meta_{chain[0]}_{chain[-1]}"
        
        # Check if already exists
        for meta in self.meta_skills:
            if meta["name"] == name:
                meta["use_count"] = meta.get("use_count", 0) + 1
                return
        
        self.meta_skills.append({
            "name": name,
            "chain": chain,
            "goal_pattern": "",
            "success_count": 1,
            "created": datetime.now().isoformat()
        })
        
        # Try to infer goal pattern
        self.meta_skills[-1]["goal_pattern"] = f"{chain[0]} to {chain[-1]}"
    
    def get_meta_skills(self) -> List[Dict]:
        """Get all emergent meta-skills"""
        return self.meta_skills
    
    def get_recommended_chain(self, emotion_state: Dict = None) -> Optional[List[str]]:
        """
        Get a recommended chain based on emotional state.
        """
        if not self.meta_skills:
            return None
        
        emotion = emotion_state.get("dominant", "neutral") if emotion_state else "neutral"
        
        # Weight by emotion (simplified)
        scored = []
        for meta in self.meta_skills:
            # Higher score for more used
            score = meta.get("use_count", 1)
            scored.append((meta, score))
        
        if scored:
            # Return most used
            return max(scored, key=lambda x: x[1])[0]["chain"]
        
        return None
    
    def _save(self):
        save_json(META_SKILLS_FILE, self.meta_skills)
        save_json(COMPOSITIONS_FILE, self.composition_history)


# Singleton
_composer = None

def get_skill_composer():
    global _composer
    if _composer is None:
        _composer = SkillComposer()
    return _composer


if __name__ == "__main__":
    composer = get_skill_composer()
    chain = composer.propose_chain("research something interesting")
    print("Proposed chain:", chain)
    composer.approve_chain(chain, True)
    print("Meta-skills:", composer.get_meta_skills())
