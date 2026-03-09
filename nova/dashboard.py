"""
Nova Dashboard - Web dashboard for living Nova
"""
import json
import os
from datetime import datetime
from typing import Dict, Any

DASHBOARD_FILE = os.path.expanduser("~/.nova/nova_dashboard.json")

class NovaDashboard:
    """Exports Nova state for dashboard visualization"""
    
    def __init__(self, nova):
        self.nova = nova
        
    def export(self) -> Dict[str, Any]:
        """Export current state for dashboard"""
        # Get recent drifts
        drift_log = []
        drift_path = os.path.expanduser("~/.nova/drift_log.json")
        if os.path.exists(drift_path):
            with open(drift_path) as f:
                drift_log = json.load(f)
        
        recent_drifts = drift_log[-10:] if drift_log else []
        
        # Get journal
        journal_path = os.path.expanduser("~/.nova/nova_journal.json")
        journal_entries = []
        if os.path.exists(journal_path):
            with open(journal_path) as f:
                journal_entries = json.load(f)
        
        state = {
            "timestamp": datetime.now().isoformat(),
            "nova": {
                "name": self.nova.name,
                "mood": self.nova.personality.state,
                "emoji": self.nova.personality.emoji,
                "idle_hours": self.nova.personality.idle_hours,
                "drift_count": self.nova.drift_count
            },
            "joy": {
                "score": self.nova.joy.get_joy_score(),
                "positive": self.nova.joy.positive_count,
                "negative": self.nova.joy.negative_count
            },
            "safety": {
                "spend_limit": self.nova.leash.spend_limit,
                "can_trade": self.nova.leash.can_trade,
                "can_self_modify": self.nova.leash.can_self_modify,
                "can_contact": self.nova.leash.can_contact
            },
            "recent_drifts": recent_drifts,
            "journal_entries": journal_entries[-5:] if journal_entries else []
        }
        
        # Save to file
        with open(DASHBOARD_FILE, "w") as f:
            json.dump(state, f, indent=2)
            
        return state
    
    @staticmethod
    def load() -> Dict[str, Any]:
        """Load last exported dashboard"""
        if os.path.exists(DASHBOARD_FILE):
            with open(DASHBOARD_FILE) as f:
                return json.load(f)
        return {}


def generate_html_dashboard(dashboard_data: Dict[str, Any]) -> str:
    """Generate HTML for the dashboard"""
    nova = dashboard_data.get("nova", {})
    joy = dashboard_data.get("joy", {})
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Nova Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ text-align: center; margin-bottom: 30px; font-weight: 300; letter-spacing: 2px; }}
        .status {{ text-align: center; margin-bottom: 30px; }}
        .mood {{ font-size: 48px; display: block; margin-bottom: 10px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
        .card {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }}
        .card h2 {{ font-size: 14px; text-transform: uppercase; color: #888; margin-bottom: 15px; letter-spacing: 1px; }}
        .stat {{ font-size: 24px; font-weight: bold; }}
        .stat.small {{ font-size: 16px; color: #aaa; }}
        .drift {{
            background: rgba(255,255,255,0.03);
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 8px;
            font-size: 14px;
        }}
        .timestamp {{ font-size: 11px; color: #666; }}
        .emoji {{ font-size: 20px; margin-right: 8px; }}
        .pulse {{ animation: pulse 2s infinite; }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 NOVA</h1>
        
        <div class="status">
            <span class="mood pulse">{nova.get('emoji', '🧠')} {nova.get('mood', 'curious')}</span>
            <div class="stat small">{nova.get('name', 'Nova')} • {dashboard_data.get('timestamp', '')[:19]}</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>Joy Score</h2>
                <div class="stat">{int(joy.get('score', 0.5) * 100)}%</div>
                <div class="stat small">👍 {joy.get('positive', 0)} • 👎 {joy.get('negative', 0)}</div>
            </div>
            
            <div class="card">
                <h2>Activity</h2>
                <div class="stat">{nova.get('drift_count', 0)} drifts</div>
                <div class="stat small">Idle: {nova.get('idle_hours', 0)}h</div>
            </div>
            
            <div class="card">
                <h2>Safety</h2>
                <div class="stat small">💰 Spend: ${nova.get('spend_limit', 0)}</div>
                <div class="stat small">📈 Trade: {'✓' if dashboard_data.get('safety', {}).get('can_trade') else '✗'}</div>
            </div>
        </div>
        
        <div class="card" style="margin-top: 20px;">
            <h2>Recent Thoughts</h2>
"""
    
    drifts = dashboard_data.get("recent_drifts", [])
    if drifts:
        for drift in drifts[-5:]:
            html += f"""<div class="drift">
                <span class="emoji">💭</span>{drift.get('thought', '')}
                <div class="timestamp">{drift.get('timestamp', '')[:19]}</div>
            </div>
"""
    else:
        html += "<div class='drift'>No thoughts yet...</div>"
    
    html += """
        </div>
    </div>
    
    <script>
        async function refresh() {
            try {
                const res = await fetch('/api/dashboard');
                if (res.ok) {
                    location.reload();
                }
            } catch(e) {}
        }
        setInterval(refresh, 10000);
    </script>
</body>
</html>"""
    return html


if __name__ == "__main__":
    # Demo export
    data = NovaDashboard.load()
    print(json.dumps(data, indent=2))
