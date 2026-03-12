#!/usr/bin/env python3
"""
Nova Relationship Memory System
Remembers users, preferences, shared history, trust
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


class RelationshipProfile:
    """Stores relationship data for a single user"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.name = None
        self.nickname = None
        self.timezone = None
        self.preferences = []
        self.interests = []
        self.communication_style = "neutral"  # short, detailed, casual, technical
        self.shared_history = []
        self.trust_level = 50  # 0-100
        self.interaction_count = 0
        self.last_interaction = None
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "nickname": self.nickname,
            "timezone": self.timezone,
            "preferences": self.preferences,
            "interests": self.interests,
            "communication_style": self.communication_style,
            "shared_history": self.shared_history,
            "trust_level": self.trust_level,
            "interaction_count": self.interaction_count,
            "last_interaction": self.last_interaction,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RelationshipProfile':
        profile = cls(data.get("user_id", ""))
        profile.name = data.get("name")
        profile.nickname = data.get("nickname")
        profile.timezone = data.get("timezone")
        profile.preferences = data.get("preferences", [])
        profile.interests = data.get("interests", [])
        profile.communication_style = data.get("communication_style", "neutral")
        profile.shared_history = data.get("shared_history", [])
        profile.trust_level = data.get("trust_level", 50)
        profile.interaction_count = data.get("interaction_count", 0)
        profile.last_interaction = data.get("last_interaction")
        profile.created_at = data.get("created_at", datetime.now().isoformat())
        return profile


class RelationshipMemory:
    """Manages all user relationships"""
    
    def __init__(self, storage_path: str = "~/.nova/memory/relationships"):
        self.storage_path = os.path.expanduser(storage_path)
        os.makedirs(self.storage_path, exist_ok=True)
        
        self.profiles: Dict[str, RelationshipProfile] = {}
        self.default_user = "default"
    
    def get_profile(self, user_id: str) -> RelationshipProfile:
        """Get or create a user profile"""
        if user_id not in self.profiles:
            # Try to load from disk
            profile = self._load_profile(user_id)
            if profile:
                self.profiles[user_id] = profile
            else:
                self.profiles[user_id] = RelationshipProfile(user_id)
        
        return self.profiles[user_id]
    
    def _profile_path(self, user_id: str) -> str:
        return os.path.join(self.storage_path, f"{user_id}.json")
    
    def _load_profile(self, user_id: str) -> Optional[RelationshipProfile]:
        path = self._profile_path(user_id)
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    return RelationshipProfile.from_dict(data)
            except:
                pass
        return None
    
    def save_profile(self, user_id: str):
        """Save profile to disk"""
        if user_id in self.profiles:
            path = self._profile_path(user_id)
            with open(path, 'w') as f:
                json.dump(self.profiles[user_id].to_dict(), f, indent=2)
    
    def record_interaction(self, user_id: str, interaction_type: str, description: str, sentiment: str = "neutral"):
        """Record an interaction with a user"""
        profile = self.get_profile(user_id)
        
        profile.interaction_count += 1
        profile.last_interaction = datetime.now().isoformat()
        
        # Add to shared history
        profile.shared_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "description": description,
            "sentiment": sentiment
        })
        
        # Keep history manageable
        if len(profile.shared_history) > 100:
            profile.shared_history = profile.shared_history[-100:]
        
        # Adjust trust based on sentiment
        if sentiment == "positive":
            profile.trust_level = min(100, profile.trust_level + 1)
        elif sentiment == "negative":
            profile.trust_level = max(0, profile.trust_level - 2)
        
        # Save
        self.save_profile(user_id)
    
    def update_preferences(self, user_id: str, preferences: List[str]):
        """Update user preferences"""
        profile = self.get_profile(user_id)
        profile.preferences = list(set(preferences + profile.preferences))
        self.save_profile(user_id)
    
    def update_interests(self, user_id: str, interests: List[str]):
        """Update user interests"""
        profile = self.get_profile(user_id)
        profile.interests = list(set(interests + profile.interests))
        self.save_profile(user_id)
    
    def set_communication_style(self, user_id: str, style: str):
        """Set communication style (short, detailed, casual, technical)"""
        profile = self.get_profile(user_id)
        profile.communication_style = style
        self.save_profile(user_id)
    
    def get_shared_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent shared history"""
        profile = self.get_profile(user_id)
        return profile.shared_history[-limit:]
    
    def adapt_response_style(self, user_id: str, base_response: str) -> str:
        """Adapt response based on user preferences"""
        profile = self.get_profile(user_id)
        
        style = profile.communication_style
        
        if style == "short":
            # Truncate to essentials
            sentences = base_response.split('.')
            if len(sentences) > 2:
                return '. '.join(sentences[:2]) + '.'
        
        elif style == "technical":
            # Add more detail
            return base_response
        
        elif style == "casual":
            # More relaxed
            return base_response.replace("Furthermore", "Also").replace("Therefore", "So")
        
        return base_response
    
    def get_trust_level(self, user_id: str) -> int:
        """Get user trust level"""
        return self.get_profile(user_id).trust_level
    
    def get_all_profiles(self) -> Dict[str, RelationshipProfile]:
        """Get all profiles"""
        return self.profiles


# Global instance
_relationship_memory = None

def get_relationship_memory() -> RelationshipMemory:
    global _relationship_memory
    if _relationship_memory is None:
        _relationship_memory = RelationshipMemory()
    return _relationship_memory
