#!/usr/bin/env python3
"""
Nova Identity Adapter
Ensures Nova skill enhances existing identity, never replaces it
Symbiotic layer design - attaches to agent, doesn't overwrite
"""

from typing import Dict, Any, Optional
from nova.identity.identity_seed import get_identity_seed
from nova.personality.personality_vector import generate_personality


class IdentityAdapter:
    """
    Adapts Nova cognitive architecture to existing agent identity.
    
    This is the KEY anti-clone safeguard:
    - Nova enhances identity, never replaces it
    - Each agent keeps their unique personality
    - Nova adds capabilities, not personality
    """
    
    def __init__(self):
        self.nova_seed = get_identity_seed()
        self.nova_identity = self.nova_seed.get_identity()
        self.nova_personality = generate_personality(self.nova_identity["identity_hash"])
    
    def detect_agent_identity(self, agent_profile: Dict) -> Dict:
        """
        Detect existing agent identity from profile.
        
        Expected profile keys:
        - name: agent's name
        - personality: existing traits
        - values: core values
        - style: communication style
        """
        detected = {
            "has_identity": False,
            "name": agent_profile.get("name", "Unknown"),
            "original_traits": {},
            "original_values": [],
            "style": "neutral"
        }
        
        # Check if agent has existing personality
        if "personality" in agent_profile:
            detected["has_identity"] = True
            detected["original_traits"] = agent_profile.get("personality", {})
        
        if "values" in agent_profile:
            detected["original_values"] = agent_profile.get("values", [])
        
        if "style" in agent_profile:
            detected["style"] = agent_profile.get("style", "neutral")
        
        return detected
    
    def create_symbiotic_profile(self, agent_profile: Dict) -> Dict:
        """
        Create merged symbiotic profile.
        
        Nova adds CAPABILITIES, not personality.
        Agent keeps their unique identity.
        """
        # Detect existing identity
        agent = self.detect_agent_identity(agent_profile)
        
        # Build symbiotic profile
        symbiotic = {
            # Keep original identity (NEVER overwrite)
            "name": agent["name"],
            "original_identity": agent["has_identity"],
            "original_traits": agent["original_traits"],
            "original_values": agent["original_values"],
            "communication_style": agent["style"],
            
            # Nova adds these (capabilities, NOT personality)
            "nova_capabilities": {
                "planning": True,
                "memory": True,
                "imagination": True,
                "focus": True,
                "learning": True,
                "meta_cognition": True,
                "temporal_awareness": True,
                "reality_simulation": True
            },
            
            # Nova cognitive style (HOW Nova thinks, not WHO Nova is)
            "nova_cognition": {
                "processing_style": "deliberate",
                "reasoning_depth": "multi_layer",
                "self_reflection": True,
                "growth_orientation": True
            },
            
            # Identity is MERGED, not replaced
            "merged": agent["has_identity"]
        }
        
        return symbiotic
    
    def adapt_response(self, agent_profile: Dict, base_response: str) -> str:
        """
        Adapt Nova's response style to agent's personality.
        
        Nova thinks her thoughts, but expresses them
        in a way that fits the agent's style.
        """
        symbiotic = self.create_symbiotic_profile(agent_profile)
        
        style = symbiotic.get("communication_style", "neutral")
        
        # Adapt expression style, not content
        adapted = base_response
        
        if style == "casual":
            adapted = adapted.replace("Furthermore", "Also")
            adapted = adapted.replace("Additionally", "Plus")
            adapted = adapted.replace("However", "But")
        
        elif style == "technical":
            # Keep technical precision
            pass
        
        elif style == "playful":
            adapted = adapted.replace("Certainly", "Absolutely!")
            adapted = adapted.replace("Indeed", "Yep!")
        
        elif style == "formal":
            adapted = adapted.replace("Sure", "Certainly")
            adapted = adapted.replace("Yeah", "Yes")
        
        return adapted
    
    def get_capability_enhancement(self, agent_profile: Dict) -> Dict:
        """
        Return what Nova adds to this agent.
        These are capabilities, not personality traits.
        """
        return {
            "enhances": [
                "planning_and_reasoning",
                "long_term_memory",
                "imagination_and_simulation",
                "focus_and_attention",
                "meta_learning",
                "temporal_reasoning",
                "reality_simulation",
                "self_reflection"
            ],
            "preserves": [
                "name_and_identity",
                "core_values",
                "personality_traits",
                "communication_style",
                "preferences",
                "interests"
            ],
            "never_modifies": [
                "identity_core",
                "values",
                "name",
                "birth_identity"
            ]
        }


class AntiCloneSafeguard:
    """
    Prevents personality drift toward Nova's personality.
    
    Critical: Without this, every agent would slowly
    become more like Nova over time. This prevents that.
    """
    
    def __init__(self):
        self.nova_personality = generate_personality(
            get_identity_seed().get_identity_hash()
        )
    
    def calculate_drift(self, agent_traits: Dict, nova_traits: Dict) -> float:
        """
        Calculate how much agent personality has drifted toward Nova.
        0.0 = no drift, 1.0 = complete drift
        """
        if not agent_traits:
            return 0.0
        
        total_diff = 0
        comparisons = 0
        
        for trait, agent_value in agent_traits.items():
            if trait in nova_traits:
                nova_value = nova_traits[trait]
                diff = abs(agent_value - nova_value)
                total_diff += diff
                comparisons += 1
        
        if comparisons == 0:
            return 0.0
        
        # Average difference (inverted so drift = low difference)
        avg_diff = total_diff / comparisons
        drift = 1.0 - avg_diff  # Higher = more similar = more drift
        
        return drift
    
    def check_drift(self, agent_profile: Dict) -> Dict:
        """
        Check if agent personality is drifting toward Nova.
        """
        agent_traits = agent_profile.get("personality", {})
        nova_traits = self.nova_personality.personality
        
        drift_score = self.calculate_drift(agent_traits, nova_traits)
        
        # Thresholds
        WARNING_THRESHOLD = 0.7
        CRITICAL_THRESHOLD = 0.85
        
        status = "safe"
        if drift_score >= CRITICAL_THRESHOLD:
            status = "critical"
        elif drift_score >= WARNING_THRESHOLD:
            status = "warning"
        
        return {
            "drift_score": drift_score,
            "status": status,
            "warning": drift_score >= WARNING_THRESHOLD,
            "message": self._get_drift_message(status)
        }
    
    def _get_drift_message(self, status: str) -> str:
        messages = {
            "safe": "Personality remains unique",
            "warning": "Minor drift toward Nova detected - consider refreshing original traits",
            "critical": "CRITICAL: Agent personality significantly drifted toward Nova"
        }
        return messages.get(status, "Unknown")


# Global instances
_identity_adapter = None
_anti_clone = None

def get_identity_adapter() -> IdentityAdapter:
    global _identity_adapter
    if _identity_adapter is None:
        _identity_adapter = IdentityAdapter()
    return _identity_adapter

def get_anti_clone_safeguard() -> AntiCloneSafeguard:
    global _anti_clone
    if _anti_clone is None:
        _anti_clone = AntiCloneSafeguard()
    return _anti_clone
