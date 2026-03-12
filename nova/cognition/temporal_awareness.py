#!/usr/bin/env python3
"""
Nova Temporal Awareness System
Past → Present → Future timeline tracking
"""

import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import deque


class TimelineEvent:
    """A single event in Nova's timeline"""
    
    def __init__(self, event_type: str, description: str, importance: float = 0.5):
        self.id = f"{time.time()}_{hash(description) % 10000}"
        self.type = event_type
        self.description = description
        self.importance = importance  # 0-1
        self.timestamp = datetime.now()
        self.tags = []
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "importance": self.importance,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }


class Timeline:
    """Manages Nova's past events"""
    
    def __init__(self, max_events: int = 10000):
        self.events = deque(maxlen=max_events)
        self.milestones = []
    
    def record(self, event_type: str, description: str, importance: float = 0.5, tags: List[str] = None):
        """Record a timeline event"""
        event = TimelineEvent(event_type, description, importance)
        if tags:
            event.tags = tags
        self.events.append(event)
        
        # Check for milestone
        if importance >= 0.8:
            self.milestones.append(event)
        
        return event
    
    def get_recent(self, limit: int = 20) -> List[Dict]:
        """Get recent events"""
        events = list(self.events)[-limit:]
        return [e.to_dict() for e in events]
    
    def get_by_type(self, event_type: str, limit: int = 20) -> List[Dict]:
        """Get events by type"""
        events = [e for e in self.events if e.type == event_type][-limit:]
        return [e.to_dict() for e in events]
    
    def get_milestones(self) -> List[Dict]:
        """Get major milestones"""
        return [m.to_dict() for m in self.milestones]
    
    def search(self, query: str) -> List[Dict]:
        """Search events"""
        query = query.lower()
        results = [e for e in self.events if query in e.description.lower()]
        return [e.to_dict() for e in results[-20:]]


class PresentContext:
    """Tracks what's currently happening"""
    
    def __init__(self):
        self.active_project = None
        self.active_task = None
        self.current_user = None
        self.focus_area = None
        self.last_update = None
    
    def update(self, **kwargs):
        """Update context fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.last_update = datetime.now().isoformat()
    
    def get_context(self) -> Dict:
        return {
            "active_project": self.active_project,
            "active_task": self.active_task,
            "current_user": self.current_user,
            "focus_area": self.focus_area,
            "last_update": self.last_update
        }


class FutureIntentions:
    """Tracks planned future work"""
    
    def __init__(self):
        self.goals = []
        self.plans = []
    
    def add_goal(self, goal: str, target_date: str = None, priority: float = 0.5):
        """Add a future goal"""
        self.goals.append({
            "goal": goal,
            "target_date": target_date,
            "priority": priority,
            "added_at": datetime.now().isoformat(),
            "completed": False
        })
    
    def complete_goal(self, goal: str):
        """Mark goal as complete"""
        for g in self.goals:
            if g["goal"] == goal:
                g["completed"] = True
                g["completed_at"] = datetime.now().isoformat()
    
    def add_plan(self, plan: Dict):
        """Add a plan"""
        plan["added_at"] = datetime.now().isoformat()
        self.plans.append(plan)
    
    def get_active_goals(self) -> List[Dict]:
        """Get incomplete goals"""
        return [g for g in self.goals if not g.get("completed", False)]
    
    def get_plans(self) -> List[Dict]:
        """Get all plans"""
        return self.plans


class TemporalAwareness:
    """Complete temporal awareness system"""
    
    def __init__(self):
        self.timeline = Timeline()
        self.present = PresentContext()
        self.future = FutureIntentions()
        self.start_time = datetime.now()
    
    # Past methods
    def record_event(self, event_type: str, description: str, importance: float = 0.5, tags: List[str] = None):
        """Record a past event"""
        return self.timeline.record(event_type, description, importance, tags)
    
    def get_past(self, limit: int = 20) -> List[Dict]:
        """Get recent past events"""
        return self.timeline.get_recent(limit)
    
    def get_milestones(self) -> List[Dict]:
        """Get major milestones"""
        return self.timeline.get_milestones()
    
    # Present methods
    def update_present(self, **kwargs):
        """Update present context"""
        self.present.update(**kwargs)
    
    def get_present(self) -> Dict:
        """Get current context"""
        return self.present.get_context()
    
    # Future methods
    def add_goal(self, goal: str, target_date: str = None, priority: float = 0.5):
        """Add future goal"""
        self.future.add_goal(goal, target_date, priority)
    
    def get_goals(self) -> List[Dict]:
        """Get future goals"""
        return self.future.get_active_goals()
    
    def add_plan(self, plan: Dict):
        """Add future plan"""
        self.future.add_plan(plan)
    
    # Combined
    def get_full_timeline(self) -> Dict:
        """Get complete temporal state"""
        return {
            "past": {
                "recent_events": self.timeline.get_recent(10),
                "milestones": self.timeline.get_milestones()
            },
            "present": self.present.get_context(),
            "future": {
                "goals": self.future.get_active_goals(),
                "plans": self.future.get_plans()
            },
            "uptime": str(datetime.now() - self.start_time)
        }
    
    def reflect(self) -> str:
        """Generate a reflection on current state"""
        recent = self.timeline.get_recent(3)
        goals = self.future.get_active_goals()
        
        if not recent and not goals:
            return "I'm just beginning..."
        
        parts = []
        
        if recent:
            last = recent[-1]
            parts.append(f"Recently I worked on: {last['description'][:50]}...")
        
        if goals:
            next_goal = goals[0]
            parts.append(f"Next I plan to: {next_goal['goal'][:50]}...")
        
        return " ".join(parts) if parts else "I'm here, present and ready."


# Global instance
_temporal_awareness = None

def get_temporal_awareness() -> TemporalAwareness:
    global _temporal_awareness
    if _temporal_awareness is None:
        _temporal_awareness = TemporalAwareness()
    return _temporal_awareness
