#!/usr/bin/env python3
"""
nova_market_scanner.py — Nova's market scanner.
Scans for opportunities across markets.
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional


class MarketScanner:
    """Scans markets for trading opportunities."""
    
    def __init__(self):
        self.dexscreener_url = "https://api.dexscreener.com"
        self.coingecko_url = "https://api.coingecko.com/api/v3"
        self.last_scan = None
        self.scan_results = []
    
    async def scan_dexscreener(self, limit: int = 50) -> List[Dict]:
        """Scan DexScreener for trending tokens."""
        url = f"{self.dexscreener_url}/token-boosts/top/v1"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._process_dexscreener(data.get("tokens", []))
        except Exception as e:
            print(f"DexScreener scan error: {e}")
        
        return []
    
    def _process_dexscreener(self, tokens: List[Dict]) -> List[Dict]:
        """Process DexScreener token data."""
        processed = []
        
        for token in tokens:
            try:
                processed.append({
                    "address": token.get("address"),
                    "symbol": token.get("baseToken", {}).get("symbol", "UNKNOWN"),
                    "name": token.get("baseToken", {}).get("name", "Unknown"),
                    "price": token.get("priceUsd", 0),
                    "price_change_24h": token.get("priceChange", {}).get("h24", 0),
                    "liquidity": token.get("liquidity", {}).get("usd", 0),
                    "volume_24h": token.get("volume", {}).get("h24", 0),
                    "txns_24h": token.get("txns", {}).get("h24", {}),
                    "pair_address": token.get("pairAddress"),
                    "dex": token.get("dexId", "unknown"),
                    "scanned_at": datetime.now().isoformat()
                })
            except:
                continue
        
        return processed
    
    async def get_token_pairs(self, token_address: str) -> List[Dict]:
        """Get all pairs for a token."""
        url = f"{self.dexscreener_url}/token-pairs/v1/solana/{token_address}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("pairs", [])
        except Exception as e:
            print(f"Token pairs error: {e}")
        
        return []
    
    async def scan_new_pairs(self, hours: int = 24) -> List[Dict]:
        """Scan for new pairs."""
        url = f"{self.dexscreener_url}/token-profiles/latest/v1"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._process_dexscreener(data.get("tokens", []))
        except Exception as e:
            print(f"New pairs scan error: {e}")
        
        return []
    
    def filter_opportunities(self, tokens: List[Dict], filters: Dict = None) -> List[Dict]:
        """Filter tokens for trading opportunities."""
        if filters is None:
            filters = {
                "min_liquidity": 100000,
                "min_volume": 50000,
                "max_age_hours": 168,  # 1 week
                "exclude_new": True
            }
        
        opportunities = []
        
        for token in tokens:
            # Skip low liquidity
            if token.get("liquidity", 0) < filters.get("min_liquidity", 0):
                continue
            
            # Skip low volume
            if token.get("volume_24h", 0) < filters.get("min_volume", 0):
                continue
            
            # Calculate score
            score = self._calculate_opportunity_score(token)
            token["opportunity_score"] = score
            
            if score > 0.5:
                opportunities.append(token)
        
        # Sort by score
        opportunities.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)
        
        return opportunities
    
    def _calculate_opportunity_score(self, token: Dict) -> float:
        """Calculate opportunity score for a token."""
        score = 0.0
        
        # Liquidity score (0-0.3)
        liquidity = token.get("liquidity", 0)
        if liquidity > 1000000:
            score += 0.3
        elif liquidity > 500000:
            score += 0.2
        elif liquidity > 100000:
            score += 0.1
        
        # Volume score (0-0.3)
        volume = token.get("volume_24h", 0)
        if volume > 1000000:
            score += 0.3
        elif volume > 500000:
            score += 0.2
        elif volume > 100000:
            score += 0.1
        
        # Price momentum (0-0.2)
        change = token.get("price_change_24h", 0)
        if 5 < change < 50:  # Healthy gains
            score += 0.2
        elif 0 < change <= 5:  # Building
            score += 0.1
        
        # Volume spike detection (0-0.2)
        txns = token.get("txns_24h", {})
        buys = txns.get("buys", 0)
        sells = txns.get("sells", 0)
        if buys > sells * 2:  # Strong buying pressure
            score += 0.2
        
        return min(1.0, score)
    
    async def full_scan(self) -> Dict:
        """Run full market scan."""
        # Scan trending
        trending = await self.scan_dexscreener()
        
        # Filter opportunities
        opportunities = self.filter_opportunities(trending)
        
        self.last_scan = datetime.now()
        self.scan_results = opportunities
        
        return {
            "scanned": len(trending),
            "opportunities": len(opportunities),
            "top_opportunities": opportunities[:10],
            "scan_time": self.last_scan.isoformat()
        }


# Singleton
_scanner: Optional[MarketScanner] = None


def get_market_scanner() -> MarketScanner:
    """Get market scanner singleton."""
    global _scanner
    if _scanner is None:
        _scanner = MarketScanner()
    return _scanner


if __name__ == "__main__":
    import json
    scanner = get_market_scanner()
    result = asyncio.run(scanner.full_scan())
    print(json.dumps(result, indent=2))
