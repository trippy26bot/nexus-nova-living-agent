"""
Brain Bus - Event-driven communication between brains
Allows scalable, modular brain architecture
"""

import time
import logging
from typing import Dict, List, Any, Callable
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger("BrainBus")

# Event types
class Events:
    # Trading events
    TRADE_SIGNAL = "TRADE_SIGNAL"
    TRADE_PROPOSED = "TRADE_PROPOSED"
    TRADE_EXECUTED = "TRADE_EXECUTED"
    TRADE_REJECTED = "TRADE_REJECTED"
    
    # Risk events
    RISK_WARNING = "RISK_WARNING"
    RISK_CRITICAL = "RISK_CRITICAL"
    
    # Memory events
    MEMORY_CREATED = "MEMORY_CREATED"
    MEMORY_RECALLED = "MEMORY_RECALLED"
    PATTERN_DISCOVERED = "PATTERN_DISCOVERED"
    
    # Cognition events
    THOUGHT_GENERATED = "THOUGHT_GENERATED"
    INSIGHT_EMERGED = "INSIGHT_EMERGED"
    
    # Goal events
    GOAL_CREATED = "GOAL_CREATED"
    GOAL_PROGRESS = "GOAL_PROGRESS"
    GOAL_COMPLETED = "GOAL_COMPLETED"
    
    # System events
    BRAIN_ACTIVATED = "BRAIN_ACTIVATED"
    CYCLE_COMPLETE = "CYCLE_COMPLETE"
    ERROR = "ERROR"


class BrainBus:
    """
    Event bus for brain communication.
    Brains publish events, other brains subscribe and react.
    """
    
    def __init__(self, max_events_per_cycle: int = 100, event_timeout: float = 1.0):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Observability
        self.event_count = 0
        self.events_per_type: Dict[str, int] = defaultdict(int)
        self.last_event_time = time.time()
        self.max_events_per_cycle = max_events_per_cycle
        self.event_timeout = event_timeout
        
        # Event history (last 100)
        self.event_history: List[Dict] = []
        self.max_history = 100
        
        logger.info("BrainBus initialized")
    
    def subscribe(self, event_type: str, handler: Callable):
        """Register a handler for an event type"""
        self.subscribers[event_type].append(handler)
        logger.debug(f"Subscriber registered for {event_type}")
    
    def publish(self, event_type: str, data: Any) -> bool:
        """Publish an event to all subscribers"""
        # Rate limiting
        self.event_count += 1
        if self.event_count > self.max_events_per_cycle:
            logger.warning(f"Event limit reached: {self.event_count}")
            return False
        
        # Track metrics
        self.events_per_type[event_type] += 1
        self.last_event_time = time.time()
        
        # Store in history
        self.event_history.append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Notify subscribers
        handlers = self.subscribers.get(event_type, [])
        if not handlers:
            return True
        
        # Execute handlers with timeout protection
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Handler error for {event_type}: {e}")
                # Publish error event
                self.publish(Events.ERROR, {
                    "event": event_type,
                    "error": str(e)
                })
        
        logger.debug(f"Event published: {event_type}")
        return True
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get bus metrics for observability"""
        return {
            "total_events": self.event_count,
            "events_per_type": dict(self.events_per_type),
            "last_event_seconds_ago": time.time() - self.last_event_time,
            "subscriber_count": sum(len(h) for h in self.subscribers.values()),
            "history_size": len(self.event_history)
        }
    
    def reset_metrics(self):
        """Reset metrics (for new cycle)"""
        self.event_count = 0
        self.events_per_type.clear()
    
    def get_recent_events(self, event_type: str = None, limit: int = 10) -> List[Dict]:
        """Get recent events"""
        if event_type:
            return [e for e in self.event_history if e["type"] == event_type][-limit:]
        return self.event_history[-limit:]


# Global brain bus instance
_brain_bus = None

def get_brain_bus() -> BrainBus:
    """Get or create global brain bus"""
    global _brain_bus
    if _brain_bus is None:
        _brain_bus = BrainBus()
    return _brain_bus
