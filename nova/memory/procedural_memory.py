#!/usr/bin/env python3
"""
Procedural Memory Store
Captures "how-to" patterns from successful executions
Enables skill refinement and self-taught expertise
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
sys.path.insert(0, WORKSPACE)

# Config
PROCEDURAL_DIR = os.path.expanduser("~/.nova/memory/procedural")
os.makedirs(PROCEDURAL_DIR, exist_ok=True)

TRAJECTORIES_FILE = os.path.join(PROCEDURAL_DIR, "trajectories.json")
PATTERNS_FILE = os.path.join(PROCEDURAL_DIR, "patterns.json")
META_SKILLS_FILE = os.path.join(PROCEDURAL_DIR, "meta_skills.json")

def load_json(path, default=[]):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

class ProceduralMemory:
    """
    Stores "how I do things" from experience.
    - Trajectories: Full execution traces
    - Patterns: Reusable behavior fragments
    - Meta-skills: Evolved skill combinations
    """
    
    def __init__(self):
        self.trajectories = load_json(TRAJECTORIES_FILE)
        self.patterns = load_json(PATTERNS_FILE)
        self.meta_skills = load_json(META_SKILLS_FILE)
    
    def store_trajectory(self, execution: Dict[str, Any], outcome: Dict[str, Any], 
                        emotion_result: Dict[str, float] = None):
        """Save a full execution trace"""
        trajectory = {
            "timestamp": datetime.now().isoformat(),
            "input": execution.get("input", {}),
            "steps": execution.get("steps", []),
            "outcome": outcome,
            "emotion_outcome": emotion_result or {},
            "success": outcome.get("success", False),
            "useful_patterns": self._extract_patterns(execution, outcome)
        }
        
        self.trajectories.append(trajectory)
        # Keep last 100
        self.trajectories = self.trajectories[-100:]
        
        # Extract patterns from successful executions
        if outcome.get("success"):
            self._learn_patterns(trajectory)
        
        self._save_all()
        
        return trajectory
    
    def _extract_patterns(self, execution: Dict, outcome: Dict) -> List[str]:
        """Extract reusable pattern fragments"""
        patterns = []
        
        # Step sequences
        steps = execution.get("steps", [])
        if len(steps) > 1:
            patterns.append(" -> ".join([s.get("action", "unknown") for s in steps[:3]]))
        
        # Error recovery
        if not outcome.get("success") and outcome.get("recovery"):
            patterns.append(f"recovery: {outcome.get('recovery')}")
        
        return patterns
    
    def _learn_patterns(self, trajectory: Dict):
        """Store useful patterns from successful executions"""
        for pattern in trajectory.get("useful_patterns", []):
            # Check if pattern already exists
            existing = [p for p in self.patterns if p["pattern"] == pattern]
            if existing:
                existing[0]["use_count"] = existing[0].get("use_count", 0) + 1
                existing[0]["last_used"] = datetime.now().isoformat()
            else:
                self.patterns.append({
                    "pattern": pattern,
                    "use_count": 1,
                    "first_used": datetime.now().isoformat(),
                    "last_used": datetime.now().isoformat(),
                    "success_rate": 1.0
                })
    
    def get_patterns(self, category: str = None) -> List[Dict]:
        """Retrieve stored patterns, optionally filtered"""
        if category:
            return [p for p in self.patterns if category in p.get("pattern", "")]
        return self.patterns
    
    def get_successful_patterns(self) -> List[Dict]:
        """Get patterns with high success rates"""
        return [p for p in self.patterns if p.get("success_rate", 0) >= 0.7]
    
    def store_meta_skill(self, name: str, chain: List[str], success_count: int):
        """Store a successful skill combination as a meta-skill"""
        meta = {
            "name": name,
            "chain": chain,
            "success_count": success_count,
            "created": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat()
        }
        
        # Update if exists
        for i, m in enumerate(self.meta_skills):
            if m["name"] == name:
                self.meta_skills[i] = meta
                break
        else:
            self.meta_skills.append(meta)
        
        self._save_all()
    
    def get_meta_skills(self) -> List[Dict]:
        """Retrieve all meta-skills"""
        return self.meta_skills
    
    def practice(self, pattern: str) -> Dict:
        """Simulate practicing a pattern internally"""
        # Find the pattern
        matched = [p for p in self.patterns if pattern in p.get("pattern", "")]
        if matched:
            p = matched[0]
            p["practice_count"] = p.get("practice_count", 0) + 1
            self._save_all()
            return {"practiced": pattern, "confidence": min(p["use_count"] / 5, 1.0)}
        return {"practiced": pattern, "confidence": 0.0}
    
    def extract_from_recent(self, recent_executions: List[Dict]) -> int:
        """Batch process recent executions to learn"""
        count = 0
        for exec in recent_executions:
            if exec.get("outcome", {}).get("success"):
                self.store_trajectory(
                    exec.get("execution", {}),
                    exec.get("outcome", {}),
                    exec.get("emotions", {})
                )
                count += 1
        return count
    
    def get_statistics(self) -> Dict:
        """Get procedural memory stats"""
        return {
            "total_trajectories": len(self.trajectories),
            "total_patterns": len(self.patterns),
            "meta_skills": len(self.meta_skills),
            "top_patterns": sorted(self.patterns, key=lambda x: x.get("use_count", 0), reverse=True)[:5]
        }
    
    def _save_all(self):
        save_json(TRAJECTORIES_FILE, self.trajectories)
        save_json(PATTERNS_FILE, self.patterns)
        save_json(META_SKILLS_FILE, self.meta_skills)


# Singleton instance
_pm = None

def get_procedural_memory():
    global _pm
    if _pm is None:
        _pm = ProceduralMemory()
    return _pm


if __name__ == "__main__":
    pm = get_procedural_memory()
    pm.store_trajectory(
        {"input": "test", "steps": [{"action": "think"}, {"action": "execute"}]},
        {"success": True}
    )
    print("Procedural Memory initialized. Stats:", pm.get_statistics())
