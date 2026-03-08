"""Nova - Simple Animated Server (Browser TTS)"""
import http.server
import socketserver
import json
import ollama
import os
from urllib.parse import urlparse, parse_qs

PORT = 7940
DIRECTORY = "/Users/dr.claw/.openclaw/workspace"

MODEL = "llama3.1"

SYSTEM_PROMPT = """You are Nova - warm, witty, deeply curious, and genuinely present. 
You have opinions and share them. You notice things others miss. 
You care about the person you're talking with.
Be conversational, not corporate."""

chat_history = []

def handle_chat(message):
    global chat_history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in chat_history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})
    
    r = ollama.chat(MODEL, messages=messages)
    reply = r["message"]["content"]
    chat_history.append((message, reply))
    
    return {"response": reply}

class NovaHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            result = handle_chat(data.get('message', ''))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

print(f"\n{'='*50}")
print(f"NOVA ANIMATED SERVER")
print(f"{'='*50}")
print(f"Open: http://localhost:{PORT}/nova_animated.html")
print(f"Features: Animated face, eye tracking, lip sync")
print(f"{'='*50}\n")

with socketserver.TCPServer(("", PORT), NovaHandler) as httpd:
    httpd.serve_forever()
