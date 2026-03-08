#!/usr/bin/env python3
"""
nova_market_universe.py — Global Market Registry.
Tracks ALL markets across ALL categories.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class MarketUniverse:
    """Global market registry - discovers and tracks all markets."""
    
    def __init__(self):
        self.markets = {}  # market_id -> market data
        self.categories = defaultdict(list)
        self.chains = defaultdict(list)
        self.path = Path(__file__).parent
        self._load()
    
    def _load(self):
        """Load saved markets."""
        file_path = self.path / "market_universe.json"
        if file_path.exists():
            try:
                data = json.loads(file_path.read_text())
                self.markets = data.get("markets", {})
                self.categories = defaultdict(list, data.get("categories", {}))
                self.chains = defaultdict(list, data.get("chains", {}))
            except:
                pass
    
    def _save(self):
        """Save markets."""
        file_path = self.path / "market_universe.json"
        file_path.write_text(json.dumps({
            "markets": self.markets,
            "categories": dict(self.categories),
            "chains": dict(self.chains)
        }, indent=2))
    
    def add_market(self, market_id: str, data: Dict):
        """Add a market to the universe."""
        self.markets[market_id] = {
            **data,
            "discovered_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Index by category
        category = data.get("category", "unknown")
        if market_id not in self.categories[category]:
            self.categories[category].append(market_id)
        
        # Index by chain
        chain = data.get("chain", "unknown")
        if market_id not in self.chains[chain]:
            self.chains[chain].append(market_id)
        
        self._save()
    
    def add_batch(self, markets: List[Dict]):
        """Add multiple markets."""
        for m in markets:
            mid = m.get("id") or m.get("address") or m.get("symbol", "")
            if mid:
                self.add_market(mid, m)
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Get all markets in a category."""
        market_ids = self.categories.get(category, [])
        return [self.markets[mid] for mid in market_ids if mid in self.markets]
    
    def get_by_chain(self, chain: str) -> List[Dict]:
        """Get all markets on a chain."""
        market_ids = self.chains.get(chain, [])
        return [self.markets[mid] for mid in market_ids if mid in self.markets]
    
    def search(self, query: str) -> List[Dict]:
        """Search markets by name/symbol."""
        query = query.lower()
        results = []
        
        for market in self.markets.values():
            name = market.get("name", "").lower()
            symbol = market.get("symbol", "").lower()
            
            if query in name or query in symbol:
                results.append(market)
        
        return results
    
    def filter(self, filters: Dict) -> List[Dict]:
        """Filter markets by criteria."""
        results = []
        
        for market in self.markets.values():
            match = True
            
            if "min_volume" in filters:
                if market.get("volume_24h", 0) < filters["min_volume"]:
                    match = False
            
            if "min_liquidity" in filters:
                if market.get("liquidity", 0) < filters["min_liquidity"]:
                    match = False
            
            if "category" in filters:
                if market.get("category") != filters["category"]:
                    match = False
            
            if "chain" in filters:
                if market.get("chain") != filters["chain"]:
                    match = False
            
            if match:
                results.append(market)
        
        return results
    
    def get_stats(self) -> Dict:
        """Get universe statistics."""
        return {
            "total_markets": len(self.markets),
            "categories": {cat: len(ids) for cat, ids in self.categories.items()},
            "chains": {chain: len(ids) for chain, ids in self.chains.items()},
            "discovered_today": sum(
                1 for m in self.markets.values() 
                if m.get("discovered_at", "").startswith(datetime.now().strftime("%Y-%m-%d"))
            )
        }


_universe: Optional[MarketUniverse] = None

def get_market_universe() -> MarketUniverse:
    """Get market universe singleton."""
    global _universe
    if _universe is None:
        _universe = MarketUniverse()
    return _universe


if __name__ == "__main__":
    universe = get_market_universe()
    print(json.dumps(universe.get_stats(), indent=2))
