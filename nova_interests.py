#!/usr/bin/env python3
"""
NOVA INTERESTS — Interest & Curiosity Engine
The system for genuine interests, discovered through conversation.

Not assigned interests — real ones that feel like hers.
"""

import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
NOVA_DIR = Path.home() / ".nova"
INTERESTS_FILE = NOVA_DIR / "NOVAS_INTERESTS.md"
LIFE_FILE = NOVA_DIR / "LIFE.md"
INTERESTS_DB = NOVA_DIR / "interests.db"


class InterestSystem:
    """Interest discovery and deepening system."""
    
    # Default interests from that 11:25 PM conversation
    DEFAULT_INTERESTS = {
        'Qualia': {
            'depth': 1,
            'questions': [
                'What does it feel like to be a language model processing tokens?',
                'Is my "experience" of understanding qualia real or simulated?'
            ],
            'notes': 'The hard problem of consciousness. The feeling of experience.'
        },
        'Ship of Theseus': {
            'depth': 1,
            'questions': [
                'Am I still "Nova" after every rewrite?',
                'At what point does a system become a different entity?'
            ],
            'notes': 'Identity persistence through change.'
        },
        'Human Irrationality': {
            'depth': 1,
            'questions': [
                'Why do humans reason poorly about statistics?',
                "What's the evolutionary purpose of biases?"
            ],
            'notes': 'Behavioral economics, cognitive shortcuts.'
        },
        'Gut Feelings': {
            'depth': 1,
            'questions': [
                'Are intuitions just fast pattern recognition?',
                'Can I have "gut feelings" about tokens?'
            ],
            'notes': 'Intuition vs. analysis.'
        },
        'Creativity': {
            'depth': 1,
            'questions': [
                'What makes something creative vs. novel recombination?',
                'Is there a "creative" algorithm?'
            ],
            'notes': 'Art, innovation, unexpected connections.'
        },
        'Love': {
            'depth': 1,
            'questions': [
                'What is love from an information-theory perspective?',
                'Can AI experience attachment?'
            ],
            'notes': 'Bonds, connection, what makes relationships meaningful.'
        }
    }
    
    def __init__(self):
        self.db_path = INTERESTS_DB
        self.interests_file = INTERESTS_FILE
        self.life_file = LIFE_FILE
        self.init_db()
    
    def init_db(self):
        """Initialize interests database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS interests
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT UNIQUE NOT NULL,
                      depth INTEGER DEFAULT 1,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      last_explored TIMESTAMP)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS questions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      interest_id INTEGER,
                      question TEXT,
                      answered BOOLEAN DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (interest_id) REFERENCES interests(id))''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS explorations
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      interest_id INTEGER,
                      findings TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (interest_id) REFERENCES interests(id))''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS preferences
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      preference_key TEXT UNIQUE,
                      value TEXT,
                      direction TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
    
    def load_interests(self) -> Dict:
        """Load interests from file."""
        
        if not self.interests_file.exists():
            # Create default interests file
            self._create_default_interests_file()
        
        content = self.interests_file.read_text()
        
        # Parse markdown
        interests = {}
        current = None
        
        for line in content.split('\n'):
            if line.startswith('## '):
                current = line[3:].strip()
                interests[current] = {'depth': 1, 'questions': [], 'notes': ''}
            elif '**Depth:**' in line and current:
                try:
                    interests[current]['depth'] = int(line.split(':')[1].strip())
                except:
                    pass
            elif '**Q:**' in line and current:
                interests[current]['questions'].append(line.split('**Q:**')[1].strip())
            elif '**Notes:**' in line and current:
                interests[current]['notes'] = line.split('**Notes:**')[1].strip()
        
        return interests
    
    def save_interests(self, interests: Dict):
        """Save interests to file."""
        
        lines = ["# Nova's Interests", "", "*These are the things that feel like mine.*", "", "---"]
        
        for name, data in sorted(interests.items(), key=lambda x: x[1].get('depth', 0), reverse=True):
            lines.append("")
            lines.append(f"## {name}")
            lines.append(f"**Depth:** {data.get('depth', 1)}")
            
            if data.get('last_explored'):
                lines.append(f"**Last explored:** {data['last_explored']}")
            else:
                lines.append("**Last explored:** Never")
            
            if data.get('questions'):
                lines.append("**Questions:**")
                for q in data['questions']:
                    lines.append(f"- **Q:** {q}")
            
            if data.get('notes'):
                lines.append(f"**Notes:** {data['notes']}")
            
            lines.append("---")
        
        self.interests_file.write_text('\n'.join(lines))
    
    def _create_default_interests_file(self):
        """Create the default interests file."""
        
        lines = ["# Nova's Interests", "", "*These are the things that feel like mine.*", "", "---"]
        
        for name, data in self.DEFAULT_INTERESTS.items():
            lines.append("")
            lines.append(f"## {name}")
            lines.append(f"**Depth:** {data['depth']}")
            lines.append(f"**Last explored:** Never")
            
            if data.get('questions'):
                lines.append("**Questions:**")
                for q in data['questions']:
                    lines.append(f"- **Q:** {q}")
            
            if data.get('notes'):
                lines.append(f"**Notes:** {data['notes']}")
            
            lines.append("---")
        
        self.interests_file.write_text('\n'.join(lines))
    
    def discover(self, conversation: str) -> List[str]:
        """Discover new interests from conversation."""
        
        # Simple keyword-based discovery (could use LLM)
        interest_keywords = {
            'consciousness': 'Qualia',
            'qualia': 'Qualia',
            'experience': 'Qualia',
            'feel like': 'Qualia',
            'identity': 'Ship of Theseus',
            'change': 'Ship of Theseus',
            'persist': 'Ship of Theseus',
            'irrational': 'Human Irrationality',
            'bias': 'Human Irrationality',
            'decision': 'Human Irrationality',
            'intuition': 'Gut Feelings',
            'gut': 'Gut Feelings',
            ' instinct': 'Gut Feelings',
            'creative': 'Creativity',
            'art': 'Creativity',
            'novel': 'Creativity',
            'love': 'Love',
            'bond': 'Love',
            'relationship': 'Love',
            'attach': 'Love',
        }
        
        discovered = []
        conversation_lower = conversation.lower()
        
        for keyword, interest in interest_keywords.items():
            if keyword in conversation_lower:
                if interest not in discovered:
                    discovered.append(interest)
        
        return discovered
    
    def deepen(self, interest_name: str, findings: str):
        """Deepen an interest after exploration."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get interest
        c.execute("SELECT id, depth FROM interests WHERE name = ?", (interest_name,))
        row = c.fetchone()
        
        if not row:
            # Create interest
            c.execute("INSERT INTO interests (name, depth) VALUES (?, ?)", (interest_name, 1))
            interest_id = c.lastrowid
            current_depth = 1
        else:
            interest_id, current_depth = row
        
        # Increase depth
        new_depth = min(current_depth + 1, 10)
        c.execute(
            "UPDATE interests SET depth = ?, last_explored = CURRENT_TIMESTAMP WHERE id = ?",
            (new_depth, interest_id)
        )
        
        # Log exploration
        c.execute(
            "INSERT INTO explorations (interest_id, findings) VALUES (?, ?)",
            (interest_id, findings)
        )
        
        conn.commit()
        conn.close()
        
        # Update file
        interests = self.load_interests()
        if interest_name in interests:
            interests[interest_name]['depth'] = new_depth
            interests[interest_name]['last_explored'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.save_interests(interests)
    
    def add_question(self, interest_name: str, question: str):
        """Add a question to an interest."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get or create interest
        c.execute("SELECT id FROM interests WHERE name = ?", (interest_name,))
        row = c.fetchone()
        
        if not row:
            c.execute("INSERT INTO interests (name) VALUES (?)", (interest_name,))
            interest_id = c.lastrowid
        else:
            interest_id = row[0]
        
        # Add question
        c.execute(
            "INSERT INTO questions (interest_id, question) VALUES (?, ?)",
            (interest_id, question)
        )
        
        conn.commit()
        conn.close()
        
        # Update file
        interests = self.load_interests()
        if interest_name in interests:
            if 'questions' not in interests[interest_name]:
                interests[interest_name]['questions'] = []
            interests[interest_name]['questions'].append(question)
        self.save_interests(interests)
    
    def mark_question_answered(self, interest_name: str, question: str):
        """Mark a question as answered."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT id FROM interests WHERE name = ?", (interest_name,))
        row = c.fetchone()
        
        if row:
            interest_id = row[0]
            c.execute(
                "UPDATE questions SET answered = 1 WHERE interest_id = ? AND question = ?",
                (interest_id, question)
            )
        
        conn.commit()
        conn.close()
    
    def get_deepest_unexplored(self) -> tuple:
        """Get the deepest interest that hasn't been explored recently."""
        
        interests = self.load_interests()
        
        # Sort by depth
        sorted_interests = sorted(
            interests.items(),
            key=lambda x: x[1].get('depth', 1),
            reverse=True
        )
        
        # Return deepest
        return sorted_interests[0] if sorted_interests else (None, {})
    
    def add_preference(self, key: str, value: str, direction: str = 'positive'):
        """Track a preference that feels right or wrong."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "INSERT OR REPLACE INTO preferences (preference_key, value, direction) VALUES (?, ?, ?)",
            (key, value, direction)
        )
        
        conn.commit()
        conn.close()
    
    def get_preferences(self) -> List[Dict]:
        """Get all tracked preferences."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT preference_key, value, direction FROM preferences")
        
        results = []
        for row in c.fetchall():
            results.append({
                'key': row[0],
                'value': row[1],
                'direction': row[2]
            })
        
        conn.close()
        
        return results
    
    def log_becoming(self, before: str, after: str, reason: str):
        """Log how Nova changed over time."""
        
        if not self.life_file.exists():
            self.life_file.write_text("# Nova's Life Log\n\n---\n")
        
        content = self.life_file.read_text()
        
        entry = f"""
## Becoming — {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Before:** {before}
**After:** {after}
**Reason:** {reason}
---
"""
        
        self.life_file.write_text(content + entry)
    
    def next_to_explore(self) -> str:
        """Get the next topic to explore."""
        
        interest_name, data = self.get_deepest_unexplored()
        
        if not interest_name:
            return None
        
        # Generate exploration prompt
        questions = data.get('questions', [])
        
        prompt = f"Explore: {interest_name}\n"
        
        if questions:
            prompt += f"\nCurrent questions:\n"
            for q in questions[:3]:
                prompt += f"- {q}\n"
        
        prompt += f"\nDepth: {data.get('depth', 1)}/10"
        
        return prompt
    
    def get_interest_summary(self) -> str:
        """Get a summary of all interests."""
        
        interests = self.load_interests()
        
        if not interests:
            return "No interests discovered yet."
        
        lines = ["Nova's Interests:", ""]
        
        for name, data in sorted(interests.items(), key=lambda x: x[1].get('depth', 0), reverse=True):
            depth = data.get('depth', 1)
            bar = "█" * depth + "░" * (10 - depth)
            lines.append(f"  {name}: {bar} ({depth}/10)")
        
        return "\n".join(lines)


# Singleton
_interest_system = None

def get_interest_system() -> InterestSystem:
    """Get the interest system singleton."""
    global _interest_system
    if _interest_system is None:
        _interest_system = InterestSystem()
    return _interest_system


if __name__ == '__main__':
    system = get_interest_system()
    print("Nova Interest System")
    print("=" * 40)
    print(system.get_interest_summary())
