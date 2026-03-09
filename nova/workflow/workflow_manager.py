#!/usr/bin/env python3
"""
Workflow Manager - Tracks active work and task queues
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

class WorkflowManager:
    """Manages active workflows and task queues"""
    
    def __init__(self, storage_path=None):
        if storage_path is None:
            storage_path = Path.home() / ".openclaw" / "memory" / "workflow.json"
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()
    
    def _load(self):
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                return json.load(f)
        return {
            "active_tasks": [],
            "completed_tasks": [],
            "queue": []
        }
    
    def _save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_task(self, task: str, priority: int = 5):
        """Add a task to the queue"""
        task_obj = {
            "id": str(uuid.uuid4())[:8],
            "task": task,
            "priority": priority,
            "status": "queued",
            "created": datetime.now().isoformat()
        }
        self.data["queue"].append(task_obj)
        self.data["queue"].sort(key=lambda x: x["priority"], reverse=True)
        self._save()
        return task_obj
    
    def start_task(self, task_id: str = None):
        """Start a task (either specific or next in queue)"""
        if task_id:
            # Find specific task
            for task in self.data["queue"]:
                if task["id"] == task_id:
                    task["status"] = "active"
                    self.data["active_tasks"].append(task)
                    self.data["queue"].remove(task)
                    self._save()
                    return task
        else:
            # Get next task from queue
            if self.data["queue"]:
                task = self.data["queue"].pop(0)
                task["status"] = "active"
                self.data["active_tasks"].append(task)
                self._save()
                return task
        return None
    
    def complete_task(self, task_id: str):
        """Mark a task as completed"""
        for task in self.data["active_tasks"]:
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed"] = datetime.now().isoformat()
                self.data["active_tasks"].remove(task)
                self.data["completed_tasks"].append(task)
                self._save()
                return task
        return None
    
    def get_active(self):
        """Get all active tasks"""
        return self.data["active_tasks"]
    
    def get_queue(self):
        """Get queued tasks"""
        return self.data["queue"]
    
    def get_summary(self):
        """Get workflow summary"""
        return {
            "active": len(self.data["active_tasks"]),
            "queued": len(self.data["queue"]),
            "completed": len(self.data["completed_tasks"])
        }
    
    def clear_completed(self):
        """Clear completed tasks"""
        self.data["completed_tasks"] = []
        self._save()


# Global instance
_workflow = WorkflowManager()

def get_workflow():
    return _workflow
