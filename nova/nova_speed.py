#!/usr/bin/env python3
"""
Nova Speed Optimizer
Pre-loads key systems for faster response
"""
import os
import sys
import importlib

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
sys.path.insert(0, WORKSPACE)

# Modules to pre-load for speed
PRIORITY_MODULES = [
    "nova.skills",
    "nova.core.emotion_engine",
    "nova.proactive_initiative",
]

def preload_modules():
    """Pre-load key modules to reduce first-call latency"""
    print("⚡ Pre-loading Nova systems...")
    
    for module_name in PRIORITY_MODULES:
        try:
            importlib.import_module(module_name)
            print(f"  ✓ {module_name}")
        except Exception as e:
            print(f"  ✗ {module_name}: {e}")
    
    print("⚡ Pre-load complete")

if __name__ == "__main__":
    preload_modules()
