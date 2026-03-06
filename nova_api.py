#!/usr/bin/env python3
"""
nova_api.py — REST API Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HTTP API for external integrations and the web dashboard.

Endpoints:
 /health — health check
 /chat — send message, get response
 /memory — query/store memories
 /goals — list/add/complete goals
 /emotion — get emotional state
 /identity — GET/POST IDENTITY.md
 /daemon — trigger exploration cycle
 /supervisor — run task via supervisor

Run:
 python3 nova_api.py --port 8080
"""

import json, os, sqlite3, urllib.parse
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

NOVA_DIR = Path.home() / ".nova"
PORT = int(os.environ.get("NOVA_PORT", "8080"))


def load_json(path, default=None):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            pass
    return default or {}


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


class NovaAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def get_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length).decode())
        return {}

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/health":
            self.send_json({"status": "ok", "time": datetime.now().isoformat()})

        elif path == "/emotion":
            state_file = NOVA_DIR / "emotion_state.json"
            state = load_json(state_file, {})
            emotions = {k: v for k, v in state.items() if k != "last_update"}
            dominant = max(emotions, key=emotions.get) if emotions else "neutral"
            self.send_json({"state": state, "dominant": dominant, "dominance": emotions.get(dominant, 0)})

        elif path == "/memory":
            db_file = NOVA_DIR / "nova.db"
            if db_file.exists():
                conn = sqlite3.connect(db_file)
                c = conn.cursor()
                c.execute("SELECT content, memory_type, importance, created_at FROM memories ORDER BY created_at DESC LIMIT 20")
                memories = [{"content": r[0], "type": r[1], "importance": r[2], "created": r[3]} for r in c.fetchall()]
                conn.close()
                self.send_json({"memories": memories})
            else:
                self.send_json({"memories": []})

        elif path == "/goals":
            db_file = NOVA_DIR / "nova.db"
            if db_file.exists():
                conn = sqlite3.connect(db_file)
                c = conn.cursor()
                c.execute("SELECT id, content, priority, status FROM goals ORDER BY priority DESC")
                goals = [{"id": r[0], "content": r[1], "priority": r[2], "status": r[3]} for r in c.fetchall()]
                conn.close()
                self.send_json({"goals": goals})
            else:
                self.send_json({"goals": []})

        elif path == "/identity":
            self.handle_get_identity()

        else:
            self.send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        body = self.get_body()

        if path == "/chat":
            message = body.get("message", "")
            if not message:
                self.send_json({"error": "message required"}, status=400)
                return
            
            # Try LLM
            try:
                from nova_providers import get_provider
                provider = get_provider()
                if provider and provider.available():
                    resp = provider.complete(message, max_tokens=1000)
                    if resp.success:
                        self.send_json({"response": resp.text, "provider": provider.name})
                        return
            except:
                pass
            
            self.send_json({"response": "[No API configured]", "error": "Set ANTHROPIC_API_KEY or MINIMAX_API_KEY"})

        elif path == "/memory":
            content = body.get("content", "")
            if not content:
                self.send_json({"error": "content required"}, status=400)
                return
            
            db_file = NOVA_DIR / "nova.db"
            db_file.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS memories
                (id INTEGER PRIMARY KEY, content TEXT, memory_type TEXT, importance INTEGER, created_at TEXT)""")
            c.execute("INSERT INTO memories (content, memory_type, importance, created_at) VALUES (?, ?, ?, ?)",
                      (content, body.get("type", "episodic"), body.get("importance", 5), datetime.now().isoformat()))
            conn.commit()
            conn.close()
            self.send_json({"status": "stored"})

        elif path == "/goals":
            content = body.get("content", "")
            if not content:
                self.send_json({"error": "content required"}, status=400)
                return
            
            db_file = NOVA_DIR / "nova.db"
            db_file.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS goals
                (id INTEGER PRIMARY KEY, content TEXT, priority INTEGER, status TEXT)""")
            c.execute("INSERT INTO goals (content, priority, status) VALUES (?, ?, ?)",
                      (content, body.get("priority", 5), "pending"))
            goal_id = c.lastrowid
            conn.commit()
            conn.close()
            self.send_json({"status": "created", "id": goal_id})

        elif path == "/identity":
            self.handle_post_identity(body)

        elif path == "/daemon":
            try:
                from nova_daemon import run_cycle
                result = run_cycle()
                self.send_json({"status": "success", "result": result})
            except Exception as e:
                self.send_json({"status": "error", "message": str(e)})

        elif path == "/supervisor":
            goal = body.get("goal", "")
            if not goal:
                self.send_json({"error": "goal required"}, status=400)
                return
            try:
                from nova_supervisor import Supervisor
                sv = Supervisor()
                result = sv.execute(goal)
                self.send_json({
                    "answer": result.answer,
                    "tasks": result.tasks_run,
                    "confidence": result.confidence
                })
                sv.close()
            except Exception as e:
                self.send_json({"error": str(e)})

        else:
            self.send_json({"error": "Not found"}, status=404)

    def handle_get_identity(self):
        """GET /identity — return current IDENTITY.md content."""
        identity_path = NOVA_DIR / "IDENTITY.md"
        repo_identity = Path("IDENTITY.md")

        for path in [identity_path, repo_identity]:
            if path.exists():
                try:
                    content = path.read_text(encoding="utf-8")
                    self.send_json({"content": content, "path": str(path)})
                    return
                except:
                    continue
        
        self.send_json({"error": "No IDENTITY.md found. Run: nova identity new"}, status=404)

    def handle_post_identity(self, body):
        """POST /identity — save new IDENTITY.md content."""
        content = body.get("content", "").strip()
        if not content or len(content) < 50:
            self.send_json({"error": "content required (min 50 chars)"}, status=400)

        NOVA_DIR.mkdir(parents=True, exist_ok=True)
        identity_path = NOVA_DIR / "IDENTITY.md"

        try:
            identity_path.write_text(content, encoding="utf-8")
            self.send_json({"saved": True, "path": str(identity_path)})
        except Exception as e:
            self.send_json({"error": str(e)}, status=500)


def run_server(port=PORT):
    server = HTTPServer(("", port), NovaAPIHandler)
    print(f"Nova API running on http://localhost:{port}")
    print(f"Endpoints: /health /chat /memory /goals /emotion /identity /daemon /supervisor")
    server.serve_forever()


if __name__ == "__main__":
    import sys
    port = PORT
    if "--port" in sys.argv:
        i = sys.argv.index("--port")
        port = int(sys.argv[i+1]) if i+1 < len(sys.argv) else PORT
    run_server(port)
