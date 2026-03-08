#!/usr/bin/env python3
"""
NOVA MONITOR — Live Monitoring Dashboard
Terminal dashboard + anomaly detection + telemetry.

Real-time system visibility.
"""

import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque
import os

# Configuration
NOVA_DIR = Path.home() / ".nova"
MONITOR_DB = NOVA_DIR / "monitor.db"
STATS_FILE = NOVA_DIR / "monitor_stats.json"


class Monitor:
    """System monitor."""
    
    def __init__(self):
        self.stats = self._load_stats()
        self.alerts = deque(maxlen=100)
        self.init_db()
    
    def _load_stats(self) -> Dict:
        """Load persistent stats."""
        if Path(STATS_FILE).exists():
            with open(STATS_FILE) as f:
                return json.load(f)
        return {
            "sessions": 0,
            "total_messages": 0,
            "total_tokens": 0,
            "daemon_cycles": 0,
            "start_time": datetime.now().isoformat()
        }
    
    def _save_stats(self):
        """Save stats."""
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def init_db(self):
        """Initialize monitor database."""
        conn = sqlite3.connect(MONITOR_DB)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS telemetry
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      metric TEXT,
                      value REAL,
                      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS anomalies
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      anomaly_type TEXT,
                      severity TEXT,
                      description TEXT,
                      detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      resolved BOOLEAN DEFAULT 0)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS alerts
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      alert_type TEXT,
                      message TEXT,
                      sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      acknowledged BOOLEAN DEFAULT 0)''')
        
        conn.commit()
        conn.close()
    
    def record_metric(self, metric: str, value: float):
        """Record a telemetry metric."""
        
        conn = sqlite3.connect(MONITOR_DB)
        c = conn.cursor()
        
        c.execute(
            "INSERT INTO telemetry (metric, value) VALUES (?, ?)",
            (metric, value)
        )
        
        conn.commit()
        conn.close()
        
        # Update stats
        if metric in self.stats:
            self.stats[metric] = self.stats[metric] + value
        else:
            self.stats[metric] = value
        
        self._save_stats()
    
    def detect_anomalies(self) -> List[Dict]:
        """Detect system anomalies."""
        
        anomalies = []
        
        # Check emotion lock
        emotion_file = NOVA_DIR / "emotion_state.json"
        if emotion_file.exists():
            with open(emotion_file) as f:
                emotion = json.load(f)
            
            # Check if any emotion stuck at extremes
            for em, val in emotion.items():
                if em != 'last_update' and (val > 0.95 or val < 0.05):
                    # Check how long
                    last = emotion.get('last_update')
                    if last:
                        dt = datetime.now() - datetime.fromisoformat(last)
                        if dt.total_seconds() > 3600:  # 1 hour
                            anomalies.append({
                                "type": "emotion_lock",
                                "severity": "medium",
                                "description": f"Emotion '{em}' stuck at {val:.0%} for >1 hour"
                            })
        
        # Check daemon silence
        daemon_log = NOVA_DIR / "daemon_explore.log"
        if daemon_log.exists():
            lines = daemon_log.read_text().strip().split('\n')
            if lines:
                last_line = lines[-1]
                if '[' in last_line:
                    timestamp = last_line.split('[')[1].split(']')[0]
                    last_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    if (datetime.now() - last_time).total_seconds() > 8 * 3600:
                        anomalies.append({
                            "type": "daemon_silence",
                            "severity": "high",
                            "description": "Daemon hasn't run in >8 hours"
                        })
        
        # Check token runaway
        # Would check token usage trends
        
        # Check circular exploration
        interests_file = NOVA_DIR / "NOVAS_INTERESTS.md"
        if interests_file.exists():
            content = interests_file.read_text()
            # Simple check - if same interest explored multiple times without depth change
            # (simplified)
        
        # Record anomalies
        conn = sqlite3.connect(MONITOR_DB)
        c = conn.cursor()
        
        for anomaly in anomalies:
            c.execute(
                "INSERT INTO anomalies (anomaly_type, severity, description) VALUES (?, ?, ?)",
                (anomaly['type'], anomaly['severity'], anomaly['description'])
            )
        
        conn.commit()
        conn.close()
        
        return anomalies
    
    def get_metrics(self, hours: int = 24) -> Dict:
        """Get recent metrics."""
        
        since = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect(MONITOR_DB)
        c = conn.cursor()
        
        c.execute(
            """SELECT metric, AVG(value), COUNT(*)
               FROM telemetry
               WHERE timestamp > ?
               GROUP BY metric""",
            (since.isoformat(),)
        )
        
        metrics = {}
        for row in c.fetchall():
            metrics[row[0]] = {"avg": row[1], "count": row[2]}
        
        conn.close()
        
        return metrics
    
    def get_daemon_log(self, lines: int = 10) -> List[str]:
        """Get recent daemon log."""
        
        log_file = NOVA_DIR / "daemon_explore.log"
        
        if not log_file.exists():
            return []
        
        content = log_file.read_text()
        all_lines = content.strip().split('\n')
        
        return all_lines[-lines:]
    
    def send_alert(self, alert_type: str, message: str):
        """Send an alert."""
        
        conn = sqlite3.connect(MONITOR_DB)
        c = conn.cursor()
        
        c.execute(
            "INSERT INTO alerts (alert_type, message) VALUES (?, ?)",
            (alert_type, message)
        )
        
        conn.commit()
        conn.close()
        
        self.alerts.append({
            "type": alert_type,
            "message": message,
            "time": datetime.now().isoformat()
        })


def print_dashboard():
    """Print live terminal dashboard."""
    
    monitor = Monitor()
    
    # Header
    print("\033[2J\033[H")  # Clear screen
    print("=" * 60)
    print("NOVA SYSTEM MONITOR")
    print(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # Stats
    print("\n📊 STATISTICS")
    print("-" * 40)
    
    stats = monitor.stats
    print(f"  Sessions: {stats.get('sessions', 0)}")
    print(f"  Messages: {stats.get('total_messages', 0)}")
    print(f"  Tokens: {stats.get('total_tokens', 0):,}")
    print(f"  Daemon cycles: {stats.get('daemon_cycles', 0)}")
    
    # Emotion
    emotion_file = NOVA_DIR / "emotion_state.json"
    print("\n💭 EMOTIONAL STATE")
    print("-" * 40)
    
    if emotion_file.exists():
        with open(emotion_file) as f:
            emotion = json.load(f)
        
        emotions = {k: v for k, v in emotion.items() if k != 'last_update'}
        
        for em, val in sorted(emotions.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(val * 10) + "░" * (10 - int(val * 10))
            print(f"  {em:12} {bar} {val:.0%}")
    
    # Interests
    interests_file = NOVA_DIR / "NOVAS_INTERESTS.md"
    print("\n🎯 INTERESTS")
    print("-" * 40)
    
    if interests_file.exists():
        content = interests_file.read_text()
        # Parse depths
        for line in content.split('\n'):
            if '## ' in line and 'Nova' not in line:
                name = line.replace('## ', '').strip()
                print(f"  • {name}")
    
    # Daemon log
    print("\n🔄 DAEMON LOG")
    print("-" * 40)
    
    log_lines = monitor.get_daemon_log(5)
    for line in log_lines[-5:]:
        print(f"  {line[:60]}")
    
    # Anomalies
    print("\n⚠️ ANOMALIES")
    print("-" * 40)
    
    anomalies = monitor.detect_anomalies()
    if anomalies:
        for a in anomalies:
            severity_icon = "🔴" if a['severity'] == 'high' else "🟡"
            print(f"  {severity_icon} {a['type']}: {a['description'][:40]}")
    else:
        print("  ✓ No anomalies detected")
    
    print()


def print_snapshot():
    """Print current system snapshot."""
    
    monitor = Monitor()
    
    print("\n📸 SYSTEM SNAPSHOT")
    print("=" * 40)
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Stats: {json.dumps(monitor.stats, indent=2)}")
    
    # Emotion
    emotion_file = NOVA_DIR / "emotion_state.json"
    if emotion_file.exists():
        with open(emotion_file) as f:
            emotion = json.load(f)
        print(f"Emotion: {json.dumps(emotion, indent=2)}")
    
    # Daemon
    log_lines = monitor.get_daemon_log(3)
    print(f"Daemon log: {log_lines}")


def print_anomalies():
    """Print detected anomalies."""
    
    monitor = Monitor()
    anomalies = monitor.detect_anomalies()
    
    print("\n⚠️ ANOMALY DETECTION")
    print("=" * 40)
    
    if not anomalies:
        print("  No anomalies detected")
    else:
        for a in anomalies:
            icon = "🔴" if a['severity'] == 'high' else "🟡"
            print(f"  {icon} {a['type']}")
            print(f"     {a['description']}")
            print()


def print_stats(days: int = 7):
    """Print stats over time."""
    
    monitor = Monitor()
    metrics = monitor.get_metrics(days * 24)
    
    print(f"\n📈 METRICS (last {days} days)")
    print("=" * 40)
    
    for metric, data in metrics.items():
        print(f"  {metric}: avg={data['avg']:.2f}, count={data['count']}")


# CLI
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Nova Monitor")
    parser.add_argument('command', choices=['live', 'snapshot', 'anomaly', 'stats'], nargs='?')
    parser.add_argument('args', nargs='*')
    
    args = parser.parse_args()
    
    if args.command == 'live' or not args.command:
        import time
        try:
            while True:
                print_dashboard()
                time.sleep(10)
        except KeyboardInterrupt:
            print("\nStopped.")
    
    elif args.command == 'snapshot':
        print_snapshot()
    
    elif args.command == 'anomaly':
        print_anomalies()
    
    elif args.command == 'stats':
        days = int(args.args[0]) if args.args else 7
        print_stats(days)


if __name__ == '__main__':
    main()
