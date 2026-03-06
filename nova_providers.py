#!/usr/bin/env python3
"""
NOVA PROVIDERS — Multi-Provider LLM Support
Anthropic, OpenAI, Grok, Ollama + Hybrid Routing

Use multiple LLM providers with automatic fallback.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum

# Configuration
NOVA_DIR = Path.home() / ".nova"
CONFIG_FILE = NOVA_DIR / "config.json"


class Provider(Enum):
    """Available LLM providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GROK = "grok"
    OLLAMA = "ollama"
    HYBRID = "hybrid"


@dataclass
class ProviderConfig:
    """Configuration for a provider."""
    name: str
    api_key: str
    base_url: Optional[str] = None
    model: str = "default"
    max_tokens: int = 4096
    temperature: float = 0.7
    enabled: bool = True


class BaseProvider:
    """Base class for LLM providers."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
    
    def complete(self, prompt: str, system: str = None, **kwargs) -> str:
        """Generate completion."""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if provider is available."""
        raise NotImplementedError


class AnthropicProvider(BaseProvider):
    """Anthropic (Claude) provider."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None
    
    def _get_client(self):
        """Get or create Anthropic client."""
        if self.client is None:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.config.api_key)
        return self.client
    
    def complete(self, prompt: str, system: str = None, **kwargs) -> str:
        """Generate completion."""
        
        client = self._get_client()
        
        model = kwargs.get('model', self.config.model)
        max_tokens = kwargs.get('max_tokens', self.config.max_tokens)
        temperature = kwargs.get('temperature', self.config.temperature)
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages
        )
        
        return response.content[0].text
    
    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        try:
            client = self._get_client()
            # Simple check
            return bool(self.config.api_key)
        except:
            return False


class OpenAIProvider(BaseProvider):
    """OpenAI provider."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.client = None
    
    def _get_client(self):
        """Get or create OpenAI client."""
        if self.client is None:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.config.api_key)
        return self.client
    
    def complete(self, prompt: str, system: str = None, **kwargs) -> str:
        """Generate completion."""
        
        client = self._get_client()
        
        model = kwargs.get('model', self.config.model)
        max_tokens = kwargs.get('max_tokens', self.config.max_tokens)
        temperature = kwargs.get('temperature', self.config.temperature)
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages
        )
        
        return response.choices[0].message.content
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        try:
            return bool(self.config.api_key)
        except:
            return False


class GrokProvider(BaseProvider):
    """xAI Grok provider."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
    
    def complete(self, prompt: str, system: str = None, **kwargs) -> str:
        """Generate completion."""
        
        import requests
        
        url = (self.config.base_url or "https://api.x.ai/v1") + "/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        model = kwargs.get('model', self.config.model or "grok-2-1212")
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.get('max_tokens', self.config.max_tokens),
            "temperature": kwargs.get('temperature', self.config.temperature)
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def is_available(self) -> bool:
        """Check if Grok is available."""
        return bool(self.config.api_key)


class OllamaProvider(BaseProvider):
    """Ollama local provider."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
    
    def complete(self, prompt: str, system: str = None, **kwargs) -> str:
        """Generate completion."""
        
        import requests
        
        url = (self.config.base_url or "http://localhost:11434") + "/api/generate"
        
        model = kwargs.get('model', self.config.model or "llama2")
        
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        data = {
            "model": model,
            "prompt": full_prompt,
            "stream": False
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', '')
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            import requests
            url = (self.config.base_url or "http://localhost:11434") + "/api/tags"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False


class HybridProvider(BaseProvider):
    """Hybrid provider: fast local + deep cloud."""
    
    def __init__(self, config: ProviderConfig, providers: List[BaseProvider]):
        super().__init__(config)
        self.providers = providers
    
    def complete(self, prompt: str, system: str = None, **kwargs) -> str:
        """Generate using hybrid approach."""
        
        mode = kwargs.get('hybrid_mode', 'fast')
        
        if mode == 'fast':
            # Try local first (Ollama)
            for provider in self.providers:
                if isinstance(provider, OllamaProvider) and provider.is_available():
                    try:
                        return provider.complete(prompt, system, **kwargs)
                    except:
                        continue
            
            # Fallback to cloud
            for provider in self.providers:
                if not isinstance(provider, OllamaProvider) and provider.is_available():
                    try:
                        return provider.complete(prompt, system, **kwargs)
                    except:
                        continue
        
        elif mode == 'deep':
            # Use best cloud provider
            for provider in self.providers:
                if provider.is_available():
                    try:
                        return provider.complete(prompt, system, **kwargs)
                    except:
                        continue
        
        return "Error: No providers available"


class ProviderManager:
    """Manage multiple providers with fallback."""
    
    def __init__(self, config: Dict = None):
        self.config = config or self._load_config()
        self.providers: Dict[str, BaseProvider] = {}
        self._init_providers()
    
    def _load_config(self) -> Dict:
        """Load configuration."""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                return json.load(f)
        return {}
    
    def _init_providers(self):
        """Initialize providers from config."""
        
        # Anthropic
        if self.config.get('anthropic_key'):
            self.providers['anthropic'] = AnthropicProvider(ProviderConfig(
                name='anthropic',
                api_key=self.config['anthropic_key'],
                model=self.config.get('model', 'claude-sonnet-4-20250514')
            ))
        
        # OpenAI
        if self.config.get('openai_key'):
            self.providers['openai'] = OpenAIProvider(ProviderConfig(
                name='openai',
                api_key=self.config['openai_key'],
                model=self.config.get('openai_model', 'gpt-4o')
            ))
        
        # Grok
        if self.config.get('grok_key'):
            self.providers['grok'] = GrokProvider(ProviderConfig(
                name='grok',
                api_key=self.config['grok_key'],
                base_url=self.config.get('grok_url'),
                model=self.config.get('grok_model', 'grok-2-1212')
            ))
        
        # Ollama
        if self.config.get('ollama_url'):
            self.providers['ollama'] = OllamaProvider(ProviderConfig(
                name='ollama',
                api_key='',  # No API key needed
                base_url=self.config['ollama_url'],
                model=self.config.get('ollama_model', 'llama2')
            ))
        
        # Hybrid
        if len(self.providers) > 1:
            self.providers['hybrid'] = HybridProvider(
                ProviderConfig(name='hybrid', api_key=''),
                list(self.providers.values())
            )
    
    def complete(self, prompt: str, system: str = None, 
                 provider: str = None, **kwargs) -> str:
        """Generate completion with fallback."""
        
        if provider and provider in self.providers:
            p = self.providers[provider]
            if p.is_available():
                return p.complete(prompt, system, **kwargs)
            else:
                return f"Error: Provider {provider} not available"
        
        # Try each provider in order
        for name, p in self.providers.items():
            if name == 'hybrid':
                continue  # Skip hybrid for manual calls
            
            if p.is_available():
                try:
                    return p.complete(prompt, system, **kwargs)
                except Exception as e:
                    print(f"Provider {name} failed: {e}")
                    continue
        
        return "Error: No providers available"
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return [name for name, p in self.providers.items() if p.is_available()]
    
    def get_status(self) -> Dict:
        """Get provider status."""
        
        status = {}
        for name, provider in self.providers.items():
            status[name] = {
                'available': provider.is_available(),
                'model': provider.config.model
            }
        
        return status


# Singleton
_provider_manager = None

def get_provider_manager() -> ProviderManager:
    """Get the provider manager singleton."""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ProviderManager()
    return _provider_manager


def call_provider(prompt: str, system: str = None, provider: str = None, **kwargs) -> str:
    """Convenience function to call a provider."""
    manager = get_provider_manager()
    return manager.complete(prompt, system, provider, **kwargs)


if __name__ == '__main__':
    print("Nova Providers")
    print("=" * 40)
    
    manager = get_provider_manager()
    status = manager.get_status()
    
    print("\nProvider Status:")
    for name, info in status.items():
        available = "✓" if info['available'] else "✗"
        print(f"  {available} {name}: {info['model']}")
    
    print("\nAvailable:", manager.get_available_providers())
