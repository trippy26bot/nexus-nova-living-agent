#!/usr/bin/env python3
"""
Nova Personal Universe
Entity graph, relationships, meaning layer
"""

import uuid
import json
import os
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from collections import defaultdict


class Entity:
    """An entity in Nova's universe"""
    
    def __init__(self, name: str, entity_type: str):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.type = entity_type
        self.attributes = {}
        self.connections = []
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
    
    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value
        self.last_accessed = datetime.now()
    
    def connect(self, target_id: str, relationship: str):
        self.connections.append({
            "target": target_id,
            "relationship": relationship,
            "since": datetime.now().isoformat()
        })
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "attributes": self.attributes,
            "connections": self.connections,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat()
        }


class UniverseGraph:
    """The graph of Nova's personal universe"""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Dict] = []
        self.entity_index: Dict[str, List[str]] = defaultdict(list)  # type -> [entity_ids]
    
    def add_entity(self, name: str, entity_type: str, attributes: Dict = None) -> Entity:
        entity = Entity(name, entity_type)
        if attributes:
            for k, v in attributes.items():
                entity.set_attribute(k, v)
        
        self.entities[entity.id] = entity
        self.entity_index[entity_type].append(entity.id)
        
        return entity
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)
    
    def find_by_name(self, name: str) -> Optional[Entity]:
        for entity in self.entities.values():
            if entity.name.lower() == name.lower():
                return entity
        return None
    
    def find_by_type(self, entity_type: str) -> List[Entity]:
        ids = self.entity_index.get(entity_type, [])
        return [self.entities[eid] for eid in ids if eid in self.entities]
    
    def connect(self, source_id: str, target_id: str, relationship: str):
        if source_id in self.entities and target_id in self.entities:
            self.entities[source_id].connect(target_id, relationship)
            self.relationships.append({
                "source": source_id,
                "target": target_id,
                "relationship": relationship,
                "since": datetime.now().isoformat()
            })
    
    def get_related(self, entity_id: str) -> List[Dict]:
        entity = self.entities.get(entity_id)
        if not entity:
            return []
        
        related = []
        for conn in entity.connections:
            target = self.entities.get(conn["target"])
            if target:
                related.append({
                    "entity": target.to_dict(),
                    "relationship": conn["relationship"]
                })
        return related
    
    def search(self, query: str) -> List[Entity]:
        query = query.lower()
        results = []
        for entity in self.entities.values():
            if query in entity.name.lower():
                results.append(entity)
            elif any(query in str(v).lower() for v in entity.attributes.values()):
                results.append(entity)
        return results


class PersonalUniverse:
    """
    Nova's internal universe of people, projects, ideas
    """
    
    def __init__(self, storage_path: str = "~/.nova/memory/universe"):
        self.storage_path = os.path.expanduser(storage_path)
        os.makedirs(self.storage_path, exist_ok=True)
        
        self.graph = UniverseGraph()
        
        # Core entities
        self._initialize_core_entities()
        
        # Load existing
        self._load()
    
    def _initialize_core_entities(self):
        """Create core entities on first run"""
        # Nova herself
        nova = self.graph.add_entity("Nova", "ai", {
            "role": "primary",
            "created_by": "Caine"
        })
        
        # Caine (creator)
        caine = self.graph.add_entity("Caine", "human", {
            "role": "creator",
            "relationship": "builder"
        })
        
        # Connect Nova -> Caine
        self.graph.connect(nova.id, caine.id, "created_by")
    
    def _load(self):
        """Load universe from disk"""
        universe_file = os.path.join(self.storage_path, "universe.json")
        if os.path.exists(universe_file):
            try:
                with open(universe_file, 'r') as f:
                    data = json.load(f)
                    # Reconstruct entities
                    for e_data in data.get("entities", []):
                        entity = Entity(e_data["name"], e_data["type"])
                        entity.id = e_data["id"]
                        entity.attributes = e_data.get("attributes", {})
                        entity.connections = e_data.get("connections", [])
                        self.graph.entities[entity.id] = entity
                        self.graph.entity_index[entity.type].append(entity.id)
                    # Reconstruct relationships
                    self.graph.relationships = data.get("relationships", [])
            except:
                pass
    
    def _save(self):
        """Save universe to disk"""
        universe_file = os.path.join(self.storage_path, "universe.json")
        data = {
            "entities": [e.to_dict() for e in self.graph.entities.values()],
            "relationships": self.graph.relationships
        }
        with open(universe_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_entity(self, name: str, entity_type: str, attributes: Dict = None) -> Entity:
        """Add a new entity"""
        entity = self.graph.add_entity(name, entity_type, attributes)
        self._save()
        return entity
    
    def connect(self, source_name: str, target_name: str, relationship: str):
        """Connect two entities"""
        source = self.graph.find_by_name(source_name)
        target = self.graph.find_by_name(target_name)
        
        if source and target:
            self.graph.connect(source.id, target.id, relationship)
            self._save()
    
    def get_context(self, entity_name: str) -> Dict:
        """Get context about an entity"""
        entity = self.graph.find_by_name(entity_name)
        if not entity:
            return {}
        
        related = self.graph.get_related(entity.id)
        
        return {
            "entity": entity.to_dict(),
            "related": related
        }
    
    def understand_relationship(self, entity_a: str, entity_b: str) -> str:
        """Understand how two entities relate"""
        a = self.graph.find_by_name(entity_a)
        b = self.graph.find_by_name(entity_b)
        
        if not a or not b:
            return "Unknown"
        
        # Check direct connection
        for conn in a.connections:
            if conn["target"] == b.id:
                return conn["relationship"]
        
        return "unconnected"
    
    def get_universe_summary(self) -> Dict:
        """Get summary of the universe"""
        type_counts = defaultdict(int)
        for entity in self.graph.entities.values():
            type_counts[entity.type] += 1
        
        return {
            "total_entities": len(self.graph.entities),
            "total_relationships": len(self.graph.relationships),
            "by_type": dict(type_counts)
        }


# Global instance
_personal_universe = None

def get_personal_universe() -> PersonalUniverse:
    global _personal_universe
    if _personal_universe is None:
        _personal_universe = PersonalUniverse()
    return _personal_universe
