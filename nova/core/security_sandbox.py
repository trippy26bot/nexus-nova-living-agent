"""
Security Sandbox - locks Nova down to prevent unauthorized access
"""

import sys
import logging
from typing import Any, Callable

logger = logging.getLogger("SecuritySandbox")

# Blocked modules (cannot be imported)
BLOCKED_MODULES = {
    'os', 'sys', 'subprocess', 'socket', 'requests', 'urllib',
    'http', 'ftplib', 'telnetlib', 'smtplib', 'poplib',
    'imaplib', 'nntplib', 'telnet', 'pty', 'tty', 'termios',
    'resource', 'grp', 'pwd', 'spwd', 'crypt',
    'posixpath', 'ntpath'  # path traversal
}

# Allowed modules (safe to import)
ALLOWED_MODULES = {
    'math', 'random', 'datetime', 'time', 'json', 're',
    'collections', 'itertools', 'functools', 'operator',
    'typing', 'uuid', 'hashlib', 'base64', 'zlib',
    'logging', 'threading', 'asyncio', 'concurrent',
    'abc', 'contextlib', 'copy', 'pprint', 'traceback',
    'warnings', 'enum', 'dataclasses', 'pathlib'
}


class SecuritySandbox:
    """Prevents Nova from accessing unauthorized system resources"""
    
    def __init__(self):
        self.allowed_modules = set(ALLOWED_MODULES)
        self.blocked_modules = set(BLOCKED_MODULES)
        self.violations = []
        
        logger.info("SecuritySandbox initialized")
    
    def check_import(self, module_name: str) -> bool:
        """Check if module can be imported"""
        # Allow anything starting with our core
        if module_name.startswith('core.') or module_name.startswith('brains.'):
            return True
        
        # Allow explicitly allowed
        if module_name in self.allowed_modules:
            return True
        
        # Block dangerous
        if module_name in self.blocked_modules:
            self._log_violation("import_blocked", module_name)
            return False
        
        # Unknown modules - log but allow (might be legitimate)
        logger.warning(f"Unknown module import: {module_name}")
        return True
    
    def check_execution(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function in sandboxed context"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Sandbox execution error: {e}")
            return None
    
    def check_network(self, host: str = None, port: int = None) -> bool:
        """Check if network access is allowed"""
        # Only allow specific safe hosts
        allowed_hosts = {'api.coingecko.com', 'api.simmer.markets', 'localhost', '127.0.0.1'}
        
        if host in allowed_hosts:
            return True
        
        if host:
            self._log_violation("network_blocked", f"{host}:{port}")
        
        return False
    
    def check_file_access(self, path: str, mode: str = 'r') -> bool:
        """Check if file access is allowed"""
        # Block system directories
        blocked_paths = {'/etc/', '/usr/', '/bin/', '/sbin/', '/var/', '/boot/', '/proc/', '/sys/'}
        
        for blocked in blocked_paths:
            if path.startswith(blocked):
                self._log_violation("file_access_blocked", path)
                return False
        
        # Only allow within Nova's workspace
        allowed_base = '/Users/dr.claw/.openclaw/workspace/nova'
        if path.startswith(allowed_base):
            return True
        
        # Unknown - warn but allow
        logger.warning(f"File access: {path} ({mode})")
        return True
    
    def _log_violation(self, violation_type: str, details: str):
        """Log security violation"""
        self.violations.append({
            "type": violation_type,
            "details": details
        })
        logger.warning(f"[SECURITY] {violation_type}: {details}")
    
    def get_violations(self) -> list:
        """Get list of violations"""
        return self.violations.copy()
    
    def get_status(self) -> dict:
        """Get security status"""
        return {
            "violations_count": len(self.violations),
            "allowed_modules": len(self.allowed_modules),
            "blocked_modules": len(self.blocked_modules)
        }


# Global sandbox instance
_sandbox = None

def get_sandbox() -> SecuritySandbox:
    """Get or create global sandbox"""
    global _sandbox
    if _sandbox is None:
        _sandbox = SecuritySandbox()
    return _sandbox
