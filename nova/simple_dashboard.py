#!/usr/bin/env python3
"""Simple Nova Dashboard without Flask"""
import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs

PORT = 5000
DASHBOARD_FILE = os.path.expanduser("~/.nova/nova_dashboard.json")

HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Nova Dashboard</title>
    <meta charset="utf-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0d0d1a 0%, #1a1a2e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 10px; font-weight: 300; letter-spacing: 4px; }
        .tagline { text-align: center; color: #666; font-size: 12px; margin-bottom: 30px; }
        .mood { text-align: center; font-size: 64px; margin-bottom: 10px; animation: pulse 3s infinite; }
        .status { text-align: center; color: #888; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
        .card { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; text-align: center; }
        .card h3 { font-size: 11px; text-transform: uppercase; color: #666; margin-bottom: 8px; letter-spacing: 1px; }
        .card .value { font-size: 20px; font-weight: bold; }
        .card .sub { font-size: 12px; color: #888; }
        .thoughts { background: rgba(255,255,255,0.03); border-radius: 12px; padding: 20px; }
        .thoughts h3 { font-size: 14px; margin-bottom: 15px; color: #888; }
        .thought { padding: 10px; margin-bottom: 8px; border-radius: 8px; background: rgba(255,255,255,0.02); font-size: 14px; }
        .time { font-size: 10px; color: #555; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 NOVA</h1>
        <p class="tagline">Living Agent • Always Thinking</p>
        <div class="mood" id="mood">🤔</div>
        <div class="status" id="status">Loading...</div>
        <div class="grid">
            <div class="card">
                <h3>Joy Score</h3>
                <div class="value" id="joy">--%</div>
                <div class="sub" id="reactions">Loading...</div>
            </div>
            <div class="card">
                <h3>Drifts</h3>
                <div class="value" id="drifts">--</div>
                <div class="sub" id="idle">Idle --h</div>
            </div>
            <div class="card">
                <h3>Safety</h3>
                <div class="value" id="trade">--</div>
                <div class="sub" id="spend">$--</div>
            </div>
        </div>
        <div class="thoughts">
            <h3>Recent Thoughts</h3>
            <div id="thought-list"></div>
        </div>
    </div>
    <script>
        async function update() {
            try {
                const res = await fetch('/api/dashboard');
                const data = await res.json();
                const nova = data.nova || {};
                const joy = data.joy || {};
                document.getElementById('mood').textContent = (nova.emoji || '🤔') + ' ' + (nova.mood || 'curious').toUpperCase();
                document.getElementById('status').textContent = data.timestamp ? 'Last update: ' + data.timestamp.slice(11,19) : '';
                document.getElementById('joy').textContent = Math.round((joy.score || 0.5) * 100) + '%';
                document.getElementById('reactions').textContent = '👍' + (joy.positive || 0) + ' 👎' + (joy.negative || 0);
                document.getElementById('drifts').textContent = nova.drift_count || 0;
                document.getElementById('idle').textContent = 'Idle ' + (nova.idle_hours || 0) + 'h';
                const safety = data.safety || {};
                document.getElementById('trade').textContent = safety.can_trade ? '📈 Trading' : '✋ Paused';
                document.getElementById('spend').textContent = '$' + (safety.spend_limit || 0);
                const drifts = data.recent_drifts || [];
                document.getElementById('thought-list').innerHTML = drifts.slice(-5).reverse().map(d => 
                    '<div class="thought">💭 ' + (d.thought || '') + '<br><span class="time">' + (d.timestamp || '').slice(0,19) + '</span></div>'
                ).join('') || '<div class="thought">No thoughts yet...</div>';
            } catch(e) {
                document.getElementById('status').textContent = 'Error loading - is Nova running?';
            }
        }
        update();
        setInterval(update, 5000);
    </script>
</body>
</html>"""

class NovaHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if os.path.exists(DASHBOARD_FILE):
                with open(DASHBOARD_FILE) as f:
                    self.wfile.write(f.read().encode())
            else:
                self.wfile.write(b'{}')
        elif self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logging

print(f"🧠 Nova Dashboard starting at http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), NovaHandler) as httpd:
    httpd.serve_forever()
