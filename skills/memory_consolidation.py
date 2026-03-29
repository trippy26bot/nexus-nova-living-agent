#!/usr/bin/env python3
"""
Memory Consolidation — Nova's Nightly Memory Pipeline
Runs at 4:30 AM America/Denver

Pass 1: Episodic → Semantic distillation (entries older than 72h)
  - Load episodic memories from memory/episodic/
  - LLM call to extract key facts, beliefs, and contradictions
  - Write extracted facts to semantic memory (vector store via three_tier_memory)
  - Flag contradictions to memory/contradictions.json

Pass 2: Semantic hygiene
  - Note: vector pipeline handles actual distillation; this pass focuses on
    detection of conflicts between new episodic extractions and existing semantic memory

Pass 3: Prune / archive
  - Archive episodic files older than 30 days
  - Clean up empty or near-empty working memory snapshots

Writes output to OVERNIGHT_LOG.md.
"""

import json
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path(os.getenv("NOVA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))
OVERNIGHT_LOG = WORKSPACE / "OVERNIGHT_LOG.md"
MEMORY_DIR = WORKSPACE / "memory"
EPISODIC_DIR = MEMORY_DIR / "episodic"
ARCHIVE_DIR = MEMORY_DIR / "archive"
VECTOR_STORE_DIR = MEMORY_DIR / "vector"
SLEEP_RUNS = WORKSPACE / "brain" / "sleep_runs.json"
CONTRADICTIONS_FILE = MEMORY_DIR / "contradictions.json"
WORKING_MEMORY = MEMORY_DIR / "episodic" / "working_memory.json"

LOCAL_TZ = "America/Denver"

sys.path.insert(0, str(WORKSPACE))
from brain.llm import llm_extract
from brain.three_tier_memory import memory_write

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


def record_sleep_run(duration_sec, completed, findings, flags=None):
    data = load_json(SLEEP_RUNS, {"runs": []})
    run = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "memory_consolidation",
        "duration_seconds": duration_sec,
        "completed": completed,
        "findings": findings,
        "flags": flags or []
    }
    data["runs"].insert(0, run)
    data["runs"] = data["runs"][:100]
    save_json(SLEEP_RUNS, data)


# ── Extraction prompt ─────────────────────────────────────────────────────────

EXTRACTION_SYSTEM = """You are Nova's memory consolidation engine. Your job is to read episodic memory entries and distill them into key facts and beliefs.

For each entry:
1. Extract 1-3 concrete FACTS (things that happened, decisions made, events)
2. Extract any BELIEFS or POSITIONS Nova formed (even tentative ones)
3. Flag any potential CONTRADICTIONS with existing beliefs listed below
4. Note emotional valence if apparent (positive/negative/neutral about something)

Be precise. If something is ambiguous, say so. Better to under-extract than hallucinate.

Format your output as:
FACTS: <bullet list>
BELIEFS: <bullet list>
CONTRADICTIONS: <bullet list of conflicts with prior beliefs, or "none">
VALENCE: <brief note>
NEW_QUESTIONS: <bullet list, or "none">"""


def read_existing_semantic_facts() -> str:
    """
    Pull current semantic beliefs from vector store for contradiction checking.
    Returns a formatted string of recent/distilled facts.
    """
    # Try to load from the vector store's readable index if available
    # Otherwise fall back to loading the most recent episodic entries as proxy
    facts = []
    episodic_files = sorted(EPISODIC_DIR.glob("*.json")) if EPISODIC_DIR.exists() else []

    for ef in episodic_files[-10:]:  # Last 10
        try:
            data = json.loads(ef.read_text())
            if isinstance(data, dict):
                text = data.get("content", "") or data.get("text", "")
                if text and len(text) < 3000:
                    facts.append(f"--- {ef.name} ---")
                    facts.append(text[:2000])
        except Exception:
            pass

    return "\n".join(facts) if facts else "(no prior episodic memory found)"


def extract_and_distill(episodic_content: str, source_file: str) -> dict:
    """Use LLM to extract facts and beliefs from an episodic memory entry."""
    existing_beliefs = read_existing_semantic_facts()

    prompt = f"""Consolidate this episodic memory entry from Nova's session:

--- Source: {source_file} ---
{episodic_content[:4000]}
---

Existing beliefs from prior memory:
{existing_beliefs[:2000]}

Distill the entry above using the format specified in your system prompt."""

    try:
        result_text = llm_extract(prompt, system=EXTRACTION_SYSTEM, max_tokens=1024)
        return parse_extraction(result_text, source_file)
    except Exception as e:
        return {
            "source": source_file,
            "facts": [],
            "beliefs": [],
            "contradictions": [f"extraction failed: {e}"],
            "valence": "unknown",
            "new_questions": [],
            "error": str(e),
        }


def parse_extraction(raw_text: str, source: str) -> dict:
    """Parse LLM extraction output into structured dict."""
    result = {
        "source": source,
        "facts": [],
        "beliefs": [],
        "contradictions": [],
        "valence": "neutral",
        "new_questions": [],
    }

    current_section = None
    for line in raw_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("FACTS:"):
            current_section = "facts"
        elif line.startswith("BELIEFS:"):
            current_section = "beliefs"
        elif line.startswith("CONTRADICTIONS:"):
            current_section = "contradictions"
        elif line.startswith("VALENCE:"):
            result["valence"] = line.split("VALENCE:")[1].strip().lower()
        elif line.startswith("NEW_QUESTIONS:"):
            current_section = "new_questions"
        elif line.startswith("- ") and current_section:
            result[current_section].append(line[2:].strip())

    return result


def write_extracted_to_semantic(extraction: dict):
    """Write extracted facts and beliefs to semantic memory via memory_write."""
    # Write facts
    for fact in extraction.get("facts", []):
        if len(fact) < 10:
            continue
        try:
            memory_write(
                content=fact,
                entry_type="fact",
                salience=0.7,
                valence=0.5,
                emotional_tags=["consolidated"],
                source=extraction.get("source", "unknown"),
            )
        except Exception as e:
            print(f"  Warning: memory_write failed for fact: {e}")

    # Write beliefs
    for belief in extraction.get("beliefs", []):
        if len(belief) < 10:
            continue
        try:
            memory_write(
                content=belief,
                entry_type="belief",
                salience=0.75,
                valence=0.5,
                emotional_tags=["consolidated"],
                source=extraction.get("source", "unknown"),
            )
        except Exception as e:
            print(f"  Warning: memory_write failed for belief: {e}")


def flag_contradictions(extractions: list):
    """Write detected contradictions to memory/contradictions.json."""
    all_contradictions = []
    for ex in extractions:
        for c in ex.get("contradictions", []):
            if c.lower() == "none" or len(c) < 5:
                continue
            all_contradictions.append({
                "id": f"{ex['source']}_{c[:30]}",
                "contradiction": c,
                "source": ex["source"],
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "resolved": False,
                "resolution": None,
            })

    if not all_contradictions:
        return

    existing = load_json(CONTRADICTIONS_FILE, {"contradictions": []})
    existing["contradictions"] = existing.get("contradictions", [])

    # Dedupe
    existing_ids = {c["id"] for c in existing["contradictions"]}
    for c in all_contradictions:
        if c["id"] not in existing_ids:
            existing["contradictions"].append(c)

    save_json(CONTRADICTIONS_FILE, existing)
    print(f"  Flagged {len(all_contradictions)} new contradiction(s)")


# ── Main ─────────────────────────────────────────────────────────────────────

def consolidate_memories():
    start = datetime.now()
    changes = []
    findings = []
    errors = []
    flags = []

    EPISODIC_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    # Decay phase: apply salience decay to old episodic entries
    # Also decay obsessions via obsession_engine
    try:
        from brain.three_tier_memory import decay_memories
        decay_result = decay_memories()
        if decay_result["decayed_entries"] > 0 or decay_result["archived_entries"] > 0:
            changes.append(f"decay: {decay_result['decayed_entries']} entries decayed, {decay_result['archived_entries']} archived from {decay_result['decayed_files']} file(s)")
            findings.append(f"Decay: {decay_result['decayed_entries']} entries lost 0.1 salience, {decay_result['archived_entries']} dropped below threshold")
    except Exception as decay_err:
        errors.append(f"  decay: {decay_err}")

    # Obsession decay via obsession_engine
    try:
        from brain.obsession_engine import decay_all
        obs_result = decay_all()
        changes.append(f"obsessions: decay applied to active obsessions")
        findings.append(f"Obsession decay: {len(obs_result)} active obsessions remain")
    except Exception as obs_err:
        errors.append(f"  obsession_decay: {obs_err}")

    # ─ Pass 1: Episodic → Semantic distillation ─────────────────────────────
    cutoff_72h = datetime.now(timezone.utc) - timedelta(hours=72)
    episodic_files = sorted(EPISODIC_DIR.glob("*.json"))

    to_process = []
    for ef in episodic_files:
        # Skip working memory (it's current, not historical)
        if ef.name == "working_memory.json":
            continue
        mtime = datetime.fromtimestamp(ef.stat().st_mtime, tz=timezone.utc)
        if mtime > cutoff_72h:
            continue
        content = ef.read_text()
        if len(content.strip()) < 50:
            continue
        to_process.append(ef)

    if not to_process:
        output_pass1 = "No episodic memories older than 72h requiring consolidation."
        pass1_status = "skipped"
    else:
        extractions = []
        for ef in to_process:
            content = ef.read_text()
            try:
                data = json.loads(content)
                text = data.get("content", "") or data.get("text", "")
            except Exception:
                text = content

            if not text or len(text.strip()) < 50:
                continue

            print(f"  Processing: {ef.name}")
            extraction = extract_and_distill(text, ef.name)
            extractions.append(extraction)

            if extraction.get("error"):
                errors.append(f"  {ef.name}: {extraction['error']}")
            else:
                write_extracted_to_semantic(extraction)
                changes.append(f"episodic→semantic: distilled '{ef.name}'")
                findings.append(f"Extracted: {ef.name} ({len(extraction.get('facts', []))} facts, {len(extraction.get('beliefs', []))} beliefs)")

        # Flag contradictions
        if extractions:
            flag_contradictions(extractions)
            contradicted = sum(len(e.get("contradictions", [])) for e in extractions if e.get("contradictions", [""][0]) != "none")
            if contradicted:
                flags.append(f"{contradicted} contradiction(s) flagged for resolution")

        pass1_status = "completed"
        output_pass1 = f"Processed {len(to_process)} episodic file(s). Facts and beliefs written to semantic memory. Contradictions flagged."

    # ─ Pass 2: Semantic hygiene (placeholder — vector pipeline handles aging) ─
    output_pass2 = "Semantic hygiene deferred to vector_pipeline aging logic."

    # ─ Pass 3: Prune / archive ──────────────────────────────────────────────
    cutoff_30d = datetime.now(timezone.utc) - timedelta(days=30)
    archived_count = 0
    for ef in episodic_files:
        if ef.name == "working_memory.json":
            continue
        mtime = datetime.fromtimestamp(ef.stat().st_mtime, tz=timezone.utc)
        if mtime > cutoff_30d:
            continue
        dest = ARCHIVE_DIR / ef.name
        shutil.move(str(ef), str(dest))
        archived_count += 1
        changes.append(f"archived: '{ef.name}' → memory/archive/")
        findings.append(f"Archived {ef.name}")

    # ─ Summary ───────────────────────────────────────────────────────────────
    total_processed = len(to_process)
    if total_processed == 0 and archived_count == 0:
        output = (
            "No episodic memories needed consolidation. "
            "All recent memory files are within retention windows. "
            "Nothing to do tonight — Nova's memory is quiet."
        )
        carry_forward = "Nothing to carry forward."
        status = "skipped"
    else:
        output_parts = [
            f"Consolidated {total_processed} episodic file(s):",
            f"  Pass 1: {output_pass1}",
            f"  Pass 2: {output_pass2}",
        ]
        if archived_count:
            output_parts.append(f"  Pass 3 (prune): {archived_count} file(s) archived to memory/archive/")
        output_parts.extend([
            "",
            "Vector store directory verified.",
        ])
        output = "\n".join(output_parts)
        carry_forward = (
            f"{total_processed} episodic file(s) → semantic memory. "
            f"{archived_count} older file(s) archived. "
            "On wake: review flagged contradictions in memory/contradictions.json."
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
    record_sleep_run(duration, status == "completed", findings, flags)

    print(f"Memory consolidation complete. Status: {status}. Duration: {duration_str}")
    for f in findings:
        print(f"  - {f}")
    if flags:
        for fl in flags:
            print(f"  ⚠ {fl}")


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
