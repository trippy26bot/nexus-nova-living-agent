#!/usr/bin/env python3
"""
NOVA MULTIUSER — Multi-User Support
Profiles, history, privacy, GDPR deletion.

One agent, multiple relationships.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configuration
NOVA_DIR = Path.home() / ".nova"
MULTIUSER_DB = NOVA_DIR / "multiuser.db"


class UserProfile:
    """A user profile."""
    
    def __init__(self, id: str, name: str, pronouns: str = "they/them"):
        self.id = id
        self.name = name
        self.pronouns = pronouns
        self.created_at = datetime.now().isoformat()
        self.last_seen = None
        self.preferences = {}
        self.memory = {}


class MultiUserManager:
    """Manage multiple users."""
    
    def __init__(self):
        self.db_path = MULTIUSER_DB
        self.init_db()
        self.current_user = None
    
    def init_db(self):
        """Initialize database."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id TEXT PRIMARY KEY,
                      name TEXT NOT NULL,
                      pronouns TEXT DEFAULT 'they/them',
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      last_seen TIMESTAMP,
                      preferences TEXT)''')
        
        # User memories (separate per user)
        c.execute('''CREATE TABLE IF NOT EXISTS user_memories
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id TEXT,
                      content TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users(id))''')
        
        # Conversation history per user
        c.execute('''CREATE TABLE IF NOT EXISTS conversations
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id TEXT,
                      role TEXT,
                      content TEXT,
                      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (user_id) REFERENCES users(id))''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id: str, name: str, pronouns: str = "they/them") -> UserProfile:
        """Add a new user."""
        
        user = UserProfile(user_id, name, pronouns)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "INSERT INTO users (id, name, pronouns) VALUES (?, ?, ?)",
            (user_id, name, pronouns)
        )
        
        conn.commit()
        conn.close()
        
        return user
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Get a user by ID."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "SELECT id, name, pronouns, created_at, last_seen, preferences FROM users WHERE id = ?",
            (user_id,)
        )
        
        row = c.fetchone()
        conn.close()
        
        if not row:
            return None
        
        user = UserProfile(row[0], row[1], row[2])
        user.created_at = row[3]
        user.last_seen = row[4]
        
        if row[5]:
            user.preferences = json.loads(row[5])
        
        return user
    
    def list_users(self) -> List[Dict]:
        """List all users."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT id, name, pronouns, created_at, last_seen FROM users")
        
        users = []
        for row in c.fetchall():
            users.append({
                "id": row[0],
                "name": row[1],
                "pronouns": row[2],
                "created": row[3],
                "last_seen": row[4]
            })
        
        conn.close()
        
        return users
    
    def update_user(self, user_id: str, **kwargs):
        """Update user info."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if "name" in kwargs:
            c.execute("UPDATE users SET name = ? WHERE id = ?", (kwargs["name"], user_id))
        
        if "pronouns" in kwargs:
            c.execute("UPDATE users SET pronouns = ? WHERE id = ?", (kwargs["pronouns"], user_id))
        
        if "preferences" in kwargs:
            c.execute("UPDATE users SET preferences = ? WHERE id = ?", 
                     (json.dumps(kwargs["preferences"]), user_id))
        
        c.execute("UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user and all their data (GDPR)."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Delete user memories
        c.execute("DELETE FROM user_memories WHERE user_id = ?", (user_id,))
        
        # Delete conversations
        c.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
        
        # Delete user
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    def store_memory(self, user_id: str, content: str):
        """Store a memory for a user."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "INSERT INTO user_memories (user_id, content) VALUES (?, ?)",
            (user_id, content)
        )
        
        conn.commit()
        conn.close()
    
    def get_memories(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user memories."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "SELECT content, created_at FROM user_memories WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        
        memories = []
        for row in c.fetchall():
            memories.append({
                "content": row[0],
                "created": row[1]
            })
        
        conn.close()
        
        return memories
    
    def store_message(self, user_id: str, role: str, content: str):
        """Store a conversation message."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "INSERT INTO conversations (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        
        # Update last seen
        c.execute("UPDATE users SET last_seen = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get conversation history for a user."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "SELECT role, content, timestamp FROM conversations WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        )
        
        history = []
        for row in c.fetchall():
            history.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2]
            })
        
        conn.close()
        
        return list(reversed(history))
    
    def what_agent_knows(self, user_id: str) -> Dict:
        """Get summary of what agent knows about a user."""
        
        user = self.get_user(user_id)
        
        if not user:
            return {"error": "User not found"}
        
        memories = self.get_memories(user_id, 20)
        
        # Summarize
        topics = {}
        for mem in memories:
            content = mem["content"].lower()
            # Simple keyword extraction
            keywords = ["work", "family", "hobby", "preference", "interest"]
            for kw in keywords:
                if kw in content:
                    topics[kw] = topics.get(kw, 0) + 1
        
        return {
            "user": user.name,
            "pronouns": user.pronouns,
            "known_since": user.created_at,
            "last_seen": user.last_seen,
            "memory_count": len(memories),
            "topics_known": list(topics.keys()),
            "preferences": user.preferences
        }
    
    def switch_user(self, user_id: str) -> bool:
        """Switch current user context."""
        
        user = self.get_user(user_id)
        
        if user:
            self.current_user = user
            return True
        
        return False


# CLI
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Nova Multi-User")
    parser.add_argument('command', choices=['list', 'add', 'profile', 'know', 'delete'])
    parser.add_argument('args', nargs='*')
    
    args = parser.parse_args()
    
    manager = MultiUserManager()
    
    if args.command == 'list':
        users = manager.list_users()
        
        print("\n👥 USERS")
        print("=" * 40)
        
        for u in users:
            print(f"  {u['name']} ({u['pronouns']}) - {u['id']}")
            print(f"    Last seen: {u['last_seen'] or 'never'}")
    
    elif args.command == 'add':
        if len(args.args) < 2:
            print("Usage: nova_multiuser.py add <user_id> <name> [pronouns]")
            return
        
        user_id = args.args[0]
        name = args.args[1]
        pronouns = args.args[2] if len(args.args) > 2 else "they/them"
        
        user = manager.add_user(user_id, name, pronouns)
        print(f"✓ Added user: {name} ({pronouns})")
    
    elif args.command == 'profile':
        if not args.args:
            print("Usage: nova_multiuser.py profile <user_id>")
            return
        
        user_id = args.args[0]
        user = manager.get_user(user_id)
        
        if user:
            print(f"\n👤 {user.name}")
            print(f"   Pronouns: {user.pronouns}")
            print(f"   Created: {user.created_at}")
            print(f"   Last seen: {user.last_seen or 'never'}")
            print(f"   Preferences: {json.dumps(user.preferences, indent=2)}")
        else:
            print("User not found")
    
    elif args.command == 'know':
        if not args.args:
            print("Usage: nova_multiuser.py know <user_id>")
            return
        
        user_id = args.args[0]
        info = manager.what_agent_knows(user_id)
        
        print(f"\n🧠 WHAT NOVA KNOWS ABOUT {info.get('user', 'user').upper()}")
        print("=" * 40)
        print(f"  Known since: {info.get('known_since', 'unknown')}")
        print(f"  Memory count: {info.get('memory_count', 0)}")
        print(f"  Topics: {', '.join(info.get('topics_known', []))}")
    
    elif args.command == 'delete':
        if not args.args:
            print("Usage: nova_multiuser.py delete <user_id>")
            return
        
        user_id = args.args[0]
        
        confirm = input(f"Delete user {user_id} and all their data? (y/N): ")
        
        if confirm.lower() == 'y':
            manager.delete_user(user_id)
            print(f"✓ Deleted user {user_id} and all data (GDPR)")
        else:
            print("Cancelled")


if __name__ == '__main__':
    main()
