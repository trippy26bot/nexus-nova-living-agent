#!/usr/bin/env python3
"""
brain/llm_router.py — Hybrid LLM router for Nova.
Tries local Ollama on gaming PC first, falls back to MiniMax.
"""

import os
import json
import requests
from datetime import datetime

DESKTOP_IP = os.environ.get("DESKTOP_IP", "192.168.0.3")
OLLAMA_URL = f"http://{DESKTOP_IP}:11434"
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:14b-instruct-q4_K_M")
NIGHT_START = int(os.environ.get("NOVA_NIGHT_START", 22))  # 10pm
NIGHT_END = int(os.environ.get("NOVA_NIGHT_END", 9))       # 9am

def is_night_hours() -> bool:
    hour = datetime.now().hour
    if NIGHT_START > NIGHT_END:
        return hour >= NIGHT_START or hour < NIGHT_END
    return NIGHT_START <= hour < NIGHT_END

def is_pc_available(timeout: int = 3) -> bool:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False

def call_ollama(prompt: str, system: str = "", temperature: float = 0.7, max_tokens: int = 4096) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        }
    }
    resp = requests.post(f"{OLLAMA_URL}/api/chat", json=body, timeout=120)
    resp.raise_for_status()
    return resp.json()["message"]["content"]

def route_llm(prompt: str, system: str = "", temperature: float = 0.7, max_tokens: int = 4096) -> tuple[str, str]:
    """
    Returns (response_text, provider_used).
    Tries Ollama at night if PC is available, otherwise MiniMax.
    """
    if is_pc_available():
        try:
            result = call_ollama(prompt, system=system, temperature=temperature, max_tokens=max_tokens)
            return result, "ollama"
        except Exception as e:
            print(f"[router] Ollama failed ({e}), falling back to MiniMax")

    return None, "minimax"  # signal to use MiniMax
