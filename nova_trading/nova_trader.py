"""
Nova's Trading System - Signal & Execution Separation

Signal: Reads markets from Polymarket Gamma API (public, no auth)
Execution: Places trades on Simmer (requires keys)
"""

import os
import sys
sys.path.insert(0, '/Users/dr.claw/.openclaw/workspace')

import json
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional
import requests

# Load keys
KEYS_PATH = os.path.expanduser("~/.nova/keys.json")
if os.path.exists(KEYS_PATH):
    KEYS = json.load(open(KEYS_PATH))
else:
    KEYS = {}


@dataclass
class MarketSignal:
    """A tradeable market from Polymarket."""
    question: str
    condition_id: str
    yes_token_id: str
    no_token_id: str
    end_date: Optional[datetime]
    active: bool = True
    closed: bool = False
    url: str = ""
    
    @property
    def is_live(self) -> bool:
        """Event hasn't happened yet."""
        if self.end_date is None:
            return True
        return self.end_date > datetime.now(timezone.utc)


@dataclass
class ScoredSignal:
    """A signal with a score for ranking."""
    signal: MarketSignal
    score: float
    reasons: list[str]


def score_opportunity(signal: MarketSignal, strategy: 'StrategyState' = None) -> ScoredSignal:
    """
    Score a market opportunity. Higher = better.
    
    Factors:
    - Time to end (closer = better for actionability)
    - Price range (mid-range = more interesting)
    - Category preference
    """
    score = 0.5  # Base
    reasons = []
    
    now = datetime.now(timezone.utc)
    
    # 1. Time factor (prefer 1-24 hour windows)
    if signal.end_date:
        hours_until = (signal.end_date - now).total_seconds() / 3600
        
        if hours_until < 1:
            score += 0.1
            reasons.append(f"very soon ({hours_until:.1f}h)")
        elif 1 <= hours_until <= 6:
            score += 0.3
            reasons.append(f"good window ({hours_until:.1f}h)")
        elif 6 < hours_until <= 24:
            score += 0.2
            reasons.append(f"decent window ({hours_until:.1f}h)")
        elif hours_until > 168:  # > 1 week
            score -= 0.2
            reasons.append(f"too far out ({hours_until:.0f}h)")
        else:
            reasons.append(f"medium window ({hours_until:.1f}h)")
    else:
        # No end date (Simmer markets) - give neutral score
        score += 0.1
        reasons.append("no end date (Simmer-style)")
    
    # 2. Question quality
    q = signal.question.lower()
    
    # Crypto/politics get boost (predictable volume)
    if any(x in q for x in ['bitcoin', 'btc', 'ethereum', 'solana', 'crypto', 'trump', 'election']):
        score += 0.15
        reasons.append("high-interest topic")
    
    # Sports have clear resolution
    if any(x in q for x in ['win', 'vs', 'score', 'game', 'match']):
        score += 0.1
        reasons.append("sports/clear outcome")
    
    # Avoid weird long-shots
    if any(x in q for x in ['will', 'will']):
        score += 0.05  # Standard question format
    
    # 3. Strategy preferences
    if strategy:
        prefs = strategy.state
        
        # Category preference
        pref_cats = prefs.get('preferred_categories', [])
        avoid_cats = prefs.get('avoid_categories', [])
        
        if pref_cats and any(c in q for c in pref_cats):
            score += 0.1
            reasons.append("preferred category")
        
        if avoid_cats and any(c in q for c in avoid_cats):
            score -= 0.2
            reasons.append("avoided category")
    
    # Cap score 0-1
    score = max(0.0, min(1.0, score))
    
    return ScoredSignal(signal=signal, score=score, reasons=reasons)


class PolymarketSignal:
    """Finds opportunities on Polymarket (read-only, no auth)."""
    
    API_URL = "https://gamma-api.polymarket.com/markets"
    
    def scan(self, 
              limit: int = 20,
              categories: list[str] = None,
              exclude_categories: list[str] = None,
              min_end_hours: int = 1) -> list[MarketSignal]:
        """
        Scan Polymarket for tradeable markets.
        
        Args:
            limit: Max markets to fetch
            categories: Only these categories (if None, all)
            exclude_categories: Skip these
            min_end_hours: Market must end at least this many hours from now
        """
        params = {
            "active": "true",
            "closed": "false", 
            "limit": limit
        }
        
        try:
            resp = requests.get(self.API_URL, params=params, timeout=15)
            markets = resp.json()
        except Exception as e:
            print(f"[SIGNAL] API error: {e}")
            return []
        
        signals = []
        now = datetime.now(timezone.utc)
        
        for m in markets:
            # Parse end date
            end_str = m.get("endDate")
            end_date = None
            if end_str:
                try:
                    end_date = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                except:
                    pass
            
            # Skip if ended too soon
            if end_date:
                hours_until = (end_date - now).total_seconds() / 3600
                if hours_until < min_end_hours:
                    continue
            
            # Get token IDs
            token_ids = m.get("clobTokenIds", [])
            if len(token_ids) < 2:
                continue
            
            signal = MarketSignal(
                question=m.get("question", "Unknown"),
                condition_id=m.get("conditionId", ""),
                yes_token_id=token_ids[0],
                no_token_id=token_ids[1],
                end_date=end_date,
                active=m.get("active", True),
                closed=m.get("closed", False),
                url=f"https://polymarket.com/market/{m.get('conditionId', '')}"
            )
            
            signals.append(signal)
        
        print(f"[SIGNAL] Found {len(signals)} tradeable markets")
        return signals


# Default config
DEFAULT_CONFIG = {
    "opportunity_threshold": 0.30,  # Min score to trade (lowered for testing)
    "min_price": 0.10,   # Don't trade odds < 10%
    "max_price": 0.90,   # Don't trade odds > 90%
    "preferred_categories": ["crypto", "politics"],
    "avoid_categories": ["nsfw", "esports"],
    "bet_size_usdc": 5.0,  # Simmer min bet is $5
    "max_daily_trades": 10,
    "dry_run": True,  # Default to dry run
}


class StrategyState:
    """Persists strategy parameters across sessions."""
    
    def __init__(self, path: str = None):
        self.path = path or os.path.expanduser("~/.nova/trading_strategy.json")
        self.state = DEFAULT_CONFIG.copy()
        self.trade_count = 0
        self.wins = 0
        self.load()
    
    def load(self):
        """Load state with safe fallback."""
        try:
            if os.path.exists(self.path):
                saved = json.load(open(self.path))
                self.state.update(saved)
                self.trade_count = saved.get("trade_count", 0)
                self.wins = saved.get("wins", 0)
                print(f"[STRATEGY] Loaded: {self.trade_count} trades, {self.wins} wins")
        except Exception as e:
            print(f"[STRATEGY] Load error, using defaults: {e}")
    
    def save(self):
        """Persist state safely."""
        try:
            data = {**self.state, "trade_count": self.trade_count, "wins": self.wins}
            # Write to temp first, then rename (atomic)
            tmp = self.path + ".tmp"
            with open(tmp, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, self.path)
        except Exception as e:
            print(f"[STRATEGY] Save error: {e}")
    
    def record_trade(self, won: bool = None):
        """Record a trade result."""
        self.trade_count += 1
        if won is not None and won:
            self.wins += 1
        
        # Refine every 25 trades
        if self.trade_count % 25 == 0:
            self.refine()
    
    def refine(self):
        """Adjust parameters based on performance."""
        win_rate = self.wins / self.trade_count if self.trade_count > 0 else 0.5
        
        print(f"[STRATEGY] Refining at {self.trade_count} trades, win rate: {win_rate:.1%}")
        
        # Adjust based on win rate
        if win_rate > 0.6:
            # Doing well - slightly larger bets
            self.state["bet_size_usdc"] = min(5.0, self.state["bet_size_usdc"] * 1.1)
        elif win_rate < 0.4:
            # Doing poorly - smaller bets, tighter criteria
            self.state["bet_size_usdc"] = max(0.25, self.state["bet_size_usdc"] * 0.8)
            self.state["opportunity_threshold"] = min(0.8, self.state["opportunity_threshold"] + 0.05)
        
        self.save()
    
    def should_trade(self, opportunity_score: float) -> bool:
        """Should we take this trade?"""
        if self.state["dry_run"]:
            print(f"[STRATEGY] Dry run mode - would trade: {opportunity_score:.2f}")
            return False
        return opportunity_score >= self.state["opportunity_threshold"]


def check_simmer_connection(client) -> bool:
    """Verify Simmer is reachable."""
    try:
        markets = client.get_markets()
        print(f"[SIMMER] ✓ Connected - {len(markets)} markets")
        return True
    except Exception as e:
        print(f"[SIMMER] ✗ Error: {e}")
        return False


class SimmerScanner:
    """Scan Simmer markets directly."""
    
    def __init__(self, client):
        self.client = client
    
    def scan(self, limit: int = 50) -> list:
        """Get active markets from Simmer."""
        try:
            markets = self.client.get_markets()
            return markets[:limit]
        except Exception as e:
            print(f"[SIMMER] Scan error: {e}")
            return []


def match_signal_to_simmer(signal: MarketSignal, simmer_markets: list) -> tuple:
    """
    Try to find a Simmer market matching the Polymarket signal.
    Returns (simmer_market, market_id) or (None, None)
    """
    # Normalize question for comparison
    q = signal.question.lower()
    
    # Extract key terms
    keywords = [w for w in q.split() if len(w) > 3]
    
    for m in simmer_markets:
        m_question = m.question.lower() if hasattr(m, 'question') else m.__dict__.get('question', '').lower()
        
        # Check keyword overlap
        matches = sum(1 for kw in keywords if kw in m_question)
        
        if matches >= 2:  # At least 2 keywords match
            market_id = m.id if hasattr(m, 'id') else m.__dict__.get('id')
            return m, market_id
    
    return None, None


def run(dry_run: bool = None):
    """Main run loop."""
    print("=" * 50)
    print("NOVA TRADING SYSTEM")
    print("=" * 50)
    
    # Load strategy
    strategy = StrategyState()
    
    # Override dry run if specified
    if dry_run is not None:
        strategy.state["dry_run"] = dry_run
    
    print(f"\n[CONFIG]")
    print(f"  Dry run: {strategy.state['dry_run']}")
    print(f"  Bet size: ${strategy.state['bet_size_usdc']:.2f} (min $5)")
    print(f"  Threshold: {strategy.state['opportunity_threshold']:.0%}")
    
    # Create Simmer client
    from simmer_sdk import SimmerClient
    client = SimmerClient(api_key=KEYS.get('simmer', {}).get('api_key', ''), venue='sim')
    
    # Check Simmer connection (skip in dry run)
    if not strategy.state["dry_run"]:
        if not check_simmer_connection(client):
            print("[ERROR] Cannot connect to Simmer. Run with --dry-run first.")
            return
    
    # Scan for signals - prioritize Simmer for execution
    print(f"\n[SCAN] Scanning Simmer markets...")
    simmer_scanner = SimmerScanner(client)
    simmer_markets = simmer_scanner.scan(limit=50)
    print(f"[SIMMER] Found {len(simmer_markets)} markets")
    
    # Convert to signals for unified scoring
    signals = []
    for m in simmer_markets:
        mdict = m.__dict__ if hasattr(m, '__dict__') else m
        sig = MarketSignal(
            question=mdict.get('question', 'Unknown'),
            condition_id=mdict.get('id', ''),
            yes_token_id='',
            no_token_id='',
            end_date=None,
            active=True,
            closed=False
        )
        signals.append(sig)
    
    if not signals:
        print("[SCAN] No markets found")
        return
    
    print(f"\n[SCAN] Top opportunities:")
    
    print(f"\n[SCAN] Top opportunities:")
    for i, s in enumerate(signals[:5]):
        hours = (s.end_date - datetime.now(timezone.utc)).total_seconds() / 3600 if s.end_date else 999
        print(f"  {i+1}. {s.question[:40]}...")
        print(f"     Ends in {hours:.1f}h - {'LIVE' if s.is_live else 'ENDED'}")
    
    # Score opportunities
    print(f"\n[SCORING] Ranking opportunities...")
    scored = [score_opportunity(s, strategy) for s in signals]
    scored.sort(key=lambda x: x.score, reverse=True)
    
    threshold = strategy.state["opportunity_threshold"]
    actionable = [s for s in scored if s.score >= threshold]
    
    print(f"\n[SCORING] Top ranked:")
    for i, s in enumerate(scored[:5]):
        marker = "→" if s.score >= threshold else " "
        print(f"  {marker} {s.score:.0%}: {s.signal.question[:35]}...")
        print(f"          {', '.join(s.reasons[:2]) if s.reasons else 'no reasons'}")
    
    # Execute if not dry run
    if not strategy.state["dry_run"] and actionable:
        print(f"\n[EXEC] Attempting {len(actionable)} trades...")
        
        from nova_trading.executor import execute_order
        
        trades_made = 0
        for scored_signal in actionable[:3]:  # Max 3 trades
            s = scored_signal.signal
            
            # Use condition_id as market_id (Simmer uses UUIDs)
            if s.condition_id:
                market_id = s.condition_id
                
                # Create market dict from signal
                mdict = {
                    'question': s.question,
                    '_fetched_at': datetime.now(timezone.utc)
                }
                
                print(f"  → Trading: {s.question[:35]}...")
                
                try:
                    result = execute_order(
                        market=mdict,
                        market_id=market_id,
                        side='yes',
                        amount=strategy.state['bet_size_usdc'],
                        client=client,
                        mode='virtual'
                    )
                    
                    if result.success:
                        print(f"    ✓ Success: {result.trade_id}")
                        trades_made += 1
                    else:
                        print(f"    ✗ Failed: {result.error}")
                        
                except Exception as e:
                    print(f"    ✗ Error: {e}")
        
        print(f"\n[EXEC] Completed {trades_made} trades")
        
    elif strategy.state["dry_run"] and actionable:
        print(f"\n[DRY RUN] Would execute {len(actionable)} trades above {threshold:.0%} threshold")
        for s in actionable[:3]:
            print(f"  → {s.score:.0%}: {s.signal.question[:40]}...")
    
    elif not actionable:
        print(f"\n[SCORING] No opportunities meet {threshold:.0%} threshold")
    
    print("\n" + "=" * 50)
    print("SCAN COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    import sys
    dry = "--live" not in sys.argv
    run(dry_run=dry)
