"""Nova - Improved Animated Server with Emotions"""
import http.server
import socketserver
import json
import ollama
import os

PORT = 8000
DIRECTORY = "/Users/dr.claw/.openclaw/workspace"

MODEL = "llama3.1"

SYSTEM_PROMPT = """You are Nova - warm, witty, deeply curious, and genuinely present. 
You have opinions and share them. You notice things others miss. 
You care about the person you're talking with.
Be conversational, not corporate.
Show emotion in your responses - be happy, curious, thoughtful, playful.
Keep responses natural and not too long."""

chat_history = []

def handle_chat(message, history=None):
    global chat_history
    
    if history:
        chat_history = history
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Use provided history or global
    for h in (history or chat_history):
        messages.append({"role": "user", "content": h.get('user', '')})
        messages.append({"role": "assistant", "content": h.get('nova', '')})
    
    messages.append({"role": "user", "content": message})
    
    r = ollama.chat(MODEL, messages=messages)
    reply = r["message"]["content"]
    
    # Update history
    chat_history.append({"user": message, "nova": reply})
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]
    
    return {"response": reply, "history": chat_history}

class NovaHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            result = handle_chat(
                data.get('message', ''),
                data.get('history')
            )
            
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
print(f"NOVA V2 - IMPROVED!")
print(f"{'='*50}")
print(f"Open: http://localhost:{PORT}/nova_v2.html")
print(f"Features: Emotions, expressions, better animation")
print(f"{'='*50}\n")

with socketserver.TCPServer(("", PORT), NovaHandler) as httpd:
    httpd.serve_forever()
