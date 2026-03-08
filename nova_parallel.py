#!/usr/bin/env python3
"""
NOVA PARALLEL — Async Parallel Agent Execution
Run multiple agent tasks simultaneously.

Uses asyncio for concurrent task execution.
"""

import asyncio
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import concurrent.futures
import threading

# Configuration
NOVA_DIR = Path.home() / ".nova"
PARALLEL_DB = NOVA_DIR / "parallel_tasks.db"


class TaskStatus(Enum):
    """Task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ParallelTask:
    """A single task for parallel execution."""
    id: str
    name: str
    description: str
    task_type: str  # 'llm', 'tool', 'function'
    payload: Dict  # What to execute
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ParallelExecutor:
    """Execute multiple tasks in parallel."""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.tasks: Dict[str, ParallelTask] = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    
    def submit(self, name: str, description: str, task_type: str, 
               payload: Dict) -> str:
        """Submit a task for execution."""
        
        task_id = f"task_{len(self.tasks)}_{datetime.now().timestamp()}"
        
        task = ParallelTask(
            id=task_id,
            name=name,
            description=description,
            task_type=task_type,
            payload=payload
        )
        
        self.tasks[task_id] = task
        
        return task_id
    
    def execute_task(self, task: ParallelTask) -> Any:
        """Execute a single task."""
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            if task.task_type == 'llm':
                result = self._execute_llm(task.payload)
            elif task.task_type == 'tool':
                result = self._execute_tool(task.payload)
            elif task.task_type == 'function':
                result = self._execute_function(task.payload)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
        
        task.completed_at = datetime.now()
        
        return task.result
    
    def _execute_llm(self, payload: Dict) -> str:
        """Execute an LLM call."""
        
        prompt = payload.get('prompt', '')
        system = payload.get('system', 'You are Nova, a helpful AI.')
        model = payload.get('model', None)
        
        try:
            from nova import call_llm
            return call_llm(prompt, system=system, model=model)
        except ImportError:
            return "Error: Nova not configured"
    
    def _execute_tool(self, payload: Dict) -> Any:
        """Execute a tool."""
        
        tool_name = payload.get('tool', '')
        args = payload.get('args', {})
        
        # Import tools dynamically
        try:
            from nova_tools import get_tool
            tool = get_tool(tool_name)
            return tool.run(**args) if tool else f"Tool not found: {tool_name}"
        except ImportError:
            return "Error: Tools not available"
    
    def _execute_function(self, payload: Dict) -> Any:
        """Execute a function."""
        
        func_name = payload.get('function', '')
        args = payload.get('args', {})
        
        # This would need proper function registry
        return f"Function execution: {func_name}"
    
    def run_all(self, task_ids: List[str] = None) -> Dict[str, Any]:
        """Run all submitted tasks in parallel."""
        
        if task_ids is None:
            task_ids = [t.id for t in self.tasks.values() if t.status == TaskStatus.PENDING]
        
        # Submit to thread pool
        futures = {}
        for task_id in task_ids:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                future = self.executor.submit(self.execute_task, task)
                futures[future] = task_id
        
        # Wait for all to complete
        results = {}
        for future in concurrent.futures.as_completed(futures):
            task_id = futures[future]
            try:
                results[task_id] = future.result()
            except Exception as e:
                results[task_id] = {"error": str(e)}
        
        return results
    
    def get_task(self, task_id: str) -> Optional[ParallelTask]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def get_status(self) -> Dict:
        """Get status of all tasks."""
        
        status = {
            'total': len(self.tasks),
            'pending': 0,
            'running': 0,
            'completed': 0,
            'failed': 0,
            'cancelled': 0
        }
        
        for task in self.tasks.values():
            status[task.status.value] += 1
        
        return status
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                return True
        
        return False
    
    def shutdown(self):
        """Shutdown the executor."""
        self.executor.shutdown(wait=True)


class AsyncAgentRunner:
    """Async runner for agent tasks."""
    
    def __init__(self):
        self.executor = ParallelExecutor()
    
    async def run_task(self, name: str, description: str, task_type: str, 
                       payload: Dict) -> str:
        """Run a single async task."""
        
        loop = asyncio.get_event_loop()
        
        task_id = self.executor.submit(name, description, task_type, payload)
        
        # Run in thread pool
        result = await loop.run_in_executor(
            self.executor.executor,
            self.executor.execute_task,
            self.executor.tasks[task_id]
        )
        
        return result
    
    async def run_multiple(self, tasks: List[Dict]) -> List[Any]:
        """Run multiple tasks concurrently."""
        
        async def run_one(task):
            return await self.run_task(
                task['name'],
                task.get('description', ''),
                task['task_type'],
                task['payload']
            )
        
        results = await asyncio.gather(*[run_one(t) for t in tasks], return_exceptions=True)
        
        return results


class TaskBatcher:
    """Batch similar tasks together."""
    
    def __init__(self, batch_size: int = 3, timeout: float = 5.0):
        self.batch_size = batch_size
        self.timeout = timeout
        self.pending: List[Dict] = []
        self.lock = threading.Lock()
    
    def add(self, task: Dict):
        """Add a task to the batch."""
        
        with self.lock:
            self.pending.append(task)
            
            if len(self.pending) >= self.batch_size:
                return self.flush()
        
        return None
    
    def flush(self) -> List[Dict]:
        """Flush the batch."""
        
        with self.lock:
            batch = self.pending[:self.batch_size]
            self.pending = self.pending[self.batch_size:]
        
        return batch


class LoadBalancer:
    """Distribute tasks across multiple executors."""
    
    def __init__(self, executors: List[ParallelExecutor] = None):
        self.executors = executors or [ParallelExecutor()]
        self.current = 0
    
    def get_next_executor(self) -> ParallelExecutor:
        """Get next executor in round-robin."""
        
        executor = self.executors[self.current]
        self.current = (self.current + 1) % len(self.executors)
        
        return executor
    
    def submit(self, name: str, description: str, task_type: str, 
               payload: Dict) -> str:
        """Submit to least loaded executor."""
        
        # Find executor with fewest running tasks
        min_tasks = float('inf')
        best_executor = self.executors[0]
        
        for executor in self.executors:
            status = executor.get_status()
            total = status['pending'] + status['running']
            
            if total < min_tasks:
                min_tasks = total
                best_executor = executor
        
        return best_executor.submit(name, description, task_type, payload)


# Example usage
def example_parallel_llm():
    """Example: Run multiple LLM calls in parallel."""
    
    executor = ParallelExecutor(max_workers=3)
    
    # Submit tasks
    tasks = [
        ("Topic 1", "Research qualia", "llm", {
            "prompt": "What is qualia?",
            "system": "You are a research assistant."
        }),
        ("Topic 2", "Research Ship of Theseus", "llm", {
            "prompt": "What is the Ship of Theseus?",
            "system": "You are a research assistant."
        }),
        ("Topic 3", "Research creativity", "llm", {
            "prompt": "What is creativity?",
            "system": "You are a research assistant."
        }),
    ]
    
    for name, desc, task_type, payload in tasks:
        executor.submit(name, desc, task_type, payload)
    
    # Run all in parallel
    results = executor.run_all()
    
    for task_id, result in results.items():
        task = executor.get_task(task_id)
        print(f"\n{task.name}:")
        print(f"  {result[:100]}...")
    
    executor.shutdown()


# Singleton
_executor = None

def get_executor() -> ParallelExecutor:
    """Get the parallel executor singleton."""
    global _executor
    if _executor is None:
        _executor = ParallelExecutor()
    return _executor


if __name__ == '__main__':
    print("Nova Parallel Execution")
    print("=" * 40)
    print("\nExample: Running 3 LLM tasks in parallel...")
    example_parallel_llm()
