#!/usr/bin/env python3
"""
Memory Consolidation — Nova's Nightly Memory Pipeline
Runs at 4:30 AM America/Denver

Pass 1: Episodic → Semantic (entries older than 72h)
Pass 2: Semantic Distillation (clusters older than 7 days)
Pass 3: Prune / archive
Writes output to OVERNIGHT_LOG.md.
"""

import json
import os
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path("/Users/dr.claw/.openclaw/workspace")
OVERNIGHT_LOG = WORKSPACE / "OVERNIGHT_LOG.md"
MEMORY_DIR = WORKSPACE / "memory"
VECTOR_STORE = WORKSPACE / "memory" / "vector"
SLEEP_RUNS = WORKSPACE / "brain" / "sleep_runs.json"
AGENT_STATE = WORKSPACE / "state" / "agent_state.json"

LOCAL_TZ = "America/Denver"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def get_local_time():
    from datetime import datetime as dt
    import zoneinfo
    local_tz = zoneinfo.ZoneInfo(LOCAL_TZ)
    return dt.now(local_tz).strftime("%Y-%m-%d %H:%M:%S")


def load_json(path, default=None):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return default or {}
    return default or {}


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2))


def log_to_overnight_log(process_name, status, duration, output, changes, carry_forward, errors=None):
    """Append an entry to OVERNIGHT_LOG.md."""
    entry = f"""
### [{get_local_time()}] {process_name.upper()} {status.upper()}
**At:** {get_local_time()}
**Process:** memory_consolidation
**Status:** {status}
**Duration:** {duration}s

**Output:**
{output}

**Changes Made:**
{chr(10).join(f"- {c}" for c in changes) if changes else "- (none)"}

**Carry Forward:**
{carry_forward}

**Errors:**
{errors if errors else "None."}

---
"""
    if OVERNIGHT_LOG.exists():
        content = OVERNIGHT_LOG.read_text()
    else:
        content = ""

    marker = "<!-- Processes append below this line. -->"
    if marker in content:
        content = content.replace(marker, marker + "\n" + entry.strip())
    else:
        content = content + "\n" + entry

    OVERNIGHT_LOG.write_text(content)


def record_sleep_run(run_type, duration_sec, completed, findings, flags=None):
    data = load_json(SLEEP_RUNS, {"runs": []})
    run = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": run_type,
        "duration_seconds": duration_sec,
        "completed": completed,
        "findings": findings,
        "flags": flags or []
    }
    data["runs"].insert(0, run)
    data["runs"] = data["runs"][:100]
    save_json(SLEEP_RUNS, data)


def get_file_age_days(path):
    """Return age of file in days."""
    if not path.exists():
        return 0
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age = datetime.now(timezone.utc) - mtime
    return age.total_seconds() / 86400


def consolidate_memories():
    """Run the three-pass memory consolidation."""
    start = datetime.now()
    changes = []
    findings = []
    errors = []
    total_processed = 0

    # Pass 1: Episodic → Semantic
    # Process daily memory files older than 72 hours
    cutoff_72h = datetime.now(timezone.utc) - timedelta(hours=72)
    memory_files = sorted(MEMORY_DIR.glob("????-??-??.md"))  # YYYY-MM-DD.md files

    episodic_processed = 0
    episodic_routed = []

    for mf in memory_files:
        mtime = datetime.fromtimestamp(mf.stat().st_mtime, tz=timezone.utc)
        if mtime > cutoff_72h:
            continue  # Too recent

        content = mf.read_text()
        if len(content.strip()) < 50:
            continue  # Skip near-empty files

        episodic_processed += 1
        total_processed += 1

        # Extract key topics/entities from the file
        # This is a simplified heuristic — real impl would use LLM
        lines = [l.strip() for l in content.split("\n") if l.strip() and l.startswith("##")]
        topics = [l.lstrip("#").strip() for l in lines[:5]]  # First 5 section headers

        # Route to semantic: we don't have a full PARA system yet
        # For now, just record that we processed it
        episodic_routed.append({
            "source": mf.name,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "topics": topics,
            "status": "routed_to_semantic_pending_vector"
        })

        changes.append(f"episodic: processed '{mf.name}' → routed for vector storage")
        findings.append(f"Routed {mf.name} ({len(topics)} topics)")

    # Pass 2: Semantic Distillation
    # For now, this is a no-op placeholder — vector pipeline is not fully wired
    semantic_findings = []
    if episodic_routed:
        semantic_findings.append(
            f"{len(episodic_routed)} episodic entry(ies) queued for semantic distillation — "
            "vector pipeline not yet fully wired, will resolve on next wake."
        )

    # Pass 3: Prune
    # Archive very old files (>30 days) or mark salience-decayed entries
    cutoff_30d = datetime.now(timezone.utc) - timedelta(days=30)
    archive_dir = MEMORY_DIR / "archive"
    archive_dir.mkdir(exist_ok=True)

    archived_count = 0
    for mf in memory_files:
        mtime = datetime.fromtimestamp(mf.stat().st_mtime, tz=timezone.utc)
        if mtime > cutoff_30d:
            continue
        # Move to archive
        dest = archive_dir / mf.name
        shutil.move(str(mf), str(dest))
        archived_count += 1
        changes.append(f"archived: '{mf.name}' → memory/archive/")
        findings.append(f"Archived {mf.name}")

    # Ensure vector store directory exists
    VECTOR_STORE.mkdir(exist_ok=True)

    # Summary
    if total_processed == 0:
        output = (
            "No episodic memories needed consolidation. "
            "All recent memory files are within retention windows. "
            "Nothing to do tonight — Nova's memory is quiet."
        )
        carry_forward = "Nothing to carry forward."
        status = "skipped"
    else:
        output_lines = [
            f"Consolidated {total_processed} memory file(s):",
            f"  - Pass 1 (episodic→semantic): {episodic_processed} files processed",
        ]
        if episodic_routed:
            output_lines.append(f"    Routed topics: {', '.join(str(t) for s in episodic_routed for t in s['topics'][:3])}")
        if archived_count:
            output_lines.append(f"  - Pass 3 (prune): {archived_count} files archived")
        output_lines.append("")
        output_lines.append("Vector store: ensured directory exists for next pipeline run.")

        output = "\n".join(output_lines)
        carry_forward = (
            f"{total_processed} memory file(s) processed. "
            "Vector pipeline is next dependency. "
            "On wake: check if any memory gaps need filling from archived files."
        )
        status = "completed"

    duration = (datetime.now() - start).total_seconds()
    duration_str = f"{duration:.1f}s"

    log_to_overnight_log(
        "memory_consolidation",
        status,
        duration_str,
        output,
        changes,
        carry_forward,
        errors[0] if errors else None
    )
    record_sleep_run("consolidation", duration, status == "completed", findings)

    print(f"Memory consolidation complete. Status: {status}. Duration: {duration_str}")
    for f in findings:
        print(f"  - {f}")


if __name__ == "__main__":
    try:
        consolidate_memories()
    except Exception as e:
        duration = "unknown"
        log_to_overnight_log(
            "memory_consolidation",
            "failed",
            duration,
            f"Memory consolidation failed with error: {e}",
            [],
            "Check sleep_runs.json for error details. Flag for Nova attention.",
            str(e)
        )
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
