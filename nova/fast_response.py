#!/usr/bin/env python3
"""
Fast Response Layer - Instant responses while deep thinking continues
"""

import asyncio
from collections import OrderedDict
from datetime import datetime

# LRU cache for responses - max 512 entries
MAX_CACHE_SIZE = 512

class FastResponse:
    """Send instant responses while deep brains continue processing."""
    
    def __init__(self):
        self.cache = OrderedDict()  # Use OrderedDict for LRU behavior
        self.fast_mode = True
        self._cache_hits = 0
        self._cache_misses = 0
    
    def _get_cached(self, key: str) -> str | None:
        """Get from cache with LRU eviction."""
        if key in self.cache:
            self._cache_hits += 1
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        self._cache_misses += 1
        return None
    
    def _set_cached(self, key: str, value: str):
        """Add to cache with LRU eviction."""
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            self.cache[key] = value
            # Evict oldest if over limit
            if len(self.cache) > MAX_CACHE_SIZE:
                self.cache.popitem(last=False)
    
    def get_cached_response(self, prompt: str) -> str | None:
        """Get cached response if available."""
        return self._get_cached(prompt)
    
    def cache_response(self, prompt: str, response: str):
        """Cache a response."""
        self._set_cached(prompt, response)
    
    def is_simple(self, prompt: str) -> bool:
        """Check if prompt is simple enough for instant response."""
        simple_indicators = [
            "hello", "hi", "hey",
            "what's up", "how are",
            "thanks", "thank you",
            "yes", "no",
            "time", "date",
        ]
        prompt_lower = prompt.lower()
        return any(ind in prompt_lower for ind in simple_indicators) or len(prompt) < 50
    
    async def fast_response(self, prompt: str, fast_brain=None, deep_brains=None):
        """Send instant answer, think deeply in background."""
        
        # Check cache first
        cached = self._get_cached(prompt)
        if cached:
            return cached
        
        # Instant response for simple questions
        if self.is_simple(prompt):
            quick_responses = {
                "hello": "Hey! What's on your mind? 👑",
                "hi": "Hi there! 👑",
                "hey": "Hey! What's up? 👑",
                "thanks": "You're welcome! 👑",
                "thank you": "Happy to help! 👑",
            }
            prompt_lower = prompt.lower()
            for key, response in quick_responses.items():
                if key in prompt_lower:
                    self._set_cached(prompt, response)
                    return response
        
        # Default quick response
        return None
    
    def get_cache_stats(self) -> dict:
        """Return cache statistics."""
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0
        return {
            "size": len(self.cache),
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": f"{hit_rate:.1%}"
        }
