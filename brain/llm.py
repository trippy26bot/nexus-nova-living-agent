#!/usr/bin/env python3
"""
brain/llm.py — Nova's LLM wrapper.
Now using llm_router.py: Ollama first, MiniMax fallback.
"""

from brain.llm_router import llm_extract, ollama_available


if __name__ == "__main__":
    # Quick test
    print(f"Ollama available: {ollama_available()}")
    result = llm_extract("Say 'hello' in exactly one word.", max_tokens=10)
    print(f"Test result: {result}")
