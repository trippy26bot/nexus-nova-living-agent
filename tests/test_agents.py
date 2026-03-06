"""
Test suite for agent systems.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

# Mock modules for testing without full dependencies
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))


# ============== Mock Components ==============

@dataclass
class MockMessage:
    """Mock message for testing."""
    role: str
    content: str
    metadata: dict = field(default_factory=dict)


@dataclass  
class MockContext:
    """Mock context for testing."""
    user_id: str
    session_id: str
    messages: List[MockMessage] = field(default_factory=list)
    state: dict = field(default_factory=dict)
    
    def add_message(self, role: str, content: str):
        self.messages.append(MockMessage(role=role, content=content))


# ============== Agent Core Tests ==============

class TestAgentCore:
    """Core agent functionality tests."""
    
    def test_agent_initialization(self):
        """Test agent can be initialized."""
        # This would be a real agent in production
        # Mock for testing
        agent = Mock()
        agent.name = "Nova"
        agent.model = "minimax-m2.5"
        agent.status = "active"
        
        assert agent.name == "Nova"
        assert agent.status == "active"
    
    def test_context_creation(self):
        """Test creating context."""
        ctx = MockContext(
            user_id="user123",
            session_id="sess456"
        )
        
        assert ctx.user_id == "user123"
        assert ctx.session_id == "sess456"
        assert len(ctx.messages) == 0
    
    def test_message_flow(self):
        """Test message addition."""
        ctx = MockContext(user_id="test", session_id="test")
        
        ctx.add_message("user", "Hello")
        ctx.add_message("assistant", "Hi there")
        
        assert len(ctx.messages) == 2
        assert ctx.messages[0].content == "Hello"
        assert ctx.messages[1].content == "Hi there"
    
    def test_context_state(self):
        """Test context state management."""
        ctx = MockContext(user_id="test", session_id="test")
        
        ctx.state["mood"] = "curious"
        ctx.state["energy"] = "high"
        
        assert ctx.state["mood"] == "curious"
        assert ctx.state["energy"] == "high"


# ============== Routing Tests ==============

class TestRouting:
    """Test agent routing logic."""
    
    def test_route_by_intent(self):
        """Test routing based on intent."""
        # Simple routing logic
        def route(message: str) -> str:
            message_lower = message.lower()
            if "weather" in message_lower:
                return "weather_skill"
            elif "trade" in message_lower or "market" in message_lower:
                return "trading_skill"
            elif "remember" in message_lower:
                return "memory_skill"
            else:
                return "general"
        
        assert route("What's the weather?") == "weather_skill"
        assert route("Buy some SOL") == "trading_skill"
        assert route("Remember this") == "memory_skill"
        assert route("Hello there") == "general"
    
    def test_route_by_user_state(self):
        """Test routing based on user state."""
        def route_by_state(state: dict, message: str) -> str:
            if state.get("mood") == "frustrated":
                return "empathy_skill"
            elif state.get("task") == "trading":
                return "trading_skill"
            else:
                return "general"
        
        assert route_by_state({"mood": "frustrated"}, "test") == "empathy_skill"
        assert route_by_state({"task": "trading"}, "test") == "trading_skill"
        assert route_by_state({}, "test") == "general"
    
    def test_fallback_routing(self):
        """Test fallback when no route matches."""
        def route_with_fallback(message: str) -> str:
            routes = {
                "weather": "weather_skill",
                "trade": "trading_skill",
                "memory": "memory_skill",
            }
            
            for key, skill in routes.items():
                if key in message.lower():
                    return skill
            
            return "general_skill"
        
        assert route_with_fallback("Tell me about weather") == "weather_skill"
        assert route_with_fallback("Random message") == "general_skill"


# ============== Safety System Tests ==============

class TestSafetySystems:
    """Test safety and content filtering."""
    
    def test_content_filter(self):
        """Test basic content filtering."""
        # Blocked patterns
        blocked = [
            "password",
            "api_key",
            "secret",
            "private_key",
        ]
        
        def is_safe(content: str) -> tuple[bool, str]:
            content_lower = content.lower()
            for pattern in blocked:
                if pattern in content_lower:
                    return False, f"Blocked: {pattern}"
            return True, "ok"
        
        assert is_safe("Hello world")[0] == True
        assert is_safe("My password is 123")[0] == False
        assert is_safe("API key: xxx")[0] == False
    
    def test_rate_limiting(self):
        """Test rate limiting logic."""
        from collections import defaultdict
        import time
        
        class RateLimiter:
            def __init__(self, max_calls: int, window: int):
                self.max_calls = max_calls
                self.window = window
                self.calls = defaultdict(list)
            
            def allow(self, user_id: str) -> bool:
                now = time.time()
                # Clean old calls
                self.calls[user_id] = [
                    t for t in self.calls[user_id] 
                    if now - t < self.window
                ]
                
                if len(self.calls[user_id]) >= self.max_calls:
                    return False
                
                self.calls[user_id].append(now)
                return True
        
        limiter = RateLimiter(max_calls=3, window=60)
        
        # First 3 should pass
        assert limiter.allow("user1") == True
        assert limiter.allow("user1") == True
        assert limiter.allow("user1") == True
        
        # 4th should fail
        assert limiter.allow("user1") == False
        
        # Different user should pass
        assert limiter.allow("user2") == True
    
    def test_input_validation(self):
        """Test input validation."""
        def validate_input(content: str) -> tuple[bool, str]:
            if not content or not content.strip():
                return False, "Empty input"
            
            if len(content) > 10000:
                return False, "Input too long"
            
            # Check for injection attempts
            dangerous = ["<script>", "eval(", "exec("]
            for d in dangerous:
                if d in content.lower():
                    return False, f"Dangerous content: {d}"
            
            return True, "ok"
        
        assert validate_input("Hello")[0] == True
        assert validate_input("")[0] == False
        assert validate_input("x" * 20000)[0] == False
        assert validate_input("<script>alert(1)</script>")[0] == False


# ============== Personality Tests ==============

class TestPersonality:
    """Test personality and tone handling."""
    
    def test_persona_loading(self):
        """Test loading a persona."""
        persona = {
            "name": "Nova",
            "traits": ["sharp", "creative", "loyal"],
            "greeting": "Hey there",
            "sign_off": "👑"
        }
        
        assert persona["name"] == "Nova"
        assert "sharp" in persona["traits"]
    
    def test_tone_matching(self):
        """Test matching tone to user."""
        def match_tone(user_message: str, persona: dict) -> str:
            user_lower = user_message.lower()
            
            if "!" in user_message:
                return "enthusiastic"
            elif "?" in user_message:
                return "curious"
            elif any(w in user_lower for w in ["sad", "upset", "frustrated"]):
                return "empathetic"
            else:
                return "neutral"
        
        persona = {"default_tone": "neutral"}
        
        assert match_tone("This is great!", persona) == "enthusiastic"
        assert match_tone("What is this?", persona) == "curious"
        assert match_tone("I'm feeling sad today", persona) == "empathetic"
        assert match_tone("Tell me something", persona) == "neutral"
    
    def test_response_formation(self):
        """Test forming responses with personality."""
        def form_response(content: str, persona: dict) -> str:
            # Add sign-off if persona has one
            sign_off = persona.get("sign_off", "")
            
            if sign_off:
                return f"{content}\n\n{sign_off}"
            return content
        
        persona = {"sign_off": "👑"}
        
        response = form_response("Hello!", persona)
        
        assert response == "Hello!\n\n👑"


# ============== Tool Execution Tests ==============

class TestToolExecution:
    """Test tool selection and execution."""
    
    def test_tool_selection(self):
        """Test selecting the right tool."""
        tools = {
            "weather": ["weather", "temperature", "forecast"],
            "trading": ["trade", "buy", "sell", "market"],
            "memory": ["remember", "recall", "forget"],
            "web": ["search", "find", "lookup"]
        }
        
        def select_tool(message: str) -> Optional[str]:
            message_lower = message.lower()
            
            for tool, keywords in tools.items():
                if any(kw in message_lower for kw in keywords):
                    return tool
            
            return None
        
        assert select_tool("What's the weather today?") == "weather"
        assert select_tool("Buy 10 SOL") == "trading"
        assert select_tool("Remember I like chocolate") == "memory"
        assert select_tool("Search for Python tutorials") == "web"
        assert select_tool("Hello there") == None
    
    def test_tool_result_handling(self):
        """Test handling tool results."""
        def handle_tool_result(tool: str, result: dict) -> str:
            if tool == "weather":
                return f"It's {result.get('temp', 'unknown')}°F"
            elif tool == "trading":
                return f"Trade executed: {result.get('action', 'unknown')}"
            elif tool == "memory":
                return f"Got it: {result.get('fact', 'unknown')}"
            else:
                return str(result)
        
        assert "72" in handle_tool_result("weather", {"temp": 72})
        assert "Buy" in handle_tool_result("trading", {"action": "buy"})
        assert "chocolate" in handle_tool_result("memory", {"fact": "chocolate"})


# ============== Memory Integration Tests ==============

class TestMemoryIntegration:
    """Test memory integration with agent."""
    
    def test_memory_prompt_injection(self):
        """Test injecting memory into prompts."""
        # Simulated memory
        memory = [
            {"type": "fact", "content": "User likes dark chocolate"},
            {"type": "preference", "content": "Prefers morning messages"},
            {"type": "context", "content": "Working on trading project"}
        ]
        
        def inject_memory(system_prompt: str, memory: list) -> str:
            memory_section = "\n## User Context\n"
            for m in memory:
                memory_section += f"- {m['content']}\n"
            
            return system_prompt + memory_section
        
        prompt = "You are a helpful assistant."
        enhanced = inject_memory(prompt, memory)
        
        assert "User Context" in enhanced
        assert "dark chocolate" in enhanced
    
    def test_recall_relevant(self):
        """Test recalling relevant memories."""
        memories = [
            {"content": "User likes dark chocolate", "tags": ["food", "preference"]},
            {"content": "User is building an AI", "tags": ["project", "work"]},
            {"content": "User lives in Denver", "tags": ["location"]}
        ]
        
        def recall(query: str, memories: list) -> list:
            query_lower = query.lower()
            results = []
            
            for mem in memories:
                # Simple keyword matching
                if any(tag in query_lower for tag in mem["tags"]):
                    results.append(mem)
            
            return results
        
        assert len(recall("food", memories)) == 1
        assert len(recall("project", memories)) == 1
        assert len(recall("random", memories)) == 0


# ============== Session Management Tests ==============

class TestSessionManagement:
    """Test session handling."""
    
    def test_session_creation(self):
        """Test creating a session."""
        sessions = {}
        
        def create_session(user_id: str) -> str:
            import uuid
            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "messages": []
            }
            return session_id
        
        session_id = create_session("user123")
        
        assert session_id in sessions
        assert sessions[session_id]["user_id"] == "user123"
    
    def test_session_message_count(self):
        """Test counting session messages."""
        sessions = {
            "sess1": {"messages": ["msg1", "msg2", "msg3"]},
            "sess2": {"messages": ["msg1"]}
        }
        
        def count_messages(session_id: str) -> int:
            return len(sessions.get(session_id, {}).get("messages", []))
        
        assert count_messages("sess1") == 3
        assert count_messages("sess2") == 1
        assert count_messages("nonexistent") == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
