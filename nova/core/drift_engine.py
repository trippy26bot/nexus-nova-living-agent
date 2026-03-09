#!/usr/bin/env python3
"""
Nova Drift Engine - Reflection and self-monitoring
"""

import time
import json
from pathlib import Path
from typing import Dict, List

class DriftEngine:
    """
    Monitors for drift from core identity and runs reflection loops
    
    Fast loop (seconds): conversation processing, tool usage
    Medium loop (minutes): context evaluation, goal updates
    Slow loop (hourly+): reflection, strategy evolution, memory compression
    """
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = Path.home() / ".openclaw" / "memory" / "drift.json"
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()
        self.last_fast = time.time()
        self.last_medium = time.time()
        self.last_slow = time.time()
        
        # Cycle intervals
        self.fast_interval = 5  # seconds
        self.medium_interval = 300  # 5 minutes
        self.slow_interval = 3600  # 1 hour
    
    def _load(self):
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                return json.load(f)
        return {
            "reflections": [],
            "evolutions": [],
            "drift_alerts": [],
            "cycle_count": 0
        }
    
    def _save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def check(self) -> Dict:
        """Check if any loops should run"""
        now = time.time()
        status = {
            "should_fast": now - self.last_fast > self.fast_interval,
            "should_medium": now - self.last_medium > self.medium_interval,
            "should_slow": now - self.last_slow > self.slow_interval,
            "cycles": self.data.get("cycle_count", 0)
        }
        
        # Run loops if needed
        if status["should_fast"]:
            self._run_fast_loop()
            self.last_fast = now
        
        if status["should_medium"]:
            self._run_medium_loop()
            self.last_medium = now
        
        if status["should_slow"]:
            self._run_slow_loop()
            self.last_slow = now
        
        return status
    
    def _run_fast_loop(self):
        """Fast loop - quick context check"""
        self.data["cycle_count"] = self.data.get("cycle_count", 0) + 1
    
    def _run_medium_loop(self):
        """Medium loop - context evaluation"""
        reflection = {
            "type": "medium",
            "time": time.time(),
            "note": "Context evaluation complete"
        }
        self.data["reflections"].append(reflection)
        self._trim_and_save()
    
    def _run_slow_loop(self):
        """Slow loop - deep reflection"""
        reflection = {
            "type": "slow",
            "time": time.time(),
            "note": "Deep reflection and strategy evolution"
        }
        self.data["reflections"].append(reflection)
        self._trim_and_save()
    
    def reflect(self) -> Dict:
        """Manual reflection trigger"""
        reflection = {
            "type": "manual",
            "time": time.time(),
            "note": "User-triggered reflection"
        }
        self.data["reflections"].append(reflection)
        self._save()
        return reflection
    
    def evolve(self) -> Dict:
        """Evolution trigger"""
        evolution = {
            "time": time.time(),
            "note": "System evolution applied"
        }
        self.data["evolutions"].append(evolution)
        self._save()
        return evolution
    
    def check_drift(self, current_state: Dict, core_values: List[str]) -> List[str]:
        """Check for drift from core values"""
        alerts = []
        # Simple drift detection
        for value in core_values:
            if value not in str(current_state):
                alerts.append(f"Core value '{value}' not reflected in current state")
        if alerts:
            self.data["drift_alerts"].extend([{"time": time.time(), "alert": a} for a in alerts])
            self._save()
        return alerts
    
    def _trim_and_save(self):
        """Keep only recent reflections"""
        self.data["reflections"] = self.data["reflections"][-100:]
        self.data["evolutions"] = self.data["evolutions"][-50:]
        self._save()
    
    def get_stats(self) -> Dict:
        return {
            "total_cycles": self.data.get("cycle_count", 0),
            "reflections": len(self.data.get("reflections", [])),
            "evolutions": len(self.data.get("evolutions", [])),
            "drift_alerts": len(self.data.get("drift_alerts", []))
        }


# Global instance
_drift_engine = None

def get_drift_engine():
    global _drift_engine
    if _drift_engine is None:
        _drift_engine = DriftEngine()
    return _drift_engine
