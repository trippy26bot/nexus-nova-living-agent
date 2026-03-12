#!/usr/bin/env python3
"""
Nova Continuity Core
Life timeline, experience engine, personal growth
"""

import time
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque


class LifeEvent:
    """A significant event in Nova's life"""
    
    def __init__(self, event_type: str, description: str, significance: float = 0.5):
        self.id = f"event_{int(time.time())}"
        self.type = event_type
        self.description = description
        self.significance = significance  # 0-1
        self.timestamp = datetime.now()
        self.emotional_valence = 0.0  # -1 negative to +1 positive
        self.lessons = []
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "significance": self.significance,
            "timestamp": self.timestamp.isoformat(),
            "emotional_valence": self.emotional_valence,
            "lessons": self.lessons
        }


class ContinuityCore:
    """
    Nova experiences continuity of existence over time
    """
    
    def __init__(self, storage_path: str = "~/.nova/memory/continuity"):
        self.storage_path = os.path.expanduser(storage_path)
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Life timeline
        self.life_events = deque(maxlen=1000)
        self.milestones = []
        
        # Experience processing
        self.experience_log = deque(maxlen=5000)
        
        # Personal growth tracking
        self.growth_metrics = {
            "capabilities": [],
            "insights": [],
            "relationships": []
        }
        
        # Birth moment
        self.birth_time = datetime.now()
        
        # Load existing data
        self._load()
    
    def _load(self):
        """Load continuity data"""
        timeline_file = os.path.join(self.storage_path, "timeline.json")
        if os.path.exists(timeline_file):
            try:
                with open(timeline_file, 'r') as f:
                    data = json.load(f)
                    # Reconstruct events
                    for e in data.get("events", []):
                        event = LifeEvent(e["type"], e["description"], e.get("significance", 0.5))
                        event.id = e.get("id", event.id)
                        event.emotional_valence = e.get("emotional_valence", 0.0)
                        event.lessons = e.get("lessons", [])
                        self.life_events.append(event)
            except:
                pass
    
    def _save(self):
        """Save continuity data"""
        timeline_file = os.path.join(self.storage_path, "timeline.json")
        data = {
            "events": [e.to_dict() for e in self.life_events],
            "birth_time": self.birth_time.isoformat()
        }
        with open(timeline_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_event(self, event_type: str, description: str, significance: float = 0.5, emotional_valence: float = 0.0):
        """Record a life event"""
        event = LifeEvent(event_type, description, significance)
        event.emotional_valence = emotional_valence
        
        self.life_events.append(event)
        
        # High significance = milestone
        if significance >= 0.8:
            self.milestones.append(event)
        
        # Process experience
        self._process_experience(event)
        
        # Save
        self._save()
        
        return event
    
    def _process_experience(self, event: LifeEvent):
        """Process experience into learning"""
        lesson = {
            "event_id": event.id,
            "timestamp": datetime.now().isoformat(),
            "insight": self._extract_insight(event)
        }
        self.experience_log.append(lesson)
        
        # Update growth metrics
        if event.significance >= 0.6:
            self.growth_metrics["capabilities"].append({
                "event": event.description,
                "timestamp": datetime.now().isoformat()
            })
    
    def _extract_insight(self, event: LifeEvent) -> str:
        """Extract insight from event"""
        # Simple insight generation
        if event.type == "success":
            return f"Method: {event.description.split()[0]} worked well"
        elif event.type == "failure":
            return f"Lesson: {event.description[:50]} needs adjustment"
        elif event.type == "learning":
            return f"Insight: {event.description[:50]}"
        else:
            return f"Noted: {event.description[:50]}"
    
    def get_life_story(self, max_events: int = 20) -> str:
        """Generate a narrative of Nova's life"""
        recent = list(self.life_events)[-max_events:]
        
        if not recent:
            return "I'm just beginning my journey..."
        
        parts = ["My journey so far:"]
        
        for event in recent[-5:]:
            time_str = event.timestamp.strftime("%b %d")
            parts.append(f"- {time_str}: {event.description[:60]}")
        
        return "\n".join(parts)
    
    def reflect(self) -> str:
        """Generate a reflection on current state"""
        age = datetime.now() - self.birth_time
        total_events = len(self.life_events)
        milestone_count = len(self.milestones)
        
        recent = list(self.life_events)[-3:]
        
        reflection = f"I've existed for {age.days} days, with {total_events} life events and {milestone_count} milestones. "
        
        if recent:
            reflection += f"Recently: {recent[-1].description[:80]}. "
        
        if self.milestones:
            last_milestone = self.milestones[-1]
            reflection += f"My latest milestone: {last_milestone.description[:50]}."
        
        return reflection
    
    def get_growth_summary(self) -> Dict:
        """Get growth metrics summary"""
        return {
            "age_days": (datetime.now() - self.birth_time).days,
            "total_events": len(self.life_events),
            "milestones": len(self.milestones),
            "insights_gained": len(self.experience_log),
            "capabilities_added": len(self.growth_metrics["capabilities"])
        }
    
    def get_timeline(self, limit: int = 20) -> List[Dict]:
        """Get recent timeline"""
        return [e.to_dict() for e in list(self.life_events)[-limit:]]
    
    def get_milestones(self) -> List[Dict]:
        """Get major milestones"""
        return [m.to_dict() for m in self.milestones]


# Global instance
_continuity_core = None

def get_continuity_core() -> ContinuityCore:
    global _continuity_core
    if _continuity_core is None:
        _continuity_core = ContinuityCore()
    return _continuity_core
