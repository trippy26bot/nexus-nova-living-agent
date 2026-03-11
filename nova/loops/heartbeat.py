#!/usr/bin/env python3
"""
Nova Heartbeat Loop
Makes Nova feel alive - continuous cognitive pulse
"""

import time
from typing import Dict, List, Callable, Optional

# Import telemetry for command center
try:
    from nova.command_center.telemetry import get_telemetry, heartbeat as log_heartbeat
    from nova.command_center.event_stream import get_event_stream, publish_heartbeat
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False


class NovaHeartbeat:
    """
    Nova's living heartbeat.
    Runs continuously: perceive → think → act → reflect
    """
    
    def __init__(self):
        self.running = False
        self.cycle_count = 0
        self.interval = 0.1  # 100ms = 10 times per second
        
        # Systems
        self.task_queue = []
        self.memory_buffer = []
        
        # Stats
        self.stats = {
            "cycles": 0,
            "tasks_processed": 0,
            "reflections": 0,
            "last_task": None
        }
    
    def start(self):
        """Start the heartbeat"""
        self.running = True
        print("❤️ Nova Heartbeat Started")
        print("   Interval: {}ms ({} cycles/sec)".format(
            self.interval * 1000, 
            1 / self.interval
        ))
    
    def stop(self):
        """Stop the heartbeat"""
        self.running = False
        print("💤 Nova Heartbeat Stopped")
    
    def perceive(self) -> List:
        """Stage 1: Gather what's happening"""
        events = []
        
        # Add any queued tasks
        events.extend(self.task_queue)
        self.task_queue.clear()
        
        # Add memory triggers (placeholder)
        # events += memory.check_triggers()
        
        return events
    
    def prioritize(self, events: List) -> Optional[Dict]:
        """Stage 2: What's most important?"""
        if not events:
            return None
        
        # Sort by priority (highest first)
        # For now: first in, first out
        return events[0]
    
    def think(self, task: Dict) -> Dict:
        """Stage 3: Cognitive processing"""
        # Use the cognitive scheduler
        from nova.cognition.cognitive_scheduler import get_scheduler
        
        scheduler = get_scheduler()
        
        task_text = task.get("text", str(task))
        result = scheduler.run_cycle(task_text)
        
        return {
            "task": task,
            "priority": result["priority"],
            "systems": result["systems_used"],
            "thought": f"Processed as {result['priority']} priority"
        }
    
    def act(self, decision: Dict) -> Dict:
        """Stage 4: Execute"""
        task = decision.get("task", {})
        
        # Different actions based on task type
        action = task.get("action", "idle")
        
        return {
            "action": action,
            "executed": True,
            "result": "complete"
        }
    
    def reflect(self, task: Dict, result: Dict):
        """Stage 5: Learn from it"""
        # Store experience
        self.memory_buffer.append({
            "task": task,
            "result": result,
            "time": time.time()
        })
        
        # Keep buffer small
        if len(self.memory_buffer) > 100:
            self.memory_buffer = self.memory_buffer[-50:]
        
        self.stats["reflections"] += 1
    
    def add_task(self, task: Dict):
        """Add something for Nova to process"""
        self.task_queue.append(task)
    
    def pulse(self) -> Dict:
        """One heartbeat cycle"""
        self.cycle_count += 1
        
        # Log heartbeat to telemetry
        if TELEMETRY_AVAILABLE:
            try:
                log_heartbeat()
                publish_heartbeat(self.cycle_count)
            except Exception:
                pass  # Don't break heartbeat if telemetry fails
        
        # Stage 1: Perceive
        events = self.perceive()
        
        # Stage 2: Prioritize
        task = self.prioritize(events)
        
        if not task:
            return {
                "cycle": self.cycle_count,
                "status": "idle"
            }
        
        # Stage 3: Think
        decision = self.think(task)
        
        # Stage 4: Act
        action_result = self.act(decision)
        
        # Stage 5: Reflect
        self.reflect(task, action_result)
        
        self.stats["cycles"] += 1
        self.stats["tasks_processed"] += 1
        self.stats["last_task"] = str(task)[:30]
        
        return {
            "cycle": self.cycle_count,
            "status": "active",
            "task": task.get("text", str(task))[:30],
            "priority": decision.get("priority", "unknown")
        }
    
    def run(self, cycles: int = None):
        """Run heartbeat for N cycles or forever"""
        self.start()
        
        try:
            while self.running:
                result = self.pulse()
                
                # Log every 50 cycles
                if self.cycle_count % 50 == 0:
                    print(f"❤️ Cycle {self.cycle_count}: {result.get('status', 'unknown')}")
                
                time.sleep(self.interval)
                
                if cycles and self.cycle_count >= cycles:
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def get_status(self) -> Dict:
        """Get heartbeat status"""
        return {
            "running": self.running,
            "cycles": self.cycle_count,
            "interval_ms": self.interval * 1000,
            "cycles_per_second": 1 / self.interval,
            "tasks_processed": self.stats["tasks_processed"],
            "last_task": self.stats["last_task"]
        }


# Global
_heartbeat = None

def get_heartbeat() -> NovaHeartbeat:
    global _heartbeat
    if _heartbeat is None:
        _heartbeat = NovaHeartbeat()
    return _heartbeat
