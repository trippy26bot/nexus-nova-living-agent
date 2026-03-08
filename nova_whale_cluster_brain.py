#!/usr/bin/env python3
"""
nova_whale_cluster_brain.py — Multi-tier whale + cluster confidence.
Wires individual whales + clusters into signal hierarchy.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from nova_whale_hunter import get_whale_hunter
from nova_wallet_clusterer import get_wallet_clusterer
from nova_wallet_predictor import get_wallet_predictor


class WhaleClusterBrain:
    """Multi-tier whale and cluster confidence scoring."""
    
    def __init__(self):
        self.whale_hunter = get_whale_hunter()
        self.clusterer = get_wallet_clusterer()
        self.predictor = get_wallet_predictor()
        
        # Signal weights
        self.weights = {
            "single_whale": 0.4,
            "multi_whale": 0.6,
            "cluster": 0.8,
            "insider_cluster": 1.0
        }
        
    def analyze_whale_activity(self, token: str, recent_trades: List[Dict]) -> Dict:
        """Analyze whale activity for a token."""
        
        if not recent_trades:
            return {"tier": 0, "confidence": 0, "signal": "none"}
        
        # Get unique wallets
        wallets = list(set(t.get("wallet") for t in recent_trades if t.get("wallet")))
        
        # Check for clusters
        cluster_analysis = self.clusterer.detect_insider_group(wallets)
        
        # Calculate scores
        whale_score = 0.0
        whale_count = len(wallets)
        
        # Score each whale
        for wallet in wallets:
            pred = self.predictor.predict(wallet)
            if pred.get("known"):
                whale_score += pred["scores"].get("overall", 0) / 100
        
        avg_whale_score = whale_score / max(1, whale_count)
        
        # Determine tier
        tier = 0
        confidence = 0.0
        signal = "none"
        bonuses = []
        
        # Tier 1: Single smart whale
        if whale_count == 1 and avg_whale_score > 0.6:
            tier = 1
            confidence = avg_whale_score * self.weights["single_whale"]
            signal = "single_whale"
        
        # Tier 2: Multiple smart wallets
        elif whale_count >= 2 and avg_whale_score > 0.5:
            tier = 2
            # Bonus for multiple whales
            multi_bonus = min(0.2, (whale_count - 1) * 0.05)
            confidence = (avg_whale_score * self.weights["multi_whale"]) + multi_bonus
            signal = "multi_whale"
            bonuses.append(f"{whale_count} whales")
        
        # Tier 3: Cluster detected
        if cluster_analysis.get("is_insider_group"):
            tier = 3
            cluster_score = cluster_analysis.get("insider_score", 0) / 100
            confidence = max(confidence, cluster_score * self.weights["cluster"])
            signal = "cluster"
            bonuses.append(f"cluster ({cluster_analysis.get('clusters_detected', 0)} groups)")
        
        # Tier 4: Strong insider cluster
        if cluster_analysis.get("insider_score", 0) >= 70:
            tier = 4
            confidence = max(confidence, 0.9)
            signal = "insider_cluster"
            bonuses.append("strong insider")
        
        # Build response
        result = {
            "token": token,
            "tier": tier,
            "signal": signal,
            "confidence": round(min(1.0, confidence), 3),
            "whale_count": whale_count,
            "avg_whale_score": round(avg_whale_score, 2),
            "bonuses": bonuses,
            "cluster_analysis": {
                "is_cluster": cluster_analysis.get("is_insider_group", False),
                "clusters": cluster_analysis.get("clusters_detected", 0)
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Determine action
        if tier >= 3:
            result["action"] = "aggressive"
        elif tier == 2:
            result["action"] = "normal"
        elif tier == 1:
            result["action"] = "cautious"
        else:
            result["action"] = "watch"
        
        return result
    
    def get_confidence_for_signal(self, token: str, trades: List[Dict]) -> Dict:
        """Get full confidence score combining all tiers."""
        
        analysis = self.analyze_whale_activity(token, trades)
        
        # Combine with predictor scores
        wallets = list(set(t.get("wallet") for t in trades if t.get("wallet")))
        
        best_wallet_score = 0
        for wallet in wallets:
            pred = self.predictor.predict(wallet)
            if pred.get("known"):
                best_wallet_score = max(best_wallet_score, pred["scores"].get("overall", 0) / 100)
        
        # Final confidence
        final_confidence = (
            analysis["confidence"] * 0.7 +
            best_wallet_score * 0.3
        )
        
        analysis["final_confidence"] = round(min(1.0, final_confidence), 3)
        
        # Signal strength label
        if final_confidence >= 0.85:
            analysis["strength"] = "VERY_STRONG"
        elif final_confidence >= 0.70:
            analysis["strength"] = "STRONG"
        elif final_confidence >= 0.50:
            analysis["strength"] = "MODERATE"
        elif final_confidence >= 0.30:
            analysis["strength"] = "WEAK"
        else:
            analysis["strength"] = "NONE"
        
        return analysis


# Singleton
_whale_cluster_brain: Optional[WhaleClusterBrain] = None


def get_whale_cluster_brain() -> WhaleClusterBrain:
    """Get whale cluster brain singleton."""
    global _whale_cluster_brain
    if _whale_cluster_brain is None:
        _whale_cluster_brain = WhaleClusterBrain()
    return _whale_cluster_brain


if __name__ == "__main__":
    brain = get_whale_cluster_brain()
    
    # Test
    test_trades = [
        {"wallet": "wallet1", "token": "ABC", "action": "buy"},
        {"wallet": "wallet2", "token": "ABC", "action": "buy"},
    ]
    
    result = brain.get_confidence_for_signal("ABC", test_trades)
    print(json.dumps(result, indent=2))
