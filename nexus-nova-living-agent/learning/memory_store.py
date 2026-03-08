"""
Memory Store - Persistent brain memory
"""
import json
from pathlib import Path

MEMORY_FILE = Path.home() / ".nova/learning/brain_memory.json"

class MemoryStore:
    def __init__(self):
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not MEMORY_FILE.exists():
            self.save({})
    
    def load(self):
        with open(MEMORY_FILE) as f:
            return json.load(f)
    
    def save(self, data):
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
    
    def get(self, key, default=None):
        data = self.load()
        return data.get(key, default)
    
    def set(self, key, value):
        data = self.load()
        data[key] = value
        self.save(data)
    
    def update(self, updates):
        data = self.load()
        data.update(updates)
        self.save(data)
