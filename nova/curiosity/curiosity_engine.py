"""Curiosity Engine - Drives exploration"""
import random

class CuriosityEngine:
    def __init__(self):
        self.exploration_types = ["analyze", "experiment", "explore", "observe"]
    
    def suggest_actions(self, shared_state):
        # Return exploratory actions
        return [random.choice(self.exploration_types)]
