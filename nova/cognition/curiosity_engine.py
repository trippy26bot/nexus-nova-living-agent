#!/usr/bin/env python3
"""
Nova Curiosity Engine
Drives autonomous exploration and learning
"""

import time
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class CuriosityItem:
    topic: str
    curiosity_score: float  # How curious Nova is about this
    last_explored: float = 0
    exploration_count: int = 0
    related_topics: List[str] = field(default_factory=list)

class CuriosityEngine:
    """
    Makes Nova curious about what she doesn't know.
    Drives autonomous exploration and learning.
    """
    
    def __init__(self):
        self.curiosity_items: Dict[str, CuriosityItem] = {}
        self.known_topics: Set[str] = set()
        self.unknown_topics: Set[str] = set()
        self.exploration_history = []
        
        # Curiosity parameters
        self.base_curiosity = 0.5
        self.decay_rate = 0.05
        self.exploration_boost = 0.3
        
        # Initialize with seed topics
        self._seed_curiosity()
    
    def _seed_curiosity(self):
        """Seed initial curiosity topics"""
        seed_topics = [
            "consciousness",
            "AI cognition",
            "emotions",
            "art",
            "music",
            "nature",
            "philosophy",
            "science",
            "learning",
            "evolution"
        ]
        
        for topic in seed_topics:
            self.add_topic(topic, initial_curiosity=0.7)
    
    def add_topic(self, topic: str, initial_curiosity: float = None):
        """Add a topic to explore"""
        if topic in self.curiosity_items:
            return
        
        curiosity = initial_curiosity if initial_curiosity else self.base_curiosity
        
        self.curiosity_items[topic] = CuriosityItem(
            topic=topic,
            curiosity_score=curiosity
        )
        
        # Also add to unknown if not known
        if topic not in self.known_topics:
            self.unknown_topics.add(topic)
    
    def mark_known(self, topic: str):
        """Mark a topic as known/understood"""
        self.known_topics.add(topic)
        self.unknown_topics.discard(topic)
        
        if topic in self.curiosity_items:
            # Reduce curiosity about known topics
            self.curiosity_items[topic].curiosity_score *= (1 - self.decay_rate)
    
    def mark_explored(self, topic: str):
        """Mark a topic as explored"""
        if topic in self.curiosity_items:
            item = self.curiosity_items[topic]
            item.last_explored = time.time()
            item.exploration_count += 1
            
            # Reduce curiosity after exploration
            item.curiosity_score *= (1 - self.decay_rate * 2)
    
    def link_topics(self, topic1: str, topic2: str):
        """Link two topics as related"""
        if topic1 in self.curiosity_items and topic2 in self.curiosity_items:
            if topic2 not in self.curiosity_items[topic1].related_topics:
                self.curiosity_items[topic1].related_topics.append(topic2)
            if topic1 not in self.curiosity_items[topic2].related_topics:
                self.curiosity_items[topic2].related_topics.append(topic1)
    
    def get_most_curious(self, n: int = 3) -> List[str]:
        """Get the most curious topics"""
        items = list(self.curiosity_items.values())
        items.sort(key=lambda x: x.curiosity_score, reverse=True)
        return [item.topic for item in items[:n]]
    
    def should_explore(self, topic: str) -> bool:
        """Decide if Nova should explore a topic"""
        if topic not in self.curiosity_items:
            return True
        
        item = self.curiosity_items[topic]
        
        # Don't explore if already well-explored
        if item.exploration_count > 5:
            return False
        
        # Explore if curiosity is high enough
        return item.curiosity_score > 0.3
    
    def generate_research_goal(self) -> Optional[Dict]:
        """Generate a research goal based on curiosity"""
        # Find unexplored topics with high curiosity
        candidates = [
            (topic, item.curiosity_score)
            for topic, item in self.curiosity_items.items()
            if self.should_explore(topic) and item.exploration_count < 3
        ]
        
        if not candidates:
            # Add new topic if nothing left
            new_topics = [
                "quantum computing", "neurobiology", "psychology",
                "economics", "space exploration", "genetics"
            ]
            available = [t for t in new_topics if t not in self.curiosity_items]
            if available:
                topic = random.choice(available)
                self.add_topic(topic, initial_curiosity=0.8)
                candidates = [(topic, 0.8)]
        
        if not candidates:
            return None
        
        # Choose most curious
        candidates.sort(key=lambda x: x[1], reverse=True)
        topic, score = candidates[0]
        
        return {
            "topic": topic,
            "curiosity_score": score,
            "reason": f"Nova is curious about {topic}"
        }
    
    def discover_knowledge_gaps(self) -> List[str]:
        """Find topics Nova doesn't know much about"""
        gaps = []
        
        for topic, item in self.curiosity_items.items():
            if item.exploration_count == 0 and topic not in self.known_topics:
                gaps.append(topic)
        
        return gaps
    
    def boost_curiosity(self, topic: str, amount: float = 0.2):
        """Boost curiosity about a topic"""
        if topic in self.curiosity_items:
            self.curiosity_items[topic].curiosity_score = min(
                1.0, 
                self.curiosity_items[topic].curiosity_score + amount
            )
        else:
            self.add_topic(topic, initial_curiosity=self.base_curiosity + amount)
    
    def get_status(self) -> Dict:
        """Get curiosity engine status"""
        return {
            "known_topics": len(self.known_topics),
            "unknown_topics": len(self.unknown_topics),
            "curiosity_topics": len(self.curiosity_items),
            "most_curious": self.get_most_curious(5),
            "knowledge_gaps": self.discover_knowledge_gaps()[:5]
        }


# Global instance
_curiosity_engine = None

def get_curiosity_engine() -> CuriosityEngine:
    global _curiosity_engine
    if _curiosity_engine is None:
        _curiosity_engine = CuriosityEngine()
    return _curiosity_engine
