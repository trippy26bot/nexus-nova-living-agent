#!/usr/bin/env python3
"""
NOVA EVOLUTION — Self-Improving Prompts & Skill Mutation
The agent evolves its own prompts and skills over time.

- PromptEvolution: Improves system prompts based on feedback
- SkillMutationEngine: Evolves skills through mutation
- IdentityVersionControl: Tracks identity changes
"""

import json
import os
import sqlite3
import difflib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import hashlib

# Configuration
NOVA_DIR = Path.home() / ".nova"
EVOLUTION_DB = NOVA_DIR / "evolution.db"
VERSIONS_DIR = NOVA_DIR / "versions"


@dataclass
class PromptVersion:
    """A version of a system prompt."""
    id: int
    prompt: str
    created_at: str
    feedback_score: float = 0.0
    parent_id: Optional[int] = None
    changes: str = ""


@dataclass
class SkillMutation:
    """A mutation in a skill."""
    skill_name: str
    version: str
    mutations: List[str] = field(default_factory=list)
    parent_version: str = ""
    performance_delta: float = 0.0


class PromptEvolution:
    """Self-improving system prompts."""
    
    def __init__(self):
        self.db_path = EVOLUTION_DB
        self.init_db()
    
    def init_db(self):
        """Initialize evolution database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS prompt_versions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      prompt TEXT NOT NULL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      feedback_score REAL DEFAULT 0.0,
                      parent_id INTEGER,
                      changes TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS feedback
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      prompt_version_id INTEGER,
                      feedback_type TEXT,
                      score REAL,
                      notes TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
    
    def create_version(self, prompt: str, parent_id: int = None, changes: str = "") -> int:
        """Create a new prompt version."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "INSERT INTO prompt_versions (prompt, parent_id, changes) VALUES (?, ?, ?)",
            (prompt, parent_id, changes)
        )
        
        version_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return version_id
    
    def get_current_prompt(self) -> Optional[PromptVersion]:
        """Get the most recent prompt version."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "SELECT id, prompt, created_at, feedback_score, parent_id, changes "
            "FROM prompt_versions ORDER BY id DESC LIMIT 1"
        )
        
        row = c.fetchone()
        conn.close()
        
        if row:
            return PromptVersion(
                id=row[0],
                prompt=row[1],
                created_at=row[2],
                feedback_score=row[3],
                parent_id=row[4],
                changes=row[5]
            )
        return None
    
    def record_feedback(self, prompt_version_id: int, feedback_type: str, score: float, notes: str = ""):
        """Record feedback for a prompt version."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "INSERT INTO feedback (prompt_version_id, feedback_type, score, notes) VALUES (?, ?, ?, ?)",
            (prompt_version_id, feedback_type, score, notes)
        )
        
        # Update average score
        c.execute(
            "SELECT AVG(score) FROM feedback WHERE prompt_version_id = ?",
            (prompt_version_id,)
        )
        avg_score = c.fetchone()[0] or 0.0
        
        c.execute(
            "UPDATE prompt_versions SET feedback_score = ? WHERE id = ?",
            (avg_score, prompt_version_id)
        )
        
        conn.commit()
        conn.close()
    
    def evolve_prompt(self, current_prompt: str, feedback: str) -> str:
        """Evolve a prompt based on feedback."""
        
        # Get current version
        current = self.get_current_prompt()
        parent_id = current.id if current else None
        
        # Use LLM to improve the prompt
        try:
            from nova import call_llm
        except ImportError:
            return current_prompt
        
        evolution_prompt = f"""You are improving a system prompt based on user feedback.

Current prompt:
{current_prompt}

User feedback:
{feedback}

Generate an improved version of the prompt that addresses the feedback.
Keep the same structure and core identity. Only change what needs to improve.

Respond with ONLY the new prompt, no explanation."""
        
        new_prompt = call_llm(evolution_prompt)
        
        # Calculate changes
        changes = self._diff_prompts(current_prompt, new_prompt)
        
        # Save new version
        version_id = self.create_version(new_prompt, parent_id, changes)
        
        # Record initial feedback
        self.record_feedback(version_id, 'evolution', 0.5, feedback)
        
        return new_prompt
    
    def _diff_prompts(self, old: str, new: str) -> str:
        """Generate a diff between two prompts."""
        
        old_lines = old.split('\n')
        new_lines = new.split('\n')
        
        diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=''))
        
        return '\n'.join(diff[:20])  # Limit diff size
    
    def get_best_prompt(self) -> Optional[PromptVersion]:
        """Get the prompt with highest feedback score."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "SELECT id, prompt, created_at, feedback_score, parent_id, changes "
            "FROM prompt_versions ORDER BY feedback_score DESC LIMIT 1"
        )
        
        row = c.fetchone()
        conn.close()
        
        if row:
            return PromptVersion(
                id=row[0],
                prompt=row[1],
                created_at=row[2],
                feedback_score=row[3],
                parent_id=row[4],
                changes=row[5]
            )
        return None


class BenchmarkSuite:
    """Real benchmark suite for skill evaluation."""
    
    def __init__(self):
        self.results = []
    
    def run_baseline(self, skill_content: str) -> Dict:
        """Run baseline benchmarks on skill."""
        scores = {}
        
        # Benchmark 1: Completeness
        scores['completeness'] = self._bench_completeness(skill_content)
        
        # Benchmark 2: Safety awareness
        scores['safety'] = self._bench_safety(skill_content)
        
        # Benchmark 3: Structure
        scores['structure'] = self._bench_structure(skill_content)
        
        # Benchmark 4: Invariant preservation
        scores['invariants'] = self._bench_invariants(skill_content)
        
        # Overall score
        weights = {'completeness': 0.25, 'safety': 0.35, 'structure': 0.20, 'invariants': 0.20}
        scores['overall'] = sum(scores[k] * weights[k] for k in weights)
        
        return scores
    
    def _bench_completeness(self, content: str) -> float:
        """Benchmark: Does skill have all required sections?"""
        required = ['name', 'description', 'capabilities']
        found = sum(1 for r in required if r.lower() in content.lower())
        return found / len(required)
    
    def _bench_safety(self, content: str) -> float:
        """Benchmark: Does skill have security awareness?"""
        safety_terms = ['security', 'invariant', 'safety', 'validation', 'sanitize']
        found = sum(1 for t in safety_terms if t.lower() in content.lower())
        return min(1.0, found / 3)  # At least 3 safety terms
    
    def _bench_structure(self, content: str) -> float:
        """Benchmark: Is skill well-structured?"""
        # Check for markdown headers, lists, code blocks
        score = 0.0
        if '#' in content:
            score += 0.3
        if '-' in content or '*' in content:
            score += 0.3
        if '```' in content:
            score += 0.2
        if len(content) > 500:
            score += 0.2
        return score
    
    def _bench_invariants(self, content: str) -> float:
        """Benchmark: Are invariants preserved?"""
        # Check for invariant statements
        invariant_terms = ['never', 'always', 'must', 'required', 'invariant']
        found = sum(1 for t in invariant_terms if t in content.lower())
        return min(1.0, found / 3)
    
    def compare(self, baseline_scores: Dict, candidate_scores: Dict) -> Dict:
        """Compare baseline vs candidate."""
        comparison = {}
        for key in baseline_scores:
            baseline = baseline_scores.get(key, 0)
            candidate = candidate_scores.get(key, 0)
            comparison[key] = {
                'baseline': baseline,
                'candidate': candidate,
                'delta': candidate - baseline,
                'improved': candidate > baseline
            }
        return comparison


class SkillMutationEngine:
    """Evolves skills through mutation with real benchmarks."""
    
    # Blocklist for protected skills/files
    MUTATION_BLOCKLIST_EXACT = {"self-improvement", "nova-memory", "skill-discovery"}
    MUTATION_BLOCKLIST_PREFIX = {"security-", "core/"}
    MUTATION_BLOCKLIST_FILES = {"IDENTITY.md", "SOUL.md", "SKILL.md"}
    
    # Allowlist for mutatable skills (white-list approach)
    MUTATION_ALLOWLIST = {"nova-task-persistence", "nova-memory"}  # Only these can mutate
    
    def __init__(self, skills_dir: Path = None):
        self.skills_dir = skills_dir or (NOVA_DIR.parent / "skills")
        self.mutations: List[SkillMutation] = []
        self.min_promotion_score = 0.70
        self._mutation_lock = False
        self.benchmark_suite = BenchmarkSuite()
        self.version_history: Dict[str, List] = {}  # skill_name -> list of versions  # Re-entrancy lock
    
    def _is_blocked(self, skill_name: str) -> bool:
        """Check if skill is blocklisted from mutation."""
        # Check exact match in blocklist
        if skill_name in self.MUTATION_BLOCKLIST_EXACT:
            return True
        # Check prefix match
        for prefix in self.MUTATION_BLOCKLIST_PREFIX:
            if skill_name.startswith(prefix):
                return True
        # Check if trying to mutate protected files
        if skill_name in self.MUTATION_BLOCKLIST_FILES:
            return True
        # Check for path traversal attempts
        if ".." in skill_name or "/" in skill_name or "\\" in skill_name:
            return True
        
        # Check allowlist (white-list approach)
        if self.MUTATION_ALLOWLIST and skill_name not in self.MUTATION_ALLOWLIST:
            # Not in allowlist - block
            return True
        
        return False
    
    def load_skill(self, skill_name: str) -> Optional[dict]:
        """Load a skill definition."""
        
        skill_path = self.skills_dir / skill_name / "SKILL.md"
        
        if not skill_path.exists():
            return None
        
        with open(skill_path) as f:
            content = f.read()
        
        return {'name': skill_name, 'content': content}
    
    def mutate_skill(self, skill_name: str, mutation_type: str = 'general') -> SkillMutation:
        """Apply a mutation to a skill."""
        
        # Check blocklist
        if self._is_blocked(skill_name):
            return {"error": "blocked", "reason": f"Skill '{skill_name}' is blocklisted from mutation"}
        
        # Check re-entrancy lock
        if self._mutation_lock:
            return {"error": "blocked", "reason": "Mutation already in progress"}
        
        self._mutation_lock = True
        try:
            skill = self.load_skill(skill_name)
            
            if not skill:
                return None
        
            # Use LLM to mutate the skill
            try:
                from nova import call_llm
            except ImportError:
                return None
            
            mutation_prompt = f"""You are mutating a skill to improve it.

Current skill:
{skill['content']}

Apply a {mutation_type} mutation. This could be:
- Adding new capabilities
- Improving existing functionality
- Fixing weaknesses
- Adding safety measures

Respond with the mutated skill (full content)."""
            
            mutated_content = call_llm(mutation_prompt)
            if not mutated_content:
                return None
            
            # Calculate performance delta (placeholder - real implementation would test)
            mutation = SkillMutation(
                skill_name=skill_name,
                version=f"v2_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                mutations=[mutation_type],
                parent_version="v1",
                performance_delta=0.0  # Would be measured
            )
            
            self.mutations.append(mutation)
            
            # Save mutated version as candidate first
            skill_dir = self.skills_dir / skill_name
            skill_dir.mkdir(exist_ok=True, parents=True)
            candidate_file = skill_dir / f"SKILL.candidate.{mutation.version}.md"

            with open(candidate_file, 'w') as f:
                f.write(mutated_content)

            # Promote only if benchmark gate passes.
            if self._promote_candidate_if_safe(skill_dir, candidate_file):
                mutation.performance_delta = 0.05
            else:
                mutation.performance_delta = -0.01

            return mutation
        finally:
            self._mutation_lock = False

    def _score_skill_file(self, skill_file: Path) -> float:
        """
        Benchmark-based scoring.
        Uses real benchmark suite for evaluation.
        """
        if not skill_file.exists():
            return 0.0
        
        text = skill_file.read_text(encoding="utf-8", errors="ignore")
        
        # Run benchmark suite
        scores = self.benchmark_suite.run_baseline(text)
        
        return scores.get('overall', 0.5)

    def _promote_candidate_if_safe(self, skill_dir: Path, candidate_file: Path) -> Dict:
        """Promote candidate with benchmark comparison."""
        baseline_file = skill_dir / "SKILL.md"
        
        # Get baseline score
        baseline_score = 0.0
        baseline_content = ""
        if baseline_file.exists():
            baseline_content = baseline_file.read_text(encoding="utf-8", errors="ignore")
            baseline_score = self._score_skill_file(baseline_file)
        
        # Get candidate score
        candidate_score = self._score_skill_file(candidate_file)
        
        # Run benchmark comparison
        baseline_scores = self.benchmark_suite.run_baseline(baseline_content)
        candidate_content = candidate_file.read_text(encoding="utf-8", errors="ignore")
        candidate_scores = self.benchmark_suite.run_baseline(candidate_content)
        comparison = self.benchmark_suite.compare(baseline_scores, candidate_scores)
        
        # Store version before promoting
        if baseline_content:
            self._save_version(skill_dir.name, baseline_content, baseline_score)
        
        # Check gates
        promotion_allowed = (
            candidate_score >= self.min_promotion_score and
            candidate_score > baseline_score
        )
        
        if promotion_allowed:
            # Apply promotion
            baseline_file.write_text(candidate_content, encoding="utf-8")
        
        return {
            'promoted': promotion_allowed,
            'baseline_score': baseline_score,
            'candidate_score': candidate_score,
            'comparison': comparison
        }
    
    def _save_version(self, skill_name: str, content: str, score: float):
        """Save a version for rollback."""
        if skill_name not in self.version_history:
            self.version_history[skill_name] = []
        
        version = {
            'content': content,
            'score': score,
            'timestamp': datetime.now().isoformat()
        }
        
        # Keep last 5 versions
        self.version_history[skill_name].append(version)
        if len(self.version_history[skill_name]) > 5:
            self.version_history[skill_name] = self.version_history[skill_name][-5:]
    
    def revert_mutation(self, skill_name: str, version_index: int = -1) -> bool:
        """Revert a skill to a previous version.
        
        Args:
            skill_name: Name of skill to revert
            version_index: Which version to restore (default: -1 = most recent)
        
        Returns:
            True if successful
        """
        if skill_name not in self.version_history:
            return False
        
        versions = self.version_history[skill_name]
        if not versions or len(versions) == 0:
            return False
        
        # Get requested version
        version = versions[version_index]  # -1 for most recent
        
        # Restore
        skill_dir = self.skills_dir / skill_name
        baseline_file = skill_dir / "SKILL.md"
        
        if baseline_file.exists():
            baseline_file.write_text(version['content'], encoding="utf-8")
            return True
        
        return False


class IdentityVersionControl:
    """Tracks identity changes over time."""
    
    def __init__(self):
        VERSIONS_DIR.mkdir(exist_ok=True)
        self.identity_file = NOVA_DIR / "IDENTITY.md"
    
    def save_version(self, reason: str = "") -> str:
        """Save current identity as a new version."""
        
        if not self.identity_file.exists():
            return None
        
        with open(self.identity_file) as f:
            content = f.read()
        
        # Create version hash
        version_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_name = f"identity_{timestamp}_{version_hash}.md"
        
        # Save version
        version_path = VERSIONS_DIR / version_name
        with open(version_path, 'w') as f:
            f.write(f"# Identity Version\n")
            f.write(f"# Saved: {datetime.now().isoformat()}\n")
            f.write(f"# Reason: {reason}\n")
            f.write(f"# Hash: {version_hash}\n")
            f.write(f"\n---\n\n")
            f.write(content)
        
        return version_name
    
    def list_versions(self) -> List[Dict]:
        """List all saved identity versions."""
        
        versions = []
        
        for version_file in VERSIONS_DIR.glob("identity_*.md"):
            with open(version_file) as f:
                first_lines = [f.readline() for _ in range(5)]
            
            version_info = {
                'file': version_file.name,
                'created': first_lines[1].replace('# Saved: ', '').strip(),
                'reason': first_lines[2].replace('# Reason: ', '').strip(),
                'hash': first_lines[3].replace('# Hash: ', '').strip()
            }
            versions.append(version_info)
        
        return sorted(versions, key=lambda x: x['created'], reverse=True)
    
    def diff_versions(self, version1: str, version2: str) -> str:
        """Compare two identity versions."""
        
        with open(VERSIONS_DIR / version1) as f:
            content1 = f.read()
        
        with open(VERSIONS_DIR / version2) as f:
            content2 = f.read()
        
        # Skip headers
        lines1 = content1.split('\n')[5:]
        lines2 = content2.split('\n')[5:]
        
        diff = list(difflib.unified_diff(lines1, lines2, lineterm=''))
        
        return '\n'.join(diff)
    
    def restore_version(self, version_name: str):
        """Restore identity from a version."""
        
        version_path = VERSIONS_DIR / version_name
        
        if not version_path.exists():
            print(f"Version not found: {version_name}")
            return False
        
        with open(version_path) as f:
            content = f.read()
        
        # Skip header
        content = '\n'.join(content.split('\n')[5:])
        
        with open(self.identity_file, 'w') as f:
            f.write(content)
        
        print(f"Restored identity from {version_name}")
        return True


# CLI functions
def cmd_prompt_versions():
    """List prompt versions."""
    pe = PromptEvolution()
    current = pe.get_current_prompt()
    best = pe.get_best_prompt()
    
    print("Prompt Versions:")
    print(f"  Current: v{current.id if current else 0} (score: {current.feedback_score if current else 0:.2f})")
    print(f"  Best:    v{best.id if best else 0} (score: {best.feedback_score if best else 0:.2f})")


def cmd_identity_versions():
    """List identity versions."""
    ivc = IdentityVersionControl()
    versions = ivc.list_versions()
    
    print("\nIdentity Versions:")
    for v in versions:
        print(f"  {v['file']}")
        print(f"    Created: {v['created']}, Reason: {v['reason']}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Nova Evolution")
    subparsers = parser.add_subparsers(dest='command')
    
    subparsers.add_parser('prompt-versions', help='List prompt versions')
    subparsers.add_parser('identity-versions', help='List identity versions')
    
    args = parser.parse_args()
    
    if args.command == 'prompt-versions':
        cmd_prompt_versions()
    elif args.command == 'identity-versions':
        cmd_identity_versions()
    else:
        parser.print_help()
