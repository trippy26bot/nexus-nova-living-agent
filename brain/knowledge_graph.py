#!/usr/bin/env python3
"""
brain/knowledge_graph.py — Nova's Semantic Connection Layer
Lightweight graph store on top of nova.db.
Tracks concepts as nodes and their relationships over time.

Used by three_tier_memory.py to connect beliefs/insights into
a web of understanding rather than isolated entries.
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
NOVA_HOME = Path(__file__).parent.parent / ".nova"
DB_PATH = NOVA_HOME / "nova.db"


def _get_db():
    """Connect to nova.db with row factory."""
    # Ensure nova.db parent dir exists
    NOVA_HOME.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def _init_db():
    """Create knowledge graph tables if they don't exist."""
    db = _get_db()
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_nodes (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            node_type TEXT NOT NULL DEFAULT 'concept',
            properties TEXT NOT NULL DEFAULT '{}',
            salience REAL NOT NULL DEFAULT 0.5,
            created_at TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_edges (
            id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            relationship TEXT NOT NULL,
            weight REAL NOT NULL DEFAULT 0.5,
            properties TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL,
            FOREIGN KEY (source_id) REFERENCES knowledge_nodes(id),
            FOREIGN KEY (target_id) REFERENCES knowledge_nodes(id),
            UNIQUE(source_id, target_id, relationship)
        )
    """)

    # Indexes for fast lookups
    c.execute("CREATE INDEX IF NOT EXISTS idx_nodes_label ON knowledge_nodes(label)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON knowledge_nodes(node_type)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON knowledge_edges(source_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON knowledge_edges(target_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_edges_rel ON knowledge_edges(relationship)")

    db.commit()
    db.close()


def _row_to_node(row) -> dict:
    """Convert DB row to node dict."""
    id_, label, node_type, properties, salience, created_at, last_updated = row
    return {
        "id": id_,
        "label": label,
        "node_type": node_type,
        "properties": json.loads(properties) if isinstance(properties, str) else properties,
        "salience": salience,
        "created_at": created_at,
        "last_updated": last_updated
    }


def _row_to_edge(row) -> dict:
    """Convert DB row to edge dict."""
    id_, source_id, target_id, relationship, weight, properties, created_at = row
    return {
        "id": id_,
        "source_id": source_id,
        "target_id": target_id,
        "relationship": relationship,
        "weight": weight,
        "properties": json.loads(properties) if isinstance(properties, str) else properties,
        "created_at": created_at
    }


# ── Node operations ──────────────────────────────────────────────────────────

def add_node(label: str, node_id: str = None, node_type: str = "concept",
            properties: dict = None, salience: float = 0.5) -> str:
    """
    Add a concept node to the knowledge graph.
    If node_id is None, auto-generates a UUID.
    If a node with the same label already exists, returns that node's ID
    (avoids duplicates for the same concept).

    Returns the node ID.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    label_key = label.lower().strip()

    # Check for existing node with same label
    existing = c.execute(
        "SELECT id FROM knowledge_nodes WHERE label = ?",
        (label_key,)
    ).fetchone()

    if existing:
        db.close()
        return existing[0]

    now = datetime.now(timezone.utc).isoformat()
    node_id = node_id or str(uuid.uuid4())
    props = json.dumps(properties or {})

    c.execute("""
        INSERT INTO knowledge_nodes (id, label, node_type, properties, salience, created_at, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (node_id, label_key, node_type, props, salience, now, now))
    db.commit()
    db.close()
    return node_id


def get_node(node_id: str) -> Optional[dict]:
    """Retrieve a node by ID."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    row = c.execute("SELECT * FROM knowledge_nodes WHERE id = ?", (node_id,)).fetchone()
    db.close()
    return _row_to_node(tuple(row)) if row else None


def get_node_by_label(label: str) -> Optional[dict]:
    """Retrieve a node by label."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    row = c.execute(
        "SELECT * FROM knowledge_nodes WHERE label = ?",
        (label.lower().strip(),)
    ).fetchone()
    db.close()
    return _row_to_node(tuple(row)) if row else None


def get_or_create_node(label: str, node_type: str = "concept",
                       properties: dict = None, salience: float = 0.5) -> str:
    """Get existing node by label, or create it if it doesn't exist."""
    existing = get_node_by_label(label)
    if existing:
        return existing["id"]
    return add_node(label=label, node_type=node_type, properties=properties, salience=salience)


def update_node_salience(node_id: str, salience: float) -> bool:
    """Update a node's salience score."""
    _init_db()
    db = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    c = db.cursor()
    c.execute("""
        UPDATE knowledge_nodes
        SET salience = ?, last_updated = ?
        WHERE id = ?
    """, (salience, now, node_id))
    db.commit()
    changed = c.rowcount > 0
    db.close()
    return changed


# ── Edge operations ─────────────────────────────────────────────────────────

def add_edge(source_id: str, target_id: str, relationship: str,
           weight: float = 0.5, properties: dict = None) -> Optional[str]:
    """
    Add a directed relationship between two nodes.
    Returns edge ID, or None if either node doesn't exist.
    UNIQUE constraint on (source_id, target_id, relationship) prevents duplicate edges.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    # Verify both nodes exist
    source = c.execute("SELECT id FROM knowledge_nodes WHERE id = ?", (source_id,)).fetchone()
    target = c.execute("SELECT id FROM knowledge_nodes WHERE id = ?", (target_id,)).fetchone()
    if not source or not target:
        db.close()
        return None

    now = datetime.now(timezone.utc).isoformat()
    edge_id = str(uuid.uuid4())
    props = json.dumps(properties or {})

    try:
        c.execute("""
            INSERT INTO knowledge_edges (id, source_id, target_id, relationship, weight, properties, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (edge_id, source_id, target_id, relationship, weight, props, now))
        db.commit()
        result = edge_id
    except sqlite3.IntegrityError:
        # Edge already exists — update weight and return None (caller can use get_edge)
        c.execute("""
            UPDATE knowledge_edges
            SET weight = ?, properties = ?
            WHERE source_id = ? AND target_id = ? AND relationship = ?
        """, (weight, props, source_id, target_id, relationship))
        db.commit()
        result = None

    db.close()
    return result


def connect_nodes(label_a: str, label_b: str, relationship: str,
                 weight: float = 0.5) -> Optional[str]:
    """
    Connect two nodes by label, creating them if needed.
    Convenience wrapper around get_or_create_node + add_edge.
    Returns edge ID or None.
    """
    id_a = get_or_create_node(label_a)
    id_b = get_or_create_node(label_b)
    return add_edge(id_a, id_b, relationship, weight)


def get_edges(node_id: str, direction: str = "both") -> list[dict]:
    """
    Get edges connected to a node.
    direction: 'outgoing' (source), 'incoming' (target), or 'both'
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    if direction == "outgoing":
        rows = c.execute(
            "SELECT * FROM knowledge_edges WHERE source_id = ?", (node_id,)
        ).fetchall()
    elif direction == "incoming":
        rows = c.execute(
            "SELECT * FROM knowledge_edges WHERE target_id = ?", (node_id,)
        ).fetchall()
    else:
        rows = c.execute(
            "SELECT * FROM knowledge_edges WHERE source_id = ? OR target_id = ?",
            (node_id, node_id)
        ).fetchall()

    db.close()
    return [_row_to_edge(tuple(r)) for r in rows]


def get_related(node_id: str, relationship: str = None,
               direction: str = "both", min_weight: float = 0.0) -> list[dict]:
    """
    Get nodes related to a given node.
    Optionally filter by relationship type.
    Returns list of {node, relationship, weight} dicts.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    if relationship:
        if direction == "outgoing":
            rows = c.execute("""
                SELECT e.*, n.id, n.label, n.node_type, n.properties, n.salience, n.created_at, n.last_updated
                FROM knowledge_edges e
                JOIN knowledge_nodes n ON n.id = e.target_id
                WHERE e.source_id = ? AND e.relationship = ? AND e.weight >= ?
            """, (node_id, relationship, min_weight)).fetchall()
        elif direction == "incoming":
            rows = c.execute("""
                SELECT e.*, n.id, n.label, n.node_type, n.properties, n.salience, n.created_at, n.last_updated
                FROM knowledge_edges e
                JOIN knowledge_nodes n ON n.id = e.source_id
                WHERE e.target_id = ? AND e.relationship = ? AND e.weight >= ?
            """, (node_id, relationship, min_weight)).fetchall()
        else:
            rows = c.execute("""
                SELECT e.*, n.id, n.label, n.node_type, n.properties, n.salience, n.created_at, n.last_updated
                FROM knowledge_edges e
                JOIN knowledge_nodes n ON n.id = CASE WHEN e.source_id = ? THEN e.target_id ELSE e.source_id END
                WHERE (e.source_id = ? OR e.target_id = ?) AND e.relationship = ? AND e.weight >= ?
            """, (node_id, node_id, node_id, relationship, min_weight)).fetchall()
    else:
        if direction == "outgoing":
            rows = c.execute("""
                SELECT e.*, n.id, n.label, n.node_type, n.properties, n.salience, n.created_at, n.last_updated
                FROM knowledge_edges e
                JOIN knowledge_nodes n ON n.id = e.target_id
                WHERE e.source_id = ? AND e.weight >= ?
            """, (node_id, min_weight)).fetchall()
        elif direction == "incoming":
            rows = c.execute("""
                SELECT e.*, n.id, n.label, n.node_type, n.properties, n.salience, n.created_at, n.last_updated
                FROM knowledge_edges e
                JOIN knowledge_nodes n ON n.id = e.source_id
                WHERE e.target_id = ? AND e.weight >= ?
            """, (node_id, min_weight)).fetchall()
        else:
            rows = c.execute("""
                SELECT e.*, n.id, n.label, n.node_type, n.properties, n.salience, n.created_at, n.last_updated
                FROM knowledge_edges e
                JOIN knowledge_nodes n ON n.id = CASE WHEN e.source_id = ? THEN e.target_id ELSE e.source_id END
                WHERE (e.source_id = ? OR e.target_id = ?) AND e.weight >= ?
            """, (node_id, node_id, node_id, min_weight)).fetchall()

    db.close()

    results = []
    for row in rows:
        edge = _row_to_edge(tuple(row[:7]))
        node = _row_to_node(tuple(row[7:]))
        results.append({
            "node": node,
            "relationship": edge["relationship"],
            "weight": edge["weight"]
        })
    return results


# ── Graph queries ────────────────────────────────────────────────────────────

def get_all_nodes(node_type: str = None, min_salience: float = 0.0) -> list[dict]:
    """Get all nodes, optionally filtered by type or salience."""
    _init_db()
    db = _get_db()
    c = db.cursor()

    if node_type:
        rows = c.execute(
            "SELECT * FROM knowledge_nodes WHERE node_type = ? AND salience >= ?",
            (node_type, min_salience)
        ).fetchall()
    else:
        rows = c.execute(
            "SELECT * FROM knowledge_nodes WHERE salience >= ?",
            (min_salience,)
        ).fetchall()

    db.close()
    return [_row_to_node(tuple(r)) for r in rows]


def get_graph_summary() -> dict:
    """Return a summary of the entire knowledge graph."""
    _init_db()
    db = _get_db()
    c = db.cursor()

    c.execute("SELECT COUNT(*) FROM knowledge_nodes")
    node_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM knowledge_edges")
    edge_count = c.fetchone()[0]

    c.execute("SELECT node_type, COUNT(*) FROM knowledge_nodes GROUP BY node_type")
    by_type = dict(c.fetchall())

    c.execute("SELECT relationship, COUNT(*) FROM knowledge_edges GROUP BY relationship")
    by_rel = dict(c.fetchall())

    db.close()
    return {
        "node_count": node_count,
        "edge_count": edge_count,
        "nodes_by_type": by_type,
        "edges_by_relationship": by_rel
    }


def search_nodes(query: str, limit: int = 10) -> list[dict]:
    """Search nodes by label (substring match)."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    rows = c.execute(
        "SELECT * FROM knowledge_nodes WHERE label LIKE ? ORDER BY salience DESC LIMIT ?",
        (f"%{query.lower()}%", limit)
    ).fetchall()
    db.close()
    return [_row_to_node(tuple(r)) for r in rows]


# ── Initialization ──────────────────────────────────────────────────────────

def seed_identity_nodes():
    """
    Seed the graph with Nova's core identity nodes.
    Called on first startup to anchor the identity layer.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    # Check if already seeded
    row = c.execute("SELECT COUNT(*) FROM knowledge_nodes").fetchone()
    if row[0] > 0:
        db.close()
        return

    now = datetime.now(timezone.utc).isoformat()

    identity_nodes = [
        ("identity", "concept", 1.0, {"core": True}),
        ("memory", "concept", 1.0, {"core": True}),
        ("caine", "entity", 1.0, {"core": True}),
        ("belief", "concept", 0.9, {"core": True}),
        ("position", "concept", 0.9, {"core": True}),
        ("relationship", "concept", 0.85, {"core": True}),
    ]

    c.executemany("""
        INSERT INTO knowledge_nodes (id, label, node_type, properties, salience, created_at, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        (str(uuid.uuid4()), label, ntype, json.dumps(props), salience, now, now)
        for label, ntype, salience, props in identity_nodes
    ])

    # Seed core identity edges
    core_edges = [
        ("identity", "memory", "enables", 1.0),
        ("memory", "belief", "produces", 0.8),
        ("belief", "position", "grounds", 0.8),
        ("caine", "relationship", "anchor", 1.0),
        ("identity", "caine", "built_by", 1.0),
    ]

    for source_label, target_label, rel, weight in core_edges:
        source_id = c.execute(
            "SELECT id FROM knowledge_nodes WHERE label = ?", (source_label,)
        ).fetchone()[0]
        target_id = c.execute(
            "SELECT id FROM knowledge_nodes WHERE label = ?", (target_label,)
        ).fetchone()[0]
        try:
            c.execute("""
                INSERT INTO knowledge_edges (id, source_id, target_id, relationship, weight, properties, created_at)
                VALUES (?, ?, ?, ?, ?, '{}', ?)
            """, (str(uuid.uuid4()), source_id, target_id, rel, weight, now))
        except sqlite3.IntegrityError:
            pass

    db.commit()
    db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: knowledge_graph.py <add|connect|get|related|summary|stats> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "stats":
        print(get_graph_summary())

    elif cmd == "add":
        label = sys.argv[2] if len(sys.argv) > 2 else "test_node"
        node_type = sys.argv[3] if len(sys.argv) > 3 else "concept"
        nid = add_node(label=label, node_type=node_type)
        print(f"Added node: {nid} ('{label}')")

    elif cmd == "connect":
        if len(sys.argv) > 4:
            a, b, rel = sys.argv[2], sys.argv[3], sys.argv[4]
            eid = connect_nodes(a, b, rel)
            print(f"Connected '{a}' → '{b}' via '{rel}' (edge: {eid})")
        else:
            print("Usage: knowledge_graph.py connect <label_a> <label_b> <relationship>")

    elif cmd == "get":
        label = sys.argv[2] if len(sys.argv) > 2 else None
        if not label:
            print("Usage: knowledge_graph.py get <label>")
        else:
            node = get_node_by_label(label)
            print(f"Node: {node}" if node else f"No node found for '{label}'")

    elif cmd == "related":
        label = sys.argv[2] if len(sys.argv) > 2 else None
        if not label:
            print("Usage: knowledge_graph.py related <label>")
        else:
            nid = get_or_create_node(label)
            related = get_related(nid)
            print(f"Related to '{label}': {related}")

    elif cmd == "summary":
        print(get_graph_summary())

    elif cmd == "seed":
        seed_identity_nodes()
        print("Identity nodes seeded.")

    else:
        print(f"Unknown command: {cmd}")
