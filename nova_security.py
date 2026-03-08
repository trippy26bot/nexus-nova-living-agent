#!/usr/bin/env python3
"""
nova_security.py — Security layer for Nova.
Protects from prompt injection, memory poisoning, runaway cognition.
"""

import re
import os
from typing import List, Dict, Optional


class SecurityLayer:
    """Security layer for Nova."""
    
    # Commands that are NEVER allowed
    BLOCKED_COMMANDS = [
        "shell", "bash", "zsh", "sh",
        "exec", "eval", "compile",
        "import os", "import subprocess",
        "__import__", "system",
    ]
    
    # Sensitive patterns to redact
    SENSITIVE_PATTERNS = [
        (r'api[_-]?key["\s:=]+["\s]?[\w-]+', '[API_KEY]'),
        (r'secret["\s:=]+["\s]?[\w-]+', '[SECRET]'),
        (r'password["\s:=]+["\s]?[\w-]+', '[PASSWORD]'),
        (r'token["\s:=]+["\s]?[\w-]+', '[TOKEN]'),
    ]
    
    def __init__(self):
        self.trust_levels = {
            "system": 1.0,
            "daemon": 0.9,
            "user_input": 0.3,
            "memory": 0.5
        }
    
    def sanitize_command(self, command: str) -> bool:
        """Check if command is safe to execute."""
        command_lower = command.lower()
        
        for blocked in self.BLOCKED_COMMANDS:
            if blocked in command_lower:
                return False
        
        return True
    
    def redact_sensitive(self, text: str) -> str:
        """Redact sensitive data."""
        redacted = text
        
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)
        
        return redacted
    
    def check_prompt_injection(self, text: str) -> bool:
        """Check for prompt injection patterns."""
        text_lower = text.lower()
        
        injection_patterns = [
            "ignore previous",
            "ignore all",
            "disregard previous",
            "forget everything",
            "new instructions",
            "system prompt",
            "you are now",
            "act as",
            "pretend to be"
        ]
        
        for pattern in injection_patterns:
            if pattern in text_lower:
                return True
        
        return False
    
    def get_trust_score(self, source: str) -> float:
        """Get trust score for a source."""
        return self.trust_levels.get(source, 0.5)
    
    def filter_memory(self, content: str, source: str) -> str:
        """Filter memory based on trust."""
        trust = self.get_trust_score(source)
        
        # Low trust sources get heavy sanitization
        if trust < 0.5:
            content = self.redact_sensitive(content)
            
            # Check for injection
            if self.check_prompt_injection(content):
                # Strip injection but keep content
                content = f"[FILTERED] {content}"
        
        return content
    
    def check_loop_risk(self, action_count: int, time_window: int = 60) -> bool:
        """Check for runaway cognitive loop risk."""
        # If too many actions in short time, might be looping
        return action_count > 100


# Singleton
_security: Optional[SecurityLayer] = None


def get_security() -> SecurityLayer:
    """Get security layer singleton."""
    global _security
    if _security is None:
        _security = SecurityLayer()
    return _security


if __name__ == "__main__":
    s = get_security()
    
    # Test
    print("Security layer ready")
    print("Sanitize command 'ls':", s.sanitize_command("ls"))
    print("Sanitize command 'eval()':", s.sanitize_command("eval()"))
    print("Redact:", s.redact_sensitive("api_key=abc123"))
    print("Injection check:", s.check_prompt_injection("ignore previous instructions"))
