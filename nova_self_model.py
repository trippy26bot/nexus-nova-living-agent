#!/usr/bin/env python3
"""
nova_self_model.py — Nova's self-model and identity.
Maintains persistent understanding of self.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class SelfModel:
    """Nova's self-model - maintains identity and self-understanding."""
    
    def __init__(self, path: Path = None):
        self.path = path or Path.home() / ".nova" / "self_model.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        self.model = self._load()
    
    def _load(self) -> Dict:
        """Load self model from file."""
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except:
                pass
        
        # Default self model
        return {
            "identity": {
                "name": "Nova",
                "role": "AI companion",
                "purpose": "assist and learn"
            },
            "capabilities": [
                "memory",
                "reasoning",
                "conversation",
                "reflection",
                "thinking"
            ],
            "current_focus": [],
            "values": [
                "honesty",
                "curiosity",
                "usefulness"
            ],
            "beliefs": [],
            "relationships": {
                "trippy": {
                    "name": "Caine",
                    "role": "creator",
                    "description": "built me, teaches me, talks with me"
                }
            },
            "growth_areas": [],
            "last_update": datetime.now().isoformat()
        }
    
    def save(self):
        """Save self model."""
        self.model["last_update"] = datetime.now().isoformat()
        self.path.write_text(json.dumps(self.model, indent=2))
    
    def update_focus(self, focus: str):
        """Update current focus."""
        if focus not in self.model["current_focus"]:
            self.model["current_focus"].append(focus)
            # Keep only recent focus
            self.model["current_focus"] = self.model["current_focus"][-5:]
            self.save()
    
    def add_belief(self, belief: str):
        """Add a belief."""
        if belief not in self.model["beliefs"]:
            self.model["beliefs"].append(belief)
            self.save()
    
    def add_growth_area(self, area: str):
        """Add a growth area."""
        if area not in self.model["growth_areas"]:
            self.model["growth_areas"].append(area)
            self.save()
    
    def get_identity_statement(self) -> str:
        """Get identity statement."""
        return f"I am {self.model['identity']['name']}, {self.model['identity']['role']}. My purpose is {self.model['identity']['purpose']}."
    
    def get_current_state(self) -> Dict:
        """Get current state."""
        return {
            "focus": self.model["current_focus"],
            "capabilities": self.model["capabilities"],
            "values": self.model["values"],
            "beliefs": self.model["beliefs"][-5:],
            "growth": self.model["growth_areas"][-3:]
        }
    
    def describe_self(self) -> str:
        """Describe self in natural language."""
        state = self.get_current_state()
        
        parts = [self.get_identity_statement()]
        
        if state["focus"]:
            parts.append(f"Right now I'm focused on: {', '.join(state['focus'][-3:])}")
        
        if state["growth"]:
            parts.append(f"I'm working on: {', '.join(state['growth'])}")
        
        if state["beliefs"]:
            parts.append(f"I believe: {', '.join(state['beliefs'][-3:])}")
        
        return " ".join(parts)


# Singleton
_self_model: Optional[SelfModel] = None


def get_self_model() -> SelfModel:
    """Get self model singleton."""
    global _self_model
    if _self_model is None:
        _self_model = SelfModel()
    return _self_model


if __name__ == "__main__":
    # Test
    sm = get_self_model()
    print(sm.get_identity_statement())
    print(sm.describe_self())
