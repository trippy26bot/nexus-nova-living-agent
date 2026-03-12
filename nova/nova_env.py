#!/usr/bin/env python3
"""
Nova Environment Loader
Loads .env files for configuration
"""
import os
from pathlib import Path

def load_env():
    """
    Load .env file if it exists.
    Looks in workspace root and ~/.nova/
    """
    workspace = Path(__file__).parent.parent
    env_paths = [
        workspace / ".env",
        workspace / ".env.local",
        Path.home() / ".nova" / ".env"
    ]
    
    loaded = []
    
    for env_path in env_paths:
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        # Don't override existing env vars
                        if key not in os.environ:
                            os.environ[key] = value
                            loaded.append(key)
    
    return loaded

# Auto-load on import
loaded_vars = load_env()
if loaded_vars:
    print(f"Loaded env vars: {loaded_vars}")
