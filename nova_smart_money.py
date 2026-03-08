#!/usr/bin/env python3
"""
nova_smart_money.py — Smart Money Tracker.
Tracks top performing wallets and auto-copy trades.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class SmartMoneyTracker:
    """Tracks and ranks smart money wallets."""
    
    def __init__(self):
        self.wallets = {}  # address -> stats
        self.trades = []   # Recent trades
        self._load_wallets()
    
    def _load_wallets(self):
        """Load wallet database."""
        path = Path(__file__).parent / "smart_money.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self.wallets = data.get("wallets", {})
            except:
                self.wallets = {}
    
    def _save_wallets(self):
        """Save wallet database."""
        path = Path(__file__).parent / "smart_money.json"
        data = {"wallets": self.wallets}
        path.write_text(json.dumps(data, indent=2))
    
    def add_wallet(self, address: str, label: str = "manual"):
        """Add a wallet to track."""
        self.wallets[address] = {
            "label": label,
            "added_at": datetime.now().isoformat(),
            "trades": [],
            "total_pnl": 0.0,
            "win_count": 0,
            "loss_count": 0,
            "total_invested": 0.0,
            "score": 0.0
        }
        self._save_wallets()
    
    def record_trade(self, wallet: str, token: str, amount: float, pnl: float = 0, 
                     realized: bool = False):
        """Record a trade by a tracked wallet."""
        if wallet not in self.wallets:
            self.add_wallet(wallet)
        
        trade = {
            "token": token,
            "amount": amount,
            "pnl": pnl,
            "realized": realized,
            "timestamp": datetime.now().isoformat()
        }
        
        self.wallets[wallet]["trades"].append(trade)
        
        if realized:
            self.wallets[wallet]["total_pnl"] += pnl
            self.wallets[wallet]["total_invested"] += amount
            
            if pnl > 0:
                self.wallets[wallet]["win_count"] += 1
            else:
                self.wallets[wallet]["loss_count"] += 1
        
        # Recalculate score
        self._update_score(wallet)
        self._save_wallets()
    
    def _update_score(self, wallet: str):
        """Calculate smart money score for wallet."""
        w = self.wallets[wallet]
        
        total_trades = w["win_count"] + w["loss_count"]
        if total_trades == 0:
            w["score"] = 0.0
            return
        
        win_rate = w["win_count"] / total_trades
        avg_pnl = w["total_pnl"] / total_trades if total_trades > 0 else 0
        
        # Score formula: win_rate * avg_pnl (normalized)
        # Win rate 70%+ and positive PnL = high score
        score = (win_rate * 50) + (min(avg_pnl / 100, 50))
        
        # Bonus for consistent wins
        if win_rate > 0.7:
            score += 10
        if win_rate > 0.8:
            score += 15
        
        # Penalty for losses
        if win_rate < 0.4:
            score -= 20
        
        w["score"] = max(0, min(100, score))
    
    def get_top_wallets(self, limit: int = 10) -> List[Dict]:
        """Get top performing wallets."""
        sorted_wallets = sorted(
            self.wallets.items(),
            key=lambda x: x[1].get("score", 0),
            reverse=True
        )
        
        results = []
        for address, data in sorted_wallets[:limit]:
            total = data["win_count"] + data["loss_count"]
            win_rate = data["win_count"] / total if total > 0 else 0
            
            results.append({
                "address": address,
                "label": data.get("label"),
                "score": data.get("score", 0),
                "total_pnl": data.get("total_pnl", 0),
                "win_rate": win_rate * 100,
                "total_trades": total
            })
        
        return results
    
    def get_wallet_score(self, wallet: str) -> Dict:
        """Get score for specific wallet."""
        if wallet not in self.wallets:
            return {"found": False, "score": 0}
        
        w = self.wallets[wallet]
        total = w["win_count"] + w["loss_count"]
        
        return {
            "found": True,
            "address": wallet,
            "label": w.get("label"),
            "score": w.get("score", 0),
            "total_pnl": w.get("total_pnl", 0),
            "win_rate": (w["win_count"] / total * 100) if total > 0 else 0,
            "total_trades": total
        }
    
    def should_copy(self, wallet: str, token: str) -> Dict:
        """Check if we should copy a trade from this wallet."""
        score = self.get_wallet_score(wallet)
        
        if not score["found"]:
            return {"copy": False, "reason": "unknown_wallet"}
        
        if score["score"] < 30:
            return {"copy": False, "reason": "low_score", "score": score["score"]}
        
        # Good wallet - check if already traded this token recently
        wallet_trades = self.wallets[wallet].get("trades", [])
        recent_same_token = [
            t for t in wallet_trades 
            if t["token"] == token and 
            datetime.fromisoformat(t["timestamp"]) > datetime.now() - timedelta(hours=24)
        ]
        
        if recent_same_token:
            return {
                "copy": True, 
                "reason": "confirmed_buying",
                "score": score["score"],
                "position_size": self._get_copy_size(score["score"])
            }
        
        return {
            "copy": True,
            "reason": "high_score_wallet",
            "score": score["score"],
            "position_size": self._get_copy_size(score["score"])
        }
    
    def _get_copy_size(self, score: float) -> str:
        """Determine copy position size based on wallet score."""
        if score >= 80:
            return "5%"
        elif score >= 60:
            return "3%"
        elif score >= 40:
            return "2%"
        else:
            return "1%"
    
    def get_status(self) -> Dict:
        """Get tracker status."""
        return {
            "tracked_wallets": len(self.wallets),
            "top_wallets": self.get_top_wallets(5)
        }


# Singleton
_smart_money: Optional[SmartMoneyTracker] = None


def get_smart_money() -> SmartMoneyTracker:
    """Get smart money tracker singleton."""
    global _smart_money
    if _smart_money is None:
        _smart_money = SmartMoneyTracker()
    return _smart_money


if __name__ == "__main__":
    tracker = get_smart_money()
    print(json.dumps(tracker.get_status(), indent=2))
