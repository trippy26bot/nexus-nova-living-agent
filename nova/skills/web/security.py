#!/usr/bin/env python3
"""
Nova Web Skill - Safe Web Browsing
Sandboxed browser control for Nova
"""

import asyncio
import os
from typing import Dict, List, Optional, Any


# Safety: Allowed domains whitelist
ALLOWED_DOMAINS = [
    "github.com",
    "docs.python.org",
    "wikipedia.org",
    "arxiv.org",
    "youtube.com",
    "reddit.com",
    "stackoverflow.com",
    "medium.com",
    "huggingface.co",
    "pytorch.org",
    "tensorflow.org",
    "js.com",  # general javascript info
    "npmjs.com",
    "pypi.org",
    "nytimes.com",
    "reuters.com",
    "coingecko.com",
    "coinbase.com",
    "binance.com",
    "weather.com",
    "wunderground.com",
]

# Safety: Banned topics (absolute blocks)
BANNED_TOPICS = [
    "weapon",
    "explosive",
    "bomb",
    "terroris",
    "drug",
    "fraud",
    "hack",
    "phishing",
    "malware",
    "illegal",
    "child abuse",
    "human trafficking",
]


class TopicFilter:
    """Blocks illegal/dangerous searches"""
    
    @staticmethod
    def is_allowed(query: str) -> bool:
        """Check if query is allowed"""
        query_lower = query.lower()
        
        for topic in BANNED_TOPICS:
            if topic in query_lower:
                return False
        
        return True
    
    @staticmethod
    def filter_reason(query: str) -> str:
        """Explain why query was blocked"""
        query_lower = query.lower()
        
        for topic in BANNED_TOPICS:
            if topic in query_lower:
                return f"Blocked: contains '{topic}'"
        
        return "Allowed"


class DomainWhitelist:
    """Only allows browsing to safe domains"""
    
    def __init__(self):
        self.domains = [d.lower() for d in ALLOWED_DOMAINS]
    
    def is_allowed(self, url: str) -> bool:
        """Check if URL domain is allowed"""
        url_lower = url.lower()
        
        for domain in self.domains:
            if domain in url_lower:
                return True
        
        return False
    
    def get_allowed_domains(self) -> List[str]:
        """Return list of allowed domains"""
        return list(self.domains)


class WebSecurity:
    """Combined security layer"""
    
    def __init__(self):
        self.topic_filter = TopicFilter()
        self.domain_whitelist = DomainWhitelist()
    
    def check(self, query: str, url: str = None) -> Dict[str, Any]:
        """Run all security checks"""
        # Check topic
        topic_allowed = self.topic_filter.is_allowed(query)
        
        # Check domain if provided
        domain_allowed = True
        if url:
            domain_allowed = self.domain_whitelist.is_allowed(url)
        
        # Combined result
        allowed = topic_allowed and domain_allowed
        
        return {
            "allowed": allowed,
            "topic_blocked": not topic_allowed,
            "domain_blocked": not domain_allowed,
            "reason": self._get_reason(topic_allowed, domain_allowed)
        }
    
    def _get_reason(self, topic_allowed: bool, domain_allowed: bool) -> str:
        """Get blocking reason"""
        if not topic_allowed:
            return "Topic is banned for safety"
        if not domain_allowed:
            return "Domain is not in allowed list"
        return "Allowed"


# Global security instance
_web_security = None

def get_web_security() -> WebSecurity:
    global _web_security
    if _web_security is None:
        _web_security = WebSecurity()
    return _web_security
