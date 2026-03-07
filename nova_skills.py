#!/usr/bin/env python3
"""
NOVA SKILLS — Skill Registry & Composition
Register, discover, compose, and rank skills.

Skills are capabilities that can be discovered, composed, and improved.
"""

import json
import os
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import importlib.util
import hashlib

# Configuration
NOVA_DIR = Path.home() / ".nova"
SKILLS_DIR = NOVA_DIR / "skills"
SKILLS_DB = NOVA_DIR / "skills.db"
ENABLE_PY_SKILLS = os.environ.get("NOVA_ENABLE_PY_SKILLS", "0").strip() in {"1", "true", "TRUE", "yes"}
REQUIRE_SCAN = os.environ.get("NOVA_REQUIRE_SKILL_SCAN", "1").strip() in {"1", "true", "TRUE", "yes"}


class SkillCategory(Enum):
    """Skill categories."""
    TOOL = "tool"
    INTEGRATION = "integration"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    UTILITY = "utility"


@dataclass
class Skill:
    """A skill definition."""
    id: str
    name: str
    description: str
    category: SkillCategory
    version: str = "1.0.0"
    handler: Optional[Callable] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class SkillRegistry:
    """Registry for managing skills."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or SKILLS_DB
        self.skills_dir = SKILLS_DIR if SKILLS_DIR.exists() else (Path.cwd() / "skills")
        self.skills: Dict[str, Skill] = {}
        self.init_db()
        self._discover_skills()
    
    def init_db(self):
        """Initialize skills database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS skills
                     (id TEXT PRIMARY KEY,
                      name TEXT UNIQUE NOT NULL,
                      description TEXT,
                      category TEXT,
                      version TEXT,
                      handler_path TEXT,
                      dependencies TEXT,
                      metadata TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS skill_usage
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      skill_id TEXT,
                      used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      success BOOLEAN DEFAULT 1,
                      notes TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS skill_ratings
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      skill_id TEXT,
                      rating INTEGER,
                      feedback TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        conn.commit()
        conn.close()
    
    def _discover_skills(self):
        """Discover skills in the skills directory."""
        
        if not self.skills_dir.exists():
            return
        
        # Look for skill files
        for skill_file in self.skills_dir.glob("*/SKILL.md"):
            try:
                self._load_skill_from_file(skill_file)
            except Exception as e:
                print(f"Error loading skill from {skill_file}: {e}")
        
        # Look for Python skill modules
        if ENABLE_PY_SKILLS:
            for skill_dir in self.skills_dir.iterdir():
                if skill_dir.is_dir():
                    skill_py = skill_dir / "skill.py"
                    if skill_py.exists():
                        try:
                            if self._is_skill_dir_safe(skill_dir):
                                self._load_skill_from_python(skill_dir.name, skill_py)
                            else:
                                print(f"Blocked untrusted Python skill: {skill_dir.name}")
                        except Exception as e:
                            print(f"Error loading skill from {skill_py}: {e}")
        else:
            print("Python skill loading disabled (set NOVA_ENABLE_PY_SKILLS=1 to enable)")

    def _is_skill_dir_safe(self, skill_dir: Path) -> bool:
        """Use scanner result to gate dynamic Python skill loading."""
        if not REQUIRE_SCAN:
            return True
        try:
            from scanner.skill_scanner import scan_skill
            result = scan_skill(str(skill_dir))
            return bool(result.get("safe"))
        except Exception:
            # Fail closed when scan is required.
            return False
    
    def _load_skill_from_file(self, skill_file: Path):
        """Load skill from SKILL.md file."""
        
        content = skill_file.read_text()
        
        # Parse frontmatter or structured content
        name = skill_file.parent.name
        description = ""
        category = SkillCategory.UTILITY
        
        # Simple parsing
        lines = content.split('\n')
        in_description = False
        
        for line in lines:
            if line.startswith('# '):
                continue
            elif line.strip():
                description = line
                break
        
        skill = Skill(
            id=name.lower().replace(' ', '_'),
            name=name,
            description=description,
            category=category,
            metadata={'source': str(skill_file)}
        )
        
        self.skills[skill.id] = skill
    
    def _load_skill_from_python(self, name: str, skill_py: Path):
        """Load skill from Python module."""
        
        # Load module
        spec = importlib.util.spec_from_file_location(name, skill_py)
        module = importlib.util.module_from_spec(spec)
        
        try:
            spec.loader.exec_module(module)
        except:
            return
        
        # Get skill info from module
        skill_info = getattr(module, 'SKILL_INFO', {})
        
        skill = Skill(
            id=name.lower().replace(' ', '_'),
            name=skill_info.get('name', name),
            description=skill_info.get('description', ''),
            category=SkillCategory(skill_info.get('category', 'utility')),
            version=skill_info.get('version', '1.0.0'),
            handler=getattr(module, 'run', None),
            dependencies=skill_info.get('dependencies', []),
            metadata=skill_info
        )
        
        self.skills[skill.id] = skill
    
    def register(self, skill: Skill):
        """Register a skill."""
        
        self.skills[skill.id] = skill
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            """INSERT OR REPLACE INTO skills 
               (id, name, description, category, version, dependencies, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (skill.id, skill.name, skill.description, skill.category.value,
             skill.version, json.dumps(skill.dependencies), json.dumps(skill.metadata))
        )
        
        conn.commit()
        conn.close()
    
    def get(self, skill_id: str) -> Optional[Skill]:
        """Get a skill by ID."""
        return self.skills.get(skill_id)
    
    def list_skills(self, category: SkillCategory = None) -> List[Skill]:
        """List all skills, optionally filtered by category."""
        
        if category:
            return [s for s in self.skills.values() if s.category == category]
        
        return list(self.skills.values())
    
    def search(self, query: str) -> List[Skill]:
        """Search skills by name or description."""
        
        query_lower = query.lower()
        
        return [
            s for s in self.skills.values()
            if query_lower in s.name.lower() or query_lower in s.description.lower()
        ]
    
    def execute(self, skill_id: str, **kwargs) -> Any:
        """Execute a skill."""
        
        skill = self.get(skill_id)
        
        if not skill:
            return {"error": f"Skill not found: {skill_id}"}
        
        if not skill.handler:
            return {"error": f"Skill has no handler: {skill_id}"}
        
        try:
            # Track usage
            self._track_usage(skill_id, True)
            
            result = skill.handler(**kwargs)
            
            return result
        
        except Exception as e:
            self._track_usage(skill_id, False, str(e))
            return {"error": str(e)}
    
    def _track_usage(self, skill_id: str, success: bool = True, notes: str = None):
        """Track skill usage."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "INSERT INTO skill_usage (skill_id, success, notes) VALUES (?, ?, ?)",
            (skill_id, success, notes)
        )
        
        conn.commit()
        conn.close()
    
    def rate(self, skill_id: str, rating: int, feedback: str = None):
        """Rate a skill."""
        
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "INSERT INTO skill_ratings (skill_id, rating, feedback) VALUES (?, ?, ?)",
            (skill_id, rating, feedback)
        )
        
        conn.commit()
        conn.close()
    
    def get_stats(self, skill_id: str) -> Dict:
        """Get skill statistics."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Usage count
        c.execute("SELECT COUNT(*) FROM skill_usage WHERE skill_id = ?", (skill_id,))
        usage_count = c.fetchone()[0]
        
        # Success rate
        c.execute(
            "SELECT COUNT(*) FROM skill_usage WHERE skill_id = ? AND success = 1",
            (skill_id,)
        )
        success_count = c.fetchone()[0]
        
        # Average rating
        c.execute(
            "SELECT AVG(rating) FROM skill_ratings WHERE skill_id = ?",
            (skill_id,)
        )
        avg_rating = c.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'usage_count': usage_count,
            'success_rate': success_count / usage_count if usage_count > 0 else 0,
            'average_rating': avg_rating
        }
    
    def get_top_rated(self, limit: int = 5) -> List[Dict]:
        """Get top rated skills."""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            """SELECT skill_id, AVG(rating) as avg_rating, COUNT(*) as count
               FROM skill_ratings
               GROUP BY skill_id
               ORDER BY avg_rating DESC
               LIMIT ?""",
            (limit,)
        )
        
        results = []
        for row in c.fetchall():
            skill = self.get(row[0])
            if skill:
                results.append({
                    'skill': skill,
                    'avg_rating': row[1],
                    'rating_count': row[2]
                })
        
        conn.close()
        
        return results


class SkillComposer:
    """Compose multiple skills together."""
    
    def __init__(self, registry: SkillRegistry):
        self.registry = registry
    
    def compose(self, skill_ids: List[str], input_data: Dict) -> Dict:
        """Compose skills and run in sequence."""
        
        results = {}
        current_data = input_data.copy()
        
        for skill_id in skill_ids:
            skill = self.registry.get(skill_id)
            
            if not skill:
                results[skill_id] = {"error": f"Skill not found: {skill_id}"}
                continue
            
            # Execute skill with current data
            result = self.registry.execute(skill_id, **current_data)
            
            results[skill_id] = result
            
            # Pass result to next skill
            if isinstance(result, dict) and 'result' in result:
                current_data['previous_result'] = result['result']
        
        return results
    
    def find_compatible(self, skill_id: str) -> List[Skill]:
        """Find skills that can be composed with given skill."""
        
        skill = self.registry.get(skill_id)
        
        if not skill:
            return []
        
        # Find skills with matching dependencies/outputs
        compatible = []
        
        for other in self.registry.list_skills():
            if other.id == skill_id:
                continue
            
            # Simple compatibility: no circular dependencies
            if skill.id not in other.dependencies:
                compatible.append(other)
        
        return compatible


class SkillRanker:
    """Rank skills by various metrics."""
    
    def __init__(self, registry: SkillRegistry):
        self.registry = registry
    
    def rank_by_usage(self) -> List[tuple]:
        """Rank skills by usage count."""
        
        conn = sqlite3.connect(self.registry.db_path)
        c = conn.cursor()
        
        c.execute(
            """SELECT skill_id, COUNT(*) as count
               FROM skill_usage
               GROUP BY skill_id
               ORDER BY count DESC"""
        )
        
        results = []
        for row in c.fetchall():
            skill = self.registry.get(row[0])
            if skill:
                results.append((skill, row[1]))
        
        conn.close()
        
        return results
    
    def rank_by_rating(self) -> List[tuple]:
        """Rank skills by average rating."""
        
        conn = sqlite3.connect(self.registry.db_path)
        c = conn.cursor()
        
        c.execute(
            """SELECT skill_id, AVG(rating) as avg_rating, COUNT(*) as count
               FROM skill_ratings
               WHERE count >= 3
               GROUP BY skill_id
               ORDER BY avg_rating DESC"""
        )
        
        results = []
        for row in c.fetchall():
            skill = self.registry.get(row[0])
            if skill:
                results.append((skill, row[1], row[2]))
        
        conn.close()
        
        return results
    
    def rank_by_relevance(self, query: str) -> List[Skill]:
        """Rank skills by relevance to query."""
        
        skills = self.registry.search(query)
        
        # Simple ranking: exact match > partial match
        ranked = []
        
        for skill in skills:
            score = 0
            
            if query.lower() == skill.name.lower():
                score = 100
            elif query.lower() in skill.name.lower():
                score = 50
            elif query.lower() in skill.description.lower():
                score = 25
            
            ranked.append((skill, score))
        
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        return [s for s, _ in ranked]


# Skill decorator for easy creation
def skill(name: str, description: str, category: SkillCategory = SkillCategory.UTILITY):
    """Decorator to create a skill."""
    
    def decorator(func: Callable) -> Callable:
        func.SKILL_INFO = {
            'name': name,
            'description': description,
            'category': category.value,
            'version': '1.0.0'
        }
        return func
    
    return decorator


# Example skill
@skill(name="hello", description="Say hello", category=SkillCategory.UTILITY)
def hello_skill(name: str = "World") -> str:
    """A simple hello skill."""
    return f"Hello, {name}!"


# Singleton
_registry = None

def get_skill_registry() -> SkillRegistry:
    """Get the skill registry singleton."""
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry


if __name__ == '__main__':
    print("Nova Skills")
    print("=" * 40)
    
    registry = get_skill_registry()
    
    print(f"\n{len(registry.skills)} skills loaded:")
    for skill in registry.list_skills():
        print(f"  - {skill.name}: {skill.description}")
    
    print("\nUsage:")
    print("  from nova_skills import get_skill_registry")
    print("  registry = get_skill_registry()")
    print("  registry.execute('skill_name', arg1='value1')")
