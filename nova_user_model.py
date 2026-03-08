#!/usr/bin/env python3
"""
nova_user_model.py — Model of the user.
Learns interests, patterns, preferences.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class UserModel:
    """Model of the user."""
    
    def __init__(self, path: Path = None):
        self.path = path or Path.home() / ".nova" / "user_model.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.model = self._load()
    
    def _load(self) -> Dict:
        """Load user model."""
        if self.path.exists():
            try:
                return json.loads(self.path.read_text())
            except:
                pass
        
        return {
            "name": "Caine",
            "interests": {},
            "behavior": {
                "curiosity_score": 0.0,
                "detail_level": 0.0,
                "correction_rate": 0.0,
                "total_messages": 0,
                "corrections": 0
            },
            "topics": {},
            "last_updated": datetime.now().isoformat()
        }
    
    def save(self):
        """Save user model."""
        self.model["last_updated"] = datetime.now().isoformat()
        self.path.write_text(json.dumps(self.model, indent=2))
    
    def update_from_message(self, user_message: str, is_correction: bool = False):
        """Update model from user message."""
        self.model["behavior"]["total_messages"] += 1
        
        if is_correction:
            self.model["behavior"]["corrections"] += 1
        
        # Update curiosity (questions)
        if "?" in user_message:
            self.model["behavior"]["curiosity_score"] = min(1.0, 
                self.model["behavior"]["curiosity_score"] + 0.05)
        
        # Update detail level
        word_count = len(user_message.split())
        if word_count > 50:
            self.model["behavior"]["detail_level"] = min(1.0,
                self.model["behavior"]["detail_level"] + 0.02)
        
        # Extract topics
        topics = self._extract_topics(user_message)
        for topic in topics:
            self.model["topics"][topic] = self.model["topics"].get(topic, 0) + 0.1
        
        self.save()
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text."""
        text = text.lower()
        
        topic_keywords = {
            "ai_agents": ["ai agent", "autonomous", "agent"],
            "memory": ["memory", "recall", "remember"],
            "cognitive": ["cognitive", "architecture", "brain"],
            "emotions": ["emotion", "feel", "sad", "happy"],
            "programming": ["code", "python", "program"],
            "learning": ["learn", "learning", "train"],
            "curiosity": ["curious", "curiosity", "why"],
        }
        
        found = []
        for topic, keywords in topic_keywords.items():
            if any(k in text for k in keywords):
                found.append(topic)
        
        return found
    
    def get_interests(self) -> List[str]:
        """Get top interests."""
        sorted_interests = sorted(
            self.model["topics"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [t[0] for t in sorted_interests[:5]]
    
    def get_behavior_summary(self) -> str:
        """Get behavior summary."""
        b = self.model["behavior"]
        
        traits = []
        
        if b.get("curiosity_score", 0) > 0.5:
            traits.append("curious")
        if b.get("detail_level", 0) > 0.5:
            traits.append("detailed")
        if b.get("correction_rate", 0) > 0.1:
            traits.append("corrector")
        
        if traits:
            return f"{self.model['name']} is {' and '.join(traits)}"
        return f"{self.model['name']} is still being understood"
    
    def describe_user(self) -> str:
        """Describe user in natural language."""
        name = self.model["name"]
        interests = self.get_interests()
        behavior = self.get_behavior_summary()
        
        parts = [behavior]
        
        if interests:
            parts.append(f"Interested in: {', '.join(interests)}")
        
        return f"{name}: {'. '.join(parts)}"


# Singleton
_user_model: Optional[UserModel] = None


def get_user_model() -> UserModel:
    """Get user model singleton."""
    global _user_model
    if _user_model is None:
        _user_model = UserModel()
    return _user_model


if __name__ == "__main__":
    um = get_user_model()
    print(um.describe_user())
    print("Interests:", um.get_interests())
