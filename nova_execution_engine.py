#!/usr/bin/env python3
"""
nova_execution_engine.py — Smart Order Execution.
TWAP, VWAP, iceberg orders.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class ExecutionEngine:
    """Smart order execution strategies."""
    
    def __init__(self):
        self.active_orders = {}
    
    def create_twap_order(self, order_id: str, side: str, total_size: float,
                         splits: int, duration_minutes: int) -> Dict:
        """Create TWAP (Time Weighted Average Price) order."""
        
        chunk_size = total_size / splits
        
        self.active_orders[order_id] = {
            "type": "TWAP",
            "side": side,
            "total_size": total_size,
            "chunk_size": chunk_size,
            "splits": splits,
            "executed": 0,
            "duration": duration_minutes,
            "start_time": datetime.now(),
            "status": "ACTIVE"
        }
        
        return {
            "order_id": order_id,
            "type": "TWAP",
            "chunks": splits,
            "size_per_chunk": chunk_size,
            "status": "READY"
        }
    
    def create_vwap_order(self, order_id: str, side: str, total_size: float,
                         vwap_data: List[Dict]) -> Dict:
        """Create VWAP (Volume Weighted Average Price) order."""
        
        # Distribute order based on volume at each price level
        total_volume = sum(v.get("volume", 1) for v in vwap_data)
        
        chunks = []
        remaining = total_size
        
        for level in vwap_data:
            volume = level.get("volume", 1)
            weight = volume / total_volume if total_volume > 0 else 0
            
            size = min(remaining, total_size * weight)
            
            if size > 0:
                chunks.append({
                    "price": level["price"],
                    "size": size,
                    "volume_weight": weight
                })
                remaining -= size
            
            if remaining <= 0:
                break
        
        self.active_orders[order_id] = {
            "type": "VWAP",
            "side": side,
            "total_size": total_size,
            "chunks": chunks,
            "executed": 0,
            "start_time": datetime.now(),
            "status": "ACTIVE"
        }
        
        return {
            "order_id": order_id,
            "type": "VWAP",
            "chunks": len(chunks),
            "status": "READY"
        }
    
    def create_iceberg_order(self, order_id: str, side: str, total_size: float,
                            visible_size: float) -> Dict:
        """Create iceberg order (hidden liquidity)."""
        
        self.active_orders[order_id] = {
            "type": "ICEBERG",
            "side": side,
            "total_size": total_size,
            "visible_size": visible_size,
            "executed": 0,
            "hidden_remaining": total_size - visible_size,
            "start_time": datetime.now(),
            "status": "ACTIVE"
        }
        
        return {
            "order_id": order_id,
            "type": "ICEBERG",
            "total_size": total_size,
            "visible_size": visible_size,
            "hidden_size": total_size - visible_size,
            "status": "READY"
        }
    
    def execute_chunk(self, order_id: str) -> Dict:
        """Execute next chunk of an order."""
        
        if order_id not in self.active_orders:
            return {"error": "Order not found"}
        
        order = self.active_orders[order_id]
        
        if order["status"] != "ACTIVE":
            return {"error": "Order not active"}
        
        # Simulate execution
        if order["type"] == "TWAP":
            order["executed"] += order["chunk_size"]
            
        elif order["type"] == "VWAP":
            if order["chunks"]:
                chunk = order["chunks"][0]
                order["executed"] += chunk["size"]
                order["chunks"].pop(0)
                
        elif order["type"] == "ICEBERG":
            order["executed"] += order["visible_size"]
            order["hidden_remaining"] -= order["visible_size"]
        
        # Check if complete
        if order["executed"] >= order["total_size"]:
            order["status"] = "COMPLETE"
        
        return {
            "order_id": order_id,
            "executed": order["executed"],
            "remaining": order["total_size"] - order["executed"],
            "status": order["status"]
        }
    
    def get_order_status(self, order_id: str) -> Dict:
        """Get order status."""
        if order_id not in self.active_orders:
            return {"error": "Order not found"}
        
        order = self.active_orders[order_id].copy()
        order["progress_pct"] = (order["executed"] / order["total_size"] * 100) if order["total_size"] > 0 else 0
        
        return order


_execution: Optional[ExecutionEngine] = None

def get_execution_engine() -> ExecutionEngine:
    global _execution
    if _execution is None:
        _execution = ExecutionEngine()
    return _execution


if __name__ == "__main__":
    engine = get_execution_engine()
    result = engine.create_twap_order("test1", "BUY", 1.0, 10, 30)
    print(json.dumps(result, indent=2))
