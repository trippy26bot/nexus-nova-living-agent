#!/usr/bin/env python3
"""
nova_liquidity_inflow_detector.py — Liquidity Inflow Detector.
Detects liquidity injections before pumps.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class LiquidityInflowDetector:
    """Detects liquidity inflows that precede pumps."""
    
    def __init__(self):
        self.dexscreener_url = "https://api.dexscreener.com"
        self.baseline = {}  # baseline liquidity per token
        self.inflows = []   # detected inflows
    
    async def get_token_liquidity(self, token_address: str) -> Dict:
        """Get current liquidity for a token."""
        url = f"{self.dexscreener_url}/token-pairs/v1/solana/{token_address}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pairs = data.get("pairs", [])
                        if pairs:
                            pair = pairs[0]  # Take first pair
                            return {
                                "address": token_address,
                                "liquidity": pair.get("liquidity", {}).get("usd", 0),
                                "volume_24h": pair.get("volume", {}).get("h24", 0),
                                "price": pair.get("priceUsd"),
                                "timestamp": datetime.now().isoformat()
                            }
        except Exception as e:
            print(f"Liquidity check error: {e}")
        
        return {"address": token_address, "liquidity": 0}
    
    def set_baseline(self, token_address: str, liquidity: float):
        """Set baseline liquidity for comparison."""
        self.baseline[token_address] = {
            "liquidity": liquidity,
            "set_at": datetime.now().isoformat()
        }
    
    def detect_inflow(self, token_address: str, current_liquidity: float) -> Dict:
        """Detect liquidity inflow."""
        if token_address not in self.baseline:
            # First check - set baseline
            self.set_baseline(token_address, current_liquidity)
            return {"detected": False, "reason": "baseline_set"}
        
        baseline = self.baseline[token_address]["liquidity"]
        
        if baseline == 0:
            return {"detected": False, "reason": "zero_baseline"}
        
        change_pct = ((current_liquidity - baseline) / baseline) * 100
        
        if change_pct > 50:  # 50% increase
            inflow = {
                "token": token_address,
                "baseline": baseline,
                "current": current_liquidity,
                "change_pct": round(change_pct, 1),
                "detected_at": datetime.now().isoformat()
            }
            
            self.inflows.append(inflow)
            
            return {
                "detected": True,
                "type": "major_inflow" if change_pct > 100 else "significant_inflow",
                "change_pct": round(change_pct, 1),
                "baseline": baseline,
                "current": current_liquidity
            }
        
        return {"detected": False, "change_pct": round(change_pct, 1)}
    
    async def scan_for_inflows(self, tokens: List[str]) -> List[Dict]:
        """Scan multiple tokens for inflows."""
        inflows = []
        
        for token in tokens:
            data = await self.get_token_liquidity(token)
            liquidity = data.get("liquidity", 0)
            
            if liquidity > 0:
                result = self.detect_inflow(token, liquidity)
                
                if result.get("detected"):
                    result["token"] = token
                    inflows.append(result)
        
        return inflows
    
    async def get_major_inflows(self, chain: str = "solana") -> List[Dict]:
        """Scan chain for major liquidity inflows."""
        url = f"{self.dexscreener_url}/latest/dex/pairs/{chain}"
        
        major_inflows = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pairs = data.get("pairs", [])
                        
                        for pair in pairs[:50]:
                            pair_address = pair.get("pairAddress", "")
                            liquidity = pair.get("liquidity", {}).get("usd", 0)
                            
                            if liquidity > 0:
                                result = self.detect_inflow(pair_address, liquidity)
                                
                                if result.get("detected"):
                                    result["token"] = pair.get("baseToken", {}).get("symbol")
                                    major_inflows.append(result)
        
        except Exception as e:
            print(f"Major inflows scan error: {e}")
        
        # Sort by change percentage
        major_inflows.sort(key=lambda x: x.get("change_pct", 0), reverse=True)
        
        return major_inflows[:10]
    
    def get_recent_inflows(self, limit: int = 10) -> List[Dict]:
        """Get recent inflow detections."""
        return self.inflows[-limit:]
    
    def get_status(self) -> Dict:
        """Get detector status."""
        return {
            "baselines_tracked": len(self.baseline),
            "total_inflows_detected": len(self.inflows)
        }


# Singleton
_liquidity_inflow: Optional[LiquidityInflowDetector] = None


def get_liquidity_inflow_detector() -> LiquidityInflowDetector:
    """Get liquidity inflow detector singleton."""
    global _liquidity_inflow
    if _liquidity_inflow is None:
        _liquidity_inflow = LiquidityInflowDetector()
    return _liquidity_inflow


if __name__ == "__main__":
    import json
    detector = get_liquidity_inflow_detector()
    print(json.dumps(detector.get_status(), indent=2))
