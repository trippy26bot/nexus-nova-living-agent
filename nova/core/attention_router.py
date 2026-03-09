#!/usr/bin/env python3
"""
Attention Router - Selects which brains should activate based on input
"""

class AttentionRouter:
    """Routes input to relevant brains only"""
    
    def __init__(self, brains: dict = None):
        self.brains = brains or {}
        self.default_brains = ["GeneralBrain", "LogicBrain"]
        
    def route(self, message: str) -> list:
        """Determine which brains should activate"""
        message_lower = message.lower()
        
        # Coding questions
        if any(w in message_lower for w in ["code", "python", "function", "class", "debug", "script"]):
            return ["CodeBrain", "LogicBrain", "CriticBrain"]
        
        # Emotional questions
        if any(w in message_lower for w in ["feel", "emotion", "sad", "happy", "angry", "upset", "worried"]):
            return ["EmotionBrain", "EmpathyBrain", "MemoryBrain"]
        
        # Technical/analysis
        if any(w in message_lower for w in ["analyze", "data", "pattern", "trend", "market"]):
            return ["AnalysisBrain", "LogicBrain", "MemoryBrain"]
        
        # Planning
        if any(w in message_lower for w in ["plan", "strategy", "roadmap", "should i", "recommend"]):
            return ["PlanningBrain", "LogicBrain", "CriticBrain"]
        
        # Quick/simple questions
        if len(message) < 30 or "?" in message:
            return ["FastBrain", "MemoryBrain"]
        
        # Default
        return self.default_brains
    
    def register_brain(self, name: str, brain):
        """Register a brain"""
        self.brains[name] = brain
    
    def get_available_brains(self) -> list:
        return list(self.brains.keys())
