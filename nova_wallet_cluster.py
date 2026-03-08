#!/usr/bin/env python3
"""
nova_wallet_cluster.py — Wallet Cluster Detection.
Maps wallet relationships to identify insider groups.
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


class WalletCluster:
    """Detects wallet clusters (insider groups)."""
    
    def __init__(self):
        self.wallets = {}  # address -> info
        self.clusters = {}  # cluster_id -> [wallets]
        self.funding_map = {}  # wallet -> funder
        self._load_clusters()
    
    def _load_clusters(self):
        """Load cluster data."""
        path = Path(__file__).parent / "wallet_clusters.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self.wallets = data.get("wallets", {})
                self.clusters = data.get("clusters", {})
                self.funding_map = data.get("funding_map", {})
            except:
                pass
    
    def _save_clusters(self):
        """Save cluster data."""
        path = Path(__file__).parent / "wallet_clusters.json"
        data = {
            "wallets": self.wallets,
            "clusters": self.clusters,
            "funding_map": self.funding_map
        }
        path.write_text(json.dumps(data, indent=2))
    
    def add_funding_link(self, wallet: str, funder: str):
        """Record that funder funded wallet."""
        self.funding_map[wallet] = funder
        
        # Update wallet info
        if wallet not in self.wallets:
            self.wallets[wallet] = {"added_at": datetime.now().isoformat()}
        
        # Check if this creates a cluster
        if funder in self.wallets:
            # Find funder's cluster
            funder_cluster = self._find_cluster(funder)
            
            # Add wallet to same cluster
            cluster_id = funder_cluster or f"cluster_{len(self.clusters)}"
            
            if cluster_id not in self.clusters:
                self.clusters[cluster_id] = []
            
            if wallet not in self.clusters[cluster_id]:
                self.clusters[cluster_id].append(wallet)
        
        self._save_clusters()
    
    def _find_cluster(self, wallet: str) -> Optional[str]:
        """Find which cluster a wallet belongs to."""
        for cluster_id, members in self.clusters.items():
            if wallet in members:
                return cluster_id
        return None
    
    def get_cluster(self, wallet: str) -> List[str]:
        """Get all wallets in the same cluster as given wallet."""
        cluster_id = self._find_cluster(wallet)
        if cluster_id:
            return self.clusters.get(cluster_id, [])
        return []
    
    def is_in_cluster(self, wallet: str) -> bool:
        """Check if wallet is part of any cluster."""
        return self._find_cluster(wallet) is not None
    
    def add_whale(self, address: str, label: str = "manual", score: float = 0):
        """Add a whale wallet."""
        self.wallets[address] = {
            "label": label,
            "score": score,
            "added_at": datetime.now().isoformat(),
            "type": "whale"
        }
        self._save_clusters()
    
    def get_cluster_size(self, wallet: str) -> int:
        """Get size of wallet's cluster."""
        cluster = self.get_cluster(wallet)
        return len(cluster)
    
    def detect_insider_activity(self, wallets: List[str]) -> Dict:
        """Detect if multiple wallets from same cluster are active."""
        # Group by cluster
        cluster_activity = defaultdict(list)
        
        for wallet in wallets:
            cluster_id = self._find_cluster(wallet)
            if cluster_id:
                cluster_activity[cluster_id].append(wallet)
        
        # Find clusters with multiple activity
        insider_signals = []
        for cluster_id, active_wallets in cluster_activity.items():
            if len(active_wallets) >= 2:
                insider_signals.append({
                    "cluster_id": cluster_id,
                    "active_wallets": active_wallets,
                    "count": len(active_wallets),
                    "signal": "strong" if len(active_wallets) >= 3 else "moderate"
                })
        
        return {
            "insider_detected": len(insider_signals) > 0,
            "signals": insider_signals
        }
    
    def get_all_clusters(self) -> Dict:
        """Get all clusters."""
        return self.clusters
    
    def get_status(self) -> Dict:
        """Get cluster status."""
        return {
            "total_wallets": len(self.wallets),
            "total_clusters": len(self.clusters),
            "clusters": {k: len(v) for k, v in list(self.clusters.items())[:5]}
        }


# Singleton
_wallet_cluster: Optional[WalletCluster] = None


def get_wallet_cluster() -> WalletCluster:
    """Get wallet cluster singleton."""
    global _wallet_cluster
    if _wallet_cluster is None:
        _wallet_cluster = WalletCluster()
    return _wallet_cluster


if __name__ == "__main__":
    cluster = get_wallet_cluster()
    print(json.dumps(cluster.get_status(), indent=2))
