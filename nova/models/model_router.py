#!/usr/bin/env python3
"""
Nova Model Router
Routes tasks to the best model
"""

from typing import Dict, List, Any, Optional

class ModelRouter:
    """
    Routes tasks to different models based on the task type.
    Uses the right brain for the job.
    """
    
    def __init__(self):
        self.models = {
            "analysis": "default",      # General analysis
            "coding": "default",       # Code generation
            "research": "default",      # Research tasks
            "creative": "default",      # Creative tasks
            "planning": "default",      # Strategic planning
            "conversation": "default"   # Chat
        }
        
        # Routing rules
        self.rules = {
            "code": "coding",
            "program": "coding",
            "script": "coding",
            "analyze": "analysis",
            "evaluate": "analysis",
            "assess": "analysis",
            "research": "research",
            "investigate": "research",
            "explore": "research",
            "create": "creative",
            "write": "creative",
            "design": "creative",
            "plan": "planning",
            "strategy": "planning",
            "organize": "planning",
        }
        
        # Usage tracking
        self.usage = {k: 0 for k in self.models.keys()}
    
    def route(self, task: str) -> str:
        """Route a task to the appropriate model"""
        task_lower = task.lower()
        
        # Check rules
        for keyword, model_type in self.rules.items():
            if keyword in task_lower:
                self.usage[model_type] += 1
                return model_type
        
        # Default
        self.usage["analysis"] += 1
        return "analysis"
    
    def get_model(self, task: str) -> str:
        """Get the model for a task"""
        model_type = self.route(task)
        return self.models.get(model_type, "default")
    
    def add_rule(self, keyword: str, model_type: str):
        """Add a routing rule"""
        self.rules[keyword.lower()] = model_type
    
    def set_model(self, model_type: str, model_name: str):
        """Set which model handles a type"""
        self.models[model_type] = model_name
    
    def get_statistics(self) -> Dict:
        """Get routing statistics"""
        return {
            "models": self.models,
            "usage": self.usage,
            "total_routes": sum(self.usage.values())
        }


# Global instance
_model_router = None

def get_model_router() -> ModelRouter:
    global _model_router
    if _model_router is None:
        _model_router = ModelRouter()
    return _model_router
