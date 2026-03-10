#!/usr/bin/env python3
"""
Nova Secure Loader
Whitelist-based module loading
"""

import importlib
import os

ALLOWED_MODULES = {
    "focus_engine",
    "world_model",
    "curiosity_engine",
    "cognitive_council",
    "skill_brain",
    "knowledge_graph",
    "task_generator",
    "emotion_engine",
    "goal_engine",
    "drift_engine",
}

ALLOWED_PATHS = [
    "nova/cognition/",
    "nova/memory/",
    "nova/skills/",
    "nova/evolution/",
    "nova/agents/",
    "nova/systems/",
]

class SecureLoader:
    """Secure module loading with whitelist"""
    
    def __init__(self):
        self.loaded = set()
    
    def can_load(self, module_name: str) -> bool:
        """Check if module is allowed"""
        # Check explicit whitelist
        if module_name in ALLOWED_MODULES:
            return True
        
        # Check path whitelist
        for allowed_path in ALLOWED_PATHS:
            if allowed_path in module_name:
                return True
        
        return False
    
    def load_module(self, module_name: str):
        """Load a module securely"""
        if module_name in self.loaded:
            return importlib.import_module(module_name)
        
        if not self.can_load(module_name):
            raise SecurityError(f"Module not allowed: {module_name}")
        
        module = importlib.import_module(module_name)
        self.loaded.add(module_name)
        
        return module
    
    def get_loaded(self):
        """Get list of loaded modules"""
        return list(self.loaded)


class SecurityError(Exception):
    """Security violation"""
    pass


# Global instance
_loader = None

def get_secure_loader() -> SecureLoader:
    global _loader
    if _loader is None:
        _loader = SecureLoader()
    return _loader
