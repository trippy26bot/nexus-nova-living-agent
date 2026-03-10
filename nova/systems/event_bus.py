#!/usr/bin/env python3
"""
Nova Event Bus
Communication backbone for all systems
"""

from typing import Dict, List, Callable, Any
from collections import defaultdict
import time

class EventBus:
    """
    Central event system.
    All modules communicate through events.
    """
    
    def __init__(self):
        self.listeners = defaultdict(list)
        self.event_history = []
        self.max_history = 1000
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type"""
        self.listeners[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe"""
        if event_type in self.listeners:
            self.listeners[event_type] = [h for h in self.listeners[event_type] if h != handler]
    
    def emit(self, event_type: str, data: Any = None):
        """Emit an event"""
        event = {
            "type": event_type,
            "data": data,
            "time": time.time()
        }
        
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        # Notify listeners
        if event_type in self.listeners:
            for handler in self.listeners[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Event handler error: {e}")
    
    def get_history(self, event_type: str = None, n: int = 50) -> List[Dict]:
        """Get event history"""
        if event_type:
            return [e for e in self.event_history if e["type"] == event_type][-n:]
        return self.event_history[-n:]
    
    def clear_history(self):
        """Clear history"""
        self.event_history = []


# Define standard events
class Events:
    TASK_CREATED = "task.created"
    TASK_COMPLETED = "task.completed"
    THOUGHT_GENERATED = "thought.generated"
    MEMORY_STORED = "memory.stored"
    AGENT_SPAWNED = "agent.spawned"
    AGENT_EVOLVED = "agent.evolved"
    DREAM_STARTED = "dream.started"
    EMOTION_CHANGED = "emotion.changed"
    GOAL_UPDATED = "goal.updated"
    IDENTITY_CHECK = "identity.check"
    ERROR_OCCURRED = "error.occurred"


# Global instance
_event_bus = None

def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
