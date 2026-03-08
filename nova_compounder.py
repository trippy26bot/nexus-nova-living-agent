#!/usr/bin/env python3
"""
nova_compounder.py — Profit Compounding Engine.
"""

import json
from datetime import datetime
from typing import Dict, Optional


class Compounder:
    """Controls profit compounding and capital scaling."""
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.compound_threshold = 1.1  # 10% gain
        self.max_drawdown_pause = 0.10  # 10% drawdown
        self.growth_factor = 1.2  # 20% increase per tier
    
    def record_trade(self, pnl: float) -> Dict:
        """Record trade result."""
        
        self.current_capital += pnl
        
        # Check drawdown
        drawdown = (self.initial_capital - self.current_capital) / self.initial_capital
        
        return {
            "pnl": pnl,
            "current_capital": self.current_capital,
            "drawdown": round(drawdown * 100, 2),
            "total_return_pct": round((self.current_capital - self.initial_capital) / self.initial_capital * 100, 2)
        }
    
    def get_position_size(self, base_size: float) -> float:
        """Get compounded position size."""
        
        # Scale based on capital growth
        growth_ratio = self.current_capital / self.initial_capital
        
        if growth_ratio >= 2.0:
            # Double - cap growth
            size = base_size * 2
        elif growth_ratio >= 1.5:
            size = base_size * 1.5
        elif growth_ratio >= 1.25:
            size = base_size * 1.25
        elif growth_ratio >= 1.1:
            size = base_size * 1.1
        else:
            size = base_size
        
        # Check if paused due to drawdown
        drawdown = (self.initial_capital - self.current_capital) / self.initial_capital
        
        if drawdown > self.max_drawdown_pause:
            size *= 0.5  # Reduce on drawdown
        
        return round(size, 4)
    
    def should_compound(self) -> Dict:
        """Check if should compound profits."""
        
        growth = (self.current_capital - self.initial_capital) / self.initial_capital
        
        if growth >= self.compound_threshold:
            return {
                "should_compound": True,
                "current_capital": self.current_capital,
                "growth_pct": round(growth * 100, 2),
                "action": "INCREASE_POSITION_SIZES"
            }
        
        return {
            "should_compound": False,
            "current_capital": self.current_capital,
            "growth_pct": round(growth * 100, 2),
            "action": "MAINTAIN_BASE_SIZES"
        }
    
    def reset(self) -> Dict:
        """Reset compounder."""
        old_capital = self.current_capital
        self.current_capital = self.initial_capital
        
        return {
            "reset": True,
            "old_capital": old_capital,
            "new_capital": self.current_capital
        }
    
    def get_status(self) -> Dict:
        """Get compounder status."""
        growth = (self.current_capital - self.initial_capital) / self.initial_capital
        
        return {
            "initial_capital": self.initial_capital,
            "current_capital": self.current_capital,
            "total_return_pct": round(growth * 100, 2),
            "compound_threshold": self.compound_threshold * 100,
            "max_drawdown_pause": self.max_drawdown_pause * 100
        }


_compounder: Optional[Compounder] = None

def get_compounder(initial_capital: float = 10000) -> Compounder:
    global _compounder
    if _compounder is None:
        _compounder = Compounder(initial_capital)
    return _compounder


if __name__ == "__main__":
    comp = get_compounder(10000)
    comp.record_trade(500)
    print(json.dumps(comp.get_position_size(0.02), indent=2))
