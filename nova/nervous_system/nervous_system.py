#!/usr/bin/env python3
"""
Nova Digital Nervous System
Internal awareness - monitors system health, performance, security
"""

import time
import threading
from typing import Dict, List, Any, Optional, Callable
from collections import deque
from datetime import datetime

# Optional: psutil for system metrics
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class SystemMonitor:
    """Monitors system resources"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_cpu(self) -> Dict:
        """Get CPU usage"""
        if not PSUTIL_AVAILABLE:
            return {"percent": 0, "count": 1, "freq": None}
        return {
            "percent": psutil.cpu_percent(interval=0.1),
            "count": psutil.cpu_count(),
            "freq": psutil.cpu_freq().current if psutil.cpu_freq() else None
        }
    
    def get_memory(self) -> Dict:
        """Get memory usage"""
        if not PSUTIL_AVAILABLE:
            return {"total": 0, "available": 0, "percent": 0, "used": 0}
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "percent": mem.percent,
            "used": mem.used
        }
    
    def get_disk(self) -> Dict:
        """Get disk usage"""
        if not PSUTIL_AVAILABLE:
            return {"total": 0, "used": 0, "free": 0, "percent": 0}
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
    
    def get_network(self) -> Dict:
        """Get network I/O"""
        if not PSUTIL_AVAILABLE:
            return {"bytes_sent": 0, "bytes_recv": 0, "packets_sent": 0, "packets_recv": 0}
        net = psutil.net_io_counters()
        return {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv
        }
    
    def get_all(self) -> Dict:
        """Get all system metrics"""
        return {
            "cpu": self.get_cpu(),
            "memory": self.get_memory(),
            "disk": self.get_disk(),
            "network": self.get_network(),
            "uptime": time.time() - self.start_time
        }


class HealthChecker:
    """Checks system health status"""
    
    def __init__(self):
        self.checks = {}
        self.thresholds = {
            "cpu_percent": 90.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0
        }
    
    def check(self, system_metrics: Dict) -> Dict:
        """Run health checks"""
        issues = []
        
        # CPU check
        cpu = system_metrics.get("cpu", {})
        if cpu.get("percent", 0) > self.thresholds["cpu_percent"]:
            issues.append({
                "severity": "warning",
                "system": "cpu",
                "message": f"CPU usage high: {cpu['percent']}%"
            })
        
        # Memory check
        mem = system_metrics.get("memory", {})
        if mem.get("percent", 0) > self.thresholds["memory_percent"]:
            issues.append({
                "severity": "critical",
                "system": "memory",
                "message": f"Memory usage high: {mem['percent']}%"
            })
        
        # Disk check
        disk = system_metrics.get("disk", {})
        if disk.get("percent", 0) > self.thresholds["disk_percent"]:
            issues.append({
                "severity": "warning",
                "system": "disk",
                "message": f"Disk usage high: {disk['percent']}%"
            })
        
        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "timestamp": datetime.now().isoformat()
        }
    
    def set_thresholds(self, thresholds: Dict):
        """Set health check thresholds"""
        self.thresholds.update(thresholds)


class PerformanceMonitor:
    """Monitors Nova's performance metrics"""
    
    def __init__(self):
        self.metrics = deque(maxlen=1000)
        self.counters = {}
    
    def record(self, metric_type: str, value: float, metadata: Optional[Dict] = None):
        """Record a performance metric"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": metric_type,
            "value": value,
            "metadata": metadata or {}
        }
        self.metrics.append(entry)
        
        # Update counter
        self.counters[metric_type] = self.counters.get(metric_type, 0) + 1
    
    def get_recent(self, metric_type: str = None, limit: int = 100) -> List[Dict]:
        """Get recent metrics"""
        metrics = list(self.metrics)
        if metric_type:
            metrics = [m for m in metrics if m["type"] == metric_type]
        return metrics[-limit:]
    
    def get_average(self, metric_type: str, window: int = 100) -> float:
        """Get average value for a metric"""
        recent = self.get_recent(metric_type, window)
        if not recent:
            return 0.0
        return sum(m["value"] for m in recent) / len(recent)
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        return {
            "total_records": len(self.metrics),
            "metric_types": len(self.counters),
            "counters": dict(self.counters)
        }


class SecurityMonitor:
    """Monitors security-related events"""
    
    def __init__(self):
        self.alerts = deque(maxlen=100)
        self.events = deque(maxlen=500)
    
    def log_event(self, event_type: str, details: Dict):
        """Log a security event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details
        }
        self.events.append(event)
    
    def alert(self, severity: str, message: str, details: Optional[Dict] = None):
        """Raise a security alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "message": message,
            "details": details or {}
        }
        self.alerts.append(alert)
        
        # Also log as event
        self.log_event("alert", alert)
    
    def get_alerts(self, limit: int = 20) -> List[Dict]:
        """Get recent alerts"""
        return list(self.alerts)[-limit:]
    
    def get_events(self, limit: int = 100) -> List[Dict]:
        """Get recent events"""
        return list(self.events)[-limit:]
    
    def get_stats(self) -> Dict:
        """Get security statistics"""
        return {
            "total_events": len(self.events),
            "total_alerts": len(self.alerts),
            "recent_alerts": len([a for a in self.alerts if a.get("severity") == "critical"])
        }


class DataFlowMonitor:
    """Monitors data flow between systems"""
    
    def __init__(self):
        self.flows = {}
        self.transfers = deque(maxlen=1000)
    
    def start_transfer(self, flow_id: str, from_system: str, to_system: str, size: int):
        """Record start of data transfer"""
        self.flows[flow_id] = {
            "from": from_system,
            "to": to_system,
            "size": size,
            "started": datetime.now().isoformat(),
            "status": "active"
        }
    
    def end_transfer(self, flow_id: str, success: bool = True):
        """Record end of data transfer"""
        if flow_id in self.flows:
            flow = self.flows[flow_id]
            flow["status"] = "completed" if success else "failed"
            flow["completed"] = datetime.now().isoformat()
            
            self.transfers.append(flow)
            del self.flows[flow_id]
    
    def get_active_flows(self) -> Dict:
        """Get active transfers"""
        return dict(self.flows)
    
    def get_recent_transfers(self, limit: int = 50) -> List[Dict]:
        """Get recent transfers"""
        return list(self.transfers)[-limit:]


class DigitalNervousSystem:
    """Core nervous system - coordinates all monitoring"""
    
    def __init__(self):
        self.system = SystemMonitor()
        self.health = HealthChecker()
        self.performance = PerformanceMonitor()
        self.security = SecurityMonitor()
        self.dataflow = DataFlowMonitor()
        
        self.monitoring_enabled = True
        self.auto_stabilize = False
        self.start_time = time.time()
    
    def get_full_status(self) -> Dict:
        """Get complete system status"""
        system_metrics = self.system.get_all()
        health_status = self.health.check(system_metrics)
        
        return {
            "status": "healthy" if health_status["healthy"] else "degraded",
            "uptime": time.time() - self.start_time,
            "system": system_metrics,
            "health": health_status,
            "performance": self.performance.get_stats(),
            "security": self.security.get_stats(),
            "dataflow": {
                "active": len(self.dataflow.get_active_flows()),
                "recent": len(self.dataflow.get_recent_transfers())
            }
        }
    
    def record_performance(self, metric_type: str, value: float, metadata: Optional[Dict] = None):
        """Record performance metric"""
        self.performance.record(metric_type, value, metadata)
    
    def log_security_event(self, event_type: str, details: Dict):
        """Log security event"""
        self.security.log_event(event_type, details)
    
    def raise_alert(self, severity: str, message: str, details: Optional[Dict] = None):
        """Raise security alert"""
        self.security.alert(severity, message, details)
        
        # Auto-stabilize if enabled
        if self.auto_stabilize and severity == "critical":
            self._attempt_stabilize(message)
    
    def _attempt_stabilize(self, issue: str):
        """Attempt to stabilize system"""
        # This would trigger various stabilization routines
        # For now, just log the attempt
        self.log_security_event("stabilize_attempt", {"issue": issue})
    
    def enable(self):
        """Enable monitoring"""
        self.monitoring_enabled = True
    
    def disable(self):
        """Disable monitoring"""
        self.monitoring_enabled = False


# Global instance
_nervous_system = None

def get_nervous_system() -> DigitalNervousSystem:
    global _nervous_system
    if _nervous_system is None:
        _nervous_system = DigitalNervousSystem()
    return _nervous_system


# Convenience functions
def get_system_status() -> Dict:
    """Get complete system status"""
    return get_nervous_system().get_full_status()

def record_performance(metric_type: str, value: float, metadata: Optional[Dict] = None):
    """Record performance metric"""
    get_nervous_system().record_performance(metric_type, value, metadata)

def raise_security_alert(severity: str, message: str, details: Optional[Dict] = None):
    """Raise security alert"""
    get_nervous_system().raise_alert(severity, message, details)
