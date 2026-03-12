#!/usr/bin/env python3
"""
Cognitive Bus - Event-driven communication between brains
Allows brains to subscribe to events and react in parallel
"""

import asyncio
from collections import deque
from typing import Dict, List, Callable, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Max events to keep in history
MAX_HISTORY_SIZE = 1000

class EventType(Enum):
    USER_INPUT = "user_input"
    THINKING = "thinking"
    TOOL_CALL = "tool_call"
    MEMORY_LOOKUP = "memory_lookup"
    REASONING = "reasoning"
    CRITIQUE = "critique"
    RESPONSE = "response"
    BACKGROUND_TASK = "background_task"

@dataclass
class Event:
    event_type: EventType
    data: Any
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "system"

class CognitiveBus:
    """Event bus for brain communication"""
    
    def __init__(self, max_history: int = MAX_HISTORY_SIZE):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: deque = deque(maxlen=max_history)  # Fixed memory leak
    
    def subscribe(self, event: EventType, handler: Callable):
        """Subscribe a brain to an event"""
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(handler)
    
    def unsubscribe(self, event: EventType, handler: Callable):
        """Unsubscribe from event"""
        if event in self.subscribers:
            self.subscribers[event] = [h for h in self.subscribers[event] if h != handler]
    
    async def publish(self, event: EventType, data: Any, source: str = "system") -> List[Any]:
        """Publish event to all subscribers"""
        e = Event(event_type=event, data=data, source=source)
        self.event_history.append(e)
        
        results = []
        if event in self.subscribers:
            tasks = [handler(data) for handler in self.subscribers[event]]
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    def get_history(self, event_type: EventType = None, limit: int = 10) -> List[Event]:
        """Get event history"""
        if event_type:
            return [e for e in self.event_history if e.event_type == event_type][-limit:]
        return self.event_history[-limit:]


# Global bus instance
_cognitive_bus = CognitiveBus()

def get_bus() -> CognitiveBus:
    return _cognitive_bus


# Example brain subscriptions
async def reasoning_brain_handler(data):
    return {"brain": "reasoning", "result": "analyzed"}

async def memory_brain_handler(data):
    return {"brain": "memory", "result": "retrieved"}

async def tool_brain_handler(data):
    return {"brain": "tools", "result": "selected"}


# Example setup
def setup_brains(bus: CognitiveBus):
    """Register brains to events"""
    bus.subscribe(EventType.USER_INPUT, reasoning_brain_handler)
    bus.subscribe(EventType.USER_INPUT, memory_brain_handler)
    bus.subscribe(EventType.USER_INPUT, tool_brain_handler)


if __name__ == "__main__":
    bus = CognitiveBus()
    setup_brains(bus)
    
    async def test():
        results = await bus.publish(EventType.USER_INPUT, "Hello world")
        print("Results:", results)
    
    asyncio.run(test())
