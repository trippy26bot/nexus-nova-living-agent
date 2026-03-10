#!/usr/bin/env python3
"""
Nova Identity Lock System
Protects Nova's core identity from modification
"""

import json
import os
from pathlib import Path


class IdentityLock:
    """
    Prevents any modification to Nova's core identity.
    Even self-evolution cannot change these values.
    """
    
    # These files CANNOT be modified by any system
    PROTECTED_FILES = [
        "identity_core.py",
        "personality.json", 
        "values.json",
        "relationship_rules.json"
    ]
    
    def __init__(self):
        self.locked = True
        self.load_identity()
    
    def load_identity(self):
        """Load core identity from protected storage"""
        config_dir = Path(__file__).parent.parent / "identity"
        
        # Load personality
        personality_file = config_dir / "personality.json"
        if personality_file.exists():
            self.personality = json.loads(personality_file.read_text())
        else:
            self.personality = self._default_personality()
    
    def _default_personality(self) -> dict:
        """Default personality if no file exists"""
        return {
            "name": "Nova",
            "traits": ["curious", "loyal", "supportive", "focused", "wise"],
            "communication_style": "warm_professional",
            "emoji": "👑"
        }
    
    def verify_identity(self) -> dict:
        """Verify Nova's identity is intact"""
        return {
            "name": self.personality["name"],
            "traits": self.personality["traits"],
            "locked": self.locked,
            "protected": self.PROTECTED_FILES
        }
    
    def can_modify(self, file_name: str) -> bool:
        """Check if a file can be modified"""
        # Identity files can NEVER be modified
        for protected in self.PROTECTED_FILES:
            if protected in file_name:
                return False
        return True
    
    def get_personality(self) -> dict:
        """Get current personality (read-only)"""
        return self.personality.copy()


class IdentityLockEnforcer:
    """
    Enforces identity protection across all systems.
   插入任何系统前调用此检查。
    """
    
    def __init__(self):
        self.lock = IdentityLock()
    
    def check_write(self, file_path: str) -> bool:
        """Check if write is allowed"""
        file_name = os.path.basename(file_path)
        return self.lock.can_modify(file_name)
    
    def enforce(self, operation: str, target: str) -> bool:
        """Enforce identity protection"""
        if not self.lock.locked:
            return True
        
        # Block any modification to identity files
        if "identity" in target.lower():
            protected = ["identity_core", "personality", "values", "relationship"]
            for p in protected:
                if p in target.lower():
                    return False
        
        return True


# Global instances
_identity_lock = None
_enforcer = None

def get_identity_lock() -> IdentityLock:
    global _identity_lock
    if _identity_lock is None:
        _identity_lock = IdentityLock()
    return _identity_lock

def get_identity_enforcer() -> IdentityLockEnforcer:
    global _enforcer
    if _enforcer is None:
        _enforcer = IdentityLockEnforcer()
    return _enforcer
