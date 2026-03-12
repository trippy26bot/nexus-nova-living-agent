#!/usr/bin/env python3
"""
Nova Web Fetcher
Lightweight web fetching for research and awareness
"""
import urllib.request
import urllib.error
import json
import ssl

# Bypass SSL verification for some endpoints
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def fetch_url(url: str, timeout: int = 10) -> dict:
    """
    Fetch a URL and return basic info.
    Returns: {'success': bool, 'content': str, 'error': str}
    """
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Nova/1.0 (AI Assistant)'}
        )
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as response:
            content = response.read().decode('utf-8')
            return {
                'success': True,
                'content': content[:5000],  # Limit to 5k chars
                'status': response.status,
                'content_type': response.headers.get('Content-Type', '')
            }
    except urllib.error.HTTPError as e:
        return {'success': False, 'error': f'HTTP {e.code}: {e.reason}'}
    except urllib.error.URLError as e:
        return {'success': False, 'error': f'URL Error: {e.reason}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def fetch_json(url: str, timeout: int = 10) -> dict:
    """Fetch JSON endpoint and parse"""
    result = fetch_url(url, timeout)
    if result['success']:
        try:
            result['data'] = json.loads(result['content'])
        except json.JSONDecodeError:
            result['error'] = 'Failed to parse JSON'
            result['success'] = False
    return result

# Quick endpoints for awareness
QUICK_CHECKS = {
    'time': 'http://worldtimeapi.org/api/timezone/America/Denver',
    'ip': 'https://api.ipify.org?format=json',
    'news': None  # Would need API key
}

def quick_check(check_type: str = 'time') -> dict:
    """Quick awareness checks"""
    if check_type == 'time':
        return fetch_json(QUICK_CHECKS['time'])
    elif check_type == 'ip':
        return fetch_json(QUICK_CHECKS['ip'])
    else:
        return {'success': False, 'error': 'Unknown check type'}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = quick_check(sys.argv[1])
        print(json.dumps(result, indent=2))
    else:
        # Test fetch
        print("Testing web fetcher...")
        r = fetch_url("https://httpbin.org/get")
        print(f"Success: {r['success']}")
