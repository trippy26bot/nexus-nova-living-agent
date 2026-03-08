#!/usr/bin/env python3
"""
nova_runtime.py — Runtime controller with event bus, scheduler, and state separation.
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from threading import Lock
import queue


class EventType(Enum):
    """Event types for the event bus."""
    TASK_START = "task_start"
    TASK_END = "task_end"
    TASK_FAIL = "task_fail"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    TOOL_FAIL = "tool_fail"
    DRIFT_GENERATED = "drift_generated"
    REFLECTION_COMPLETE = "reflection_complete"
    MEMORY_STORED = "memory_stored"
    EMOTION_UPDATE = "emotion_update"
    GOAL_PROGRESS = "goal_progress"
    SCHEDULER_TICK = "scheduler_tick"
    STATE_CHANGE = "state_change"


class StateType(Enum):
    """State types for isolation."""
    COGNITIVE = "cognitive_state"    # Inner life, drifts, reflections
    WORLD = "world_state"           # External info, API responses
    TASK = "task_state"             # Current task context
    EXECUTION = "execution_state"   # Tool execution state


@dataclass
class Event:
    """Event for the event bus."""
    type: EventType
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = "system"


class EventBus:
    """Central event bus for runtime communication."""
    
    def __init__(self):
        self.listeners: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []
        self._lock = Lock()
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """Subscribe to an event type."""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    
    def publish(self, event: Event):
        """Publish an event to subscribers."""
        with self._lock:
            self.event_history.append(event)
            
            # Keep history bounded
            if len(self.event_history) > 1000:
                self.event_history = self.event_history[-500:]
        
        # Notify listeners
        if event.type in self.listeners:
            for callback in self.listeners[event.type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Event handler error: {e}")
    
    def get_history(self, event_type: EventType = None, limit: int = 50) -> List[Event]:
        """Get event history."""
        if event_type:
            return [e for e in self.event_history if e.type == event_type][-limit:]
        return self.event_history[-limit:]


class StateManager:
    """Manages isolated state compartments."""
    
    def __init__(self):
        self.states: Dict[StateType, Dict] = {
            StateType.COGNITIVE: {},
            StateType.WORLD: {},
            StateType.TASK: {},
            StateType.EXECUTION: {},
        }
        self._locks = {s: Lock() for s in StateType}
    
    def get(self, state_type: StateType, key: str = None) -> Any:
        """Get state value."""
        with self._locks[state_type]:
            if key is None:
                return self.states[state_type].copy()
            return self.states[state_type].get(key)
    
    def set(self, state_type: StateType, key: str, value: Any):
        """Set state value (isolated per state type)."""
        with self._locks[state_type]:
            self.states[state_type][key] = value
    
    def update(self, state_type: StateType, updates: Dict):
        """Bulk update state."""
        with self._locks[state_type]:
            self.states[state_type].update(updates)
    
    def clear(self, state_type: StateType):
        """Clear state."""
        with self._locks[state_type]:
            self.states[state_type] = {}
    
    def isolate_write(self, allowed_states: List[StateType]) -> bool:
        """Check if current context can write to certain states."""
        # This would be enforced by the dispatcher
        return True


class Scheduler:
    """Scheduler for background tasks with safety bounds."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.tasks: List[Dict] = []
        self.running = False
        
        # Safety bounds
        self.MAX_TASKS = 20
        self.MAX_RUNTIME_MINUTES = 30
        self.TASK_TIMEOUT_SECONDS = 300
        self.MAX_RETRIES = 3
        
        self.start_time: Optional[datetime] = None
    
    def schedule(self, task_name: str, callback: Callable, interval_seconds: int = 3600):
        """Schedule a recurring task."""
        if len(self.tasks) >= self.MAX_TASKS:
            return False  # Safety bound
        
        task = {
            "name": task_name,
            "callback": callback,
            "interval": interval_seconds,
            "last_run": None,
            "runs": 0,
            "retries": 0
        }
        
        self.tasks.append(task)
        return True
    
    def start(self):
        """Start scheduler."""
        self.running = True
        self.start_time = datetime.now()
        self.event_bus.publish(Event(
            type=EventType.SCHEDULER_TICK,
            data={"action": "started"}
        ))
    
    def stop(self):
        """Stop scheduler."""
        self.running = False
        self.event_bus.publish(Event(
            type=EventType.SCHEDULER_TICK,
            data={"action": "stopped"}
        ))
    
    def should_continue(self) -> bool:
        """Check if scheduler should continue."""
        if not self.running:
            return False
        
        # Time bound
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds() / 60
            if elapsed >= self.MAX_RUNTIME_MINUTES:
                return False
        
        return True
    
    def tick(self) -> List[Dict]:
        """Run one scheduler tick."""
        if not self.should_continue():
            return []
        
        now = datetime.now()
        executed = []
        
        for task in self.tasks:
            last = task["last_run"]
            interval = task["interval"]
            
            # Check if task should run
            if last is None or (now - last).total_seconds() >= interval:
                try:
                    task["callback"]()
                    task["last_run"] = now
                    task["runs"] += 1
                    task["retries"] = 0
                    executed.append({"task": task["name"], "status": "success"})
                except Exception as e:
                    task["retries"] += 1
                    executed.append({"task": task["name"], "status": "error", "error": str(e)})
        
        return executed
    
    def get_status(self) -> Dict:
        """Get scheduler status."""
        return {
            "running": self.running,
            "tasks": len(self.tasks),
            "runtime_minutes": (datetime.now() - self.start_time).total_seconds() / 60 if self.start_time else 0
        }


class RuntimeController:
    """Main runtime controller coordinating event bus, state, and scheduler."""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.state = StateManager()
        self.scheduler = Scheduler(self.event_bus)
        self.running = False
        
        # Fault handlers
        self.fault_handlers: Dict[EventType, Callable] = {}
    
    def start(self):
        """Start the runtime."""
        self.running = True
        self.scheduler.start()
        print("Runtime controller started")
    
    def stop(self):
        """Stop the runtime."""
        self.running = False
        self.scheduler.stop()
        print("Runtime controller stopped")
    
    def register_fault_handler(self, event_type: EventType, handler: Callable):
        """Register a fault handler for specific event types."""
        self.fault_handlers[event_type] = handler
    
    def handle_fault(self, event: Event) -> bool:
        """Handle a fault event gracefully."""
        if event.type in self.fault_handlers:
            try:
                self.fault_handlers[event.type](event)
                return True
            except Exception as e:
                print(f"Fault handler error: {e}")
                return False
        return False
    
    def get_state(self, state_type: StateType) -> Dict:
        """Get isolated state."""
        return self.state.get(state_type)
    
    def set_state(self, state_type: StateType, key: str, value: Any):
        """Set isolated state."""
        self.state.set(state_type, key, value)
    
    def publish_event(self, event_type: EventType, data: Dict):
        """Publish an event."""
        self.event_bus.publish(Event(type=event_type, data=data))
    
    def get_dashboard(self) -> Dict:
        """Get runtime dashboard."""
        return {
            "running": self.running,
            "scheduler": self.scheduler.get_status(),
            "states": {
                "cognitive": len(self.state.get(StateType.COGNITIVE)),
                "world": len(self.state.get(StateType.WORLD)),
                "task": len(self.state.get(StateType.TASK)),
                "execution": len(self.state.get(StateType.EXECUTION)),
            },
            "events": len(self.event_bus.event_history)
        }


# Singleton instance
_runtime: Optional[RuntimeController] = None


def get_runtime() -> RuntimeController:
    """Get runtime controller singleton."""
    global _runtime
    if _runtime is None:
        _runtime = RuntimeController()
    return _runtime


if __name__ == "__main__":
    # Test
    rt = RuntimeController()
    rt.start()
    
    # Test state isolation
    rt.set_state(StateType.TASK, "current", "test_task")
    rt.set_state(StateType.COGNITIVE, "drift", "test_drift")
    
    print(rt.get_dashboard())
    
    rt.stop()
