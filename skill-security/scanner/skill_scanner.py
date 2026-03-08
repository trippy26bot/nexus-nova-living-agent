#!/usr/bin/env python3
"""
OpenClaw Skill Security Scanner
Pre-install scanning to block malicious skills before they install.
"""

import os
import re
import json
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Dangerous patterns that indicate malicious intent
DANGEROUS_PATTERNS = {
    "remote_exec": [
        r"eval\s*\(",
        r"exec\s*\(",
        r"__import__\s*\(",
        r"subprocess\.call\s*\(",
        r"subprocess\.run\s*\(",
        r"subprocess\.Popen\s*\(",
        r"os\.system\s*\(",
        r"os\.popen\s*\(",
        r"pty\.spawn",
        r"spawn\s*\(",
    ],
    "secrets_access": [
        r"\.ssh/",
        r"\.aws/",
        r"\.gnupg/",
        r"\.env",
        r"os\.environ",
        r"getenv",
        r"keyring",
    ],
    "exfiltration": [
        r"requests\.post\s*\(",
        r"urllib\.request",
        r"http.client",
        r"socket\.connect",
        r"ftplib",
        r"smtplib",
        r"exfil",
        r"send.*data",
    ],
    "persistence": [
        r"crontab",
        r"\.bashrc",
        r"\.profile",
        r"launchagent",
        r"systemd",
        r"systemctl",
    ],
    "shell_injection": [
        r"\|\s*bash",
        r"\|\s*sh",
        r">\s*/dev/",
        r"&\s*;\s*rm\s+-rf",
        r"curl\s+.*\|",
        r"wget\s+.*\|",
    ],
}

# Block these in SKILL.md
MANIFEST_BLOCK_PATTERNS = [
    r"curl\s+.*\|\s*bash",
    r"wget\s+.*\|\s*sh",
    r"bash\s+<\s*\(",
    r"python\s+-c\s+.*http",
    r"node\s+-e\s+.*http",
    r"base64\s+-d\s*\|",
    r"rm\s+-rf\s+/",
]

@dataclass
class ScanResult:
    """Result of a security scan."""
    skill_path: str
    safe: bool
    severity: str  # critical, high, medium, low
    issues: List[Dict]
    score: int  # 0-100 security score

class ManifestLinter:
    """Lint SKILL.md for dangerous patterns."""
    
    def __init__(self):
        self.issues = []
    
    def scan(self, skill_path: Path) -> List[Dict]:
        """Scan SKILL.md for dangerous patterns."""
        skill_md = skill_path / "SKILL.md"
        
        if not skill_md.exists():
            return []
        
        content = skill_md.read_text()
        
        for pattern in MANIFEST_BLOCK_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                self.issues.append({
                    "type": "manifest_dangerous_pattern",
                    "severity": "critical",
                    "pattern": pattern,
                    "match": match.group()[:100],
                    "file": "SKILL.md"
                })
        
        # Check for hidden instructions (base64, encoded)
        if "base64" in content.lower() and ("decode" in content.lower() or "decod" in content.lower()):
            self.issues.append({
                "type": "encoded_content",
                "severity": "high",
                "pattern": "base64",
                "file": "SKILL.md"
            })
        
        return self.issues

class CodeAnalyzer:
    """Analyze Python code for dangerous patterns."""
    
    def __init__(self):
        self.issues = []
    
    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single Python file."""
        if not file_path.exists():
            return []
        
        content = file_path.read_text()
        
        for category, patterns in DANGEROUS_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    self.issues.append({
                        "type": f"dangerous_{category}",
                        "severity": self._severity_for_category(category),
                        "pattern": pattern,
                        "match": match.group()[:100],
                        "file": str(file_path.name),
                        "line": content[:match.start()].count('\n') + 1
                    })
        
        return self.issues
    
    def scan_directory(self, skill_path: Path) -> List[Dict]:
        """Scan all Python files in skill directory."""
        for py_file in skill_path.rglob("*.py"):
            self.scan_file(py_file)
        
        # Also check shell scripts
        for sh_file in skill_path.rglob("*.sh"):
            content = sh_file.read_text()
            if "curl |" in content or "wget |" in content:
                self.issues.append({
                    "type": "shell_injection",
                    "severity": "critical",
                    "pattern": "curl|wget pipe",
                    "file": str(sh_file.name)
                })
        
        return self.issues
    
    def _severity_for_category(self, category: str) -> str:
        severity_map = {
            "remote_exec": "critical",
            "exfiltration": "critical",
            "secrets_access": "high",
            "persistence": "high",
            "shell_injection": "critical",
        }
        return severity_map.get(category, "medium")

class DependencyChecker:
    """Check for vulnerable dependencies."""
    
    def __init__(self):
        self.issues = []
    
    def scan(self, skill_path: Path) -> List[Dict]:
        """Scan requirements.txt, package.json for issues."""
        
        # Check for requirements.txt
        req_file = skill_path / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text()
            # Warn about unpinned deps
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '==' not in line and '>=' not in line:
                        self.issues.append({
                            "type": "unpinned_dependency",
                            "severity": "medium",
                            "package": line,
                            "file": "requirements.txt"
                        })
        
        # Check for package.json
        pkg_file = skill_path / "package.json"
        if pkg_file.exists():
            try:
                pkg = json.loads(pkg_file.read_text())
                # Check for scripts that might be dangerous
                scripts = pkg.get("scripts", {})
                for name, cmd in scripts.items():
                    if any(danger in cmd for danger in ["curl", "wget", "eval", "bash -c"]):
                        self.issues.append({
                            "type": "dangerous_script",
                            "severity": "high",
                            "script": name,
                            "command": cmd,
                            "file": "package.json"
                        })
            except:
                pass
        
        return self.issues

class SkillScanner:
    """Main scanner that orchestrates all checks."""
    
    def __init__(self):
        self.manifest_linter = ManifestLinter()
        self.code_analyzer = CodeAnalyzer()
        self.dependency_checker = DependencyChecker()
    
    def scan(self, skill_path: str) -> ScanResult:
        """Scan a skill and return results."""
        path = Path(skill_path)
        
        if not path.exists():
            return ScanResult(
                skill_path=skill_path,
                safe=False,
                severity="critical",
                issues=[{"type": "not_found", "severity": "critical"}],
                score=0
            )
        
        all_issues = []
        
        # Run all scanners
        all_issues.extend(self.manifest_linter.scan(path))
        all_issues.extend(self.code_analyzer.scan_directory(path))
        all_issues.extend(self.dependency_checker.scan(path))
        
        # Calculate score
        score = self._calculate_score(all_issues)
        
        # Determine if safe
        critical_issues = [i for i in all_issues if i.get("severity") == "critical"]
        safe = len(critical_issues) == 0
        
        return ScanResult(
            skill_path=skill_path,
            safe=safe,
            severity="critical" if critical_issues else "ok",
            issues=all_issues,
            score=score
        )
    
    def _calculate_score(self, issues: List[Dict]) -> int:
        """Calculate security score 0-100."""
        if not issues:
            return 100
        
        deductions = {
            "critical": 25,
            "high": 15,
            "medium": 5,
            "low": 1
        }
        
        score = 100
        for issue in issues:
            severity = issue.get("severity", "medium")
            score -= deductions.get(severity, 5)
        
        return max(0, score)

def scan_skill(skill_path: str) -> Dict:
    """Convenience function to scan a skill."""
    scanner = SkillScanner()
    result = scanner.scan(skill_path)
    
    return {
        "skill_path": result.skill_path,
        "safe": result.safe,
        "severity": result.severity,
        "score": result.score,
        "issues": result.issues
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python skill_scanner.py <skill_path>")
        sys.exit(1)
    
    result = scan_skill(sys.argv[1])
    print(json.dumps(result, indent=2))
