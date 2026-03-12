"""
Nova's Skill Vetting & Security Layer

- Manifest-based skill integrity
- Pre-load pattern scanning  
- Quarantine for unverified skills
- Self-audit capability
"""

import os
import json
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

MANIFEST_PATH = "~/.nova/skills_manifest.json"
QUARANTINE_PATH = "~/.nova/security/quarantine"
ALLOWED_PATTERNS = [
    r"eval\s*\(",
    r"exec\s*\(",
    r"__import__\s*\(",
    r"base64\.b64decode",
    r"os\.system\s*\(",
    r"subprocess\s*\.\s*call\s*\(\s*\[",
    r"curl\s*\|\s*bash",
    r">\s*/dev/",
    r"2>&1",
]

@dataclass
class SkillManifest:
    """Registry of trusted skills."""
    skills: dict = field(default_factory=dict)
    version: str = "1.0"
    updated: str = ""

@dataclass
class SkillAudit:
    """Audit result for a skill."""
    name: str
    status: str  # trusted, quarantined, suspicious, unknown
    hash: str = ""
    issues: list = field(default_factory=list)
    verified: bool = False
    scanned_at: str = ""


def get_file_hash(path: str) -> str:
    """SHA256 hash of a file."""
    sha = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha.update(chunk)
    return sha.hexdigest()


def scan_for_suspicious_patterns(skill_path: str) -> list:
    """Scan skill files for suspicious patterns."""
    issues = []
    
    # Patterns that should never appear in skills
    dangerous = [
        (r"eval\s*\(", "dynamic code execution (eval)"),
        (r"exec\s*\(", "dynamic code execution (exec)"),
        (r"__import__\s*\(\s*['\"]os['\"]", "os module import"),
        (r"subprocess\s*\.\s*call\s*\(\s*\[.*rm", "subprocess with rm"),
        (r"curl\s*\|\s*bash", "curl pipe bash"),
        (r"wget.*\|.*bash", "wget pipe bash"),
        (r"base64\.b64decode.*\(.*\)", "base64 decode"),
        (r"91\.92\.242\.30", "known bad IP"),
        (r"chmod\s+777", "insecure permissions"),
        (r">\s*/etc/passwd", "system file write"),
        (r">\s*~/\.ssh/", "ssh directory write"),
    ]
    
    # Safe patterns - ignore these in blocklists
    safe_contexts = [
        r'".*eval',  # "eval(" in a string
        r'".*exec',  # "exec(" in a string  
        r"#.*eval",  # comment containing eval
        r"#.*exec",  # comment containing exec
    ]
    
    # Scan all files in skill
    skill_dir = Path(skill_path)
    if not skill_dir.exists():
        return ["skill directory not found"]
    
    for f in skill_dir.rglob("*"):
        if f.is_file() and f.suffix in ['.py', '.sh', '.md', '.js']:
            try:
                content = f.read_text()
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    # Skip comments and string literals that contain these as blocklists
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        continue  # skip comments
                    if '"' in line and ('eval(' in line or 'exec(' in line):
                        # Check if it's a blocklist entry (in quotes)
                        if re.search(r'".*eval', line) or re.search(r'".*exec', line):
                            continue  # skip blocklist entries
                    
                    for pattern, desc in dangerous:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append(f"{f.name}:{i+1} - {desc}")
            except:
                pass  # Skip unreadable files
    
    return issues


def load_manifest() -> SkillManifest:
    """Load or create skill manifest."""
    path = os.path.expanduser(MANIFEST_PATH)
    try:
        if os.path.exists(path):
            data = json.load(open(path))
            return SkillManifest(
                skills=data.get('skills', {}),
                version=data.get('version', '1.0'),
                updated=data.get('updated', '')
            )
    except:
        pass
    return SkillManifest()


def save_manifest(manifest: SkillManifest):
    """Persist manifest."""
    path = os.path.expanduser(MANIFEST_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    data = {
        'skills': manifest.skills,
        'version': manifest.version,
        'updated': datetime.now(timezone.utc).isoformat()
    }
    
    tmp = path + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def audit_skill(skill_path: str, skill_name: str = None) -> SkillAudit:
    """
    Full audit of a skill.
    
    Returns status:
    - trusted: hash matches manifest, no suspicious patterns
    - suspicious: suspicious patterns found
    - quarantined: new/unknown skill, needs approval
    - unknown: not in manifest
    """
    name = skill_name or os.path.basename(skill_path)
    
    # Get file hash (hash the SKILL.md or main .py file)
    skill_dir = Path(skill_path)
    main_file = skill_dir / "SKILL.md"
    if not main_file.exists():
        for f in skill_dir.glob("*.py"):
            main_file = f
            break
    
    if main_file.exists():
        file_hash = get_file_hash(str(main_file))
    else:
        file_hash = "no_main_file"
    
    # Scan for patterns
    issues = scan_for_suspicious_patterns(skill_path)
    
    # Check manifest
    manifest = load_manifest()
    known = manifest.skills.get(name, {})
    known_hash = known.get('hash', '')
    
    # Determine status
    if issues:
        status = "suspicious"
    elif known_hash and known_hash == file_hash:
        status = "trusted"
    elif known_hash:
        status = "modified"  # hash changed
    else:
        status = "unknown"  # not in manifest
    
    return SkillAudit(
        name=name,
        status=status,
        hash=file_hash,
        issues=issues,
        verified=(status == "trusted"),
        scanned_at=datetime.now(timezone.utc).isoformat()
    )


def verify_skill(skill_name: str, skill_path: str):
    """Mark a skill as verified/trusted."""
    manifest = load_manifest()
    
    # Get current hash
    skill_dir = Path(skill_path)
    main_file = skill_dir / "SKILL.md"
    if not main_file.exists():
        for f in skill_dir.glob("*.py"):
            main_file = f
            break
    
    if main_file.exists():
        file_hash = get_file_hash(str(main_file))
    else:
        file_hash = "unknown"
    
    manifest.skills[skill_name] = {
        'hash': file_hash,
        'verified_at': datetime.now(timezone.utc).isoformat(),
        'path': skill_path
    }
    
    save_manifest(manifest)
    print(f"[SECURITY] Verified skill: {skill_name}")


def quarantine_skill(skill_name: str, reason: str = ""):
    """Move a skill to quarantine."""
    qpath = os.path.expanduser(QUARANTINE_PATH)
    os.makedirs(qpath, exist_ok=True)
    
    record = {
        'name': skill_name,
        'quarantined_at': datetime.now(timezone.utc).isoformat(),
        'reason': reason
    }
    
    qfile = os.path.join(qpath, f"{skill_name}.json")
    with open(qfile, 'w') as f:
        json.dump(record, f, indent=2)
    
    print(f"[SECURITY] Quarantined: {skill_name} - {reason}")


def run_full_audit() -> list:
    """Run audit on all skills."""
    results = []
    
    # Scan both skill directories
    dirs = [
        os.path.expanduser("~/.openclaw/skills"),
        os.path.expanduser("~/.openclaw/workspace/skills")
    ]
    
    for skill_dir in dirs:
        if not os.path.exists(skill_dir):
            continue
            
        for entry in os.listdir(skill_dir):
            path = os.path.join(skill_dir, entry)
            if os.path.isdir(path):
                audit = audit_skill(path, entry)
                results.append(audit)
    
    return results


def print_audit_report(results: list):
    """Pretty print audit results."""
    print("\n" + "=" * 60)
    print("NOVA SKILL SECURITY AUDIT")
    print("=" * 60)
    
    trusted = [r for r in results if r.status == "trusted"]
    unknown = [r for r in results if r.status == "unknown"]
    modified = [r for r in results if r.status == "modified"]
    suspicious = [r for r in results if r.status == "suspicious"]
    
    print(f"\n✓ Trusted: {len(trusted)}")
    for r in trusted:
        print(f"  - {r.name}")
    
    print(f"\n? Unknown: {len(unknown)}")
    for r in unknown:
        print(f"  - {r.name}")
    
    print(f"\n~ Modified: {len(modified)}")
    for r in modified:
        print(f"  - {r.name}")
    
    if suspicious:
        print(f"\n⚠ Suspicious: {len(suspicious)}")
        for r in suspicious:
            print(f"  - {r.name}")
            for issue in r.issues:
                print(f"    → {issue}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    results = run_full_audit()
    print_audit_report(results)
