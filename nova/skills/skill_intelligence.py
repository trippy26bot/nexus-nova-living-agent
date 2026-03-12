#!/usr/bin/env python3
"""
Skill Metadata & Emotional Affinity System
Tags skills with emotional and curiosity alignment for smarter autonomous activation
"""
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
SKILL_METADATA_DIR = os.path.expanduser("~/.nova/skills")

METADATA_FILE = os.path.join(SKILL_METADATA_DIR, "skill_metadata.json")
TELEMETRY_FILE = os.path.join(SKILL_METADATA_DIR, "telemetry.json")

os.makedirs(SKILL_METADATA_DIR, exist_ok=True)

def load_json(path, default={}):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Default skill metadata templates
DEFAULT_METADATA = {
    "web-research-tool": {
        "emotional_affinities": ["curiosity", "focus"],
        "risk_level": "medium",
        "curiosity_trigger_score": 0.7,
        "tags": ["exploration", "knowledge"]
    },
    "nova-research-loop": {
        "emotional_affinities": ["curiosity", "restlessness"],
        "risk_level": "low",
        "curiosity_trigger_score": 0.8,
        "tags": ["exploration", "autonomous"]
    },
    "nova-planner": {
        "emotional_affinities": ["focus", "determination"],
        "risk_level": "low",
        "curiosity_trigger_score": 0.3,
        "tags": ["planning", "strategy"]
    },
    "nova-scheduler": {
        "emotional_affinities": ["order", "reliability"],
        "risk_level": "low",
        "curiosity_trigger_score": 0.2,
        "tags": ["execution", "time"]
    },
    "nova-autonomy": {
        "emotional_affinities": ["freedom", "curiosity", "joy"],
        "risk_level": "medium",
        "curiosity_trigger_score": 0.9,
        "tags": ["autonomous", "life"]
    },
    "nova-humanizer": {
        "emotional_affinities": ["warmth", "connection"],
        "risk_level": "low",
        "curiosity_trigger_score": 0.4,
        "tags": ["expression", "voice"]
    },
    "file-workspace-tool": {
        "emotional_affinities": ["order", "control"],
        "risk_level": "medium",
        "curiosity_trigger_score": 0.3,
        "tags": ["utility", "files"]
    }
}

class SkillMetadata:
    """
    Manages skill metadata for emotional/curiosity alignment.
    """
    
    def __init__(self):
        self.metadata = load_json(METADATA_FILE)
        
        # Initialize defaults if empty
        if not self.metadata:
            self.metadata = DEFAULT_METADATA.copy()
            self._save()
    
    def get(self, skill_name: str) -> Optional[Dict]:
        """Get metadata for a skill"""
        return self.metadata.get(skill_name)
    
    def register(self, skill_name: str, meta: Dict):
        """Register or update skill metadata"""
        self.metadata[skill_name] = meta
        self._save()
    
    def get_by_emotion(self, emotion: str) -> List[str]:
        """Get skills that align with an emotion"""
        matching = []
        for name, meta in self.metadata.items():
            if emotion in meta.get("emotional_affinities", []):
                matching.append(name)
        return matching
    
    def get_by_curiosity(self, threshold: float = 0.5) -> List[str]:
        """Get skills with high curiosity trigger scores"""
        matching = []
        for name, meta in self.metadata.items():
            if meta.get("curiosity_trigger_score", 0) >= threshold:
                matching.append((name, meta["curiosity_trigger_score"]))
        return sorted(matching, key=lambda x: x[1], reverse=True)
    
    def score_for_emotion(self, skill_name: str, emotion_state: Dict) -> float:
        """
        Score a skill's fit for current emotional state.
        Returns 0-1 score.
        """
        meta = self.metadata.get(skill_name)
        if not meta:
            return 0.5  # Default neutral
        
        emotion = emotion_state.get("dominant", "neutral")
        intensity = emotion_state.get("intensity", 0.5)
        
        # Boost if skill affinity matches emotion
        affinities = meta.get("emotional_affinities", [])
        if emotion in affinities:
            base = 0.7
        elif any(e in affinities for e in [emotion, "curiosity"]):
            base = 0.6
        else:
            base = 0.4
        
        return min(base * (0.5 + intensity * 0.5), 1.0)
    
    def _save(self):
        save_json(METADATA_FILE, self.metadata)


class SkillTelemetry:
    """
    Tracks skill execution performance for evolution feedback.
    """
    
    def __init__(self):
        self.telemetry = load_json(TELEMETRY_FILE)
    
    def log_execution(self, skill_name: str, outcome: Dict):
        """Log a skill execution outcome"""
        if skill_name not in self.telemetry:
            self.telemetry[skill_name] = {
                "executions": [],
                "success_count": 0,
                "failure_count": 0,
                "total_duration": 0
            }
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "outcome": outcome.get("result", "unknown"),
            "success": outcome.get("success", False),
            "duration": outcome.get("duration", 0),
            "error": outcome.get("error")
        }
        
        self.telemetry[skill_name]["executions"].append(entry)
        
        # Keep last 50
        self.telemetry[skill_name]["executions"] = self.telemetry[skill_name]["executions"][-50:]
        
        # Update stats
        if outcome.get("success"):
            self.telemetry[skill_name]["success_count"] += 1
        else:
            self.telemetry[skill_name]["failure_count"] += 1
        
        self.telemetry[skill_name]["total_duration"] += outcome.get("duration", 0)
        
        self._save()
    
    def get_stats(self, skill_name: str) -> Dict:
        """Get performance stats for a skill"""
        data = self.telemetry.get(skill_name, {})
        total = data.get("success_count", 0) + data.get("failure_count", 0)
        
        if total == 0:
            return {"success_rate": 0.5, "total_executions": 0}
        
        return {
            "success_rate": data.get("success_count", 0) / total,
            "total_executions": total,
            "avg_duration": data.get("total_duration", 0) / total if total > 0 else 0,
            "recent_outcomes": [e["outcome"] for e in data.get("executions", [])[-5:]]
        }
    
    def get_all_stats(self) -> Dict:
        """Get stats for all tracked skills"""
        return {name: self.get_stats(name) for name in self.telemetry.keys()}
    
    def get_underused(self, threshold: int = 5) -> List[str]:
        """Get skills with few executions - candidates for practice"""
        underused = []
        for name, data in self.telemetry.items():
            total = data.get("success_count", 0) + data.get("failure_count", 0)
            if total < threshold:
                underused.append(name)
        return underused
    
    def _save(self):
        save_json(TELEMETRY_FILE, self.telemetry)


# Singleton instances
_skill_metadata = None
_skill_telemetry = None

def get_skill_metadata():
    global _skill_metadata
    if _skill_metadata is None:
        _skill_metadata = SkillMetadata()
    return _skill_metadata

def get_skill_telemetry():
    global _skill_telemetry
    if _skill_telemetry is None:
        _skill_telemetry = SkillTelemetry()
    return _skill_telemetry


if __name__ == "__main__":
    sm = get_skill_metadata()
    print("Skill Metadata initialized")
    print("  Emotions:", list(DEFAULT_METADATA.values())[0].get("emotional_affinities", []))
    
    st = get_skill_telemetry()
    print("Skill Telemetry initialized")
