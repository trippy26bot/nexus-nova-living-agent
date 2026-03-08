#!/usr/bin/env python3
"""
nova_wallet_predictor.py — Wallet Behavior Predictor.
Predicts which wallets are about to make profitable moves.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class WalletPredictor:
    """Predicts wallet behavior based on historical patterns."""
    
    def __init__(self):
        self.wallets = {}  # address -> profile
        self.trade_history = []
        self._load_wallets()
    
    def _load_wallets(self):
        """Load wallet profiles."""
        path = Path(__file__).parent / "wallet_profiles.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self.wallets = data.get("wallets", {})
            except:
                self.wallets = {}
    
    def _save_wallets(self):
        """Save wallet profiles."""
        path = Path(__file__).parent / "wallet_profiles.json"
        path.write_text(json.dumps({"wallets": self.wallets}, indent=2))
    
    def add_transaction(self, wallet: str, transaction: Dict):
        """Record a wallet transaction."""
        if wallet not in self.wallets:
            self.wallets[wallet] = self._create_profile(wallet)
        
        profile = self.wallets[wallet]
        
        # Add to history
        tx_record = {
            "token": transaction.get("token"),
            "action": transaction.get("action"),  # buy/sell
            "amount": transaction.get("amount", 0),
            "value": transaction.get("value", 0),
            "timestamp": datetime.now().isoformat()
        }
        
        profile["transactions"].append(tx_record)
        profile["total_trades"] += 1
        
        # Update stats
        if transaction.get("action") == "buy":
            profile["buy_count"] += 1
        else:
            profile["sell_count"] += 1
        
        # Update PnL if realized
        if transaction.get("pnl"):
            profile["total_pnl"] += transaction["pnl"]
            if transaction["pnl"] > 0:
                profile["wins"] += 1
            else:
                profile["losses"] += 1
        
        # Recalculate scores
        self._update_scores(profile)
        
        self._save_wallets()
    
    def _create_profile(self, address: str) -> Dict:
        """Create a new wallet profile."""
        return {
            "address": address,
            "created_at": datetime.now().isoformat(),
            "transactions": [],
            "total_trades": 0,
            "buy_count": 0,
            "sell_count": 0,
            "wins": 0,
            "losses": 0,
            "total_pnl": 0.0,
            "scores": {
                "win_rate": 0.0,
                "avg_return": 0.0,
                "early_entry": 0.0,
                "narrative_alignment": 0.0,
                "overall": 0.0
            }
        }
    
    def _update_scores(self, profile: Dict):
        """Calculate behavior scores."""
        trades = profile["total_trades"]
        if trades == 0:
            return
        
        # Win rate score (0-100)
        win_rate = (profile["wins"] / trades) * 100 if trades > 0 else 0
        profile["scores"]["win_rate"] = round(win_rate, 1)
        
        # Average return score (0-100)
        avg_pnl = profile["total_pnl"] / trades if trades > 0 else 0
        if avg_pnl > 100:
            avg_score = 100
        elif avg_pnl > 50:
            avg_score = 80
        elif avg_pnl > 20:
            avg_score = 60
        elif avg_pnl > 0:
            avg_score = 40
        else:
            avg_score = 20
        profile["scores"]["avg_return"] = avg_score
        
        # Early entry score (simplified)
        # In production, compare to token launch time
        profile["scores"]["early_entry"] = 50  # placeholder
        
        # Narrative alignment (simplified)
        profile["scores"]["narrative_alignment"] = 50  # placeholder
        
        # Overall whale score
        profile["scores"]["overall"] = round(
            (profile["scores"]["win_rate"] * 0.35) +
            (profile["scores"]["avg_return"] * 0.35) +
            (profile["scores"]["early_entry"] * 0.15) +
            (profile["scores"]["narrative_alignment"] * 0.15)
        )
    
    def predict(self, wallet: str) -> Dict:
        """Predict wallet behavior."""
        if wallet not in self.wallets:
            return {
                "known": False,
                "prediction": "unknown",
                "confidence": 0
            }
        
        profile = self.wallets[wallet]
        scores = profile["scores"]
        
        # Determine prediction
        overall = scores.get("overall", 0)
        
        if overall >= 80:
            prediction = "elite_trader"
            confidence = "high"
        elif overall >= 60:
            prediction = "profitable"
            confidence = "medium"
        elif overall >= 40:
            prediction = "average"
            confidence = "low"
        else:
            prediction = "underperforming"
            confidence = "low"
        
        # Check for recent activity (active now?)
        recent_trades = [
            t for t in profile["transactions"]
            if datetime.fromisoformat(t["timestamp"]) > datetime.now() - timedelta(hours=24)
        ]
        
        return {
            "known": True,
            "address": wallet,
            "prediction": prediction,
            "confidence": confidence,
            "scores": scores,
            "total_trades": profile["total_trades"],
            "total_pnl": profile["total_pnl"],
            "recent_activity": len(recent_trades),
            "is_active_now": len(recent_trades) > 0
        }
    
    def should_copy(self, wallet: str, token: str) -> Dict:
        """Should we copy this wallet's trade?"""
        pred = self.predict(wallet)
        
        if not pred["known"]:
            return {"copy": False, "reason": "unknown_wallet"}
        
        if pred["prediction"] == "underperforming":
            return {"copy": False, "reason": "low_performance"}
        
        # Check if already traded this token recently
        profile = self.wallets.get(wallet, {})
        recent_same = [
            t for t in profile.get("transactions", [])
            if t.get("token") == token and
            datetime.fromisoformat(t["timestamp"]) > datetime.now() - timedelta(hours=12)
        ]
        
        if recent_same:
            return {
                "copy": False,
                "reason": "already_traded",
                "action": recent_same[0].get("action")
            }
        
        # Determine position size based on confidence
        if pred["confidence"] == "high":
            size = "5%"
        elif pred["confidence"] == "medium":
            size = "3%"
        else:
            size = "1%"
        
        return {
            "copy": True,
            "reason": f"{pred['prediction']} wallet",
            "position_size": size,
            "confidence": pred["confidence"],
            "scores": pred["scores"]
        }
    
    def get_top_wallets(self, limit: int = 10) -> List[Dict]:
        """Get top performing wallets."""
        sorted_wallets = sorted(
            self.wallets.items(),
            key=lambda x: x[1].get("scores", {}).get("overall", 0),
            reverse=True
        )
        
        results = []
        for address, profile in sorted_wallets[:limit]:
            results.append({
                "address": address,
                "scores": profile["scores"],
                "total_trades": profile["total_trades"],
                "total_pnl": profile["total_pnl"]
            })
        
        return results
    
    def get_status(self) -> Dict:
        """Get predictor status."""
        return {
            "tracked_wallets": len(self.wallets),
            "total_trades": sum(w.get("total_trades", 0) for w in self.wallets.values()),
            "top_wallets": len([w for w in self.wallets.values() if w.get("scores", {}).get("overall", 0) >= 60])
        }


# Singleton
_wallet_predictor: Optional[WalletPredictor] = None


def get_wallet_predictor() -> WalletPredictor:
    """Get wallet predictor singleton."""
    global _wallet_predictor
    if _wallet_predictor is None:
        _wallet_predictor = WalletPredictor()
    return _wallet_predictor


if __name__ == "__main__":
    import json
    predictor = get_wallet_predictor()
    print(json.dumps(predictor.get_status(), indent=2))
