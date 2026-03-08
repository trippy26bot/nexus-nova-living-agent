#!/usr/bin/env python3
"""
nova_api_detector.py — API Detection & Capability Mapping

Detects available APIs, probes capabilities, builds routing table.
"""

import os
import json
import time
from dataclasses import dataclass
from typing import Optional

# API Registry
API_REGISTRY = {
    "anthropic": {
        "env_key": "ANTHROPIC_API_KEY",
        "base_url": "https://api.anthropic.com/v1/messages",
        "test_model": "claude-haiku-4-5-20251001",
        "capabilities": {"reasoning": True, "code": True, "vision": True, "function_calling": True},
        "context_window": 200000,
    },
    "minimax": {
        "env_key": "MINIMAX_API_KEY",
        "base_url": "https://api.minimax.chat/v1/text/chatcompletion_v2",
        "test_model": "MiniMax-Text-01",
        "capabilities": {"reasoning": True, "code": True, "vision": True, "function_calling": True},
        "context_window": 1000000,
    },
    "openai": {
        "env_key": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1/chat/completions",
        "test_model": "gpt-4o-mini",
        "capabilities": {"reasoning": True, "code": True, "vision": True, "function_calling": True},
        "context_window": 128000,
    },
    "grok": {
        "env_key": "GROK_API_KEY",
        "base_url": "https://api.x.ai/v1/chat/completions",
        "test_model": "grok-2-latest",
        "capabilities": {"reasoning": True, "code": True, "real_time_web": True},
        "context_window": 131072,
    },
    "deepseek": {
        "env_key": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com/v1/chat/completions",
        "test_model": "deepseek-coder",
        "capabilities": {"reasoning": True, "code": True},
        "context_window": 16384,
    },
    "gemini": {
        "env_key": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "test_model": "gemini-2.0-flash",
        "capabilities": {"reasoning": True, "code": True, "vision": True, "real_time_web": True},
        "context_window": 2000000,
    },
    "ollama": {
        "env_key": None,
        "base_url": "http://localhost:11434/api/chat",
        "test_model": "llama3.1",
        "capabilities": {"reasoning": True, "code": True},
        "context_window": 32768,
    },
}

TASK_ROUTING = {
    "code_generation": ["deepseek", "minimax", "anthropic", "openai"],
    "code_review": ["anthropic", "minimax", "deepseek"],
    "long_document": ["minimax", "gemini", "anthropic"],
    "reasoning": ["anthropic", "openai", "grok"],
    "current_events": ["grok", "gemini"],
    "fast_cheap": ["deepseek", "minimax", "gemini", "ollama"],
}


@dataclass
class APICapability:
    name: str
    available: bool
    model: str
    capabilities: dict
    context_window: int
    latency_ms: int = 0
    error: str = ""


@dataclass
class APIReport:
    scanned_at: str
    available: list
    unavailable: list
    capabilities: dict
    best_for_reasoning: str
    best_for_code: str
    best_for_long_ctx: str
    best_for_speed: str


class APIDetector:
    def __init__(self):
        self._cache = None

    def scan(self, force=False) -> APIReport:
        if self._cache and not force:
            return self._cache

        available = []
        unavailable = []
        capabilities = {}

        for api_name, config in API_REGISTRY.items():
            cap = self._probe(api_name, config)
            capabilities[api_name] = cap
            if cap.available:
                available.append(api_name)
            else:
                unavailable.append(api_name)

        def best_from(prefs):
            for p in prefs:
                if p in available:
                    return p
            return "none"

        report = APIReport(
            scanned_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            available=available,
            unavailable=unavailable,
            capabilities=capabilities,
            best_for_reasoning=best_from(["anthropic", "openai", "minimax"]),
            best_for_code=best_from(["deepseek", "minimax", "anthropic"]),
            best_for_long_ctx=best_from(["minimax", "gemini"]),
            best_for_speed=best_from(["deepseek", "minimax", "ollama"]),
        )
        self._cache = report
        return report

    def _probe(self, name, config) -> APICapability:
        key_name = config.get("env_key")
        if key_name:
            api_key = os.environ.get(key_name, "")
            if not api_key:
                return APICapability(name=name, available=False, model=config["test_model"],
                                     capabilities=config["capabilities"], context_window=config["context_window"],
                                     error=f"No {key_name}")
        else:
            api_key = ""

        start = time.time()
        try:
            import urllib.request
            test_msg = "Say 'ok'"
            
            if name == "anthropic":
                headers = {"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"}
                payload = {"model": config["test_model"], "max_tokens": 5, "messages": [{"role": "user", "content": test_msg}]}
            elif name == "ollama":
                headers = {"Content-Type": "application/json"}
                payload = {"model": config["test_model"], "messages": [{"role": "user", "content": test_msg}]}
            else:
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
                payload = {"model": config["test_model"], "max_tokens": 5, "messages": [{"role": "user", "content": test_msg}]}

            req = urllib.request.Request(config["base_url"], data=json.dumps(payload).encode(), headers=headers)
            resp = urllib.request.urlopen(req, timeout=8)
            latency = int((time.time() - start) * 1000)

            return APICapability(name=name, available=True, model=config["test_model"],
                                 capabilities=config["capabilities"], context_window=config["context_window"],
                                 latency_ms=latency)
        except Exception as e:
            return APICapability(name=name, available=False, model=config["test_model"],
                                 capabilities=config["capabilities"], context_window=config["context_window"],
                                 error=str(e)[:80])

    def available_apis(self):
        return self.scan().available

    def best_for(self, task):
        report = self.scan()
        if task in TASK_ROUTING:
            for api in TASK_ROUTING[task]:
                if api in report.available:
                    return api
        return report.best_for_reasoning


if __name__ == "__main__":
    import sys
    detector = APIDetector()
    
    if len(sys.argv) > 1 and sys.argv[1] == "scan":
        report = detector.scan(force=True)
        print(f"\nAPI Detection Report")
        print(f"{'='*40}")
        print(f"Available: {', '.join(report.available) if report.available else 'none'}")
        print(f"Unavailable: {', '.join(report.unavailable) if report.unavailable else 'none'}")
        print(f"\nBest for reasoning: {report.best_for_reasoning}")
        print(f"Best for code: {report.best_for_code}")
        print(f"Best for long context: {report.best_for_long_ctx}")
        print(f"Best for speed: {report.best_for_speed}")
    else:
        print(f"Available APIs: {detector.available_apis()}")
