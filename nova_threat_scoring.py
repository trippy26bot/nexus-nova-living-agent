#!/usr/bin/env python3
"""
nova_threat_scoring.py — Threat Scoring Engine.
Combines all threat data into final risk score.
"""

import json
from typing import Dict, Optional

from nova_blacklist_db import get_blacklist_db
from nova_wallet_reputation import get_wallet_reputation
from nova_rug_scanner import get_rug_scanner


class ThreatScoring:
    """Calculates overall threat score for trades."""
    
    def __init__(self):
        self.blacklist = get_blacklist_db()
        self.reputation = get_wallet_reputation()
        self.rug_scanner = get_rug_scanner()
    
    async def assess(self, token: str, dev_wallet: str, 
                    contract: str, trade_wallets: list) -> Dict:
        """Calculate threat score for a trade."""
        
        # Initialize scores
        wallet_risk = 0
        contract_risk = 0
        dev_risk = 0
        liquidity_risk = 0
        
        # 1. Blacklist checks
        blacklist_check = self.blacklist.check_entity(
            address=dev_wallet,
            token=token,
            contract=contract
        )
        
        if blacklist_check["scam_wallet"]:
            wallet_risk += 100
        if blacklist_check["rug_dev"]:
            dev_risk += 100
        if blacklist_check["honeypot"]:
            contract_risk += 100
        if blacklist_check["suspicious_cluster"]:
            wallet_risk += 40
        if blacklist_check["malicious_token"]:
            contract_risk += 80
        
        # 2. Wallet reputation
        for wallet in trade_wallets:
            rep = self.reputation.get_reputation(wallet)
            score = rep.get("score", 50)
            
            if score < 0:
                wallet_risk += 30
            elif score < 30:
                wallet_risk += 15
        
        # 3. Contract security scan
        if contract:
            scan = await self.rug_scanner.scan(contract)
            contract_risk += scan.get("risk_score", 0)
        
        # Calculate total risk
        total_risk = wallet_risk + contract_risk + dev_risk + liquidity_risk
        total_risk = min(100, total_risk)
        
        # Determine verdict
        if total_risk >= 60:
            verdict = "BLOCK"
        elif total_risk >= 30:
            verdict = "CAUTION"
        else:
            verdict = "CLEAR"
        
        return {
            "token": token,
            "total_risk": total_risk,
            "verdict": verdict,
            "components": {
                "wallet_risk": wallet_risk,
                "contract_risk": contract_risk,
                "dev_risk": dev_risk,
                "liquidity_risk": liquidity_risk
            },
            "blacklist_hits": blacklist_check
        }


# Singleton
_threat_scoring: Optional[ThreatScoring] = None


def get_threat_scoring() -> ThreatScoring:
    """Get threat scoring singleton."""
    global _threat_scoring
    if _threat_scoring is None:
        _threat_scoring = ThreatScoring()
    return _threat_scoring


if __name__ == "__main__":
    import asyncio
    scoring = get_threat_scoring()
    result = asyncio.run(scoring.assess("TEST", "dev_wallet", "contract", []))
    print(json.dumps(result, indent=2))
