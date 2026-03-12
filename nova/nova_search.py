#!/usr/bin/env python3
"""
Nova Universal Search
Uses local SearXNG instance (self-hosted, no API key needed)
"""
import urllib.request
import urllib.parse
import json
import ssl

# Local SearXNG instance
SEARXNG_URL = "http://localhost:8080"

def search(query: str, limit: int = 5) -> dict:
    """
    Search using local SearXNG instance.
    Returns: {'success': bool, 'results': [...], 'error': str}
    """
    try:
        url = f"{SEARXNG_URL}/search?q={urllib.parse.quote(query)}&format=json&engines=general"
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Nova/1.0 (AI Assistant)'
            }
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.load(response)
            results = data.get('results', [])
            
            # Limit results
            limited = []
            for r in results[:limit]:
                limited.append({
                    'title': r.get('title', ''),
                    'url': r.get('url', ''),
                    'content': r.get('content', '')[:200],
                    'engine': r.get('engine', '')
                })
            
            return {
                'success': True,
                'results': limited,
                'total': len(results),
                'query': query
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'results': []
        }

def search_and_format(query: str, limit: int = 5) -> str:
    """Search and format as readable text"""
    result = search(query, limit)
    
    if not result['success']:
        return f"Search failed: {result.get('error', 'Unknown error')}"
    
    output = f"🔍 Results for: {query}\n\n"
    
    for i, r in enumerate(result['results'], 1):
        output += f"{i}. {r['title']}\n"
        output += f"   {r['url']}\n"
        if r.get('content'):
            output += f"   {r['content'][:150]}...\n"
        output += "\n"
    
    return output.strip()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(search_and_format(query))
    else:
        print("Usage: nova_search.py <query>")
