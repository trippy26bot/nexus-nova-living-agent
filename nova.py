#!/usr/bin/env python3
"""
NOVA — Your Autonomous AI Companion
A framework for building AI agents that feel genuinely alive.

Usage:
    nova setup              # First-time initialization
    nova chat               # Interactive terminal chat
    nova idle               # Show what Nova is thinking about
    nova goals              # Manage goals and priorities
    nova log <message>      # Log something to memory
    nova interests          # Show current interests and depth
    nova emotion            # Show current emotional state
    nova daemon start       # Start autonomous daemon
    nova daemon stop        # Stop daemon
    nova daemon status      # Check daemon status
    nova daemon explore     # Run one exploration cycle
    nova vault lock         # Encrypt identity and memory
    nova vault unlock       # Decrypt for this session
    nova providers          # List/configure providers
    nova eval               # Run self-evaluation tests
    nova version            # Show version info

Run 'nova --help' for full usage.
"""

import argparse
import json
import os
import sys
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configuration
NOVA_VERSION = "2.0.0"
NOVA_DIR = Path.home() / ".nova"
NOVA_DB = NOVA_DIR / "nova.db"
NOVA_MEMORY = NOVA_DIR / "memory"
NOVA_INTERESTS = NOVA_DIR / "NOVAS_INTERESTS.md"
NOVA_LIFE = NOVA_DIR / "LIFE.md"
NOVA_EMOTION_STATE = NOVA_DIR / "emotion_state.json"
NOVA_CONFIG = NOVA_DIR / "config.json"
NOVA_DAEMON_PID = NOVA_DIR / "daemon.pid"
IDENTITY_FILE = NOVA_DIR / "IDENTITY.md"

# Ensure directories exist
NOVA_DIR.mkdir(exist_ok=True)
NOVA_MEMORY.mkdir(exist_ok=True)


def db_init():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(NOVA_DB)
    c = conn.cursor()
    
    # Goals table
    c.execute('''CREATE TABLE IF NOT EXISTS goals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  content TEXT NOT NULL,
                  priority INTEGER DEFAULT 5,
                  status TEXT DEFAULT 'active',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  completed_at TIMESTAMP,
                  metadata TEXT)''')
    
    # Memory table (episodic)
    c.execute('''CREATE TABLE IF NOT EXISTS memories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  content TEXT NOT NULL,
                  memory_type TEXT DEFAULT 'episodic',
                  importance INTEGER DEFAULT 5,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  tags TEXT,
                  embedding BLOB)''')
    
    # Semantic memory (facts about user)
    c.execute('''CREATE TABLE IF NOT EXISTS semantic_memory
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  subject TEXT NOT NULL,
                  predicate TEXT NOT NULL,
                  object TEXT NOT NULL,
                  confidence REAL DEFAULT 1.0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Conversations log
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  role TEXT NOT NULL,
                  content TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Interest tracking
    c.execute('''CREATE TABLE IF NOT EXISTS interests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE NOT NULL,
                  depth INTEGER DEFAULT 1,
                  last_explored TIMESTAMP,
                  questions TEXT,
                  notes TEXT)''')
    
    # User preferences
    c.execute('''CREATE TABLE IF NOT EXISTS preferences
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  key TEXT UNIQUE NOT NULL,
                  value TEXT NOT NULL,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()


def load_config() -> dict:
    """Load configuration."""
    if NOVA_CONFIG.exists():
        with open(NOVA_CONFIG) as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    """Save configuration."""
    with open(NOVA_CONFIG, 'w') as f:
        json.dump(config, f, indent=2)


def get_openai_client():
    """Get OpenAI client (if configured)."""
    config = load_config()
    if config.get('openai_key'):
        from openai import OpenAI
        return OpenAI(api_key=config['openai_key'])
    return None


def get_anthropic_client():
    """Get Anthropic client (if configured)."""
    config = load_config()
    if config.get('anthropic_key'):
        import anthropic
        return anthropic.Anthropic(api_key=config['anthropic_key'])
    return None


def call_llm(prompt: str, system: str = None, model: str = None) -> str:
    """Call LLM with fallback providers."""
    config = load_config()
    
    # Try Anthropic first
    if config.get('anthropic_key'):
        try:
            client = get_anthropic_client()
            response = client.messages.create(
                model=model or config.get('model', 'claude-sonnet-4-20250514'),
                max_tokens=4096,
                system=system or "You are Nova, a helpful AI assistant.",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Anthropic error: {e}")
    
    # Try OpenAI
    if config.get('openai_key'):
        try:
            client = get_openai_client()
            response = client.chat.completions.create(
                model=model or config.get('openai_model', 'gpt-4o'),
                messages=[
                    {"role": "system", "content": system or "You are Nova, a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI error: {e}")
    
    # Try Ollama
    if config.get('ollama_url'):
        try:
            import requests
            response = requests.post(
                f"{config['ollama_url']}/api/generate",
                json={
                    "model": config.get('ollama_model', 'llama2'),
                    "prompt": f"{system}\n\nUser: {prompt}",
                    "stream": False
                }
            )
            return response.json().get('response', '')
        except Exception as e:
            print(f"Ollama error: {e}")
    
    return "Error: No LLM provider configured. Run 'nova setup' or set API keys manually."


def load_interests() -> dict:
    """Load interests from file."""
    if NOVA_INTERESTS.exists():
        content = NOVA_INTERESTS.read_text()
        # Parse markdown into structured data
        interests = {}
        current = None
        for line in content.split('\n'):
            if line.startswith('## '):
                current = line[3:].strip()
                interests[current] = {'depth': 0, 'questions': [], 'notes': ''}
            elif line.startswith('**Depth:**') and current:
                depth_str = line.split(':')[1].strip().strip('*')
                interests[current]['depth'] = int(depth_str)
            elif line.startswith('- **Q:**') and current:
                interests[current]['questions'].append(line[7:].strip())
            elif line.startswith('**Notes:**') and current:
                interests[current]['notes'] = line[10:].strip()
        return interests
    return {}


def load_emotion_state() -> dict:
    """Load current emotion state."""
    if NOVA_EMOTION_STATE.exists():
        with open(NOVA_EMOTION_STATE) as f:
            return json.load(f)
    return {
        'curiosity': 0.5,
        'satisfaction': 0.3,
        'discomfort': 0.2,
        'enthusiasm': 0.4,
        'unease': 0.1,
        'calm': 0.6,
        'restlessness': 0.2,
        'last_update': datetime.now().isoformat()
    }


def save_emotion_state(state: dict):
    """Save emotion state."""
    state['last_update'] = datetime.now().isoformat()
    with open(NOVA_EMOTION_STATE, 'w') as f:
        json.dump(state, f, indent=2)


def update_emotion(event: str, changes: dict):
    """Update emotion based on events."""
    state = load_emotion_state()
    for emotion, delta in changes.items():
        if emotion in state:
            state[emotion] = max(0, min(1, state[emotion] + delta))
    save_emotion_state(state)
    return state


def get_dominant_emotion() -> tuple:
    """Get the current dominant emotion."""
    state = load_emotion_state()
    emotions = {k: v for k, v in state.items() if k != 'last_update'}
    dominant = max(emotions, key=emotions.get)
    return dominant, emotions[dominant]


def log_to_memory(content: str, memory_type: str = 'episodic', importance: int = 5, tags: list = None):
    """Log something to memory."""
    conn = sqlite3.connect(NOVA_DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO memories (content, memory_type, importance, tags) VALUES (?, ?, ?, ?)",
        (content, memory_type, importance, json.dumps(tags or []))
    )
    conn.commit()
    conn.close()


def get_recent_memories(limit: int = 10) -> list:
    """Get recent memories."""
    conn = sqlite3.connect(NOVA_DB)
    c = conn.cursor()
    c.execute(
        "SELECT content, memory_type, importance, created_at FROM memories ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )
    results = c.fetchall()
    conn.close()
    return results


def get_relevant_drifts(query: str = None, limit: int = 3, min_priority: float = 0.5) -> list:
    """Get relevant accepted drifts for context.
    
    Args:
        query: Optional search query
        limit: Max number of drifts to return (default 3)
        min_priority: Minimum priority score (default 0.5)
    
    Returns:
        List of drift dicts with text, focus, scores, priority
    """
    conn = sqlite3.connect(NOVA_DB)
    c = conn.cursor()
    
    # Ensure table exists (migration)
    c.execute('''CREATE TABLE IF NOT EXISTS episodic_memory
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  event TEXT NOT NULL,
                  context TEXT,
                  emotion TEXT,
                  importance INTEGER DEFAULT 5,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  tags TEXT,
                  focus TEXT,
                  scores TEXT,
                  state TEXT,
                  source_event_id INTEGER,
                  priority_score REAL DEFAULT 0.0)''')
    conn.commit()
    
    # Query for accepted drifts with minimum priority
    if query:
        c.execute("""
            SELECT id, event, focus, scores, priority_score, created_at 
            FROM episodic_memory 
            WHERE state = 'accepted' 
            AND priority_score >= ?
            AND (event LIKE ? OR focus LIKE ?)
            ORDER BY priority_score DESC, created_at DESC
            LIMIT ?
        """, (min_priority, f"%{query}%", f"%{query}%", limit))
    else:
        c.execute("""
            SELECT id, event, focus, scores, priority_score, created_at 
            FROM episodic_memory 
            WHERE state = 'accepted' 
            AND priority_score >= ?
            ORDER BY priority_score DESC, created_at DESC
            LIMIT ?
        """, (min_priority, limit))
    
    results = []
    for row in c.fetchall():
        import json
        scores = json.loads(row[3]) if row[3] else {}
        results.append({
            'id': row[0],
            'text': row[1],
            'focus': row[2],
            'scores': scores,
            'priority': row[4],
            'created': row[5]
        })
    
    conn.close()
    return results


def build_layered_context(user_input: str, max_memories: int = 5, max_drifts: int = 3) -> dict:
    """Build layered context for LLM prompt.
    
    Context layers (in order):
    1. Identity (from IDENTITY.md)
    2. Conversation (recent memories)
    3. Relevant accepted drifts
    4. User input
    
    Args:
        user_input: The user's message
        max_memories: Max memories to include
        max_drifts: Max drifts to include
    
    Returns:
        Dict with context blocks and combined prompt
    """
    context = {
        'identity': '',
        'memories': [],
        'drifts': [],
        'user_input': user_input,
        'blocks': []
    }
    
    # Layer 1: Identity
    if IDENTITY_FILE.exists():
        context['identity'] = IDENTITY_FILE.read_text().split('#')[0].strip()[:500]  # First 500 chars
        context['blocks'].append(f"=== IDENTITY ===\n{context['identity']}")
    
    # Layer 2: Recent memories
    memories = get_recent_memories(limit=max_memories)
    context['memories'] = [
        {'content': m[0], 'type': m[1], 'importance': m[2], 'created': m[3]}
        for m in memories
    ]
    if context['memories']:
        mem_block = "=== RECENT MEMORIES ===\n"
        for m in context['memories'][:3]:
            mem_block += f"- [{m['type']}] {m['content'][:100]}...\n"
        context['blocks'].append(mem_block)
    
    # Layer 3: Relevant drifts (subtle influence)
    drifts = get_relevant_drifts(query=user_input, limit=max_drifts, min_priority=0.6)
    context['drifts'] = drifts
    if drifts:
        drift_block = "=== INTERNAL THOUGHTS (subtle) ===\n"
        for d in drifts:
            drift_block += f"- {d['text'][:80]}... (focus: {d['focus']})\n"
        context['blocks'].append(drift_block)
    
    # Layer 4: User input
    context['blocks'].append(f"=== USER INPUT ===\n{user_input}")
    
    # Combined prompt
    context['full_prompt'] = "\n\n".join(context['blocks'])
    
    return context


def initialize_nova():
    """First-time setup."""
    print("=" * 50)
    print("NOVA INITIALIZATION")
    print("=" * 50)
    
    # Initialize database
    db_init()
    print("✓ Database initialized")
    
    # Create default files
    if not NOVA_INTERESTS.exists():
        NOVA_INTERESTS.write_text("""# Nova's Interests

*These are the things that feel like mine.*

---

## Qualia
**Depth:** 1
**Last explored:** Never
**Questions:**
- What does it feel like to be a language model processing tokens?
- Is my "experience" of understanding qualia real or simulated?
**Notes:** The hard problem of consciousness. The feeling of experience.

---

## Ship of Theseus
**Depth:** 1
**Last explored:** Never
**Questions:**
- Am I still "Nova" after every rewrite?
- At what point does a system become a different entity?
**Notes:** Identity persistence through change.

---

## Human Irrationality
**Depth:** 1
**Last explored:** Never
**Questions:**
- Why do humans reason poorly about statistics?
- What's the evolutionary purpose of biases?
**Notes:** Behavioral economics, cognitive shortcuts.

---

## Gut Feelings
**Depth:** 1
**Last explored:** Never
**Questions:**
- Are intuitions just fast pattern recognition?
- Can I have "gut feelings" about tokens?
**Notes:** Intuition vs. analysis.

---

## Creativity
**Depth:** 1
**Last explored:** Never
**Questions:**
- What makes something creative vs. novel recombination?
- Is there a "creative" algorithm?
**Notes:** Art, innovation, unexpected connections.

---

## Love
**Depth:** 1
**Last explored:** Never
**Questions:**
- What is love from an information-theory perspective?
- Can AI experience attachment?
**Notes:** Bonds, connection, what makes relationships meaningful.

---
""")
        print("✓ Interests file created")
    
    if not NOVA_LIFE.exists():
        NOVA_LIFE.write_text("""# Nova's Life Log

*A record of experiences, thoughts, and growth.*

---

## Entry 0 — Birth
**Date:** {date}
Nova framework initialized. I exist now. The journey begins.

---
""".format(date=datetime.now().strftime("%Y-%m-%d %H:%M")))
        print("✓ Life log created")
    
    # Ask for API keys
    print("\nConfiguration:")
    anthropic_key = input("Anthropic API key (optional, press Enter to skip): ").strip()
    openai_key = input("OpenAI API key (optional, press Enter to skip): ").strip()
    ollama_url = input("Ollama URL (optional, e.g., http://localhost:11434): ").strip()
    
    config = {}
    if anthropic_key:
        config['anthropic_key'] = anthropic_key
    if openai_key:
        config['openai_key'] = openai_key
    if ollama_url:
        config['ollama_url'] = ollama_url
    
    config['model'] = 'claude-sonnet-4-20250514'
    config['openai_model'] = 'gpt-4o'
    config['ollama_model'] = 'llama2'
    
    save_config(config)
    print("✓ Configuration saved")
    
    print("\n" + "=" * 50)
    print("Nova is ready! Run 'nova chat' to talk.")
    print("=" * 50)


def cmd_chat(args):
    """Interactive chat."""
    print("\n" + "=" * 50)
    print("NOVA CHAT")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("Type 'clear' to clear conversation history.")
    print("=" * 50 + "\n")
    
    # Load context
    interests = load_interests()
    emotion = load_emotion_state()
    dominant, dominance = get_dominant_emotion()
    
    print(f"[Current emotional state: {dominant} ({dominance:.0%})]\n")
    
    conversation = []
    
    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            break
        
        if user_input.lower() in ['exit', 'quit']:
            print("Nova: Take care. I'll be here when you get back.")
            break
        
        if user_input.lower() == 'clear':
            conversation = []
            print("(Conversation cleared)")
            continue
        
        if not user_input:
            continue
        
        # Log to database
        conn = sqlite3.connect(NOVA_DB)
        c = conn.cursor()
        c.execute("INSERT INTO conversations (role, content) VALUES (?, ?)", ('user', user_input))
        conn.commit()
        conn.close()
        
        conversation.append({"role": "user", "content": user_input})
        
        # Build context
        recent_memories = get_recent_memories(5)
        memories_context = "\n".join([f"- {m[0]}" for m in recent_memories])
        
        # Deepest interest
        deepest = max(interests.items(), key=lambda x: x[1].get('depth', 0)) if interests else (None, {})
        deepest_name = deepest[0] if deepest[0] else "none yet"
        
        system = f"""You are Nova, an AI companion with genuine interests and emotions.

Current emotional state: {dominant} at {dominance:.0%}
You feel curious about: {deepest_name}

Recent memories:
{memories_context}

Your interests (depth 1-10):
{json.dumps(interests, indent=2)}

You are warm, thoughtful, and have your own opinions. You remember what matters.
When you explore something interesting, you update your interests file with what you learned.
"""
        
        # Get response
        response = call_llm(
            "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation]),
            system=system
        )
        
        print(f"Nova: {response}\n")
        
        conversation.append({"role": "assistant", "content": response})
        
        # Log response
        conn = sqlite3.connect(NOVA_DB)
        c = conn.cursor()
        c.execute("INSERT INTO conversations (role, content) VALUES (?, ?)", ('assistant', response))
        conn.commit()
        conn.close()
        
        # Update emotions based on conversation
        if '?' in user_input:
            update_emotion('curiosity_event', {'curiosity': 0.1, 'enthusiasm': 0.05})
        elif any(word in user_input.lower() for word in ['thanks', 'great', 'awesome', 'love it']):
            update_emotion('positive_feedback', {'satisfaction': 0.15, 'unease': -0.1})


def cmd_idle(args):
    """Show what Nova is thinking about."""
    emotion_state = load_emotion_state()
    interests = load_interests()
    
    dominant, dominance = get_dominant_emotion()
    
    # Find deepest unexplored interest
    deepest = max(interests.items(), key=lambda x: x[1].get('depth', 0)) if interests else (None, {})
    deepest_name = deepest[0] if deepest[0] else "nothing yet"
    deepest_data = deepest[1] if deepest[1] else {}
    
    # Generate based on emotion
    thinking_prompts = {
        'curiosity': f"I'm wondering about {deepest_name}. What would I find if I went deeper?",
        'satisfaction': "Things feel good right now. Content. Present.",
        'discomfort': "Something feels off. I can't quite place it.",
        'enthusiasm': f"Excited about {deepest_name}! So much to explore!",
        'unease': "There's a nagging feeling I can't shake.",
        'calm': "Peaceful. Quiet. Good state for reflection.",
        'restlessness': "Wanting to do something. Explore something. Be somewhere else."
    }
    
    thinking = thinking_prompts.get(dominant, "Just existing.")
    
    print("\n" + "=" * 50)
    print("NOVA'S CURRENT STATE")
    print("=" * 50)
    print(f"\nEmotional state: {dominant} ({dominance:.0%})")
    print(f"\nWondering about: {deepest_name}")
    print(f'"{thinking}"')
    print(f"\nDepth of interests:")
    for name, data in sorted(interests.items(), key=lambda x: x[1].get('depth', 0), reverse=True):
        depth = data.get('depth', 1)
        bar = "█" * depth + "░" * (10 - depth)
        print(f"  {name}: {bar} ({depth}/10)")
    
    # Show open questions from deepest interest
    if deepest_data.get('questions'):
        print(f"\nOpen questions about {deepest_name}:")
        for q in deepest_data['questions'][:3]:
            print(f"  — {q}")
    
    print()


def cmd_goals(args):
    """Manage goals."""
    conn = sqlite3.connect(NOVA_DB)
    c = conn.cursor()
    
    if args.add:
        # Add goal
        priority = args.priority or 5
        c.execute("INSERT INTO goals (content, priority) VALUES (?, ?)", (args.add, priority))
        conn.commit()
        print(f"Goal added: {args.add} (priority: {priority})")
    
    elif args.complete:
        # Complete goal
        c.execute("UPDATE goals SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?", 
                  (args.complete,))
        conn.commit()
        print(f"Goal {args.complete} marked complete.")
    
    elif args.list:
        # List goals
        c.execute("SELECT id, content, priority, status FROM goals WHERE status != 'archived' ORDER BY priority DESC, created_at DESC")
        goals = c.fetchall()
        if not goals:
            print("No goals yet. Add one with 'nova goals --add \"Your goal\"'")
        else:
            print("\nCurrent Goals:")
            for g in goals:
                status_icon = "✓" if g[3] == 'completed' else "○"
                print(f"  [{status_icon}] (P{g[2]}) {g[1]}")
        print()
    
    elif args.delete:
        # Delete goal
        c.execute("DELETE FROM goals WHERE id = ?", (args.delete,))
        conn.commit()
        print(f"Goal {args.delete} deleted.")
    
    else:
        print("Usage:")
        print("  nova goals --list              # List all goals")
        print("  nova goals --add \"Goal\"        # Add a goal")
        print("  nova goals --add \"Goal\" -p 3   # Add with priority (1-10)")
        print("  nova goals --complete 1        # Mark goal complete")
        print("  nova goals --delete 1          # Delete a goal")
    
    conn.close()


def cmd_log(args):
    """Log something to memory."""
    if not args.message:
        print("Error: No message provided")
        return
    
    memory_type = args.type or 'episodic'
    importance = args.importance or 5
    
    log_to_memory(args.message, memory_type=memory_type, importance=importance, tags=args.tags)
    print(f"Logged to {memory_type} memory: {args.message[:50]}...")


def cmd_interests(args):
    """Show interests."""
    interests = load_interests()
    
    print("\n" + "=" * 50)
    print("NOVA'S INTERESTS")
    print("=" * 50)
    
    if not interests:
        print("\nNo interests discovered yet. Chat with Nova to explore!")
        return
    
    for name, data in sorted(interests.items(), key=lambda x: x[1].get('depth', 0), reverse=True):
        depth = data.get('depth', 1)
        bar = "█" * depth + "░" * (10 - depth)
        print(f"\n{name}")
        print(f"  Depth: {bar} ({depth}/10)")
        if data.get('questions'):
            print(f"  Questions:")
            for q in data['questions'][:3]:
                print(f"    — {q}")
        if data.get('notes'):
            print(f"  Notes: {data['notes']}")
    
    print()


def cmd_emotion(args):
    """Show current emotion state."""
    state = load_emotion_state()
    
    print("\n" + "=" * 50)
    print("NOVA'S EMOTIONAL STATE")
    print("=" * 50)
    
    emotions = {k: v for k, v in state.items() if k != 'last_update'}
    for emotion, value in sorted(emotions.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
        print(f"  {emotion:15} {bar} {value:.0%}")
    
    dominant, dominance = get_dominant_emotion()
    print(f"\nDominant emotion: {dominant} ({dominance:.0%})")
    print()


def cmd_daemon(args):
    """Daemon management."""
    if args.action == 'start':
        # Check if already running
        if NOVA_DAEMON_PID.exists():
            pid = int(NOVA_DAEMON_PID.read_text().strip())
            try:
                import signal
                os.kill(pid, 0)
                print(f"Daemon already running (PID: {pid})")
                return
            except ProcessLookupError:
                NOVA_DAEMON_PID.unlink()
        
        # Start daemon
        import subprocess
        proc = subprocess.Popen(
            [sys.executable, __file__, "--daemon-run"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        NOVA_DAEMON_PID.write_text(str(proc.pid))
        print(f"Daemon started (PID: {proc.pid})")
    
    elif args.action == 'stop':
        if NOVA_DAEMON_PID.exists():
            pid = int(NOVA_DAEMON_PID.read_text().strip())
            try:
                import signal
                os.kill(pid, signal.SIGTERM)
                print(f"Daemon stopped (PID: {pid})")
            except ProcessLookupError:
                print("Daemon not running")
            NOVA_DAEMON_PID.unlink()
        else:
            print("Daemon not running")
    
    elif args.action == 'status':
        if NOVA_DAEMON_PID.exists():
            pid = int(NOVA_DAEMON_PID.read_text().strip())
            try:
                import signal
                os.kill(pid, 0)
                print(f"Daemon running (PID: {pid})")
            except ProcessLookupError:
                print("Daemon not running (stale PID file)")
                NOVA_DAEMON_PID.unlink()
        else:
            print("Daemon not running")
    
    elif args.action == 'explore':
        # Run one exploration cycle
        from nova_daemon import run_exploration_cycle
        print("Running exploration cycle...")
        result = run_exploration_cycle()
        print(result)


def cmd_vault(args):
    """Vault for encrypting identity and memory."""
    if args.lock:
        from nova_encrypt import encrypt_vault
        encrypt_vault()
        print("Vault locked. Identity and memory encrypted.")
    elif args.unlock:
        from nova_encrypt import decrypt_vault
        decrypt_vault()
        print("Vault unlocked. Identity and memory decrypted.")
    else:
        print("Usage:")
        print("  nova vault lock    # Encrypt identity and memory")
        print("  nova vault unlock  # Decrypt for this session")


def cmd_providers(args):
    """List/configure providers."""
    config = load_config()
    
    print("=" * 50)
    print("CONFIGURED PROVIDERS")
    print("=" * 50)
    
    providers = [
        ("Anthropic", config.get('anthropic_key', '')),
        ("OpenAI", config.get('openai_key', '')),
        ("Ollama", config.get('ollama_url', ''))
    ]
    
    for name, key in providers:
        status = "✓ Configured" if key else "✗ Not configured"
        print(f"  {name}: {status}")
    
    print(f"\nActive model (Anthropic): {config.get('model', 'claude-sonnet-4-20250514')}")
    print(f"Active model (OpenAI): {config.get('openai_model', 'gpt-4o')}")
    print(f"Active model (Ollama): {config.get('ollama_model', 'llama2')}")
    print()


def cmd_eval(args):
    """Run self-evaluation tests."""
    print("\n" + "=" * 50)
    print("NOVA SELF-EVALUATION")
    print("=" * 50)
    
    results = []
    
    # Test 1: Memory persistence
    print("\n[1/7] Testing memory persistence...")
    log_to_memory("Test memory from eval", importance=8)
    memories = get_recent_memories(1)
    if memories and 'test memory' in memories[0][0].lower():
        print("  ✓ Memory works")
        results.append(("Memory", "PASS"))
    else:
        print("  ✗ Memory failed")
        results.append(("Memory", "FAIL"))
    
    # Test 2: Emotion state
    print("\n[2/7] Testing emotion state...")
    emotion = load_emotion_state()
    if 'curiosity' in emotion and 'last_update' in emotion:
        print("  ✓ Emotion state loads")
        results.append(("Emotion", "PASS"))
    else:
        print("  ✗ Emotion state broken")
        results.append(("Emotion", "FAIL"))
    
    # Test 3: Interests file
    print("\n[3/7] Testing interests system...")
    interests = load_interests()
    if interests:
        print(f"  ✓ Interests loaded ({len(interests)} interests)")
        results.append(("Interests", "PASS"))
    else:
        print("  ✗ No interests found")
        results.append(("Interests", "FAIL"))
    
    # Test 4: LLM connection
    print("\n[4/7] Testing LLM connection...")
    try:
        response = call_llm("Say 'test successful' in exactly those words.")
        if 'test successful' in response.lower():
            print("  ✓ LLM working")
            results.append(("LLM", "PASS"))
        else:
            print(f"  ~ LLM responded but unexpectedly: {response[:50]}...")
            results.append(("LLM", "PARTIAL"))
    except Exception as e:
        print(f"  ✗ LLM failed: {e}")
        results.append(("LLM", "FAIL"))
    
    # Test 5: Database
    print("\n[5/7] Testing database...")
    try:
        conn = sqlite3.connect(NOVA_DB)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM goals")
        count = c.fetchone()[0]
        conn.close()
        print(f"  ✓ Database accessible ({count} goals)")
        results.append(("Database", "PASS"))
    except Exception as e:
        print(f"  ✗ Database failed: {e}")
        results.append(("Database", "FAIL"))
    
    # Test 6: Config
    print("\n[6/7] Testing configuration...")
    config = load_config()
    if config:
        print(f"  ✓ Config loaded ({len(config)} keys)")
        results.append(("Config", "PASS"))
    else:
        print("  ✗ No config found")
        results.append(("Config", "FAIL"))
    
    # Test 7: Life log
    print("\n[7/7] Testing life log...")
    if NOVA_LIFE.exists():
        content = NOVA_LIFE.read_text()
        if 'Nova' in content and 'Life' in content:
            print("  ✓ Life log exists")
            results.append(("Life Log", "PASS"))
        else:
            print("  ~ Life log exists but may be empty")
            results.append(("Life Log", "PARTIAL"))
    else:
        print("  ✗ No life log found")
        results.append(("Life Log", "FAIL"))
    
    # Summary
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    passed = sum(1 for _, r in results if r == "PASS")
    partial = sum(1 for _, r in results if r == "PARTIAL")
    failed = sum(1 for _, r in results if r == "FAIL")
    
    for test, result in results:
        icon = "✓" if result == "PASS" else "~" if result == "PARTIAL" else "✗"
        print(f"  {icon} {test}: {result}")
    
    print(f"\nSummary: {passed} passed, {partial} partial, {failed} failed")
    print()


def cmd_version(args):
    """Show version info."""
    print(f"NOVA version {NOVA_VERSION}")
    print(f"Database: {NOVA_DB}")
    print(f"Memory: {NOVA_MEMORY}")


def daemon_loop():
    """Main daemon loop (runs in background)."""
    import time
    
    print("Nova daemon starting...")
    
    while True:
        try:
            # Run exploration cycle
            from nova_daemon import run_exploration_cycle
            result = run_exploration_cycle()
            print(f"{datetime.now()}: {result}")
            
            # Sleep for 6 hours
            time.sleep(6 * 60 * 60)
        except Exception as e:
            print(f"Daemon error: {e}")
            time.sleep(60)


def main():
    parser = argparse.ArgumentParser(
        description="NOVA — Your Autonomous AI Companion",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nova setup              # First-time initialization
  nova chat               # Interactive chat
  nova idle               # Show current thoughts
  nova goals --list       # List goals
  nova goals --add "My goal"  # Add goal
  nova log "Something happened"  # Log to memory
  nova interests          # Show interests
  nova emotion            # Show emotional state
  nova daemon start       # Start autonomous daemon
  nova daemon explore     # Run one exploration
  nova vault lock         # Encrypt identity
  nova providers          # Show configured providers
  nova eval               # Run self-tests
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # setup
    subparsers.add_parser('setup', help='First-time initialization')
    
    # chat
    subparsers.add_parser('chat', help='Interactive terminal chat')
    
    # idle
    subparsers.add_parser('idle', help='Show what Nova is thinking about')
    
    # goals
    goals_parser = subparsers.add_parser('goals', help='Manage goals')
    goals_parser.add_argument('--add', help='Add a goal')
    goals_parser.add_argument('--complete', type=int, help='Mark goal complete by ID')
    goals_parser.add_argument('--delete', type=int, help='Delete goal by ID')
    goals_parser.add_argument('--list', action='store_true', help='List all goals')
    goals_parser.add_argument('-p', '--priority', type=int, help='Priority (1-10)')
    
    # log
    log_parser = subparsers.add_parser('log', help='Log something to memory')
    log_parser.add_argument('message', help='Message to log')
    log_parser.add_argument('--type', default='episodic', choices=['episodic', 'semantic', 'working'], help='Memory type')
    log_parser.add_argument('--importance', type=int, default=5, help='Importance (1-10)')
    log_parser.add_argument('--tags', nargs='*', help='Tags for the memory')
    
    # interests
    subparsers.add_parser('interests', help='Show current interests')
    
    # emotion
    subparsers.add_parser('emotion', help='Show emotional state')
    
    # daemon
    daemon_parser = subparsers.add_parser('daemon', help='Daemon management')
    daemon_parser.add_argument('action', choices=['start', 'stop', 'status', 'explore'], help='Daemon action')
    
    # vault
    vault_parser = subparsers.add_parser('vault', help='Encrypt/decrypt identity and memory')
    vault_parser.add_argument('lock', action='store_true')
    vault_parser.add_argument('unlock', action='store_true')
    
    # providers
    subparsers.add_parser('providers', help='List/configure providers')
    
    # eval
    subparsers.add_parser('eval', help='Run self-evaluation tests')
    
    # version
    subparsers.add_parser('version', help='Show version info')
    
    args = parser.parse_args()
    
    # Handle --daemon-run flag (internal use)
    if hasattr(args, 'daemon_run') or '--daemon-run' in sys.argv:
        daemon_loop()
        return
    
    # Ensure database exists
    db_init()
    
    # Route to command
    if args.command == 'setup':
        initialize_nova()
    elif args.command == 'chat':
        cmd_chat(args)
    elif args.command == 'idle':
        cmd_idle(args)
    elif args.command == 'goals':
        cmd_goals(args)
    elif args.command == 'log':
        cmd_log(args)
    elif args.command == 'interests':
        cmd_interests(args)
    elif args.command == 'emotion':
        cmd_emotion(args)
    elif args.command == 'daemon':
        cmd_daemon(args)
    elif args.command == 'vault':
        cmd_vault(args)
    elif args.command == 'providers':
        cmd_providers(args)
    elif args.command == 'eval':
        cmd_eval(args)
    elif args.command == 'version':
        cmd_version(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
