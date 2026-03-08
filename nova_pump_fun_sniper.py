#!/usr/bin/env python3
"""
nova_pump_fun_sniper.py — Pump.fun Launch Sniper.
Detects tokens seconds after launch.
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional


class PumpFunSniper:
    """Snipes tokens from Pump.fun."""
    
    def __init__(self):
        self.dexscreener_url = "https://api.dexscreener.com"
        self.scanned_tokens = set()
        self.new_tokens = []
        
    async def scan_for_new_tokens(self, min_liquidity: int = 10000) -> List[Dict]:
        """Scan for new tokens with liquidity."""
        url = f"{self.dexscreener_url}/latest/dex/pairs/solana"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._filter_new_pairs(data.get("pairs", []), min_liquidity)
        except Exception as e:
            print(f"Scan error: {e}")
        
        return []
    
    def _filter_new_pairs(self, pairs: List[Dict], min_liquidity: int) -> List[Dict]:
        """Filter for new pairs with liquidity."""
        new_pairs = []
        
        for pair in pairs:
            try:
                liquidity = pair.get("liquidity", {}).get("usd", 0)
                if liquidity < min_liquidity:
                    continue
                
                pair_address = pair.get("pairAddress", "")
                if pair_address in self.scanned_tokens:
                    continue
                
                # Check if it's new (no price history)
                fdv = pair.get("fdv", 0)
                if fdv < 50000:  # Very low FDV = very new
                    self.scanned_tokens.add(pair_address)
                    
                    new_pairs.append({
                        "address": pair_address,
                        "symbol": pair.get("baseToken", {}).get("symbol"),
                        "name": pair.get("baseToken", {}).get("name"),
                        "liquidity": liquidity,
                        "price": pair.get("priceUsd"),
                        "dex": pair.get("dexId"),
                        "scanned_at": datetime.now().isoformat()
                    })
            except:
                continue
        
        return new_pairs
    
    async def monitor(self, interval: int = 30):
        """Continuous monitoring."""
        print(f"🕵️ Pump.fun sniper active (interval: {interval}s)")
        
        while True:
            new = await self.scan_for_new_tokens()
            
            if new:
                print(f"🚀 Found {len(new)} new tokens:")
                for token in new[:5]:
                    print(f"  {token['symbol']}: ${token['liquidity']:,.0f} liquidity")
                    self.new_tokens.append(token)
            
            await asyncio.sleep(interval)


# Singleton
_pump_sniper: Optional[PumpFunSniper] = None


def get_pump_fun_sniper() -> PumpFunSniper:
    """Get pump.fun sniper singleton."""
    global _pump_sniper
    if _pump_sniper is None:
        _pump_sniper = PumpFunSniper()
    return _pump_sniper


if __name__ == "__main__":
    import json
    sniper = get_pump_fun_sniper()
    result = asyncio.run(sniper.scan_for_new_tokens())
    print(json.dumps(result, indent=2))
