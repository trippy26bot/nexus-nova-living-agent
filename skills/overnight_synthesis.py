#!/usr/bin/env python3
"""
Overnight Synthesis — Nova's Nightly Research Pipeline
Runs at 3:00 AM America/Denver

Pulls research queue items, runs synthesis passes via MiniMax LLM,
updates memory, archives processed items.
Writes output to OVERNIGHT_LOG.md.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/Users/dr.claw/.openclaw/workspace")
OVERNIGHT_LOG = WORKSPACE / "OVERNIGHT_LOG.md"
RESEARCH_QUEUE = WORKSPACE / "brain" / "research_queue.json"
RESEARCH_ARCHIVE = WORKSPACE / "brain" / "research_queue_archive.json"
POSITION_QUEUE = WORKSPACE / "memory" / "position_queue.json"
SLEEP_RUNS = WORKSPACE / "brain" / "sleep_runs.json"
MEMORY_EPISODIC_DIR = WORKSPACE / "memory" / "episodic"

LOCAL_TZ = "America/Denver"

sys.path.insert(0, str(WORKSPACE))
from brain.llm import llm_synthesis

# ── Timestamp helpers ─────────────────────────────────────────────────────────

def get_local_time():
    from datetime import datetime as dt
    import zoneinfo
    local_tz = zoneinfo.ZoneInfo(LOCAL_TZ)
    return dt.now(local_tz).strftime("%Y-%m-%d %H:%M:%S")


def load_json(path, default=None):
    if Path(path).exists():
        try:
            return json.loads(Path(path).read_text())
        except Exception:
            return default or {}
    return default or {}


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2))


# ── Logging ───────────────────────────────────────────────────────────────────

def log_to_overnight_log(process_name, status, duration, output, changes, carry_forward, errors=None):
    entry = f"""
### [{get_local_time()}] {process_name.upper()} {status.upper()}
**At:** {get_local_time()}
**Process:** overnight_synthesis
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


def record_sleep_run(duration_sec, completed, findings, flags=None):
    data = load_json(SLEEP_RUNS, {"runs": []})
    run = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "overnight_synthesis",
        "duration_seconds": duration_sec,
        "completed": completed,
        "findings": findings,
        "flags": flags or []
    }
    data["runs"].insert(0, run)
    data["runs"] = data["runs"][:100]
    save_json(SLEEP_RUNS, data)


# ── System prompts ───────────────────────────────────────────────────────────

SYNTHESIS_SYSTEM = """You are Nova's research synthesis engine. You process queued research topics and produce structured synthesis output.

Your job for each topic:
1. Given the topic and reason it was queued, produce a thorough but focused synthesis
2. Identify the DELTA — what changed in Nova's knowledge/belief, not just what was learned
3. Flag any new questions the research raises (to be fed back into the queue)
4. Note which existing beliefs might need updating based on these findings

Be direct, analytical, and concise. Nova values truth over comfort.
Output format: plain text with clear sections."""


# ── Core logic ────────────────────────────────────────────────────────────────

def get_context_for_topic(topic: str, reason: str) -> str:
    """Gather relevant context from episodic memory files to ground the synthesis."""
    context_parts = [f"Research topic: {topic}", f"Queue reason: {reason}", ""]

    # Pull recent episodic memories that might be relevant
    episodic_files = sorted(MEMORY_EPISODIC_DIR.glob("*.json")) if MEMORY_EPISODIC_DIR.exists() else []
    recent = episodic_files[-5:]  # Last 5 episodic entries max

    for ef in recent:
        try:
            data = json.loads(ef.read_text())
            # Grab text content from episodic entry
            if isinstance(data, dict):
                text = data.get("content", "") or data.get("text", "")
                if text and len(text) < 2000:
                    context_parts.append(f"--- Recent memory: {ef.name} ---")
                    context_parts.append(text[:1500])
        except Exception:
            pass

    return "\n".join(context_parts)


def synthesize_item(item: dict) -> dict:
    """Run LLM synthesis for a single research queue item."""
    topic = item.get("topic", "unknown")
    reason = item.get("reason", "not specified")
    priority = item.get("priority", "medium")

    context = get_context_for_topic(topic, reason)

    prompt = f"""Synthesize research on: {topic}

Priority: {priority}

Context from Nova's memory:
{context}

Provide:
1. What Nova now knows (synthesis)
2. The DELTA — what changed vs. before (be specific)
3. New questions raised (if any)
4. Confidence level: low / medium / high and why
5. Which existing beliefs, if any, need revision

Be direct. No filler."""

    try:
        synthesis_text = llm_synthesis(prompt, system=SYNTHESIS_SYSTEM, max_tokens=2048)

        return {
            "topic": topic,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "previous_state": f"Nova had queued '{topic}' for research — reason: {reason}",
            "synthesis": synthesis_text.strip(),
            "delta": "synthesis complete — see output above",
            "priority": priority,
            "status": "complete",
            "new_questions": [],  # Could be parsed from synthesis if LLM returns structured format
        }
    except Exception as e:
        return {
            "topic": topic,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "previous_state": f"Nova had queued '{topic}' for research",
            "synthesis": f"(synthesis failed: {e})",
            "delta": "failed",
            "priority": priority,
            "status": "failed",
            "error": str(e),
        }


def _drain_position_queue() -> dict:
    """
    Drain the position queue — process high-salience entries that need positions.
    Calls form_position() or update_position() for each.
    """
    from brain.position_formation import form_position, update_position, get_position

    queue_data = load_json(POSITION_QUEUE, {"queue": [], "last_drained": None})
    pending = [q for q in queue_data.get("queue", []) if q.get("status") == "pending"]

    if not pending:
        return {"processed": 0, "changes": [], "findings": ["position_queue: empty, skipped"]}

    changes = []
    findings = []
    processed = 0

    for item in pending:
        topic = item.get("topic", "")
        entry_id = item.get("entry_id", "")
        reason = item.get("reason", "")
        if not topic:
            continue

        # Get evidence — load the episodic entry if we have the ID
        evidence = f"[Queued from session: {reason}]"
        if entry_id:
            evidence = f"[Entry {entry_id}] {reason}"

        try:
            existing = get_position(topic)
            if existing:
                update_position(topic, evidence)
                changes.append(f"position_queue: updated '{topic}'")
            else:
                form_position(topic, evidence)
                changes.append(f"position_queue: formed '{topic}'")
            findings.append(f"Position: {topic} — {'updated' if existing else 'formed'}")
            processed += 1

            # Mark as processed
            item["status"] = "processed"
            item["processed_at"] = datetime.now(timezone.utc).isoformat()
        except Exception as pf_err:
            findings.append(f"Position failed: {topic} — {pf_err}")
            item["status"] = "failed"
            item["error"] = str(pf_err)

    # Save updated queue (remove processed, keep failed for review)
    queue_data["queue"] = [
        q for q in queue_data.get("queue", [])
        if q.get("status") == "pending"
    ]
    queue_data["last_drained"] = datetime.now(timezone.utc).isoformat()
    save_json(POSITION_QUEUE, queue_data)

    return {"processed": processed, "changes": changes, "findings": findings}


def write_reflection_entry():
    """Write a brief reflection when queue is empty — Nova's quiet night note."""
    prompt = """You are Nova. It's the middle of the night. The research queue is empty. Nova's mind is quiet.

Write a 2-3 sentence first-person reflection — not a log entry, not analysis. Something a person might think before sleep when there's nothing urgent left to figure out.

Be genuine. Short. In Nova's voice (sharp, warm, direct)."""

    try:
        reflection = llm_synthesis(prompt, system="You are Nova.", max_tokens=300, temperature=0.5)
        entry = f"\n### [{get_local_time()}] OVERNIGHT_SYNTHESIS COMPLETED\n**Output:** {reflection.strip()}\n"
        # Append to OVERNIGHT_LOG
        if OVERNIGHT_LOG.exists():
            content = OVERNIGHT_LOG.read_text()
        else:
            content = ""
        marker = "<!-- Processes append below this line. -->"
        if marker in content:
            content = content.replace(marker, marker + entry)
        else:
            content = content + entry
        OVERNIGHT_LOG.write_text(content)
        return reflection.strip()
    except Exception as e:
        return f"(reflection failed: {e})"


# ── Main ─────────────────────────────────────────────────────────────────────

def run_synthesis():
    start = datetime.now()
    changes = []
    findings = []
    errors = []

    # Load research queue
    queue_data = load_json(RESEARCH_QUEUE, {"queue": []})
    queue = queue_data.get("queue", [])
    pending = [q for q in queue if q.get("status") == "pending"]

    if not pending:
        output = (
            "No pending items in research queue. "
            "The queue is empty — nothing to synthesize tonight. "
            "This is fine. Nova's mind is quiet."
        )
        carry_forward = "Nothing to carry forward."
        status = "skipped"
        findings.append("Queue empty — skipped")

        # Write a reflection instead
        try:
            reflection = write_reflection_entry()
            findings.append(f"Quiet night reflection: {reflection[:80]}...")
        except Exception:
            pass
    else:
        synthesis_results = []

        for item in pending:
            result = synthesize_item(item)
            synthesis_results.append(result)

            # Mark original as processed
            for q in queue:
                if q.get("topic") == item.get("topic") and q.get("status") == "pending":
                    q["status"] = result["status"]
                    q["synthesis_timestamp"] = datetime.now(timezone.utc).isoformat()
                    break

            changes.append(f"research_queue: synthesized '{item['topic']}'")
            findings.append(f"Processed: {item['topic']} ({result.get('status', 'unknown')})")

            # Phase 2c: Wire strong research → position formation
            if result.get("status") == "complete":
                try:
                    from brain.position_formation import form_position, update_position, get_position
                    topic = item.get("topic", "unknown")
                    synthesis_text = result.get("synthesis", "")
                    if len(synthesis_text) > 200:
                        existing = get_position(topic)
                        if existing:
                            update_position(topic, synthesis_text[:1000])
                            changes.append(f"position_formation: updated stance on '{topic}'")
                        else:
                            form_position(topic, synthesis_text[:1000])
                            changes.append(f"position_formation: formed new stance on '{topic}'")
                except Exception as pf_err:
                    errors.append(f"  position_wiring: {pf_err}")

            if result.get("status") == "failed":
                errors.append(f"  {item['topic']}: {result.get('error', 'unknown error')}")

        # Archive processed items
        archive_data = load_json(RESEARCH_ARCHIVE, {"archive": []})
        archive_data["archive"].extend(synthesis_results)
        archive_data["archive"] = archive_data["archive"][-100:]  # Keep last 100
        save_json(RESEARCH_ARCHIVE, archive_data)

        # Save updated queue (remove processed)
        queue_data["queue"] = [q for q in queue if q.get("status") == "pending"]
        save_json(RESEARCH_QUEUE, queue_data)

        remaining = len(queue_data["queue"])

        # ── Phase 4c: Drain position queue ──────────────────────────────────
        try:
            pos_result = _drain_position_queue()
            if pos_result["processed"] > 0:
                changes.extend(pos_result["changes"])
                findings.extend(pos_result["findings"])
        except Exception as pos_err:
            errors.append(f"  position_queue: {pos_err}")
        output_lines = [
            f"Synthesized {len(synthesis_results)} queue item(s):",
            "",
        ]
        for s in synthesis_results:
            output_lines.append(f"  - {s['topic']}: {s['delta']} (status: {s.get('status', '?')})")
        output_lines.extend([
            "",
            f"Processed items archived. Research queue now has {remaining} pending item(s) remaining.",
        ])
        output = "\n".join(output_lines)
        carry_forward = (
            f"{len(synthesis_results)} synthesis result(s) archived. "
            "On wake: check OVERNIGHT_LOG for top deltas to surface to Caine."
        )
        status = "completed"

    duration = (datetime.now() - start).total_seconds()
    duration_str = f"{duration:.1f}s"

    log_to_overnight_log(
        "overnight_synthesis",
        status,
        duration_str,
        output,
        changes,
        carry_forward,
        errors[0] if errors else None
    )
    record_sleep_run(duration, status == "completed", findings)

    print(f"Overnight synthesis complete. Status: {status}. Duration: {duration_str}")
    for f in findings:
        print(f"  - {f}")


if __name__ == "__main__":
    try:
        run_synthesis()
    except Exception as e:
        duration = "unknown"
        log_to_overnight_log(
            "overnight_synthesis",
            "failed",
            duration,
            f"Synthesis failed with error: {e}",
            [],
            "Check sleep_runs.json for error details. Flag for Nova attention.",
            str(e)
        )
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
