"""
Knowledge Graph — Relational Memory System

Stores entities and their relationships, enabling complex queries
like "what is Caine building?" or "what tools does Nova have?"

Based on: user → builds → trading_bot
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any


class KnowledgeGraph:
    """
    Relational memory with entities and typed relationships.
    
    Example relationships:
    - (Caine) --builds--> (Nova)
    - (Nova) --uses--> (Simmer)
    - (Caine) --likes--> (dark chocolate)
    - (Nova) --knows--> (Python)
    """
    
    def __init__(self, db_path: str = "~/.nova/knowledge_graph.db"):
        self.db_path = db_path.replace("~", str(__import__("os").path.expanduser("~")))
        self._init_db()
    
    def _init_db(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                entity_type TEXT,
                properties TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_entity TEXT NOT NULL,
                relationship TEXT NOT NULL,
                to_entity TEXT NOT NULL,
                properties TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (from_entity) REFERENCES entities(name),
                FOREIGN KEY (to_entity) REFERENCES entities(name)
            )
        """)
        
        # Index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_relationships 
            ON relationships(from_entity, relationship, to_entity)
        """)
        
        conn.commit()
        conn.close()
    
    def add_entity(self, name: str, entity_type: str = None, 
                   properties: Dict = None) -> int:
        """Add or update an entity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO entities (name, entity_type, properties)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                entity_type = COALESCE(entity_type, entity_type),
                properties = COALESCE(?, properties),
                updated_at = CURRENT_TIMESTAMP
        """, (name, entity_type, json.dumps(properties or {}), 
              json.dumps(properties or {})))
        
        conn.commit()
        conn.close()
        
        return cursor.lastrowid
    
    def add_relationship(self, from_entity: str, relationship: str,
                        to_entity: str, properties: Dict = None) -> int:
        """Add a relationship between entities."""
        # Ensure entities exist
        self.add_entity(from_entity)
        self.add_entity(to_entity)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO relationships 
            (from_entity, relationship, to_entity, properties)
            VALUES (?, ?, ?, ?)
        """, (from_entity, relationship, to_entity, 
              json.dumps(properties or {})))
        
        conn.commit()
        conn.close()
        
        return cursor.lastrowid
    
    def query(self, from_entity: str = None, 
              relationship: str = None,
              to_entity: str = None) -> List[Dict]:
        """
        Query relationships.
        
        Examples:
        - kg.query(from_entity="Caine") → all Caine's relationships
        - kg.query(relationship="builds") → all "builds" relationships
        - kg.query(from_entity="Caine", relationship="builds") → what Caine builds
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM relationships WHERE 1=1"
        params = []
        
        if from_entity:
            query += " AND from_entity = ?"
            params.append(from_entity)
        if relationship:
            query += " AND relationship = ?"
            params.append(relationship)
        if to_entity:
            query += " AND to_entity = ?"
            params.append(to_entity)
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_entity(self, name: str) -> Optional[Dict]:
        """Get an entity's properties."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM entities WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_outgoing(self, entity: str) -> List[Dict]:
        """Get all relationships FROM an entity."""
        return self.query(from_entity=entity)
    
    def get_incoming(self, entity: str) -> List[Dict]:
        """Get all relationships TO an entity."""
        return self.query(to_entity=entity)
    
    def find_path(self, from_entity: str, to_entity: str, 
                  max_depth: int = 3) -> List[List[str]]:
        """
        Find paths between two entities.
        
        Returns list of paths, each path is a list of relationship strings.
        """
        # BFS to find paths
        paths = []
        visited = set()
        queue = [(from_entity, [from_entity])]
        
        while queue and len(paths) < 10:
            current, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            # Get all outgoing from current
            for rel in self.get_outgoing(current):
                next_entity = rel['to_entity']
                
                if next_entity == to_entity:
                    # Found a path
                    paths.append(path + [next_entity])
                elif next_entity not in visited:
                    visited.add(next_entity)
                    queue.append((next_entity, path + [next_entity]))
        
        return paths
    
    def ask(self, question: str) -> str:
        """
        Natural language query (simple pattern matching).
        
        Examples:
        - "What does Caine build?" 
        - "What is Nova?"
        - "What does Caine like?"
        """
        question = question.lower().strip()
        
        # Pattern: "what does X do/build/like/etc"
        import re
        match = re.match(r"what (?:does|is|are|do) (\w+)", question)
        
        if not match:
            return "I don't understand the question. Try: 'What does [entity] [relationship]?'"
        
        entity = match.group(1).title()  # Capitalize for matching
        
        # Find relationships
        relationships = self.query(from_entity=entity)
        
        if not relationships:
            return f"I don't know anything about {entity} yet."
        
        # Format response
        lines = [f"About {entity}:"]
        for rel in relationships:
            prop = json.loads(rel['properties']) if rel['properties'] else {}
            if prop:
                lines.append(f"  - {rel['relationship']} → {rel['to_entity']} ({prop})")
            else:
                lines.append(f"  - {rel['relationship']} → {rel['to_entity']}")
        
        return "\n".join(lines)
    
    def dump(self) -> Dict:
        """Export entire graph as dict."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM entities")
        entities = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM relationships")
        relationships = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {"entities": entities, "relationships": relationships}


# Convenience function
def create_test_graph() -> KnowledgeGraph:
    """Create a test knowledge graph with sample data."""
    kg = KnowledgeGraph()
    
    # Add entities
    kg.add_entity("Caine", "human", {"role": "builder", "location": "Denver"})
    kg.add_entity("Nova", "AI", {"role": "assistant", "built_from": "9 TV assistants"})
    kg.add_entity("Simmer", "platform", {"type": "prediction market"})
    kg.add_entity("Trading", "activity", {})
    
    # Add relationships
    kg.add_relationship("Caine", "builds", "Nova", {"date": "2026-03-04"})
    kg.add_relationship("Caine", "uses", "Simmer", {"role": "trader"})
    kg.add_relationship("Nova", "trades_on", "Simmer", {"balance": 10000})
    kg.add_relationship("Caine", "likes", "dark chocolate", {})
    kg.add_relationship("Nova", "knows", "Python", {})
    kg.add_relationship("Nova", "knows", "trading", {})
    
    return kg


if __name__ == "__main__":
    # Test it
    kg = create_test_graph()
    
    print("=== Entities ===")
    print(kg.dump()["entities"])
    
    print("\n=== What does Caine build? ===")
    print(kg.query(from_entity="Caine", relationship="builds"))
    
    print("\n=== Natural query ===")
    print(kg.ask("What does Caine build?"))
