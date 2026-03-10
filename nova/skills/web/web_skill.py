#!/usr/bin/env python3
"""
Nova Web Skill
Safe web browsing for Nova
"""

import asyncio
from typing import Dict, List, Any, Optional
from nova.skills.web.security import get_web_security, TopicFilter, DomainWhitelist
from nova.skills.web.browser_controller import get_browser


class WebSkill:
    """
    Nova's safe web browsing skill.
    
    Features:
    - Topic filtering (blocks illegal/dangerous)
    - Domain whitelist (safe sites only)
    - Simple text extraction
    - Search capability
    """
    
    def __init__(self):
        self.security = get_web_security()
        self.browser = get_browser()
        self.topic_filter = TopicFilter()
        self.domain_whitelist = DomainWhitelist()
    
    async def browse(self, url: str) -> Dict[str, Any]:
        """Browse a URL with security checks"""
        # Check domain first
        security = self.security.check("", url)
        
        if not security["allowed"]:
            return {
                "success": False,
                "error": security["reason"],
                "content": None
            }
        
        # Get page content
        content = await self.browser.get_page_text(url)
        
        return {
            "success": True,
            "url": url,
            "content": content,
            "security": "passed"
        }
    
    async def search(self, query: str) -> Dict[str, Any]:
        """Search the web with security checks"""
        # Check topic
        security = self.security.check(query)
        
        if not security["allowed"]:
            return {
                "success": False,
                "error": security["reason"],
                "results": []
            }
        
        # Perform search
        results = await self.browser.search(query)
        
        return results
    
    async def research(self, topic: str, max_sources: int = 3) -> Dict[str, Any]:
        """Research a topic safely"""
        # First search
        search_result = await self.search(topic)
        
        if not search_result.get("success"):
            return search_result
        
        # Get content from top results
        sources = []
        
        for result in search_result.get("results", [])[:max_sources]:
            url = result.get("url", "")
            
            # Check if domain is allowed
            if not self.domain_whitelist.is_allowed(url):
                continue
            
            # Get content
            content = await self.browser.get_page_text(url)
            
            sources.append({
                "title": result.get("title"),
                "url": url,
                "content": content[:5000] if content else ""
            })
        
        return {
            "success": True,
            "topic": topic,
            "sources": sources,
            "count": len(sources)
        }
    
    def get_allowed_domains(self) -> List[str]:
        """Get list of allowed domains"""
        return self.domain_whitelist.get_allowed_domains()
    
    def is_topic_allowed(self, query: str) -> bool:
        """Check if topic is allowed"""
        return self.topic_filter.is_allowed(query)


# Global instance
_web_skill = None

def get_web_skill() -> WebSkill:
    global _web_skill
    if _web_skill is None:
        _web_skill = WebSkill()
    return _web_skill


# Convenience functions
async def browse(url: str) -> Dict[str, Any]:
    """Browse a URL safely"""
    return await get_web_skill().browse(url)

async def search(query: str) -> Dict[str, Any]:
    """Search the web safely"""
    return await get_web_skill().search(query)

async def research(topic: str, max_sources: int = 3) -> Dict[str, Any]:
    """Research a topic safely"""
    return await get_web_skill().research(topic, max_sources)
