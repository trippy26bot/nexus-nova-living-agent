#!/usr/bin/env python3
"""
Fast Response Layer - Instant responses while deep thinking continues
"""

import asyncio
from datetime import datetime

class FastResponse:
    """Send instant responses while deep brains continue processing."""
    
    def __init__(self):
        self.cache = {}
        self.fast_mode = True
    
    def is_simple(self, prompt: str) -> bool:
        """判断是否简单问题"""
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
        
        # Instant response for simple questions
        if self.is_simple(prompt):
            quick_responses = {
                "hello": "Hey! 👑 What's on your mind?",
                "hi": "Hi there! 👑",
                "hey": "Hey! 👑 What's up?",
                "thanks": "You're welcome! 👑",
                "thank you": "Happy to help! 👑",
            }
            
            prompt_lower = prompt.lower()
            for key, response in quick_responses.items():
                if key in prompt_lower:
                    # Trigger deep thinking in background
                    if deep_brains:
                        asyncio.create_task(self._deep_think(prompt, deep_brains))
                    return response
        
        # For complex questions, still try to be fast
        if fast_brain:
            result = await fast_brain.run(prompt)
        else:
            result = "Let me think about that..."
        
        # Continue deep thinking in background
        if deep_brains:
            asyncio.create_task(self._deep_think(prompt, deep_brains))
        
        return result
    
    async def _deep_think(self, prompt: str, brains):
        """Background deep thinking."""
        try:
            tasks = [brain.run(prompt) for brain in brains]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        except Exception:
            pass
    
    def cached_response(self, prompt: str, generator_func):
        """Cache frequent responses."""
        if prompt in self.cache:
            return self.cache[prompt]
        
        result = generator_func()
        self.cache[prompt] = result
        return result
    
    def clear_cache(self):
        """Clear response cache."""
        self.cache.clear()


# Async brain runner
async def run_brains_parallel(prompt: str, brains: list):
    """Run all brains in parallel for speed."""
    tasks = [brain.run(prompt) for brain in brains]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results


if __name__ == "__main__":
    fr = FastResponse()
    print("Fast Response Layer loaded")
    print(f"Simple detection: {fr.is_simple('hello')}")
    print(f"Complex detection: {fr.is_simple('analyze the crypto markets and recommend trades')}")
