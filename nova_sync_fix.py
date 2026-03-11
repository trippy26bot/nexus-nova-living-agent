#!/usr/bin/env python3
"""
Nova Session Sync Fix v3 - Extracts real conversation content and syncs across channels.
Simple version that works with current session format.
"""
import json
import os
from datetime import datetime
from pathlib import Path

SHARED_SESSION_PATH = os.path.expanduser("~/.nova/memory/SHARED_SESSION.json")
SESSIONS_DIR = os.path.expanduser("~/.openclaw/agents/main/sessions")

def get_latest_session_file():
    """Find the most recently modified session file."""
    sessions = Path(SESSIONS_DIR)
    if not sessions.exists():
        return None
    
    files = list(sessions.glob("*.jsonl"))
    files = [f for f in files if ".lock" not in str(f) and ".deleted" not in str(f)]
    if not files:
        return None
    
    return max(files, key=lambda f: f.stat().st_mtime)

def extract_recent_conversation(session_file, max_messages=8):
    """Extract recent messages - simpler approach."""
    try:
        with open(session_file, 'r') as f:
            lines = f.readlines()
        
        messages = []
        for line in reversed(lines[-80:]):
            try:
                data = json.loads(line)
                if data.get('type') == 'message':
                    role = data.get('message', {}).get('role')
                    content = data.get('message', {}).get('content', [])
                    
                    if role in ['user', 'assistant'] and content:
                        for item in content:
                            if item.get('type') == 'text' and item.get('text'):
                                text = item.get('text', '')
                                # Skip metadata blocks, tool results
                                if 'message_id' not in text and len(text) > 3:
                                    if role == 'user':
                                        messages.append(('user', text[:150]))
                                    elif role == 'assistant' and len(text) > 20:
                                        messages.append(('assistant', text[:100]))
                                        break
            except:
                continue
        
        return messages[-max_messages:] if messages else []
    except:
        return []

def generate_summary(messages):
    """Generate summary from conversation."""
    if not messages:
        return {'summary': 'Session active', 'topics': ['general'], 'last_user': ''}
    
    # Last user message
    last_user = ""
    for role, text in reversed(messages):
        if role == 'user':
            last_user = text[:100]
            break
    
    # Topics
    all_text = " ".join([t for _, t in messages]).lower()
    keywords = []
    important = ['mic', 'microphone', 'voice', 'memory', 'github', 'trade', 
                 'polymarket', 'aurora', 'art', 'body', 'agent', 'api', 
                 'telegram', 'dashboard', 'sync', 'fix', 'weather', 'bitcoin']
    for word in important:
        if word in all_text:
            keywords.append(word)
    
    topics = list(set(keywords))[:5] if keywords else ['conversation']
    
    summary = f"Last: {last_user}" if last_user else "Active session"
    return {'summary': summary, 'topics': topics, 'last_user': last_user}

def detect_channel(session_file, messages):
    """Detect channel."""
    fname = str(session_file).lower()
    if 'telegram' in fname:
        return 'telegram'
    all_text = " ".join([t for _, t in messages]).lower()
    if 'telegram' in all_text:
        return 'telegram'
    return 'dashboard'

def sync_session():
    """Main sync."""
    os.makedirs(os.path.dirname(SHARED_SESSION_PATH), exist_ok=True)
    
    existing = {}
    if os.path.exists(SHARED_SESSION_PATH):
        try:
            existing = json.load(open(SHARED_SESSION_PATH))
        except:
            existing = {}
    
    session_file = get_latest_session_file()
    
    if session_file:
        messages = extract_recent_conversation(session_file)
        analysis = generate_summary(messages)
        channel = detect_channel(session_file, messages)
        
        channel_history = existing.get("channel_history", {})
        channel_history[channel] = {
            "last_active": datetime.now().isoformat(),
            "last_summary": analysis['summary'][:50],
            "message_count": channel_history.get(channel, {}).get("message_count", 0) + 1
        }
        
        existing.update({
            "last_updated": datetime.now().isoformat(),
            "last_channel": channel,
            "open_channels": existing.get("open_channels", ["dashboard", "telegram", "voice"]),
            "conversation_summary": analysis['summary'],
            "recent_topics": analysis['topics'],
            "pending_tasks": existing.get("pending_tasks", []),
            "last_user_message": analysis['last_user'],
            "channel_history": channel_history
        })
    else:
        existing["last_updated"] = datetime.now().isoformat()
    
    json.dump(existing, open(SHARED_SESSION_PATH, 'w'), indent=2)
    print(f"✅ Synced: {analysis['summary'][:60]} | ch:{channel}")

if __name__ == "__main__":
    sync_session()
