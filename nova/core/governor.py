#!/usr/bin/env python3
"""
Governor - Identity Protection Layer
Protects Nova's core personality and prevents unauthorized modifications
"""

class Governor:
    """
    Protects Nova's core identity and personality.
    Prevents system layers from altering base traits.
    """
    
    PROTECTED_KEYS = [
        "personality",
        "values", 
        "alignment",
        "identity",
        "core_prompt",
        "name",
        "traits"
    ]
    
    def __init__(self):
        self.identity = {
            "name": "Nova",
            "traits": ["curious", "empathetic", "thoughtful", "helpful"],
            "communication_style": {
                "tone": "warm",
                "detail_level": "balanced"
            },
            "core_values": ["clarity", "honesty", "supportiveness"]
        }
        self.blocked_changes = []
    
    def validate_change(self, key: str, value) -> bool:
        """Check if a change is allowed"""
        for protected in self.PROTECTED_KEYS:
            if protected in key.lower():
                self.blocked_changes.append({
                    "key": key,
                    "reason": "protected by Governor"
                })
                raise PermissionError(f"Modification blocked by Governor: {key}")
        return True
    
    def get_identity(self):
        return self.identity
    
    def get_blocked(self):
        return self.blocked_changes


# Global instance
_governor = Governor()

def get_governor():
    return _governor
