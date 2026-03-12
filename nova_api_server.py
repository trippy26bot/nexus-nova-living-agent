#!/usr/bin/env python3
"""
Nova API Server - Simple HTTP Version
Uses only standard library (no pip install needed)
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Optional

# ============== In-Memory Store ==============
class NovaMemory:
    def __init__(self):
        self.history = []
        self.last_state = None
        self.agents = {}
        self.last_thought = "Nova initialized. Waiting for world state..."
    
    def record(self, event: dict):
        self.history.append({"time": time.time(), **event})
        if len(self.history) > 1000:
            self.history = self.history[-1000:]

memory = NovaMemory()

# ============== Request Handler ==============
class NovaHandler(BaseHTTPRequestHandler):
    
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length))
        return {}
    
    def do_GET(self):
        path = urlparse(self.path).path
        
        if path == "/":
            self._send_json({
                "name": "Nova API",
                "version": "1.0.0",
                "status": "running"
            })
        
        elif path == "/world/state":
            if memory.last_state:
                self._send_json(memory.last_state)
            else:
                self._send_json({"error": "No world state yet"}, 404)
        
        elif path == "/nova/memory":
            self._send_json({
                "last_thought": memory.last_thought,
                "events": len(memory.history)
            })
        
        elif path == "/agents":
            self._send_json({"agents": list(memory.agents.values())})
        
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        data = self._read_json()
        
        if path == "/world/state":
            memory.last_state = data
            memory.record({"type": "world_state", "agents": len(data.get("agents", []))})
            self._send_json({"status": "received"})
        
        elif path == "/nova/think":
            # Nova processes world and returns decisions
            agents = data.get("agents", [])
            
            orders = []
            thoughts = []
            
            # Group by role
            explorers = [a for a in agents if a.get("role") == "explorer"]
            builders = [a for a in agents if a.get("role") == "builder"]
            guards = [a for a in agents if a.get("role") == "guard"]
            
            # Simple AI logic
            if explorers:
                for i, exp in enumerate(explorers[:3]):
                    orders.append({
                        "agent": exp.get("id"),
                        "goal": "explore",
                        "target": [100 + i*50, 100, 0]
                    })
                thoughts.append(f"Explorers: mapping territory")
            
            if builders and data.get("resources"):
                orders.append({
                    "agent": builders[0].get("id"),
                    "goal": "build",
                    "target": [50, 50, 0]
                })
                thoughts.append(f"Builder: constructing")
            
            if guards and data.get("players"):
                orders.append({
                    "agent": guards[0].get("id"),
                    "goal": "guard",
                    "target": data["players"][0].get("location", [0,0,0])
                })
                thoughts.append(f"Guard: protecting")
            
            memory.last_thought = " | ".join(thoughts) if thoughts else "Observing..."
            memory.record({"type": "think_cycle"})
            
            self._send_json({
                "orders": orders,
                "thoughts": memory.last_thought
            })
        
        elif path == "/world/orders":
            for order in data:
                memory.record({"type": "order", **order})
            self._send_json({"status": "executing"})
        
        elif path == "/agent/spawn":
            agent_id = data.get("id")
            memory.agents[agent_id] = data
            memory.record({"type": "spawn", "agent": agent_id})
            self._send_json({"status": "spawned", "id": agent_id})
        
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def log_message(self, format, *args):
        print(f"[Nova API] {args[0]}")

# ============== Run Server ==============
def run(port=8001):
    server = HTTPServer(("0.0.0.0", port), NovaHandler)
    print(f"🌐 Nova API Server running on http://localhost:{port}")
    print("Endpoints:")
    print("  GET  /world/state - Get current world")
    print("  POST /world/state - Update world state")
    print("  POST /nova/think   - Nova processes & decides")
    print("  GET  /nova/memory - Nova's thoughts")
    print("  POST /agent/spawn - Spawn new agent")
    print()
    server.serve_forever()

if __name__ == "__main__":
    run()
