#!/usr/bin/env python3
"""
nova_liquidity_tracker.py — Liquidity Migration Detector.
Detects where capital is moving across chains.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict


class LiquidityTracker:
    """Tracks liquidity movements across chains."""
    
    def __init__(self):
        self.dexscreener_url = "https://api.dexscreener.com"
        self.baseline = {}  # Baseline liquidity per chain
        self.history = []
    
    async def get_chain_liquidity(self, chain: str) -> Dict:
        """Get total liquidity for a chain."""
        url = f"{self.dexscreener_url}/tokens/high-liquid/v1"
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {"chain": chain}
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        tokens = data.get("tokens", [])
                        
                        total_liq = sum(t.get("liquidity", {}).get("usd", 0) for t in tokens)
                        total_vol = sum(t.get("volume", {}).get("h24", 0) for t in tokens)
                        
                        return {
                            "chain": chain,
                            "total_liquidity": total_liq,
                            "total_volume": total_vol,
                            "token_count": len(tokens),
                            "top_tokens": sorted(
                                [{"symbol": t.get("baseToken", {}).get("symbol"),
                                  "liquidity": t.get("liquidity", {}).get("usd", 0),
                                  "volume": t.get("volume", {}).get("h24", 0)}
                                 for t in tokens[:10]],
                                key=lambda x: x["liquidity"],
                                reverse=True
                            )
                        }
        except Exception as e:
            print(f"Chain {chain} error: {e}")
        
        return {"chain": chain, "total_liquidity": 0, "total_volume": 0}
    
    async def scan_all_chains(self) -> Dict:
        """Scan liquidity across all major chains."""
        chains = ["solana", "ethereum", "base", "arbitrum", "bsc", "polygon", "avalanche"]
        
        results = {}
        
        for chain in chains:
            data = await self.get_chain_liquidity(chain)
            results[chain] = data
        
        return results
    
    def detect_shifts(self, current: Dict, baseline: Dict = None) -> Dict:
        """Detect liquidity shifts between chains."""
        if baseline is None:
            baseline = self.baseline
        
        shifts = []
        
        for chain, data in current.items():
            curr_liq = data.get("total_liquidity", 0)
            base_liq = baseline.get(chain, {}).get("total_liquidity", curr_liq)
            
            if base_liq > 0:
                change_pct = ((curr_liq - base_liq) / base_liq) * 100
                
                if abs(change_pct) > 10:  # 10% threshold
                    shifts.append({
                        "chain": chain,
                        "change_pct": round(change_pct, 1),
                        "current_liquidity": curr_liq,
                        "baseline_liquidity": base_liquidity,
                        "direction": "inflow" if change_pct > 0 else "outflow"
                    })
        
        # Sort by absolute change
        shifts.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
        
        return shifts
    
    async def get_opportunities(self) -> List[Dict]:
        """Find liquidity opportunities."""
        current = await self.scan_all_chains()
        
        opportunities = []
        
        # Find chains with growing liquidity
        for chain, data in current.items():
            liq = data.get("total_liquidity", 0)
            vol = data.get("total_volume", 0)
            
            if liq > 0:
                vol_ratio = vol / liq if liq > 0 else 0
                
                # High volume relative to liquidity = active trading
                if vol_ratio > 0.5:
                    opportunities.append({
                        "chain": chain,
                        "liquidity": liq,
                        "volume": vol,
                        "volume_ratio": round(vol_ratio, 2),
                        "signal": "hot" if vol_ratio > 1 else "active"
                    })
        
        opportunities.sort(key=lambda x: x["volume_ratio"], reverse=True)
        
        return opportunities
    
    def set_baseline(self, baseline: Dict):
        """Set baseline for shift detection."""
        self.baseline = baseline
    
    def get_status(self) -> Dict:
        """Get tracker status."""
        return {
            "baseline_set": bool(self.baseline),
            "chains_tracked": len(self.baseline) if self.baseline else 7,
            "scans_completed": len(self.history)
        }


# Singleton
_liquidity_tracker: Optional[LiquidityTracker] = None


def get_liquidity_tracker() -> LiquidityTracker:
    """Get liquidity tracker singleton."""
    global _liquidity_tracker
    if _liquidity_tracker is None:
        _liquidity_tracker = LiquidityTracker()
    return _liquidity_tracker


if __name__ == "__main__":
    import json
    tracker = get_liquidity_tracker()
    result = asyncio.run(tracker.get_opportunities())
    print(json.dumps(result, indent=2))
