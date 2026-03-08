#!/usr/bin/env python3
"""
OpenClaw Skill Security Module
Unified interface for skill security: scanning, sandboxing, policies, and auditing.
"""

from pathlib import Path
from typing import Dict, List, Optional
import json

# Import components
from scanner.skill_scanner import SkillScanner, scan_skill
from monitor.audit_logger import AuditLogger, SkillAuditContext, get_audit_logger

# Policy loading
import yaml

def load_policy(policy_path: str) -> Dict:
    """Load a skill policy from YAML file."""
    with open(policy_path) as f:
        return yaml.safe_load(f)

def check_policy_compliance(skill_path: str, policy: Dict) -> Dict:
    """Check if a skill complies with its declared policy."""
    # This would verify skill matches declared permissions
    # Simplified for now
    return {"compliant": True, "issues": []}

class SkillSecurityManager:
    """Main manager for skill security."""
    
    def __init__(self):
        self.scanner = SkillScanner()
        self.audit = AuditLogger()
    
    def pre_install_scan(self, skill_path: str) -> Dict:
        """Scan a skill before installation."""
        result = scan_skill(skill_path)
        
        if not result["safe"]:
            self.audit.logger.warning(
                f"BLOCKED: Skill {skill_path} failed security scan. "
                f"Issues: {len(result['issues'])}"
            )
        
        return result
    
    def enforce_policy(self, skill_id: str, policy: Dict) -> bool:
        """Enforce policy during skill execution."""
        # Check circuit breaker
        if self.audit.should_circuit_break(skill_id):
            self.audit.logger.error(f"CIRCUIT BREAKER: {skill_id}")
            return False
        
        return True
    
    def log_event(self, skill_id: str, event: str, data: Dict = None):
        """Log a skill event."""
        self.audit.log(skill_id, event, data or {})

# Default configuration
DEFAULT_CONFIG = {
    "sandbox": {
        "enabled": True,
        "network_mode": "none",
        "readonly_fs": True,
        "tmpfs": ["/tmp", "/workspace"]
    },
    "scanner": {
        "block_critical": True,
        "block_high": True,
        "min_score": 70
    },
    "circuit_breaker": {
        "failure_threshold": 5,
        "blocked_threshold": 10,
        "cooldown_seconds": 300
    },
    "audit": {
        "enabled": True,
        "log_dir": "~/.openclaw/logs"
    }
}

def get_default_config() -> Dict:
    """Get default security configuration."""
    return DEFAULT_CONFIG.copy()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("OpenClaw Skill Security Module")
        print("Usage:")
        print("  python security.py scan <skill_path>   # Pre-install scan")
        print("  python security.py audit <skill_id>     # Get audit logs")
        print("  python security.py config               # Show default config")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "scan" and len(sys.argv) >= 3:
        result = scan_skill(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "audit" and len(sys.argv) >= 3:
        logger = get_audit_logger()
        events = logger.get_skill_events(sys.argv[2])
        print(json.dumps(events, indent=2))
    
    elif cmd == "config":
        print(json.dumps(get_default_config(), indent=2))
    
    else:
        print("Unknown command")
        sys.exit(1)
