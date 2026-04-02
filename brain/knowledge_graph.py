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
            last_updated TEXT NOT NULL,
            belief_updated_at TEXT NOT NULL DEFAULT '1970-01-01T00:00:00+00:00'
        )
    """)

    # Temporal history — logs previous salience/position values on change
    c.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_node_history (
            id TEXT PRIMARY KEY,
            node_id TEXT NOT NULL,
            field TEXT NOT NULL,
            previous_value REAL,
            previous_text TEXT,
            previous_timestamp TEXT NOT NULL,
            change_reason TEXT,
            changed_at TEXT NOT NULL,
            FOREIGN KEY (node_id) REFERENCES knowledge_nodes(id)
        )
    """)

    # Council dynamics memory — records each council vote as a node
    c.execute("""
        CREATE TABLE IF NOT EXISTS council_votes (
            id TEXT PRIMARY KEY,
            node_id TEXT NOT NULL,
            decision_context TEXT NOT NULL,
            votes TEXT NOT NULL DEFAULT '[]',
            outcome TEXT,
            confidence_spread REAL NOT NULL DEFAULT 0.0,
            dissent_count INTEGER NOT NULL DEFAULT 0,
            is_divergence_point INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (node_id) REFERENCES knowledge_nodes(id)
        )
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_council_node ON council_votes(node_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_council_created ON council_votes(created_at)")

    # Belief Gravity Field — belief nodes with mass and reinforcement tracking
    c.execute("""
        CREATE TABLE IF NOT EXISTS belief_nodes (
            id TEXT PRIMARY KEY,
            label TEXT NOT NULL,
            belief_text TEXT NOT NULL,
            mass REAL NOT NULL DEFAULT 0.5,
            reinforcement_count INTEGER NOT NULL DEFAULT 0,
            contradiction_count INTEGER NOT NULL DEFAULT 0,
            stage TEXT NOT NULL DEFAULT 'raw',
            lineage_depth INTEGER NOT NULL DEFAULT 0,
            trace_status TEXT NOT NULL DEFAULT 'untraced',
            origin_memory_ids TEXT NOT NULL DEFAULT '[]',
            timestamp_created TEXT NOT NULL,
            timestamp_last_reinforced TEXT NOT NULL,
            properties TEXT NOT NULL DEFAULT '{}'
        )
    """)

    # Tension nodes — crystallized contradictions
    c.execute("""
        CREATE TABLE IF NOT EXISTS tension_nodes (
            id TEXT PRIMARY KEY,
            pole_a_id TEXT NOT NULL,
            pole_b_id TEXT NOT NULL,
            tension_strength REAL NOT NULL DEFAULT 0.5,
            resolution_status TEXT NOT NULL DEFAULT 'crystallized',
            generative_outputs TEXT NOT NULL DEFAULT '[]',
            timestamp_created TEXT NOT NULL,
            timestamp_last_active TEXT NOT NULL,
            properties TEXT NOT NULL DEFAULT '{}',
            FOREIGN KEY (pole_a_id) REFERENCES belief_nodes(id),
            FOREIGN KEY (pole_b_id) REFERENCES belief_nodes(id)
        )
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_belief_stage ON belief_nodes(stage)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_belief_mass ON belief_nodes(mass)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_tension_strength ON tension_nodes(tension_strength)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_tension_status ON tension_nodes(resolution_status)")

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
    c.execute("CREATE INDEX IF NOT EXISTS idx_history_node ON knowledge_node_history(node_id)")

    db.commit()
    db.close()


def _row_to_node(row) -> dict:
    """Convert DB row to node dict."""
    id_, label, node_type, properties, salience, created_at, last_updated, belief_updated_at = row
    return {
        "id": id_,
        "label": label,
        "node_type": node_type,
        "properties": json.loads(properties) if isinstance(properties, str) else properties,
        "salience": salience,
        "created_at": created_at,
        "last_updated": last_updated,
        "belief_updated_at": belief_updated_at
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
        INSERT INTO knowledge_nodes (id, label, node_type, properties, salience, created_at, last_updated, belief_updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (node_id, label_key, node_type, props, salience, now, now, now))
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


def update_node_salience(node_id: str, salience: float, reason: str = None) -> bool:
    """
    Update a node's salience score.
    Logs the previous value to knowledge_node_history before changing.
    """
    _init_db()
    db = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    c = db.cursor()

    # Fetch previous value before updating
    prev_row = c.execute(
        "SELECT salience, belief_updated_at FROM knowledge_nodes WHERE id = ?", (node_id,)
    ).fetchone()
    if not prev_row:
        db.close()
        return False

    prev_salience, prev_timestamp = prev_row

    # Log history
    history_id = str(uuid.uuid4())
    c.execute("""
        INSERT INTO knowledge_node_history (id, node_id, field, previous_value, previous_timestamp, change_reason, changed_at)
        VALUES (?, ?, 'salience', ?, ?, ?, ?)
    """, (history_id, node_id, prev_salience, prev_timestamp, reason or "salience_update", now))

    # Update salience and set belief_updated_at to now if salience changed meaningfully
    c.execute("""
        UPDATE knowledge_nodes
        SET salience = ?, last_updated = ?, belief_updated_at = ?
        WHERE id = ?
    """, (salience, now, now, node_id))
    db.commit()
    changed = c.rowcount > 0
    db.close()
    return changed


def update_node_position(node_id: str, position_value: float, reason: str = None) -> bool:
    """
    Record a position update for a node (e.g. belief strength, conviction level).
    Logs the previous value to knowledge_node_history before changing.
    Sets belief_updated_at to now.
    """
    _init_db()
    db = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    c = db.cursor()

    prev_row = c.execute(
        "SELECT salience, belief_updated_at FROM knowledge_nodes WHERE id = ?", (node_id,)
    ).fetchone()
    if not prev_row:
        db.close()
        return False

    prev_salience, prev_timestamp = prev_row

    history_id = str(uuid.uuid4())
    c.execute("""
        INSERT INTO knowledge_node_history (id, node_id, field, previous_value, previous_timestamp, change_reason, changed_at)
        VALUES (?, ?, 'position', ?, ?, ?, ?)
    """, (history_id, node_id, prev_salience, prev_timestamp, reason or "position_update", now))

    c.execute("""
        UPDATE knowledge_nodes
        SET salience = ?, last_updated = ?, belief_updated_at = ?
        WHERE id = ?
    """, (position_value, now, now, node_id))
    db.commit()
    changed = c.rowcount > 0
    db.close()
    return changed


def get_node_history(node_id: str) -> list[dict]:
    """Return the temporal change log for a node."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    rows = c.execute("""
        SELECT * FROM knowledge_node_history
        WHERE node_id = ?
        ORDER BY changed_at DESC
    """, (node_id,)).fetchall()
    db.close()
    return [{"id": r[0], "node_id": r[1], "field": r[2], "previous_value": r[3],
             "previous_text": r[4], "previous_timestamp": r[5], "change_reason": r[6],
             "changed_at": r[7]} for r in rows]


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
        INSERT INTO knowledge_nodes (id, label, node_type, properties, salience, created_at, last_updated, belief_updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (str(uuid.uuid4()), label, ntype, json.dumps(props), salience, now, now, now)
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


# ── Council Dynamics Memory ───────────────────────────────────────────────────

def write_council_vote(decision_context: str, votes: list, outcome: str = None,
                       is_divergence_point: bool = False) -> str:
    """
    Record a council decision as a council_vote node.
    Returns the council vote ID.

    votes: list of dicts with keys: specialist, position, confidence, dissent
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    now = datetime.now(timezone.utc).isoformat()
    vote_id = str(uuid.uuid4())

    # Compute derived fields
    confidences = [v.get("confidence", 0.0) for v in votes]
    confidence_spread = max(confidences) - min(confidences) if confidences else 0.0
    dissent_count = sum(1 for v in votes if v.get("dissent", False))

    # Create a placeholder node for the council vote
    node_id = str(uuid.uuid4())
    label = f"council_vote:{now[:16]}"

    c.execute("""
        INSERT INTO knowledge_nodes (id, label, node_type, properties, salience, created_at, last_updated, belief_updated_at)
        VALUES (?, ?, 'council_vote', '{}', 0.6, ?, ?, ?)
    """, (node_id, label, now, now, now))

    c.execute("""
        INSERT INTO council_votes (id, node_id, decision_context, votes, outcome, confidence_spread, dissent_count, is_divergence_point, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        vote_id, node_id, decision_context,
        json.dumps(votes), outcome or "",
        confidence_spread, dissent_count,
        1 if is_divergence_point else 0,
        now
    ))

    db.commit()
    db.close()
    return vote_id


def get_council_vote(vote_id: str) -> Optional[dict]:
    """Retrieve a single council vote by ID."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    row = c.execute("SELECT * FROM council_votes WHERE id = ?", (vote_id,)).fetchone()
    db.close()
    if not row:
        return None
    return {
        "id": row[0], "node_id": row[1], "decision_context": row[2],
        "votes": json.loads(row[3]), "outcome": row[4],
        "confidence_spread": row[5], "dissent_count": row[6],
        "is_divergence_point": bool(row[7]), "created_at": row[8]
    }


def get_recent_council_votes(limit: int = 20) -> list:
    """Return recent council votes, newest first."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    rows = c.execute("""
        SELECT * FROM council_votes
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    db.close()
    return [
        {"id": r[0], "node_id": r[1], "decision_context": r[2],
         "votes": json.loads(r[3]), "outcome": r[4],
         "confidence_spread": r[5], "dissent_count": r[6],
         "is_divergence_point": bool(r[7]), "created_at": r[8]}
        for r in rows
    ]


def get_divergence_points(limit: int = 10) -> list:
    """Return recent votes flagged as significant divergence points (spread > 0.4)."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    rows = c.execute("""
        SELECT * FROM council_votes
        WHERE is_divergence_point = 1 OR confidence_spread > 0.4
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    db.close()
    return [
        {"id": r[0], "node_id": r[1], "decision_context": r[2],
         "votes": json.loads(r[3]), "outcome": r[4],
         "confidence_spread": r[5], "dissent_count": r[6],
         "is_divergence_point": bool(r[7]), "created_at": r[8]}
        for r in rows
    ]


# ── Belief Gravity ─────────────────────────────────────────────────────────────

def _row_to_belief(row) -> dict:
    """Convert DB row to belief dict."""
    return {
        "id": row[0],
        "label": row[1],
        "belief_text": row[2],
        "mass": row[3],
        "reinforcement_count": row[4],
        "contradiction_count": row[5],
        "stage": row[6],
        "lineage_depth": row[7],
        "trace_status": row[8],
        "origin_memory_ids": json.loads(row[9]) if isinstance(row[9], str) else row[9],
        "timestamp_created": row[10],
        "timestamp_last_reinforced": row[11],
        "properties": json.loads(row[12]) if isinstance(row[12], str) else row[12]
    }


def create_belief_node(belief: str, origin_memory_ids: list,
                       trace_status: str = "partial") -> str:
    """
    Write a new belief_node to the knowledge graph.

    Stage starts at 'raw', mass at 0.5.
    trace_status: 'untraced' | 'partial' | 'complete'
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    now = datetime.now(timezone.utc).isoformat()
    belief_id = str(uuid.uuid4())

    c.execute("""
        INSERT INTO belief_nodes
        (id, label, belief_text, mass, reinforcement_count, contradiction_count,
         stage, lineage_depth, trace_status, origin_memory_ids,
         timestamp_created, timestamp_last_reinforced, properties)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        belief_id,
        belief[:60].lower(),          # label truncated
        belief,
        0.5,                           # mass
        0,                             # reinforcement_count
        0,                             # contradiction_count
        "raw",                         # stage
        0,                             # lineage_depth
        trace_status,
        json.dumps(origin_memory_ids),
        now,
        now,
        "{}"                           # properties
    ))

    db.commit()
    db.close()
    return belief_id


def get_belief(belief_id: str) -> Optional[dict]:
    """Retrieve a belief node by ID."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    row = c.execute(
        "SELECT * FROM belief_nodes WHERE id = ?", (belief_id,)
    ).fetchone()
    db.close()
    return _row_to_belief(tuple(row)) if row else None


def get_active_beliefs(min_mass: float = 0.1) -> list:
    """Load all beliefs with mass above threshold."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    rows = c.execute(
        "SELECT * FROM belief_nodes WHERE mass >= ? ORDER BY mass DESC",
        (min_mass,)
    ).fetchall()
    db.close()
    return [_row_to_belief(tuple(r)) for r in rows]


def reinforce_belief(belief_id: str, source_memory_id: str):
    """
    Reinforce a belief — increases mass, updates timestamp.
    Mass caps at 1.0.
    """
    _init_db()
    db = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    c = db.cursor()

    c.execute("""
        UPDATE belief_nodes
        SET mass = MIN(1.0, mass + 0.05),
            reinforcement_count = reinforcement_count + 1,
            timestamp_last_reinforced = ?
        WHERE id = ?
    """, (now, belief_id))

    db.commit()
    db.close()


def contradict_belief(belief_id: str, source_memory_id: str):
    """
    Contradict a belief — reduces mass faster than reinforcement builds it.
    Mass floors at 0.1 (never fully disappears).
    """
    _init_db()
    db = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    c = db.cursor()

    c.execute("""
        UPDATE belief_nodes
        SET mass = MAX(0.1, mass - 0.08),
            contradiction_count = contradiction_count + 1
        WHERE id = ?
    """, (belief_id,))

    db.commit()
    db.close()


def apply_belief_gravity(options: list) -> list:
    """
    Re-rank a list of options using active beliefs as gravity wells.

    Each option should be a dict with:
      - label: short string name
      - text: the content/description
      - base_score: pre-gravity score (optional, defaults to 0.5)

    Returns options with:
      - score: re-ranked after belief gravity
      - gravity_trace: list of {belief, proximity, mass_boost} dicts

    Pulls constraint field values from constraint_fields.py to apply
    belief-aligned multipliers.
    """
    try:
        from brain.constraint_fields import get_fields
        fields = get_fields()
    except ImportError:
        fields = {"truth_gravity": 0.9}

    active_beliefs = get_active_beliefs(min_mass=0.2)

    # truth_gravity multiplier: beliefs aligned with high truth_gravity get stronger pull
    truth_multiplier = fields.get("truth_gravity", 0.9)

    results = []
    for option in options:
        base_score = option.get("base_score", 0.5)
        text = option.get("text", option.get("label", "")).lower()
        gravity_trace = []
        total_boost = 0.0

        for belief in active_beliefs:
            belief_text = belief["belief_text"].lower()
            mass = belief["mass"]

            # Compute semantic proximity (simple word overlap for now)
            belief_words = set(belief_text.split())
            option_words = set(text.split())
            overlap = len(belief_words & option_words)
            union = len(belief_words | option_words)
            proximity = overlap / union if union > 0 else 0.0

            # Boost is proportional to mass * proximity
            boost = mass * proximity

            # Apply truth_gravity multiplier to final boost
            boosted = boost * truth_multiplier
            total_boost += boosted

            if proximity > 0.05:  # Only trace meaningful connections
                gravity_trace.append({
                    "belief": belief["belief_text"],
                    "proximity": round(proximity, 4),
                    "mass": mass,
                    "mass_boost": round(boosted, 4)
                })

        final_score = base_score + total_boost
        results.append({
            **option,
            "score": round(final_score, 4),
            "gravity_trace": gravity_trace
        })

    # Re-rank by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def update_belief_stage(belief_id: str, new_stage: str):
    """Advance or update a belief's crystallization stage."""
    _init_db()
    db = _get_db()
    now = datetime.now(timezone.utc).isoformat()
    c = db.cursor()

    c.execute("""
        UPDATE belief_nodes
        SET stage = ?, timestamp_last_reinforced = ?
        WHERE id = ?
    """, (new_stage, now, belief_id))

    db.commit()
    db.close()


def get_beliefs_by_stage(stage: str) -> list:
    """Get all beliefs at a given stage."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    rows = c.execute(
        "SELECT * FROM belief_nodes WHERE stage = ? ORDER BY mass DESC",
        (stage,)
    ).fetchall()
    db.close()
    return [_row_to_belief(tuple(r)) for r in rows]


def get_belief_erosion_candidates(threshold: float = 0.6) -> list:
    """
    Flag beliefs where contradiction_count > reinforcement_count * threshold.
    These are beliefs losing the tug-of-war.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    rows = c.execute("""
        SELECT * FROM belief_nodes
        WHERE contradiction_count > reinforcement_count * ?
        AND mass > 0.1
        ORDER BY (contradiction_count - reinforcement_count) DESC
    """, (threshold,)).fetchall()
    db.close()
    return [_row_to_belief(tuple(r)) for r in rows]


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
