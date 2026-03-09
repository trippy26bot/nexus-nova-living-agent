#!/usr/bin/env python3
"""
System Validator - Validates all Nova modules can be imported
"""

import importlib
import sys
from pathlib import Path

MODULES = [
    "nova.core.governor",
    "nova.core.attention_router", 
    "nova.core.self_reflection",
    "nova.core.thought_stream",
    "nova.emotional_engine",
    "nova.cognitive_bus",
    "nova.priority_scheduler",
    "nova.output_filter",
    "nova.response_synthesizer",
    "nova.fast_response",
]

def validate_modules():
    """Validate all core modules can be imported"""
    results = {}
    
    for mod_name in MODULES:
        try:
            mod = importlib.import_module(mod_name)
            results[mod_name] = {"status": "OK", "error": None}
        except Exception as e:
            results[mod_name] = {"status": "ERROR", "error": str(e)}
    
    return results

def print_results(results):
    """Pretty print validation results"""
    print("=" * 50)
    print("NOVA MODULE VALIDATION")
    print("=" * 50)
    
    ok_count = sum(1 for r in results.values() if r["status"] == "OK")
    err_count = sum(1 for r in results.values() if r["status"] == "ERROR")
    
    for mod, result in results.items():
        status = "✅" if result["status"] == "OK" else "❌"
        print(f"{status} {mod}")
        if result["error"]:
            print(f"   Error: {result['error'][:80]}")
    
    print("-" * 50)
    print(f"Total: {len(results)} | ✅ OK: {ok_count} | ❌ Error: {err_count}")
    print("=" * 50)
    
    return ok_count == len(results)


if __name__ == "__main__":
    results = validate_modules()
    success = print_results(results)
    sys.exit(0 if success else 1)
