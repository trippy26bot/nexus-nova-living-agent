#!/usr/bin/env python3
"""
nova_wallet_dna.py — Wallet DNA Profiling.
Builds behavior fingerprints for wallets.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class WalletDNA:
    """Builds DNA profiles for wallets."""
    
    def __init__(self):
        self.profiles = {}  # wallet -> DNA
        self.path = Path(__file__).parent
        self._load()
    
    def _load(self):
        """Load DNA profiles."""
        file_path = self.path / "wallet_dna.json"
        if file_path.exists():
            try:
                self.profiles = json.loads(file_path.read_text())
            except:
                pass
    
    def _save(self):
        """Save DNA profiles."""
        file_path = self.path / "wallet_dna.json"
        file_path.write_text(json.dumps(self.profiles, indent=2))
    
    def record_trade(self, wallet: str, token: str, action: str, 
                    amount: float, profit_pct: float = 0, held_hours: float = 0):
        """Record a trade for DNA analysis."""
        if wallet not in self.profiles:
            self.profiles[wallet] = {
                "created": datetime.now().isoformat(),
                "trades": [],
                "metrics": {}
            }
        
        profile = self.profiles[wallet]
        
        # Record trade
        trade = {
            "token": token,
            "action": action,
            "amount": amount,
            "profit_pct": profit_pct,
            "held_hours": held_hours,
            "timestamp": datetime.now().isoformat()
        }
        profile["trades"].append(trade)
        
        # Update DNA metrics
        self._update_dna(wallet)
        
        self._save()
    
    def _update_dna(self, wallet: str):
        """Calculate DNA metrics."""
        profile = self.profiles[wallet]
        trades = profile.get("trades", [])
        
        if not trades:
            return
        
        # Calculate metrics
        buys = [t for t in trades if t["action"] == "buy"]
        sells = [t for t in trades if t["action"] == "sell"]
        
        # ROI
        profits = [t["profit_pct"] for t in trades if t["profit_pct"] != 0]
        avg_roi = sum(profits) / len(profits) if profits else 0
        
        # Entry timing (avg hold time)
        hold_times = [t["held_hours"] for t in trades if t.get("held_hours", 0) > 0]
        avg_hold = sum(hold_times) / len(hold_times) if hold_times else 0
        
        # Early vs late entry
        early_entries = sum(1 for h in hold_times if h < 1)  # < 1 hour
        early_pct = early_entries / len(hold_times) if hold_times else 0
        
        # Win rate
        wins = sum(1 for p in profits if p > 0)
        win_rate = wins / len(profits) if profits else 0
        
        # Store DNA
        profile["metrics"] = {
            "total_trades": len(trades),
            "avg_roi": round(avg_roi, 2),
            "avg_hold_hours": round(avg_hold, 1),
            "early_entry_pct": round(early_pct * 100, 1),
            "win_rate": round(win_rate * 100, 1),
            "pump_participation": round(early_pct * win_rate * 100, 1)
        }
    
    def get_dna(self, wallet: str) -> Dict:
        """Get wallet DNA profile."""
        if wallet not in self.profiles:
            return {"known": False}
        
        profile = self.profiles[wallet]
        metrics = profile.get("metrics", {})
        
        # Calculate alpha score
        alpha_score = self._calculate_alpha(metrics)
        
        # Determine role
        role = self._determine_role(metrics)
        
        return {
            "known": True,
            "wallet": wallet,
            "metrics": metrics,
            "alpha_score": alpha_score,
            "role": role,
            "total_trades": metrics.get("total_trades", 0)
        }
    
    def _calculate_alpha(self, metrics: Dict) -> float:
        """Calculate alpha score."""
        avg_roi = metrics.get("avg_roi", 0)
        win_rate = metrics.get("win_rate", 0) / 100
        early_pct = metrics.get("early_entry_pct", 0) / 100
        pump_part = metrics.get("pump_participation", 0) / 100
        
        score = (
            min(avg_roi / 10, 40) +  # Up to 40 points for ROI
            win_rate * 30 +  # Up to 30 for win rate
            early_pct * 20 +  # Up to 20 for early entry
            pump_part * 10  # Up to 10 for pump participation
        )
        
        return min(100, round(score, 1))
    
    def _determine_role(self, metrics: Dict) -> str:
        """Determine wallet role based on behavior."""
        avg_hold = metrics.get("avg_hold_hours", 0)
        early_pct = metrics.get("early_entry_pct", 0)
        roi = metrics.get("avg_roi", 0)
        
        if early_pct > 60 and roi > 3:
            return "PUMP_STARTER"
        elif avg_hold < 1 and early_pct > 40:
            return "EARLY_BIRD"
        elif avg_hold > 24:
            return "SWING_TRADER"
        elif avg_hold < 2:
            return "FLIPPER"
        elif roi > 2:
            return "PROFIT_TAKER"
        else:
            return "AVERAGE"
    
    def get_watch_priority(self, wallet: str) -> str:
        """Get watch priority."""
        dna = self.get_dna(wallet)
        
        if not dna["known"]:
            return "LOW"
        
        score = dna.get("alpha_score", 0)
        
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"


# Singleton
_wallet_dna: Optional[WalletDNA] = None


def get_wallet_dna() -> WalletDNA:
    """Get wallet DNA singleton."""
    global _wallet_dna
    if _wallet_dna is None:
        _wallet_dna = WalletDNA()
    return _wallet_dna


if __name__ == "__main__":
    dna = get_wallet_dna()
    
    # Record test trades
    dna.record_trade("wallet_A", "TOKEN1", "buy", 1000, 5.2, 0.5)
    dna.record_trade("wallet_A", "TOKEN2", "buy", 2000, 8.1, 0.3)
    
    print(json.dumps(dna.get_dna("wallet_A"), indent=2))
