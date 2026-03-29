"""
brain/knowledge_graph.py
Lightweight JSON-backed knowledge graph for Nova's long-term semantic memory.
No external DB — stored to memory/knowledge_graph.json
"""

from __future__ import annotations
import json
import os
import uuid
from datetime import datetime
from typing import Literal, Optional

GRAPH_PATH = "/Users/dr.claw/.openclaw/workspace/memory/knowledge_graph.json"

NodeType = Literal["concept", "entity", "belief", "person", "place", "topic"]
EdgeType = Literal["causes", "contradicts", "supports", "relates-to", "is-a", "leads-to"]


def _load_graph() -> dict:
    if not os.path.exists(GRAPH_PATH):
        return {"nodes": {}, "edges": []}
    with open(GRAPH_PATH, "r") as f:
        return json.load(f)


def _save_graph(graph: dict) -> None:
    with open(GRAPH_PATH, "w") as f:
        json.dump(graph, f, indent=2)


def add_node(
    node_id: Optional[str],
    label: str,
    node_type: NodeType,
    properties: Optional[dict] = None
) -> str:
    """Add a node to the graph. Returns the node_id."""
    graph = _load_graph()
    if node_id is None:
        node_id = f"{node_type}_{uuid.uuid4().hex[:8]}"
    graph["nodes"][node_id] = {
        "id": node_id,
        "label": label,
        "type": node_type,
        "properties": properties or {},
        "created_at": datetime.now().isoformat()
    }
    _save_graph(graph)
    return node_id


def add_edge(
    from_id: str,
    to_id: str,
    edge_type: EdgeType,
    weight: float = 1.0,
    properties: Optional[dict] = None
) -> bool:
    """Add a directed edge between two nodes. Returns False if either node missing."""
    graph = _load_graph()
    if from_id not in graph["nodes"] or to_id not in graph["nodes"]:
        return False
    edge_id = f"e_{uuid.uuid4().hex[:8]}"
    graph["edges"].append({
        "id": edge_id,
        "from": from_id,
        "to": to_id,
        "type": edge_type,
        "weight": weight,
        "properties": properties or {},
        "created_at": datetime.now().isoformat()
    })
    _save_graph(graph)
    return True


def query_node(node_id: str) -> dict | None:
    """Get a single node by ID."""
    graph = _load_graph()
    return graph["nodes"].get(node_id)


def find_related(node_id: str, edge_type: EdgeType | None = None) -> list[dict]:
    """Find all nodes connected to node_id, optionally filtered by edge type."""
    graph = _load_graph()
    related = []
    for edge in graph["edges"]:
        if edge["from"] == node_id and (edge_type is None or edge["type"] == edge_type):
            related.append({
                "edge": edge,
                "node": graph["nodes"].get(edge["to"])
            })
        elif edge["to"] == node_id and (edge_type is None or edge["type"] == edge_type):
            related.append({
                "edge": edge,
                "node": graph["nodes"].get(edge["from"])
            })
    return related


def get_neighborhood(node_id: str, depth: int = 2) -> dict:
    """Get all nodes within N hops of node_id, with edges between them."""
    graph = _load_graph()
    if node_id not in graph["nodes"]:
        return {"nodes": {}, "edges": []}

    visited_ids = {node_id}
    frontier = {node_id}
    for _ in range(depth):
        next_frontier = set()
        for edge in graph["edges"]:
            if edge["from"] in frontier:
                next_frontier.add(edge["to"])
            if edge["to"] in frontier:
                next_frontier.add(edge["from"])
        visited_ids |= next_frontier
        frontier = next_frontier - visited_ids

    subgraph_nodes = {nid: graph["nodes"][nid] for nid in visited_ids if nid in graph["nodes"]}
    subgraph_edges = [
        e for e in graph["edges"]
        if e["from"] in visited_ids and e["to"] in visited_ids
    ]
    return {"nodes": subgraph_nodes, "edges": subgraph_edges}


def all_nodes(node_type: NodeType | None = None) -> list[dict]:
    """List all nodes, optionally filtered by type."""
    graph = _load_graph()
    nodes = list(graph["nodes"].values())
    if node_type:
        nodes = [n for n in nodes if n["type"] == node_type]
    return nodes


def remove_node(node_id: str) -> bool:
    """Remove a node and all its edges."""
    graph = _load_graph()
    if node_id not in graph["nodes"]:
        return False
    del graph["nodes"][node_id]
    graph["edges"] = [
        e for e in graph["edges"] if e["from"] != node_id and e["to"] != node_id
    ]
    _save_graph(graph)
    return True
