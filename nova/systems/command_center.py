#!/usr/bin/env python3
"""
Nova Command Center Dashboard
Real-time monitoring and control
"""

import time
from typing import Dict, List, Any
from nova.systems.coordinator import get_coordinator, get_nova_metrics
from nova.cognition.cognitive_council import get_cognitive_council

class CommandCenter:
    """Nova's command center dashboard"""
    
    def __init__(self):
        self.coordinator = get_coordinator()
        self.metrics = get_nova_metrics()
        self.council = get_cognitive_council()
        self.start_time = time.time()
    
    def get_status(self) -> Dict:
        """Get full system status"""
        return {
            "uptime": time.time() - self.start_time,
            "coordinator": self.coordinator.get_statistics(),
            "metrics": self.metrics.get_metrics(),
            "cognitive_council": {
                "brains": len(self.council.get_perspectives())
            }
        }
    
    def get_dashboard(self) -> str:
        """Generate dashboard display"""
        status = self.get_status()
        
        dashboard = f"""
╔══════════════════════════════════════════════════════════════╗
║               NOVA COMMAND CENTER                             ║
╠══════════════════════════════════════════════════════════════╣
║  Uptime: {status['uptime']:.1f}s
║
║  AGENTS: {status['coordinator']['total_agents']} active
║    Completed: {status['coordinator']['total_completed']}
║    Failed: {status['coordinator']['total_failed']}
║    Success Rate: {status['coordinator']['success_rate']*100:.1f}%
║
║  TASKS: {status['metrics']['total_tasks']} total
║    Success Rate: {status['metrics']['success_rate']*100:.1f}%
║    Errors: {status['metrics']['error_count']}
║
║  COGNITIVE COUNCIL: {status['cognitive_council']['brains']} brains
║
╚══════════════════════════════════════════════════════════════╝
"""
        return dashboard
    
    def print_dashboard(self):
        """Print dashboard to console"""
        print(self.get_dashboard())


# Global instance
_command_center = None

def get_command_center() -> CommandCenter:
    global _command_center
    if _command_center is None:
        _command_center = CommandCenter()
    return _command_center
