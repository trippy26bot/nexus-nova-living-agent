#!/usr/bin/env python3
"""
NOVA MEMORY — Three-Tier Memory System
Working + Episodic + Semantic memory with optional vector search.

Tier 1: Working memory — current context, immediately relevant
Tier 2: Episodic memory — specific experiences, events, conversations
Tier 3: Semantic memory — facts, knowledge, understanding
"""

import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import deque
import re

# Configuration
NOVA_DIR = Path.home() / ".nova"
MEMORY_DB = NOVA_DIR / "nova.db"
WORKING_MEMORY_MAX = 10  # Max items in working memory


class WorkingMemory:
    """Tier 1: Working memory — immediate context."""
    
    def __init__(self):
        self.items: deque = deque(maxlen=WORKING_MEMORY_MAX)
    
    def add(self, item: str, metadata: Dict = None):
        """Add an item to working memory."""
        self.items.append({
            'content': item,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        })
    
    def get_recent(self, n: int = 5) -> List[Dict]:
        """Get n most recent items."""
        return list(self.items)[-n:]
    
    def get_context(self) -> str:
        """Get context string from working memory."""
        items = self.get_recent(3)
        return "\n".join([
            f"- {item['content'][:100]}"
            for item in items
        ])
    
    def clear(self):
        """Clear working memory."""
        self.items.clear()
    
    def __len__(self):
        return len(self.items)


class EpisodicMemory:
    """Tier 2: Episodic memory — events and experiences."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or MEMORY_DB
        self.ensure_table()
    
    def ensure_table(self):
        """Ensure episodic memory table exists."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if old schema exists
        c.execute("PRAGMA table_info(episodic_memory)")
        columns = [row[1] for row in c.fetchall()]
        
        # Create table with full schema
        c.execute('''CREATE TABLE IF NOT EXISTS episodic_memory
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      event TEXT NOT NULL,
                      context TEXT,
                      emotion TEXT,
                      importance INTEGER DEFAULT 5,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      tags TEXT,
                      focus TEXT,
                      scores TEXT,
                      state TEXT,
                      source_event_id INTEGER,
                      priority_score REAL DEFAULT 0.0)''')
        
        # Add priority_score column if not exists (migration)
        if 'priority_score' not in columns:
            try:
                c.execute("ALTER TABLE episodic_memory ADD COLUMN priority_score REAL DEFAULT 0.0")
            except:
                pass
        
        conn.commit()
        conn.close()
    
    def store(self, event: str, context: str = None, emotion: str = None, 
              importance: int = 5, tags: List[str] = None, focus: str = None,
              scores: Dict = None, state: str = "stored", source_event_id: int = None):
        """Store an episodic memory with full metadata."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        tags_json = json.dumps(tags or [])
        scores_json = json.dumps(scores) if scores else None
        
        # Calculate priority score
        priority = self._calculate_priority(importance, scores, state)
        
        c.execute(
            """INSERT INTO episodic_memory 
               (event, context, emotion, importance, tags, focus, scores, state, source_event_id, priority_score)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (event, context, emotion, importance, tags_json, focus, scores_json, state, source_event_id, priority)
        )
        
        conn.commit()
        conn.close()
    
    def _calculate_priority(self, importance: int, scores: Dict = None, state: str = "stored") -> float:
        """Calculate priority score based on importance, scores, and state."""
        # Base from importance (1-10 -> 0-1)
        importance_score = importance / 10.0
        
        # State priority
        state_weights = {"accepted": 1.0, "stored_only": 0.6, "rejected": 0.2}
        state_score = state_weights.get(state, 0.5)
        
        # Composite score from evaluation
        composite_score = scores.get("composite", 0.5) if scores else 0.5
        
        # Weighted priority
        priority = (importance_score * 0.3) + (state_score * 0.4) + (composite_score * 0.3)
        
        return round(priority, 3)
    
    def retrieve(self, query: str = None, since: datetime = None, 
                 limit: int = 10, focus: str = None, min_priority: float = 0.0) -> List[Dict]:
        """Retrieve episodic memories with priority scoring.
        
        Prioritizes by:
        - Higher composite scores
        - Higher importance
        - Similar focus topics
        - Accepted state > stored_only > rejected
        """
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        conditions = []
        params = []
        
        if query:
            conditions.append("event LIKE ?")
            params.append(f"%{query}%")
        
        if since:
            conditions.append("created_at >= ?")
            params.append(since.isoformat())
        
        if focus:
            conditions.append("focus LIKE ?")
            params.append(f"%{focus}%")
        
        if min_priority > 0:
            conditions.append("priority_score >= ?")
            params.append(min_priority)
        
        where = " AND ".join(conditions) if conditions else "1=1"
        
        c.execute(
            f"""SELECT id, event, context, emotion, importance, created_at, tags, 
                       focus, scores, state, priority_score
                FROM episodic_memory
                WHERE {where}
                ORDER BY priority_score DESC, created_at DESC
                LIMIT ?""",
            params + [limit]
        )
        
        results = []
        for row in c.fetchall():
            scores = json.loads(row[8]) if row[8] else {}
            results.append({
                'id': row[0],
                'event': row[1],
                'context': row[2],
                'emotion': row[3],
                'importance': row[4],
                'created': row[5],
                'tags': json.loads(row[6] or '[]'),
                'focus': row[7],
                'scores': scores,
                'state': row[9],
                'priority_score': row[10]
            })
        
        conn.close()
        
        return results
    
    def get_timeline(self, days: int = 7) -> List[Dict]:
        """Get memory timeline for last n days."""
        
        since = datetime.now() - timedelta(days=days)
        return self.retrieve(since=since, limit=50)
    
    def search(self, keyword: str) -> List[Dict]:
        """Search memories by keyword."""
        return self.retrieve(query=keyword, limit=20)


class SemanticMemory:
    """Tier 3: Semantic memory — facts and knowledge."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or MEMORY_DB
        self.ensure_table()
    
    def ensure_table(self):
        """Ensure semantic memory table exists."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS semantic_memory
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      subject TEXT NOT NULL,
                      predicate TEXT NOT NULL,
                      object TEXT NOT NULL,
                      confidence REAL DEFAULT 1.0,
                      source TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      UNIQUE(subject, predicate, object))''')
        
        conn.commit()
        conn.close()
    
    def store(self, subject: str, predicate: str, object: str, 
              confidence: float = 1.0, source: str = None):
        """Store a semantic memory (fact)."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            """INSERT OR REPLACE INTO semantic_memory 
               (subject, predicate, object, confidence, source)
               VALUES (?, ?, ?, ?, ?)""",
            (subject, predicate, object, confidence, source)
        )
        
        conn.commit()
        conn.close()
    
    def retrieve(self, subject: str = None, predicate: str = None) -> List[Dict]:
        """Retrieve semantic memories."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        conditions = []
        params = []
        
        if subject:
            conditions.append("subject = ?")
            params.append(subject)
        
        if predicate:
            conditions.append("predicate = ?")
            params.append(predicate)
        
        where = " AND ".join(conditions) if conditions else "1=1"
        
        c.execute(
            f"""SELECT subject, predicate, object, confidence, source, created_at
                FROM semantic_memory
                WHERE {where}
                ORDER BY confidence DESC""",
            params
        )
        
        results = []
        for row in c.fetchall():
            results.append({
                'subject': row[0],
                'predicate': row[1],
                'object': row[2],
                'confidence': row[3],
                'source': row[4],
                'created': row[5]
            })
        
        conn.close()
        
        return results
    
    def get_facts_about(self, subject: str) -> List[Dict]:
        """Get all facts about a subject."""
        return self.retrieve(subject=subject)
    
    def extract_from_text(self, text: str) -> List[Dict]:
        """Extract potential facts from text using simple patterns."""
        
        facts = []
        
        # Pattern: "X is Y"
        pattern1 = re.compile(r'(\w+) is (a|an|the)? (\w+)', re.IGNORECASE)
        for match in pattern1.finditer(text):
            facts.append({
                'subject': match.group(1),
                'predicate': 'is',
                'object': match.group(3)
            })
        
        # Pattern: "X has Y"
        pattern2 = re.compile(r'(\w+) has (\w+)', re.IGNORECASE)
        for match in pattern2.finditer(text):
            facts.append({
                'subject': match.group(1),
                'predicate': 'has',
                'object': match.group(2)
            })
        
        return facts[:5]  # Limit


class MemoryCompressor:
    """Compresses memories via LLM with insight extraction."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or MEMORY_DB
    
    def compress_episodic(self, memories: List[Dict]) -> str:
        """Compress multiple episodic memories into summary."""
        
        if not memories:
            return "No memories to compress."
        
        # Format memories
        text = "Memories to compress:\n\n"
        for m in memories[:10]:
            text += f"- {m.get('event', '')} ({m.get('created', ''[:10])})\n"
            if m.get('context'):
                text += f"  Context: {m['context'][:100]}\n"
        
        # Use LLM to extract insights
        try:
            from nova import call_llm
            
            prompt = f"""Compress these memories into a brief summary of what happened and what matters:

{text}

Provide:
1. A 2-3 sentence summary
2. Key insights (bullet points)
3. Important facts to retain"""

            summary = call_llm(prompt)
            return summary
        
        except ImportError:
            return f"Summary of {len(memories)} memories (LLM not available)"
    
    def extract_insights(self, text: str) -> Dict:
        """Extract semantic insights from text."""
        
        try:
            from nova import call_llm
            
            prompt = f"""Extract key facts and insights from this text:

{text}

Return JSON:
{{
  "facts": ["fact 1", "fact 2"],
  "entities": ["person 1", "place 2"],
  "topics": ["topic 1", "topic 2"],
  "importance": 1-10,
  "insight": "main insight if any"
}}"""

            result = call_llm(prompt)
            
            # Try to parse as JSON
            try:
                return json.loads(result)
            except:
                return {"raw": result}
        
        except ImportError:
            return {"error": "LLM not available"}


class MemoryManager:
    """Unified memory manager across all tiers."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or MEMORY_DB
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory(db_path)
        self.semantic = SemanticMemory(db_path)
        self.compressor = MemoryCompressor(db_path)
    
    def remember(self, content: str, context: str = None, 
                 memory_type: str = 'episodic', importance: int = 5,
                 tags: List[str] = None):
        """Remember something."""
        
        # Always add to working memory
        self.working.add(content, {'context': context, 'importance': importance})
        
        if memory_type == 'episodic':
            self.episodic.store(content, context, importance=importance, tags=tags)
        elif memory_type == 'semantic':
            # Extract and store facts
            facts = self.semantic.extract_from_text(content)
            for fact in facts:
                self.semantic.store(
                    fact['subject'],
                    fact['predicate'],
                    fact['object'],
                    confidence=0.7
                )
    
    def recall(self, query: str = None, tier: str = 'all') -> Dict:
        """Recall from memory."""
        
        results = {}
        
        if tier in ['all', 'working']:
            results['working'] = self.working.get_recent()
        
        if tier in ['all', 'episodic']:
            results['episodic'] = self.episodic.retrieve(query=query)
        
        if tier in ['all', 'semantic']:
            results['semantic'] = self.semantic.retrieve(subject=query)
        
        return results
    
    def get_context(self, for_query: str = None) -> str:
        """Get context string for LLM prompts."""
        
        parts = []
        
        # Working memory
        working = self.working.get_recent(3)
        if working:
            parts.append("Recent context:")
            for w in working:
                parts.append(f"- {w['content'][:80]}")
        
        # Episodic
        episodic = self.episodic.retrieve(query=for_query, limit=3)
        if episodic:
            parts.append("\nRelevant memories:")
            for e in episodic[:3]:
                parts.append(f"- {e['event'][:80]}")
        
        # Semantic
        if for_query:
            semantic = self.semantic.retrieve(subject=for_query)
            if semantic:
                parts.append("\nKnown facts:")
                for s in semantic[:3]:
                    parts.append(f"- {s['subject']} {s['predicate']} {s['object']}")
        
        return "\n".join(parts)
    
    def get_user_profile(self) -> Dict:
        """Get extracted user profile from semantic memory."""
        
        facts = self.semantic.retrieve()
        
        profile = {
            'name': None,
            'preferences': [],
            'facts': []
        }
        
        for fact in facts:
            if fact['subject'].lower() == 'user' and fact['predicate'] == 'name':
                profile['name'] = fact['object']
            elif fact['predicate'] in ['prefers', 'likes']:
                profile['preferences'].append(f"{fact['subject']} {fact['predicate']} {fact['object']}")
            else:
                profile['facts'].append(f"{fact['subject']} {fact['predicate']} {fact['object']}")
        
        return profile


# Singleton
_memory_manager = None

def get_memory_manager() -> MemoryManager:
    """Get the memory manager singleton."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


if __name__ == '__main__':
    print("Nova Memory System")
    print("=" * 40)
    
    manager = get_memory_manager()
    
    # Test
    manager.remember("Met with Caine today", context="first meeting", importance=8)
    manager.remember("Caine likes AI", memory_type='semantic', importance=7)
    
    print("\nWorking memory:", len(manager.working.items), "items")
    print("\nUser profile:", manager.get_user_profile())
