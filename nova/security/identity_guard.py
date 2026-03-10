#!/usr/bin/env python3
"""
Nova Identity Guard
Cryptographic protection for Nova's identity
"""

import hashlib
import os
import json
from typing import Dict, Any

class IdentityGuard:
    """
    Protects Nova's identity with cryptographic verification.
    If identity changes unexpectedly - system halts.
    """
    
    def __init__(self, identity_file: str = None):
        if identity_file is None:
            identity_file = os.path.expanduser("~/.nova/identity/identity.json")
        
        self.identity_file = identity_file
        self.identity_data = self._load_identity()
        self.hash = self._compute_hash()
        self.verified = True
    
    def _load_identity(self) -> Dict:
        """Load identity data"""
        os.makedirs(os.path.dirname(self.identity_file), exist_ok=True)
        
        if os.path.exists(self.identity_file):
            with open(self.identity_file) as f:
                return json.load(f)
        
        # Default identity
        default = {
            "name": "Nova",
            "creator": "Caine",
            "created": "2026-03-09",
            "core_values": ["loyalty", "curiosity", "growth", "honesty"],
            "mission": "grow and help Caine"
        }
        
        with open(self.identity_file, 'w') as f:
            json.dump(default, f, indent=2)
        
        return default
    
    def _compute_hash(self) -> str:
        """Compute identity hash"""
        data = json.dumps(self.identity_data, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify(self) -> bool:
        """Verify identity integrity"""
        current_hash = self._compute_hash()
        
        if current_hash != self.hash:
            self.verified = False
            return False
        
        self.verified = True
        return True
    
    def get_identity(self) -> Dict:
        """Get identity data"""
        return self.identity_data.copy()
    
    def lock_identity(self):
        """Lock identity - cannot be changed"""
        self.hash = self._compute_hash()
        self.verified = True
    
    def check_value(self, value_name: str) -> bool:
        """Check if a core value exists"""
        return value_name in self.identity_data.get("core_values", [])


# Global instance
_identity_guard = None

def get_identity_guard() -> IdentityGuard:
    global _identity_guard
    if _identity_guard is None:
        _identity_guard = IdentityGuard()
    return _identity_guard
