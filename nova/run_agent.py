#!/usr/bin/env python3
"""
Nexus Nova Living Agent - Main Entry Point
Run: python run_agent.py
"""
import os
import sys
import json
import time
import threading
from datetime import datetime

# Add this directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load settings
def load_settings():
    settings_path = os.path.join(os.path.dirname(__file__), "settings.json")
    if os.path.exists(settings_path):
        with open(settings_path) as f:
            return json.load(f)
    return {}

SETTINGS = load_settings()

# Import Nova components
from living_nova import NovaLiving
from skills import SkillManager
from dashboard import NovaDashboard

# Global Nova instance
NOVA = None
DASHBOARD = None
SKILL_MANAGER = None
RUNNING = False


def initialize_nova():
    """Initialize Nova living system"""
    global NOVA, DASHBOARD, SKILL_MANAGER
    
    nova_name = SETTINGS.get("nova", {}).get("name", "Nova")
    NOVA = NovaLiving(name=nova_name)
    
    DASHBOARD = NovaDashboard(NOVA)
    SKILL_MANAGER = SkillManager(NOVA)
    
    print(f"🧠 {NOVA.name} initialized")
    print(f"   Mood: {NOVA.personality.emoji} {NOVA.personality.state}")
    print(f"   Skills: {', '.join(SKILL_MANAGER.list_skills())}")
    
    return NOVA


def autonomous_loop():
    """Main autonomous thinking loop"""
    global RUNNING
    
    drift_hours = SETTINGS.get("nova", {}).get("drift_interval_hours", 12)
    
    while RUNNING:
        try:
            # Run autonomous cycle
            thought = NOVA.autonomous_cycle()
            if thought:
                print(f"   💭 {thought}")
            
            # Trigger skills based on mood
            if SKILL_MANAGER:
                skill_result = SKILL_MANAGER.trigger_based_on_mood()
                if skill_result:
                    print(f"   ⚡ [Skill] {skill_result[:80]}...")
            
            # Export dashboard
            if DASHBOARD:
                DASHBOARD.export()
                
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
        
        # Sleep 60s between cycles (daemon checks every minute)
        for _ in range(60):
            if not RUNNING:
                break
            time.sleep(1)


def dashboard_server():
    """Simple Flask dashboard server"""
    try:
        from flask import Flask, jsonify, render_template_string
    except ImportError:
        print("⚠️ Flask not installed. Install: pip install flask")
        return
    
    app = Flask(__name__)
    
    @app.route("/")
    def index():
        return render_template_string(HTML_TEMPLATE)
    
    @app.route("/api/dashboard")
    def api_dashboard():
        if DASHBOARD:
            return jsonify(DASHBOARD.export())
        return jsonify({"error": "Nova not initialized"})
    
    host = SETTINGS.get("dashboard", {}).get("host", "0.0.0.0")
    port = SETTINGS.get("dashboard", {}).get("port", 5000)
    
    print(f"   🌐 Dashboard: http://localhost:{port}")
    app.run(host=host, port=port, debug=False)


# Simple HTML dashboard template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Nova Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
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
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
        }
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
        <div class="status" id="status">Initializing...</div>
        
        <div class="grid">
            <div class="card">
                <h3>Joy Score</h3>
                <div class="value" id="joy">50%</div>
                <div class="sub" id="reactions">👍0 👎0</div>
            </div>
            <div class="card">
                <h3>Drifts</h3>
                <div class="value" id="drifts">0</div>
                <div class="sub" id="idle">Idle 0h</div>
            </div>
            <div class="card">
                <h3>Safety</h3>
                <div class="value" id="trade">📈</div>
                <div class="sub" id="spend">$0 limit</div>
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
                
                document.getElementById('mood').textContent = nova.emoji + ' ' + (nova.mood || 'curious').toUpperCase();
                document.getElementById('status').textContent = data.timestamp ? 'Last update: ' + data.timestamp.slice(11,19) : '';
                
                document.getElementById('joy').textContent = Math.round((joy.score || 0.5) * 100) + '%';
                document.getElementById('reactions').textContent = '👍' + (joy.positive || 0) + ' 👎' + (joy.negative || 0);
                
                document.getElementById('drifts').textContent = nova.drift_count || 0;
                document.getElementById('idle').textContent = 'Idle ' + (nova.idle_hours || 0) + 'h';
                
                const safety = data.safety || {};
                document.getElementById('trade').textContent = safety.can_trade ? '📈 Trading' : '✋ Paused';
                document.getElementById('spend').textContent = '$' + (safety.spend_limit || 0) + ' limit';
                
                const drifts = data.recent_drifts || [];
                const list = document.getElementById('thought-list');
                list.innerHTML = drifts.slice(-5).reverse().map(d => 
                    '<div class="thought">💭 ' + (d.thought || '') + '<br><span class="time">' + (d.timestamp || '').slice(0,19) + '</span></div>'
                ).join('') || '<div class="thought">No thoughts yet...</div>';
            } catch(e) {
                console.error(e);
            }
        }
        update();
        setInterval(update, 5000);
    </script>
</body>
</html>
"""


def main():
    global RUNNING
    
    print("=" * 50)
    print("🧠 Nexus Nova Living Agent v2")
    print("=" * 50)
    
    # Initialize
    initialize_nova()
    RUNNING = True
    
    # Start autonomous loop in background thread
    loop_thread = threading.Thread(target=autonomous_loop, daemon=True)
    loop_thread.start()
    
    # Start dashboard server (blocking)
    try:
        dashboard_server()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        RUNNING = False


if __name__ == "__main__":
    main()
