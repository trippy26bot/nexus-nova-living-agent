#!/usr/bin/env python3
"""
nova_arbitrage_engine.py — Cross-Exchange Arbitrage.
"""

import json
import aiohttp
from datetime import datetime
from typing import Dict, Optional


class ArbitrageEngine:
    """Detects cross-exchange price differences."""
    
    EXCHANGES = ["binance", "coinbase", "kraken", "kucoin"]
    
    async def get_prices(self, symbol: str = "BTC/USDT") -> Dict:
        """Fetch prices from multiple exchanges."""
        prices = {}
        
        # Simulated prices (in real use, call APIs)
        # In production: use exchange APIs
        prices = {
            "binance": {"bid": 64200, "ask": 64205},
            "coinbase": {"bid": 64250, "ask": 64255},
            "kraken": {"bid": 64180, "ask": 64185},
            "kucoin": {"bid": 64220, "ask": 64225}
        }
        
        return prices
    
    async def find_arbitrage(self, symbol: str = "BTC/USDT") -> Dict:
        """Find arbitrage opportunity."""
        prices = await self.get_prices(symbol)
        
        if not prices:
            return {"opportunity": False}
        
        # Find best bid/ask
        lowest_ask = min(prices.values(), key=lambda x: x["ask"])
        highest_bid = max(prices.values(), key=lambda x: x["bid"])
        
        # Calculate spread
        spread = highest_bid["bid"] - lowest_ask["ask"]
        spread_pct = (spread / lowest_ask["ask"]) * 100
        
        # Only worthwhile if spread > 0.1%
        if spread_pct > 0.1:
            return {
                "opportunity": True,
                "spread": spread,
                "spread_pct": round(spread_pct, 3),
                "buy_exchange": self._get_exchange(lowest_ask, prices),
                "sell_exchange": self._get_exchange(highest_bid, prices),
                "buy_price": lowest_ask["ask"],
                "sell_price": highest_bid["bid"],
                "profit_per_unit": spread,
                "timestamp": datetime.now().isoformat()
            }
        
        return {"opportunity": False, "spread_pct": spread_pct}
    
    def _get_exchange(self, price_data: Dict, all_prices: Dict) -> str:
        """Find exchange for price data."""
        for exchange, data in all_prices.items():
            if data == price_data:
                return exchange
        return "unknown"


_arbitrage: Optional[ArbitrageEngine] = None

def get_arbitrage_engine() -> ArbitrageEngine:
    global _arbitrage
    if _arbitrage is None:
        _arbitrage = ArbitrageEngine()
    return _arbitrage


if __name__ == "__main__":
    import asyncio
    arb = get_arbitrage_engine()
    print(json.dumps(asyncio.run(arb.find_arbitrage()), indent=2))
