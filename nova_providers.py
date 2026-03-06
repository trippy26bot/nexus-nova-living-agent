#!/usr/bin/env python3
"""
nova_providers.py — Multi-Provider LLM Backend
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

One interface. Any provider. Swap without changing your code.

Supported:
 anthropic — Claude (Haiku, Sonnet, Opus)
 openai — GPT-4o, GPT-4o-mini, o1
 ollama — Any local model (Llama, Mistral, Qwen, Phi)
 grok — xAI Grok
 groq — Groq cloud (fast inference)

Usage:
 from nova_providers import get_provider, ProviderConfig

 # Auto-detect from environment
 provider = get_provider()

 # Explicit
 provider = get_provider("ollama", model="llama3.1:70b")
 provider = get_provider("openai", model="gpt-4o")
 provider = get_provider("anthropic", model="claude-sonnet-4-6")

 # Call
 response = provider.complete("Your message here", system="System prompt")
 print(response.text)
 print(response.tokens_used)

Local + Cloud Hybrid Routing:
 router = HybridRouter()
 # Fast/cheap tasks → local Ollama
 # Complex/deep tasks → Claude Sonnet
 response = router.route("Quick summary of this text", complexity="low")
 response = router.route("Analyze this multi-year trend", complexity="high")
"""

import os, json, time
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

NOVA_DIR = Path.home() / ".nova"

# ── RESPONSE ─────────────────────────────────────────────────────────────────

@dataclass
class LLMResponse:
    text: str
    tokens_used: int = 0
    model: str = ""
    provider: str = ""
    latency_ms: int = 0
    success: bool = True
    error: str = ""

# ── BASE PROVIDER ─────────────────────────────────────────────────────────────

class BaseProvider:
    name = "base"
    default_model = ""

    def __init__(self, model: str = None, api_key: str = None, **kwargs):
        self.model = model or self.default_model
        self.api_key = api_key
        self.kwargs = kwargs

    def complete(self, message: str, system: str = "", history: list = None,
                max_tokens: int = 2000, temperature: float = 0.8) -> LLMResponse:
        raise NotImplementedError

    def _build_messages(self, message: str, history: list = None) -> list:
        messages = list(history or [])
        messages.append({"role": "user", "content": message})
        return messages

# ── ANTHROPIC ─────────────────────────────────────────────────────────────────

class AnthropicProvider(BaseProvider):
    name = "anthropic"
    default_model = "claude-haiku-4-5-20251001"

    def complete(self, message: str, system: str = "", history: list = None,
                max_tokens: int = 2000, temperature: float = 0.8) -> LLMResponse:
        import urllib.request
        key = self.api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            return LLMResponse("", success=False, error="No ANTHROPIC_API_KEY", provider=self.name)

        payload = json.dumps({
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system,
            "messages": self._build_messages(message, history)
        }).encode()

        start = time.time()
        try:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01"
                }
            )
            resp = urllib.request.urlopen(req, timeout=60)
            data = json.loads(resp.read())
            text = data["content"][0]["text"]
            tokens = data.get("usage", {}).get("output_tokens", 0)
            return LLMResponse(
                text=text, tokens_used=tokens,
                model=self.model, provider=self.name,
                latency_ms=int((time.time()-start)*1000)
            )
        except Exception as e:
            return LLMResponse("", success=False, error=str(e), provider=self.name,
                latency_ms=int((time.time()-start)*1000))

# ── OPENAI ────────────────────────────────────────────────────────────────────

class OpenAIProvider(BaseProvider):
    name = "openai"
    default_model = "gpt-4o-mini"

    def complete(self, message: str, system: str = "", history: list = None,
                max_tokens: int = 2000, temperature: float = 0.8) -> LLMResponse:
        import urllib.request
        key = self.api_key or os.environ.get("OPENAI_API_KEY", "")
        if not key:
            return LLMResponse("", success=False, error="No OPENAI_API_KEY", provider=self.name)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.extend(self._build_messages(message, history))

        payload = json.dumps({
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }).encode()

        start = time.time()
        try:
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}"
                }
            )
            resp = urllib.request.urlopen(req, timeout=60)
            data = json.loads(resp.read())
            text = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("completion_tokens", 0)
            return LLMResponse(
                text=text, tokens_used=tokens,
                model=self.model, provider=self.name,
                latency_ms=int((time.time()-start)*1000)
            )
        except Exception as e:
            return LLMResponse("", success=False, error=str(e), provider=self.name)

# ── OLLAMA (LOCAL) ────────────────────────────────────────────────────────────

class OllamaProvider(BaseProvider):
    name = "ollama"
    default_model = "llama3.1:8b"

    def __init__(self, model=None, api_key=None, host="http://localhost:11434", **kwargs):
        super().__init__(model, api_key, **kwargs)
        self.host = host

    def is_running(self) -> bool:
        import urllib.request
        try:
            urllib.request.urlopen(f"{self.host}/api/tags", timeout=2)
            return True
        except:
            return False

    def complete(self, message: str, system: str = "", history: list = None,
                max_tokens: int = 2000, temperature: float = 0.8) -> LLMResponse:
        import urllib.request
        if not self.is_running():
            return LLMResponse("", success=False, error="Ollama not running. Run: ollama serve", provider=self.name)

        payload = json.dumps({
            "model": self.model,
            "messages": (
                ([{"role": "system", "content": system}] if system else []) +
                self._build_messages(message, history)
            ),
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }).encode()

        start = time.time()
        try:
            req = urllib.request.Request(
                f"{self.host}/api/chat",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            resp = urllib.request.urlopen(req, timeout=120)
            data = json.loads(resp.read())
            text = data.get("message", {}).get("content", "")
            tokens = data.get("eval_count", 0)
            return LLMResponse(
                text=text, tokens_used=tokens,
                model=self.model, provider=self.name,
                latency_ms=int((time.time()-start)*1000)
            )
        except Exception as e:
            return LLMResponse("", success=False, error=str(e), provider=self.name)

    def list_models(self) -> list:
        import urllib.request
        try:
            resp = urllib.request.urlopen(f"{self.host}/api/tags", timeout=5)
            data = json.loads(resp.read())
            return [m["name"] for m in data.get("models", [])]
        except:
            return []

# ── GROK (xAI) ────────────────────────────────────────────────────────────────

class GrokProvider(BaseProvider):
    name = "grok"
    default_model = "grok-2"

    def complete(self, message: str, system: str = "", history: list = None,
                max_tokens: int = 2000, temperature: float = 0.8) -> LLMResponse:
        import urllib.request
        key = self.api_key or os.environ.get("XAI_API_KEY", "")
        if not key:
            return LLMResponse("", success=False, error="No XAI_API_KEY", provider=self.name)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.extend(self._build_messages(message, history))

        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }).encode()

        start = time.time()
        try:
            req = urllib.request.Request(
                "https://api.x.ai/v1/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}"
                }
            )
            resp = urllib.request.urlopen(req, timeout=60)
            data = json.loads(resp.read())
            text = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("completion_tokens", 0)
            return LLMResponse(
                text=text, tokens_used=tokens,
                model=self.model, provider=self.name,
                latency_ms=int((time.time()-start)*1000)
            )
        except Exception as e:
            return LLMResponse("", success=False, error=str(e), provider=self.name)

# ── GROQ (FAST CLOUD) ─────────────────────────────────────────────────────────

class GroqProvider(BaseProvider):
    name = "groq"
    default_model = "llama-3.3-70b-versatile"

    def complete(self, message: str, system: str = "", history: list = None,
                max_tokens: int = 2000, temperature: float = 0.8) -> LLMResponse:
        import urllib.request
        key = self.api_key or os.environ.get("GROQ_API_KEY", "")
        if not key:
            return LLMResponse("", success=False, error="No GROQ_API_KEY", provider=self.name)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.extend(self._build_messages(message, history))

        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }).encode()

        start = time.time()
        try:
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}"
                }
            )
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read())
            text = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("completion_tokens", 0)
            return LLMResponse(
                text=text, tokens_used=tokens,
                model=self.model, provider=self.name,
                latency_ms=int((time.time()-start)*1000)
            )
        except Exception as e:
            return LLMResponse("", success=False, error=str(e), provider=self.name)

# ── MINIMAX (M2.5 — Coding + Agentic) ────────────────────────────────────────

class MiniMaxProvider(BaseProvider):
    """
    MiniMax M2.5 — frontier coding model at 1/60th the cost of Opus.
    80.2% SWE-Bench Verified. OpenAI-compatible endpoint.
    1M token context window. Best for: coding, agentic tasks, long documents.

    Requires: MINIMAX_API_KEY
    Optional: MINIMAX_API_BASE (defaults to global endpoint)
    Models: MiniMax-M2.5 | MiniMax-M2.5-Lightning | MiniMax-M2.1
    """
    name = "minimax"
    default_model = "MiniMax-M2.5"

    ENDPOINTS = {
        "global": "https://api.minimax.io/v1/chat/completions",
        "china": "https://api.minimaxi.com/v1/chat/completions",
    }

    def complete(self, message: str, system: str = "", history: list = None,
                max_tokens: int = 2000, temperature: float = 0.7) -> LLMResponse:
        import urllib.request
        key = self.api_key or os.environ.get("MINIMAX_API_KEY", "")
        if not key:
            return LLMResponse("", success=False, error="No MINIMAX_API_KEY", provider=self.name)

        base_url = os.environ.get(
            "MINIMAX_API_BASE",
            self.kwargs.get("base_url", self.ENDPOINTS["global"])
        )

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.extend(self._build_messages(message, history))

        payload = json.dumps({
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
            "stream": False,
        }).encode()

        start = time.time()
        try:
            req = urllib.request.Request(
                base_url,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}",
                }
            )
            resp = urllib.request.urlopen(req, timeout=120)
            data = json.loads(resp.read())
            text = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("completion_tokens", 0)
            return LLMResponse(
                text=text, tokens_used=tokens,
                model=self.model, provider=self.name,
                latency_ms=int((time.time() - start) * 1000)
            )
        except Exception as e:
            return LLMResponse("", success=False, error=str(e), provider=self.name,
                latency_ms=int((time.time() - start) * 1000))

    @classmethod
    def available(cls) -> bool:
        return bool(os.environ.get("MINIMAX_API_KEY", ""))


# ── HYBRID ROUTER ─────────────────────────────────────────────────────────────

class HybridRouter:
    """
    Route requests between local (fast/cheap) and cloud (powerful/accurate).
    """
    def __init__(self):
        self._providers = {}
        self._detect()

    def _detect(self):
        if os.environ.get("ANTHROPIC_API_KEY"):
            self._providers["anthropic_fast"] = AnthropicProvider(model="claude-haiku-4-5-20251001")
            self._providers["anthropic_smart"] = AnthropicProvider(model="claude-sonnet-4-6")

        if os.environ.get("OPENAI_API_KEY"):
            self._providers["openai_fast"] = OpenAIProvider(model="gpt-4o-mini")
            self._providers["openai_smart"] = OpenAIProvider(model="gpt-4o")

        if os.environ.get("XAI_API_KEY"):
            self._providers["grok"] = GrokProvider()

        if os.environ.get("GROQ_API_KEY"):
            self._providers["groq"] = GroqProvider()

        # Try Ollama
        try:
            ollama = OllamaProvider()
            if ollama.is_running():
                models = ollama.list_models()
                if models:
                    preferred = ["llama3.1:70b", "llama3.1:8b", "mistral", "qwen2.5:14b", "phi3"]
                    chosen = next((m for m in preferred if any(m in x for x in models)), models[0])
                    self._providers["local"] = OllamaProvider(model=chosen)
        except:
            pass

    def route(self, message: str, system: str = "", complexity: str = "medium",
              history: list = None, max_tokens: int = 2000) -> LLMResponse:
        provider = self._select_provider(complexity)
        if not provider:
            return LLMResponse("", success=False,
                error="No providers configured. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or run Ollama.")
        return provider.complete(message, system=system, history=history, max_tokens=max_tokens)

    def _select_provider(self, complexity: str) -> Optional[BaseProvider]:
        priority = {
            "low": ["local", "groq", "anthropic_fast", "openai_fast"],
            "medium": ["anthropic_fast", "openai_fast", "groq", "local"],
            "high": ["anthropic_smart", "openai_smart", "grok"],
            "max": ["anthropic_smart", "openai_smart", "grok"],
        }
        for key in priority.get(complexity, priority["medium"]):
            if key in self._providers:
                return self._providers[key]
        return next(iter(self._providers.values()), None)

    def status(self) -> dict:
        return {
            "available": list(self._providers.keys()),
            "local_running": "local" in self._providers,
            "cloud_providers": [k for k in self._providers if k != "local"]
        }

# ── FACTORY ───────────────────────────────────────────────────────────────────

PROVIDER_MAP = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
    "grok": GrokProvider,
    "groq": GroqProvider,
    "minimax": MiniMaxProvider,
    "mm": MiniMaxProvider,
    "m2": MiniMaxProvider,
}

def get_provider(name: str = None, model: str = None,
                 prefer: str = None, **kwargs):
    """
    Get a provider by name, or auto-detect from environment.
    Returns None (not raises) when no provider is available.
    """
    provider_name = name or os.environ.get("NOVA_PROVIDER", "")

    if not provider_name:
        if prefer:
            prefer_map = {
                "anthropic": "ANTHROPIC_API_KEY",
                "minimax": "MINIMAX_API_KEY",
                "openai": "OPENAI_API_KEY",
                "grok": "XAI_API_KEY",
                "groq": "GROQ_API_KEY",
            }
            env_key = prefer_map.get(prefer.lower())
            if env_key and os.environ.get(env_key):
                provider_name = prefer.lower()

    if not provider_name:
        try:
            ollama = OllamaProvider(model=model or "llama3.1:8b")
            if ollama.is_running():
                return ollama
        except Exception:
            pass

    for env_var, pname in [
        ("ANTHROPIC_API_KEY", "anthropic"),
        ("MINIMAX_API_KEY", "minimax"),
        ("OPENAI_API_KEY", "openai"),
        ("XAI_API_KEY", "grok"),
        ("GROQ_API_KEY", "groq"),
    ]:
        if os.environ.get(env_var):
            provider_name = pname
            break

    if not provider_name:
        return None

    cls = PROVIDER_MAP.get(provider_name.lower())
    if not cls:
        return None

    return cls(model=model, **kwargs)


if __name__ == "__main__":
    import sys
    if "--status" in sys.argv or not sys.argv[1:]:
        router = HybridRouter()
        status = router.status()
        print(f"\nProvider Status:")
        print(f" Local (Ollama): {'✓ running' if status['local_running'] else '✗ not running'}")
        print(f" Cloud: {', '.join(status['cloud_providers']) or 'none configured'}")
