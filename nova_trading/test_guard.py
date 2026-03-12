#!/usr/bin/env python3
"""
Test the pre-trade guard with Simmer virtual trading.
"""

import sys
sys.path.insert(0, '/Users/dr.claw/.openclaw/workspace')
sys.path.insert(0, '/Users/dr.claw/Library/Python/3.9/lib/python/site-packages')

from datetime import datetime, timezone
from simmer_sdk import SimmerClient
import requests
import json

# Load keys
keys = json.load(open('/Users/dr.claw/.nova/keys.json'))
client = SimmerClient(api_key=keys['simmer']['api_key'], venue='sim')

print("=" * 60)
print("NOVA TRADING GUARD TEST")
print("=" * 60)

# Fetch active markets
print("\n[1] Fetching active markets from Simmer...")
try:
    # Try Simmer's API
    markets_resp = client.get_markets()
    print(f"  Markets response type: {type(markets_resp)}")
    
    if isinstance(markets_resp, dict):
        markets = markets_resp.get("data", markets_resp.get("markets", []))
    elif isinstance(markets_resp, list):
        markets = markets_resp
    else:
        markets = []
        
    print(f"  Found {len(markets)} markets")
    
except Exception as e:
    print(f"  Error fetching markets: {e}")
    markets = []

# Show market details
print("\n[2] Market Details:")
for i, m in enumerate(markets[:5]):
    # Handle both dict and object formats
    if hasattr(m, '__dict__'):
        m_dict = m.__dict__
    else:
        m_dict = m
    
    end_date = m_dict.get("end_date_iso") or m_dict.get("endDate") or m_dict.get("end_date") or "N/A"
    print(f"  {i+1}. {m_dict.get('question', m_dict.get('title', 'Unknown'))[:50]}")
    print(f"     ID: {m_dict.get('id', m_dict.get('market_id', 'N/A'))}")
    print(f"     End: {end_date}")
    print(f"     Accepting: {m_dict.get('accepting_orders')}, Active: {m_dict.get('active')}, Closed: {m_dict.get('closed')}")

# Test the guard
print("\n[3] Testing Pre-Trade Guard:")
from nova_trading.guards import validate_market_before_trade, is_truly_tradeable

now = datetime.now(timezone.utc)
tradeable_markets = []
non_tradeable = []

for m in markets:
    # Convert to dict if it's an object
    if hasattr(m, '__dict__'):
        m_dict = m.__dict__
    else:
        m_dict = m
    
    report = validate_market_before_trade(m_dict)
    if report.tradeable:
        tradeable_markets.append(m_dict)
        print(f"  ✓ TRADEABLE: {report.market_question[:40]}")
        print(f"    Reasons: {report.reasons}")
    else:
        non_tradeable.append((m_dict, report))
        print(f"  ✗ BLOCKED: {report.market_question[:40]}")
        print(f"    Reasons: {report.reasons}")

print(f"\n  Summary: {len(tradeable_markets)} tradeable, {len(non_tradeable)} blocked")

# Try a test trade if we have tradeable markets
if tradeable_markets:
    print("\n[4] Attempting Test Trade (virtual, $0.50):")
    
    # Pick the first tradeable market
    test_market = tradeable_markets[0]
    
    # Convert to dict if needed
    if hasattr(test_market, '__dict__'):
        test_market = test_market.__dict__
    
    market_id = test_market.get('id') or test_market.get('market_id')
    
    if market_id:
        print(f"  Market: {test_market.get('question', 'Unknown')}")
        print(f"  Market ID: {market_id}")
        
        try:
            # Test with small amount
            result = client.trade(
                market_id=market_id,
                side='yes',
                amount=0.50,  # Very small test amount
                allow_rebuy=True
            )
            print(f"  ✓ Trade placed: {result}")
        except Exception as e:
            print(f"  Trade error: {e}")
    else:
        print("  No market ID found")
else:
    print("\n[4] No tradeable markets found - cannot test")

# Show balance
print("\n[5] Portfolio:")
try:
    portfolio = client.get_portfolio()
    print(f"  {portfolio}")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
