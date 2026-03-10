#!/usr/bin/env python3
"""
Nova Coordinator - Task distribution and aggregation
"""

from typing import Dict, List, Any, Optional, Callable
import time

class WorkerAgent:
    """A capability-focused worker agent"""
    
    def __init__(self, agent_id: str, role: str, tools: List[str] = None):
        self.id = agent_id
        self.role = role
        self.tools = tools or []
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_time = 0
    
    def execute(self, task: str, tool_func: Callable = None) -> Dict:
        """Execute a task"""
        start = time.time()
        
        try:
            # Execute task (or use provided function)
            if tool_func:
                result = tool_func(task)
            else:
                # Default processing
                result = f"{self.role} processed: {task}"
            
            self.tasks_completed += 1
            duration = time.time() - start
            self.total_time += duration
            
            return {
                "agent": self.id,
                "role": self.role,
                "task": task,
                "result": result,
                "success": True,
                "duration": duration
            }
            
        except Exception as e:
            self.tasks_failed += 1
            return {
                "agent": self.id,
                "role": self.role,
                "task": task,
                "error": str(e),
                "success": False
            }
    
    def get_stats(self) -> Dict:
        """Get agent statistics"""
        total = self.tasks_completed + self.tasks_failed
        success_rate = self.tasks_completed / total if total > 0 else 0
        avg_time = self.total_time / self.tasks_completed if self.tasks_completed > 0 else 0
        
        return {
            "id": self.id,
            "role": self.role,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "success_rate": success_rate,
            "avg_time": avg_time
        }


class NovaCoordinator:
    """
    Nova coordinates worker agents
    Distributes tasks, aggregates results
    """
    
    def __init__(self):
        self.agents: List[WorkerAgent] = []
        self.task_history = []
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register default worker agents"""
        roles = [
            ("researcher", ["search", "read"]),
            ("analyst", ["analyze", "calculate"]),
            ("builder", ["create", "assemble"]),
            ("explorer", ["discover", "map"]),
            ("planner", ["organize", "schedule"]),
        ]
        
        for i, (role, tools) in enumerate(roles):
            agent = WorkerAgent(f"worker_{i:03d}", role, tools)
            self.agents.append(agent)
    
    def add_agent(self, agent: WorkerAgent):
        """Add a worker agent"""
        self.agents.append(agent)
    
    def get_agent(self, role: str = None) -> Optional[WorkerAgent]:
        """Get an available agent"""
        available = [a for a in self.agents if a.tasks_failed < 3]
        
        if not available:
            return self.agents[0] if self.agents else None
        
        if role:
            for a in available:
                if a.role == role:
                    return a
        
        return available[0]
    
    def distribute_task(self, task: str, role: str = None) -> Dict:
        """Distribute task to an agent"""
        agent = self.get_agent(role)
        
        if not agent:
            return {"error": "No agents available"}
        
        result = agent.execute(task)
        
        self.task_history.append({
            "task": task,
            "agent": agent.id,
            "result": result,
            "time": time.time()
        })
        
        return result
    
    def aggregate_results(self, results: List[Dict]) -> Dict:
        """Aggregate multiple results"""
        successful = [r for r in results if r.get("success", False)]
        failed = [r for r in results if not r.get("success", True)]
        
        # Simple voting or ranking
        if successful:
            # Return highest confidence
            best = max(successful, key=lambda r: r.get("duration", 1))
            return {
                "best_result": best["result"],
                "confidence": len(successful) / len(results) if results else 0,
                "success_count": len(successful),
                "failure_count": len(failed)
            }
        
        return {
            "error": "All tasks failed",
            "failure_count": len(failed)
        }
    
    def get_statistics(self) -> Dict:
        """Get coordinator statistics"""
        total_completed = sum(a.tasks_completed for a in self.agents)
        total_failed = sum(a.tasks_failed for a in self.agents)
        
        return {
            "total_agents": len(self.agents),
            "total_completed": total_completed,
            "total_failed": total_failed,
            "success_rate": total_completed / (total_completed + total_failed) if (total_completed + total_failed) > 0 else 0,
            "agents": [a.get_stats() for a in self.agents]
        }


class ToolManager:
    """Manages tools for agents"""
    
    def __init__(self):
        self.tools = {}
    
    def register(self, name: str, func: Callable):
        """Register a tool"""
        self.tools[name] = func
    
    def run(self, name: str, input_data: Any) -> Any:
        """Run a tool"""
        if name in self.tools:
            return self.tools[name](input_data)
        return {"error": f"Tool {name} not found"}
    
    def list_tools(self) -> List[str]:
        """List all tools"""
        return list(self.tools.keys())


class NovaMetrics:
    """Monitoring and metrics"""
    
    def __init__(self):
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.errors = []
        self.start_time = time.time()
    
    def log_task(self, success: bool):
        """Log task completion"""
        if success:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1
    
    def log_error(self, error: str):
        """Log an error"""
        self.errors.append({
            "error": error,
            "time": time.time()
        })
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        total = self.tasks_completed + self.tasks_failed
        uptime = time.time() - self.start_time
        
        return {
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "total_tasks": total,
            "success_rate": self.tasks_completed / total if total > 0 else 0,
            "uptime_seconds": uptime,
            "error_count": len(self.errors)
        }


# Global instances
_coordinator = None
_tool_manager = None
_metrics = None

def get_coordinator() -> NovaCoordinator:
    global _coordinator
    if _coordinator is None:
        _coordinator = NovaCoordinator()
    return _coordinator

def get_tool_manager() -> ToolManager:
    global _tool_manager
    if _tool_manager is None:
        _tool_manager = ToolManager()
    return _tool_manager

def get_nova_metrics() -> NovaMetrics:
    global _metrics
    if _metrics is None:
        _metrics = NovaMetrics()
    return _metrics
