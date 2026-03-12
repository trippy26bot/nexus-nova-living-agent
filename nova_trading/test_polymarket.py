#!/usr/bin/env python3
"""
Test the pre-trade guard - check Polymarket for live markets
"""

import sys
sys.path.insert(0, '/Users/dr.claw/.openclaw/workspace')
sys.path.insert(0, '/Users/dr.claw/Library/Python/3.9/lib/python/site-packages')

from datetime import datetime, timezone
import requests
import json

print("=" * 60)
print("CHECKING POLYMARKET FOR LIVE MARKETS")
print("=" * 60)

# Fetch from Polymarket Gamma API
print("\n[1] Fetching from Polymarket Gamma API...")
try:
    resp = requests.get(
        "https://gamma-api.polymarket.com/markets",
        params={"active": "true", "closed": "false", "limit": 10},
        timeout=15
    )
    pm_markets = resp.json()
    print(f"  Found {len(pm_markets)} Polymarket markets")
    
    for i, m in enumerate(pm_markets[:5]):
        print(f"\n  {i+1}. {m.get('question', 'N/A')[:50]}")
        print(f"     ConditionID: {m.get('conditionId', 'N/A')[:20]}...")
        print(f"     End Date: {m.get('endDate')}")
        print(f"     ClobTokenIDs: {m.get('clobTokenIds', [])[:2]}")
        print(f"     Active: {m.get('active')}")
        print(f"     Closed: {m.get('closed')}")
        print(f"     Accepting Orders: {m.get('acceptingOrders')}")
        
except Exception as e:
    print(f"  Error: {e}")
    pm_markets = []

# Now test with Simmer's get_market for details
print("\n[2] Checking Simmer market details...")

try:
    from simmer_sdk import SimmerClient
    keys = json.load(open('/Users/dr.claw/.nova/keys.json'))
    client = SimmerClient(api_key=keys['simmer']['api_key'], venue='sim')
    
    # Get markets list
    markets = client.get_markets()
    print(f"  Simmer markets: {len(markets)}")
    
    # Try to get details on one market
    if markets:
        m = markets[0]
        mid = m.id if hasattr(m, 'id') else m.__dict__.get('id')
        print(f"\n  Fetching details for: {mid}")
        
        # This might give us more fields
        try:
            detail = client.get_market(mid)
            print(f"  Market detail keys: {list(detail.keys()) if isinstance(detail, dict) else type(detail)}")
            if isinstance(detail, dict):
                for k, v in detail.items():
                    if k not in ('question', 'id'):
                        print(f"    {k}: {v}")
        except Exception as e:
            print(f"  Could not get detail: {e}")
            
except Exception as e:
    print(f"  Simmer error: {e}")

# Test guard on Polymarket data
print("\n[3] Testing Guard on Polymarket Data:")
from nova_trading.guards import validate_market_before_trade

tradeable = []
for m in pm_markets:
    # Map Polymarket fields to our expected format
    pm_mapped = {
        "question": m.get("question"),
        "endDate": m.get("endDate"),
        "accepting_orders": m.get("acceptingOrders"),
        "active": m.get("active"),
        "closed": m.get("closed"),
        "archived": m.get("archived"),
        "_fetched_at": datetime.now(timezone.utc)
    }
    
    report = validate_market_before_trade(pm_mapped)
    if report.tradeable:
        tradeable.append(m)
        print(f"  ✓ {report.market_question[:40]}")
    else:
        print(f"  ✗ {report.market_question[:40]}: {report.reasons}")

print(f"\n  Polymarket: {len(tradeable)} tradeable out of {len(pm_markets)}")

print("\n" + "=" * 60)
