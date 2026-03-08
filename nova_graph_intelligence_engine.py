#!/usr/bin/env python3
"""
nova_graph_intelligence_engine.py — Graph Intelligence Engine.
Maps wallet relationships and detects insider networks.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class WalletNode:
    """Represents a wallet in the graph."""
    address: str
    first_seen: str = ""
    total_received: float = 0.0
    total_sent: float = 0.0
    tokens_interacted: List[str] = field(default_factory=list)
    wallets_funded: List[str] = field(default_factory=list)
    wallets_funded_by: List[str] = field(default_factory=list)
    clusters: List[str] = field(default_factory=list)
    reputation_score: float = 0.0


@dataclass
class Edge:
    """Represents a relationship between wallets."""
    wallet_a: str
    wallet_b: str
    edge_type: str  # funding, trade, lp, token_launch
    weight: float = 0.0
    last_updated: str = ""
    transaction_count: int = 0


class GraphIntelligenceEngine:
    """Maps wallet relationships and detects networks."""
    
    def __init__(self):
        self.wallets: Dict[str, WalletNode] = {}
        self.edges: List[Edge] = []
        self.clusters: Dict[str, List[str]] = {}
        self.path = Path(__file__).parent
        self._load()
        
    def _load(self):
        """Load saved graph data."""
        graph_file = self.path / "wallet_graph.json"
        if graph_file.exists():
            try:
                data = json.loads(graph_file.read_text())
                # Rebuild wallets
                for addr, wdata in data.get("wallets", {}).items():
                    self.wallets[addr] = WalletNode(**wdata)
                # Rebuild edges
                for edata in data.get("edges", []):
                    self.edges.append(Edge(**edata))
                self.clusters = data.get("clusters", {})
            except:
                pass
    
    def _save(self):
        """Save graph data."""
        graph_file = self.path / "wallet_graph.json"
        data = {
            "wallets": {addr: vars(w) for addr, w in self.wallets.items()},
            "edges": [vars(e) for e in self.edges],
            "clusters": self.clusters
        }
        graph_file.write_text(json.dumps(data, indent=2))
    
    def add_wallet(self, address: str):
        """Add a wallet to the graph."""
        if address not in self.wallets:
            self.wallets[address] = WalletNode(
                address=address,
                first_seen=datetime.now().isoformat()
            )
    
    def add_edge(self, wallet_a: str, wallet_b: str, edge_type: str, weight: float = 1.0):
        """Add a relationship edge between wallets."""
        # Add wallets if not exist
        self.add_wallet(wallet_a)
        self.add_wallet(wallet_b)
        
        # Check if edge exists
        for edge in self.edges:
            if (edge.wallet_a == wallet_a and edge.wallet_b == wallet_b) or \
               (edge.wallet_a == wallet_b and edge.wallet_b == wallet_a):
                edge.weight += weight
                edge.transaction_count += 1
                edge.last_updated = datetime.now().isoformat()
                break
        else:
            # New edge
            self.edges.append(Edge(
                wallet_a=wallet_a,
                wallet_b=wallet_b,
                edge_type=edge_type,
                weight=weight,
                last_updated=datetime.now().isoformat(),
                transaction_count=1
            ))
            
            # Update wallet relationships
            if edge_type == "funding":
                self.wallets[wallet_a].wallets_funded.append(wallet_b)
                self.wallets[wallet_b].wallets_funded_by.append(wallet_a)
        
        self._save()
    
    def add_transaction(self, from_wallet: str, to_wallet: str, token: str, 
                        tx_type: str, value: float = 0):
        """Record a transaction and update graph."""
        # Add funding edge
        if tx_type == "transfer" or tx_type == "funding":
            self.add_edge(from_wallet, to_wallet, "funding", weight=value/1000)
        
        # Update wallet stats
        for w in [from_wallet, to_wallet]:
            if w in self.wallets:
                self.wallets[w].tokens_interacted.append(token)
        
        # Check for synchronized trading (same token, different wallets)
        if token in self.wallets[from_wallet].tokens_interacted:
            # Find other wallets that traded this token
            for addr, wallet in self.wallets.items():
                if addr != from_wallet and token in wallet.tokens_interacted:
                    self.add_edge(from_wallet, addr, "shared_token", weight=0.5)
    
    def compute_clusters(self):
        """Detect wallet clusters using graph analysis."""
        # Simple connected components
        visited = set()
        
        for start_wallet in self.wallets:
            if start_wallet in visited:
                continue
            
            cluster = []
            queue = [start_wallet]
            
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                    
                visited.add(current)
                cluster.append(current)
                
                # Find connected wallets
                for edge in self.edges:
                    neighbor = None
                    if edge.wallet_a == current:
                        neighbor = edge.wallet_b
                    elif edge.wallet_b == current:
                        neighbor = edge.wallet_a
                    
                    if neighbor and neighbor not in visited:
                        queue.append(neighbor)
            
            if len(cluster) >= 2:
                cluster_id = f"cluster_{len(self.clusters)}"
                self.clusters[cluster_id] = cluster
                
                # Update wallet cluster membership
                for wallet in cluster:
                    if cluster_id not in self.wallets[wallet].clusters:
                        self.wallets[wallet].clusters.append(cluster_id)
        
        self._save()
    
    def detect_insider_network(self, token: str) -> Dict:
        """Detect if there's an insider network trading a token."""
        # Find all wallets that interacted with this token
        token_wallets = [
            addr for addr, wallet in self.wallets.items()
            if token in wallet.tokens_interacted
        ]
        
        if len(token_wallets) < 2:
            return {"detected": False, "reason": "insufficient_wallets"}
        
        # Check for connections between these wallets
        connected_pairs = 0
        for edge in self.edges:
            if edge.wallet_a in token_wallets and edge.wallet_b in token_wallets:
                connected_pairs += 1
        
        # Calculate network density
        total_possible = len(token_wallets) * (len(token_wallets) - 1) / 2
        density = connected_pairs / max(1, total_possible)
        
        # Calculate cluster score
        cluster_score = 0
        for wallet in token_wallets:
            cluster_score += len(self.wallets[wallet].clusters)
        
        cluster_score = cluster_score / max(1, len(token_wallets))
        
        # Determine if insider network
        insider_score = (density * 50) + (cluster_score * 50)
        
        return {
            "detected": insider_score > 40,
            "insider_score": round(insider_score, 1),
            "wallets_involved": len(token_wallets),
            "connected_pairs": connected_pairs,
            "network_density": round(density, 3),
            "cluster_presence": cluster_score > 0
        }
    
    def get_wallet_network(self, wallet: str, depth: int = 2) -> Dict:
        """Get network around a wallet."""
        if wallet not in self.wallets:
            return {"found": False}
        
        network = {wallet}
        current_depth = {wallet: 0}
        queue = [(wallet, 0)]
        
        while queue:
            current, depth = queue.pop(0)
            
            if depth >= max_depth:
                continue
                
            # Find connected wallets
            for edge in self.edges:
                neighbor = None
                if edge.wallet_a == current:
                    neighbor = edge.wallet_b
                elif edge.wallet_b == current:
                    neighbor = edge.wallet_a
                
                if neighbor and neighbor not in network:
                    network.add(neighbor)
                    queue.append((neighbor, depth + 1))
        
        return {
            "wallet": wallet,
            "network_size": len(network),
            "wallets": list(network)
        }
    
    def predict_wallet_behavior(self, wallet: str) -> Dict:
        """Predict wallet behavior based on graph position."""
        if wallet not in self.wallets:
            return {"known": False}
        
        w = self.wallets[wallet]
        
        # Score based on network position
        network_score = 0
        
        # Funding others = potential dev/insider
        if len(w.wallets_funded) > 3:
            network_score += 30
        
        # Funded by many = whale
        if len(w.wallets_funded_by) > 5:
            network_score += 25
        
        # In clusters = coordinated
        if len(w.clusters) > 1:
            network_score += 20
        
        # Multiple tokens = active trader
        if len(set(w.tokens_interacted)) > 10:
            network_score += 15
        
        # Connected to high-reputation wallets
        for neighbor_addr in w.wallets_funded + w.wallets_funded_by:
            if neighbor_addr in self.wallets:
                network_score += self.wallets[neighbor_addr].reputation_score * 0.1
        
        return {
            "wallet": wallet,
            "network_score": min(100, round(network_score, 1)),
            "likely_type": self._classify_wallet(network_score),
            "funded_count": len(w.wallets_funded),
            "funded_by_count": len(w.wallets_funded_by),
            "clusters": len(w.clusters),
            "tokens_traded": len(set(w.tokens_interacted))
        }
    
    def _classify_wallet(self, score: float) -> str:
        """Classify wallet based on network score."""
        if score >= 70:
            return "insider"
        elif score >= 50:
            return "whale"
        elif score >= 30:
            return "active_trader"
        else:
            return "casual"
    
    def get_status(self) -> Dict:
        """Get graph status."""
        return {
            "total_wallets": len(self.wallets),
            "total_edges": len(self.edges),
            "total_clusters": len(self.clusters),
            "avg_cluster_size": sum(len(c) for c in self.clusters.values()) / max(1, len(self.clusters))
        }


# Singleton
_graph_engine: Optional[GraphIntelligenceEngine] = None


def get_graph_engine() -> GraphIntelligenceEngine:
    """Get graph intelligence engine singleton."""
    global _graph_engine
    if _graph_engine is None:
        _graph_engine = GraphIntelligenceEngine()
    return _graph_engine


if __name__ == "__main__":
    engine = get_graph_engine()
    
    # Test
    engine.add_edge("wallet_A", "wallet_B", "funding", 1000)
    engine.add_edge("wallet_A", "wallet_C", "funding", 800)
    engine.compute_clusters()
    
    print(json.dumps(engine.get_status(), indent=2))
