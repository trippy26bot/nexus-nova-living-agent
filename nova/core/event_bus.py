#!/usr/bin/env python3
"""
Nova Event Bus - Asynchronous module communication
Keeps the architecture scalable
"""

import time
from typing import Dict, List, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Event:
    type: str
    data: Any
    source: str = "system"
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)

class EventBus:
    """
    Event bus for asynchronous module communication.
    Modules communicate by emitting and listening to events.
    This keeps the architecture scalable.
    """
    
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history = 100
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
        return True
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from an event type"""
        if event_type in self.listeners:
            self.listeners[event_type] = [c for c in self.listeners[event_type] if c != callback]
            return True
        return False
    
    def emit(self, event_type: str, data: Any, source: str = "system", metadata: Dict = None):
        """Emit an event to all subscribers"""
        event = Event(
            type=event_type,
            data=data,
            source=source,
            metadata=metadata or {}
        )
        
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        # Notify listeners
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Event callback error: {e}")
        
        return event
    
    def on(self, event_type: str):
        """Decorator for subscribing to events"""
        def decorator(func: Callable):
            self.subscribe(event_type, func)
            return func
        return decorator
    
    def get_history(self, event_type: str = None, n: int = 10) -> List[Event]:
        """Get event history"""
        if event_type:
            events = [e for e in self.event_history if e.type == event_type]
        else:
            events = self.event_history
        
        return events[-n:]
    
    def clear_history(self):
        """Clear event history"""
        self.event_history = []
    
    def get_stats(self) -> Dict:
        """Get event bus statistics"""
        event_counts = {}
        for event in self.event_history:
            event_counts[event.type] = event_counts.get(event.type, 0) + 1
        
        return {
            "total_events": len(self.event_history),
            "event_types": list(event_counts.keys()),
            "listener_count": sum(len(v) for v in self.listeners.values()),
            "subscriptions": {k: len(v) for k, v in self.listeners.items()}
        }


# Pre-defined event types
class Events:
    USER_MESSAGE = "user.message"
    NOVA_RESPONSE = "nova.response"
    TOOL_CALL = "tool.call"
    TOOL_RESULT = "tool.result"
    EMOTION_CHANGE = "emotion.change"
    GOAL_UPDATE = "goal.update"
    TASK_COMPLETE = "task.complete"
    TASK_FAIL = "task.fail"
    MEMORY_STORE = "memory.store"
    MEMORY_RETRIEVE = "memory.retrieve"
    REFLECTION = "reflection"
    DRIFT_DETECTED = "drift.detected"
    SKILL_INVOKED = "skill.invoked"


# Global instance
_event_bus = None

def get_event_bus():
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
