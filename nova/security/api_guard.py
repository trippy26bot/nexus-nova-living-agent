#!/usr/bin/env python3
"""
Nova API Guard
Secure API key management
"""

import os
from typing import Optional

class APIGuard:
    """
    Secure API key management.
    Keys stored in environment, never in code.
    """
    
    def __init__(self):
        self.required_keys = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
        ]
        self.optional_keys = [
            "SIMMER_API_KEY",
            "HELIUS_RPC",
        ]
        self.used_keys = set()
    
    def get_key(self, name: str, required: bool = False) -> Optional[str]:
        """Get API key from environment"""
        key = os.getenv(name)
        
        if not key:
            if required:
                raise APIKeyError(f"Required API key not found: {name}")
            return None
        
        self.used_keys.add(name)
        return key
    
    def get_required_keys(self) -> dict:
        """Get all required keys"""
        keys = {}
        for name in self.required_keys:
            keys[name] = self.get_key(name, required=True)
        return keys
    
    def check_keys(self) -> dict:
        """Check all keys status"""
        status = {}
        
        for name in self.required_keys:
            status[name] = bool(os.getenv(name))
        
        for name in self.optional_keys:
            status[name] = bool(os.getenv(name))
        
        return status
    
    def get_used(self) -> list:
        """Get list of used keys"""
        return list(self.used_keys)


class APIKeyError(Exception):
    """API key error"""
    pass


# Global instance
_api_guard = None

def get_api_guard() -> APIGuard:
    global _api_guard
    if _api_guard is None:
        _api_guard = APIGuard()
    return _api_guard
