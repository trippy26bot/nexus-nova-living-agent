#!/usr/bin/env python3
"""
Nova Heartbeat Loop - The living agent cycle
This is what makes Nova feel alive rather than just responding
"""

import time
import threading
from nova.core.nova_core import get_nova_core
from nova.core.emotion_engine import get_emotion_engine
from nova.core.drift_engine import get_drift_engine
from nova.core.memory_engine import get_memory_engine

class NovaHeartbeat:
    """
    Background loop that keeps Nova 'alive'
    
    Fast cycle (5s): Quick processing, emotion decay
    Medium cycle (30s): Context check, memory consolidation  
    Slow cycle (5min): Deep reflection, goal review
    """
    
    def __init__(self):
        self.running = False
        self.core = get_nova_core()
        self.emotions = get_emotion_engine()
        self.drift = get_drift_engine()
        self.memory = get_memory_engine()
        self.thread = None
        
        # Cycle timing
        self.fast_interval = 5
        self.medium_interval = 30
        self.slow_interval = 300
        
        self.last_medium = time.time()
        self.last_slow = time.time()
    
    def start(self):
        """Start the heartbeat"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("💓 Nova heartbeat started")
    
    def stop(self):
        """Stop the heartbeat"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("💔 Nova heartbeat stopped")
    
    def _run(self):
        """Main heartbeat loop"""
        while self.running:
            try:
                now = time.time()
                
                # Fast cycle - always runs
                self._fast_cycle()
                
                # Medium cycle
                if now - self.last_medium > self.medium_interval:
                    self._medium_cycle()
                    self.last_medium = now
                
                # Slow cycle  
                if now - self.last_slow > self.slow_interval:
                    self._slow_cycle()
                    self.last_slow = time.time()
                
                time.sleep(self.fast_interval)
                
            except Exception as e:
                print(f"Heartbeat error: {e}")
                time.sleep(5)
    
    def _fast_cycle(self):
        """Fast processing - emotion decay, quick checks"""
        # Apply emotion decay
        self.emotions.decay()
    
    def _medium_cycle(self):
        """Medium cycle - context check, memory work"""
        # Check drift
        status = self.drift.check()
        
        # Consolidate short-term to conversation history
        short = self.memory.get_short(3)
        if short:
            # Already handled by memory engine
    
    def _slow_cycle(self):
        """Slow cycle - deep reflection, evolution"""
        # Run reflection
        self.drift.reflect()
        
        # Compress memory if needed
        self.memory.compress()
    
    def status(self) -> dict:
        """Get heartbeat status"""
        return {
            "running": self.running,
            "fast_interval": self.fast_interval,
            "medium_interval": self.medium_interval,
            "slow_interval": self.slow_interval,
            "drift_stats": self.drift.get_stats(),
            "emotions": self.emotions.get_state()
        }


# Global instance
_heartbeat = None

def get_heartbeat():
    global _heartbeat
    if _heartbeat is None:
        _heartbeat = NovaHeartbeat()
    return _heartbeat

def start_nova():
    """Start Nova's heartbeat"""
    hb = get_heartbeat()
    hb.start()
    return hb

def stop_nova():
    """Stop Nova's heartbeat"""
    hb = get_heartbeat()
    hb.stop()
