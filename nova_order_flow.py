#!/usr/bin/env python3
"""
nova_order_flow.py — Order Flow Intelligence.
Tracks aggressive buys/sells, absorption patterns.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class OrderFlow:
    """Analyzes order flow patterns."""
    
    def __init__(self):
        self.order_book_snapshots = []
        self.trade_flows = []
    
    def analyze_order_book(self, bids: List, asks: List, spread_pct: float) -> Dict:
        """Analyze order book for imbalances."""
        
        # Calculate totals
        bid_volume = sum(b["size"] for b in bids)
        ask_volume = sum(a["size"] for a in asks)
        
        # Imbalance ratio
        total = bid_volume + ask_volume
        if total > 0:
            bid_ratio = bid_volume / total
            ask_ratio = ask_volume / total
        else:
            bid_ratio = ask_ratio = 0.5
        
        # Determine pressure
        if bid_ratio > 0.65:
            pressure = "BUYING_PRESSURE"
            strength = bid_ratio - 0.5
        elif ask_ratio > 0.65:
            pressure = "SELLING_PRESSURE"
            strength = ask_ratio - 0.5
        else:
            pressure = "BALANCED"
            strength = 0
        
        # Spread analysis
        tight_spread = spread_pct < 0.1
        
        return {
            "pressure": pressure,
            "strength": round(strength * 100, 1),
            "bid_volume": bid_volume,
            "ask_volume": ask_volume,
            "spread_pct": spread_pct,
            "tight_spread": tight_spread,
            "timestamp": datetime.now().isoformat()
        }
    
    def detect_absorption(self, trades: List, price_change: float) -> Dict:
        """Detect if large orders are being absorbed."""
        if not trades:
            return {"absorption": False}
                   # Group by direction
        aggressive_buys = [t for t in trades if t.get("side") == "buy"]
        aggressive_sells = [t for t in trades if t.get("side") == "sell"]
        
        buy_volume = sum(t.get("size", 0) for t in aggressive_buys)
        sell_volume = sum(t.get("size", 0) for t in aggressive_sells)
        
        # Absorption = high volume but price not moving much
        if buy_volume > 0 and price_change < 1:
            return {
                "absorption": True,
                "type": "BUY_ABSORPTION",
                "absorbed_volume": buy_volume,
                "price_impact": price_change,
                "interpretation": "Large buyer(s) absorbing sell pressure"
            }
        elif sell_volume > 0 and price_change > -1:
            return {
                "absorption": True,
                "type": "SELL_ABSORPTION",
                "absorbed_volume": sell_volume,
                "price_impact": price_change,
                "interpretation": "Large seller(s) absorbing buy pressure"
            }
        
        return {"absorption": False}
    
    def detect_iceberg_orders(self, order_changes: List) -> Dict:
        """Detect hidden iceberg orders."""
        detected = []
        
        for change in order_changes:
            # Iceberg = repeated small orders at same price
            size = change.get("size", 0)
            frequency = change.get("frequency", 0)
            
            if size < 100 and frequency > 10:
                detected.append({
                    "price": change.get("price"),
                    "estimated_real_size": size * frequency,
                    "type": "POSSIBLE_ICEBERG"
                })
        
        return {
            "icebergs_detected": len(detected),
            "orders": detected[:5]
        }
    
    def get_flow_signal(self, order_book: Dict, recent_trades: List) -> Dict:
        """Get unified order flow signal."""
        
        # Analyze book
        ob_analysis = self.analyze_order_book(
            order_book.get("bids", []),
            order_book.get("asks", []),
            order_book.get("spread_pct", 0)
        )
        
        # Detect absorption
        price_change = order_book.get("price_change_5m", 0)
        absorption = self.detect_absorption(recent_trades, price_change)
        
        # Calculate confidence
        confidence = 0
        if ob_analysis["pressure"] != "BALANCED":
            confidence += ob_analysis["strength"] * 0.5
        if absorption.get("absorption"):
            confidence += 40
        
        return {
            "order_flow": ob_analysis,
            "absorption": absorption,
            "confidence": min(100, round(confidence, 1)),
            "signal": "STRONG_FLOW" if confidence > 60 else "WEAK_FLOW" if confidence > 30 else "NO_CLEAR_FLOW",
            "timestamp": datetime.now().isoformat()
        }


_order_flow: Optional[OrderFlow] = None


def get_order_flow() -> OrderFlow:
    """Get order flow singleton."""
    global _order_flow
    if _order_flow is None:
        _order_flow = OrderFlow()
    return _order_flow


if __name__ == "__main__":
    flow = get_order_flow()
    print(json.dumps({"status": "ready"}, indent=2))
