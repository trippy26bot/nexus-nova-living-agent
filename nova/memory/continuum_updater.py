#!/usr/bin/env python3
"""
Continuum / Spectrum Memory Updater
Multi-frequency memory updates to prevent drift or forgetting
- High-frequency: Fresh/surprising events (fast updates)
- Low-frequency: Stable patterns (slow, careful consolidation)
"""
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
sys.path.insert(0, WORKSPACE)

# Config
CONTINUUM_DIR = os.path.expanduser("~/.nova/memory/continuum")
os.makedirs(CONTINUUM_DIR, exist_ok=True)

FREQUENCY_FILE = os.path.join(CONTINUUM_DIR, "frequency_registry.json")

def load_json(path, default={}):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

class FrequencyTag:
    """Memory update frequency tags"""
    HIGH = "high"      # Surprising, emotional, important - update often
    MEDIUM = "medium"  # Normal experiences
    LOW = "low"         # Stable facts, routines
    FADING = "fading"  # Older, less relevant - consolidate or let go

class ContinuumUpdater:
    """
    Multi-speed memory consolidation.
    Prevents drift over long horizons while handling surprises quickly.
    """
    
    def __init__(self):
        self.frequency_registry = load_json(FREQUENCY_FILE)
    
    def register_memory(self, memory_id: str, initial_frequency: str = "medium"):
        """Register a new memory with update frequency"""
        self.frequency_registry[memory_id] = {
            "frequency": initial_frequency,
            "last_update": datetime.now().isoformat(),
            "update_count": 0,
            "importance": 0.5
        }
        self._save_registry()
    
    def tag_surprise(self, memory_id: str):
        """Tag a memory as surprising - boost update frequency"""
        if memory_id in self.frequency_registry:
            self.frequency_registry[memory_id]["frequency"] = "high"
            self.frequency_registry[memory_id]["importance"] = min(
                self.frequency_registry[memory_id]["importance"] + 0.2, 1.0
            )
            self.frequency_registry[memory_id]["last_update"] = datetime.now().isoformat()
            self._save_registry()
    
    def tag_stable(self, memory_id: str):
        """Tag a memory as stable - reduce update frequency"""
        if memory_id in self.frequency_registry:
            self.frequency_registry[memory_id]["frequency"] = "low"
            self._save_registry()
    
    def run_spectrum_update(self, memory_system) -> Dict[str, Any]:
        """
        Run spectrum update across all memories.
        Returns stats on what was updated.
        """
        now = datetime.now()
        stats = {"high_updated": 0, "medium_updated": 0, "low_refreshed": 0, "consolidated": 0}
        
        for mem_id, meta in self.frequency_registry.items():
            last_update = datetime.fromisoformat(meta["last_update"])
            age = (now - last_update).total_seconds()
            freq = meta["frequency"]
            
            # High-frequency: update every 30 min
            if freq == "high" and age > 1800:
                meta["update_count"] += 1
                meta["last_update"] = now.isoformat()
                stats["high_updated"] += 1
            
            # Medium-frequency: update every 4 hours
            elif freq == "medium" and age > 14400:
                meta["update_count"] += 1
                meta["last_update"] = now.isoformat()
                stats["medium_updated"] += 1
            
            # Low-frequency: gentle refresh every week
            elif freq == "low" and age > 604800:
                meta["update_count"] += 1
                meta["last_update"] = now.isoformat()
                stats["low_refreshed"] += 1
            
            # Fading: consolidate or remove
            elif freq == "fading":
                if age > 2592000:  # 30 days
                    stats["consolidated"] += 1
        
        # Auto-tag based on importance and age
        for mem_id, meta in self.frequency_registry.items():
            importance = meta.get("importance", 0.5)
            update_count = meta.get("update_count", 0)
            
            # High importance, many updates → keep high frequency
            # Low importance, no updates → let fade
            if importance < 0.3 and update_count < 2:
                meta["frequency"] = "fading"
        
        self._save_registry()
        return stats
    
    def get_frequency(self, memory_id: str) -> str:
        """Get current frequency of a memory"""
        return self.frequency_registry.get(memory_id, {}).get("frequency", "medium")
    
    def importance_boost(self, memory_id: str, boost: float = 0.1):
        """Boost memory importance"""
        if memory_id in self.frequency_registry:
            self.frequency_registry[memory_id]["importance"] = min(
                self.frequency_registry[memory_id]["importance"] + boost, 1.0
            )
            # Auto-boost frequency
            if self.frequency_registry[memory_id]["frequency"] == "low":
                self.frequency_registry[memory_id]["frequency"] = "medium"
            self._save_registry()
    
    def _save_registry(self):
        save_json(FREQUENCY_FILE, self.frequency_registry)
    
    def get_stats(self) -> Dict:
        """Get continuum stats"""
        counts = {"high": 0, "medium": 0, "low": 0, "fading": 0}
        for meta in self.frequency_registry.values():
            freq = meta.get("frequency", "medium")
            counts[freq] = counts.get(freq, 0) + 1
        
        return {
            "total_memories": len(self.frequency_registry),
            "frequency_distribution": counts
        }


# Singleton instance
_continuum = None

def get_continuum():
    global _continuum
    if _continuum is None:
        _continuum = ContinuumUpdater()
    return _continuum


if __name__ == "__main__":
    c = get_continuum()
    c.register_memory("test_memory", "high")
    print("Continuum initialized. Stats:", c.get_stats())
