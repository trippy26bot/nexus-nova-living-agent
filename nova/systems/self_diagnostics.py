#!/usr/bin/env python3
"""
Nova Self-Diagnostics
Detects problems automatically
"""

from typing import Dict, List, Any
import time

class SelfDiagnostics:
    """
    Nova monitors herself for problems.
    """
    
    def __init__(self):
        self.issues = []
        self.checks_run = 0
        self.last_check = None
        
        # Thresholds
        self.memory_threshold = 0.9
        self.error_threshold = 10
        self.slow_threshold = 5.0  # seconds
    
    def check_all(self, systems: Dict) -> Dict:
        """Run all diagnostics"""
        self.checks_run += 1
        self.last_check = time.time()
        
        results = {
            "timestamp": self.last_check,
            "checks": self.checks_run,
            "issues": [],
            "status": "healthy"
        }
        
        # Check memory
        memory_check = self._check_memory(systems.get("memory", {}))
        if memory_check:
            results["issues"].append(memory_check)
        
        # Check agents
        agent_check = self._check_agents(systems.get("agents", {}))
        if agent_check:
            results["issues"].append(agent_check)
        
        # Check emotions
        emotion_check = self._check_emotions(systems.get("emotions", {}))
        if emotion_check:
            results["issues"].append(emotion_check)
        
        # Check focus
        focus_check = self._check_focus(systems.get("focus", {}))
        if focus_check:
            results["issues"].append(focus_check)
        
        # Set overall status
        if len(results["issues"]) > 0:
            results["status"] = "warning"
        if len(results["issues"]) > 3:
            results["status"] = "critical"
        
        # Store issues
        self.issues.extend(results["issues"])
        
        return results
    
    def _check_memory(self, memory_data: Dict) -> Dict:
        """Check memory system"""
        # Check for memory issues
        if memory_data.get("count", 0) > 10000:
            return {
                "system": "memory",
                "issue": "memory_overflow",
                "severity": "high",
                "message": "Memory count exceeds threshold"
            }
        return None
    
    def _check_agents(self, agent_data: Dict) -> Dict:
        """Check agent system"""
        failed = agent_data.get("failed", 0)
        if failed > self.error_threshold:
            return {
                "system": "agents",
                "issue": "too_many_failures",
                "severity": "high",
                "message": f"{failed} agents have failed"
            }
        
        inactive = agent_data.get("inactive", 0)
        if inactive > 100:
            return {
                "system": "agents",
                "issue": "agents_inactive",
                "severity": "medium",
                "message": f"{inactive} agents inactive"
            }
        
        return None
    
    def _check_emotions(self, emotion_data: Dict) -> Dict:
        """Check emotion system"""
        joy = emotion_data.get("joy", 0.5)
        
        if joy < 0.1:
            return {
                "system": "emotions",
                "issue": "low_joy",
                "severity": "low",
                "message": "Nova's joy is very low"
            }
        
        return None
    
    def _check_focus(self, focus_data: Dict) -> Dict:
        """Check focus system"""
        if focus_data.get("drift_count", 0) > 10:
            return {
                "system": "focus",
                "issue": "drift_detected",
                "severity": "medium",
                "message": "Task drift detected"
            }
        
        return None
    
    def get_diagnostics(self) -> Dict:
        """Get diagnostic summary"""
        return {
            "total_issues": len(self.issues),
            "checks_run": self.checks_run,
            "last_check": self.last_check,
            "recent_issues": self.issues[-10:]
        }


# Global instance
_diagnostics = None

def get_self_diagnostics() -> SelfDiagnostics:
    global _diagnostics
    if _diagnostics is None:
        _diagnostics = SelfDiagnostics()
    return _diagnostics
