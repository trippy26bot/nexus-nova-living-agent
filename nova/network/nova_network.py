#!/usr/bin/env python3
"""
Nova Distributed Network
Allows multiple Nova nodes to collaborate
"""

import uuid
import socket
import json
import time
from typing import Optional


class NovaNode:
    """
    A single Nova instance that can join a network.
    Each node keeps its own identity.
    """
    
    def __init__(self, name: str = "Nova"):
        self.node_id = str(uuid.uuid4())[:8]
        self.name = name
        self.host = socket.gethostname()
        self.peers = {}
        self.knowledge_shared = 0
    
    def get_info(self) -> dict:
        """Get node information"""
        return {
            "node_id": self.node_id,
            "name": self.name,
            "host": self.host,
            "peers": len(self.peers),
            "knowledge_shared": self.knowledge_shared
        }
    
    def register_peer(self, peer_id: str, peer_info: dict):
        """Register another Nova node"""
        self.peers[peer_id] = {
            **peer_info,
            "last_seen": time.time()
        }
    
    def remove_peer(self, peer_id: str):
        """Remove a peer"""
        if peer_id in self.peers:
            del self.peers[peer_id]
    
    def get_peers(self) -> dict:
        """Get all peers"""
        # Clean stale peers (>5 min)
        now = time.time()
        stale = [p for p, info in self.peers.items() 
                 if now - info.get("last_seen", 0) > 300]
        for p in stale:
            del self.peers[p]
        return self.peers


class PeerDiscovery:
    """
    Discovers other Nova nodes on the network.
    """
    
    def __init__(self, port: int = 5050):
        self.port = port
        self.discovered = []
    
    def scan_local_network(self, subnet: str = "192.168.1.") -> list:
        """Scan local network for Nova nodes"""
        nodes = []
        
        for i in range(1, 255):
            addr = f"{subnet}{i}"
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.2)
                result = sock.connect_ex((addr, self.port))
                sock.close()
                
                if result == 0:
                    nodes.append(addr)
            except:
                pass
        
        return nodes
    
    def discover(self) -> list:
        """Run discovery"""
        self.discovered = self.scan_local_network()
        return self.discovered


class MessageBus:
    """
    Secure communication between Nova nodes.
    """
    
    def __init__(self, node: NovaNode):
        self.node = node
    
    def create_message(self, msg_type: str, data: dict) -> dict:
        """Create a message packet"""
        return {
            "from": self.node.node_id,
            "type": msg_type,
            "data": data,
            "timestamp": time.time()
        }
    
    def send_to_peer(self, peer_id: str, message: dict, peer_info: dict):
        """Send message to a peer"""
        # In production, use TLS encryption
        # This is a placeholder
        pass
    
    def broadcast(self, message: dict, peers: dict):
        """Broadcast to all peers"""
        for peer_id, peer_info in peers.items():
            self.send_to_peer(peer_id, message, peer_info)


class KnowledgeSync:
    """
    Share knowledge between Nova nodes.
    """
    
    def __init__(self, node: NovaNode):
        self.node = node
    
    def share_discovery(self, knowledge: dict, peers: dict):
        """Share new knowledge with peers"""
        message = {
            "type": "knowledge",
            "data": knowledge
        }
        
        for peer_id in peers:
            self.node.knowledge_shared += 1
            # In production: actually send the data
    
    def receive_knowledge(self, data: dict) -> dict:
        """Process incoming knowledge"""
        return {
            "learned": True,
            "source": data.get("source", "unknown"),
            "content": data.get("content", {})
        }


class TaskDistributor:
    """
    Distribute tasks across Nova nodes.
    """
    
    def __init__(self, node: NovaNode):
        self.node = node
    
    def distribute(self, task: dict, peers: dict) -> Optional[str]:
        """Distribute task to least busy peer"""
        if not peers:
            return None
        
        # Simple: pick first available peer
        # In production: check peer load
        selected = list(peers.keys())[0]
        return selected
    
    def receive_task(self, task: dict) -> dict:
        """Process incoming task"""
        return {
            "task_received": True,
            "task": task,
            "node": self.node.node_id
        }


class NovaNetwork:
    """
    Complete distributed Nova network.
    """
    
    def __init__(self, name: str = "Nova"):
        self.node = NovaNode(name)
        self.discovery = PeerDiscovery()
        self.message_bus = MessageBus(self.node)
        self.knowledge_sync = KnowledgeSync(self.node)
        self.task_distributor = TaskDistributor(self.node)
    
    def get_status(self) -> dict:
        """Get network status"""
        return {
            "node": self.node.get_info(),
            "peers": len(self.node.get_peers()),
            "discovered": len(self.discovery.discovered)
        }
    
    def discover_peers(self) -> int:
        """Discover other Nova nodes"""
        self.discovery.discover()
        return len(self.discovery.discovered)


# Global instance
_nova_network = None

def get_nova_network(name: str = "Nova") -> NovaNetwork:
    global _nova_network
    if _nova_network is None:
        _nova_network = NovaNetwork(name)
    return _nova_network
