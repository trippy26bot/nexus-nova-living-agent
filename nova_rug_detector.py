#!/usr/bin/env python3
"""
nova_rug_detector.py — Rug Pull Detection.
Identifies red flags before trading.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class RugDetector:
    """Detects rug pull risks in tokens."""
    
    def __init__(self):
        self.known_rugs = set()  # Known rug dev addresses
        self.known_safe = set()  # Known safe devs
        self._load_databases()
    
    def _load_databases(self):
        """Load known rug/safe dev databases."""
        # Could load from files in production
        pass
    
    def analyze_token(self, token_data: Dict) -> Dict:
        """Analyze token for rug pull risks."""
        risks = []
        score = 0  # 0 = safe, 100 = certain rug
         # 0 = safe, 100 = certain rug
        
        # Check 1: Liquidity Locked
        liquidity_locked = token_data.get("liquidity_locked", True)
        if not liquidity_locked:
            risks.append({
                "type": "liquidity_unlocked",
                "severity": "critical",
                "description": "Liquidity is not locked"
            })
            score += 40
        
        # Check 2: Mint Authority
        mint_authority = token_data.get("mint_authority", None)
        if mint_authority and mint_authority != "null":
            risks.append({
                "type": "mint_authority_active",
                "severity": "critical",
                "description": "Dev can mint infinite tokens"
            })
            score += 35
        
        # Check 3: Freeze Authority
        freeze_authority = token_data.get("freeze_authority", None)
        if freeze_authority and freeze_authority != "null":
            risks.append({
                "type": "freeze_authority_active",
                "severity": "high",
                "description": "Dev can freeze transactions"
            })
            score += 25
        
        # Check 4: Dev Supply
        dev_supply_pct = token_data.get("dev_supply_percent", 0)
        if dev_supply_pct > 20:
            risks.append({
                "type": "high_dev_supply",
                "severity": "high",
                "description": f"Dev holds {dev_supply_pct}% of supply"
            })
            score += 20
        elif dev_supply_pct > 10:
            risks.append({
                "type": "moderate_dev_supply",
                "severity": "medium",
                "description": f"Dev holds {dev_supply_pct}% of supply"
            })
            score += 10
        
        # Check 5: Top Holder Concentration
        top_holder_pct = token_data.get("top_holder_percent", 0)
        if top_holder_pct > 50:
            risks.append({
                "type": "high_concentration",
                "severity": "critical",
                "description": f"Top holder has {top_holder_pct}%"
            })
            score += 30
        elif top_holder_pct > 30:
            risks.append({
                "type": "moderate_concentration",
                "severity": "medium",
                "description": f"Top holder has {top_holder_pct}%"
            })
            score += 15
        
        # Check 6: Token Age
        age_hours = token_data.get("age_hours", 0)
        if age_hours < 1 and liquidity_locked:  # Very new but locked
            risks.append({
                "type": "very_new",
                "severity": "low",
                "description": "Token is less than 1 hour old"
            })
            score += 5
        
        # Check 7: Known Rug Dev
        dev_address = token_data.get("dev_address", "")
        if dev_address in self.known_rugs:
            risks.append({
                "type": "known_rug_dev",
                "severity": "critical",
                "description": "Dev is on rug list"
            })
            score += 50
        
        # Check 8: Liquidity to MC ratio
        liquidity = token_data.get("liquidity", 0)
        market_cap = token_data.get("market_cap", 1)
        if market_cap > 0:
            liq_mc_ratio = liquidity / market_cap
            if liq_mc_ratio < 0.05:  # Less than 5% liquidity
                risks.append({
                    "type": "low_liquidity_ratio",
                    "severity": "high",
                    "description": f"Liquidity is only {liq_mc_ratio*100:.1f}% of MC"
                })
                score += 20
        
        # Determine verdict
        if score >= 70:
            verdict = "avoid"
        elif score >= 40:
            verdict = "caution"
        elif score >= 20:
            verdict = "monitor"
        else:
            verdict = "safe"
        
        return {
            "verdict": verdict,
            "risk_score": min(100, score),
            "risks": risks,
            "recommendations": self._get_recommendations(verdict),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_recommendations(self, verdict: str) -> List[str]:
        """Get recommendations based on verdict."""
        if verdict == "avoid":
            return ["Do not trade", "Flag dev address"]
        elif verdict == "caution":
            return ["Small position only", "Set tight stop loss", "Monitor dev wallet"]
        elif verdict == "monitor":
            return ["Watch for dev activity", "Check liquidity changes"]
        else:
            return ["Proceed with normal risk management"]
    
    def is_known_rug(self, address: str) -> bool:
        """Check if address is a known rug dev."""
        return address in self.known_rugs
    
    def add_rug_dev(self, address: str):
        """Add address to rug list."""
        self.known_rugs.add(address)
    
    def add_safe_dev(self, address: str):
        """Add address to safe list."""
        self.known_safe.add(address)
    
    def check_dev_history(self, dev_address: str, token_history: List[Dict]) -> Dict:
        """Check dev's history of past tokens."""
        if not token_history:
            return {"verdict": "unknown", "tokens_tracked": 0}
        
        rugs = sum(1 for t in token_history if t.get("rugged", False))
        total = len(token_history)
        rug_rate = rugs / total if total > 0 else 0
        
        verdict = "safe"
        if rug_rate > 0.5:
            verdict = "rug"
        elif rug_rate > 0.3:
            verdict = "risky"
        elif rug_rate > 0.1:
            verdict = "caution"
        
        return {
            "verdict": verdict,
            "rug_rate": rug_rate * 100,
            "tokens_tracked": total,
            "rugs": rugs
        }


# Singleton
_rug_detector: Optional[RugDetector] = None


def get_rug_detector() -> RugDetector:
    """Get rug detector singleton."""
    global _rug_detector
    if _rug_detector is None:
        _rug_detector = RugDetector()
    return _rug_detector


if __name__ == "__main__":
    detector = get_rug_detector()
    
    # Test with sample risky token
    test_token = {
        "liquidity_locked": False,
        "mint_authority": "CUSTOM_MINT_AUTH",
        "freeze_authority": None,
        "dev_supply_percent": 25,
        "top_holder_percent": 55,
        "liquidity": 20000,
        "market_cap": 500000,
        "age_hours": 0.5
    }
    
    result = detector.analyze_token(test_token)
    print(json.dumps(result, indent=2))
