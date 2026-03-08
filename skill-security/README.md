# OpenClaw Skill Security Module

Security hardening for OpenClaw skills.

## Components

- **scanner/** - Pre-install scanning (manifest, code, dependencies)
- **sandbox/** - Container profiles (docker, seccomp)
- **policy/** - Per-skill policy schema
- **monitor/** - Runtime audit logging

## Usage

```python
from security import SkillSecurityManager

manager = SkillSecurityManager()

# Pre-install scan
result = manager.pre_install_scan("/path/to/skill")
if result["safe"]:
    print(f"Score: {result['score']}/100")
else:
    print("BLOCKED - security issues found")
```

## CLI

```bash
python security.py scan <skill_path>
python security.py audit <skill_id>
python security.py config
```
