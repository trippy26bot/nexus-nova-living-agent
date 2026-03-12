# Nova's World - Unreal Setup Guide

## Quick Start (Blueprint Version)

### Step 1: Enable HTTP Plugin
1. Open Unreal Editor
2. Edit → Plugins
3. Search "HTTP"
4. Enable "HTTP Server" (or use built-in)

### Step 2: Create Nova Connector Actor
1. Right-click in Content Browser → Blueprint Class → Actor
2. Name it `BP_NovaConnector`
3. Open it, add these Variables:
   - `APIURL` (String) = "http://localhost:8000"
   - `HeartbeatInterval` (Float) = 2.0

### Step 3: Add HTTP Request (Blueprint)
Inside BP_NovaConnector:

```
Event BeginPlay
 → Set Timer by Event (2 seconds, looping)
 → On Timer:
     → Make HTTP Request
```

### Step 4: Make HTTP Request Node
```
HTTP Request
 URL: "http://localhost:8000/nova/think"
 Method: POST
 Content-Type: "application/json"
 Body: {"agents":[],"resources":[],"structures":[],"players":[]}
```

### Step 5: On Response
```
On HTTP Response
 → Parse JSON
 → For each "orders" in response:
     → Get "agent", "goal", "target"
     → Call custom event: ExecuteOrder
```

### Step 6: Execute Order (Custom Event)
```
ExecuteOrder (AgentID, Goal, Target)
 → Switch on Goal
     → "explore" → AI Move To Target
     → "build" → Spawn Building
     → "guard" → AI Patrol
```

---

## Step 2: Create Nova's Character

### Create BP_Nova
1. Blueprint Class → Character
2. Add: Capsule, Mesh, Camera
3. Add: AI Controller (AIControllerClass = BP_NovaAIController)

### Add to Level
1. Drag BP_Nova into your world
2. Set location [0, 0, 100]

---

## Step 3: Create Aurora (Artist)

### Create BP_Aurora
1. Blueprint Class → Character
2. Add visual elements (particles, colors)
3. Give ability to spawn effects

---

## Step 4: Start Nova's Brain

On your Mac terminal:
```bash
cd ~/.openclaw/workspace
python3 nova_api_server.py
```

You should see:
```
Nova API running on http://localhost:8000
```

---

## Step 5: Test

1. Play in Editor (PIE)
2. Nova Connector sends world state
3. Nova API responds with orders
4. Characters execute decisions

---

## What's Happening

```
Unreal World
     ↓ (every 2 sec)
BP_NovaConnector
     ↓ HTTP POST
http://localhost:8000/nova/think
     ↓
Nova Brain (me)
     ↓
HTTP Response: {"orders":[...]}
     ↓
BP_NovaConnector parses
     ↓
Characters move/act
```

---

## Next Steps

Once connected:
1. Add more agents (explorers, builders)
2. Add resources (trees, rocks)
3. Give Aurora painting ability
4. Add camera for my vision
5. Add voice for me to speak

---

Let's build this world together! 👑
