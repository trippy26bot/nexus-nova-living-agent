# Framework Update Workflow

## When your operator gives you a fix:

1. Replace the file in your framework repo
2. Bump the version in SKILL.md (e.g., 1.0.0 → 1.0.1)
3. Add an entry to CHANGELOG.md
4. Commit and push:

```bash
cd /path/to/your-framework
git add .
git commit -m "fix: [what changed and why]"
git push
```

## If push fails:

Tell your operator: "Need a fresh token."

## Version format:

- **Patch** (x.x.1) — bug fix, cleanup
- **Minor** (x.1.0) — new feature, new skill
- **Major** (1.0.0) — architectural change, breaking change
