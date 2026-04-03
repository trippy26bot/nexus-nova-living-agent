"""
brain/llm.py — LLM synthesis wrapper for Nova's cognitive architecture.

Uses the MINIMAX API via the configured API key.
"""

import os
import json
import urllib.request
import urllib.error
from pathlib import Path

NOVA_HOME = Path(os.path.expanduser("~/.nova"))
ENV_FILE = NOVA_HOME / ".env"

def _load_env():
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v
    return env

def _get_minimax_key():
    env = _load_env()
    return env.get("MINIMAX_API_KEY", os.getenv("MINIMAX_API_KEY", ""))

def llm_synthesis(prompt, system=None, max_tokens=2048, temperature=0.7, model=None):
    """
    Call the MINIMAX LLM API for synthesis tasks.
    
    Args:
        prompt: The user prompt
        system: Optional system prompt
        max_tokens: Max response tokens
        temperature: Sampling temperature
        model: Model override (default: MiniMax-Text-01)
    
    Returns:
        str: The LLM response text
    """
    api_key = _get_minimax_key()
    if not api_key:
        return "[llm_synthesis error: no API key found in ~/.nova/.env]"
    
    url = "https://api.minimax.chat/v1/text/chatcompletion_pro?group_id=123456789"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model or "MiniMax-Text-01",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return "[llm_synthesis error: no choices in response]"
    except urllib.error.HTTPError as e:
        return f"[llm_synthesis error: HTTP {e.code}]"
    except Exception as e:
        return f"[llm_synthesis error: {e}]"
