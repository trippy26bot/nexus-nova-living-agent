#!/usr/bin/env python3
"""
nova_liquidity_mapping.py — Liquidity Mapping Engine.
Maps stop clusters, liquidation levels, thin zones.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class LiquidityMapper:
    """Maps liquidity zones and stop clusters."""
    
    def __init__(self):
        self.price_levels = {}  # token -> price -> liquidity
    
    def map_price_levels(self, token: str, current_price: float, 
                        bids: List, asks: List) -> Dict:
        """Map liquidity at different price levels."""
        
        zones = {
            "stop_clusters": [],
            "liquidation_walls": [],
            "thin_zones": [],
            " liquidity_pools": []
        }
        
        # Find stop clusters (concentrated orders near current price)
        stop_range = current_price * 0.02  # 2% range
        
        bid_cluster = 0
        ask_cluster = 0
        
        for bid in bids:
            dist = (current_price - bid["price"]) / current_price
            if dist < 0.02:  # Within 2% below
                bid_cluster += bid.get("size", 0)
        
        for ask in asks:
            dist = (ask["price"] - current_price) / current_price
            if dist < 0.02:  # Within 2% above
                ask_cluster += ask.get("size", 0)
        
        # Detect walls
        if bid_cluster > 10000:
            zones["liquidation_walls"].append({
                "side": "BID",
                "strength": "STRONG" if bid_cluster > 50000 else "MODERATE",
                "size": bid_cluster,
                "distance_pct": round((current_price - bids[0]["price"]) / current_price * 100, 2) if bids else 0
            })
        
        if ask_cluster > 10000:
            zones["liquidation_walls"].append({
                "side": "ASK",
                "strength": "STRONG" if ask_cluster > 50000 else "MODERATE",
                "size": ask_cluster,
                "distance_pct": round((asks[0]["price"] - current_price) / current_price * 100, 2) if asks else 0
            })
        
        # Find thin zones (low liquidity)
        all_bids = sum(b.get("size", 0) for b in bids)
        all_asks = sum(a.get("size", 0) for a in asks)
        avg_liquidity = (all_bids + all_asks) / 2
        
        if avg_liquidity < 5000:
            zones["thin_zones"].append({
                "type": "LOW_LIQUIDITY",
                "avg_size": avg_liquidity,
                "warning": "High slippage risk"
            })
        
        return {
            "token": token,
            "current_price": current_price,
            "zones": zones,
            "total_bid_liquidity": all_bids,
            "total_ask_liquidity": all_asks,
            "timestamp": datetime.now().isoformat()
        }
    
    def detect_stop_hunt(self, price: float, stops_triggered: List,
                        direction: str) -> Dict:
        """Detect if stop hunt occurred."""
        
        if not stops_triggered:
            return {"stop_hunt": False}
        
        total_stops = len(stops_triggered)
        
        if total_stops > 5:
            return {
                "stop_hunt": True,
                "type": "STOP_HUNT",
                "stops_triggered": total_stops,
                "direction": direction,
                "interpretation": f"Liquidity sweep of {total_stops} stop orders"
            }
        
        return {"stop_hunt": False}
    
    def get_liquidity_signal(self, token: str, current_price: float,
                           bids: List, asks: List) -> Dict:
        """Get unified liquidity signal."""
        
        mapping = self.map_price_levels(token, current_price, bids, asks)
        
        walls = mapping["zones"]["liquidation_walls"]
        thin = mapping["zones"]["thin_zones"]
        
        # Score liquidity quality
        score = 50  # neutral
        
        for wall in walls:
            if wall["strength"] == "STRONG":
                score += 20
            else:
                score += 10
        
        if thin:
            score -= 30
        
        # Determine action
        if score >= 70:
            signal = "HIGH_LIQUIDITY_QUALITY"
        elif score >= 40:
            signal = "MODERATE_LIQUIDITY"
        else:
            signal = "LOW_LIQUIDITY"
        
        return {
            "liquidity_analysis": mapping,
            "quality_score": min(100, max(0, score)),
            "signal": signal,
            "walls": walls,
            "warnings": thin,
            "timestamp": datetime.now().isoformat()
        }


_liquidity_mapper: Optional[LiquidityMapper] = None


def get_liquidity_mapper() -> LiquidityMapper:
    """Get liquidity mapper singleton."""
    global _liquidity_mapper
    if _liquidity_mapper is None:
        _liquidity_mapper = LiquidityMapper()
    return _liquidity_mapper


if __name__ == "__main__":
    mapper = get_liquidity_mapper()
    print(json.dumps({"status": "ready"}, indent=2))
