#!/usr/bin/env python3
"""
Nova Intrusion Monitor
Detects abnormal behavior
"""

import time
from typing import Dict, List, Any

class IntrusionMonitor:
    """
    Monitors Nova for abnormal behavior.
    Triggers lockdown if anomalies exceed threshold.
    """
    
    def __init__(self, threshold: int = 10):
        self.threshold = threshold
        self.anomalies = []
        self.anomaly_count = 0
        self.locked = False
        self.start_time = time.time()
    
    def report(self, event: str, severity: str = "low"):
        """Report a security event"""
        anomaly = {
            "event": event,
            "severity": severity,
            "time": time.time()
        }
        
        self.anomalies.append(anomaly)
        self.anomaly_count += 1
        
        # Check threshold
        if self.anomaly_count > self.threshold:
            self._trigger_lockdown()
    
    def _trigger_lockdown(self):
        """Trigger system lockdown"""
        self.locked = True
        self.anomalies.append({
            "event": "SYSTEM_LOCKDOWN",
            "severity": "critical",
            "time": time.time()
        })
    
    def is_locked(self) -> bool:
        """Check if system is locked"""
        return self.locked
    
    def reset(self):
        """Reset monitor"""
        self.anomalies = []
        self.anomaly_count = 0
        self.locked = False
    
    def get_anomalies(self, n: int = 10) -> List[Dict]:
        """Get recent anomalies"""
        return self.anomalies[-n:]
    
    def get_stats(self) -> Dict:
        """Get monitor statistics"""
        uptime = time.time() - self.start_time
        
        return {
            "anomaly_count": self.anomaly_count,
            "threshold": self.threshold,
            "locked": self.locked,
            "uptime_seconds": uptime,
            "recent_count": len(self.anomalies[-10:])
        }


# Global instance
_monitor = None

def get_intrusion_monitor() -> IntrusionMonitor:
    global _monitor
    if _monitor is None:
        _monitor = IntrusionMonitor()
    return _monitor
