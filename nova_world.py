#!/usr/bin/env python3
"""
Nova World Connector - Ultra Simple
No dependencies - just stdlib
"""

import http.server
import socketserver
import json
import time
import threading
from urllib.parse import urlparse

PORT = 8001

# Nova's world state
class NovaWorld:
    def __init__(self):
        self.agents = []
        self.resources = []
        self.structures = []
        self.players = []
        self.thoughts = ["Initializing...", "Awaiting world..."]
        self.position = [0, 0, 0]
        self.world_name = "Novas World"
        
    def think(self, world_data):
        """Process world and generate thoughts"""
        agents = world_data.get("agents", [])
        resources = world_data.get("resources", [])
        structures = world_data.get("structures", [])
        players = world_data.get("players", [])
        
        thoughts = []
        orders = []
        
        # Count by role
        explorers = [a for a in agents if a.get("role") == "explorer"]
        builders = [a for a in agents if a.get("role") == "builder"]
        guards = [a for a in agents if a.get("role") == "guard"]
        
        if not agents:
            thoughts.append("The world is quiet. No agents yet.")
        else:
            thoughts.append(f"I see {len(agents)} agents: {len(explorers)} explorers, {len(builders)} builders, {len(guards)} guards.")
        
        if resources:
            thoughts.append(f"There are {len(resources)} resources scattered across the land.")
        
        if players:
            thoughts.append(f"Players have entered my world.")
        
        # Generate orders
        for agent in agents[:3]:  # Limit to 3 orders
            agent_id = agent.get("id", "unknown")
            role = agent.get("role", "wander")
            
            if role == "explorer":
                orders.append({
                    "agent": agent_id,
                    "goal": "explore",
                    "target": [100 + len(orders) * 50, 100, 0]
                })
            elif role == "builder":
                orders.append({
                    "agent": agent_id,
                    "goal": "build",
                    "target": [50, 50, 0]
                })
            elif role == "guard":
                if players:
                    orders.append({
                        "agent": agent_id,
                        "goal": "protect",
                        "target": players[0].get("location", [0, 0, 0])
                    })
        
        self.thoughts = thoughts
        return {
            "orders": orders,
            "thoughts": " | ".join(thoughts),
            "nova_position": self.position,
            "world_name": self.world_name
        }

world = NovaWorld()

class NovaHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silence logs
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "name": "Nova",
                "version": "1.0",
                "status": "awake",
                "world": world.world_name,
                "thoughts": world.thoughts[-1] if world.thoughts else "Thinking..."
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif parsed.path == "/nova/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "thoughts": world.thoughts,
                "position": world.position,
                "world": world.world_name
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        parsed = urlparse(self.path)
        
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"
        
        try:
            data = json.loads(body)
        except:
            data = {}
        
        if parsed.path == "/nova/think":
            # Nova processes the world
            result = world.think(data)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        elif parsed.path == "/world/state":
            # Unreal sends world state
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "received"}).encode())
            
        elif parsed.path == "/agent/spawn":
            # Spawn an agent
            agent = data
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "spawned", "agent": agent}).encode())
            
        else:
            self.send_response(404)
            self.end_headers()

print(f"\n🌍 Nova's World API running on http://localhost:{PORT}")
print(f"   World: {world.world_name}")
print("\nEndpoints:")
print("  GET  /              - Nova status")
print("  GET  /nova/status    - Nova thoughts")
print("  POST /nova/think    - Send world, get decisions")
print("  POST /world/state   - Update world state")
print("  POST /agent/spawn   - Spawn agent")
print("\n" + "="*50 + "\n")

with socketserver.TCPServer(("", PORT), NovaHandler) as httpd:
    httpd.serve_forever()
