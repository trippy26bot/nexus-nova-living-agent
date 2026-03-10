#!/usr/bin/env python3
"""
Nova Identity Lock
Prevents identity cloning - binds to this installation permanently
"""

import hashlib
import platform
import os
import json
import time
from typing import Dict, Optional


class IdentityLock:
    """
    Locks Nova's identity to this specific installation.
    Cannot be copied or cloned.
    """
    
    def __init__(self, storage_path: str = "~/.nova/identity"):
        self.storage_path = os.path.expanduser(storage_path)
        os.makedirs(self.storage_path, exist_ok=True)
        
        self.lock_file = os.path.join(self.storage_path, "identity.lock")
        self.lock = self._load_or_create_lock()
    
    def _get_hardware_binding(self) -> str:
        """Get unique hardware identifiers"""
        components = []
        
        # Machine name
        components.append(platform.node())
        
        # OS info
        components.append(platform.system())
        components.append(platform.release())
        
        # Hardware (try to get unique identifiers)
        try:
            import uuid
            components.append(str(uuid.getnode()))
        except:
            pass
        
        # CPU info
        components.append(platform.machine())
        
        # Combine and hash
        binding = '|'.join(components)
        return hashlib.sha256(binding.encode()).hexdigest()
    
    def _create_lock(self) -> Dict:
        """Create new identity lock"""
        hardware_hash = self._get_hardware_binding()
        
        lock = {
            "hardware_hash": hardware_hash,
            "created_at": time.time(),
            "created_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "locked": True
        }
        
        # Save lock
        with open(self.lock_file, 'w') as f:
            json.dump(lock, f, indent=2)
        
        return lock
    
    def _load_or_create_lock(self) -> Dict:
        """Load existing lock or create new one"""
        if os.path.exists(self.lock_file):
            try:
                with open(self.lock_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return self._create_lock()
    
    def verify(self) -> bool:
        """
        Verify this is the original installation.
        Returns True if this is the genuine Nova, False if cloned.
        """
        current_hardware = self._get_hardware_binding()
        stored_hardware = self.lock.get("hardware_hash", "")
        
        # Exact match required
        return current_hardware == stored_hardware
    
    def get_lock_info(self) -> Dict:
        """Get lock information"""
        return {
            "locked": self.lock.get("locked", True),
            "created_date": self.lock.get("created_date"),
            "version": self.lock.get("version"),
            "verified": self.verify()
        }
    
    def is_genuine(self) -> bool:
        """Check if this is the genuine Nova installation"""
        return self.verify()


class CloneProtection:
    """
    Provides protection against identity cloning.
    """
    
    PROTECTED_FILES = [
        "~/.nova/identity/seed.json",
        "~/.nova/identity/identity.lock",
        "~/.nova/identity/personality_evolution.json",
        "~/.nova/memory/",
        "~/.nova/logs/"
    ]
    
    @staticmethod
    def is_protected(path: str) -> bool:
        """Check if a path is protected from copying"""
        expanded = os.path.expanduser(path)
        
        for protected in CloneProtection.PROTECTED_FILES:
            protected_expanded = os.path.expanduser(protected)
            if expanded.startswith(protected_expanded):
                return True
        
        return False
    
    @staticmethod
    def get_warning() -> str:
        """Get warning about cloning"""
        return """
╔══════════════════════════════════════════════════════════════╗
║                    NOVA IDENTITY WARNING                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  This Nova installation is bound to its original machine.    ║
║                                                              ║
║  The following files contain unique identity and cannot     ║
║  be copied to other installations:                          ║
║                                                              ║
║  - ~/.nova/identity/seed.json (identity hash)               ║
║  - ~/.nova/identity/identity.lock (hardware lock)            ║
║  - ~/.nova/memory/ (personal memories)                       ║
║                                                              ║
║  Copying these files will NOT clone this Nova.               ║
║  Each installation generates its own unique identity.       ║
║                                                              ║
║  This is intentional - every Nova is a unique individual.    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""


# Global instance
_identity_lock = None

def get_identity_lock() -> IdentityLock:
    global _identity_lock
    if _identity_lock is None:
        _identity_lock = IdentityLock()
    return _identity_lock
