#!/usr/bin/env python3
"""
NOVA API — REST API Server for External Integrations
Allows external tools and services to communicate with Nova.

Endpoints:
  POST /chat         — Send a message, get a response
  GET  /memory       — Query memories
  POST /memory       — Store a memory
  GET  /goals         — List goals
  POST /goals         — Add a goal
  GET  /interests     — Get interests
  GET  /emotion       — Get emotional state
  POST /daemon/cycle — Trigger exploration cycle
  GET  /health        — Health check

Run: nova api --port 8080
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sqlite3
import threading
import asyncio

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Configuration
API_VERSION = "2.0.0"
DEFAULT_PORT = 8080

# Import Nova functions
try:
    from nova import (
        call_llm, load_interests, load_emotion_state, get_dominant_emotion,
        log_to_memory, get_recent_memories, NOVA_DB, NOVA_DIR,
        update_emotion, get_recent_memories
    )
except ImportError:
    # Fallback if nova.py not available
    def call_llm(prompt, system=None):
        return "Nova API: LLM not configured"
    
    def load_interests():
        return {}
    
    def load_emotion_state():
        return {"curiosity": 0.5}
    
    def get_dominant_emotion():
        return "curiosity", 0.5
    
    def log_to_memory(*args, **kwargs):
        pass
    
    def get_recent_memories(limit=10):
        return []


class NovaAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Nova API."""
    
    def log_message(self, format, *args):
        """Log to stderr."""
        sys.stderr.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}\n")
    
    def send_json(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def get_body(self):
        """Get request body as JSON."""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            return json.loads(body.decode())
        return {}
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        if path == '/health':
            self.send_json({
                "status": "ok",
                "version": API_VERSION,
                "timestamp": datetime.now().isoformat()
            })
        
        elif path == '/memory':
            limit = int(query.get('limit', [10])[0])
            memories = get_recent_memories(limit)
            self.send_json({
                "memories": [
                    {"content": m[0], "type": m[1], "importance": m[2], "created": m[3]}
                    for m in memories
                ]
            })
        
        elif path == '/goals':
            conn = sqlite3.connect(str(NOVA_DB) if 'NOVA_DB' in dir() else "~/.nova/nova.db")
            c = conn.cursor()
            c.execute("SELECT id, content, priority, status FROM goals ORDER BY priority DESC")
            goals = [{"id": g[0], "content": g[1], "priority": g[2], "status": g[3]} for g in c.fetchall()]
            conn.close()
            self.send_json({"goals": goals})
        
        elif path == '/interests':
            interests = load_interests()
            self.send_json({"interests": interests})
        
        elif path == '/emotion':
            state = load_emotion_state()
            dominant, dominance = get_dominant_emotion()
            self.send_json({
                "state": state,
                "dominant": dominant,
                "dominance": dominance
            })
        
        else:
            self.send_json({"error": "Not found"}, status=404)
    
    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        body = self.get_body()
        
        if path == '/chat':
            message = body.get('message', '')
            context = body.get('context', {})
            
            if not message:
                self.send_json({"error": "No message provided"}, status=400)
                return
            
            # Build prompt
            system = context.get('system', 'You are Nova, a helpful AI assistant.')
            
            # Add emotion context
            dominant, dominance = get_dominant_emotion()
            system += f"\n\nCurrent emotional state: {dominant} ({dominance:.0%})"
            
            # Get response
            response = call_llm(message, system=system)
            
            # Log the interaction
            log_to_memory(f"API: {message}", memory_type='episodic', importance=5)
            
            self.send_json({
                "response": response,
                "emotion": {"dominant": dominant, "dominance": dominance}
            })
        
        elif path == '/memory':
            content = body.get('content', '')
            memory_type = body.get('type', 'episodic')
            importance = body.get('importance', 5)
            
            if not content:
                self.send_json({"error": "No content provided"}, status=400)
                return
            
            log_to_memory(content, memory_type=memory_type, importance=importance)
            
            self.send_json({"status": "stored", "content": content[:50] + "..."})
        
        elif path == '/goals':
            content = body.get('content', '')
            priority = body.get('priority', 5)
            
            if not content:
                self.send_json({"error": "No content provided"}, status=400)
                return
            
            conn = sqlite3.connect(str(NOVA_DB) if 'NOVA_DB' in dir() else "~/.nova/nova.db")
            c = conn.cursor()
            c.execute("INSERT INTO goals (content, priority) VALUES (?, ?)", (content, priority))
            goal_id = c.lastrowid
            conn.commit()
            conn.close()
            
            self.send_json({"status": "created", "id": goal_id, "content": content})
        
        elif path == '/goals/complete':
            goal_id = body.get('id')
            
            if not goal_id:
                self.send_json({"error": "No goal id provided"}, status=400)
                return
            
            conn = sqlite3.connect(str(NOVA_DB) if 'NOVA_DB' in dir() else "~/.nova/nova.db")
            c = conn.cursor()
            c.execute("UPDATE goals SET status = 'completed' WHERE id = ?", (goal_id,))
            conn.commit()
            conn.close()
            
            self.send_json({"status": "completed", "id": goal_id})
        
        elif path == '/emotion/update':
            event = body.get('event', '')
            changes = body.get('changes', {})
            
            if not event:
                self.send_json({"error": "No event provided"}, status=400)
                return
            
            new_state = update_emotion(event, changes)
            
            self.send_json({"status": "updated", "state": new_state})
        
        elif path == '/daemon/cycle':
            # Trigger exploration cycle
            try:
                from nova_daemon import run_exploration_cycle
                result = run_exploration_cycle()
                self.send_json({"status": "success", "result": result})
            except Exception as e:
                self.send_json({"status": "error", "message": str(e)}, status=500)
        
        else:
            self.send_json({"error": "Not found"}, status=404)
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


class APIServer:
    """Nova API Server."""
    
    def __init__(self, port=DEFAULT_PORT, host='0.0.0.0'):
        self.port = port
        self.host = host
        self.server = None
        self.thread = None
    
    def start(self):
        """Start the API server."""
        self.server = HTTPServer((self.host, self.port), NovaAPIHandler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        print(f"Nova API server running on http://{self.host}:{self.port}")
        print(f"Health check: http://{self.host}:{self.port}/health")
        return self
    
    def stop(self):
        """Stop the API server."""
        if self.server:
            self.server.shutdown()
            print("Nova API server stopped")
    
    def run_forever(self):
        """Run the server."""
        try:
            self.start()
            print("Press Ctrl+C to stop")
            while True:
                input()
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.stop()


def run_api_server(port=DEFAULT_PORT, host='0.0.0.0'):
    """Run the API server."""
    server = APIServer(port, host)
    server.run_forever()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Nova API Server")
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help='Port to run on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    
    args = parser.parse_args()
    
    run_api_server(args.port, args.host)
