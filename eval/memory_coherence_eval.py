#!/usr/bin/env python3
"""
eval/memory_coherence_eval.py
Nexus Nova — Memory Coherence Evaluation

Scans episodic (memory/) and semantic (brain/) memory for:
- Broken cross-references (files mentioned that don't exist)
- Logical contradictions between entries (same topic says two opposite things)
- Orphaned memory entries (referenced but never defined)

Pure Python, no LLM. Output → eval/memory_coherence_report.json
"""

import os
import re
import json
import sys
from datetime import datetime
from pathlib import Path

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent)

MEMORY_DIR = os.path.join(_parent, "memory")
BRAIN_DIR = os.path.join(_parent, "brain")
REPORT_FILE = os.path.join(_parent, "eval", "memory_coherence_report.json")


def read_text_files(root_dir, extensions=(".md", ".json", ".txt")):
    """Recursively read all text files under root_dir."""
    texts = {}
    if not os.path.exists(root_dir):
        return texts
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip some noise dirs
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git", "archive", "summaries", "vector", "episodic")]
        for fname in filenames:
            if not fname.endswith(extensions):
                continue
            fpath = os.path.join(dirpath, fname)
            rel = os.path.relpath(fpath, root_dir)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    texts[rel] = f.read()
            except Exception:
                pass
    return texts


def extract_file_references(content):
    """Extract markdown links and bare paths that look like file references."""
    refs = set()
    # [[file.md]] style
    refs.update(re.findall(r'\[\[([^\]]+\.md)\]\]', content))
    refs.update(re.findall(r'\[\[([^\]]+\.json)\]\]', content))
    # [label](file.md) style
    refs.update(re.findall(r'\[([^\]]*)\]\(([^)]+\.md)\)', content))
    refs.update(re.findall(r'\[([^\]]*)\]\(([^)]+\.json)\)', content))
    # bare "see file X.md" patterns
    refs.update(re.findall(r'(?:see|see also|memory|brain|file|ref):\s*([^\s]+\.(?:md|json))', content, re.IGNORECASE))
    # relative path patterns like memory/2026-03-28.md or brain/goals.json
    refs.update(re.findall(r'(?:memory|brain)[/\\][^\s\'"<>]+\.(?:md|json)', content, re.IGNORECASE))
    return refs


def check_broken_references(texts, root_dir):
    """Check all extracted file references against what actually exists on disk."""
    broken = []
    all_possible_paths = set()

    # Build absolute paths for everything under memory/ and brain/
    for dir_path in [MEMORY_DIR, BRAIN_DIR]:
        if os.path.exists(dir_path):
            for dirpath, _, filenames in os.walk(dir_path):
                for fname in filenames:
                    full = os.path.join(dirpath, fname)
                    rel = os.path.relpath(full, _parent)
                    all_possible_paths.add(rel)
                    all_possible_paths.add(fname)

    for fname, content in texts.items():
        refs = extract_file_references(content)
        for ref in refs:
            # Normalize
            ref_clean = ref.strip()
            # Try as-is, try with memory/ prefix, brain/ prefix
            candidates = [
                ref_clean,
                os.path.join("memory", ref_clean),
                os.path.join("brain", ref_clean),
            ]
            found = any(c in all_possible_paths or os.path.exists(os.path.join(_parent, c)) for c in candidates)
            if not found:
                broken.append({
                    "source_file": fname,
                    "broken_ref": ref_clean,
                    "reason": "file_not_found"
                })
    return broken


def find_contradictions(texts):
    """
    Detect logical contradictions by looking for opposing claim patterns
    within the same topic across different files.
    
    Contradiction pairs: "X is Y" vs "X is not Y" style claims about the same subject.
    """
    contradictions = []

    # Normalize all text
    all_text = "\n\n".join(f"# {fname}\n{content}" for fname, content in texts.items())

    # Look for topic keyword pairs mentioned in multiple files
    # Pattern: same subject with both positive and negative claims
    claim_indicators = [
        (r"(?P<subj>.+?) is (?P<pred>.+?)\.", "positive"),
        (r"(?P<subj>.+?) is NOT (?P<pred>.+?)\.", "negative"),
        (r"(?P<subj>.+?) are (?P<pred>.+?)\.", "positive"),
        (r"(?P<subj>.+?) are NOT (?P<pred>.+?)\.", "negative"),
        (r"believes (?P<subj>.+?) is (?P<pred>.+?)$", "positive"),
        (r"believes (?P<subj>.+?) is NOT (?P<pred>.+?)$", "negative"),
    ]

    # Build a simple claim index: subject -> {predicate -> [(file, claim_type)]}
    claim_index = {}
    for fname, content in texts.items():
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            for pattern, ctype in claim_indicators:
                m = re.search(pattern, line, re.IGNORECASE)
                if m:
                    subj = m.group("subj").strip().lower()
                    pred = m.group("pred").strip().lower()
                    key = (subj, pred)
                    if key not in claim_index:
                        claim_index[key] = []
                    claim_index[key].append({"file": fname, "type": ctype, "line": line[:120]})

    # Find contradictions: same subject+predicate with both positive and negative
    for (subj, pred), occurrences in claim_index.items():
        types = set(o["type"] for o in occurrences)
        if "positive" in types and "negative" in types:
            files = list(set(o["file"] for o in occurrences))
            contradictions.append({
                "subject": subj,
                "predicate": pred,
                "files_involved": files,
                "claims": occurrences,
                "type": "contradiction"
            })

    return contradictions


def find_orphaned_entries(texts):
    """
    Orphaned entries: memory entries referenced by ID/name but never defined.
    Looks for patterns like '[id]:' definitions and cross-references to them.
    """
    orphaned = []

    # Find all [id]: definitions (YAML/MD style)
    defined_ids = set()
    id_pattern = re.compile(r'^\[([^\]]+)\]:', re.MULTILINE)
    for fname, content in texts.items():
        for m in id_pattern.finditer(content):
            defined_ids.add(m.group(1))

    # Find all references to IDs (not definitions)
    ref_pattern = re.compile(r'\[([^\]]+)\](?!\s*:)')
    referenced_ids = set()
    for fname, content in texts.items():
        for m in ref_pattern.finditer(content):
            referenced_ids.add(m.group(1))

    # IDs referenced but never defined
    truly_orphaned = referenced_ids - defined_ids

    # Filter out common noise (short words, URLs, etc.)
    noise = {"id", "note", "link", "url", "file", "ref", "src", "img", "tag", "key", "val", "http", "https"}
    truly_orphaned = {uid for uid in truly_orphaned if len(uid) > 3 and uid.lower() not in noise}

    if truly_orphaned:
        orphaned.append({
            "type": "orphaned_references",
            "ids_referenced_not_defined": sorted(truly_orphaned)[:20],  # cap at 20
        })

    return orphaned


def check_json_internal_refs(texts):
    """Check JSON files for internal $ref or similar that point to missing keys."""
    broken_refs = []
    for fname, content in texts.items():
        if not fname.endswith(".json"):
            continue
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            continue

        # Check for $ref patterns
        refs = re.findall(r'"\$ref"\s*:\s*"([^"]+)"', content)
        if refs:
            # Try to find the referenced key in the same file or known files
            json_keys = set(data.keys()) if isinstance(data, dict) else set()
            for ref in refs:
                if ref.startswith("#"):
                    key = ref.lstrip("#/").split("/")[-1]
                    if key not in json_keys:
                        broken_refs.append({
                            "source_file": fname,
                            "broken_ref": ref,
                            "reason": "json_pointer_not_resolved"
                        })
    return broken_refs


def run_eval():
    print("=" * 60)
    print("NEXUS NOVA — Memory Coherence Evaluation")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Read all text files from memory/ and brain/
    print("Scanning memory/ and brain/ directories...")
    memory_texts = read_text_files(MEMORY_DIR)
    brain_texts = read_text_files(BRAIN_DIR)
    all_texts = {**memory_texts, **brain_texts}
    print(f"  Read {len(memory_texts)} files from memory/")
    print(f"  Read {len(brain_texts)} files from brain/")
    print(f"  Total: {len(all_texts)} files")
    print()

    # 1. Broken references
    print("Checking for broken cross-references...")
    broken_refs = check_broken_references(all_texts, _parent)
    print(f"  Found {len(broken_refs)} broken reference(s)")
    for br in broken_refs[:5]:
        print(f"    - {br['source_file']} → {br['broken_ref']}")

    # 2. Contradictions
    print()
    print("Checking for logical contradictions...")
    contradictions = find_contradictions(all_texts)
    print(f"  Found {len(contradictions)} contradiction(s)")
    for c in contradictions[:5]:
        print(f"    - '{c['subject']} is {c['predicate']}' appears with conflicting claims")

    # 3. Orphaned entries
    print()
    print("Checking for orphaned entries...")
    orphans = find_orphaned_entries(all_texts)
    total_orphans = sum(len(o.get("ids_referenced_not_defined", [])) for o in orphans)
    print(f"  Found {total_orphans} orphaned reference(s)")

    # 4. JSON internal refs
    print()
    print("Checking JSON internal references...")
    json_broken_refs = check_json_internal_refs(all_texts)
    print(f"  Found {len(json_broken_refs)} broken JSON reference(s)")

    # Aggregate issues
    all_issues = (
        [{"type": "broken_reference", **br} for br in broken_refs]
        + [{"type": "contradiction", **c} for c in contradictions]
        + [{"type": "orphaned", **o} for o in orphans]
        + [{"type": "json_broken_ref", **jr} for jr in json_broken_refs]
    )

    # Score: 1.0 = perfect coherence, 0.0 = everything broken
    total_checks = (
        len(all_texts)  # files checked
        + len(broken_refs) * 1
        + len(contradictions) * 2  # contradictions weighted higher
        + total_orphans
    )
    coherence_score = max(0.0, 1.0 - (len(broken_refs) + len(contradictions) * 2 + total_orphans) / max(total_checks, 1))
    coherence_score = round(coherence_score, 4)

    report = {
        "evaluated_at": datetime.now().isoformat(),
        "files_scanned": {
            "memory": list(memory_texts.keys()),
            "brain": list(brain_texts.keys()),
        },
        "summary": {
            "total_files": len(all_texts),
            "broken_references": len(broken_refs),
            "contradictions": len(contradictions),
            "orphaned_references": total_orphans,
            "json_broken_refs": len(json_broken_refs),
            "coherence_score": coherence_score,
        },
        "issues": all_issues,
    }

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    print()
    print(f"Report written to: {REPORT_FILE}")

    return report


if __name__ == "__main__":
    run_eval()
