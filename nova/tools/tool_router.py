#!/usr/bin/env python3
"""
Tool Router - Manages and routes tool executions
"""

import json
from pathlib import Path
from typing import Callable, Any

class ToolRouter:
    """Routes tasks to appropriate tools"""
    
    def __init__(self, storage_path=None):
        if storage_path is None:
            storage_path = Path.home() / ".openclaw" / "memory" / "tools.json"
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.tools = self._load_tools()
        self.execution_log = []
    
    def _load_tools(self):
        """Load tool registry"""
        # Default tools
        defaults = {
            "search_web": {
                "description": "Search the web for information",
                "category": "information",
                "reliability": 0.9
            },
            "read_file": {
                "description": "Read a file from disk",
                "category": "system",
                "reliability": 0.95
            },
            "write_file": {
                "description": "Write content to a file",
                "category": "system",
                "reliability": 0.95
            },
            "run_code": {
                "description": "Execute Python code safely",
                "category": "execution",
                "reliability": 0.85
            },
            "send_message": {
                "description": "Send a message to a channel",
                "category": "communication",
                "reliability": 0.9
            },
            "calculate": {
                "description": "Perform calculations",
                "category": "computation",
                "reliability": 0.99
            }
        }
        
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                saved = json.load(f)
                return {**defaults, **saved}
        return defaults
    
    def _save_tools(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.tools, f, indent=2)
    
    def register(self, name: str, description: str, category: str = "custom", reliability: float = 0.8):
        """Register a new tool"""
        self.tools[name] = {
            "description": description,
            "category": category,
            "reliability": reliability,
            "registered": True
        }
        self._save_tools()
        return name
    
    def find_tool(self, intent: str):
        """Find best tool for an intent"""
        intent_lower = intent.lower()
        scores = []
        
        for name, tool in self.tools.items():
            score = 0
            # Check description
            if intent_lower in tool.get("description", "").lower():
                score += 5
            # Check category
            if intent_lower in tool.get("category", "").lower():
                score += 3
            # Check name
            if intent_lower in name.lower():
                score += 7
            
            if score > 0:
                scores.append((name, tool, score))
        
        if scores:
            scores.sort(key=lambda x: x[2], reverse=True)
            return scores[0][0], scores[0][1]
        
        return None, None
    
    def route(self, intent: str):
        """Route an intent to the best tool"""
        tool_name, tool_info = self.find_tool(intent)
        
        # Log the routing
        self.execution_log.append({
            "intent": intent,
            "tool": tool_name,
            "timestamp": datetime.now().isoformat()
        })
        
        return tool_name, tool_info
    
    def list_tools(self, category: str = None):
        """List all tools, optionally filtered by category"""
        if category:
            return {k: v for k, v in self.tools.items() if v.get("category") == category}
        return self.tools
    
    def get_log(self, n=10):
        """Get recent execution log"""
        return self.execution_log[-n:]


# Global instance
_router = ToolRouter()

def get_router():
    return _router
