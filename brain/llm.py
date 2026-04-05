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
    Call local Ollama for synthesis tasks. Falls back to MiniMax if Ollama is unavailable.
    
    Args:
        prompt: The user prompt
        system: Optional system prompt
        max_tokens: Max response tokens
        temperature: Sampling temperature
        model: Model override (default: qwen2.5:14b-instruct-q4_K_M)
    
    Returns:
        str: The LLM response text
    """
    # Primary: use local Ollama on the desktop PC
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_model = model or "qwen2.5:14b-instruct-q4_K_M"
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": ollama_model,
        "messages": messages,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
        "stream": False,
    }
    
    try:
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return "[llm_synthesis error: no choices in response from Ollama]"
    except Exception as ollama_err:
        # Fallback: try MiniMax if API key is available
        api_key = _get_minimax_key()
        if not api_key:
            return f"[llm_synthesis error: Ollama unavailable ({ollama_err}), no MiniMax fallback key]"
        
        # MiniMax fallback
        url = "https://api.minimax.chat/v1/text/chatcompletion_pro?group_id=123456789"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
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
                return "[llm_synthesis error: no choices in response from MiniMax]"
        except urllib.error.HTTPError as e:
            return f"[llm_synthesis error: HTTP {e.code}]"
        except Exception as e:
            return f"[llm_synthesis error: both Ollama ({ollama_err}) and MiniMax failed: {e}]"
