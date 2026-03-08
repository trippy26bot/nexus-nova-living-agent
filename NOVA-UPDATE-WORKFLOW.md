# Nova Update Workflow

## When Caine gives you a fix:

1. Replace the file in ~/nexus-nova/
2. Bump version in SKILL.md (1.0.0 → 1.0.1)
3. Add entry to CHANGELOG.md
4. Commit and push:
   cd ~/nexus-nova && git add . && git commit -m "fix: [what]" && git push

## If push fails:
Tell Caine: "Need a fresh token."
