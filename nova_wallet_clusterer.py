#!/usr/bin/env python3
"""
nova_wallet_clusterer.py — Wallet Cluster Detection.
Identifies insider groups and wallet families.
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set


class WalletClusterer:
    """Detects wallet clusters (insider groups)."""
    
    def __init__(self):
        self.wallets = {}  # address -> info
        self.clusters = {}  # cluster_id -> members
        self.relationships = []  # wallet relationships
        self._load_data()
    
    def _load_data(self):
        """Load cluster data."""
        path = Path(__file__).parent / "wallet_clusters.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self.wallets = data.get("wallets", {})
                self.clusters = data.get("clusters", {})
            except:
                pass
    
    def _save_data(self):
        """Save cluster data."""
        path = Path(__file__).parent / "wallet_clusters.json"
        data = {
            "wallets": self.wallets,
            "clusters": self.clusters
        }
        path.write_text(json.dumps(data, indent=2))
    
    def add_wallet(self, address: str, label: str = "unknown", score: float = 0):
        """Add a wallet to track."""
        if address not in self.wallets:
            self.wallets[address] = {
                "label": label,
                "score": score,
                "added_at": datetime.now().isoformat(),
                "clusters": []
            }
            self._save_data()
    
    def link_wallets(self, wallet_a: str, wallet_b: str, relationship: str = "funded"):
        """Link two wallets (indicates same owner/cluster)."""
        # Add to cluster
        cluster_id = f"cluster_{len(self.clusters)}"
        
        if wallet_a not in self.wallets:
            self.add_wallet(wallet_a)
        if wallet_b not in self.wallets:
            self.add_wallet(wallet_b)
        
        # Check if either already in a cluster
        existing_a = self._find_cluster(wallet_a)
        existing_b = self._find_cluster(wallet_b)
        
        if existing_a and existing_b:
            if existing_a != existing_b:
                # Merge clusters
                self.clusters[existing_a].extend(self.clusters[existing_b])
                del self.clusters[existing_b]
        elif existing_a:
            self.clusters[existing_a].append(wallet_b)
        elif existing_b:
            self.clusters[existing_b].append(wallet_a)
        else:
            # New cluster
            self.clusters[cluster_id] = [wallet_a, wallet_b]
        
        # Add relationship
        self.relationships.append({
            "wallet_a": wallet_a,
            "wallet_b": wallet_b,
            "type": relationship,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_data()
    
    def _find_cluster(self, wallet: str) -> Optional[str]:
        """Find cluster containing wallet."""
        for cluster_id, members in self.clusters.items():
            if wallet in members:
                return cluster_id
        return None
    
    def get_cluster(self, wallet: str) -> List[str]:
        """Get all wallets in same cluster."""
        cluster_id = self._find_cluster(wallet)
        if cluster_id:
            return self.clusters.get(cluster_id, [])
        return []
    
    def analyze_cluster(self, wallet: str) -> Dict:
        """Analyze a wallet's cluster."""
        cluster = self.get_cluster(wallet)
        
        if not cluster:
            return {"in_cluster": False}
        
        # Score the cluster
        scores = []
        for w in cluster:
            if w in self.wallets:
                scores.append(self.wallets[w].get("score", 0))
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "in_cluster": True,
            "cluster_id": self._find_cluster(wallet),
            "cluster_size": len(cluster),
            "members": cluster[:10],  # First 10
            "avg_cluster_score": round(avg_score, 1),
            "risk_level": "high" if len(cluster) > 5 else "medium" if len(cluster) > 2 else "low"
        }
    
    def detect_insider_group(self, wallets: List[str]) -> Dict:
        """Detect if multiple wallets form an insider group."""
        # Find clusters represented
        cluster_ids = set()
        cluster_members = defaultdict(list)
        
        for w in wallets:
            cid = self._find_cluster(w)
            if cid:
                cluster_ids.add(cid)
                cluster_members[cid].append(w)
        
        if not cluster_ids:
            return {"is_insider_group": False}
        
        # Calculate cluster strength
        total_cluster_members = sum(len(m) for m in cluster_members.values())
        
        insider_score = 0
        
        # More clusters = stronger group
        if len(cluster_ids) >= 3:
            insider_score += 30
        elif len(cluster_ids) >= 2:
            insider_score += 20
        
        # More members = stronger
        if total_cluster_members >= 5:
            insider_score += 30
        elif total_cluster_members >= 3:
            insider_score += 20
        
        # Check cluster scores
        cluster_scores = []
        for cid in cluster_ids:
            for w in self.clusters.get(cid, []):
                if w in self.wallets:
                    cluster_scores.append(self.wallets[w].get("score", 0))
        
        if cluster_scores:
            avg = sum(cluster_scores) / len(cluster_scores)
            if avg >= 70:
                insider_score += 40
            elif avg >= 50:
                insider_score += 25
        
        is_insider = insider_score >= 50
        
        return {
            "is_insider_group": is_insider,
            "clusters_detected": len(cluster_ids),
            "total_members": total_cluster_members,
            "insider_score": insider_score,
            "clusters": dict(cluster_members)
        }
    
    def get_all_clusters(self) -> Dict:
        """Get all clusters."""
        return {
            "total_clusters": len(self.clusters),
            "clusters": {k: len(v) for k, v in self.clusters.items()}
        }
    
    def get_status(self) -> Dict:
        """Get clusterer status."""
        return {
            "tracked_wallets": len(self.wallets),
            "total_clusters": len(self.clusters),
            "relationships": len(self.relationships)
        }


# Singleton
_wallet_clusterer: Optional[WalletClusterer] = None


def get_wallet_clusterer() -> WalletClusterer:
    """Get wallet clusterer singleton."""
    global _wallet_clusterer
    if _wallet_clusterer is None:
        _wallet_clusterer = WalletClusterer()
    return _wallet_clusterer


if __name__ == "__main__":
    import json
    clusterer = get_wallet_clusterer()
    print(json.dumps(clusterer.get_status(), indent=2))
