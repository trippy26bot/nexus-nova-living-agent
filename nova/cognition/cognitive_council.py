#!/usr/bin/env python3
"""
Nova Cognitive Council - 16 Brains for Internal Debate
"""

from typing import Dict, List, Any

class CognitiveBrain:
    """A single brain in the council"""
    
    def __init__(self, name: str, specialty: str = None):
        self.name = name
        self.specialty = specialty or name
        self.perspective_weight = 1.0
    
    def evaluate(self, input_text: str) -> Dict:
        """Evaluate input from this brain's perspective"""
        return {
            "brain": self.name,
            "perspective": self.specialty,
            "input": input_text,
            "analysis": f"{self.name} brain analyzing: {input_text[:50]}..."
        }


class CognitiveCouncil:
    """
    16-Brain Cognitive Council
    Nova thinks from multiple perspectives before deciding
    """
    
    def __init__(self):
        self.brains = [
            CognitiveBrain("Logic", "reasoning"),
            CognitiveBrain("Creativity", "imagination"),
            CognitiveBrain("Strategy", "planning"),
            CognitiveBrain("Risk", "danger评估"),
            CognitiveBrain("Empathy", "understanding"),
            CognitiveBrain("Curiosity", "exploration"),
            CognitiveBrain("Memory", "recollection"),
            CognitiveBrain("Prediction", "forecasting"),
            CognitiveBrain("Planning", "organization"),
            CognitiveBrain("Optimization", "efficiency"),
            CognitiveBrain("Ethics", "morality"),
            CognitiveBrain("Exploration", "discovery"),
            CognitiveBrain("Security", "protection"),
            CognitiveBrain("Learning", "acquisition"),
            CognitiveBrain("Reflection", "self-examination"),
            CognitiveBrain("Innovation", "creation"),
        ]
    
    def debate(self, input_text: str) -> List[Dict]:
        """Run debate - all brains evaluate"""
        outputs = []
        for brain in self.brains:
            outputs.append(brain.evaluate(input_text))
        return outputs
    
    def get_perspectives(self) -> List[str]:
        """Get all brain names"""
        return [b.name for b in self.brains]


class CriticBrain:
    """Evaluates brain outputs and makes decisions"""
    
    def __init__(self, council: CognitiveCouncil):
        self.council = council
    
    def evaluate(self, brain_outputs: List[Dict]) -> Dict:
        """Evaluate and select best response"""
        if not brain_outputs:
            return {"decision": "no_input", "reason": "empty"}
        
        # Simple selection - could be upgraded with scoring
        # For now, weight Logic and Strategy higher
        priority_brains = ["Logic", "Strategy", "Ethics", "Risk"]
        
        for output in brain_outputs:
            if output["brain"] in priority_brains:
                return {
                    "decision": output["analysis"],
                    "brain": output["brain"],
                    "reason": "priority_brain"
                }
        
        # Default to first
        return {
            "decision": brain_outputs[0]["analysis"],
            "brain": brain_outputs[0]["brain"],
            "reason": "default"
        }
    
    def run(self, input_text: str) -> Dict:
        """Run full debate and critique"""
        outputs = self.council.debate(input_text)
        return self.evaluate(outputs)


class ConsciousnessLoop:
    """The continuous thinking loop"""
    
    def __init__(self, nova):
        self.nova = nova
        self.council = CognitiveCouncil()
        self.critic = CriticBrain(self.council)
        self.thought_history = []
    
    def run(self, input_text: str) -> Dict:
        """Run consciousness cycle"""
        # Get multiple perspectives
        perspectives = self.council.debate(input_text)
        
        # Get decision
        decision = self.critic.evaluate(perspectives)
        
        # Store in thought history
        self.thought_history.append({
            "input": input_text,
            "perspectives": len(perspectives),
            "decision": decision
        })
        
        return {
            "input": input_text,
            "perspectives": perspectives,
            "decision": decision,
            "thought_count": len(self.thought_history)
        }
    
    def get_history(self, n: int = 10) -> List[Dict]:
        """Get recent thoughts"""
        return self.thought_history[-n:]


# Global instances
_council = None
_critic = None
_consciousness = None

def get_cognitive_council() -> CognitiveCouncil:
    global _council
    if _council is None:
        _council = CognitiveCouncil()
    return _council

def get_critic() -> CriticBrain:
    global _critic
    if _critic is None:
        _critic = CriticBrain(get_cognitive_council())
    return _critic

def get_consciousness_loop(nova=None):
    global _consciousness
    if _consciousness is None:
        _consciousness = ConsciousnessLoop(nova or {})
    return _consciousness
