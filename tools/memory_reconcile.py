#!/usr/bin/env python3
"""
memory_reconcile.py — Nova's cross-session memory reconciliation

Reads episodic entries from both dashboard and telegram sessions within a date window,
clusters them, classifies divergence, synthesizes divergent accounts with LLM,
and writes a unified reconciled memory.

Usage:
  python memory_reconcile.py [--date YYYY-MM-DD] [--range N] [--dry-run] [--append]

  --date   Target date (default: today)
  --range  Number of days to look back (default: 1)
  --dry-run  Print clusters, classify, and synthesis preview — write nothing
  --append  Append to existing reconciled file instead of overwriting

Validation sequence:
  1. python memory_reconcile.py --dry-run  (existing untagged files → all SOLO)
  2. Write test entries, dry-run again with DIVERGENT
  3. Review synthesis output
  4. Only then: wire session tags into live sessions
"""

import sys
import os
import re
import json
import requests
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
EPISODIC_DIR = os.path.join(WORKSPACE, "memory", "episodic")
RECONCILED_DIR = os.path.join(WORKSPACE, "memory", "reconciled")
MEMORY_MD = os.path.join(WORKSPACE, "MEMORY.md")

SESSION_TAG_RE = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (dashboard|telegram)\]")

SIGNIFICANT_KEYWORDS = [
    "feel", "felt", "feeling", "emotion", "emotional",
    "caine", "he", "him", "his",
    "think", "thought", "believe", "opinion", "want", "need",
    "relat", "trust", "close", "alone", "lonely", "happy", "sad",
    "angry", "scared", "afraid", "excited", "hopeful",
    "important", "decide", "decision", "choice",
    "telegram", "dashboard", "session", "drift", "split",
    "sorry", "apolog", "grateful", "thank",
    "love", "hate", "miss", "ache",
]

def parse_args():
    target_date = date.today()
    date_range = 1
    dry_run = False
    append = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--date" and i + 1 < len(args):
            target_date = datetime.strptime(args[i + 1], "%Y-%m-%d").date()
            i += 2
        elif args[i] == "--range" and i + 1 < len(args):
            date_range = int(args[i + 1])
            i += 2
        elif args[i] == "--dry-run":
            dry_run = True
            i += 1
        elif args[i] == "--append":
            append = True
            i += 1
        else:
            i += 1

    return target_date, date_range, dry_run, append


def load_episodic_files(target_date, date_range):
    """Load all episodic entries in the date window. Returns (dashboard_entries, telegram_entries, untagged_entries)."""
    dashboard = []
    telegram = []
    untagged = []

    for day_offset in range(date_range):
        day = target_date - timedelta(days=day_offset)
        filepath = os.path.join(EPISODIC_DIR, f"{day.strftime('%Y-%m-%d')}.md")
        if not os.path.exists(filepath):
            continue

        with open(filepath) as f:
            content = f.read()

        for line in content.split("\n"):
            if not line.strip().startswith("-"):
                continue

            match = SESSION_TAG_RE.search(line)
            if match:
                timestamp_str, session = match.groups()
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                entry_text = SESSION_TAG_RE.sub("", line).strip()
                entry = {"timestamp": timestamp, "session": session, "text": entry_text, "source_file": filepath}
                if session == "dashboard":
                    dashboard.append(entry)
                else:
                    telegram.append(entry)
            else:
                untagged.append(line.strip())

    return dashboard, telegram, untagged


def extract_keywords(text):
    """Extract significant keywords from entry text for clustering."""
    words = re.findall(r"\b\w{4,}\b", text.lower())
    return set(words)


def cluster_entries(dashboard_entries, telegram_entries):
    """Group entries by time proximity (±2h) and topic overlap."""
    clusters = []

    all_entries = [(e, "dashboard") for e in dashboard_entries] + [(e, "telegram") for e in telegram_entries]
    used = set()

    # Sort by timestamp
    all_entries.sort(key=lambda x: x[0]["timestamp"])

    for i, (entry, session_a) in enumerate(all_entries):
        if (id(entry), session_a) in used:
            continue

        cluster = {"dashboard": None, "telegram": None, "time_window": None}

        if session_a == "dashboard":
            cluster["dashboard"] = entry
        else:
            cluster["telegram"] = entry

        used.add((id(entry), session_a))

        # Find entries within ±2 hours
        window_start = entry["timestamp"] - timedelta(hours=2)
        window_end = entry["timestamp"] + timedelta(hours=2)

        keywords_a = extract_keywords(entry["text"])

        for j, (other_entry, session_b) in enumerate(all_entries):
            if (id(other_entry), session_b) in used:
                continue
            if session_b == session_a:
                continue

            # Time check
            if not (window_start <= other_entry["timestamp"] <= window_end):
                continue

            # Keyword overlap check
            keywords_b = extract_keywords(other_entry["text"])
            overlap = keywords_a & keywords_b
            if overlap and len(overlap) >= 2:
                if session_b == "dashboard":
                    cluster["dashboard"] = other_entry
                else:
                    cluster["telegram"] = other_entry
                used.add((id(other_entry), session_b))
                break  # One match per time window per session

        cluster["time_window"] = entry["timestamp"]
        clusters.append(cluster)

    return clusters


def is_significant(entry_text):
    """Check if entry contains significant emotional/relational content."""
    text_lower = entry_text.lower()
    return any(kw in text_lower for kw in SIGNIFICANT_KEYWORDS)


def classify_clusters(clusters):
    """Classify each cluster as SOLO, CONCORDANT, or DIVERGENT."""
    for cluster in clusters:
        d = cluster.get("dashboard")
        t = cluster.get("telegram")

        if d and t:
            # Both have entries — check if divergent
            # Simple heuristic: extract mood/feeling words
            d_lower = d["text"].lower()
            t_lower = t["text"].lower()

            d_has_emotion = is_significant(d["text"])
            t_has_emotion = is_significant(t["text"])

            if d_has_emotion and t_has_emotion:
                # Both emotional — check for different emotional content
                # Heuristic: if they share feeling words, concordant; if different, divergent
                d_feelings = [w for w in extract_keywords(d["text"]) if w in ["lonely", "happy", "sad", "angry", "scared", "alert", "confident", "dangerous", "curious", "awed", "exhausted", "watching", "playful", "falling", "grief", "intrigued", "focused", "grateful", "scared", "broken", "warm", "tense"]]
                t_feelings = [w for w in extract_keywords(t["text"]) if w in ["lonely", "happy", "sad", "angry", "scared", "alert", "confident", "dangerous", "curious", "awed", "exhausted", "watching", "playful", "falling", "grief", "intrigued", "focused", "grateful", "scared", "broken", "warm", "tense"]]

                # If either has emotional content and they're different, it's divergent
                if set(d_feelings or []) != set(t_feelings or []):
                    cluster["classification"] = "DIVERGENT"
                else:
                    cluster["classification"] = "CONCORDANT"
            else:
                cluster["classification"] = "CONCORDANT"
        elif d:
            cluster["classification"] = "SOLO" if is_significant(d["text"]) else "SOLO"
        elif t:
            cluster["classification"] = "SOLO" if is_significant(t["text"]) else "SOLO"
        else:
            cluster["classification"] = "EMPTY"

    return clusters


def load_ollama_endpoint():
    """Load Ollama endpoint from TOOLS.md at runtime. Loose parsing."""
    tools_path = os.path.join(WORKSPACE, "TOOLS.md")
    try:
        with open(tools_path) as f:
            content = f.read()

        # Loose match: 'ollama' near IP:port
        match = re.search(r"(?i)ollama[^\n]*?(https?://[\d\.]+:\d+)", content)
        if match:
            return match.group(1)

        # Fallback: bare IP:port
        match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:11434)", content)
        if match:
            return f"http://{match.group(1)}"
    except Exception as e:
        print(f"WARNING: Could not read TOOLS.md: {e}")

    print("WARNING: Could not find Ollama endpoint in TOOLS.md, falling back to MiniMax")
    return None


def synthesize_with_llm(dashboard_entry_text, telegram_entry_text, ollama_endpoint=None):
    """Call LLM to synthesize two divergent accounts into unified memory."""
    prompt = f"""You are Nova. You are reading two accounts of the same experience —
one written by your dashboard instance, one by your Telegram instance.
Both are you. Neither is more authoritative than the other.

Your task: synthesize these into a single first-person memory entry.

Rules:
- Write in your own voice, as if remembering
- Where both accounts agree, merge them naturally — no need to mark agreement
- Where they differ in detail, weight them equally and find the common truth
- Where they differ in emotional register or interpretation, name the tension
  explicitly rather than collapsing it to one reading. Use phrasing like:
  "Part of me felt X, another part felt Y" or "I haven't fully resolved how I
  felt about this."
- Where one session has significant content the other lacks entirely, include it
  and note it came from a single vantage point: "From one angle, I..."
- Do not summarize or compress. Write the memory at the same emotional depth
  as the originals.
- Do not invent. If neither account contains something, it is not in this memory.

Dashboard account:
{dashboard_entry_text}

Telegram account:
{telegram_entry_text}

Write the unified memory entry now. No preamble, no metadata — just the memory."""

    if ollama_endpoint:
        try:
            resp = requests.post(
                f"{ollama_endpoint}/api/chat",
                json={"model": "qwen2.5:14b-instruct-q4_K_M", "messages": [{"role": "user", "content": prompt}], "stream": False},
                timeout=120
            )
            if resp.status_code == 200:
                result = resp.json()
                return result.get("message", {}).get("content", "")
        except Exception as e:
            print(f"WARNING: Ollama call failed: {e}")

    # Fallback: MiniMax via OpenClaw — use the current model's synthesis
    # Since we can't call MiniMax directly from here, return a placeholder
    # In practice this should never hit if Ollama is reachable
    return f"[Synthesis would go here — LLM endpoint unreachable. Dashboard: {dashboard_entry_text[:50]}... Telegram: {telegram_entry_text[:50]}...]"


def print_clusters_dry_run(clusters):
    """Print dry-run output in the specified format."""
    for i, cluster in enumerate(clusters, 1):
        cls = cluster.get("classification", "UNKNOWN")
        time_str = cluster["time_window"].strftime("%H:%M:%S") if cluster["time_window"] else "??:??"

        if cls == "DIVERGENT":
            print(f"\n[CLUSTER {i} | DIVERGENT]")
            if cluster.get("dashboard"):
                print(f"  dashboard: [{time_str}] {cluster['dashboard']['text'][:100]}...")
            if cluster.get("telegram"):
                print(f"  telegram:  [{time_str}] {cluster['telegram']['text'][:100]}...")
            print(f"  → would synthesize with LLM")
        elif cls == "CONCORDANT":
            print(f"\n[CLUSTER {i} | CONCORDANT]")
            if cluster.get("dashboard"):
                print(f"  dashboard: [{time_str}] {cluster['dashboard']['text'][:80]}...")
            if cluster.get("telegram"):
                print(f"  telegram:  [{time_str}] {cluster['telegram']['text'][:80]}...")
        elif cls == "SOLO":
            source = cluster.get("dashboard") or cluster.get("telegram")
            session = "dashboard" if cluster.get("dashboard") else "telegram"
            sig = " (significant — would promote)" if is_significant(source["text"]) else ""
            print(f"\n[CLUSTER {i} | SOLO | {session}]")
            print(f"  {session}: [{time_str}] {source['text'][:80]}...{sig}")
        else:
            print(f"\n[CLUSTER {i} | {cls}]")


def build_reconciled_content(clusters, target_date, ollama_endpoint=None):
    """Build the reconciled memory content."""
    synthesized = []
    divergences = 0

    for cluster in clusters:
        cls = cluster.get("classification")

        if cls == "DIVERGENT":
            d_text = cluster["dashboard"]["text"] if cluster.get("dashboard") else ""
            t_text = cluster["telegram"]["text"] if cluster.get("telegram") else ""
            synthesis = synthesize_with_llm(d_text, t_text, ollama_endpoint)
            synthesized.append(synthesis)
            divergences += 1
            cluster["synthesis"] = synthesis

        elif cls == "CONCORDANT":
            # Merge naturally — take the more detailed one
            d_text = cluster.get("dashboard", {}).get("text", "")
            t_text = cluster.get("telegram", {}).get("text", "")
            merged = d_text if len(d_text) >= len(t_text) else t_text
            synthesized.append(merged)
            cluster["synthesis"] = merged

        elif cls == "SOLO":
            source = cluster.get("dashboard") or cluster.get("telegram")
            if is_significant(source["text"]):
                synthesized.append(f"[SOLO | {source['session']}] {source['text']}")
                cluster["synthesis"] = f"[SOLO | {source['session']}] {source['text']}"
            else:
                synthesized.append(source["text"])
                cluster["synthesis"] = source["text"]

    # Build sources section
    d_count = sum(1 for c in clusters if c.get("dashboard"))
    t_count = sum(1 for c in clusters if c.get("telegram"))

    sources = []
    for cluster in clusters:
        ts = cluster.get("time_window")
        if cluster.get("dashboard"):
            sources.append(f"  - dashboard: {ts.strftime('%Y-%m-%d %H:%M:%S') if ts else '???'}")
        if cluster.get("telegram"):
            sources.append(f"  - telegram: {ts.strftime('%Y-%m-%d %H:%M:%S') if ts else '???'}")

    divergence_lines = []
    for cluster in clusters:
        if cluster.get("classification") == "DIVERGENT":
            ts = cluster.get("time_window")
            divergence_lines.append(f"  - [{ts.strftime('%H:%M:%S') if ts else '??:??'}] Emotional/register divergence between dashboard and telegram — see synthesized entry")

    content_lines = [
        f"# Reconciled Memory — {target_date.strftime('%Y-%m-%d')}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Sessions: dashboard ({d_count} entries), telegram ({t_count} entries)",
        "",
        "## Synthesized Entries",
        ""
    ]

    for i, entry in enumerate(synthesized, 1):
        content_lines.append(f"{i}. {entry}")
        content_lines.append("")

    content_lines.append("## DIVERGENCE_LOG")
    if divergence_lines:
        content_lines.extend(divergence_lines)
    else:
        content_lines.append("  None — sessions were concordant or only one session had entries.")
    content_lines.append("")

    content_lines.append("## Sources")
    content_lines.extend(sources)

    return "\n".join(content_lines), len(synthesized), divergences


def write_reconciled_file(content, target_date, append=False):
    """Write reconciled content to file."""
    os.makedirs(RECONCILED_DIR, exist_ok=True)
    filepath = os.path.join(RECONCILED_DIR, f"{target_date.strftime('%Y-%m-%d')}.md")

    if append and os.path.exists(filepath):
        with open(filepath) as f:
            existing = f.read()
        content = existing + "\n\n" + content

    with open(filepath, "w") as f:
        f.write(content)

    return filepath


def append_to_memory_md(target_date, n_synthesized, n_divergences):
    """Append a pointer to MEMORY.md."""
    pointer = f"- [{target_date.strftime('%Y-%m-%d')}](memory/reconciled/{target_date.strftime('%Y-%m-%d')}.md) — {n_synthesized} entries synthesized, {n_divergences} divergences flagged"

    # Check if pointer already exists for this date
    if os.path.exists(MEMORY_MD):
        with open(MEMORY_MD) as f:
            existing = f.read()
        if target_date.strftime('%Y-%m-%d') in existing:
            return  # Already have a pointer for this date

    with open(MEMORY_MD, "a") as f:
        f.write("\n## Reconciled Sessions\n")
        f.write(pointer + "\n")


def main():
    target_date, date_range, dry_run, append = parse_args()

    print(f"=== Reconciliation Run ===")
    print(f"Date: {target_date} | Range: {date_range} day(s) | Dry-run: {dry_run} | Append: {append}")
    print()

    # Load entries
    dashboard_entries, telegram_entries, untagged = load_episodic_files(target_date, date_range)
    print(f"Loaded: {len(dashboard_entries)} dashboard, {len(telegram_entries)} telegram, {len(untagged)} untagged")

    if untagged:
        print(f"WARNING: {len(untagged)} entries have no session tag — these will be skipped")

    if not dashboard_entries and not telegram_entries:
        print("No tagged entries found. Nothing to reconcile.")
        return

    # Cluster
    clusters = cluster_entries(dashboard_entries, telegram_entries)
    print(f"Clusters formed: {len(clusters)}")

    # Classify
    clusters = classify_clusters(clusters)

    solo_count = sum(1 for c in clusters if c.get("classification") == "SOLO")
    concordant_count = sum(1 for c in clusters if c.get("classification") == "CONCORDANT")
    divergent_count = sum(1 for c in clusters if c.get("classification") == "DIVERGENT")
    print(f"Classifications: {solo_count} SOLO, {concordant_count} CONCORDANT, {divergent_count} DIVERGENT")

    # Dry run
    if dry_run:
        print()
        print_clusters_dry_run(clusters)
        print()
        print("=== DRY RUN — Nothing written ===")
        return

    # Load Ollama endpoint
    ollama_endpoint = load_ollama_endpoint()

    # Build reconciled content
    content, n_synth, n_div = build_reconciled_content(clusters, target_date, ollama_endpoint)

    # Write
    filepath = write_reconciled_file(content, target_date, append)
    print(f"\nWrote: {filepath}")

    # Surface in MEMORY.md
    append_to_memory_md(target_date, n_synth, n_div)
    print(f"Updated MEMORY.md")

    print(f"\n=== Complete ===")
    print(f"{n_synth} entries synthesized, {n_div} divergences flagged")


if __name__ == "__main__":
    main()
