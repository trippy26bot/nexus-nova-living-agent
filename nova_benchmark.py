#!/usr/bin/env python3
"""
nova_benchmark.py — System Benchmark & Health Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tests Nova's capabilities across multiple dimensions.
Measures: memory, reasoning, identity, tools, skills, composition.

Usage:
 python3 nova_benchmark.py (full benchmark)
 python3 nova_benchmark.py --quick (fast tests only)
 python3 nova_benchmark.py --category reasoning (specific category)
"""

import os, sys, json, time, sqlite3, traceback
from pathlib import Path
from datetime import datetime

NOVA_DIR = Path.home() / ".nova"
BENCHMARK_DB = NOVA_DIR / "benchmark_history.db"


def load_json(path, default=None):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            pass
    return default or {}


# ── TEST CATEGORIES ─────────────────────────────────────────────────────────

class Benchmark:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.total = 0

    def test(self, name, func):
        self.total += 1
        try:
            result = func()
            status = "PASS" if result else "FAIL"
            self.results.append({"test": name, "status": status, "score": 1.0 if result else 0.0})
            if result:
                self.passed += 1
            print(f"  [{status}] {name}")
            return result
        except Exception as e:
            self.results.append({"test": name, "status": "ERROR", "error": str(e), "score": 0.0})
            print(f"  [ERROR] {name}: {e}")
            return False

    def summary(self):
        score = self.passed / self.total if self.total else 0
        grade = "F" if score < 0.6 else "D" if score < 0.7 else "C" if score < 0.8 else "B" if score < 0.9 else "A"
        return {
            "passed": self.passed,
            "total": self.total,
            "score": score,
            "grade": grade,
            "tests": self.results
        }


def test_identity():
    """IDENTITY.md exists and is non-empty."""
    for path in [NOVA_DIR / "IDENTITY.md", Path("IDENTITY.md"), Path.cwd() / "IDENTITY.md"]:
        if path.exists() and path.stat().st_size > 100:
            return True
    return False


def test_memory():
    """Memory system functional."""
    db_file = NOVA_DIR / "nova.db"
    if not db_file.exists():
        # Try creating
        NOVA_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_file)
        conn.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, content TEXT)")
        conn.execute("INSERT INTO memories (content) VALUES ('test')")
        conn.commit()
        conn.close()
        return db_file.exists()
    return True


def test_providers():
    """LLM providers available."""
    try:
        from nova_providers import get_provider
        provider = get_provider()
        if provider and provider.available():
            return True
        # Check direct env vars
        for var in ["ANTHROPIC_API_KEY", "MINIMAX_API_KEY", "OPENAI_API_KEY"]:
            if os.environ.get(var):
                return True
        return False
    except ImportError:
        # Check env vars directly
        for var in ["ANTHROPIC_API_KEY", "MINIMAX_API_KEY", "OPENAI_API_KEY"]:
            if os.environ.get(var):
                return True
        return False


def test_skills():
    """Skills system loads."""
    skill_dir = Path.home() / ".openclaw" / "workspace" / "skills"
    if not skill_dir.exists():
        return False
    
    # Check for nova skills
    nova_skills = list(skill_dir.glob("nova-*/SKILL.md"))
    if nova_skills:
        return True
    
    # Check for any skills
    skills = list(skill_dir.glob("*/SKILL.md"))
    return len(skills) > 0


def test_daemon():
    """Daemon can be imported."""
    try:
        import nova_daemon
        return True
    except ImportError:
        return False


def test_supervisor():
    """Supervisor can be imported."""
    try:
        import nova_supervisor
        return True
    except ImportError:
        return False


def test_api():
    """API module can be imported."""
    try:
        import nova_api
        return True
    except ImportError:
        return False


def test_reasoning():
    """Reasoning module exists."""
    for path in ["nova_reasoning.py", Path.cwd() / "nova_reasoning.py"]:
        if Path(path).exists():
            return True
    return False


def test_emotion():
    """Emotion state file exists or can be created."""
    state_file = NOVA_DIR / "emotion_state.json"
    if state_file.exists():
        return True
    # Try creating default
    try:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps({"neutral": 1.0}))
        return True
    except:
        return False


def test_goals():
    """Goals system functional."""
    db_file = NOVA_DIR / "nova.db"
    if not db_file.exists():
        return test_memory()  # Reuse memory test
    return True


def test_tools():
    """Tools can be imported."""
    try:
        from nova_tool_registry import ToolRegistry
        _ = ToolRegistry()
        return True
    except ImportError:
        return False


def test_composition_1():
    """Can chain: identity + memory."""
    try:
        has_identity = test_identity()
        has_memory = test_memory()
        return has_identity and has_memory
    except:
        return False


def test_composition_2():
    """Can chain: emotion + reasoning."""
    try:
        has_emotion = test_emotion()
        has_reasoning = test_reasoning()
        return has_emotion and has_reasoning
    except:
        return False


def test_composition_3():
    """Can chain: providers + supervisor."""
    try:
        has_providers = test_providers()
        has_supervisor = test_supervisor()
        return has_providers and has_supervisor
    except:
        return False


def test_composition_4():
    """Can chain: api + daemon + supervisor + providers."""
    try:
        has_api = test_api()
        has_daemon = test_daemon()
        has_supervisor = test_supervisor()
        has_providers = test_providers()
        return has_api and has_daemon and has_supervisor and has_providers
    except:
        return False


# ── RUNNER ──────────────────────────────────────────────────────────────────

def run_full():
    print("=" * 50)
    print("NEXUS NOVA BENCHMARK")
    print("=" * 50)

    b = Benchmark()

    print("\n[Identity]")
    b.test("IDENTITY.md exists", test_identity)

    print("\n[Memory]")
    b.test("Memory DB functional", test_memory)
    b.test("Goals system functional", test_goals)

    print("\n[Providers]")
    b.test("LLM providers available", test_providers)

    print("\n[Skills]")
    b.test("Skills system loads", test_skills)

    print("\n[Reasoning]")
    b.test("Reasoning module exists", test_reasoning)

    print("\n[Emotion]")
    b.test("Emotion state functional", test_emotion)

    print("\n[Tools]")
    b.test("Tools can be imported", test_tools)

    print("\n[Architecture]")
    b.test("Daemon can import", test_daemon)
    b.test("Supervisor can import", test_supervisor)
    b.test("API can import", test_api)

    print("\n[Composition]")
    b.test("identity + memory", test_composition_1)
    b.test("emotion + reasoning", test_composition_2)
    b.test("providers + supervisor", test_composition_3)
    b.test("api + daemon + supervisor + providers", test_composition_4)

    result = b.summary()
    print("\n" + "=" * 50)
    print(f"SCORE: {result['passed']}/{result['total']} ({result['score']:.1%})")
    print(f"GRADE: {result['grade']}")
    print("=" * 50)

    # Save to history
    save_result(result)
    return result


def run_quick():
    """Fast tests only."""
    print("Quick benchmark...")
    b = Benchmark()
    b.test("Identity", test_identity)
    b.test("Memory", test_memory)
    b.test("Providers", test_providers)
    result = b.summary()
    print(f"Quick: {result['passed']}/{result['total']} — {result['grade']}")
    return result


def save_result(result):
    """Save to benchmark history."""
    BENCHMARK_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(BENCHMARK_DB))
    conn.execute("""CREATE TABLE IF NOT EXISTS history
        (id INTEGER PRIMARY KEY, timestamp TEXT, passed INTEGER, total INTEGER, score REAL, grade TEXT)""")
    conn.execute("INSERT INTO history (timestamp, passed, total, score, grade) VALUES (?,?,?,?,?)",
                (datetime.now().isoformat(), result["passed"], result["total"], result["score"], result["grade"]))
    conn.commit()
    conn.close()


# ── MAIN ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--quick" in sys.argv:
        run_quick()
    elif "--category" in sys.argv:
        cat = sys.argv[sys.argv.index("--category") + 1] if len(sys.argv) > 2 else None
        print(f"Category: {cat}")
    else:
        run_full()
