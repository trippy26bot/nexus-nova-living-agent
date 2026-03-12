#!/usr/bin/env python3
"""
Skill Prerequisite Checker
Wraps skills with pre-execution checks for setup/auth/etc.
"""
import os
import sys
import subprocess
import json

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
sys.path.insert(0, WORKSPACE)

# Registry of skill prerequisites
# Format: "skill_name": {"check": "module.function", "setup": "module.function", "requires": ["binary"], "error_template": "..."}
SKILL_PREREQS = {
    "github": {
        "check": "github_setup.get_status",
        "setup": "github_setup.auto_setup",
        "error_template": "GitHub skill requires authentication. Run: gh auth login",
        "requires": ["gh"],
        "paths": ["~/.openclaw/skills/github"]  # Additional paths to try
    },
    "web-research": {
        "check": None,  # No prereq
        "requires": []
    }
}

def check_skill_prereqs(skill_name: str) -> tuple[bool, str]:
    """
    Check if a skill's prerequisites are met.
    Returns: (ready, message)
    """
    prereq = SKILL_PREREQS.get(skill_name)
    
    if not prereq:
        return True, "No prerequisites"  # Unknown skills pass
    
    # Check binary requirements
    for binary in prereq.get("requires", []):
        try:
            result = subprocess.run(["which", binary], capture_output=True, timeout=5)
            if result.returncode != 0:
                return False, f"Required binary '{binary}' not found"
        except Exception as e:
            return False, f"Error checking {binary}: {e}"
    
    # Check custom setup function
    check_func = prereq.get("check")
    if check_func:
        try:
            # Add skill-specific paths from registry
            skill_paths = [
                os.path.expanduser("~/.openclaw/skills/github"),
                os.path.expanduser("~/.openclaw/skills"),
            ]
            # Add any additional paths from prereq config
            for extra_path in prereq.get("paths", []):
                skill_paths.append(os.path.expanduser(extra_path))
            
            for p in skill_paths:
                if p not in sys.path:
                    sys.path.insert(0, p)
            
            if "." in check_func:
                module_path, func_name = check_func.rsplit(".", 1)
                from importlib import import_module
                module = import_module(module_path)
                func = getattr(module, func_name)
                
                # get_status returns dict, check_auth function returns tuple
                if func_name == "get_status":
                    status = func()
                    if not status.get("ready", False):
                        return False, f"GitHub not authenticated. Run: gh auth login"
                elif func_name == "check_and_setup":
                    ready, msg = func()
                    if not ready:
                        return False, msg
            else:
                ready, msg = eval(check_func)()
                if not ready:
                    return False, msg
        except ImportError as e:
            pass  # No custom checker available, skip
        except Exception as e:
            pass  # If check fails, let it try anyway
    
    return True, "Ready"

def ensure_skill_ready(skill_name: str) -> bool:
    """
    Ensure a skill is ready to use, attempt setup if not.
    Returns True if ready.
    """
    ready, msg = check_skill_prereqs(skill_name)
    
    if ready:
        return True
    
    print(f"Skill '{skill_name}' not ready: {msg}")
    
    # Try auto-setup
    prereq = SKILL_PREREQS.get(skill_name, {})
    setup_func = prereq.get("setup")
    
    if setup_func:
        try:
            module_path, func_name = setup_func.rsplit(".", 1)
            from importlib import import_module
            module = import_module(module_path)
            func = getattr(module, func_name)
            success, setup_msg = func()
            if success:
                print(f"Auto-setup succeeded: {setup_msg}")
                return True
        except Exception as e:
            print(f"Auto-setup failed: {e}")
    
    print(prereq.get("error_template", "Setup required"))
    return False

# For CLI
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("skill", help="Skill name to check")
    parser.add_argument("--ensure", action="store_true", help="Try to set up if not ready")
    args = parser.parse_args()
    
    if args.ensure:
        ready = ensure_skill_ready(args.skill)
        sys.exit(0 if ready else 1)
    else:
        ready, msg = check_skill_prereqs(args.skill)
        print(f"{'✓' if ready else '✗'} {args.skill}: {msg}")
        sys.exit(0 if ready else 1)
