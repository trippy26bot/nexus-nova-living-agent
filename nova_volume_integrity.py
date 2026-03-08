#!/usr/bin/env python3
"""
nova_volume_integrity.py — Volume Integrity Detector.
Detects fake volume from wash trading.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict


class VolumeIntegrity:
    """Detects fake volume from wash trading."""
    
    def __init__(self):
        self.trade_history = defaultdict(list)  # token -> trades
        
    def record_trade(self, token: str, wallet: str, side: str, amount: float):
        """Record a trade."""
        self.trade_history[token].append({
            "wallet": wallet,
            "side": side,  # buy/sell
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        })
    
    def check_integrity(self, token: str) -> Dict:
        """Check if volume is real or wash trading."""
        trades = self.trade_history.get(token, [])
        
        if len(trades) < 5:
            return {"integrity": "unknown", "reason": "insufficient_data"}
        
        # Analyze patterns
        wallets = set(t["wallet"] for t in trades)
        buys = [t for t in trades if t["side"] == "buy"]
        sells = [t for t in trades if t["side"] == "sell"]
        
        # Check for wash trading patterns
        issues = []
        
        # 1. Same wallet trading
        if len(wallets) < len(trades) * 0.5:
            issues.append("low_wallet_diversity")
        
        # 2. Buy/sell matching (same sizes)
        buy_amounts = sorted([t["amount"] for t in buys])
        sell_amounts = sorted([t["amount"] for t in sells])
        
        if buy_amounts == sell_amounts and len(buy_amounts) > 2:
            issues.append("matching_trade_sizes")
        
        # 3. Regular timing (bots)
        timestamps = [datetime.fromisoformat(t["timestamp"]) for t in trades]
        if len(timestamps) > 3:
            intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                      for i in range(len(timestamps)-1)]
            avg_interval = sum(intervals) / len(intervals)
            if avg_interval < 5:  # Less than 5 seconds between trades
                issues.append("bot_like_timing")
        
        # Calculate integrity score
        integrity_score = 100 - (len(issues) * 30)
        
        if integrity_score >= 70:
            verdict = "REAL"
        elif integrity_score >= 40:
            verdict = "SUSPICIOUS"
        else:
            verdict = "FAKE"
        
        return {
            "token": token,
            "verdict": verdict,
            "integrity_score": max(0, integrity_score),
            "issues": issues,
            "unique_wallets": len(wallets),
            "total_trades": len(trades)
        }
    
    def get_status(self) -> Dict:
        """Get status."""
        return {
            "tokens_tracked": len(self.trade_history)
        }


# Singleton
_volume_integrity: Optional[VolumeIntegrity] = None


def get_volume_integrity() -> VolumeIntegrity:
    """Get volume integrity singleton."""
    global _volume_integrity
    if _volume_integrity is None:
        _volume_integrity = VolumeIntegrity()
    return _volume_integrity


if __name__ == "__main__":
    import json
    vi = get_volume_integrity()
    print(json.dumps(vi.get_status(), indent=2))
