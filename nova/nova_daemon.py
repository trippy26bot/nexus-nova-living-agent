#!/usr/bin/env python3
"""
NOVA Background Daemon
Runs NOVA's thinking cycle continuously in the background
"""
import os
import sys
import time
import json
import signal
from datetime import datetime

# Add workspace to path
WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
sys.path.insert(0, WORKSPACE)

# Config
CYCLE_INTERVAL = int(os.getenv("NOVA_CYCLE_SECONDS", 60))
LOG_FILE = os.path.expanduser("~/.nova/logs/daemon.log")
PID_FILE = os.path.expanduser("~/.nova/daemon.pid")
STATE_FILE = os.path.expanduser("~/.nova/daemon_state.json")

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}")

def save_pid():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def load_pid():
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            return int(f.read().strip())
    return None

def run_cycle():
    """Run one NOVA thinking cycle"""
    try:
        # Import NOVA systems
        from nova.core.brain_orchestrator import BrainOrchestrator
        from nova.core.emotion_engine import EmotionEngine
        from nova.memory.nova_memory import NovaMemory
        
        # Initialize systems
        orchestrator = BrainOrchestrator()
        emotions = EmotionEngine()
        memory = NovaMemory()
        
        # Simple context
        context = {
            'price_change': 0,
            'volatility': 1,
            'sentiment': 0,
            'liquidity': 5,
            'risk_level': 0.3
        }
        
        # Run brain decision
        decision = orchestrator.process(context, {})
        
        # Update emotions
        emotions.update("success")
        
        # Store in memory
        memory.store_short("last_cycle", {
            "time": datetime.now().isoformat(),
            "decision": decision
        })
        
        log(f"Cycle complete. Decision: {decision.get('action', 'HOLD')}")
        return True
        
    except Exception as e:
        log(f"Cycle error: {e}")
        return False

def daemon_loop():
    """Continuous background loop"""
    save_pid()
    log("NOVA daemon started")
    
    while True:
        run_cycle()
        time.sleep(CYCLE_INTERVAL)

def status():
    """Check daemon status"""
    pid = load_pid()
    if pid:
        try:
            os.kill(pid, 0)
            print(f"NOVA daemon running with PID {pid}")
        except:
            print("Daemon not running (stale PID)")
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
    else:
        print("NOVA daemon not running")

def stop():
    """Stop daemon"""
    pid = load_pid()
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"Stopped daemon PID {pid}")
        except:
            print("Could not stop daemon")
    else:
        print("No daemon running")

def start():
    """Start daemon in background"""
    pid = load_pid()
    if pid:
        try:
            os.kill(pid, 0)
            print(f"Daemon already running PID {pid}")
            return
        except:
            pass
    
    log("Starting NOVA daemon...")
    pid = os.fork()
    if pid == 0:
        # Child process
        daemon_loop()
    else:
        # Parent
        print(f"Started daemon with PID {pid}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "start":
        start()
    elif cmd == "stop":
        stop()
    elif cmd == "status":
        status()
    elif cmd == "run":
        # Run one cycle
        run_cycle()
    else:
        print("Usage: nova_daemon.py [start|stop|status|run]")
