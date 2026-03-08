#!/usr/bin/env python3
"""
nova_launch_radar.py — Launch Radar.
Detects tokens seconds after creation.
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional


class LaunchRadar:
    """Detects new token launches in real-time."""
    
    def __init__(self):
        self.dexscreener_url = "https://api.dexscreener.com"
        self.known_pairs = set()
        self.launch_alerts = []
        
    async def scan_new_pairs(self, min_liquidity: int = 10000) -> List[Dict]:
        """Scan for newly created pairs."""
        url = f"{self.dexscreener_url}/latest/dex/pairs/solana"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._filter_new(data.get("pairs", []), min_liquidity)
        except Exception as e:
            print(f"Launch scan error: {e}")
        
        return []
    
    def _filter_new(self, pairs: List[Dict], min_liquidity: int) -> List[Dict]:
        """Filter for new pairs with liquidity."""
        new_pairs = []
        
        for pair in pairs:
            pair_address = pair.get("pairAddress", "")
            
            # Skip known pairs
            if pair_address in self.known_pairs:
                continue
            
            liquidity = pair.get("liquidity", {}).get("usd", 0)
            
            # Skip low liquidity
            if liquidity < min_liquidity:
                continue
            
            # Mark as known
            self.known_pairs.add(pair_address)
            
            # Calculate age estimate (very low FDV = new)
            fdv = pair.get("fdv", 0)
            
            new_pairs.append({
                "address": pair_address,
                "chain": pair.get("dexId", "unknown"),
                "base_token": pair.get("baseToken", {}).get("symbol"),
                "quote_token": pair.get("quoteToken", {}).get("symbol"),
                "liquidity": liquidity,
                "fdv": fdv,
                "price": pair.get("priceUsd"),
                "volume_24h": pair.get("volume", {}).get("h24", 0),
                "buys_24h": pair.get("txns", {}).get("h24", {}).get("buys", 0),
                "sells_24h": pair.get("txns", {}).get("h24", {}).get("sells", 0),
                "detected_at": datetime.now().isoformat(),
                "estimated_age": "new" if fdv < 50000 else "recent"
            })
        
        return new_pairs
    
    async def detect_launches(self) -> Dict:
        """Detect fresh launches."""
        new_pairs = await self.scan_new_pairs()
        
        launches = []
        
        for pair in new_pairs:
            # Score the launch
            score = 0
            
            # Liquidity score
            liq = pair.get("liquidity", 0)
            if liq >= 100000:
                score += 30
            elif liq >= 50000:
                score += 20
            elif liq >= 20000:
                score += 10
            
            # Trading activity
            buys = pair.get("buys_24h", 0)
            sells = pair.get("sells_24h", 0)
            
            if buys > sells * 3:  # Strong buying pressure
                score += 25
            elif buys > sells:
                score += 15
            
            # Volume score
            vol = pair.get("volume_24h", 0)
            if vol >= 100000:
                score += 20
            elif vol >= 50000:
                score += 15
            elif vol >= 10000:
                score += 10
            
            # Age score (lower FDV = newer)
            if pair.get("estimated_age") == "new":
                score += 25
            
            pair["launch_score"] = score
            
            if score >= 30:
                launches.append(pair)
                
                # Add to alerts
                self.launch_alerts.append({
                    "pair": pair,
                    "score": score,
                    "detected_at": datetime.now().isoformat()
                })
        
        # Sort by score
        launches.sort(key=lambda x: x["launch_score"], reverse=True)
        
        return {
            "detected_at": datetime.now().isoformat(),
            "new_pairs": len(new_pairs),
            "hot_launches": launches,
            "top_launch": launches[0] if launches else None
        }
    
    async def monitor(self, interval: int = 30):
        """Continuous monitoring."""
        print(f"🚀 Launch radar active (interval: {interval}s)")
        
        while True:
            result = await self.detect_launches()
            
            if result["hot_launches"]:
                print(f"🚀 Found {len(result['hot_launches'])} hot launches:")
                for launch in result["hot_launches"][:3]:
                    print(f"  {launch['base_token']}: score {launch['launch_score']}")
            
            await asyncio.sleep(interval)
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent launch alerts."""
        return self.launch_alerts[-limit:]


# Singleton
_launch_radar: Optional[LaunchRadar] = None


def get_launch_radar() -> LaunchRadar:
    """Get launch radar singleton."""
    global _launch_radar
    if _launch_radar is None:
        _launch_radar = LaunchRadar()
    return _launch_radar


if __name__ == "__main__":
    import json
    radar = get_launch_radar()
    result = asyncio.run(radar.detect_launches())
    print(json.dumps(result, indent=2, default=str))
