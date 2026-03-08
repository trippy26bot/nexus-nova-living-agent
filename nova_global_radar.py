#!/usr/bin/env python3
"""
nova_global_radar.py — Global Market Radar.
Scans ALL markets across ALL categories continuously.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from nova_market_universe import get_market_universe
from nova_market_discovery import get_market_discovery
from nova_category_classifier import get_category_classifier


class GlobalRadar:
    """Global market radar - scans everything continuously."""
    
    def __init__(self):
        self.universe = get_market_universe()
        self.discovery = get_market_discovery()
        self.classifier = get_category_classifier()
        self.last_scan = None
        self.scanning = False
    
    async def full_scan(self) -> Dict:
        """Run full market discovery scan."""
        if self.scanning:
            return {"status": "already_scanning"}
        
        self.scanning = True
        start_time = datetime.now()
        
        try:
            # Discover markets
            markets = await self.discovery.discover_all()
            
            # Classify markets
            classified = self.classifier.classify_batch(markets)
            
            # Add to universe
            for market in classified:
                mid = market.get("id")
                if mid:
                    self.universe.add_market(mid, market)
            
            # Get stats
            stats = self.universe.get_stats()
            
            self.last_scan = datetime.now()
            
            return {
                "status": "complete",
                "markets_discovered": len(markets),
                "total_markets": stats["total_markets"],
                "scan_time": str(datetime.now() - start_time),
                "timestamp": datetime.now().isoformat()
            }
        
        finally:
            self.scanning = False
    
    async def scan_category(self, category: str) -> Dict:
        """Scan specific category."""
        markets = await self.discovery.discover_category(category)
        classified = self.classifier.classify_batch(markets)
        
        for market in classified:
            mid = market.get("id")
            if mid:
                self.universe.add_market(mid, market)
        
        return {
            "category": category,
            "discovered": len(markets),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_opportunities(self, filters: Dict = None) -> List[Dict]:
        """Find trading opportunities."""
        if filters is None:
            filters = {
                "min_volume": 100000,
                "min_liquidity": 50000
            }
        
        markets = self.universe.filter(filters)
        
        # Score opportunities
        scored = []
        for m in markets:
            volume = m.get("volume_24h", 0) or m.get("volume", 0)
            score = min(100, volume / 1000000)  # Simple scoring
            
            scored.append({
                **m,
                "opportunity_score": round(score, 2)
            })
        
        # Sort by score
        scored.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)
        
        return scored[:50]  # Top 50
    
    def get_category_summary(self) -> Dict:
        """Get summary by category."""
        return self.universe.get_stats()
    
    def search_markets(self, query: str) -> List[Dict]:
        """Search markets."""
        return self.universe.search(query)
    
    def get_status(self) -> Dict:
        """Get radar status."""
        return {
            "scanning": self.scanning,
            "last_scan": self.last_scan.isoformat() if self.last_scan else None,
            "stats": self.universe.get_stats()
        }


_radar: Optional[GlobalRadar] = None

def get_global_radar() -> GlobalRadar:
    """Get radar singleton."""
    global _radar
    if _radar is None:
        _radar = GlobalRadar()
    return _radar


if __name__ == "__main__":
    import asyncio
    
    async def test():
        radar = get_global_radar()
        print("Running full scan...")
        result = await radar.full_scan()
        print(json.dumps(result, indent=2))
        
        print("\nOpportunities:")
        ops = radar.get_opportunities()
        print(f"Found {len(ops)} opportunities")
        
        print("\nCategory summary:")
        print(json.dumps(radar.get_category_summary(), indent=2))
    
    asyncio.run(test())
