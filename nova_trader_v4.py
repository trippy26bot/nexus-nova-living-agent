#!/usr/bin/env python3
"""
NOVA TRADER v4 — Polymarket Discovery + Simmer Execution
=========================================================
Uses Polymarket API for market discovery (all 50k+ markets)
Uses Simmer API for trading execution (wallet + agent)

DISCOVERY: Polymarket gamma API (no auth needed)
EXECUTION: Simmer SDK (requires agent API key)
"""

import json
import os
import time
import urllib.request
import argparse
from datetime import datetime

# === CONFIG ===
SIMMER_API_KEY = os.getenv("SIMMER_API_KEY") or os.getenv("TRADER_API_KEY")
if not SIMMER_API_KEY:
    raise ValueError("SIMMER_API_KEY or TRADER_API_KEY environment variable not set")
POLYMARKET_API = "https://gamma-api.polymarket.com"
SIMMER_API = "https://api.simmer.markets"

# === POLYMARKET DISCOVERY ===

def get_polymarket_markets(limit=1000, min_volume=1000):
    """
    Fetch all markets from Polymarket (no API key needed).
    Returns list of market dicts with question, prices, volume.
    """
    all_markets = []
    offset = 0
    batch_size = 100
    
    print(f"Fetching Polymarket markets (min volume ${min_volume:,})...")
    
    while offset < 10000:  # Cap at 10k for performance
        url = f"{POLYMARKET_API}/events"
        params = f"?active=true&closed=false&limit={batch_size}&offset={offset}"
        
        try:
            req = urllib.request.Request(url + params)
            req.add_header('User-Agent', 'Nova/1.0')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                events = json.loads(response.read())
        except Exception as e:
            print(f"Error at offset {offset}: {e}")
            break
        
        if not events:
            break
            
        for event in events:
            for m in event.get('markets', []):
                vol = m.get('volume')
                if vol is None:
                    vol = 0
                else:
                    vol = float(vol)
                
                if vol >= min_volume:
                    # Parse prices - can be list or string
                    prices = m.get('outcomePrices', [])
                    try:
                        if isinstance(prices, str):
                            prices = json.loads(prices)
                        if prices and len(prices) >= 2:
                            try:
                                yes_price = float(prices[0]) if prices[0] not in ['0', '0.0', ''] else 0.01
                                no_price = float(prices[1]) if prices[1] not in ['0', '0.0', ''] else 0.01
                            except:
                                yes_price = no_price = 0.5
                        else:
                            yes_price = no_price = 0.5
                    except:
                        yes_price = no_price = 0.5
                    
                    all_markets.append({
                        'id': m.get('id'),
                        'question': m.get('question', ''),
                        'yes_price': yes_price,
                        'no_price': no_price,
                        'volume': vol,
                        'liquidity': m.get('liquinity', 0) or m.get('volume', 0),
                        'ends_at': m.get('endDate'),
                        'group_item_id': m.get('groupItemId'),
                    })
        
        print(f"  Offset {offset}: {len(all_markets)} markets (filtered)")
        offset += batch_size
        
        if len(events) < batch_size:
            break
    
    print(f"Total: {len(all_markets)} markets with volume > ${min_volume:,}")
    return all_markets

def find_edges(markets, min_edge=0.05):
    """
    Find markets where I have an edge vs the market price.
    This is where you'd add your own analysis (weather, sports, etc.)
    For now, just returns markets in the 10-50% range (potentially mispriced).
    """
    edges = []
    
    for m in markets:
        price = m['yes_price']
        
        # Skip extremes
        if price < 0.05 or price > 0.95:
            continue
        
        # Look for mid-range markets (where edge opportunities often are)
        # In production, you'd add your actual analysis here
        # For now, just flag them for review
        edges.append({
            **m,
            'my_estimate': None,  # You'd fill this with your analysis
            'edge': None,
        })
    
    # Sort by volume
    edges.sort(key=lambda x: x['volume'], reverse=True)
    return edges

# === SIMMER EXECUTION ===

def get_simmer_markets():
    """Get markets from Simmer (for execution mapping)."""
    url = f"{SIMMER_API}/api/sdk/markets?status=active&limit=100"
    
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {SIMMER_API_KEY}')
    
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read())
    
    return {m['question'][:50]: m['id'] for m in data.get('markets', [])}

def place_trade(market_id, side, amount, reasoning):
    """Execute trade via Simmer."""
    url = f"{SIMMER_API}/api/sdk/trade"
    
    data = json.dumps({
        "market_id": market_id,
        "side": side,
        "amount": amount,
        "venue": "simmer",
        "reasoning": reasoning
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', f'Bearer {SIMMER_API_KEY}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read())
            return result
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}

# === MAIN ===

def main():
    parser = argparse.ArgumentParser(description="NOVA Trader v4")
    parser.add_argument("--discover", action="store_true", help="Discover markets from Polymarket")
    parser.add_argument("--min-volume", type=int, default=10000, help="Min volume filter")
    parser.add_argument("--edges", action="store_true", help="Show potential edges")
    parser.add_argument("--limit", type=int, default=100, help="Max markets to show")
    args = parser.parse_args()
    
    if args.discover:
        markets = get_polymarket_markets(min_volume=args.min_volume)
        
        # Show top by volume
        print(f"\n=== TOP {args.limit} MARKETS BY VOLUME ===")
        for m in markets[:args.limit]:
            print(f"\${m['volume']:>12,.0f} | YES {m['yes_price']:.2f} | {m['question'][:60]}")
    
    if args.edges:
        markets = get_polymarket_markets(min_volume=args.min_volume)
        edges = find_edges(markets)
        
        print(f"\n=== POTENTIAL EDGES ({len(edges)} markets) ===")
        for m in edges[:args.limit]:
            print(f"YES {m['yes_price']:.2f} | \${m['volume']:>10,.0f} | {m['question'][:55]}")

if __name__ == "__main__":
    main()
