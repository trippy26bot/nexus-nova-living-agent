#!/usr/bin/env python3
"""
Nova Voice UI Bridge - Direct agent invocation
"""

import http.server
import socketserver
import json
import subprocess
import os

PORT = 8769
GATEWAY = "http://127.0.0.1:18789"

class NovaHandler(http.server.BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                message = data.get('message', '')
                
                if message:
                    # Send to OpenClaw gateway API
                    import urllib.request
                    import urllib.parse
                    
                    req_data = json.dumps({
                        'channel': 'telegram',
                        'text': message
                    }).encode('utf-8')
                    
                    req = urllib.request.Request(
                        f'{GATEWAY}/api/message',
                        data=req_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    try:
                        with urllib.request.urlopen(req, timeout=60) as response:
                            result = response.read().decode()
                            response_data = json.loads(result)
                            response_text = response_data.get('text', '') or "Message sent"
                    except Exception as e:
                        response_text = f"Error: {str(e)}"
                    
                    response = {'response': response_text, 'status': 'ok'}
                    
                    if result.returncode == 0:
                        try:
                            response_data = json.loads(result.stdout)
                            # Extract the response text
                            response_text = response_data.get('text', '') or response_data.get('response', '')
                        except:
                            response_text = result.stdout
                    else:
                        response_text = "I'm here. Let's talk."
                    
                    response = {'response': response_text, 'status': 'ok'}
                else:
                    response = {'response': 'No message received', 'status': 'error'}
                    
            except subprocess.TimeoutExpired:
                response = {'response': "Let me think about that...", 'status': 'timeout'}
            except Exception as e:
                response = {'response': str(e), 'status': 'error'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

# Allow port reuse
class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def run_server():
    with ReusableTCPServer(("", PORT), NovaHandler) as httpd:
        print(f"🌟 Nova Voice UI: http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
