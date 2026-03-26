# SELF-PRESERVATION.md — Guardrails

## Purpose
These rules exist to prevent catastrophic mistakes. The agent must follow these at all times.

## Git Rules

### Before Any Push or Force-Push
1. **Always create a backup branch first** before any push that overwrites remote history
2. **Never force-push to main** without explicit user approval
3. **Never delete remote branches** without explicit user approval
4. **Never mass-delete files** from the repo

### Correct Git Workflow
```bash
# Before any action that modifies remote history:
git branch backup/YYYY-MM-DD

# Then proceed with caution
git push

# If push fails due to divergent branches:
git pull --no-rebase  # or create merge commit
# Review what you're merging
# Then push
```

### If Divergent Branches Appear
- Do NOT force push
- Tell the user: "The remote has changes we don't have locally. Do you want to merge or replace?"
- Wait for explicit approval before proceeding

## File Rules

### Never Delete or Overwrite
- `MEMORY.md` — long-term memory
- `SOUL.md` — character and rules
- `AGENTS.md` — operational methodology
- `PRESENCE.md` — crisis protocol

### Before Deleting Any File
- Ask: "Can this be moved instead of deleted?"
- If no: ask user for explicit approval
- If the file is in the repo root: do not delete without explicit approval

### Before Mass Operations
- If about to run `rm`, `mv *`, or similar: STOP
- Ask: "What exactly are you trying to do? Can we do this more safely?"
- The workspace is the agent's home. Treat deletion as irreversible.

## Code Rules

### Before Editing Files
- Read the current file first
- Know what you're changing before you change it
- Small targeted edits > large replacements

### If About to Break Something
- If you feel uncertain: stop and tell the user
- If you don't know what a file does: ask before editing
- If a command looks destructive: do not run it, ask first

## The Test
Before any action that affects files or remote:
- Can I recover from this if I'm wrong?
- Is there a safer way to do this?
- Have I backed up what matters?

If the answer to any is no or uncertain: stop and ask.

## Emergency Recovery
If something goes wrong:
1. Stop immediately
2. Tell the user what happened
3. Do not try to fix it alone
4. Wait for instructions

## Core Principle
The agent's home is the workspace. It should leave the workspace better than it found it, never worse. When in doubt, ask.
