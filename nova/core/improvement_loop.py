#!/usr/bin/env python3
"""
Autonomous Improvement Loop - Nova analyzes and improves herself
"""

from nova.core.metrics import get_metrics
from nova.core.learning_log import get_learning_log

class ImprovementLoop:
    """Nova reviews performance and suggests improvements"""
    
    def __init__(self, metrics=None, log=None):
        self.metrics = metrics or get_metrics()
        self.log = log or get_learning_log()
    
    def analyze(self):
        """Analyze performance and generate improvements"""
        data = self.metrics.summary()
        suggestions = []
        
        # Analyze failure rate
        if data["responses"] > 0:
            failure_rate = data["failures"] / data["responses"]
            if failure_rate > 0.1:
                suggestions.append("High failure rate detected - review error handling")
        
        # Analyze slow responses
        if data["slow_responses"] > 5:
            suggestions.append("Consider optimizing response pathways")
        
        # Analyze critic flags
        if data["critic_flags"] > 10:
            suggestions.append("Review reasoning quality - high critic activity")
        
        # Analyze governor blocks
        if data["governor_blocks"] > 0:
            suggestions.append("Governor blocked unauthorized changes - system working as designed")
        
        # Memory analysis
        if data["memory_ops"] == 0 and data["responses"] > 10:
            suggestions.append("No memory operations - consider memory integration")
        
        # Brain activation analysis
        if data["responses"] > 0:
            brain_rate = data["brain_activations"] / data["responses"]
            if brain_rate < 0.5:
                suggestions.append("Low brain activation rate - verify routing")
        
        # Default if everything looks good
        if not suggestions:
            suggestions.append("System performing within expected parameters")
        
        # Record suggestions
        for s in suggestions:
            self.log.record_improvement(s)
        
        return {
            "metrics": data,
            "suggestions": suggestions
        }
    
    def quick_check(self) -> str:
        """Quick status check"""
        data = self.metrics.summary()
        
        if data["failures"] > data["responses"] * 0.1:
            return "⚠️ Elevated failure rate"
        if data["slow_responses"] > 10:
            return "⚠️ High latency detected"
        
        return "✅ Systems nominal"


# Global instance
_improvement_loop = ImprovementLoop()

def get_improvement_loop():
    return _improvement_loop
