#!/usr/bin/env python3
"""
Test a real virtual trade with the guard in place.
"""

import sys
sys.path.insert(0, '/Users/dr.claw/.openclaw/workspace')
sys.path.insert(0, '/Users/dr.claw/Library/Python/3.9/lib/python/site-packages')

from datetime import datetime, timezone
from simmer_sdk import SimmerClient
from nova_trading.guards import validate_market_before_trade, MarketNotTradeableError
from nova_trading.executor import execute_order
import json

# Load keys
keys = json.load(open('/Users/dr.claw/.nova/keys.json'))
client = SimmerClient(api_key=keys['simmer']['api_key'], venue='sim')

print("=" * 60)
print("GUARD-ENFORCED VIRTUAL TRADE TEST")
print("=" * 60)

# Get markets
markets = client.get_markets()
print(f"\n[1] Found {len(markets)} markets")

# Find a good one (first one)
m = markets[0]
market_id = m.id if hasattr(m, 'id') else m.__dict__.get('id')
market_question = m.question if hasattr(m, 'question') else m.__dict__.get('question', 'Unknown')

print(f"\n[2] Selected market: {market_question}")
print(f"    ID: {market_id}")

# Convert to dict for guard
market_dict = m.__dict__ if hasattr(m, '__dict__') else m
market_dict["_fetched_at"] = datetime.now(timezone.utc)

# PRE-TRADE VALIDATION
print(f"\n[3] Running pre-trade guard...")
report = validate_market_before_trade(market_dict)

print(f"    Tradeable: {report.tradeable}")
print(f"    Reasons: {report.reasons}")

if not report.tradeable:
    print(f"\n    ❌ GUARD BLOCKED THE TRADE")
    print(f"    This is what we want - no money lost!")
else:
    print(f"\n    ✓ Guard passed - executing trade...")
    
    # Execute the trade via executor
    try:
        result = execute_order(
            market=market_dict,
            market_id=market_id,
            side='yes',
            amount=0.50,  # Very small test
            client=client,
            mode="virtual"
        )
        
        if result.get("success"):
            print(f"\n    ✓ TRADE EXECUTED: {result}")
        else:
            print(f"\n    ❌ Trade failed: {result.get('error')}")
            
    except MarketNotTradeableError as e:
        print(f"\n    ❌ GUARD BLOCKED: {e}")
    except Exception as e:
        print(f"\n    ❌ Error: {e}")

# Show balance
print("\n[4] Portfolio:")
try:
    portfolio = client.get_portfolio()
    print(f"    {portfolio}")
except Exception as e:
    print(f"    Error: {e}")

print("\n" + "=" * 60)
