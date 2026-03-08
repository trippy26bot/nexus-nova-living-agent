"""
Test suite for memory systems.
"""

import pytest
import os
import tempfile
import time
import ast
import json
from pathlib import Path

# Import the modules we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from knowledge_graph import KnowledgeGraph
from world_model import WorldModel


# ============== Knowledge Graph Tests ==============

class TestKnowledgeGraph:
    """Tests for KnowledgeGraph."""
    
    @pytest.fixture
    def kg(self):
        """Create a fresh KnowledgeGraph for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        kg = KnowledgeGraph(db_path=db_path)
        yield kg
        os.unlink(db_path)
    
    def test_add_entity(self, kg):
        """Test adding an entity."""
        kg.add_entity("Caine", "human", {"role": "builder"})
        
        entity = kg.get_entity("Caine")
        
        assert entity is not None
        assert entity["name"] == "Caine"
        assert entity["entity_type"] == "human"
        assert "role" in entity["properties"]
    
    def test_add_relationship(self, kg):
        """Test adding a relationship."""
        kg.add_entity("Caine", "human")
        kg.add_entity("Nova", "AI")
        kg.add_relationship("Caine", "builds", "Nova")
        
        relationships = kg.query(from_entity="Caine")
        
        assert len(relationships) == 1
        assert relationships[0]["relationship"] == "builds"
        assert relationships[0]["to_entity"] == "Nova"
    
    def test_query_by_relationship(self, kg):
        """Test querying by relationship type."""
        kg.add_entity("Caine", "human")
        kg.add_entity("Nova", "AI")
        kg.add_entity("Simmer", "platform")
        
        kg.add_relationship("Caine", "uses", "Simmer")
        kg.add_relationship("Caine", "builds", "Nova")
        
        builds_rels = kg.query(relationship="builds")
        
        assert len(builds_rels) == 1
        assert builds_rels[0]["from_entity"] == "Caine"
    
    def test_get_outgoing(self, kg):
        """Test getting outgoing relationships."""
        kg.add_entity("A", "entity")
        kg.add_entity("B", "entity")
        kg.add_entity("C", "entity")
        
        kg.add_relationship("A", "connects_to", "B")
        kg.add_relationship("A", "connects_to", "C")
        
        outgoing = kg.get_outgoing("A")
        
        assert len(outgoing) == 2
    
    def test_get_incoming(self, kg):
        """Test getting incoming relationships."""
        kg.add_entity("A", "entity")
        kg.add_entity("B", "entity")
        
        kg.add_relationship("A", "likes", "B")
        
        incoming = kg.get_incoming("B")
        
        assert len(incoming) == 1
        assert incoming[0]["from_entity"] == "A"
    
    def test_find_path(self, kg):
        """Test path finding between entities."""
        kg.add_entity("A", "entity")
        kg.add_entity("B", "entity")
        kg.add_entity("C", "entity")
        
        kg.add_relationship("A", "knows", "B")
        kg.add_relationship("B", "knows", "C")
        
        paths = kg.find_path("A", "C", max_depth=3)
        
        assert len(paths) > 0
        assert "C" in paths[0]
    
    def test_ask_question(self, kg):
        """Test natural language query."""
        kg.add_entity("Caine", "human")
        kg.add_entity("Nova", "AI")
        
        kg.add_relationship("Caine", "builds", "Nova")
        
        result = kg.ask("What does Caine build?")
        
        assert "Nova" in result
        assert "builds" in result
    
    def test_entity_properties(self, kg):
        """Test entity with properties."""
        props = {"role": "builder", "location": "Denver", "age": 30}
        kg.add_entity("Caine", "human", props)
        
        entity = kg.get_entity("Caine")
        try:
            loaded_props = json.loads(entity["properties"])
        except Exception:
            loaded_props = ast.literal_eval(entity["properties"])
        
        assert loaded_props["role"] == "builder"
        assert loaded_props["location"] == "Denver"
    
    def test_relationship_properties(self, kg):
        """Test relationship with properties."""
        kg.add_entity("Caine", "human")
        kg.add_entity("Nova", "AI")
        
        kg.add_relationship("Caine", "builds", "Nova", {"date": "2026-03-04"})
        
        rels = kg.query(from_entity="Caine")
        
        assert "date" in rels[0]["properties"]


# ============== World Model Tests ==============

class TestWorldModel:
    """Tests for WorldModel."""
    
    @pytest.fixture
    def wm(self):
        """Create a fresh WorldModel for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        wm = WorldModel(db_path=db_path)
        yield wm
        os.unlink(db_path)
    
    def test_set_and_get_state(self, wm):
        """Test setting and getting state."""
        wm.set_state("user", "mood", "happy", confidence=0.9)
        
        state = wm.get_state(category="user", key="mood")
        
        assert "mood" in state
        assert state["mood"] == "happy"
    
    def test_get_all_current_state(self, wm):
        """Test getting all current state."""
        wm.set_state("user", "mood", "curious")
        wm.set_state("agent", "status", "active")
        wm.set_state("environment", "hour", 14)
        
        all_state = wm.get_all_current_state()
        
        assert "user.mood" in all_state
        assert "agent.status" in all_state
        assert "environment.hour" in all_state
    
    def test_make_prediction(self, wm):
        """Test making a prediction."""
        pred_id = wm.predict("user will ask about trading", "intent", 0.7)
        
        assert pred_id > 0
    
    def test_resolve_prediction(self, wm):
        """Test resolving a prediction."""
        pred_id = wm.predict("test prediction", "test", 0.5)
        
        wm.resolve_prediction(pred_id, "test prediction")
        
        accuracy = wm.get_prediction_accuracy()
        
        assert accuracy == 1.0
    
    def test_add_heuristic(self, wm):
        """Test adding a heuristic."""
        condition = {"user.mood": "frustrated"}
        action = {"type": "encourage"}
        
        wm.add_heuristic("test_heuristic", condition, action, 1.5)
        
        triggered = wm.evaluate_heuristics({"user.mood": "frustrated"})
        
        assert len(triggered) == 1
        assert triggered[0]["name"] == "test_heuristic"
    
    def test_evaluate_heuristics_no_match(self, wm):
        """Test heuristics that don't match."""
        condition = {"user.mood": "happy"}
        action = {"type": "celebrate"}
        
        wm.add_heuristic("happy_heuristic", condition, action)
        
        triggered = wm.evaluate_heuristics({"user.mood": "sad"})
        
        assert len(triggered) == 0
    
    def test_record_turn(self, wm):
        """Test recording a conversation turn."""
        wm.record_turn("user", "Hello there", sentiment=0.3, topics=["greeting"])
        wm.record_turn("assistant", "Hi! How can I help?", sentiment=0.5)
        
        flow = wm.get_conversation_flow()
        
        assert len(flow) == 2
        assert flow[0]["role"] == "user"
        assert flow[1]["role"] == "assistant"
    
    def test_infer_user_mood(self, wm):
        """Test inferring user mood."""
        wm.record_turn("user", "This is frustrating", sentiment=-0.5)
        
        mood = wm.infer_user_mood()
        
        assert mood == "frustrated"
    
    def test_infer_user_mood_positive(self, wm):
        """Test inferring positive mood."""
        wm.record_turn("user", "This is great!", sentiment=0.7)
        
        mood = wm.infer_user_mood()
        
        assert mood == "happy"
    
    def test_context_summary(self, wm):
        """Test getting context summary."""
        wm.set_state("user", "energy", "high")
        wm.record_turn("user", "Hello")
        
        summary = wm.get_context_summary()
        
        assert "energy" in summary.lower() or "turn" in summary.lower()
    
    def test_multiple_state_updates(self, wm):
        """Test that state updates create new entries."""
        wm.set_state("user", "mood", "happy")
        wm.set_state("user", "mood", "excited")
        
        state = wm.get_state(category="user", key="mood")
        
        # Should get the latest value
        assert state["mood"] == "excited"


# ============== Integration Tests ==============

class TestMemoryIntegration:
    """Integration tests for memory systems."""
    
    @pytest.fixture
    def kg(self):
        """Knowledge graph fixture."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        kg = KnowledgeGraph(db_path=db_path)
        yield kg
        os.unlink(db_path)
    
    @pytest.fixture
    def wm(self):
        """World model fixture."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        wm = WorldModel(db_path=db_path)
        yield wm
        os.unlink(db_path)
    
    def test_kg_and_wm_together(self, kg, wm):
        """Test using KG and WM together."""
        # KG tracks relationships
        kg.add_entity("Caine", "human")
        kg.add_entity("Nova", "AI")
        kg.add_relationship("Caine", "builds", "Nova")
        
        # WM tracks state
        wm.set_state("user", "name", "Caine")
        wm.set_state("agent", "name", "Nova")
        
        # They work together
        assert kg.get_entity("Caine") is not None
        assert "user.name" in wm.get_all_current_state()
    
    def test_world_model_influences_kg(self, kg, wm):
        """Test how world model state affects knowledge graph."""
        # User expresses interest
        wm.record_turn("user", "I like trading", sentiment=0.4, topics=["trading"])
        
        # KG can store this as knowledge
        kg.add_entity("Caine", "human")
        kg.add_relationship("Caine", "interested_in", "trading")
        
        assert kg.query(from_entity="Caine", relationship="interested_in")


# ============== Performance Tests ==============

class TestPerformance:
    """Basic performance tests."""
    
    @pytest.fixture
    def kg(self):
        """KG fixture."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        kg = KnowledgeGraph(db_path=db_path)
        yield kg
        os.unlink(db_path)
    
    @pytest.fixture
    def wm(self):
        """WM fixture."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        wm = WorldModel(db_path=db_path)
        yield wm
        os.unlink(db_path)
    
    def test_kg_many_entities(self, kg):
        """Test adding many entities."""
        start = time.time()
        
        for i in range(100):
            kg.add_entity(f"Entity_{i}", "test")
        
        elapsed = time.time() - start
        
        assert elapsed < 2.0  # Should complete in 2 seconds
    
    def test_wm_many_states(self, wm):
        """Test setting many state values."""
        start = time.time()
        
        for i in range(100):
            wm.set_state("test", f"key_{i}", f"value_{i}")
        
        elapsed = time.time() - start
        
        assert elapsed < 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
