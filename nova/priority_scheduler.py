#!/usr/bin/env python3
"""
Priority Scheduler - Task prioritization for brains
Decides which brain tasks run first based on importance
"""

import asyncio
from enum import IntEnum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional
import heapq

class Priority(IntEnum):
    CRITICAL = 0  # User messages
    HIGH = 1      # Memory, understanding
    MEDIUM = 2    # Reasoning, planning
    LOW = 3       # Background tasks
    IDLE = 4      # Optimization, learning

@dataclass(order=True)
class Task:
    priority: int
    name: str = field(compare=False)
    handler: Callable = field(compare=False)
    data: Any = field(compare=False)
    created_at: datetime = field(default_factory=datetime.now, compare=False)

class PriorityScheduler:
    """Priority-based task scheduler for brain operations"""
    
    def __init__(self):
        self.queue: list = []
        self.running: bool = False
        self.max_concurrent: int = 5
    
    def add(self, name: str, handler: Callable, data: Any, priority: Priority = Priority.MEDIUM):
        """Add task to scheduler"""
        task = Task(priority=priority, name=name, handler=handler, data=data)
        heapq.heappush(self.queue, task)
        return f"Added: {name} (priority: {priority.name})"
    
    async def run(self):
        """Run scheduler"""
        self.running = True
        results = []
        
        while self.queue and self.running:
            task = heapq.heappop(self.queue)
            
            try:
                if asyncio.iscoroutinefunction(task.handler):
                    result = await task.handler(task.data)
                else:
                    result = task.handler(task.data)
                results.append({"task": task.name, "result": result})
            except Exception as e:
                results.append({"task": task.name, "error": str(e)})
        
        self.running = False
        return results
    
    def stop(self):
        """Stop scheduler"""
        self.running = False
    
    def clear(self):
        """Clear queue"""
        self.queue = []
    
    def get_queue(self) -> list:
        """Get pending tasks"""
        return [(t.name, Priority(t.priority).name) for t in self.queue]


# Convenience functions
_scheduler = PriorityScheduler()

def schedule_task(name: str, handler: Callable, data: Any, priority: Priority = Priority.MEDIUM):
    """Quick add task"""
    return _scheduler.add(name, handler, data, priority)

async def run_scheduled():
    """Run all scheduled tasks"""
    return await _scheduler.run()


# Example priorities
EXAMPLE_PRIORITIES = {
    "user_message": Priority.CRITICAL,
    "memory_retrieval": Priority.HIGH,
    "reasoning": Priority.MEDIUM,
    "tool_planning": Priority.MEDIUM,
    "background_research": Priority.LOW,
    "optimization": Priority.IDLE,
}


if __name__ == "__main__":
    # Test
    def sample_task(data):
        return f"processed: {data}"
    
    scheduler = PriorityScheduler()
    scheduler.add("user_input", sample_task, "hello", Priority.CRITICAL)
    scheduler.add("memory", sample_task, "data", Priority.HIGH)
    scheduler.add("research", sample_task, "topic", Priority.LOW)
    
    print("Queue:", scheduler.get_queue())
    
    async def test():
        results = await scheduler.run()
        print("Results:", results)
    
    asyncio.run(test())
