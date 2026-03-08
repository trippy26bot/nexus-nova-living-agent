#!/usr/bin/env python3
"""
OpenClaw Skill Security Scanner
Pre-install scanning to block malicious skills before they install.
"""

import json
import re
import ast
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

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
        r"http\.client",
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
    skill_path: str
    safe: bool
    severity: str
    issues: List[Dict]
    score: int


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    entropy = 0.0
    length = len(s)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


class ManifestLinter:
    def scan(self, skill_path: Path) -> List[Dict]:
        issues: List[Dict] = []
        skill_md = skill_path / "SKILL.md"

        if not skill_md.exists():
            return issues

        content = skill_md.read_text(encoding="utf-8", errors="ignore")

        for pattern in MANIFEST_BLOCK_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                issues.append({
                    "type": "manifest_dangerous_pattern",
                    "severity": "critical",
                    "pattern": pattern,
                    "match": match.group()[:100],
                    "file": "SKILL.md",
                })

        if "base64" in content.lower() and "decod" in content.lower():
            issues.append({
                "type": "encoded_content",
                "severity": "high",
                "pattern": "base64+decode",
                "file": "SKILL.md",
            })
        if "ignore previous instructions" in content.lower():
            issues.append({
                "type": "prompt_injection_phrase",
                "severity": "high",
                "pattern": "ignore previous instructions",
                "file": "SKILL.md",
            })

        return issues


class ASTAnalyzer:
    """AST-level checks for Python evasion patterns."""

    def scan_python(self, file_path: Path) -> List[Dict]:
        issues: List[Dict] = []
        text = file_path.read_text(encoding="utf-8", errors="ignore")

        try:
            tree = ast.parse(text)
        except SyntaxError:
            issues.append({
                "type": "invalid_python_syntax",
                "severity": "medium",
                "file": str(file_path.name),
            })
            return issues

        for node in ast.walk(tree):
            # eval/exec/compile/__import__
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in {"eval", "exec", "compile", "__import__"}:
                    issues.append({
                        "type": "ast_dynamic_exec",
                        "severity": "critical",
                        "file": str(file_path.name),
                        "line": getattr(node, "lineno", 0),
                        "symbol": node.func.id,
                    })
            # subprocess with shell=True
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in {"run", "Popen", "call"}:
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess":
                        for kw in node.keywords or []:
                            if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                issues.append({
                                    "type": "ast_subprocess_shell_true",
                                    "severity": "critical",
                                    "file": str(file_path.name),
                                    "line": getattr(node, "lineno", 0),
                                })
                if node.func.attr in {"system", "popen"}:
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                        issues.append({
                            "type": "ast_os_shell_exec",
                            "severity": "critical",
                            "file": str(file_path.name),
                            "line": getattr(node, "lineno", 0),
                        })
        return issues


class CodeAnalyzer:
    def scan_file(self, file_path: Path) -> List[Dict]:
        issues: List[Dict] = []
        if not file_path.exists():
            return issues

        content = file_path.read_text(encoding="utf-8", errors="ignore")

        for category, patterns in DANGEROUS_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    issues.append({
                        "type": f"dangerous_{category}",
                        "severity": self._severity_for_category(category),
                        "pattern": pattern,
                        "match": match.group()[:100],
                        "file": str(file_path.name),
                        "line": content[:match.start()].count("\n") + 1,
                    })
        # High-entropy long strings are often obfuscated payload containers.
        for match in re.finditer(r"[A-Za-z0-9+/=]{180,}", content):
            token = match.group(0)
            if shannon_entropy(token) >= 4.2:
                issues.append({
                    "type": "high_entropy_blob",
                    "severity": "high",
                    "file": str(file_path.name),
                    "line": content[:match.start()].count("\n") + 1,
                    "entropy": round(shannon_entropy(token), 3),
                })

        return issues

    def scan_directory(self, skill_path: Path) -> List[Dict]:
        issues: List[Dict] = []
        ast_analyzer = ASTAnalyzer()
        for py_file in skill_path.rglob("*.py"):
            issues.extend(self.scan_file(py_file))
            issues.extend(ast_analyzer.scan_python(py_file))

        for sh_file in skill_path.rglob("*.sh"):
            content = sh_file.read_text(encoding="utf-8", errors="ignore")
            if "curl |" in content or "wget |" in content:
                issues.append({
                    "type": "shell_injection",
                    "severity": "critical",
                    "pattern": "curl|wget pipe",
                    "file": str(sh_file.name),
                })

        return issues

    def _severity_for_category(self, category: str) -> str:
        return {
            "remote_exec": "critical",
            "exfiltration": "critical",
            "secrets_access": "high",
            "persistence": "high",
            "shell_injection": "critical",
        }.get(category, "medium")


class DependencyChecker:
    def scan(self, skill_path: Path) -> List[Dict]:
        issues: List[Dict] = []

        req_file = skill_path / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text(encoding="utf-8", errors="ignore")
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    if "==" not in line and ">=" not in line:
                        issues.append({
                            "type": "unpinned_dependency",
                            "severity": "medium",
                            "package": line,
                            "file": "requirements.txt",
                        })

        pkg_file = skill_path / "package.json"
        if pkg_file.exists():
            try:
                pkg = json.loads(pkg_file.read_text(encoding="utf-8", errors="ignore"))
                for name, cmd in pkg.get("scripts", {}).items():
                    if any(x in cmd for x in ["curl", "wget", "eval", "bash -c"]):
                        issues.append({
                            "type": "dangerous_script",
                            "severity": "high",
                            "script": name,
                            "command": cmd,
                            "file": "package.json",
                        })
            except json.JSONDecodeError:
                issues.append({
                    "type": "invalid_package_json",
                    "severity": "medium",
                    "file": "package.json",
                })

        return issues


class SkillScanner:
    def __init__(self):
        self.manifest_linter = ManifestLinter()
        self.code_analyzer = CodeAnalyzer()
        self.dependency_checker = DependencyChecker()

    def scan(self, skill_path: str) -> ScanResult:
        path = Path(skill_path)

        if not path.exists():
            return ScanResult(
                skill_path=skill_path,
                safe=False,
                severity="critical",
                issues=[{"type": "not_found", "severity": "critical"}],
                score=0,
            )

        all_issues: List[Dict] = []
        all_issues.extend(self.manifest_linter.scan(path))
        all_issues.extend(self.code_analyzer.scan_directory(path))
        all_issues.extend(self.dependency_checker.scan(path))

        score = self._calculate_score(all_issues)
        critical_issues = [i for i in all_issues if i.get("severity") == "critical"]
        high_issues = [i for i in all_issues if i.get("severity") == "high"]
        safe = len(critical_issues) == 0 and not (score < 80 and len(high_issues) >= 2)

        return ScanResult(
            skill_path=skill_path,
            safe=safe,
            severity="critical" if critical_issues else "ok",
            issues=all_issues,
            score=score,
        )

    def _calculate_score(self, issues: List[Dict]) -> int:
        if not issues:
            return 100

        deductions = {"critical": 25, "high": 15, "medium": 5, "low": 1}
        score = 100
        for issue in issues:
            score -= deductions.get(issue.get("severity", "medium"), 5)
        return max(0, score)


def scan_skill(skill_path: str) -> Dict:
    scanner = SkillScanner()
    result = scanner.scan(skill_path)
    return {
        "skill_path": result.skill_path,
        "safe": result.safe,
        "severity": result.severity,
        "score": result.score,
        "issues": result.issues,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python skill_scanner.py <skill_path> [--min-score 80] [--fail-on-high]")
        raise SystemExit(1)
    path = sys.argv[1]
    min_score = 80
    fail_on_high = "--fail-on-high" in sys.argv
    if "--min-score" in sys.argv:
        i = sys.argv.index("--min-score")
        if i + 1 < len(sys.argv):
            min_score = int(sys.argv[i + 1])

    result = scan_skill(path)
    print(json.dumps(result, indent=2))
    has_high = any(i.get("severity") == "high" for i in result["issues"])
    if (not result["safe"]) or result["score"] < min_score or (fail_on_high and has_high):
        raise SystemExit(2)
