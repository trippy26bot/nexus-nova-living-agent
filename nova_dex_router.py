#!/usr/bin/env python3
"""
nova_dex_router.py — DEX Router.
Routes trades to best DEX with MEV protection.
"""

import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional


class DexRouter:
    """Routes trades to best DEX with protection."""
    
    # Supported DEXs
    DEXES = {
        "solana": ["jupiter", "raydium", "orca"],
        "ethereum": ["uniswap", "sushiswap", "curve"],
        "base": ["uniswap", "baseswap"],
        "arbitrum": ["uniswap", "camelot"]
    }
    
    def __init__(self):
        self.jupiter_url = "https://api.jup.ag"
        
    async def get_quote(self, from_token: str, to_token: str, amount: float, 
                       chain: str = "solana") -> Dict:
        """Get best quote across DEXs."""
        
        if chain == "solana":
            return await self._jupiter_quote(from_token, to_token, amount)
        
        return {"error": "Chain not supported"}
    
    async def _jupiter_quote(self, from_token: str, to_token: str, 
                             amount: float) -> Dict:
        """Get Jupiter aggregator quote."""
        url = f"{self.jupiter_url}/v1/quote"
        
        params = {
            "inputMint": from_token,
            "outputMint": to_token,
            "amount": int(amount * 1e9),  # lamports
            "slippage": 5
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data:
                            best = data[0]
                            return {
                                "dex": best.get("dex", "unknown"),
                                "price_impact": best.get("priceImpact", 0),
                                "out_amount": best.get("outAmount", 0),
                                "route": best.get("routePlan", [])
                            }
        except Exception as e:
            return {"error": str(e)}
        
        return {"error": "No quote available"}
    
    async def execute_swap(self, wallet, from_token: str, to_token: str, 
                          amount: float) -> Dict:
        """Execute swap through best DEX."""
        # Get quote first
        quote = await self.get_quote(from_token, to_token, amount)
        
        if "error" in quote:
            return {"success": False, "error": quote["error"]}
        
        # Return quote for user approval (not auto-execute)
        return {
            "success": True,
            "quote": quote,
            "action": "APPROVE_TO_EXECUTE"
        }
    
    def should_use_private_relay(self, token: str, amount: float) -> bool:
        """Determine if private relay should be used."""
        # Use private relay for large trades
        return amount > 1000  # > $1000


# Singleton
_dex_router: Optional[DexRouter] = None


def get_dex_router() -> DexRouter:
    """Get DEX router singleton."""
    global _dex_router
    if _dex_router is None:
        _dex_router = DexRouter()
    return _dex_router


if __name__ == "__main__":
    import asyncio
    router = get_dex_router()
    print(json.dumps({"status": "ready"}, indent=2))
