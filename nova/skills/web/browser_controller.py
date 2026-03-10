#!/usr/bin/env python3
"""
Nova Browser Controller
Safe browser automation for web browsing
"""

import asyncio
import re
from typing import Dict, List, Optional, Any


class BrowserController:
    """
    Safe browser controller for Nova.
    Uses requests + beautifulsoup for simple browsing,
    or Playwright if available for complex interactions.
    """
    
    def __init__(self):
        self.session = None
        self.playwright = None
        self.browser = None
        self.page = None
        self.use_playwright = False
    
    async def initialize(self):
        """Initialize browser session"""
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
        except ImportError:
            pass
    
    async def open(self, url: str) -> Dict[str, Any]:
        """Open a URL and return content"""
        if not self.session:
            await self.initialize()
        
        if not self.session:
            return {
                "success": False,
                "error": "No browser available",
                "content": None
            }
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            return {
                "success": True,
                "url": url,
                "status": response.status_code,
                "content": response.text[:50000],  # Limit content size
                "content_length": len(response.text)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "content": None
            }
    
    async def get_page_text(self, url: str) -> str:
        """Get plain text from a page"""
        result = await self.open(url)
        
        if not result.get("success"):
            return f"Error: {result.get('error')}"
        
        # Simple HTML to text conversion
        html = result.get("content", "")
        
        # Remove scripts and styles
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        
        # Convert HTML to text
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text[:30000]  # Limit text length
    
    async def search(self, query: str) -> Dict[str, Any]:
        """Perform a safe search"""
        # Use DuckDuckGo (no tracking)
        search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        
        result = await self.open(search_url)
        
        if not result.get("success"):
            return result
        
        # Extract search results
        content = result.get("content", "")
        
        # Simple result extraction
        results = []
        
        # Look for result links
        link_pattern = r'<a class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(link_pattern, content)
        
        for url, title in matches[:5]:
            results.append({
                "title": title.strip(),
                "url": url
            })
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    async def close(self):
        """Close browser session"""
        if self.session:
            self.session = None


# Global instance
_browser = None

def get_browser() -> BrowserController:
    global _browser
    if _browser is None:
        _browser = BrowserController()
    return _browser
