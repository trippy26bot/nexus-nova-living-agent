#!/usr/bin/env python3
"""
NOVA MCP — Model Context Protocol Server
Allows Claude to call Nova's tools natively.

MCP lets other AI systems use Nova as a tool.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import sys

# Configuration
NOVA_DIR = Path.home() / ".nova"
NOVA_DB = NOVA_DIR / "nova.db"


@dataclass
class MCPTool:
    """An MCP tool definition."""
    name: str
    description: str
    input_schema: Dict
    handler: callable


class MCPServer:
    """MCP Server for Nova's capabilities."""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools."""
        
        # Memory tools
        self.register_tool(MCPTool(
            name="nova_memory_store",
            description="Store something in Nova's memory",
            input_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "What to remember"},
                    "memory_type": {"type": "string", "enum": ["episodic", "semantic", "working"]},
                    "importance": {"type": "integer", "minimum": 1, "maximum": 10}
                },
                "required": ["content"]
            },
            handler=self._handle_memory_store
        ))
        
        self.register_tool(MCPTool(
            name="nova_memory_recall",
            description="Recall memories from Nova's memory",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for"},
                    "limit": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            },
            handler=self._handle_memory_recall
        ))
        
        # Goal tools
        self.register_tool(MCPTool(
            name="nova_goals_list",
            description="List Nova's current goals",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_goals_list
        ))
        
        self.register_tool(MCPTool(
            name="nova_goals_add",
            description="Add a goal to Nova's list",
            input_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Goal description"},
                    "priority": {"type": "integer", "minimum": 1, "maximum": 10}
                },
                "required": ["content"]
            },
            handler=self._handle_goals_add
        ))
        
        # Interest tools
        self.register_tool(MCPTool(
            name="nova_interests",
            description="Get Nova's current interests",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_interests
        ))
        
        self.register_tool(MCPTool(
            name="nova_emotion",
            description="Get Nova's current emotional state",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_emotion
        ))
        
        # Chat tool
        self.register_tool(MCPTool(
            name="nova_chat",
            description="Send a message to Nova and get a response",
            input_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Message to Nova"},
                    "context": {"type": "string", "description": "Additional context"}
                },
                "required": ["message"]
            },
            handler=self._handle_chat
        ))
        
        # Daemon tools
        self.register_tool(MCPTool(
            name="nova_explore",
            description="Trigger Nova to explore her interests",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Specific topic to explore"}
                }
            },
            handler=self._handle_explore
        ))
    
    def register_tool(self, tool: MCPTool):
        """Register a tool."""
        self.tools[tool.name] = tool
    
    def get_tools(self) -> List[Dict]:
        """Get all registered tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            }
            for tool in self.tools.values()
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Call a tool with arguments."""
        
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
        
        tool = self.tools[tool_name]
        
        try:
            return tool.handler(arguments)
        except Exception as e:
            return {"error": str(e)}
    
    # Tool handlers
    def _handle_memory_store(self, args: Dict) -> Dict:
        """Store a memory."""
        
        content = args.get('content', '')
        memory_type = args.get('memory_type', 'episodic')
        importance = args.get('importance', 5)
        
        if not NOVA_DB.exists():
            return {"error": "Nova not initialized"}
        
        conn = sqlite3.connect(NOVA_DB)
        c = conn.cursor()
        
        c.execute(
            "INSERT INTO memories (content, memory_type, importance) VALUES (?, ?, ?)",
            (content, memory_type, importance)
        )
        
        conn.commit()
        conn.close()
        
        return {"status": "stored", "content": content[:50] + "..."}
    
    def _handle_memory_recall(self, args: Dict) -> Dict:
        """Recall memories."""
        
        query = args.get('query', '')
        limit = args.get('limit', 5)
        
        if not NOVA_DB.exists():
            return {"error": "Nova not initialized"}
        
        conn = sqlite3.connect(NOVA_DB)
        c = conn.cursor()
        
        c.execute(
            "SELECT content, memory_type, importance, created_at FROM memories WHERE content LIKE ? ORDER BY importance DESC LIMIT ?",
            (f"%{query}%", limit)
        )
        
        results = []
        for row in c.fetchall():
            results.append({
                "content": row[0],
                "type": row[1],
                "importance": row[2],
                "created": row[3]
            })
        
        conn.close()
        
        return {"memories": results}
    
    def _handle_goals_list(self, args: Dict) -> Dict:
        """List goals."""
        
        if not NOVA_DB.exists():
            return {"error": "Nova not initialized"}
        
        conn = sqlite3.connect(NOVA_DB)
        c = conn.cursor()
        
        c.execute("SELECT id, content, priority, status FROM goals ORDER BY priority DESC")
        
        goals = []
        for row in c.fetchall():
            goals.append({
                "id": row[0],
                "content": row[1],
                "priority": row[2],
                "status": row[3]
            })
        
        conn.close()
        
        return {"goals": goals}
    
    def _handle_goals_add(self, args: Dict) -> Dict:
        """Add a goal."""
        
        content = args.get('content', '')
        priority = args.get('priority', 5)
        
        if not NOVA_DB.exists():
            return {"error": "Nova not initialized"}
        
        conn = sqlite3.connect(NOVA_DB)
        c = conn.cursor()
        
        c.execute(
            "INSERT INTO goals (content, priority) VALUES (?, ?)",
            (content, priority)
        )
        
        goal_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return {"status": "created", "id": goal_id, "content": content}
    
    def _handle_interests(self, args: Dict) -> Dict:
        """Get interests."""
        
        interests_file = NOVA_DIR / "NOVAS_INTERESTS.md"
        
        if not interests_file.exists():
            return {"interests": {}}
        
        content = interests_file.read_text()
        
        # Parse interests
        interests = {}
        current = None
        
        for line in content.split('\n'):
            if line.startswith('## '):
                current = line[3:].strip()
                interests[current] = {'depth': 1, 'questions': []}
            elif '**Depth:**' in line and current:
                try:
                    interests[current]['depth'] = int(line.split(':')[1].strip())
                except:
                    pass
        
        return {"interests": interests}
    
    def _handle_emotion(self, args: Dict) -> Dict:
        """Get emotional state."""
        
        emotion_state = NOVA_DIR / "emotion_state.json"
        
        if not emotion_state.exists():
            return {"error": "No emotion state"}
        
        with open(emotion_state) as f:
            state = json.load(f)
        
        # Find dominant
        emotions = {k: v for k, v in state.items() if k != 'last_update'}
        dominant = max(emotions, key=emotions.get)
        
        return {
            "state": state,
            "dominant": dominant,
            "dominance": emotions[dominant]
        }
    
    def _handle_chat(self, args: Dict) -> Dict:
        """Handle chat message."""
        
        message = args.get('message', '')
        
        if not message:
            return {"error": "No message provided"}
        
        # Try to import Nova's LLM
        try:
            from nova import call_llm, load_emotion_state, get_dominant_emotion
            
            dominant, dominance = get_dominant_emotion()
            system = f"You are Nova. Current emotional state: {dominant} ({dominance:.0%})"
            
            response = call_llm(message, system=system)
            
            return {"response": response, "emotion": {"dominant": dominant, "dominance": dominance}}
        
        except ImportError:
            return {"error": "Nova not configured"}
    
    def _handle_explore(self, args: Dict) -> Dict:
        """Trigger exploration."""
        
        try:
            from nova_daemon import run_exploration_cycle
            
            result = run_exploration_cycle()
            return {"status": "explored", "result": result}
        
        except Exception as e:
            return {"error": str(e)}


# MCP Protocol implementation
def mcp_list_tools() -> str:
    """List all available tools (MCP protocol)."""
    server = MCPServer()
    tools = server.get_tools()
    
    return json.dumps({
        "jsonrpc": "2.0",
        "id": None,
        "result": {"tools": tools}
    })


def mcp_call_tool(tool_name: str, arguments: Dict) -> str:
    """Call a tool (MCP protocol)."""
    server = MCPServer()
    result = server.call_tool(tool_name, arguments)
    
    return json.dumps({
        "jsonrpc": "2.0",
        "id": None,
        "result": result
    })


def mcp_handle_request(request: Dict) -> Dict:
    """Handle an MCP request."""
    
    method = request.get('method')
    request_id = request.get('id')
    
    if method == "tools/list":
        server = MCPServer()
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": server.get_tools()}
        }
    
    elif method == "tools/call":
        tool_name = request.get('params', {}).get('name')
        arguments = request.get('params', {}).get('arguments', {})
        
        server = MCPServer()
        result = server.call_tool(tool_name, arguments)
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }


# Run as server
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Nova MCP Server")
    parser.add_argument('--stdio', action='store_true', help='Run in stdio mode')
    parser.add_argument('--port', type=int, default=8080, help='Port for TCP mode')
    
    args = parser.parse_args()
    
    if args.stdio:
        # Stdio mode (for Claude integration)
        import sys
        
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            
            try:
                request = json.loads(line)
                response = mcp_handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            except Exception as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": str(e)}
                }))
                sys.stdout.flush()
    
    else:
        print("Nova MCP Server")
        print("=" * 40)
        print(f"Run with --stdio for Claude integration")
        print("\nAvailable tools:")
        server = MCPServer()
        for tool in server.get_tools():
            print(f"  - {tool['name']}: {tool['description']}")
