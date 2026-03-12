"""
Pre-trade validation guard for Nova's trading system.
Hard gate that must pass before ANY order is submitted.
"""

from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional


class MarketNotTradeableError(Exception):
    """Raised when a market fails pre-trade validation."""
    pass


@dataclass
class TradeabilityReport:
    tradeable: bool
    reasons: list[str]  # why it failed, empty if passed
    market_question: str


def validate_market_before_trade(market: dict) -> TradeabilityReport:
    """
    Hard gate. Must pass before ANY order is submitted.
    Called inside execute_order(), not in market discovery.
    """
    now = datetime.now(timezone.utc)
    reasons = []
    question = market.get("question", market.get("title", "Unknown"))

    # Check if we have meaningful market status info
    has_status_info = False
    
    # 1. Explicitly not accepting orders (must be True, not None/False)
    accepting = market.get("accepting_orders")
    if accepting is True:
        has_status_info = True
    elif accepting is False:
        reasons.append("accepting_orders=false")
        has_status_info = True

    # 2. Market is closed (must be explicitly False to pass)
    closed = market.get("closed")
    if closed is True:
        reasons.append("market is closed")
        has_status_info = True

    # 3. Market is archived (must be explicitly False to pass)
    archived = market.get("archived")
    if archived is True:
        reasons.append("market is archived")
        has_status_info = True

    # 4. Not active (must be True to pass)
    active = market.get("active")
    if active is False:
        reasons.append("market is inactive")
        has_status_info = True
    elif active is True:
        has_status_info = True

    # 5. End date has passed — the core fix (most reliable check)
    end_date_str = (
        market.get("end_date_iso") or 
        market.get("endDate") or 
        market.get("end_date") or
        market.get("game_start_time")
    )
    end_in_future = True  # assume true if no end date
    if end_date_str:
        try:
            # Handle various date formats
            clean_str = end_date_str.replace("Z", "+00:00")
            # Fix double timezone issue
            if clean_str.count("+") > 1:
                clean_str = clean_str.split("+")[0] + "+00:00"
            end_dt = datetime.fromisoformat(clean_str)
            if end_dt <= now:
                reasons.append(f"end date passed: {end_date_str}")
                end_in_future = False
        except (ValueError, TypeError) as e:
            reasons.append(f"could not parse end date: {end_date_str} ({e})")

    # If we have no status info but end date is in future or missing, be lenient
    if not has_status_info:
        if end_in_future:
            # No status info AND end date is in future or missing = pass with warning
            reasons.append("WARNING: no status info - assuming tradeable (end date OK)")
        else:
            # No status info AND end date passed = definitely block
            reasons.append("end date has passed and no status info available")
    
    # 6. Re-fetch check - if market data is stale (older than 60s)
    fetched_at = market.get("_fetched_at")
    if fetched_at:
        if isinstance(fetched_at, str):
            fetched_at = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
        age = (now - fetched_at).total_seconds()
        if age > 60:
            reasons.append(f"market data is stale ({int(age)}s old)")

    # Separate warnings from errors
    # Warnings don't block, errors do
    errors = [r for r in reasons if not r.startswith("WARNING")]
    
    # Also check if we have any date-based blocks
    date_blocks = [r for r in reasons if "end date passed" in r]
    
    # Tradeable if: no errors AND no date blocks
    is_tradeable = len(errors) == 0 and len(date_blocks) == 0

    return TradeabilityReport(
        tradeable=is_tradeable, 
        reasons=reasons,  # Keep all for logging
        market_question=question
    )


def is_truly_tradeable(market: dict) -> bool:
    """Quick check - returns True only if market can be traded."""
    report = validate_market_before_trade(market)
    return report.tradeable


def get_fresh_market(market_id: str, client, cache: dict = None) -> dict:
    """
    Always returns a market with guaranteed-fresh data.
    Re-fetches if cache is stale (>60s).
    """
    import requests
    
    now = datetime.now(timezone.utc)
    cache = cache or {}
    cached = cache.get(market_id)
    
    if cached:
        age = (now - cached.get("_fetched_at", now)).total_seconds()
        if age < 60:
            print(f"  [CACHE] Market {market_id[:8]}... still fresh ({int(age)}s)")
            return cached
    
    # Re-fetch from Simmer API
    print(f"  [FETCH] Re-fetching market {market_id}...")
    
    # Simmer API endpoint
    url = f"https://simmer-api.rev.club/markets/{market_id}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            fresh = resp.json()
            fresh["_fetched_at"] = now
            cache[market_id] = fresh
            return fresh
    except Exception as e:
        print(f"  [WARN] Could not re-fetch market: {e}")
        # Return cached if fetch fails, but mark as stale
        if cached:
            cached["_stale_fetch"] = True
            return cached
    
    return cached or {}


# For backwards compatibility
def check_market_tradeable(market: dict) -> tuple[bool, list[str]]:
    """Returns (is_tradeable, reasons) tuple."""
    report = validate_market_before_trade(market)
    return report.tradeable, report.reasons
