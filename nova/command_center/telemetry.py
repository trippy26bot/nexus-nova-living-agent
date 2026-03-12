#!/usr/bin/env python3
"""
Nova Telemetry System
Logs internal events for the Command Center
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import deque


class Telemetry:
    """Nova's internal telemetry system"""
    
    def __init__(self, max_events: int = 10000):
        self.events = deque(maxlen=max_events)
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.counters = {}
    
    def log(self, event: str, data: Optional[Dict[str, Any]] = None) -> Dict:
        """Log an event with optional data"""
        entry = {
            "id": len(self.events),
            "time": time.time(),
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data or {},
            "elapsed": time.time() - self.start_time
        }
        
        with self.lock:
            self.events.append(entry)
            # Update counters
            self.counters[event] = self.counters.get(event, 0) + 1
        
        return entry
    
    def get_events(self, limit: int = 100, event_type: Optional[str] = None) -> List[Dict]:
        """Get recent events, optionally filtered by type"""
        with self.lock:
            events = list(self.events)
        
        if event_type:
            events = [e for e in events if e["event"] == event_type]
        
        return events[-limit:]
    
    def get_counter(self, event: str) -> int:
        """Get count of specific event type"""
        return self.counters.get(event, 0)
    
    def get_all_counters(self) -> Dict[str, int]:
        """Get all event counters"""
        return dict(self.counters)
    
    def get_stats(self) -> Dict:
        """Get telemetry statistics"""
        with self.lock:
            return {
                "total_events": len(self.events),
                "counters": dict(self.counters),
                "uptime": time.time() - self.start_time,
                "events_per_second": len(self.events) / max(1, time.time() - self.start_time)
            }
    
    def clear(self):
        """Clear all events (use carefully)"""
        with self.lock:
            self.events.clear()
            self.counters.clear()


# Convenience logging functions
def heartbeat():
    """Log a heartbeat cycle"""
    return _telemetry.log("heartbeat")

def agent_spawn(agent_id: str, role: str = "worker"):
    """Log agent spawn"""
    return _telemetry.log("agent_spawn", {"agent_id": agent_id, "role": role})

def agent_complete(agent_id: str, success: bool = True):
    """Log agent completion"""
    return _telemetry.log("agent_complete", {"agent_id": agent_id, "success": success})

def goal_update(goal_id: str, status: str, progress: float = 0.0):
    """Log goal update"""
    return _telemetry.log("goal_update", {"goal_id": goal_id, "status": status, "progress": progress})

def memory_store(memory_type: str, key: str):
    """Log memory storage"""
    return _telemetry.log("memory_store", {"type": memory_type, "key": key})

def evolution_step(system: str, result: str):
    """Log evolution step"""
    return _telemetry.log("evolution_step", {"system": system, "result": result})

def cognition_thought(thought: str, source: str):
    """Log cognition thought"""
    return _telemetry.log("cognition_thought", {"thought": thought, "source": source})

def error(error_type: str, message: str):
    """Log error"""
    return _telemetry.log("error", {"type": error_type, "message": message})

def user_message(direction: str, preview: str):
    """Log user message"""
    return _telemetry.log("user_message", {"direction": direction, "preview": preview[:50]})


# Global instance
_telemetry = None

def get_telemetry() -> Telemetry:
    global _telemetry
    if _telemetry is None:
        _telemetry = Telemetry()
    return _telemetry
