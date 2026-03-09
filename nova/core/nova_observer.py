"""
Observability Layer - monitors Nova's internal state
Tracks latency, brain activity, memory, and system health
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

logger = logging.getLogger("NovaObserver")


class NovaObserver:
    """Monitors Nova's internal systems for stability and performance"""
    
    def __init__(self):
        # Cycle metrics
        self.fast_loop_times: List[float] = []
        self.slow_loop_times: List[float] = []
        self.dream_loop_times: List[float] = []
        
        # Brain metrics
        self.brain_execution_times: Dict[str, List[float]] = defaultdict(list)
        self.brain_call_counts: Dict[str, int] = defaultdict(int)
        
        # Memory metrics
        self.memory_sizes: List[int] = []
        self.memory_growth_rate = 0.0
        
        # Event metrics
        self.events_per_cycle: List[int] = []
        
        # System health
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        
        # Counts
        self.total_cycles = 0
        self.total_thoughts = 0
        
        logger.info("NovaObserver initialized")
    
    # ─────────────────────────────────────────────────────────────
    # RECORDING METHODS
    # ─────────────────────────────────────────────────────────────
    
    def record_fast_loop(self, elapsed: float):
        """Record fast loop execution time"""
        self.fast_loop_times.append(elapsed)
        if len(self.fast_loop_times) > 1000:
            self.fast_loop_times.pop(0)
    
    def record_slow_loop(self, elapsed: float):
        """Record slow loop execution time"""
        self.slow_loop_times.append(elapsed)
        if len(self.slow_loop_times) > 100:
            self.slow_loop_times.pop(0)
    
    def record_dream_loop(self, elapsed: float):
        """Record dream loop execution time"""
        self.dream_loop_times.append(elapsed)
        if len(self.dream_loop_times) > 100:
            self.dream_loop_times.pop(0)
    
    def record_brain_execution(self, brain_name: str, elapsed: float):
        """Record brain execution time"""
        self.brain_execution_times[brain_name].append(elapsed)
        self.brain_call_counts[brain_name] += 1
        
        # Keep only recent
        if len(self.brain_execution_times[brain_name]) > 100:
            self.brain_execution_times[brain_name].pop(0)
    
    def record_memory_size(self, size: int):
        """Record memory size"""
        self.memory_sizes.append(size)
        if len(self.memory_sizes) > 100:
            self.memory_sizes.pop(0)
            
            # Calculate growth rate
            if len(self.memory_sizes) > 2:
                self.memory_growth_rate = (
                    self.memory_sizes[-1] - self.memory_sizes[0]
                ) / len(self.memory_sizes)
    
    def record_event_count(self, count: int):
        """Record events per cycle"""
        self.events_per_cycle.append(count)
        if len(self.events_per_cycle) > 100:
            self.events_per_cycle.pop(0)
    
    def record_cycle(self):
        """Record a completed cycle"""
        self.total_cycles += 1
    
    def record_thought(self):
        """Record a thought generated"""
        self.total_thoughts += 1
    
    def record_error(self, error: str, context: str = ""):
        """Record an error"""
        self.errors.append({
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "context": context
        })
        if len(self.errors) > 100:
            self.errors.pop(0)
        logger.warning(f"Error recorded: {error} ({context})")
    
    def record_warning(self, warning: str, context: str = ""):
        """Record a warning"""
        self.warnings.append({
            "timestamp": datetime.now().isoformat(),
            "warning": warning,
            "context": context
        })
        if len(self.warnings) > 100:
            self.warnings.pop(0)
    
    # ─────────────────────────────────────────────────────────────
    # ANALYTICS METHODS
    # ─────────────────────────────────────────────────────────────
    
    def get_fast_loop_stats(self) -> Dict[str, float]:
        """Get fast loop statistics"""
        if not self.fast_loop_times:
            return {"avg_ms": 0, "min_ms": 0, "max_ms": 0}
        
        return {
            "avg_ms": sum(self.fast_loop_times) / len(self.fast_loop_times) * 1000,
            "min_ms": min(self.fast_loop_times) * 1000,
            "max_ms": max(self.fast_loop_times) * 1000,
            "samples": len(self.fast_loop_times)
        }
    
    def get_slow_loop_stats(self) -> Dict[str, float]:
        """Get slow loop statistics"""
        if not self.slow_loop_times:
            return {"avg_ms": 0, "min_ms": 0, "max_ms": 0}
        
        return {
            "avg_ms": sum(self.slow_loop_times) / len(self.slow_loop_times) * 1000,
            "min_ms": min(self.slow_loop_times) * 1000,
            "max_ms": max(self.slow_loop_times) * 1000,
            "samples": len(self.slow_loop_times)
        }
    
    def get_brain_stats(self) -> Dict[str, Any]:
        """Get brain execution statistics"""
        stats = {}
        for brain, times in self.brain_execution_times.items():
            if times:
                stats[brain] = {
                    "avg_ms": sum(times) / len(times) * 1000,
                    "calls": self.brain_call_counts[brain],
                    "total_ms": sum(times) * 1000
                }
        return stats
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        if not self.memory_sizes:
            return {"current": 0, "growth_rate": 0}
        
        return {
            "current": self.memory_sizes[-1],
            "max": max(self.memory_sizes),
            "growth_rate": self.memory_growth_rate
        }
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Get event statistics"""
        if not self.events_per_cycle:
            return {"avg_per_cycle": 0}
        
        return {
            "avg_per_cycle": sum(self.events_per_cycle) / len(self.events_per_cycle),
            "max_per_cycle": max(self.events_per_cycle)
        }
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        fast_stats = self.get_fast_loop_stats()
        
        # Determine health status
        status = "healthy"
        if fast_stats.get("max_ms", 0) > 500:
            status = "slow"
        if len(self.errors) > 10:
            status = "degraded"
        
        return {
            "status": status,
            "total_cycles": self.total_cycles,
            "total_thoughts": self.total_thoughts,
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "fast_loop": fast_stats,
            "slow_loop": self.get_slow_loop_stats(),
            "memory": self.get_memory_stats()
        }
    
    # ─────────────────────────────────────────────────────────────
    # UTILITY
    # ─────────────────────────────────────────────────────────────
    
    def get_report(self) -> str:
        """Get human-readable status report"""
        health = self.get_health_summary()
        
        lines = [
            "=== NOVA OBSERVABILITY REPORT ===",
            f"Status: {health['status'].upper()}",
            f"Cycles: {health['total_cycles']}",
            f"Thoughts: {health['total_thoughts']}",
            "",
            "Fast Loop:",
            f"  Avg: {health['fast_loop']['avg_ms']:.2f}ms",
            f"  Max: {health['fast_loop']['max_ms']:.2f}ms",
            "",
            "Slow Loop:",
            f"  Avg: {health['slow_loop']['avg_ms']:.2f}ms",
            f"  Max: {health['slow_loop']['max_ms']:.2f}ms",
            "",
            "Memory:",
            f"  Current: {health['memory']['current']}",
            f"  Growth: {health['memory']['growth_rate']:.2f}/item",
            "",
            f"Errors: {health['errors_count']}",
            f"Warnings: {health['warnings_count']}",
        ]
        
        return "\n".join(lines)


# Global observer instance
_observer = None

def get_observer() -> NovaObserver:
    """Get or create global observer"""
    global _observer
    if _observer is None:
        _observer = NovaObserver()
    return _observer
