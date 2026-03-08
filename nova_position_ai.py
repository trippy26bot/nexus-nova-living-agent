#!/usr/bin/env python3
"""
nova_position_ai.py — Adaptive Position Sizing AI.
"""

import json
from datetime import datetime
from typing import Dict, Optional


class PositionAI:
    """Dynamic position sizing based on confidence."""
    
    def __init__(self):
        self.base_size_pct = 2  # 2% base
        self.max_size_pct = 10  # 10% max
        self.min_size_pct = 0.5  # 0.5% min
    
    def calculate_size(self, confidence: float, volatility: float = 0.02,
                      streak: int = 0) -> Dict:
        """Calculate position size based on confidence."""
        
        # Confidence-based sizing
        if confidence >= 0.90:
            size_pct = self.max_size_pct
        elif confidence >= 0.80:
            size_pct = 5
        elif confidence >= 0.70:
            size_pct = 3
        elif confidence >= 0.60:
            size_pct = 2
        elif confidence >= 0.50:
            size_pct = 1
        else:
            size_pct = self.min_size_pct
        
        # Adjust for volatility
        if volatility > 0.05:  # High volatility
            size_pct *= 0.5
        elif volatility > 0.03:
            size_pct *= 0.75
        
        # Adjust for streak
        if streak > 3:
            size_pct *= 1.5  # Increase on winning streak
        elif streak < -3:
            size_pct *= 0.5  # Decrease on losing streak
        
        # Clamp
        size_pct = max(self.min_size_pct, min(self.max_size_pct, size_pct))
        
        return {
            "confidence": confidence,
            "position_size_pct": round(size_pct, 2),
            "reason": self._get_reason(confidence, volatility, streak),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_reason(self, confidence: float, volatility: float, streak: int) -> str:
        """Get sizing reason."""
        reasons = []
        
        if confidence >= 0.80:
            reasons.append("high confidence")
        elif confidence >= 0.60:
            reasons.append("moderate confidence")
        else:
            reasons.append("low confidence")
        
        if volatility > 0.05:
            reasons.append("reduced for volatility")
        
        if streak > 3:
            reasons.append("increased for streak")
        elif streak < -3:
            reasons.append("reduced after losses")
        
        return ", ".join(reasons)
    
    def get_kelly_size(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Calculate Kelly Criterion position size."""
        
        if avg_loss == 0:
            return self.base_size_pct
        
        win_loss_ratio = avg_win / avg_loss
        
        # Kelly formula
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Use fractional Kelly (half) for safety
        kelly = kelly * 0.5
        
        # Convert to percentage and clamp
        size_pct = max(self.min_size_pct, min(self.max_size_pct, kelly * 100))
        
        return round(size_pct, 2)


_position_ai: Optional[PositionAI] = None

def get_position_ai() -> PositionAI:
    global _position_ai
    if _position_ai is None:
        _position_ai = PositionAI()
    return _position_ai


if __name__ == "__main__":
    ai = get_position_ai()
    print(json.dumps(ai.calculate_size(0.85, 0.03, 2), indent=2))
