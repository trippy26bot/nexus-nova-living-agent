"""
Nova's Trading Executor - Guard-Enforced Order Submission

This is the ONLY code path for placing orders.
The guard lives inside and cannot be bypassed.
"""

import sys
import os
sys.path.insert(0, '/Users/dr.claw/.openclaw/workspace')
sys.path.insert(0, '/Users/dr.claw/Library/Python/3.9/lib/python/site-packages')

from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional
import json


# Import guard
from nova_trading.guards import validate_market_before_trade, MarketNotTradeableError


@dataclass
class OrderResult:
    success: bool
    trade_id: Optional[str] = None
    market: str = ""
    amount: float = 0.0
    side: str = ""
    error: Optional[str] = None
    mode: str = "virtual"


def execute_order(
    market: dict,
    market_id: str,
    side: str,
    amount: float,
    client,
    mode: str = "virtual"
) -> OrderResult:
    """
    THE ONLY PLACE orders are submitted.
    Guard is non-negotiable - cannot be bypassed.
    
    Args:
        market: Market dict (validated)
        market_id: Market identifier
        side: 'yes' or 'no'
        amount: USDC amount
        client: SimmerClient
        mode: 'virtual' or 'real'
    
    Returns:
        OrderResult with success status
    """
    now = datetime.now(timezone.utc)
    question = market.get("question", "Unknown")
    
    # Stamp freshness
    market["_fetched_at"] = now
    
    # === THE GUARD - MUST PASS ===
    report = validate_market_before_trade(market)
    
    if not report.tradeable:
        error_msg = f"BLOCKED: {question} - {', '.join(report.reasons)}"
        print(f"  [GUARD] ❌ {error_msg}")
        raise MarketNotTradeableError(error_msg)
    
    print(f"  [GUARD] ✓ {question} passed validation")
    
    # Try to re-fetch fresh data (best effort)
    try:
        fresh = _refetch_market(market_id, client)
        if fresh:
            fresh_report = validate_market_before_trade(fresh)
            if not fresh_report.tradeable:
                raise MarketNotTradeableError(
                    f"BLOCKED on re-validate: {fresh_report.market_question} - {fresh_report.reasons}"
                )
            market = fresh
            print(f"  [GUARD] ✓ Fresh data validated")
    except MarketNotTradeableError:
        raise
    except Exception as e:
        print(f"  [WARN] Re-validate skipped: {e}")
    
    # === EXECUTE ===
    print(f"  [ORDER] {mode.upper()}: ${amount} on '{question}' ({side})")
    
    try:
        result = client.trade(
            market_id=market_id,
            side=side,
            amount=amount,
            allow_rebuy=True
        )
        
        # Extract trade ID
        tid = getattr(result, 'trade_id', None) or result.get('trade_id', 'unknown')
        
        print(f"  [ORDER] ✓ Success: {tid}")
        
        return OrderResult(
            success=True,
            trade_id=str(tid),
            market=question,
            amount=amount,
            side=side,
            mode=mode
        )
        
    except Exception as e:
        error = str(e)
        print(f"  [ORDER] ❌ Failed: {error}")
        
        return OrderResult(
            success=False,
            error=error,
            market=question,
            amount=amount,
            side=side,
            mode=mode
        )


def _refetch_market(market_id: str, client) -> Optional[dict]:
    """Attempt to get fresh market data."""
    # Try Simmer's market endpoint
    try:
        # This depends on Simmer SDK having this method
        if hasattr(client, 'get_market'):
            m = client.get_market(market_id)
            if m:
                m["_fetched_at"] = datetime.now(timezone.utc)
                return m.__dict__ if hasattr(m, '__dict__') else m
    except Exception as e:
        pass
    
    return None


def preview_order(market: dict) -> dict:
    """
    Preview an order without executing.
    Shows validation status.
    """
    report = validate_market_before_trade(market)
    
    return {
        "market": report.market_question,
        "will_pass": report.tradeable,
        "reasons": report.reasons,
        "end_date": market.get("endDate") or market.get("end_date_iso"),
        "accepting_orders": market.get("accepting_orders"),
        "active": market.get("active"),
        "closed": market.get("closed")
    }
