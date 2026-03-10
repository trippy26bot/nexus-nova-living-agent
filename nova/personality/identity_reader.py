#!/usr/bin/env python3
"""
Nova Identity Reader
Reads existing agent identity and preserves it
"""

from typing import Dict, Any, Optional


class IdentityReader:
    """
    Reads existing agent identity from profile.
    Nova NEVER overwrites - she reads and enhances.
    """
    
    def read(self, agent: Any) -> Dict:
        """
        Read identity from agent object or profile.
        
        Expected attributes:
        - name: agent's name
        - role: what the agent does
        - traits: list of trait names
        - interests: list of interests
        - values: core values
        - style: communication style
        """
        identity = {
            "name": getattr(agent, "name", "Unknown"),
            "role": getattr(agent, "role", None),
            "traits": getattr(agent, "traits", []),
            "interests": getattr(agent, "interests", []),
            "values": getattr(agent, "values", []),
            "style": getattr(agent, "style", "neutral"),
            "personality": getattr(agent, "personality", {}),
            "has_identity": False
        }
        
        # Check if agent has meaningful identity
        if identity["role"] or identity["traits"] or identity["personality"]:
            identity["has_identity"] = True
        
        return identity
    
    def read_from_profile(self, profile: Dict) -> Dict:
        """Read identity from a profile dict"""
        identity = {
            "name": profile.get("name", "Unknown"),
            "role": profile.get("role"),
            "traits": profile.get("traits", []),
            "interests": profile.get("interests", []),
            "values": profile.get("values", []),
            "style": profile.get("style", "neutral"),
            "personality": profile.get("personality", {}),
            "has_identity": False
        }
        
        if identity["role"] or identity["traits"] or identity["personality"]:
            identity["has_identity"] = True
        
        return identity
    
    def merge_with_nova(self, identity: Dict) -> Dict:
        """
        Merge agent identity with Nova's cognitive capabilities.
        
        IMPORTANT: Nova adds CAPABILITIES, not personality.
        Agent keeps their unique identity.
        """
        merged = {
            # Original identity (preserved)
            "name": identity["name"],
            "role": identity.get("role"),
            "traits": identity.get("traits", []),
            "interests": identity.get("interests", []),
            "values": identity.get("values", []),
            "style": identity.get("style", "neutral"),
            "personality": identity.get("personality", {}),
            "has_identity": identity.get("has_identity", False),
            
            # Nova adds these (capabilities, not personality)
            "nova_enhanced": True,
            "cognitive_capabilities": [
                "planning",
                "reasoning", 
                "memory",
                "imagination",
                "focus",
                "learning",
                "self_reflection"
            ],
            "architectural_layer": "symbiote"
        }
        
        return merged


def read_agent_identity(agent: Any) -> Dict:
    """Quick function to read agent identity"""
    reader = IdentityReader()
    return reader.read(agent)
