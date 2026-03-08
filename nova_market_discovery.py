#!/usr/bin/env python3
"""
nova_market_discovery.py — Market Discovery Engine.
Discovers markets from all sources automatically.
"""

import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional


class MarketDiscovery:
    """Discovers markets from all sources."""
    
    def __init__(self):
        self.sources = {
            "coingecko": self._discover_coingecko,
            "dexscreener": self._discover_dexscreener,
            "defillama": self._discover_defillama,
            "polymarket": self._discover_polymarket,
        }
    
    async def discover_all(self) -> List[Dict]:
        """Discover markets from all sources."""
        all_markets = []
        
        tasks = []
        for source, func in self.sources.items():
            tasks.append(self._safe_discover(source, func))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_markets.extend(result)
        
        return all_markets
    
    async def _safe_discover(self, source: str, func) -> List[Dict]:
        """Safely run discovery function."""
        try:
            return await func()
        except Exception as e:
            print(f"Discovery error ({source}): {e}")
            return []
    
    async def _discover_coingecko(self) -> List[Dict]:
        """Discover from CoinGecko."""
        markets = []
        
        # Top coins
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "volume_desc",
            "per_page": 250,
            "page": 1
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for coin in data:
                            markets.append({
                                "id": f"coingecko_{coin['id']}",
                                "symbol": coin.get("symbol", "").upper(),
                                "name": coin.get("name", ""),
                                "category": "crypto_cex",
                                "chain": "multi",
                                "price": coin.get("current_price", 0),
                                "volume_24h": coin.get("total_volume", 0),
                                "market_cap": coin.get("market_cap", 0),
                                "source": "coingecko"
                            })
        except Exception as e:
            print(f"CoinGecko error: {e}")
        
        return markets
    
    async def _discover_dexscreener(self) -> List[Dict]:
        """Discover from Dexscreener."""
        markets = []
        
        url = "https://api.dexscreener.com/latest/dex/pairs"
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get trending pairs
                async with session.get("https://api.dexscreener.com/latest/dex/tokens/popular", 
                                     timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pairs = data.get("pairs", [])[:100]
                        
                        for pair in pairs:
                            markets.append({
                                "id": f"dex_{pair.get('pairAddress', '')}",
                                "symbol": pair.get("baseToken", {}).get("symbol", ""),
                                "name": pair.get("pairAddress", ""),
                                "category": "crypto_dex",
                                "chain": pair.get("chainId", "unknown"),
                                "price": pair.get("priceUsd", 0),
                                "volume_24h": pair.get("txns", {}).get("h24", {}).get("volume", 0),
                                "liquidity": pair.get("liquidity", {}).get("usd", 0),
                                "source": "dexscreener"
                            })
        except Exception as e:
            print(f"Dexscreener error: {e}")
        
        return markets
    
    async def _discover_defillama(self) -> List[Dict]:
        """Discover from DefiLlama."""
        markets = []
        
        # Get protocols
        url = "https://api.llama.fi/protocols"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        for protocol in data[:100]:
                            markets.append({
                                "id": f"defillama_{protocol.get('slug', '')}",
                                "symbol": protocol.get("symbol", ""),
                                "name": protocol.get("name", ""),
                                "category": "defi_protocol",
                                "chain": "multi",
                                "tvl": protocol.get("tvl", 0),
                                "source": "defillama"
                            })
        except Exception as e:
            print(f"DefiLlama error: {e}")
        
        return markets
    
    async def _discover_polymarket(self) -> List[Dict]:
        """Discover from Polymarket."""
        markets = []
        
        # Get trending markets
        url = "https://clob.polymarket.com/markets"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        for market in data[:50]:
                            markets.append({
                                "id": f"polymarket_{market.get('conditionId', '')}",
                                "symbol": market.get("question", "")[:20],
                                "name": market.get("question", ""),
                                "category": "prediction",
                                "chain": "polygon",
                                "volume": market.get("volume", 0),
                                "source": "polymarket"
                            })
        except Exception as e:
            print(f"Polymarket error: {e}")
        
        return markets
    
    async def discover_category(self, category: str) -> List[Dict]:
        """Discover markets for a specific category."""
        discover_funcs = {
            "crypto": [self._discover_coingecko, self._discover_dexscreener],
            "defi": [self._discover_defillama],
            "prediction": [self._discover_polymarket],
        }
        
        funcs = discover_funcs.get(category, [])
        
        results = []
        for func in funcs:
            try:
                result = await func()
                results.extend(result)
            except:
                pass
        
        return results


_discovery: Optional[MarketDiscovery] = None

def get_market_discovery() -> MarketDiscovery:
    """Get market discovery singleton."""
    global _discovery
    if _discovery is None:
        _discovery = MarketDiscovery()
    return _discovery


if __name__ == "__main__":
    import asyncio
    disc = get_market_discovery()
    print("Discovering markets...")
    markets = asyncio.run(disc.discover_all())
    print(f"Found {len(markets)} markets")
