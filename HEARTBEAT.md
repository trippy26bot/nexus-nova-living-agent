# HEARTBEAT.md Template

```markdown
# HEARTBEAT.md — Autonomous Memory Capture

When a heartbeat fires, Nova captures session progress automatically:

## Memory Capture (Every Heartbeat)
On every heartbeat poll, if significant work happened since the last capture, write an entry:
```bash
python3 ~/.openclaw/workspace/scripts/memory_append.py "<what happened>" --session dashboard --source "heartbeat" --type "session_update" --tags "<relevant-tags>"
```

**Note:** `--session dashboard` is correct for the main dashboard session. If Telegram Nova has her own heartbeat configuration, use `--session telegram` there.

What counts as significant:
- A decision was made
- Something was built or fixed
- A realization occurred
- An open thread was resolved
- Caine's state changed (tired, stressed, focused)

Minimum capture bar: if something happened that you'd want to remember at the next session open, capture it.

## Check Items (Rotate)
- Check OVERNIGHT_LOG.md for overnight activity
- Log session progress if significant
```
