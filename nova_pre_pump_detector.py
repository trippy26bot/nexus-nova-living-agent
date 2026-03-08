#!/usr/bin/env python3
"""
nova_pre_pump_detector.py — Pre-Pump Detection.
Detects tokens before they pump.
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional


class PrePumpDetector:
    """Detects pre-pump setups."""
    
    def __init__(self):
        self.dexscreener_url = "https://api.dexscreener.com"
        self.detections = []
        
    async def analyze_token(self, token_address: str) -> Dict:
        """Analyze a token for pre-pump signals."""
        
        # Get token data
        url = f"{self.dexscreener_url}/token-pairs/v1/solana/{token_address}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pairs = data.get("pairs", [])
                        
                        if not pairs:
                            return {"detected": False, "reason": "no_pairs"}
                        
                        pair = pairs[0]
                        return self._analyze_pair(token_address, pair)
        except Exception as e:
            print(f"Analysis error: {e}")
        
        return {"detected": False, "reason": "api_error"}
    
    def _analyze_pair(self, address: str, pair: Dict) -> Dict:
        """Analyze a trading pair for pre-pump signals."""
        
        # Signal scores
        signals = {}
        
        # 1. Liquidity Seeding
        liquidity = pair.get("liquidity", {}).get("usd", 0)
        if liquidity >= 50000:
            signals["liquidity_seeding"] = min(25, liquidity / 20000)
        else:
            signals["liquidity_seeding"] = 0
        
        # 2. Smart Wallet Accumulation (placeholder - would need wallet data)
        # For now, use buy/sell ratio as proxy
        txns = pair.get("txns", {}).get("h24", {})
        buys = txns.get("buys", 0)
        sells = txns.get("sells", 0)
        
        if buys > sells * 3:
            signals["accumulation"] = 25
        elif buys > sells:
            signals["accumulation"] = 15
        else:
            signals["accumulation"] = 0
        
        # 3. Holder Growth (placeholder - would need holder API)
        signals["holder_growth"] = 10  # neutral
        
        # 4. Volume Without Price Movement (accumulation pattern)
        volume = pair.get("volume", {}).get("h24", 0)
        price_change = abs(pair.get("priceChange", {}).get("h24", 0))
        
        if volume > 100000 and price_change < 5:
            signals["accumulation_pattern"] = 20
        elif volume > 50000 and price_change < 3:
            signals["accumulation_pattern"] = 15
        else:
            signals["accumulation_pattern"] = 0
        
        # 5. Dev Activity (placeholder - would need dev tracking)
        signals["dev_activity"] = 10  # neutral
        
        # Calculate total pre-pump score
        weights = {
            "liquidity_seeding": 0.20,
            "accumulation": 0.30,
            "holder_growth": 0.15,
            "accumulation_pattern": 0.25,
            "dev_activity": 0.10
        }
        
        total_score = sum(signals[k] * weights[k] for k in weights)
        
        # Determine if pre-pump detected
        if total_score >= 70:
            verdict = "strong_pre_pump"
            action = "aggressive_entry"
        elif total_score >= 50:
            verdict = "pre_pump_setup"
            action = "watch"
        elif total_score >= 35:
            verdict = "early_signs"
            action = "monitor"
        else:
            verdict = "no_setup"
            action = "skip"
        
        result = {
            "detected": verdict != "no_setup",
            "token": address,
            "symbol": pair.get("baseToken", {}).get("symbol"),
            "pre_pump_score": round(total_score, 1),
            "verdict": verdict,
            "action": action,
            "signals": {k: round(v, 1) for k, v in signals.items()},
            "metrics": {
                "liquidity": liquidity,
                "volume_24h": volume,
                "price_change_24h": price_change,
                "buy_sell_ratio": round(buys / max(1, sells), 2)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        if result["detected"]:
            self.detections.append(result)
        
        return result
    
    async def scan_for_pre_pumps(self) -> List[Dict]:
        """Scan for pre-pump opportunities."""
        url = f"{self.dexscreener_url}/latest/dex/pairs/solana"
        
        pre_pumps = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        pairs = data.get("pairs", [])
                        
                        # Filter for pairs with some volume but not huge
                        candidates = [
                            p for p in pairs
                            if 10000 < p.get("liquidity", {}).get("usd", 0) < 500000
                            and p.get("volume", {}).get("h24", 0) > 10000
                        ]
                        
                        # Analyze each candidate
                        for pair in candidates[:30]:
                            address = pair.get("pairAddress", "")
                            result = self._analyze_pair(address, pair)
                            
                            if result["detected"]:
                                pre_pumps.append(result)
        
        except Exception as e:
            print(f"Scan error: {e}")
        
        # Sort by score
        pre_pumps.sort(key=lambda x: x["pre_pump_score"], reverse=True)
        
        return pre_pumps[:10]
    
    def get_recent_detections(self, limit: int = 10) -> List[Dict]:
        """Get recent pre-pump detections."""
        return self.detections[-limit:]
    
    def get_status(self) -> Dict:
        """Get detector status."""
        return {
            "total_detections": len(self.detections),
            "strong_pre_pumps": len([d for d in self.detections if d.get("verdict") == "strong_pre_pump"])
        }


# Singleton
_pre_pump_detector: Optional[PrePumpDetector] = None


def get_pre_pump_detector() -> PrePumpDetector:
    """Get pre-pump detector singleton."""
    global _pre_pump_detector
    if _pre_pump_detector is None:
        _pre_pump_detector = PrePumpDetector()
    return _pre_pump_detector


if __name__ == "__main__":
    import json
    detector = get_pre_pump_detector()
    result = asyncio.run(detector.scan_for_pre_pumps())
    print(json.dumps(result[:3], indent=2, default=str))
