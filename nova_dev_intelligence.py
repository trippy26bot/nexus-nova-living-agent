#!/usr/bin/env python3
"""
nova_dev_intelligence.py — Dev Wallet Intelligence.
Tracks developer wallets and their token launch history.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class DevIntelligence:
    """Tracks developer wallet reputation and history."""
    
    def __init__(self):
        self.devs = {}
        self._load_devs()
    
    def _load_devs(self):
        """Load dev database."""
        path = Path(__file__).parent / "dev_db.json"
        if path.exists():
            try:
                self.devs = json.loads(path.read_text())
            except:
                self.devs = {}
    
    def _save_devs(self):
        """Save dev database."""
        path = Path(__file__).parent / "dev_db.json"
        path.write_text(json.dumps(self.devs, indent=2))
    
    def register_dev(self, address: str, label: str = "unknown"):
        """Register a new developer wallet."""
        if address not in self.devs:
            self.devs[address] = {
                "label": label,
                "first_seen": datetime.now().isoformat(),
                "tokens": [],
                "stats": {
                    "total_launches": 0,
                    "successful": 0,
                    "rugs": 0,
                    "total_roi": 0.0
                }
            }
            self._save_devs()
    
    def add_token(self, dev_address: str, token_address: str, token_data: Dict):
        """Record a token launch by a developer."""
        if dev_address not in self.devs:
            self.register_dev(dev_address)
        
        token_entry = {
            "address": token_address,
            "launched_at": datetime.now().isoformat(),
            "liquidity": token_data.get("liquidity", 0),
            "status": "active"  # active, rugged, successful
        }
        
        self.devs[dev_address]["tokens"].append(token_entry)
        self.devs[dev_address]["stats"]["total_launches"] += 1
        self._save_devs()
    
    def update_token_performance(self, dev_address: str, token_address: str, roi: float, rugged: bool = False):
        """Update token performance metrics."""
        if dev_address not in self.devs:
            return
        
        for token in self.devs[dev_address]["tokens"]:
            if token["address"] == token_address:
                token["roi"] = roi
                token["rugged"] = rugged
                token["updated_at"] = datetime.now().isoformat()
                
                # Update stats
                stats = self.devs[dev_address]["stats"]
                stats["total_roi"] += roi
                
                if rugged:
                    stats["rugs"] += 1
                elif roi > 0:
                    stats["successful"] += 1
                
                break
        
        self._save_devs()
    
    def get_dev_score(self, dev_address: str) -> Dict:
        """Calculate developer reputation score."""
        if dev_address not in self.devs:
            return {"score": 5, "level": "unknown", "reason": "No history"}
        
        dev = self.devs[dev_address]
        stats = dev["stats"]
        
        launches = stats["total_launches"]
        if launches == 0:
            return {"score": 5, "level": "unknown", "reason": "No launches"}
        
        avg_roi = stats["total_roi"] / launches
        rug_rate = stats["rugs"] / launches
        
        # Calculate score
        score = 0
        
        # Launch count
        if launches >= 10:
            score += 15
        elif launches >= 5:
            score += 10
        elif launches >= 2:
            score += 5
        
        # ROI
        if avg_roi >= 20:
            score += 25
        elif avg_roi >= 10:
            score += 20
        elif avg_roi >= 5:
            score += 15
        elif avg_roi >= 1:
            score += 10
        elif avg_roi >= 0:
            score += 5
        
        # Penalty for rugs
        if rug_rate >= 0.5:
            score -= 30
        elif rug_rate >= 0.3:
            score -= 20
        elif rug_rate >= 0.1:
            score -= 10
        
        score = max(0, min(100, score))
        
        # Determine level
        if score >= 80:
            level = "legend"
        elif score >= 60:
            level = "skilled"
        elif score >= 40:
            level = "average"
        elif score >= 20:
            level = "risky"
        else:
            level = "rug"
        
        return {
            "score": score,
            "level": level,
            "launches": launches,
            "avg_roi": round(avg_roi, 2),
            "rug_rate": round(rug_rate * 100, 1),
            "reason": f"{launches} launches, {avg_roi:.0f}x avg ROI, {rug_rate*100:.0f}% rugs"
        }
    
    def get_dev_history(self, dev_address: str) -> Dict:
        """Get full developer history."""
        if dev_address not in self.devs:
            return {"found": False}
        
        dev = self.devs[dev_address]
        score = self.get_dev_score(dev_address)
        
        return {
            "found": True,
            "address": dev_address,
            "label": dev.get("label"),
            "first_seen": dev.get("first_seen"),
            "score": score,
            "tokens": dev.get("tokens", [])
        }
    
    def is_known_rug_dev(self, dev_address: str) -> bool:
        """Check if developer is a known rug."""
        if dev_address not in self.devs:
            return False
        
        score = self.get_dev_score(dev_address)
        return score["level"] == "rug"
    
    def get_legend_devs(self) -> List[Dict]:
        """Get top performing developers."""
        legends = []
        
        for address, dev in self.devs.items():
            score = self.get_dev_score(address)
            if score["level"] in ["legend", "skilled"]:
                legends.append({
                    "address": address,
                    "label": dev.get("label"),
                    "score": score
                })
        
        legends.sort(key=lambda x: x["score"]["score"], reverse=True)
        return legends[:10]
    
    def get_status(self) -> Dict:
        """Get intelligence status."""
        return {
            "tracked_devs": len(self.devs),
            "legend_devs": len([d for d in self.devs.values() 
                               if self.get_dev_score(d.get("address", ""))["level"] == "legend"]),
            "recent_legend_devs": self.get_legend_devs()[:3]
        }


# Singleton
_dev_intel: Optional[DevIntelligence] = None


def get_dev_intelligence() -> DevIntelligence:
    """Get dev intelligence singleton."""
    global _dev_intel
    if _dev_intel is None:
        _dev_intel = DevIntelligence()
    return _dev_intel


if __name__ == "__main__":
    intel = get_dev_intelligence()
    print(json.dumps(intel.get_status(), indent=2, default=str))
