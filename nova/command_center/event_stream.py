#!/usr/bin/env python3
"""
Nova Event Stream
Real-time event streaming for the Command Center
"""

import asyncio
import json
import time
import threading
from typing import Dict, List, Any, Callable, Optional
from collections import deque
from datetime import datetime


class EventStream:
    """Real-time event stream for Nova"""
    
    def __init__(self, max_listeners: int = 100):
        self.listeners = []
        self.event_history = deque(maxlen=1000)
        self.lock = threading.Lock()
        self.start_time = time.time()
        self._callbacks = []
    
    def add_listener(self, callback: Callable[[Dict], None]):
        """Add an event listener callback"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def remove_listener(self, callback: Callable[[Dict], None]):
        """Remove an event listener"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def publish(self, event: str, data: Optional[Dict[str, Any]] = None):
        """Publish an event to all listeners"""
        entry = {
            "event": event,
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
            "time": time.time() - self.start_time
        }
        
        with self.lock:
            self.event_history.append(entry)
            
            # Notify all callbacks
            for callback in self._callbacks:
                try:
                    callback(entry)
                except Exception as e:
                    print(f"Event listener error: {e}")
    
    def subscribe(self) -> List[Dict]:
        """Get all events (for initial sync)"""
        with self.lock:
            return list(self.event_history)
    
    def get_recent(self, limit: int = 50) -> List[Dict]:
        """Get recent events"""
        with self.lock:
            events = list(self.event_history)
        return events[-limit:]
    
    def get_by_type(self, event_type: str, limit: int = 50) -> List[Dict]:
        """Get events by type"""
        with self.lock:
            events = [e for e in self.event_history if e["event"] == event_type]
        return events[-limit:]
    
    def get_stats(self) -> Dict:
        """Get stream statistics"""
        with self.lock:
            return {
                "total_events": len(self.event_history),
                "listeners": len(self._callbacks),
                "uptime": time.time() - self.start_time
            }


# Global instance
_event_stream = None

def get_event_stream() -> EventStream:
    global _event_stream
    if _event_stream is None:
        _event_stream = EventStream()
    return _event_stream


# Convenience publish functions
def publish_heartbeat(cycle: int):
    """Publish heartbeat event"""
    get_event_stream().publish("heartbeat", {"cycle": cycle})

def publish_agent_spawn(agent_id: str, role: str):
    """Publish agent spawn event"""
    get_event_stream().publish("agent_spawn", {"agent_id": agent_id, "role": role})

def publish_agent_complete(agent_id: str, success: bool, duration: float):
    """Publish agent complete event"""
    get_event_stream().publish("agent_complete", {"agent_id": agent_id, "success": success, "duration": duration})

def publish_goal_update(goal_id: str, status: str, progress: float):
    """Publish goal update event"""
    get_event_stream().publish("goal_update", {"goal_id": goal_id, "status": status, "progress": progress})

def publish_cognition(thought: str, brain: str):
    """Publish cognition event"""
    get_event_stream().publish("cognition", {"thought": thought, "brain": brain})

def publish_error(error_type: str, message: str):
    """Publish error event"""
    get_event_stream().publish("error", {"type": error_type, "message": message})

def publish_memory(operation: str, key: str):
    """Publish memory event"""
    get_event_stream().publish("memory", {"operation": operation, "key": key})
