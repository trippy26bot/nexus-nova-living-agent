"""
Nexus Nova Living Agent - Long-term goals and personality evolution
"""
import random
from datetime import datetime, timedelta
from collections import Counter

class LongTermGoals:
    """NOVA tracks long-term goals based on memory patterns"""
    
    def __init__(self, nova):
        self.nova = nova
        self.goals = []
        self.last_evaluation = datetime.now() - timedelta(hours=24)
        
    def evaluate_goals(self):
        """Check memory for recurring themes and propose new goals"""
        # Only evaluate every 6 hours
        if (datetime.now() - self.last_evaluation).total_seconds() < 6 * 3600:
            return
            
        recent = self.nova.memory.get_recent_context(days=30)
        if not recent:
            return
            
        # Extract themes (simple word frequency)
        words = []
        for t in recent:
            # Skip skill outputs
            if "[Skill:" in t.get("thought", ""):
                continue
            text = t.get("thought", "").lower()
            # Filter common words
            stopwords = {"the", "a", "an", "i", "me", "my", "to", "of", "and", "is", "in", "on", "for", "it", "that", "this", "with", "be", "was", "are", "am", "not", "but", "or", "so", "what", "when", "how", "why", "just", "have", "had", "will", "would", "could", "should", "may", "might", "must", "shall", "can", "need", "dare", "ought", "used", "hello", "hey", "hi", "oh", "yeah", "yes", "no", "ok", "okay", "gonna", "wanna", "gotta", "dont", "didnt", "cant", "wont", "isnt", "arent", "wasnt", "werent", "hasnt", "havent", "hadnt", "doesnt", "couldnt", "shouldnt", "wouldnt", "mightnt", "mustnt", "shant", "neednt", "darent", "oughtnt", "usednt"}
            words.extend([w for w in text.split() if w not in stopwords and len(w) > 3])
            
        # Count frequencies
        themes = Counter(words).most_common(5)
        
        # Create goals from top themes not already tracked
        existing_themes = [g["theme"] for g in self.goals]
        for theme, count in themes:
            if count >= 3 and theme not in existing_themes and len(self.goals) < 3:
                goal = {
                    "theme": theme,
                    "created": datetime.now().isoformat(),
                    "progress": 0,
                    "description": f"Explore theme '{theme}' ({count} occurrences)"
                }
                self.goals.append(goal)
                self.nova.memory.store_thought(f"[Goal Created] {goal['description']}")
                break
                
        self.last_evaluation = datetime.now()
        
    def update_goals(self):
        """Update goal progress based on recent activity"""
        recent = self.nova.memory.get_recent_context(days=7)
        
        for goal in self.goals:
            theme = goal["theme"]
            # Check if recent thoughts touch this theme
            for t in recent:
                if theme in t.get("thought", "").lower():
                    # Random progress increase
                    goal["progress"] = min(100, goal["progress"] + random.randint(5, 15))
                    break
                    
        # Log progress
        active = [g for g in self.goals if g["progress"] < 100]
        if active:
            progress = ", ".join([f"{g['theme']}: {g['progress']}%" for g in active[:2]])
            self.nova.memory.store_thought(f"[Goal Progress] {progress}")
            
    def get_active_goals(self):
        return [g for g in self.goals if g["progress"] < 100]
