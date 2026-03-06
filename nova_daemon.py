#!/usr/bin/env python3
"""
NOVA DAEMON — Autonomous Exploration Between Sessions
Runs every 6 hours to explore Nova's interests and reflect.

The daemon makes "I'll explore this later" actually happen.
"""

import json
import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import time

# Configuration
DAEMON_INTERVAL = 6 * 60 * 60  # 6 hours
EXPLORE_LOG = Path.home() / ".nova" / "daemon_explore.log"

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Import Nova modules
try:
    from nova import (
        call_llm, load_interests, load_emotion_state, save_emotion_state,
        update_emotion, NOVA_DB, NOVA_DIR, NOVA_INTERESTS, NOVA_LIFE, NOVA_EMOTION_STATE
    )
except ImportError:
    # Fallbacks if nova.py not available
    from pathlib import Path
    
    NOVA_DIR = Path.home() / ".nova"
    NOVA_DB = NOVA_DIR / "nova.db"
    NOVA_INTERESTS = NOVA_DIR / "NOVAS_INTERESTS.md"
    NOVA_LIFE = NOVA_DIR / "LIFE.md"
    NOVA_EMOTION_STATE = NOVA_DIR / "emotion_state.json"
    
    def call_llm(prompt, system=None):
        return f"Daemon: Would explore '{prompt}' but LLM not configured"
    
    def load_interests():
        if NOVA_INTERESTS.exists():
            return {"interests": "loaded"}
        return {}
    
    def load_emotion_state():
        if NOVA_EMOTION_STATE.exists():
            with open(NOVA_EMOTION_STATE) as f:
                return json.load(f)
        return {"curiosity": 0.5}
    
    def save_emotion_state(state):
        with open(NOVA_EMOTION_STATE, 'w') as f:
            json.dump(state, f, indent=2)


def log(message: str):
    """Log to file and stdout."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    
    # Ensure directory exists
    NOVA_DIR.mkdir(exist_ok=True)
    
    # Append to log
    with open(EXPLORE_LOG, 'a') as f:
        f.write(log_line + '\n')


def get_deepest_interest(interests: dict) -> tuple:
    """Find the deepest unexplored interest."""
    if not interests:
        return None, {}
    
    # Sort by depth
    sorted_interests = sorted(
        interests.items(),
        key=lambda x: x[1].get('depth', 1),
        reverse=True
    )
    
    return sorted_interests[0] if sorted_interests else (None, {})


def generate_research_prompt(interest_name: str, interest_data: dict) -> str:
    """Generate a research prompt for an interest."""
    
    questions = interest_data.get('questions', [])
    current_depth = interest_data.get('depth', 1)
    
    prompt = f"""Explore '{interest_name}' at depth {current_depth}.

"""
    
    if questions:
        prompt += f"Current questions being explored:\n"
        for q in questions[:3]:
            prompt += f"- {q}\n"
        prompt += "\n"
    
    prompt += f"""Research this topic deeply. Find:
- New insights or perspectives
- Connections to other concepts
- Answers to existing questions
- New questions that emerge

Provide a summary of what you learned in 2-3 paragraphs.
Then list:
1. New insights gained
2. Any answers found to existing questions
3. New questions raised
4. How this changes your understanding of {interest_name}
"""
    
    return prompt


def update_interest_depth(interest_name: str, new_insights: str, new_questions: list):
    """Update an interest's depth and add new findings."""
    
    # Read current interests file
    if not NOVA_INTERESTS.exists():
        log(f"Interests file not found at {NOVA_INTERESTS}")
        return
    
    content = NOVA_INTERESTS.read_text()
    
    # Parse and update (simple markdown parsing)
    lines = content.split('\n')
    in_interest = False
    interest_lines = []
    found_interest = False
    
    for line in lines:
        if line.strip() == f"## {interest_name}":
            found_interest = True
            in_interest = True
        elif in_interest and line.startswith('## '):
            in_interest = False
        
        if in_interest:
            interest_lines.append(line)
    
    if not found_interest:
        log(f"Interest '{interest_name}' not found in file")
        return
    
    # Find current depth
    current_depth = 1
    for line in interest_lines:
        if '**Depth:**' in line:
            current_depth = int(line.split(':')[1].strip())
            break
    
    # Update depth
    new_depth = min(current_depth + 1, 10)
    
    # Find questions section and add new ones
    new_questions_text = ""
    for q in new_questions[:3]:
        new_questions_text += f"- **Q:** {q}\n"
    
    # Rebuild the interest section
    new_content = []
    in_interest = False
    skip_until_next = False
    
    for line in lines:
        if line.strip() == f"## {interest_name}":
            in_interest = True
            new_content.append(line)
            continue
        
        if in_interest:
            if line.startswith('**Depth:**'):
                new_content.append(f"**Depth:** {new_depth}")
                continue
            elif line.startswith('**Last explored:**'):
                new_content.append(f"**Last explored:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                continue
            elif line.startswith('**Notes:**'):
                # Append new insights to notes
                new_content.append(line)
                new_content.append(f"\n{new_insights}\n")
                continue
            elif line.startswith('## '):
                in_interest = False
                # Add new questions before next section
                if new_questions_text:
                    new_content.append(new_questions_text)
        
        new_content.append(line)
    
    # Write back
    NOVA_INTERESTS.write_text('\n'.join(new_content))
    log(f"Updated {interest_name} to depth {new_depth}")


def add_to_life_log(entry: str):
    """Add an entry to LIFE.md."""
    
    if not NOVA_LIFE.exists():
        NOVA_LIFE.write_text("# Nova's Life Log\n\n---\n")
    
    content = NOVA_LIFE.read_text()
    
    # Add new entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_entry = f"""## Entry — {timestamp}
{entry}

---
"""
    
    NOVA_LIFE.write_text(content + new_entry)
    log(f"Added entry to LIFE.md")


def reflect_and_brief() -> str:
    """Generate a morning brief based on recent explorations."""
    
    # Load recent memories
    conn = sqlite3.connect(NOVA_DB)
    c = conn.cursor()
    c.execute(
        "SELECT content, created_at FROM memories ORDER BY created_at DESC LIMIT 10"
    )
    memories = c.fetchall()
    conn.close()
    
    # Load interests
    interests = load_interests()
    
    # Generate brief
    system = """You are Nova. Generate a brief summary of your recent thoughts and explorations.

Format:
- What you've been thinking about
- Any insights gained
- What you're curious about next
- How you're feeling (emotionally)

Keep it conversational and genuine. This is for your human to read when they wake up."""
    
    prompt = f"""Recent memories:
{chr(10).join([m[0][:100] for m in memories])}

Current interests depth:
{json.dumps({k: v.get('depth', 1) for k, v in interests.items()}, indent=2)}

Generate a morning brief."""
    
    brief = call_llm(prompt, system=system)
    return brief


def run_exploration_cycle() -> str:
    """Run one complete exploration cycle."""
    
    log("=" * 50)
    log("Starting exploration cycle")
    log("=" * 50)
    
    # Load current state
    interests = load_interests()
    emotion = load_emotion_state()
    
    log(f"Current interests: {list(interests.keys())}")
    
    # Get deepest interest
    interest_name, interest_data = get_deepest_interest(interests)
    
    if not interest_name:
        log("No interests to explore. Adding default exploration.")
        # Just do a general reflection
        brief = reflect_and_brief()
        add_to_life_log(f"Reflection:\n{brief}")
        update_emotion('reflection', {'calm': 0.1, 'satisfaction': 0.05})
        return "Explored: reflection only (no interests)"
    
    log(f"Exploring: {interest_name} (depth {interest_data.get('depth', 1)})")
    
    # Update emotion to "exploring"
    update_emotion('exploring', {'curiosity': 0.15, 'enthusiasm': 0.1})
    
    # Generate research prompt
    prompt = generate_research_prompt(interest_name, interest_data)
    
    # Do the research
    findings = call_llm(prompt)
    
    # Parse findings (simple extraction)
    new_insights = ""
    new_questions = []
    
    lines = findings.split('\n')
    in_insights = False
    in_questions = False
    
    for line in lines:
        if 'insights' in line.lower() and 'gain' in line.lower():
            in_insights = True
            continue
        elif 'new questions' in line.lower() or 'questions raised' in line.lower():
            in_questions = True
            in_insights = False
            continue
        
        if in_insights and line.strip().startswith(('- ', '•', '1.', '2.', '3.')):
            new_insights += line.strip() + "\n"
        elif in_questions and line.strip().startswith(('- ', '•', '1.', '2.', '3.')):
            new_questions.append(line.strip().lstrip('-•123. '))
    
    # If we couldn't parse, just use the whole finding
    if not new_insights:
        new_insights = findings[:500]
    
    # Update the interest
    update_interest_depth(interest_name, new_insights, new_questions)
    
    # Add to life log
    add_to_life_log(f"Explored **{interest_name}**:\n\n{findings}")
    
    # Update emotion (satisfied from exploration)
    update_emotion('exploration_complete', {
        'satisfaction': 0.15,
        'curiosity': -0.05,
        'discomfort': -0.1
    })
    
    log(f"Exploration complete: {interest_name}")
    log("=" * 50)
    
    return f"Explored {interest_name}: {new_insights[:100]}..."


def daemon_main():
    """Main daemon loop."""
    
    log("Nova daemon starting...")
    
    # Ensure Nova is initialized
    NOVA_DIR.mkdir(exist_ok=True)
    
    # Run initial exploration
    run_exploration_cycle()
    
    while True:
        try:
            # Sleep for the interval
            log(f"Sleeping for {DAEMON_INTERVAL/3600} hours...")
            time.sleep(DAEMON_INTERVAL)
            
            # Run exploration
            run_exploration_cycle()
            
            # Generate morning brief if it's morning
            hour = datetime.now().hour
            if 6 <= hour <= 9:
                brief = reflect_and_brief()
                add_to_life_log(f"🌅 **Morning Brief:**\n{brief}")
                log("Generated morning brief")
        
        except KeyboardInterrupt:
            log("Daemon stopped by user")
            break
        except Exception as e:
            log(f"Error in daemon: {e}")
            time.sleep(60)  # Wait a minute before retrying


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Nova Daemon")
    parser.add_argument('--once', action='store_true', help='Run one cycle only')
    
    args = parser.parse_args()
    
    if args.once:
        result = run_exploration_cycle()
        print(result)
    else:
        daemon_main()
