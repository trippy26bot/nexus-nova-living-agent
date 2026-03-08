#!/usr/bin/env python3
"""
nova_whale_exit_detector.py — Whale Exit Detector.
Tracks when whales exit profitably to predict market tops.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class WhaleExitDetector:
    """Detects whale profit-taking that signals market top."""
    
    def __init__(self):
        self.wallet_exits = defaultdict(list)  # token -> exit events
        self.path = Path(__file__).parent
        self._load()
    
    def _load(self):
        """Load saved data."""
        file_path = self.path / "whale_exits.json"
        if file_path.exists():
            try:
                data = json.loads(file_path.read_text())
                self.wallet_exits = defaultdict(list, data)
            except:
                pass
    
    def _save(self):
        """Save data."""
        file_path = self.path / "whale_exits.json"
        file_path.write_text(json.dumps(dict(self.wallet_exits), indent=2))
    
    def record_exit(self, wallet: str, token: str, amount: float, price: float, profit_pct: float):
        """Record a whale exit."""
        event = {
            "wallet": wallet,
            "token": token,
            "amount": amount,
            "price": price,
            "profit_pct": profit_pct,
            "timestamp": datetime.now().isoformat()
        }
        
        self.wallet_exits[token].append(event)
        self._save()
    
    def detect_exit_pattern(self, token: str) -> Dict:
        """Detect if whales are exiting a token."""
        exits = self.wallet_exits.get(token, [])
        
        if not exits:
            return {"detected": False, "reason": "no_exits_recorded"}
        
        # Get recent exits (last 30 minutes)
        recent = [
            e for e in exits
            if datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(minutes=30)
        ]
        
        if not recent:
            return {"detected": False, "reason": "no_recent_exits"}
        
        # Calculate metrics
        total_exits = len(recent)
        total_value = sum(e["amount"] * e["price"] for e in recent)
        avg_profit = sum(e["profit_pct"] for e in recent) / len(recent)
        
        # Detect exit pattern
        if total_exits >= 3:
            pattern = "mass_exit"
            detected = True
        elif total_value > 10000:  # $10k+
            pattern = "large_exit"
            detected = True
        elif avg_profit > 100:  # 100%+ profit
            pattern = "profit_taking"
            detected = True
        else:
            pattern = "normal"
            detected = False
        
        return {
            "detected": detected,
            "pattern": pattern,
            "recent_exits": total_exits,
            "total_value": round(total_value, 2),
            "avg_profit": round(avg_profit, 1),
            "action": "EXIT" if detected else "HOLD"
        }
    
    def should_exit_position(self, token: str, entry_price: float, current_price: float) -> Dict:
        """Check if position should exit based on whale exits."""
        # Check for exit signals
        exit_check = self.detect_exit_pattern(token)
        
        if not exit_check.get("detected"):
            return {"action": "HOLD", "reason": "no_whale_exits"}
        
        # Calculate current profit
        if entry_price > 0:
            profit_pct = ((current_price - entry_price) / entry_price) * 100
        else:
            profit_pct = 0
        
        # Exit decision
        if exit_check["pattern"] == "mass_exit":
            action = "EXIT_ALL"
            reason = "Mass whale exit detected"
        elif exit_check["pattern"] == "large_exit":
            if profit_pct > 20:
                action = "EXIT_ALL"
                reason = "Large exit with profit"
            else:
                action = "EXIT_HALF"
                reason = "Large exit - secure partial profit"
        elif exit_check["pattern"] == "profit_taking":
            if profit_pct > exit_check["avg_profit"]:
                action = "EXIT_ALL"
                reason = "Profit target reached before whale exit"
            else:
                action = "WATCH"
                reason = "Whale taking profits at lower %"
        else:
            action = "HOLD"
            reason = "Normal whale activity"
        
        return {
            "action": action,
            "reason": reason,
            "whale_exit_data": exit_check,
            "current_profit_pct": round(profit_pct, 1)
        }
    
    def get_whale_exit_history(self, token: str) -> List[Dict]:
        """Get full exit history for a token."""
        return self.wallet_exits.get(token, [])
    
    def get_status(self) -> Dict:
        """Get detector status."""
        return {
            "tokens_tracked": len(self.wallet_exits),
            "total_exits": sum(len(v) for v in self.wallet_exits.values())
        }


# Singleton
_whale_exit_detector: Optional[WhaleExitDetector] = None


def get_whale_exit_detector() -> WhaleExitDetector:
    """Get whale exit detector singleton."""
    global _whale_exit_detector
    if _whale_exit_detector is None:
        _whale_exit_detector = WhaleExitDetector()
    return _whale_exit_detector


if __name__ == "__main__":
    import json
    detector = get_whale_exit_detector()
    print(json.dumps(detector.get_status(), indent=2))
