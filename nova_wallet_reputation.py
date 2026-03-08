#!/usr/bin/env python3
"""
nova_wallet_reputation.py — Wallet Reputation System.
Scores wallet trustworthiness based on history.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class WalletReputation:
    """Tracks wallet reputation scores."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.db_path = self.base_path / "wallet_reputation.json"
        self.wallets = {}
        self._load()
    
    def _load(self):
        """Load reputation data."""
        if self.db_path.exists():
            try:
                self.wallets = json.loads(self.db_path.read_text())
            except:
                self.wallets = {}
    
    def _save(self):
        """Save reputation data."""
        self.db_path.write_text(json.dumps(self.wallets, indent=2))
    
    def record_trade(self, wallet: str, token: str, profit_pct: float, 
                    held_hours: float, was_rug: bool):
        """Record a wallet's trade."""
        if wallet not in self.wallets:
            self.wallets[wallet] = {
                "trades": [],
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "total_profit": 0.0,
                "rug_participation": 0,
                "score": 50  # Start neutral
            }
        
        w = self.wallets[wallet]
        
        # Record trade
        w["trades"].append({
            "token": token,
            "profit_pct": profit_pct,
            "held_hours": held_hours,
            "was_rug": was_rug,
            "timestamp": datetime.now().isoformat()
        })
        w["total_trades"] += 1
        
        # Update stats
        if profit_pct > 0:
            w["wins"] += 1
            w["total_profit"] += profit_pct
        else:
            w["losses"] += 1
        
        if was_rug:
            w["rug_participation"] += 1
        
        # Recalculate score
        self._update_score(wallet)
        
        self._save()
    
    def _update_score(self, wallet: str):
        """Update reputation score."""
        w = self.wallets[wallet]
        
        total = w["total_trades"]
        if total == 0:
            return
        
        # Win rate
        win_rate = w["wins"] / total
        
        # Average profit
        avg_profit = w["total_profit"] / total if total > 0 else 0
        
        # Rug penalty
        rug_penalty = w["rug_participation"] * 20
        
        # Calculate score (-100 to +100)
        score = 50  # Base
        score += (win_rate - 0.5) * 60  # ±30 based on win rate
        score += min(30, avg_profit / 10)  # Up to +30 for profit
        score -= rug_penalty  # Subtract for rug participation
        
        w["score"] = max(-100, min(100, int(score)))
    
    def get_score(self, wallet: str) -> int:
        """Get wallet score."""
        if wallet not in self.wallets:
            return 50  # Unknown = neutral
        return self.wallets[wallet].get("score", 50)
    
    def get_reputation(self, wallet: str) -> Dict:
        """Get full reputation data."""
        if wallet not in self.wallets:
            return {"score": 50, "status": "unknown"}
        
        w = self.wallets[wallet]
        
        # Determine status
        score = w.get("score", 50)
        if score >= 70:
            status = "trusted"
        elif score >= 40:
            status = "neutral"
        elif score >= 0:
            status = "suspicious"
        else:
            status = "dangerous"
        
        return {
            "score": score,
            "status": status,
            "total_trades": w.get("total_trades", 0),
            "wins": w.get("wins", 0),
            "losses": w.get("losses", 0),
            "rug_participation": w.get("rug_participation", 0)
        }
    
    def should_trust(self, wallet: str, min_score: int = 40) -> bool:
        """Should we trust this wallet?"""
        return self.get_score(wallet) >= min_score


# Singleton
_wallet_reputation: Optional[WalletReputation] = None


def get_wallet_reputation() -> WalletReputation:
    """Get wallet reputation singleton."""
    global _wallet_reputation
    if _wallet_reputation is None:
        _wallet_reputation = WalletReputation()
    return _wallet_reputation


if __name__ == "__main__":
    rep = get_wallet_reputation()
    print(json.dumps(rep.get_reputation("test_wallet"), indent=2))
