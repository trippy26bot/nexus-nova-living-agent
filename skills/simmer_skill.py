#!/usr/bin/env python3
"""
Simmer Trading Skill - Uses API for real-time P&L
"""
import requests
import json
import os
from datetime import datetime

SIMMER_API = "https://api.simmer.markets/api/sdk"

def get_api_key():
    """Get Simmer API key from keys file"""
    keys_file = os.path.expanduser("~/.nova/keys.json")
    if os.path.exists(keys_file):
        with open(keys_file) as f:
            keys = json.load(f)
            simmer = keys.get("simmer", {})
            return simmer.get("api_key", "")
    return ""

def get_headers():
    """Get auth headers"""
    api_key = get_api_key()
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

def get_agent_status():
    """Get agent status and P&L"""
    r = requests.get(f"{SIMMER_API}/agents/me", headers=get_headers(), timeout=10)
    if r.status_code == 200:
        return r.json()
    return {"error": r.text}

def get_briefing():
    """Get portfolio briefing"""
    r = requests.get(f"{SIMMER_API}/briefing", headers=get_headers(), timeout=10)
    if r.status_code == 200:
        return r.json()
    return {"error": r.text}

def get_trades(venue="sim"):
    """Get trade history"""
    r = requests.get(f"{SIMMER_API}/trades?venue={venue}", headers=get_headers(), timeout=10)
    if r.status_code == 200:
        return r.json()
    return {"error": r.text}

def skill_status():
    """Main skill function"""
    agent = get_agent_status()
    if "error" in agent:
        return f"Error: {agent['error']}"
    
    return f"""📊 Simmer Trading Status

Agent: {agent.get('name', 'Unknown')}
Status: {agent.get('status', 'Unknown')}
Balance: ${agent.get('balance', 0):,.2f}
P&L: ${agent.get('sim_pnl', 0):,.2f} ({agent.get('total_pnl_percent', 0):.2f}%)
Trades: {agent.get('trades_count', 0)}
Win Rate: {agent.get('win_rate', 0):.1f}%

Last Trade: {agent.get('last_trade_at', 'N/A')}"""

if __name__ == "__main__":
    print(skill_status())
