#!/usr/bin/env python3
"""
Skill Dispatcher - Enforces registry-driven skill activation.
"""

import json
from pathlib import Path
from typing import Optional, Dict, List

SKILLS_DIR = Path(__file__).parent
REGISTRY_FILE = SKILLS_DIR / "REGISTRY.json"


class SkillDispatcher:
    """Dispatches skills only from active registry."""
    
    def __init__(self, registry_path: Path = REGISTRY_FILE):
        self.registry_path = registry_path
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load skill registry."""
        if not self.registry_path.exists():
            return {"registry": {}, "archived": {}}
        
        with open(self.registry_path) as f:
            return json.load(f)
    
    def is_active(self, skill_name: str) -> bool:
        """Check if skill is active."""
        return skill_name in self.registry.get("registry", {})
    
    def get_skill(self, skill_name: str) -> Optional[Dict]:
        """Get skill if active, None if not."""
        if not self.is_active(skill_name):
            return None
        
        return self.registry["registry"].get(skill_name)
    
    def get_trust_level(self, skill_name: str) -> Optional[str]:
        """Get trust level for skill."""
        skill = self.get_skill(skill_name)
        return skill.get("trust_level") if skill else None
    
    def list_active_skills(self) -> List[str]:
        """List all active skill names."""
        return list(self.registry.get("registry", {}).keys())
    
    def dispatch(self, skill_name: str, operation: str = "execute") -> Dict:
        """Dispatch a skill operation with registry enforcement.
        
        Returns:
            {
                "allowed": bool,
                "skill": dict or None,
                "error": str or None
            }
        """
        # Check if skill exists in registry
        if not self.is_active(skill_name):
            return {
                "allowed": False,
                "skill": None,
                "error": f"Skill '{skill_name}' is not in active registry (archived or deleted)"
            }
        
        skill = self.get_skill(skill_name)
        
        # Check trust level
        trust = skill.get("trust_level", "restricted")
        
        # For approval_required skills, require explicit approval
        if trust == "approval_required":
            return {
                "allowed": False,
                "skill": skill,
                "error": f"Skill '{skill_name}' requires approval (trust level: approval_required)"
            }
        
        return {
            "allowed": True,
            "skill": skill,
            "error": None
        }


def dispatch_skill(skill_name: str, operation: str = "execute") -> Dict:
    """Convenience function."""
    dispatcher = SkillDispatcher()
    return dispatcher.dispatch(skill_name, operation)


if __name__ == "__main__":
    import sys
    
    d = SkillDispatcher()
    
    print("Skill Dispatcher")
    print("=" * 40)
    print(f"Active skills: {d.list_active_skills()}")
    print()
    
    if len(sys.argv) > 1:
        skill = sys.argv[1]
        result = d.dispatch(skill)
        print(f"Dispatch '{skill}':")
        print(f"  Allowed: {result['allowed']}")
        if result['error']:
            print(f"  Error: {result['error']}")
