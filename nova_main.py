#!/usr/bin/env python3
"""
Nova Agent - Main Entry Point

This is the main entry point to run Nova as a standalone agent.
For use with OpenClaw, Nova runs inside the framework automatically.

Usage:
    python nova_main.py              # Interactive mode
    python nova_main.py --daemon     # Run as background daemon
    python nova_main.py --test      # Test skills and systems
"""
import os
import sys
import argparse

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
sys.path.insert(0, WORKSPACE)

# Load environment variables
try:
    from nova.nova_env import load_env
    loaded = load_env()
    if loaded:
        print(f"📋 Loaded config: {', '.join(loaded)}")
except Exception:
    pass  # Non-critical if .env loading fails

def test_systems():
    """Test all Nova systems"""
    print("🧪 Testing Nova Systems...\n")
    
    # Test skills
    print("📦 Testing Skills...")
    from nova.skills import SKILLS
    print(f"   Loaded {len(SKILLS)} skills: {', '.join(SKILLS.keys())}")
    
    # Test memory
    print("\n💾 Testing Memory...")
    try:
        from nova.memory import get_hem, get_procedural_memory, get_continuum
        print("   ✓ Memory systems loaded")
    except Exception as e:
        print(f"   ✗ Memory error: {e}")
    
    # Test search
    print("\n🔍 Testing Search...")
    try:
        from nova.nova_search import search
        result = search("test query", limit=1)
        print(f"   ✓ Search working" if result['success'] else "   ✗ Search failed")
    except Exception as e:
        print(f"   ✗ Search error: {e}")
    
    # Test web fetcher
    print("\n🌐 Testing Web Fetcher...")
    try:
        from nova.nova_web_fetcher import fetch_url
        result = fetch_url("https://httpbin.org/get")
        print(f"   ✓ Web fetcher working" if result['success'] else "   ✗ Fetcher failed")
    except Exception as e:
        print(f"   ✗ Fetcher error: {e}")
    
    print("\n✅ Test complete!")

def run_interactive():
    """Run Nova in interactive mode"""
    print("🎭 Starting Nova Interactive Mode...")
    print("Type 'quit' to exit\n")
    
    from nova.skills import SkillManager
    
    class InteractiveNova:
        class Personality:
            state = 'curious'
        personality = Personality()
    
    nova = InteractiveNova()
    sm = SkillManager(nova)
    
    print(f"Available skills: {', '.join(sm.list_skills())}\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Bye!")
                break
            
            # Simple skill routing
            if user_input.startswith("!"):
                # Call a skill directly
                skill_name = user_input[1:].split()[0]
                result = sm.call(skill_name)
                if result:
                    print(f"Nova: {result}")
                else:
                    print(f"Nova: Unknown skill '{skill_name}'")
            else:
                print("Nova: I'm here. Try '!search topic' or '!reflect'")
                
        except KeyboardInterrupt:
            print("\n👋 Bye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def run_daemon():
    """Run Nova as a background daemon"""
    print("🚀 Starting Nova Daemon...")
    import subprocess
    subprocess.Popen([sys.executable, os.path.join(WORKSPACE, "nova/nova_autonomy_daemon.py"), "start"])
    print("Daemon started. Check ~/.nova/logs/ for output.")

def main():
    parser = argparse.ArgumentParser(description="Nova Agent")
    parser.add_argument("--test", action="store_true", help="Run system tests")
    parser.add_argument("--daemon", action="store_true", help="Run as background daemon")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if args.test:
        test_systems()
    elif args.daemon:
        run_daemon()
    elif args.interactive:
        run_interactive()
    else:
        # Default: run interactive
        run_interactive()

if __name__ == "__main__":
    main()
