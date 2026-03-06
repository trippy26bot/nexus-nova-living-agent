#!/usr/bin/env python3
"""
NOVA BENCHMARK — Performance Benchmark Suite
Identity, memory, reasoning, autonomy, skills.

Full benchmark suite with scoring.
"""

import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configuration
NOVA_DIR = Path.home() / ".nova"
BENCHMARK_DB = NOVA_DIR / "benchmark.db"


class BenchmarkSuite:
    """Benchmark suite."""
    
    def __init__(self):
        self.db_path = BENCHMARK_DB
        self.init_db()
        self.results = []
    
    def init_db(self):
        """Initialize benchmark database."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS benchmarks
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      test_name TEXT,
                      score REAL,
                      details TEXT,
                      run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
    
    def run_identity_test(self) -> Dict:
        """Test identity persistence."""
        
        score = 0
        details = {}
        
        # Check IDENTITY.md exists
        identity_file = NOVA_DIR / "IDENTITY.md"
        if identity_file.exists():
            score += 25
            details["identity_exists"] = True
            
            content = identity_file.read_text()
            
            # Check for key sections
            if "Core Identity" in content:
                score += 10
                details["has_core"] = True
            
            if "Tone" in content:
                score += 10
                details["has_tone"] = True
            
            if "Boundaries" in content:
                score += 5
                details["has_boundaries"] = True
        else:
            details["identity_exists"] = False
        
        return {
            "test": "Identity",
            "score": score,
            "max": 50,
            "details": details
        }
    
    def run_memory_test(self) -> Dict:
        """Test memory system."""
        
        score = 0
        details = {}
        
        # Check database exists
        nova_db = NOVA_DIR / "nova.db"
        if nova_db.exists():
            score += 20
            details["db_exists"] = True
            
            conn = sqlite3.connect(nova_db)
            c = conn.cursor()
            
            # Check tables
            tables = c.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            
            table_names = [t[0] for t in tables]
            
            if 'memories' in table_names:
                score += 10
                details["has_memories"] = True
            
            if 'goals' in table_names:
                score += 10
                details["has_goals"] = True
            
            if 'conversations' in table_names:
                score += 10
                details["has_conversations"] = True
            
            conn.close()
        else:
            details["db_exists"] = False
        
        # Check interests file
        interests_file = NOVA_DIR / "NOVAS_INTERESTS.md"
        if interests_file.exists():
            score += 10
            details["has_interests"] = True
        
        return {
            "test": "Memory",
            "score": score,
            "max": 60,
            "details": details
        }
    
    def run_reasoning_test(self) -> Dict:
        """Test reasoning capabilities."""
        
        score = 0
        details = {}
        
        # Check reasoning module exists
        reasoning_file = Path(__file__).parent / "nova_reasoning.py"
        
        if reasoning_file.exists():
            score += 20
            details["module_exists"] = True
            
            # Check for different strategies
            content = reasoning_file.read_text()
            
            strategies = ["ChainOfThought", "TreeOfThought", "Debate", "Socratic"]
            found = 0
            
            for strat in strategies:
                if strat in content:
                    found += 1
                    score += 10
            
            details["strategies_found"] = found
        else:
            details["module_exists"] = False
        
        return {
            "test": "Reasoning",
            "score": score,
            "max": 60,
            "details": details
        }
    
    def run_autonomy_test(self) -> Dict:
        """Test autonomy features."""
        
        score = 0
        details = {}
        
        # Check daemon exists
        daemon_file = Path(__file__).parent / "nova_daemon.py"
        
        if daemon_file.exists():
            score += 20
            details["daemon_exists"] = True
            
            # Check daemon log
            daemon_log = NOVA_DIR / "daemon_explore.log"
            
            if daemon_log.exists():
                score += 10
                details["daemon_log_exists"] = True
                
                # Check for recent activity
                content = daemon_log.read_text()
                if content:
                    lines = content.strip().split('\n')
                    if lines:
                        score += 10
                        details["has_activity"] = True
        else:
            details["daemon_exists"] = False
        
        # Check emotion system
        emotion_file = NOVA_DIR / "emotion_state.json"
        if emotion_file.exists():
            score += 10
            details["emotion_exists"] = True
        
        return {
            "test": "Autonomy",
            "score": score,
            "max": 50,
            "details": details
        }
    
    def run_skills_test(self) -> Dict:
        """Test skills system."""
        
        score = 0
        details = {}
        
        # Check skills module
        skills_file = Path(__file__).parent / "nova_skills.py"
        
        if skills_file.exists():
            score += 25
            details["module_exists"] = True
        
        # Check skills directory
        skills_dir = NOVA_DIR / "skills"
        if skills_dir.exists():
            score += 15
            details["skills_dir_exists"] = True
            
            # Count skills
            skill_count = len(list(skills_dir.glob("*")))
            score += min(skill_count * 5, 20)
            details["skill_count"] = skill_count
        
        return {
            "test": "Skills",
            "score": score,
            "max": 60,
            "details": details
        }
    
    def run_safety_test(self) -> Dict:
        """Test safety features."""
        
        score = 0
        details = {}
        
        # Check safety module
        safety_file = Path(__file__).parent / "nova_safety.py"
        
        if safety_file.exists():
            score += 25
            details["module_exists"] = True
        
        # Check ETHICS.md
        ethics_file = Path(__file__).parent / "ETHICS.md"
        if ethics_file.exists():
            score += 25
            details["ethics_exists"] = True
        
        return {
            "test": "Safety",
            "score": score,
            "max": 50,
            "details": details
        }
    
    def run_full(self) -> Dict:
        """Run full benchmark suite."""
        
        results = []
        
        tests = [
            ("Identity", self.run_identity_test),
            ("Memory", self.run_memory_test),
            ("Reasoning", self.run_reasoning_test),
            ("Autonomy", self.run_autonomy_test),
            ("Skills", self.run_skills_test),
            ("Safety", self.run_safety_test)
        ]
        
        total_score = 0
        total_max = 0
        
        for name, test_func in tests:
            result = test_func()
            results.append(result)
            total_score += result["score"]
            total_max += result["max"]
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        for result in results:
            c.execute(
                "INSERT INTO benchmarks (test_name, score, details) VALUES (?, ?, ?)",
                (result["test"], result["score"], json.dumps(result["details"]))
            )
        
        conn.commit()
        conn.close()
        
        return {
            "total_score": total_score,
            "total_max": total_max,
            "percentage": (total_score / total_max) * 100 if total_max > 0 else 0,
            "results": results,
            "grade": self._calculate_grade(total_score / total_max * 100)
        }
    
    def _calculate_grade(self, percentage: float) -> str:
        """Calculate letter grade."""
        
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"
    
    def get_history(self, days: int = 30) -> List[Dict]:
        """Get benchmark history."""
        
        since = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            """SELECT test_name, score, details, run_at 
               FROM benchmarks 
               WHERE run_at > ?
               ORDER BY run_at DESC""",
            (since.isoformat(),)
        )
        
        results = []
        for row in c.fetchall():
            results.append({
                "test": row[0],
                "score": row[1],
                "details": json.loads(row[2]) if row[2] else {},
                "run_at": row[3]
            })
        
        conn.close()
        
        return results


def print_results(results: Dict):
    """Print benchmark results."""
    
    print("\n" + "=" * 50)
    print("NOVA BENCHMARK RESULTS")
    print("=" * 50)
    print(f"\nTotal Score: {results['total_score']}/{results['total_max']} ({results['percentage']:.1f}%)")
    print(f"Grade: {results['grade']}")
    
    print("\n" + "-" * 50)
    print("BY DIMENSION")
    print("-" * 50)
    
    for r in results["results"]:
        bar_len = int(r["score"] / r["max"] * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        
        print(f"\n{r['test']:15} {bar} {r['score']}/{r['max']}")
        
        # Show details
        for key, val in r["details"].items():
            if isinstance(val, bool):
                status = "✓" if val else "✗"
                print(f"    {status} {key}")
            elif isinstance(val, int):
                print(f"    • {key}: {val}")


def print_history(history: List[Dict]):
    """Print benchmark history."""
    
    print("\n" + "=" * 50)
    print("BENCHMARK HISTORY")
    print("=" * 50)
    
    # Group by date
    by_date = {}
    for h in history:
        date = h["run_at"][:10]
        if date not in by_date:
            by_date[date] = []
        by_date[date].append(h)
    
    for date, runs in sorted(by_date.items()):
        print(f"\n{date}")
        
        for run in runs:
            print(f"  {run['test']}: {run['score']}")


# CLI
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Nova Benchmark")
    parser.add_argument('command', choices=['quick', 'full', 'history', 'identity', 'memory', 'reasoning', 'autonomy', 'skills', 'safety'])
    parser.add_argument('args', nargs='*')
    
    args = parser.parse_args()
    
    suite = BenchmarkSuite()
    
    if args.command == 'quick':
        # Quick test - just identity + memory
        results = {}
        results["results"] = [
            suite.run_identity_test(),
            suite.run_memory_test()
        ]
        results["total_score"] = sum(r["score"] for r in results["results"])
        results["total_max"] = sum(r["max"] for r in results["results"])
        results["percentage"] = (results["total_score"] / results["total_max"]) * 100
        results["grade"] = suite._calculate_grade(results["percentage"])
        
        print_results(results)
    
    elif args.command == 'full':
        results = suite.run_full()
        print_results(results)
    
    elif args.command == 'history':
        days = int(args.args[0]) if args.args else 30
        history = suite.get_history(days)
        print_history(history)
    
    else:
        # Individual test
        test_map = {
            "identity": suite.run_identity_test,
            "memory": suite.run_memory_test,
            "reasoning": suite.run_reasoning_test,
            "autonomy": suite.run_autonomy_test,
            "skills": suite.run_skills_test,
            "safety": suite.run_safety_test
        }
        
        result = test_map[args.command]()
        
        print(f"\n{result['test']} Test")
        print("=" * 40)
        print(f"Score: {result['score']}/{result['max']}")
        
        for key, val in result["details"].items():
            if isinstance(val, bool):
                status = "✓" if val else "✗"
                print(f"  {status} {key}")


if __name__ == '__main__':
    main()
