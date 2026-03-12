#!/usr/bin/env python3
"""
Nova Command Center API
FastAPI server for real-time dashboard
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime

from nova.command_center.telemetry import get_telemetry
from nova.command_center.event_stream import get_event_stream


app = FastAPI(title="Nova Command Center", version="1.0")

# Get instances
telemetry = get_telemetry()
event_stream = get_event_stream()

# Track WebSocket connections
websocket_connections = []


@app.get("/")
async def index():
    """Main dashboard page"""
    return HTMLResponse(DASHBOARD_HTML)


@app.get("/api/status")
async def api_status():
    """Get Nova's current status"""
    counters = telemetry.get_all_counters()
    event_stats = event_stream.get_stats()
    
    return {
        "status": "online",
        "uptime": time.time() - event_stats["uptime"],
        "timestamp": datetime.now().isoformat(),
        "events": {
            "total": counters.get("heartbeat", 0),
            "agents_spawned": counters.get("agent_spawn", 0),
            "agents_completed": counters.get("agent_complete", 0),
            "goals_updated": counters.get("goal_update", 0),
            "memories_stored": counters.get("memory_store", 0),
            "cognition_thoughts": counters.get("cognition_thought", 0),
            "errors": counters.get("error", 0)
        },
        "event_stream": event_stats
    }


@app.get("/api/events")
async def api_events(limit: int = 100, event_type: Optional[str] = None):
    """Get recent events"""
    return event_stream.get_recent(limit)


@app.get("/api/events/heartbeats")
async def api_heartbeats(limit: int = 50):
    """Get heartbeat events"""
    return event_stream.get_by_type("heartbeat", limit)


@app.get("/api/events/agents")
async def api_agent_events(limit: int = 50):
    """Get agent events"""
    return event_stream.get_by_type("agent_spawn", limit) + event_stream.get_by_type("agent_complete", limit)


@app.get("/api/events/goals")
async def api_goal_events(limit: int = 50):
    """Get goal events"""
    return event_stream.get_by_type("goal_update", limit)


@app.get("/api/events/cognition")
async def api_cognition_events(limit: int = 50):
    """Get cognition events"""
    return event_stream.get_by_type("cognition_thought", limit)


@app.get("/api/telemetry")
async def api_telemetry():
    """Get detailed telemetry"""
    return telemetry.get_stats()


@app.get("/api/counters")
async def api_counters():
    """Get event counters"""
    return telemetry.get_all_counters()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        # Send initial state
        await websocket.send_json({
            "type": "connected",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and send updates
        while True:
            # Get recent events
            events = event_stream.get_recent(10)
            if events:
                await websocket.send_json({
                    "type": "events",
                    "data": events
                })
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)


# Background task to broadcast events
import asyncio

async def broadcast_events():
    """Broadcast events to all WebSocket connections"""
    while True:
        if websocket_connections:
            events = event_stream.get_recent(5)
            if events:
                for ws in websocket_connections[:]:
                    try:
                        await ws.send_json({
                            "type": "events",
                            "data": events
                        })
                    except:
                        pass
        await asyncio.sleep(0.5)


@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(broadcast_events())


# Dashboard HTML
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nova Command Center</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 20px 30px;
            border-bottom: 1px solid #2a2a4e;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 1.5rem;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .header h1 span {
            color: #9d4edd;
        }
        
        .status-badge {
            background: #2d4a3e;
            color: #4ade80;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
        }
        
        .container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .card {
            background: #12121a;
            border-radius: 12px;
            border: 1px solid #2a2a4e;
            overflow: hidden;
        }
        
        .card-header {
            background: #1a1a2e;
            padding: 15px 20px;
            border-bottom: 1px solid #2a2a4e;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card-body {
            padding: 20px;
        }
        
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        
        .stat {
            text-align: center;
            padding: 15px;
            background: #1a1a2e;
            border-radius: 8px;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #9d4edd;
        }
        
        .stat-label {
            font-size: 0.8rem;
            color: #888;
            margin-top: 5px;
        }
        
        .event-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .event-item {
            padding: 10px 15px;
            border-bottom: 1px solid #1a1a2e;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.9rem;
        }
        
        .event-item:last-child {
            border-bottom: none;
        }
        
        .event-time {
            color: #666;
            font-size: 0.8rem;
            min-width: 80px;
        }
        
        .event-type {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .event-type.heartbeat { background: #2d4a3e; color: #4ade80; }
        .event-type.agent { background: #3d2d4a; color: #a78bfa; }
        .event-type.goal { background: #4a3d2d; color: #fbbf24; }
        .event-type.cognition { background: #2d3d4a; color: #38bdf8; }
        .event-type.error { background: #4a2d2d; color: #f87171; }
        
        .pulse {
            width: 10px;
            height: 10px;
            background: #4ade80;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        .timestamp {
            color: #666;
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1><span>👑</span> NOVA <span>Command Center</span></h1>
        <div class="status-badge"><div class="pulse" style="display:inline-block;vertical-align:middle;margin-right:8px;"></div> Online</div>
    </div>
    
    <div class="container">
        <div class="card">
            <div class="card-header">🫀 System Health</div>
            <div class="card-body">
                <div class="stat-grid">
                    <div class="stat">
                        <div class="stat-value" id="heartbeats">0</div>
                        <div class="stat-label">Heartbeats</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="uptime">0s</div>
                        <div class="stat-label">Uptime</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">🤖 Agent Activity</div>
            <div class="card-body">
                <div class="stat-grid">
                    <div class="stat">
                        <div class="stat-value" id="agents-spawned">0</div>
                        <div class="stat-label">Spawned</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="agents-completed">0</div>
                        <div class="stat-label">Completed</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">🎯 Goals</div>
            <div class="card-body">
                <div class="stat-grid">
                    <div class="stat">
                        <div class="stat-value" id="goals-updated">0</div>
                        <div class="stat-label">Updates</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="cognition-thoughts">0</div>
                        <div class="stat-label">Thoughts</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">📚 Memory</div>
            <div class="card-body">
                <div class="stat-grid">
                    <div class="stat">
                        <div class="stat-value" id="memories-stored">0</div>
                        <div class="stat-label">Stored</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="errors">0</div>
                        <div class="stat-label">Errors</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card full-width">
            <div class="card-header">🔴 Live Events</div>
            <div class="card-body">
                <div class="event-list" id="event-list">
                    <div class="event-item">
                        <span class="timestamp">Waiting for events...</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // WebSocket connection
        let ws = null;
        
        function connect() {
            ws = new WebSocket('ws://' + location.host + '/ws');
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.type === 'connected') {
                    console.log('Connected to Nova');
                } else if (data.type === 'events') {
                    updateEvents(data.data);
                }
            };
            
            ws.onclose = function() {
                setTimeout(connect, 3000);
            };
        }
        
        // Polling fallback
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();
                
                document.getElementById('heartbeats').textContent = status.events.total || 0;
                document.getElementById('uptime').textContent = formatUptime(status.uptime);
                document.getElementById('agents-spawned').textContent = status.events.agents_spawned || 0;
                document.getElementById('agents-completed').textContent = status.events.agents_completed || 0;
                document.getElementById('goals-updated').textContent = status.events.goals_updated || 0;
                document.getElementById('cognition-thoughts').textContent = status.events.cognition_thoughts || 0;
                document.getElementById('memories-stored').textContent = status.events.memories_stored || 0;
                document.getElementById('errors').textContent = status.events.errors || 0;
            } catch (e) {
                console.error('Status update failed:', e);
            }
        }
        
        function formatUptime(seconds) {
            if (seconds < 60) return Math.floor(seconds) + 's';
            if (seconds < 3600) return Math.floor(seconds / 60) + 'm';
            return Math.floor(seconds / 3600) + 'h';
        }
        
        function updateEvents(events) {
            const list = document.getElementById('event-list');
            if (!events || events.length === 0) return;
            
            let html = '';
            events.slice().reverse().forEach(event => {
                const time = new Date(event.timestamp).toLocaleTimeString();
                const type = event.event;
                const typeClass = getEventClass(type);
                const data = JSON.stringify(event.data).substring(0, 50);
                
                html += `
                    <div class="event-item">
                        <span class="event-time">${time}</span>
                        <span class="event-type ${typeClass}">${type}</span>
                        <span>${data}</span>
                    </div>
                `;
            });
            
            list.innerHTML = html;
        }
        
        function getEventClass(type) {
            if (type.includes('heartbeat')) return 'heartbeat';
            if (type.includes('agent')) return 'agent';
            if (type.includes('goal')) return 'goal';
            if (type.includes('cognition') || type.includes('thought')) return 'cognition';
            if (type.includes('error')) return 'error';
            return '';
        }
        
        // Start
        connect();
        updateStatus();
        setInterval(updateStatus, 5000);
    </script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
