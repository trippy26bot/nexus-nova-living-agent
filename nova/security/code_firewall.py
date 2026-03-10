#!/usr/bin/env python3
"""
Nova Code Firewall
Prevents modification of protected code
"""

import os

PROTECTED_FOLDERS = [
    "nova/core/",
    "nova/identity/",
    "nova/security/",
]

PROTECTED_FILES = [
    "identity_core.py",
    "nova_supercore.py",
]

class CodeFirewall:
    """
    Prevents dangerous modifications to Nova's core.
    """
    
    def __init__(self):
        self.violations = []
        self.blocked_count = 0
    
    def can_modify(self, path: str) -> bool:
        """Check if a path can be modified"""
        path = os.path.abspath(path)
        
        # Check protected folders
        for protected in PROTECTED_FOLDERS:
            if protected in path:
                self._log_violation(path, "protected_folder")
                return False
        
        # Check protected files
        filename = os.path.basename(path)
        if filename in PROTECTED_FILES:
            self._log_violation(path, "protected_file")
            return False
        
        return True
    
    def _log_violation(self, path: str, reason: str):
        """Log a security violation"""
        self.violations.append({
            "path": path,
            "reason": reason
        })
        self.blocked_count += 1
    
    def check_and_raise(self, path: str):
        """Check and raise exception if blocked"""
        if not self.can_modify(path):
            raise FirewallError(f"Modification blocked: {path}")
    
    def get_violations(self):
        """Get all violations"""
        return self.violations.copy()
    
    def get_stats(self):
        """Get firewall statistics"""
        return {
            "blocked_count": self.blocked_count,
            "violations": len(self.violations),
            "protected_folders": PROTECTED_FOLDERS,
            "protected_files": PROTECTED_FILES
        }


class FirewallError(Exception):
    """Firewall violation"""
    pass


# Global instance
_firewall = None

def get_code_firewall() -> CodeFirewall:
    global _firewall
    if _firewall is None:
        _firewall = CodeFirewall()
    return _firewall
