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
    
    def prune_low_priority(self, min_priority: float = 0.2, keep_count: int = 100) -> int:
        """Remove low-priority memories beyond keep_count.
        
        Args:
            min_priority: Minimum priority to keep (default 0.2)
            keep_count: Maximum memories to keep (default 100)
        
        Returns:
            Number of memories pruned
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get count
        c.execute("SELECT COUNT(*) FROM episodic_memory")
        total = c.fetchone()[0]
        
        if total <= keep_count:
            conn.close()
            return 0
        
        # Get IDs to delete (lowest priority, beyond keep_count)
        c.execute("""
            SELECT id FROM episodic_memory 
            WHERE priority_score < ? 
            ORDER BY priority_score ASC, created_at ASC
            LIMIT ?
        """, (min_priority, total - keep_count))
        
        to_delete = [row[0] for row in c.fetchall()]
        
        if to_delete:
            placeholders = ','.join('?' * len(to_delete))
            c.execute(f"DELETE FROM episodic_memory WHERE id IN ({placeholders})", to_delete)
            conn.commit()
        
        conn.close()
        return len(to_delete)
    
    def archive_old(self, days: int = 90) -> int:
        """Archive memories older than specified days to separate storage.
        
        Args:
            days: Age threshold for archiving (default 90)
        
        Returns:
            Number of memories archived
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        cutoff = datetime.now() - timedelta(days=days)
        
        # Mark old accepted memories as archived
        c.execute("""
            UPDATE episodic_memory 
            SET state = 'archived'
            WHERE state = 'accepted' 
            AND created_at < ?
            AND priority_score < 0.5
        """, (cutoff.isoformat(),))
        
        deleted = c.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        stats = {}
        
        # Total
        c.execute("SELECT COUNT(*) FROM episodic_memory")
        stats['total'] = c.fetchone()[0]
        
        # By state
        c.execute("SELECT state, COUNT(*) FROM episodic_memory GROUP BY state")
        stats['by_state'] = {row[0]: row[1] for row in c.fetchall()}
        
        # Average priority
        c.execute("SELECT AVG(priority_score) FROM episodic_memory")
        stats['avg_priority'] = c.fetchone()[0] or 0
        
        # Oldest
        c.execute("SELECT MIN(created_at) FROM episodic_memory")
        stats['oldest'] = c.fetchone()[0]
        
        # Newest
        c.execute("SELECT MAX(created_at) FROM episodic_memory")
        stats['newest'] = c.fetchone()[0]
        
        conn.close()
        return stats


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


        return profile


class EmbeddingProvider:
    """Abstract embedding provider interface."""
    
    def __init__(self, provider: str = "openai"):
        self.provider = provider
    
    def embed(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text."""
        if self.provider == "openai":
            return self._openai_embed(text)
        elif self.provider == "anthropic":
            return self._anthropic_embed(text)
        elif self.provider == "local":
            return self._local_embed(text)
        else:
            return None
    
    def _openai_embed(self, text: str) -> Optional[List[float]]:
        """Generate embedding using OpenAI."""
        try:
            import os
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception:
            return None
    
    def _anthropic_embed(self, text: str) -> Optional[List[float]]:
        """Generate embedding using Anthropic (via API)."""
        # Anthropic doesn't have native embeddings yet, fallback
        return None
    
    def _local_embed(self, text: str) -> Optional[List[float]]:
        """Generate embedding using local model."""
        # Placeholder for local embedding (e.g., sentence-transformers)
        return None


class VectorStore:
    """Vector storage for semantic search."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or MEMORY_DB
        self.ensure_table()
        self.embedding_provider = EmbeddingProvider()
    
    def ensure_table(self):
        """Ensure vector table exists."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Memory vectors (linked to episodic_memory)
        c.execute('''CREATE TABLE IF NOT EXISTS memory_vectors
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      memory_id INTEGER NOT NULL,
                      memory_type TEXT NOT NULL,
                      vector BLOB NOT NULL,
                      text_preview TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(memory_id) REFERENCES episodic_memory(id))''')
        
        conn.commit()
        conn.close()
    
    def store_vector(self, memory_id: int, memory_type: str, text: str) -> bool:
        """Generate and store vector for a memory."""
        vector = self.embedding_provider.embed(text)
        if not vector:
            return False

        vector_blob = json.dumps(vector).encode("utf-8")
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if exists
        c.execute("SELECT id FROM memory_vectors WHERE memory_id = ? AND memory_type = ?", 
                  (memory_id, memory_type))
        exists = c.fetchone()
        
        if exists:
            c.execute("""
                UPDATE memory_vectors 
                SET vector = ?, text_preview = ?, created_at = CURRENT_TIMESTAMP
                WHERE memory_id = ? AND memory_type = ?
            """, (vector_blob, text[:200], memory_id, memory_type))
        else:
            c.execute("""
                INSERT INTO memory_vectors (memory_id, memory_type, vector, text_preview)
                VALUES (?, ?, ?, ?)
            """, (memory_id, memory_type, vector_blob, text[:200]))
        
        conn.commit()
        conn.close()
        return True
    
    def search_similar(self, query: str, memory_type: str = None, limit: int = 5) -> List[Dict]:
        """Search for similar memories using vector similarity."""
        query_vector = self.embedding_provider.embed(query)
        if not query_vector:
            return []  # Fallback to keyword
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get all vectors
        if memory_type:
            c.execute("""
                SELECT id, memory_id, memory_type, vector, text_preview 
                FROM memory_vectors 
                WHERE memory_type = ?
            """, (memory_type,))
        else:
            c.execute("""
                SELECT id, memory_id, memory_type, vector, text_preview 
                FROM memory_vectors
            """)
        
        results = []
        for row in c.fetchall():
            try:
                raw = row[3]
                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8")
                stored_vector = json.loads(raw)
                if not isinstance(stored_vector, list):
                    continue
                similarity = self._cosine_similarity(query_vector, stored_vector)
                results.append({
                    'id': row[0],
                    'memory_id': row[1],
                    'memory_type': row[2],
                    'text_preview': row[4],
                    'similarity': similarity
                })
            except Exception:
                continue
        
        conn.close()
        
        # Sort by similarity and return top results
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math
        
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(x * x for x in b))
        
        if mag_a == 0 or mag_b == 0:
            return 0.0
        
        return dot / (mag_a * mag_b)
    
    def is_available(self) -> bool:
        """Check if embedding provider is available."""
        test = self.embedding_provider.embed("test")
        return test is not None


class SemanticRetrieval:
    """Combined semantic + keyword retrieval."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or MEMORY_DB
        self.vector_store = VectorStore(db_path)
        self.episodic = EpisodicMemory(db_path)
    
    def retrieve(self, query: str, limit: int = 5) -> Dict:
        """Retrieve memories using semantic search with keyword fallback.
        
        Returns:
            {
                'method': 'semantic' | 'keyword',
                'results': [...],
                'fallback': True if keyword was used
            }
        """
        # Try semantic first
        if self.vector_store.is_available():
            results = self.vector_store.search_similar(query, memory_type='episodic', limit=limit)
            
            if results:
                # Enrich with full memory data
                enriched = []
                for r in results:
                    mem = self.episodic.retrieve(limit=100)
                    for m in mem:
                        if m['id'] == r['memory_id']:
                            m['similarity'] = r['similarity']
                            enriched.append(m)
                            break
                
                return {
                    'method': 'semantic',
                    'results': enriched,
                    'fallback': False
                }
        
        # Fallback to keyword search
        keyword_results = self.episodic.retrieve(query=query, limit=limit)
        
        return {
            'method': 'keyword',
            'results': keyword_results,
            'fallback': True
        }


class ReflectionEngine:
    """Engine for analyzing patterns and extracting insights."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or MEMORY_DB
        self.ensure_tables()
    
    def ensure_tables(self):
        """Ensure reflection tables exist."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS insights
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      insight TEXT NOT NULL,
                      pattern TEXT,
                      confidence REAL DEFAULT 0.5,
                      source_type TEXT,
                      source_ids TEXT,
                      promoted INTEGER DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      last_used TIMESTAMP)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS open_questions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      question TEXT NOT NULL,
                      status TEXT DEFAULT 'active',
                      context TEXT,
                      answer TEXT,
                      answered_at TIMESTAMP,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
    
    def add_insight(self, insight: str, pattern: str = None, confidence: float = 0.5,
                   source_type: str = 'reflection', source_ids: str = None) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO insights (insight, pattern, confidence, source_type, source_ids)
                   VALUES (?, ?, ?, ?, ?)""",
                  (insight, pattern, confidence, source_type, source_ids))
        insight_id = c.lastrowid
        conn.commit()
        conn.close()
        return insight_id
    
    def promote_insight(self, insight_id: int, confidence: float) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""UPDATE insights SET promoted = 1, confidence = ?, last_used = CURRENT_TIMESTAMP
                   WHERE id = ?""", (confidence, insight_id))
        updated = c.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    def get_insights(self, promoted_only: bool = False, limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if promoted_only:
            c.execute("""SELECT id, insight, pattern, confidence, created_at 
                       FROM insights WHERE promoted = 1 ORDER BY confidence DESC LIMIT ?""", (limit,))
        else:
            c.execute("""SELECT id, insight, pattern, confidence, created_at 
                       FROM insights ORDER BY confidence DESC LIMIT ?""", (limit,))
        results = [{'id': r[0], 'insight': r[1], 'pattern': r[2], 
                   'confidence': r[3], 'created': r[4]} for r in c.fetchall()]
        conn.close()
        return results
    
    def add_question(self, question: str, context: str = None) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO open_questions (question, context, status)
                   VALUES (?, ?, 'active')""", (question, context))
        q_id = c.lastrowid
        conn.commit()
        conn.close()
        return q_id
    
    def answer_question(self, question_id: int, answer: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""UPDATE open_questions 
                   SET status = 'answered', answer = ?, answered_at = CURRENT_TIMESTAMP
                   WHERE id = ?""", (answer, question_id))
        updated = c.rowcount > 0
        conn.commit()
        conn.close()
        return updated
    
    def get_questions(self, status: str = 'active', limit: int = 10) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""SELECT id, question, status, context, answer, created_at
                   FROM open_questions WHERE status = ? ORDER BY created_at DESC LIMIT ?""",
                 (status, limit))
        results = [{'id': r[0], 'question': r[1], 'status': r[2], 
                   'context': r[3], 'answer': r[4], 'created': r[5]} for r in c.fetchall()]
        conn.close()
        return results
    
    def extract_patterns(self, memories: List[Dict]) -> List[str]:
        topics = {}
        for mem in memories:
            text = mem.get('event', '') + ' ' + mem.get('context', '')
            words = text.lower().split()
            for i in range(len(words) - 1):
                phrase = f"{words[i]} {words[i+1]}"
                topics[phrase] = topics.get(phrase, 0) + 1
        sorted_patterns = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        return [p[0] for p in sorted_patterns[:5]]


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
