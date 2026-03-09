#!/usr/bin/env python3
"""
Security Scanner - Scan for unsafe code patterns
"""

import os
import re
from pathlib import Path

SUSPICIOUS_PATTERNS = [
    ("eval(", "dynamic code execution"),
    ("exec(", "dynamic code execution"),
    ("pickle.loads", "unsafe deserialization"),
    ("__import__(", "dynamic imports"),
    ("subprocess.call", "shell command execution"),
    ("os.system", "shell command execution"),
    ("input(", "user input as code"),
    ("compile(", "dynamic compilation"),
]

HARDCODED_SECRETS = [
    r"sk-[a-zA-Z0-9]{20,}",
    r"password\s*=\s*['\"][^'\"]{8,}",
    r"api_key\s*=\s*['\"][^'\"]{8,}",
    r"secret\s*=\s*['\"][^'\"]{8,}",
]

def scan_file(path: str) -> list:
    """Scan a single file for security issues"""
    problems = []
    
    try:
        with open(path, "r", errors="ignore") as f:
            content = f.read()
            lines = content.split("\n")
            
        for i, line in enumerate(lines, 1):
            # Check suspicious patterns
            for pattern, desc in SUSPICIOUS_PATTERNS:
                if pattern in line:
                    problems.append({
                        "file": path,
                        "line": i,
                        "pattern": pattern,
                        "description": desc,
                        "severity": "HIGH"
                    })
            
            # Check for hardcoded secrets
            for secret_re in HARDCODED_SECRETS:
                if re.search(secret_re, line, re.IGNORECASE):
                    problems.append({
                        "file": path,
                        "line": i,
                        "pattern": "hardcoded_secret",
                        "description": "potential hardcoded secret",
                        "severity": "CRITICAL"
                    })
                    
    except Exception as e:
        problems.append({
            "file": path,
            "error": str(e)
        })
    
    return problems

def scan_directory(root: str, extensions=None) -> dict:
    """Scan directory for security issues"""
    if extensions is None:
        extensions = [".py"]
    
    findings = {
        "files_scanned": 0,
        "issues": [],
        "by_severity": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    }
    
    root_path = Path(root)
    
    for path in root_path.rglob("*"):
        if path.is_file() and path.suffix in extensions:
            findings["files_scanned"] += 1
            issues = scan_file(str(path))
            findings["issues"].extend(issues)
            
            for issue in issues:
                sev = issue.get("severity", "MEDIUM")
                if sev in findings["by_severity"]:
                    findings["by_severity"][sev] += 1
    
    return findings


def print_security_report(findings):
    """Print security scan results"""
    print("=" * 60)
    print("NOVA SECURITY SCAN")
    print("=" * 60)
    print(f"Files scanned: {findings['files_scanned']}")
    print(f"Total issues: {len(findings['issues'])}")
    print("")
    print("By severity:")
    for sev, count in findings["by_severity"].items():
        emoji = "🔴" if sev == "CRITICAL" else "🟠" if sev == "HIGH" else "🟡"
        print(f"  {emoji} {sev}: {count}")
    
    if findings["issues"]:
        print("\nIssues found:")
        for issue in findings["issues"][:10]:
            if "error" in issue:
                print(f"  ❌ {issue['file']}: {issue['error']}")
            else:
                print(f"  ⚠️ {issue['file']}:{issue['line']} - {issue['description']}")
        
        if len(findings["issues"]) > 10:
            print(f"  ... and {len(findings['issues']) - 10} more")
    
    print("=" * 60)
    return len(findings["issues"]) == 0


if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "nova"
    findings = scan_directory(root)
    success = print_security_report(findings)
    sys.exit(0 if success else 1)
