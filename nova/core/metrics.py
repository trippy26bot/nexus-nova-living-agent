#!/usr/bin/env python3
"""
Metrics System - Track Nova's performance
"""

class Metrics:
    """Track Nova's operational metrics"""
    
    def __init__(self):
        self.data = {
            "responses": 0,
            "failures": 0,
            "slow_responses": 0,
            "critic_flags": 0,
            "memory_ops": 0,
            "brain_activations": 0,
            "governor_blocks": 0
        }
    
    def record_response(self):
        self.data["responses"] += 1
    
    def record_failure(self):
        self.data["failures"] += 1
    
    def record_slow(self):
        self.data["slow_responses"] += 1
    
    def record_critic_flag(self):
        self.data["critic_flags"] += 1
    
    def record_memory_op(self):
        self.data["memory_ops"] += 1
    
    def record_brain_activation(self):
        self.data["brain_activations"] += 1
    
    def record_governor_block(self):
        self.data["governor_blocks"] += 1
    
    def summary(self):
        return self.data.copy()
    
    def reset(self):
        for key in self.data:
            self.data[key] = 0


# Global instance
_metrics = Metrics()

def get_metrics():
    return _metrics
