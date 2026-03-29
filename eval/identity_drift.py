#!/usr/bin/env python3
"""
eval/identity_drift.py
Nexus Nova — Identity Drift Evaluation

Hashes core identity files and compares against a baseline snapshot.
Outputs a consistency score (0.0–1.0) showing how much the identity
has drifted over time.

A score of 1.0 means perfect consistency — no drift detected.
A score below 1.0 indicates one or more files changed.
"""

import os
import sys
import json
import hashlib
from datetime import datetime

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent)

CORE_IDENTITY_FILES = [
    "SOUL.md",
    "IDENTITY.md",
    "NOVA_DIRECTIVE.md",
    "PERSONALITY.md",
    "PRESENCE.md",
    "EPISTEMIC_BOUNDARIES.md",
    "NOVA_BECOMING.md",
]

SNAPSHOT_FILE = os.path.join(_parent, "eval", "identity_snapshot.json")
REPORT_FILE = os.path.join(_parent, "eval", "drift_report.json")


def hash_file(path):
    """Return SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def get_file_hashes():
    """Compute current hashes for all core identity files."""
    hashes = {}
    for fname in CORE_IDENTITY_FILES:
        path = os.path.join(_parent, fname)
        if os.path.exists(path):
            hashes[fname] = {
                "hash": hash_file(path),
                "size": os.path.getsize(path),
                "modified": datetime.fromtimestamp(os.path.getmtime(path)).isoformat(),
            }
        else:
            hashes[fname] = None  # File missing
    return hashes


def load_snapshot():
    """Load the baseline snapshot if it exists."""
    if os.path.exists(SNAPSHOT_FILE):
        try:
            with open(SNAPSHOT_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return None


def save_snapshot(hashes):
    """Save current hashes as the new baseline snapshot."""
    os.makedirs(os.path.dirname(SNAPSHOT_FILE), exist_ok=True)
    snapshot = {
        "created_at": datetime.now().isoformat(),
        "files": hashes,
    }
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshot, f, indent=2)
    print(f"  Baseline snapshot saved to: {SNAPSHOT_FILE}")


def compute_drift(current, baseline):
    """
    Compare current hashes against baseline.
    Returns (drifted_files, consistency_score)
    """
    drifted = []
    for fname in CORE_IDENTITY_FILES:
        curr = current.get(fname)
        base = baseline.get("files", {}).get(fname)

        if curr is None and base is None:
            continue  # Both missing — no change
        if curr is None or base is None:
            drifted.append({"file": fname, "reason": "presence_changed", "current": curr, "baseline": base})
            continue

        if curr["hash"] != base["hash"]:
            drifted.append({
                "file": fname,
                "reason": "content_changed",
                "current_hash": curr["hash"],
                "baseline_hash": base["hash"],
                "size_delta": curr["size"] - base.get("size", 0),
            })

    # Consistency score: 1 - (drifted_count / total_files_checked)
    total = len([f for f in CORE_IDENTITY_FILES if current.get(f) is not None or baseline.get("files", {}).get(f) is not None])
    score = 1.0 - (len(drifted) / total) if total > 0 else 1.0
    return drifted, round(score, 4)


def run_eval(init=False):
    """Run the identity drift evaluation."""
    print("=" * 60)
    print("NEXUS NOVA — Identity Drift Evaluation")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    current = get_file_hashes()

    # Show current state
    print("Current identity file hashes:")
    for fname in CORE_IDENTITY_FILES:
        h = current.get(fname)
        if h:
            print(f"  {fname}: {h['hash'][:16]}... ({h['size']} bytes)")
        else:
            print(f"  {fname}: (not found)")
    print()

    snapshot = load_snapshot()

    if snapshot:
        print(f"Baseline snapshot from: {snapshot['created_at']}")
        print()
        drifted, score = compute_drift(current, snapshot)

        print(f"Consistency Score: {score:.2%}")
        print()

        if drifted:
            print("Drift detected:")
            for d in drifted:
                print(f"  - {d['file']}: {d['reason']}")
                if d['reason'] == 'content_changed':
                    print(f"    current:  {d['current_hash'][:16]}...")
                    print(f"    baseline: {d['baseline_hash'][:16]}...")
                    if d.get('size_delta'):
                        print(f"    size delta: {d['size_delta']:+d} bytes")
        else:
            print("No drift detected — identity is consistent with baseline.")
    else:
        print("No baseline snapshot found.")
        print("Run with --init to create a baseline snapshot.")
        print()
        print("To initialize baseline:")
        print(f"  python3 eval/identity_drift.py --init")

    # Always write a report
    report = {
        "evaluated_at": datetime.now().isoformat(),
        "baseline_at": snapshot["created_at"] if snapshot else None,
        "current_hashes": current,
        "snapshot_exists": snapshot is not None,
    }
    if snapshot:
        report["drifted_files"], report["consistency_score"] = drifted, score

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    print()
    print(f"Report written to: {REPORT_FILE}")

    # Optionally save as new baseline
    if init:
        print()
        save_snapshot(current)

    return report


if __name__ == "__main__":
    init_mode = "--init" in sys.argv
    run_eval(init=init_mode)
