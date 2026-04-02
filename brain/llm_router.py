#!/usr/bin/env python3
"""
brain/llm_router.py — Nova's LLM router.
Tries Ollama (gaming PC) first, falls back to MiniMax.
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path

# Config
OLLAMA_BASE = "http://192.168.0.3:11434"
OLLAMA_MODEL = "qwen2.5:14b-instruct-q4_K_M"
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_MODEL = "MiniMax-Text-01"


def _ensure_minimax_key():
    global MINIMAX_API_KEY
    if not MINIMAX_API_KEY:
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("MINIMAX_API_KEY="):
                    MINIMAX_API_KEY = line.split("=", 1)[1].strip()
                    break


def _ollama_chat(prompt, system=None, max_tokens=512, temperature=0.7):
    """Call Ollama on the gaming PC."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "messages": messages,
        "temperature": temperature,
        "options": {
            "num_predict": max_tokens,
        },
        "stream": False,
    }).encode()

    headers = {"Content-Type": "application/json"}

    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE}/api/chat",
            data=payload,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode())
            content = data.get("message", {}).get("content", "")
            return content.strip() if content else None
    except Exception as e:
        print(f"[router] Ollama error: {e}")
        return None


def _minimax_chat(prompt, system=None, max_tokens=512, temperature=0.7):
    """Call MiniMax API as fallback."""
    _ensure_minimax_key()
    if not MINIMAX_API_KEY:
        print("[router] No MINIMAX_API_KEY found")
        return None

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    payload = json.dumps({
        "model": MINIMAX_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": 0.9,
    }).encode()

    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content.strip() if content else None
    except urllib.error.HTTPError as e:
        body = resp.read().decode() if hasattr(resp, "read") else ""
        print(f"[router] MiniMax HTTP error: {e.code} {e.reason} — {body}")
        return None
    except Exception as e:
        print(f"[router] MiniMax error: {e}")
        return None


def llm_extract(prompt, system=None, max_tokens=512, temperature=0.7):
    """
    Main entry point. Tries Ollama first, MiniMax fallback.
    
    Args:
        prompt: User prompt
        system: Optional system prompt
        max_tokens: Max tokens in response
        temperature: Temperature setting
    
    Returns:
        Response text string, or None on error
    """
    # Try Ollama first
    result = _ollama_chat(prompt, system, max_tokens, temperature)
    if result:
        print(f"[router] → Ollama ({OLLAMA_MODEL})")
        return result

    # Fallback to MiniMax
    print("[router] → Ollama unavailable, falling back to MiniMax")
    return _minimax_chat(prompt, system, max_tokens, temperature)


def ollama_available():
    """Check if Ollama is reachable."""
    try:
        req = urllib.request.Request(
            f"{OLLAMA_BASE}/api/tags",
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


if __name__ == "__main__":
    # Quick test
    print(f"[router] Ollama available: {ollama_available()}")
    result = llm_extract("Say 'hello' in exactly one word.", max_tokens=10)
    print(f"Test result: {result}")
