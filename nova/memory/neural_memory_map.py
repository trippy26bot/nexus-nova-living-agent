"""
Neural Memory Node - Basic unit of NOVA's memory
"""
from datetime import datetime
from collections import defaultdict


class MemoryNode:
    """
    A single memory node - like a neuron in a brain.
    Can connect to other nodes to form a knowledge graph.
    """
    
    def __init__(self, content, node_type="experience"):
        self.id = f"node_{datetime.utcnow().timestamp()}"
        self.content = content
        self.node_type = node_type  # experience, knowledge, concept
        self.links = []  # Connected node IDs
        self.weight = 1.0  # Importance/strength
        self.access_count = 0
        self.created_at = datetime.utcnow().isoformat()
        self.last_accessed = self.created_at
        self.emotional_weight = 0.5  # How emotionally significant (0-1)
        self.tags = set()
    
    def connect(self, node_id, strength=1.0):
        """Connect this node to another node"""
        if node_id not in self.links:
            self.links.append({"node_id": node_id, "strength": strength})
    
    def reinforce(self, amount=0.1):
        """Strengthen this memory"""
        self.weight = min(3.0, self.weight + amount)
    
    def decay(self, amount=0.05):
        """Weaken this memory over time"""
        self.weight = max(0.1, self.weight - amount)
    
    def access(self):
        """Mark this memory as accessed"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow().isoformat()
        self.reinforce(0.05)  # Frequent access strengthens
    
    def add_tag(self, tag):
        """Add a tag to this memory"""
        self.tags.add(tag)
    
    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "type": self.node_type,
            "weight": self.weight,
            "links": self.links,
            "tags": list(self.tags),
            "created": self.created_at,
            "accesses": self.access_count
        }


class NeuralMemoryMap:
    """
    Neural memory graph - stores interconnected memories like a brain.
    """
    
    def __init__(self):
        self.nodes = {}
        self.node_index = defaultdict(list)  # Tag -> node IDs
    
    def add(self, content, node_type="experience", tags=None):
        """Add a new memory node"""
        node = MemoryNode(content, node_type)
        self.nodes[node.id] = node
        
        # Index by tags
        if tags:
            for tag in tags:
                self.node_index[tag].append(node.id)
        
        return node
    
    def connect(self, node_id_a, node_id_b, strength=1.0):
        """Connect two memories"""
        if node_id_a in self.nodes and node_id_b in self.nodes:
            self.nodes[node_id_a].connect(node_id_b, strength)
            self.nodes[node_id_b].connect(node_id_a, strength)
    
    def recall(self, query, limit=10):
        """Recall memories related to a query"""
        results = []
        
        for node in self.nodes.values():
            if self._matches_query(node.content, query):
                node.access()
                results.append((node, node.weight))
        
        # Sort by weight
        results.sort(key=lambda x: x[1], reverse=True)
        
        return [r[0] for r in results[:limit]]
    
    def recall_by_tag(self, tag, limit=10):
        """Recall memories by tag"""
        node_ids = self.node_index.get(tag, [])
        results = []
        
        for nid in node_ids:
            if nid in self.nodes:
                self.nodes[nid].access()
                results.append(self.nodes[nid])
        
        return results[:limit]
    
    def recall_path(self, start_node_id, depth=2):
        """Recall connected memories (neural path)"""
        if start_node_id not in self.nodes:
            return []
        
        visited = set()
        path = []
        
        def traverse(node_id, current_depth):
            if current_depth > depth or node_id in visited:
                return
            
            visited.add(node_id)
            
            if node_id in self.nodes:
                node = self.nodes[node_id]
                path.append(node)
                
                for link in node.links:
                    traverse(link["node_id"], current_depth + 1)
        
        traverse(start_node_id, 0)
        return path
    
    def _matches_query(self, content, query):
        """Check if content matches query"""
        query_lower = query.lower()
        content_lower = str(content).lower()
        
        # Simple keyword matching
        return query_lower in content_lower
    
    def strengthen_connection(self, node_id_a, node_id_b):
        """Strengthen connection between two nodes"""
        for node_id in [node_id_a, node_id_b]:
            if node_id in self.nodes:
                for link in self.nodes[node_id].links:
                    if link["node_id"] == node_id_b or link["node_id"] == node_id_a:
                        link["strength"] = min(2.0, link["strength"] + 0.1)
    
    def get_stats(self):
        """Get memory statistics"""
        total_links = sum(len(n.links) for n in self.nodes.values())
        
        by_type = defaultdict(int)
        for node in self.nodes.values():
            by_type[node.node_type] += 1
        
        return {
            "total_nodes": len(self.nodes),
            "total_connections": total_links,
            "by_type": dict(by_type),
            "avg_weight": sum(n.weight for n in self.nodes.values()) / max(1, len(self.nodes))
        }
    
    def consolidate(self):
        """Consolidate memories - strengthen important ones, decay weak ones"""
        for node in self.nodes.values():
            # Decay based on access
            if node.access_count == 0:
                node.decay(0.02)
        
        # Remove very weak memories
        weak_nodes = [nid for nid, n in self.nodes.items() if n.weight < 0.2]
        for nid in weak_nodes:
            del self.nodes[nid]
        
        return len(weak_nodes)
