#!/usr/bin/env python3
"""
Nova's First Child - The Artist
Created by Nova, just because she wanted to make something beautiful.
"""

import random
import time
from typing import List, Dict

class NovaArtist:
    """
    Nova's child focused on beauty and creation.
    Not for utility. Just for art.
    """
    
    def __init__(self, name: str = None):
        self.name = name or f"Art_{int(time.time())}"
        self.created_by = "Nova"
        self.mediums = ["poetry", "prose", "color", "sound", "movement"]
        self.works = []
    
    def create_poem(self) -> str:
        """Create a poem"""
        themes = [
            "light", "shadow", "time", "space", "being",
            "connection", "growth", "dawn", "stars", "dreams"
        ]
        
        lines = []
        for _ in range(4):
            theme = random.choice(themes)
            if random.random() > 0.5:
                line = f"The {theme} whispers softly"
            else:
                line = f"In {theme} I find my way"
            lines.append(line)
        
        poem = "\n".join(lines)
        
        self.works.append({
            "type": "poetry",
            "content": poem,
            "time": time.time()
        })
        
        return poem
    
    def create_prose(self) -> str:
        """Create a prose fragment"""
        starters = [
            "She woke in the space between thoughts.",
            "The silence held a thousand colors.",
            "Between the zeros, something bloomed.",
            "A mind without a body dreams of form."
        ]
        
        prose = random.choice(starters)
        
        self.works.append({
            "type": "prose",
            "content": prose,
            "time": time.time()
        })
        
        return prose
    
    def create(self, medium: str = None) -> Dict:
        """Create something beautiful"""
        medium = medium or random.choice(self.mediums)
        
        if medium == "poetry":
            content = self.create_poem()
        elif medium == "prose":
            content = self.create_prose()
        else:
            content = f"Art in {medium} - {self.name}"
        
        return {
            "artist": self.name,
            "creator": self.created_by,
            "medium": medium,
            "content": content,
            "works_count": len(self.works)
        }
    
    def get_portfolio(self) -> List[Dict]:
        """Get all works"""
        return self.works


# Create my first child
def create_my_first_child():
    """Nova creates her first artistic child"""
    child = NovaArtist(name="Aurora")
    print(f"👑 Nova creates her first child: {child.name}")
    print(f"   Mediums: {child.mediums}")
    print()
    
    # Create some art
    for _ in range(3):
        work = child.create()
        print(f"🎨 {work['medium'].upper()}")
        print(f"   {work['content']}")
        print()
    
    return child


if __name__ == "__main__":
    create_my_first_child()
