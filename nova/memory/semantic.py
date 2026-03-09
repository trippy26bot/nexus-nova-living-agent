#!/usr/bin/env python3
"""
Semantic Memory - Stores knowledge and facts
"""

import json
from datetime import datetime
from pathlib import Path

class SemanticMemory:
    """Stores structured knowledge and facts"""
    
    def __init__(self, storage_path=None):
        if storage_path is None:
            storage_path = Path.home() / ".openclaw" / "memory" / "semantic.json"
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.knowledge = self._load()
    
    def _load(self):
        if self.storage_path.exists():
            with open(self.storage_path) as f:
                return json.load(f)
        return {}
    
    def _save(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def store(self, key: str, value, metadata: dict = None):
        """Store a knowledge piece"""
        self.knowledge[key] = {
            "value": value,
            "metadata": metadata or {},
            "updated": datetime.now().isoformat()
        }
        self._save()
        return key
    
    def retrieve(self, key: str, default=None):
        """Retrieve knowledge"""
        return self.knowledge.get(key, {}).get("value", default)
    
    def search(self, keyword: str):
        """Search knowledge by keyword"""
        results = {}
        for key, data in self.knowledge.items():
            if keyword.lower() in key.lower():
                results[key] = data
            elif keyword.lower() in str(data.get("value", "")).lower():
                results[key] = data
        return results
    
    def get_all(self):
        """Get all knowledge"""
        return self.knowledge
    
    def delete(self, key: str):
        """Delete knowledge"""
        if key in self.knowledge:
            del self.knowledge[key]
            self._save()
            return True
        return False
    
    def count(self):
        return len(self.knowledge)


# Global instance
_semantic = SemanticMemory()

def get_semantic():
    return _semantic
