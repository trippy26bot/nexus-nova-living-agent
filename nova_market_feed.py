#!/usr/bin/env python3
"""
nova_market_feed.py — Live Market Data Connector.
Feeds real-time data into Nova's brain.
"""

import json
import asyncio
import aiohttp
import os
from datetime import datetime
from typing import Dict, List, Optional


class MarketFeed:
    """Live market data feed."""
    
    def __init__(self):
        self.helius_key = os.environ.get("HELIUS_API_KEY", "")
        self.last_update = None
    
    async def get_token_prices(self, tokens: List[str]) -> List[Dict]:
        """Get prices from Birdeye (free, no key)."""
        markets = []
        
        # Use Birdeye API (free)
        url = "https://api.birdeye.so/public/v1/multi_price"
        params = {"list_address": ",".join(tokens[:10])}  # Limit to 10
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for addr, info in data.get("data", {}).items():
                            markets.append({
                                "address": addr,
                                "price": info.get("value", 0),
                                "source": "birdeye"
                            })
        except Exception as e:
            print(f"Birdeye error: {e}")
        
        return markets
    
    async def get_dex_pairs(self, chain: str = "solana") -> List[Dict]:
        """Get trading pairs from CoinGecko."""
        pairs = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get top coins from CoinGecko
                url = "https://api.coingecko.com/api/v3/coins/markets"
                params = {
                    "vs_currency": "usd",
                    "order": "volume_desc",
                    "per_page": 50,
                    "page": 1
                }
                
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for coin in data:
                            pairs.append({
                                "pair_address": coin.get("id"),
                                "base_token": coin.get("symbol", "").upper(),
                                "quote_token": "USD",
                                "price": coin.get("current_price"),
                                "liquidity": coin.get("market_cap", 0),
                                "volume_24h": coin.get("total_volume", 0),
                                "change_24h": coin.get("price_change_percentage_24h", 0),
                                "chain": "multi",
                                "source": "coingecko"
                            })
        except Exception as e:
            print(f"CoinGecko error: {e}")
        
        return pairs
    
    async def get_whale_activity(self, wallets: List[str]) -> List[Dict]:
        """Get whale wallet activity via Helius."""
        if not self.helius_key:
            return [{"error": "No Helius API key"}]
        
        activity = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for wallet in wallets[:5]:  # Limit requests
                    url = f"https://api.helius.xyz/v0/addresses/{wallet}/transactions"
                    params = {"api-key": self.helius_key, "limit": 5}
                    
                    async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        if resp.status == 200:
                            txs = await resp.json()
                            if txs:
                                activity.append({
                                    "wallet": wallet,
                                    "tx_count": len(txs),
                                    "recent": txs[0].get("type") if txs else None
                                })
        except Exception as e:
            activity.append({"error": str(e)})
        
        return activity
    
    async def get_global_market_data(self) -> Dict:
        """Get combined market data."""
        # Get trending pairs
        dex_pairs = await self.get_dex_pairs()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "dex_pairs": dex_pairs,
            "total_pairs": len(dex_pairs),
            "helius_connected": bool(self.helius_key)
        }
    
    def set_helius_key(self, key: str):
        """Set Helius API key."""
        self.helius_key = key


# Singleton
_market_feed: Optional[MarketFeed] = None

def get_market_feed() -> MarketFeed:
    """Get market feed singleton."""
    global _market_feed
    if _market_feed is None:
        _market_feed = MarketFeed()
    return _market_feed


if __name__ == "__main__":
    import asyncio
    
    async def test():
        feed = get_market_feed()
        print("Fetching market data...")
        
        # Get DEX pairs
        pairs = await feed.get_dex_pairs()
        print(f"Found {len(pairs)} pairs")
        
        if pairs:
            print("\nTop pairs:")
            for p in pairs[:5]:
                print(f"  {p['base_token']}: ${p['price']} (liq: ${p.get('liquidity', 0):,.0f})")
    
    asyncio.run(test())
