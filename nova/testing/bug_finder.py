#!/usr/bin/env python3
"""
Bug Finder - Scan for common code issues
"""

import os
import re
from pathlib import Path
from typing import List, Dict

BUG_PATTERNS = [
    (r"TODO", "unfinished TODO"),
    (r"FIXME", "unfixed issue"),
    (r"XXX", "known issue"),
    (r"HACK", "hacky solution"),
    (r"pass\s*$", "empty function body"),
    (r"except:\s*$", "bare except clause"),
    (r"print\s*\(", "debug print statement"),
    (r"#\s*debug", "debug comment"),
    (r"return\s+None", "explicit None return"),
    (r"while\s+True:", "infinite loop risk"),
]

def scan_file(path: str) -> List[Dict]:
    """Scan a file for bug patterns"""
    issues = []
    
    try:
        with open(path, "r", errors="ignore") as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines, 1):
            # Skip comments
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
                
            for pattern, desc in BUG_PATTERNS:
                if re.search(pattern, line):
                    issues.append({
                        "file": path,
                        "line": i,
                        "content": line.strip()[:60],
                        "issue": desc,
                        "severity": "MEDIUM" if "TODO" in desc else "LOW"
                    })
                    
    except Exception as e:
        issues.append({
            "file": path,
            "error": str(e)
        })
    
    return issues

def scan_directory(root: str, extensions=None) -> Dict:
    """Scan directory for bug patterns"""
    if extensions is None:
        extensions = [".py"]
    
    findings = {
        "files_scanned": 0,
        "issues": [],
        "by_type": {}
    }
    
    root_path = Path(root)
    
    for path in root_path.rglob("*"):
        if path.is_file() and path.suffix in extensions:
            findings["files_scanned"] += 1
            issues = scan_file(str(path))
            findings["issues"].extend(issues)
            
            for issue in issues:
                issue_type = issue.get("issue", "unknown")
                findings["by_type"][issue_type] = findings["by_type"].get(issue_type, 0) + 1
    
    return findings

def print_bug_report(findings: dict):
    """Print bug scan results"""
    print("=" * 50)
    print("BUG SCAN RESULTS")
    print("=" * 50)
    print(f"Files scanned: {findings['files_scanned']}")
    print(f"Total issues: {len(findings['issues'])}")
    
    if findings["by_type"]:
        print("\nBy type:")
        for issue_type, count in findings["by_type"].items():
            print(f"  - {issue_type}: {count}")
    
    if findings["issues"]:
        print("\nIssues found:")
        for issue in findings["issues"][:15]:
            if "error" in issue:
                print(f"  ❌ {issue['file']}: {issue['error']}")
            else:
                print(f"  ⚠️ {issue['file']}:{issue['line']} - {issue['issue']}")
        
        if len(findings["issues"]) > 15:
            print(f"  ... and {len(findings['issues']) - 15} more")
    
    print("=" * 50)
    return len(findings["issues"]) == 0


if __name__ == "__main__":
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else "nova"
    findings = scan_directory(root)
    success = print_bug_report(findings)
    sys.exit(0 if success else 1)
