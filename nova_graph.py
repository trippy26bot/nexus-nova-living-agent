#!/usr/bin/env python3
"""
NOVA GRAPH — Knowledge Graph Memory
Relational memory with path-finding and context building.

Stores entities and their relationships for richer context.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
from collections import defaultdict

# Configuration
NOVA_DIR = Path.home() / ".nova"
GRAPH_DB = NOVA_DIR / "knowledge_graph.db"


class KnowledgeGraph:
    """Knowledge graph for relational memory."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or GRAPH_DB
        self.init_db()
    
    def init_db(self):
        """Initialize graph database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Entities table
        c.execute('''CREATE TABLE IF NOT EXISTS entities
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT UNIQUE NOT NULL,
                      entity_type TEXT,
                      properties TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Relationships table
        c.execute('''CREATE TABLE IF NOT EXISTS relationships
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      from_entity INTEGER,
                      to_entity INTEGER,
                      relationship_type TEXT,
                      properties TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (from_entity) REFERENCES entities(id),
                      FOREIGN KEY (to_entity) REFERENCES entities(id))''')
        
        conn.commit()
        conn.close()
    
    def add_entity(self, name: str, entity_type: str = None, properties: Dict = None) -> int:
        """Add an entity to the graph."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        props_json = json.dumps(properties or {})
        
        c.execute(
            "INSERT OR IGNORE INTO entities (name, entity_type, properties) VALUES (?, ?, ?)",
            (name, entity_type, props_json)
        )
        
        c.execute("SELECT id FROM entities WHERE name = ?", (name,))
        entity_id = c.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        return entity_id
    
    def add_relationship(self, from_name: str, to_name: str, rel_type: str, properties: Dict = None):
        """Add a relationship between entities."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Ensure entities exist
        from_id = self.add_entity(from_name)
        to_id = self.add_entity(to_name)
        
        props_json = json.dumps(properties or {})
        
        c.execute(
            "INSERT INTO relationships (from_entity, to_entity, relationship_type, properties) VALUES (?, ?, ?, ?)",
            (from_id, to_id, rel_type, props_json)
        )
        
        conn.commit()
        conn.close()
    
    def get_entity(self, name: str) -> Optional[Dict]:
        """Get an entity and its relationships."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get entity
        c.execute("SELECT id, name, entity_type, properties FROM entities WHERE name = ?", (name,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return None
        
        entity = {
            'id': row[0],
            'name': row[1],
            'type': row[2],
            'properties': json.loads(row[3] or '{}'),
            'relationships': []
        }
        
        # Get outgoing relationships
        c.execute(
            """SELECT r.relationship_type, e.name, e.entity_type, r.properties
               FROM relationships r
               JOIN entities e ON r.to_entity = e.id
               WHERE r.from_entity = ?""",
            (entity['id'],)
        )
        
        for rel in c.fetchall():
            entity['relationships'].append({
                'type': rel[0],
                'to': rel[1],
                'to_type': rel[2],
                'properties': json.loads(rel[3] or '{}')
            })
        
        conn.close()
        
        return entity
    
    def find_path(self, start: str, end: str, max_depth: int = 3) -> List[List[str]]:
        """Find paths between two entities."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # BFS to find paths
        from collections import deque
        
        queue = deque([(start, [start])])
        visited = {start}
        paths = []
        
        while queue:
            current, path = queue.popleft()
            
            if len(path) > max_depth:
                continue
            
            if current == end:
                paths.append(path)
                continue
            
            # Get neighbors
            c.execute(
                """SELECT e.name FROM relationships r
                   JOIN entities e ON r.to_entity = e.id
                   WHERE r.from_entity = (SELECT id FROM entities WHERE name = ?)""",
                (current,)
            )
            
            for (neighbor,) in c.fetchall():
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        conn.close()
        
        return paths
    
    def get_related(self, name: str, rel_type: str = None) -> List[Dict]:
        """Get all related entities."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT id FROM entities WHERE name = ?", (name,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return []
        
        entity_id = row[0]
        
        if rel_type:
            c.execute(
                """SELECT e.name, e.entity_type, r.relationship_type, r.properties
                   FROM relationships r
                   JOIN entities e ON r.to_entity = e.id
                   WHERE r.from_entity = ? AND r.relationship_type = ?""",
                (entity_id, rel_type)
            )
        else:
            c.execute(
                """SELECT e.name, e.entity_type, r.relationship_type, r.properties
                   FROM relationships r
                   JOIN entities e ON r.to_entity = e.id
                   WHERE r.from_entity = ?""",
                (entity_id,)
            )
        
        results = []
        for row in c.fetchall():
            results.append({
                'name': row[0],
                'type': row[1],
                'relationship': row[2],
                'properties': json.loads(row[3] or '{}')
            })
        
        conn.close()
        
        return results
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search entities by name or type."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "SELECT name, entity_type, properties FROM entities WHERE name LIKE ? OR entity_type LIKE ? LIMIT ?",
            (f"%{query}%", f"%{query}%", limit)
        )
        
        results = []
        for row in c.fetchall():
            results.append({
                'name': row[0],
                'type': row[1],
                'properties': json.loads(row[2] or '{}')
            })
        
        conn.close()
        
        return results
    
    def get_stats(self) -> Dict:
        """Get graph statistics."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM entities")
        entity_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM relationships")
        rel_count = c.fetchone()[0]
        
        c.execute("SELECT relationship_type, COUNT(*) FROM relationships GROUP BY relationship_type")
        rel_types = dict(c.fetchall())
        
        conn.close()
        
        return {
            'entities': entity_count,
            'relationships': rel_count,
            'relationship_types': rel_types
        }
    
    def build_context(self, topic: str, depth: int = 2) -> str:
        """Build a context string from the graph around a topic."""
        
        context_parts = [f"Context about: {topic}"]
        
        # Get main entity
        entity = self.get_entity(topic)
        
        if entity:
            context_parts.append(f"\n## {entity['name']} ({entity['type']})")
            
            if entity['properties']:
                context_parts.append(f"Properties: {json.dumps(entity['properties'])}")
            
            # Get relationships
            if entity['relationships']:
                context_parts.append("\nRelated:")
                for rel in entity['relationships'][:5]:
                    context_parts.append(f"- {rel['type']}: {rel['to']} ({rel['to_type']})")
        
        # Get paths to other relevant entities
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "SELECT name FROM entities WHERE name LIKE ? LIMIT 5",
            (f"%{topic}%",)
        )
        
        for (name,) in c.fetchall():
            if name != topic:
                paths = self.find_path(topic, name, depth)
                if paths:
                    context_parts.append(f"\n## {name}")
                    context_parts.append(f"Path: {' → '.join(paths[0])}")
        
        conn.close()
        
        return "\n".join(context_parts)


# Functions for extracting from text
def extract_entities_from_text(text: str) -> List[Dict]:
    """Extract potential entities from text using simple heuristics."""
    
    import re
    
    entities = []
    
    # Capitalized words (potential proper nouns)
    pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
    matches = re.findall(pattern, text)
    
    for match in matches[:10]:
        entities.append({
            'name': match,
            'type': 'extracted',
            'confidence': 0.5
        })
    
    return entities


def add_text_to_graph(text: str, graph: KnowledgeGraph = None):
    """Parse text and add entities/relationships to graph."""
    
    if graph is None:
        graph = KnowledgeGraph()
    
    entities = extract_entities_from_text(text)
    
    # Add entities
    for entity in entities:
        graph.add_entity(entity['name'], entity['type'])
    
    # Simple relationship inference: consecutive entities
    for i in range(len(entities) - 1):
        graph.add_relationship(
            entities[i]['name'],
            entities[i + 1]['name'],
            'follows_in_text'
        )
    
    return len(entities)


# Singleton
_graph = None

def get_graph() -> KnowledgeGraph:
    """Get the knowledge graph singleton."""
    global _graph
    if _graph is None:
        _graph = KnowledgeGraph()
    return _graph


if __name__ == '__main__':
    graph = KnowledgeGraph()
    print("Knowledge Graph")
    print("=" * 40)
    print(f"Stats: {graph.get_stats()}")
    print("\nUsage:")
    print("  from nova_graph import get_graph")
    print("  graph = get_graph()")
    print("  graph.add_entity('Nova', 'AI')")
    print("  graph.add_relationship('Nova', 'Caine', 'created_by')")
