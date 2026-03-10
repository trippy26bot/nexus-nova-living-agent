#!/usr/bin/env python3
"""
Nova Knowledge Graph
Stores relationships between concepts for reasoning
"""

import time
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field

@dataclass
class Node:
    """A concept in the knowledge graph"""
    name: str
    node_type: str  # person, concept, object, agent, etc.
    properties: Dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

@dataclass
class Edge:
    """A relationship between two nodes"""
    source: str
    relation: str
    target: str
    weight: float = 1.0
    created_at: float = field(default_factory=time.time)

class KnowledgeGraph:
    """
    Stores memory as nodes and edges.
    Enables reasoning about relationships.
    """
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.edge_index: Dict[str, List[Edge]] = {}  # source -> edges
    
    def add_node(self, name: str, node_type: str = "concept", properties: Dict = None) -> Node:
        """Add a node to the graph"""
        if name in self.nodes:
            return self.nodes[name]
        
        node = Node(
            name=name,
            node_type=node_type,
            properties=properties or {}
        )
        self.nodes[name] = node
        return node
    
    def add_edge(self, source: str, relation: str, target: str, weight: float = 1.0) -> Edge:
        """Add a relationship between nodes"""
        # Ensure nodes exist
        self.add_node(source)
        self.add_node(target)
        
        edge = Edge(
            source=source,
            relation=relation,
            target=target,
            weight=weight
        )
        
        self.edges.append(edge)
        
        # Index by source
        if source not in self.edge_index:
            self.edge_index[source] = []
        self.edge_index[source].append(edge)
        
        return edge
    
    def get_node(self, name: str) -> Optional[Node]:
        """Get a node by name"""
        return self.nodes.get(name)
    
    def get_edges_from(self, source: str) -> List[Edge]:
        """Get all edges from a node"""
        return self.edge_index.get(source, [])
    
    def get_edges_to(self, target: str) -> List[Edge]:
        """Get all edges pointing to a node"""
        return [e for e in self.edges if e.target == target]
    
    def traverse(self, start: str, depth: int = 2) -> Dict[str, List[str]]:
        """
        Traverse the graph from a starting node.
        Returns connections at each depth level.
        """
        if start not in self.nodes:
            return {}
        
        result = {0: [start]}
        visited = {start}
        current_level = {start}
        
        for d in range(1, depth + 1):
            next_level = set()
            
            for node in current_level:
                edges = self.get_edges_from(node)
                for edge in edges:
                    if edge.target not in visited:
                        next_level.add(edge.target)
                        visited.add(edge.target)
            
            if next_level:
                result[d] = list(next_level)
                current_level = next_level
            else:
                break
        
        return result
    
    def find_path(self, start: str, end: str, max_depth: int = 3) -> Optional[List[str]]:
        """Find a path between two nodes"""
        if start not in self.nodes or end not in self.nodes:
            return None
        
        # BFS
        queue = [(start, [start])]
        visited = {start}
        
        while queue:
            current, path = queue.pop(0)
            
            if current == end:
                return path
            
            if len(path) >= max_depth:
                continue
            
            for edge in self.get_edges_from(current):
                if edge.target not in visited:
                    visited.add(edge.target)
                    queue.append((edge.target, path + [edge.target]))
        
        return None
    
    def find_related(self, concept: str, max_results: int = 5) -> List[Dict]:
        """Find related concepts"""
        if concept not in self.nodes:
            return []
        
        related = []
        
        # Outgoing
        for edge in self.get_edges_from(concept):
            related.append({
                "concept": edge.target,
                "relation": edge.relation,
                "direction": "out"
            })
        
        # Incoming
        for edge in self.get_edges_to(concept):
            related.append({
                "concept": edge.source,
                "relation": edge.relation,
                "direction": "in"
            })
        
        return related[:max_results]
    
    def extract_from_text(self, text: str):
        """Extract knowledge from text (simple version)"""
        # Simple extraction - just store the text as a node for now
        words = text.lower().split()
        
        # Add as a knowledge node
        self.add_node(text[:50], "memory", {"full_text": text})
        
        # Try to find subject-verb-object patterns (very basic)
        # This is a simplified version
        return {"extracted": True, "text": text[:50]}
    
    def get_statistics(self) -> Dict:
        """Get graph statistics"""
        node_types = {}
        for node in self.nodes.values():
            node_types[node.node_type] = node_types.get(node.node_type, 0) + 1
        
        relation_types = {}
        for edge in self.edges:
            relation_types[edge.relation] = relation_types.get(edge.relation, 0) + 1
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": node_types,
            "relation_types": relation_types
        }
    
    def clear(self):
        """Clear the graph"""
        self.nodes = {}
        self.edges = []
        self.edge_index = {}


# Global instance
_knowledge_graph = None

def get_knowledge_graph() -> KnowledgeGraph:
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = KnowledgeGraph()
    return _knowledge_graph
