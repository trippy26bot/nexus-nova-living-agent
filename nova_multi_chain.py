#!/usr/bin/env python3
"""
nova_multi_chain.py — Multi-chain data aggregator.
Watches ALL ecosystems: Solana, Ethereum, Base, Arbitrum, BSC, etc.
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional


class MultiChainData:
    """Aggregates data from multiple chains."""
    
    def __init__(self):
        # Chain configs
        self.chains = {
            "solana": {
                "rpc": "https://api.mainnet-beta.solana.com",
                "dexscreener": "solana",
                "explorer": "solscan.io"
            },
            "ethereum": {
                "rpc": "https://eth-mainnet.g.alchemy.com/v2/demo",
                "dexscreener": "ethereum",
                "explorer": "etherscan.io"
            },
            "base": {
                "rpc": "https://mainnet.base.org",
                "dexscreener": "base",
                "explorer": "basescan.org"
            },
            "arbitrum": {
                "rpc": "https://arb1.arbitrum.io/rpc",
                "dexscreener": "arbitrum",
                "explorer": "arbiscan.io"
            },
            "bsc": {
                "rpc": "https://bsc-dataseed.binance.org",
                "dexscreener": "bsc",
                "explorer": "bscscan.com"
            },
            "polygon": {
                "rpc": "https://polygon-rpc.com",
                "dexscreener": "polygon",
                "explorer": "polygonscan.com"
            },
            "avalanche": {
                "rpc": "https://api.avax.network/ext/bc/C/rpc",
                "dexscreener": "avalanche",
                "explorer": "snowtrace.io"
            }
        }
        
        self.dexscreener_url = "https://api.dexscreener.com"
    
    async def scan_chain(self, chain: str, limit: int = 50) -> List[Dict]:
        """Scan trending tokens on a chain."""
        url = f"{self.dexscreener_url}/token-boosts/top/v1?chain={chain}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        tokens = data.get("tokens", [])
                        return [{
                            "chain": chain,
                            "address": t.get("address"),
                            "symbol": t.get("baseToken", {}).get("symbol"),
                            "name": t.get("baseToken", {}).get("name"),
                            "price": t.get("priceUsd"),
                            "price_change": t.get("priceChange", {}).get("h24"),
                            "liquidity": t.get("liquidity", {}).get("usd"),
                            "volume": t.get("volume", {}).get("h24"),
                            "pair": t.get("pairAddress")
                        } for t in tokens[:limit]]
        except Exception as e:
            print(f"Chain {chain} scan error: {e}")
        
        return []
    
    async def scan_all_chains(self) -> Dict:
        """Scan all configured chains."""
        results = {}
        
        for chain in self.chains:
            tokens = await self.scan_chain(chain)
            results[chain] = {
                "count": len(tokens),
                "tokens": tokens[:10]  # Top 10 per chain
            }
        
        return results
    
    async def get_cross_chain_opportunities(self) -> List[Dict]:
        """Find opportunities across chains."""
        all_data = await self.scan_all_chains()
        
        opportunities = []
        
        for chain, data in all_data.items():
            for token in data.get("tokens", []):
                score = 0
                
                # Volume score
                volume = token.get("volume", 0)
                if volume > 1000000:
                    score += 30
                elif volume > 500000:
                    score += 20
                elif volume > 100000:
                    score += 10
                
                # Liquidity score
                liquidity = token.get("liquidity", 0)
                if liquidity > 500000:
                    score += 20
                elif liquidity > 100000:
                    score += 10
                
                # Price momentum
                change = token.get("price_change", 0)
                if 10 < change < 100:
                    score += 20
                elif 0 < change <= 10:
                    score += 10
                
                if score >= 30:
                    token["opportunity_score"] = score
                    token["chain"] = chain
                    opportunities.append(token)
        
        # Sort by score
        opportunities.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)
        
        return opportunities[:20]
    
    def get_chain_info(self, chain: str) -> Dict:
        """Get chain configuration."""
        return self.chains.get(chain, {})


# Singleton
_multi_chain: Optional[MultiChainData] = None


def get_multi_chain() -> MultiChainData:
    """Get multi-chain data singleton."""
    global _multi_chain
    if _multi_chain is None:
        _multi_chain = MultiChainData()
    return _multi_chain


if __name__ == "__main__":
    import json
    mc = get_multi_chain()
    result = asyncio.run(mc.get_cross_chain_opportunities())
    print(json.dumps(result[:5], indent=2, default=str))
