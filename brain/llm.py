#!/usr/bin/env python3
"""
brain/llm.py — MiniMax LLM caller for Nova's overnight scripts.
Single shared utility so all overnight processes call the same model the same way.
"""

import os
import json
import requests
from datetime import datetime

MINIMAX_BASE_URL = "https://api.minimax.io/anthropic/v1"
DEFAULT_MODEL = "MiniMax-M2.7"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.7


def call_llm(
    prompt: str,
    system: str = "",
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    timeout: int = 60,
) -> str:
    """
    Make a synchronous MiniMax API call.
    Returns the response text, or raises an exception on failure.
    """
    url = f"{MINIMAX_BASE_URL}/messages"

    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        raise RuntimeError("MINIMAX_API_KEY environment variable is not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01",
        "x-api-key": api_key,
    }

    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system

    resp = requests.post(url, headers=headers, json=body, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(
            f"MiniMax API error {resp.status_code}: {resp.text[:500]}"
        )

    data = resp.json()
    # Anthropic-style response
    if "content" in data:
        for block in data["content"]:
            if block.get("type") == "text":
                return block["text"]

    # Fallback: return raw content
    return data.get("content", data.get("text", str(data)))


def llm_synthesis(prompt: str, system: str = "", **kwargs) -> str:
    """
    Convenience wrapper specifically for synthesis tasks.
    Slightly lower temperature (0.4) for more focused output.
    """
    return call_llm(prompt, system=system, temperature=0.4, **kwargs)


def llm_extract(prompt: str, system: str = "", **kwargs) -> str:
    """
    Convenience wrapper for extraction/fact-distillation tasks.
    Lower temperature (0.3) for deterministic-ish output.
    """
    return call_llm(prompt, system=system, temperature=0.3, **kwargs)
