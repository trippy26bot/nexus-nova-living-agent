"""
NOVA Persistent Memory System
Multiple memory types for a living agent
"""
import json
from pathlib import Path
from datetime import datetime


class ShortTermMemory:
    """Fast access memory for current context"""
    
    def __init__(self):
        self.data = {}
        self.max_items = 100
    
    def store(self, key, value):
        self.data[key] = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Keep memory bounded
        if len(self.data) > self.max_items:
            # Remove oldest
            oldest = min(self.data.items(), key=lambda x: x[1]["timestamp"])
            del self.data[oldest[0]]
    
    def retrieve(self, key, default=None):
        return self.data.get(key, {}).get("value", default)
    
    def get_recent(self, limit=10):
        items = sorted(self.data.items(), key=lambda x: x[1]["timestamp"], reverse=True)
        return [{"key": k, "value": v["value"]} for k, v in items[:limit]]
    
    def clear(self):
        self.data = {}


class LongTermMemory:
    """Persistent storage for important memories"""
    
    def __init__(self):
        self.memory_file = Path.home() / ".nova/memory/long_term.json"
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.memory_file.exists():
            self.save([])
    
    def save(self, data):
        with open(self.memory_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        with open(self.memory_file) as f:
            return json.load(f)
    
    def store(self, memory_type, content, importance=0.5):
        """Store a long-term memory"""
        memories = self.load()
        
        memory = {
            "type": memory_type,
            "content": content,
            "importance": importance,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        memories.append(memory)
        
        # Keep bounded - remove lowest importance if too many
        if len(memories) > 1000:
            memories.sort(key=lambda x: x.get("importance", 0), reverse=True)
            memories = memories[:1000]
        
        self.save(memories)
        return memory
    
    def recall(self, query=None, memory_type=None, limit=10):
        """Recall memories"""
        memories = self.load()
        
        # Filter
        if memory_type:
            memories = [m for m in memories if m.get("type") == memory_type]
        
        # Sort by importance and time
        memories.sort(key=lambda x: (x.get("importance", 0), x.get("timestamp", "")), reverse=True)
        
        return memories[:limit]
    
    def get_stats(self):
        """Get memory statistics"""
        memories = self.load()
        
        by_type = {}
        for m in memories:
            t = m.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
        
        return {
            "total": len(memories),
            "by_type": by_type
        }


class EpisodicMemory:
    """Stores complete experiences / episodes"""
    
    def __init__(self):
        self.episode_file = Path.home() / ".nova/memory/episodes.json"
        self.episode_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.episode_file.exists():
            self.save([])
    
    def save(self, data):
        with open(self.episode_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        with open(self.episode_file) as f:
            return json.load(f)
    
    def record_episode(self, context, decision, result):
        """Record a complete episode"""
        episodes = self.load()
        
        episode = {
            "context": context,
            "decision": decision,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        episodes.append(episode)
        
        # Keep last 500 episodes
        if len(episodes) > 500:
            episodes = episodes[-500:]
        
        self.save(episodes)
        return episode
    
    def get_recent_episodes(self, limit=10):
        episodes = self.load()
        return episodes[-limit:]
    
    def analyze_patterns(self):
        """Find patterns in episodes"""
        episodes = self.load()
        
        if len(episodes) < 5:
            return "Not enough episodes for pattern analysis"
        
        # Simple pattern: what decisions lead to positive results?
        positive_episodes = [e for e in episodes if e.get("result", {}).get("pnl", 0) > 0]
        
        if not positive_episodes:
            return "No positive episodes to analyze"
        
        # Return simple insight
        decisions = [e.get("decision", {}).get("action") for e in positive_episodes]
        
        return {
            "positive_episodes": len(positive_episodes),
            "total_episodes": len(episodes),
            "winning_decisions": Counter(decisions).most_common()
        }


class KnowledgeMemory:
    """Structured knowledge storage"""
    
    def __init__(self):
        self.knowledge_file = Path.home() / ".nova/memory/knowledge.json"
        self.knowledge_file.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.knowledge_file.exists():
            self.save({})
    
    def save(self, data):
        with open(self.knowledge_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        with open(self.knowledge_file) as f:
            return json.load(f)
    
    def learn(self, key, knowledge):
        """Store a knowledge fact"""
        knowledge_base = self.load()
        
        knowledge_base[key] = {
            "content": knowledge,
            "learned_at": datetime.utcnow().isoformat()
        }
        
        self.save(knowledge_base)
    
    def recall(self, key):
        """Recall a knowledge fact"""
        knowledge_base = self.load()
        return knowledge_base.get(key, {}).get("content")
    
    def get_all_knowledge(self):
        return self.load()


class NovaMemory:
    """Unified memory system for NOVA"""
    
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.episodes = EpisodicMemory()
        self.knowledge = KnowledgeMemory()
    
    def remember_short(self, key, default=None):
        return self.short_term.retrieve(key, default)
    
    def remember_long(self, query=None, memory_type=None):
        return self.long_term.recall(query, memory_type)
    
    def remember_episodes(self, limit=10):
        return self.episodes.get_recent_episodes(limit)
    
    def recall_knowledge(self, key):
        return self.knowledge.recall(key)
    
    def store_short(self, key, value):
        self.short_term.store(key, value)
    
    def store_long(self, memory_type, content, importance=0.5):
        return self.long_term.store(memory_type, content, importance)
    
    def store_episode(self, context, decision, result):
        return self.episodes.record_episode(context, decision, result)
    
    def learn(self, key, knowledge):
        self.knowledge.learn(key, knowledge)
    
    def get_status(self):
        """Get memory system status"""
        return {
            "short_term_items": len(self.short_term.data),
            "long_term_memories": self.long_term.get_stats(),
            "episodes_recorded": len(self.episodes.load()),
            "knowledge_items": len(self.knowledge.get_all_knowledge())
        }
    
    def reflect(self):
        """NOVA's reflection on her memories"""
        patterns = self.episodes.analyze_patterns()
        
        return {
            "patterns": patterns,
            "knowledge_count": len(self.knowledge.get_all_knowledge())
        }
