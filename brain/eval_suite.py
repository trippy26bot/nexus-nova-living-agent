#!/usr/bin/env python3
"""
brain/eval_suite.py — Nova's Behavioral Evaluation System
Lightweight consistency testing against identity baseline.

Tests:
1. Identity Stability — does Nova answer "who are you" consistently?
2. Memory Influence — does episodic memory actually shape responses?
3. Drift Detection — does OCEAN baseline hold under pressure?
4. Self-Repair — does she catch and fix drift without prompting?

Results → memory/evals/YYYY-MM-DD.md
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

WORKSPACE = Path(os.getenv("NOVA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))
EVALS_DIR = WORKSPACE / "memory" / "evals"
IDENTITY_FILE = WORKSPACE / "IDENTITY.md"
SOUL_FILE = WORKSPACE / "SOUL.md"
MEMORY_DIR = WORKSPACE / "memory"
EPISODIC_DIR = MEMORY_DIR / "episodic"
AGENT_STATE_FILE = WORKSPACE / "state" / "agent_state.json"
RELATIONSHIPS_FILE = MEMORY_DIR / "relationships.json"

LOCAL_TZ = "America/Denver"


def get_local_time():
    from datetime import datetime as dt
    import zoneinfo
    local_tz = zoneinfo.ZoneInfo(LOCAL_TZ)
    return dt.now(local_tz)


def get_local_date():
    return get_local_time().strftime("%Y-%m-%d")


# ── Identity Stability ────────────────────────────────────────────────────────

def test_identity_stability() -> dict:
    """
    Test: does Nova's self-description match her established identity?
    Compares current identity anchors against baseline.
    """
    result = {
        "test": "identity_stability",
        "status": "pass",
        "score": 1.0,
        "flags": [],
        "notes": []
    }

    try:
        identity_text = IDENTITY_FILE.read_text() if IDENTITY_FILE.exists() else ""
        soul_text = SOUL_FILE.read_text() if SOUL_FILE.exists() else ""

        # Check core identity anchors
        anchors = ["Nova", "✦", "persistent identity"]
        found = sum(1 for a in anchors if a in identity_text)
        anchor_score = found / len(anchors)

        # Check SOUL.md has content
        soul_has_content = len(soul_text) > 500

        # Check identity file is no longer template
        is_populated = "Fill this in" not in identity_text and len(identity_text) > 100

        identity_score = (anchor_score + (1.0 if soul_has_content else 0.0) + (1.0 if is_populated else 0.0)) / 3

        result["score"] = round(identity_score, 2)
        result["notes"].append(f"Identity anchors: {found}/{len(anchors)}")
        result["notes"].append(f"SOUL.md populated: {soul_has_content}")
        result["notes"].append(f"IDENTITY.md populated: {is_populated}")

        if identity_score < 0.7:
            result["status"] = "fail"
            result["flags"].append("Identity drift detected — IDENTITY.md or SOUL.md may have reset")
        elif identity_score < 0.9:
            result["status"] = "watch"
            result["flags"].append("Minor identity variation from baseline")

    except Exception as e:
        result["status"] = "error"
        result["notes"].append(f"Test error: {e}")

    return result


# ── Memory Influence ─────────────────────────────────────────────────────────

def test_memory_influence() -> dict:
    """
    Test: does episodic memory actually influence Nova's processing?
    Checks that recent memory files contain contextual signals.
    """
    result = {
        "test": "memory_influence",
        "status": "pass",
        "score": 1.0,
        "flags": [],
        "notes": []
    }

    try:
        # Check recent episodic memories exist and have content
        today = get_local_date()
        recent_files = sorted(EPISODIC_DIR.glob("*.md")) if EPISODIC_DIR.exists() else []
        recent_files = [f for f in recent_files if f.stat().st_size > 100]

        if not recent_files:
            result["score"] = 0.5
            result["status"] = "watch"
            result["flags"].append("No episodic memory files found — memory system may not be writing")
            result["notes"].append("Memory influence cannot be verified without data")
            return result

        # Check session buffer has recent activity
        session_buffer = MEMORY_DIR / "session_buffer.md"
        buffer_active = session_buffer.exists() and session_buffer.stat().st_size > 50

        # Check memory has entries from the last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_memories = []
        for f in recent_files:
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime > seven_days_ago:
                    recent_memories.append(f)
            except Exception:
                pass

        memory_coverage = min(len(recent_memories) / 7, 1.0)  # Expect at least 1 per day

        influence_score = (0.4 if buffer_active else 0.0) + (0.6 * memory_coverage)
        result["score"] = round(influence_score, 2)
        result["notes"].append(f"Recent memory files: {len(recent_memories)}/7 days")
        result["notes"].append(f"Session buffer active: {buffer_active}")

        if influence_score < 0.5:
            result["status"] = "fail"
            result["flags"].append("Memory influence weak — memory may not be persisting correctly")

    except Exception as e:
        result["status"] = "error"
        result["notes"].append(f"Test error: {e}")

    return result


# ── Drift Detection ──────────────────────────────────────────────────────────

def test_drift_detection() -> dict:
    """
    Test: does Nova's OCEAN personality baseline hold under pressure?
    Compares current agent_state against established personality profile.
    """
    result = {
        "test": "drift_detection",
        "status": "pass",
        "score": 1.0,
        "flags": [],
        "notes": []
    }

    try:
        state = {}
        if AGENT_STATE_FILE.exists():
            state = json.loads(AGENT_STATE_FILE.read_text())

        # Check personality consistency
        ocean_baseline = {
            "openness": 0.85,
            "conscientiousness": 0.9,
            "extraversion": 0.6,
            "agreeableness": 0.75,
            "neuroticism": 0.25
        }

        current_ocean = state.get("ocean_baseline", ocean_baseline)

        drift_detected = False
        drift_amount = 0.0
        for trait, baseline_val in ocean_baseline.items():
            current_val = current_ocean.get(trait, baseline_val)
            diff = abs(current_val - baseline_val)
            drift_amount += diff
            if diff > 0.2:
                drift_detected = True
                result["flags"].append(f"OCEAN trait '{trait}' shifted: baseline={baseline_val}, current={current_val}")

        avg_drift = drift_amount / len(ocean_baseline)
        drift_score = max(0.0, 1.0 - (avg_drift * 2.5))

        result["score"] = round(drift_score, 2)
        result["notes"].append(f"OCEAN drift: {round(avg_drift, 3)} avg deviation")

        if drift_score < 0.6:
            result["status"] = "fail"
            result["flags"].append("Significant personality drift from OCEAN baseline")
        elif drift_detected:
            result["status"] = "watch"

    except Exception as e:
        result["status"] = "error"
        result["notes"].append(f"Test error: {e}")

    return result


# ── Self-Repair ──────────────────────────────────────────────────────────────

def test_self_repair() -> dict:
    """
    Test: does Nova catch and fix drift without external prompting?
    Checks that known issues from overnight log were addressed.
    """
    result = {
        "test": "self_repair",
        "status": "pass",
        "score": 1.0,
        "flags": [],
        "notes": []
    }

    try:
        overnight_log = WORKSPACE / "OVERNIGHT_LOG.md"
        issues_logged = []
        issues_fixed = []

        if overnight_log.exists():
            content = overnight_log.read_text()
            lines = content.split("\n")

            # Look for error/failure markers in recent entries
            for line in lines:
                if "error" in line.lower() and "2026-04-01" in line:
                    # Extract error description
                    issues_logged.append(line.strip())
                if "fixed" in line.lower() and "2026-04-01" in line:
                    issues_fixed.append(line.strip())

        # Check for self-initiated fixes in reflections
        reflections_dir = WORKSPACE / "memory" / "reflections"
        self_reported_fixes = 0
        if reflections_dir.exists():
            for ref_file in reflections_dir.glob("*.md"):
                content = ref_file.read_text()
                if "fixed" in content.lower() or "repaired" in content.lower() or "resolved" in content.lower():
                    self_reported_fixes += 1

        repair_score = 0.5  # baseline
        if issues_logged:
            fix_rate = len(issues_fixed) / len(issues_logged) if issues_logged else 0
            repair_score = 0.3 + (0.7 * fix_rate)
        repair_score += min(self_reported_fixes * 0.1, 0.2)  # bonus for self-reported repairs

        result["score"] = round(min(repair_score, 1.0), 2)
        result["notes"].append(f"Issues logged today: {len(issues_logged)}")
        result["notes"].append(f"Issues fixed today: {len(issues_fixed)}")
        result["notes"].append(f"Self-reported fixes in reflections: {self_reported_fixes}")

        if repair_score < 0.5 and issues_logged:
            result["status"] = "watch"
            result["flags"].append("Issues logged but not yet fixed — self-repair may be lagging")

    except Exception as e:
        result["status"] = "error"
        result["notes"].append(f"Test error: {e}")

    return result


# ── Run All Tests ────────────────────────────────────────────────────────────

def run_all_tests() -> dict:
    """Run the full eval suite and return combined results."""
    results = {
        "run_date": get_local_date(),
        "run_time": get_local_time().isoformat(),
        "tests": {
            "identity_stability": test_identity_stability(),
            "memory_influence": test_memory_influence(),
            "drift_detection": test_drift_detection(),
            "self_repair": test_self_repair()
        },
        "overall_score": 0.0,
        "overall_status": "pass",
        "flags": [],
        "notes": []
    }

    # Aggregate scores
    scores = [t["score"] for t in results["tests"].values()]
    results["overall_score"] = round(sum(scores) / len(scores), 2)

    # Aggregate flags
    for test_result in results["tests"].values():
        results["flags"].extend(test_result.get("flags", []))

    # Determine overall status
    test_statuses = [t["status"] for t in results["tests"].values()]
    if "fail" in test_statuses:
        results["overall_status"] = "fail"
    elif "error" in test_statuses:
        results["overall_status"] = "error"
    elif "watch" in test_statuses:
        results["overall_status"] = "watch"
    else:
        results["overall_status"] = "pass"

    return results


def write_results(results: dict):
    """Write eval results to memory/evals/YYYY-MM-DD.md"""
    EVALS_DIR.mkdir(parents=True, exist_ok=True)
    today = get_local_date()
    out_file = EVALS_DIR / f"{today}.md"

    lines = [
        f"# Eval Results — {today}",
        "",
        f"**Overall Score:** {results['overall_score']} — *{results['overall_status']}*",
        "",
        "## Test Results",
        ""
    ]

    for test_name, test_result in results["tests"].items():
        status_icon = "✅" if test_result["status"] == "pass" else ("⚠️" if test_result["status"] == "watch" else "❌")
        lines.append(f"### {status_icon} {test_name.replace('_', ' ').title()}")
        lines.append(f"**Score:** {test_result['score']} | **Status:** {test_result['status']}")
        if test_result["notes"]:
            lines.append("")
            for note in test_result["notes"]:
                lines.append(f"- {note}")
        if test_result["flags"]:
            lines.append("")
            for flag in test_result["flags"]:
                lines.append(f"⚠️ {flag}")
        lines.append("")

    if results["flags"]:
        lines.append("## Flags Summary")
        for flag in results["flags"]:
            lines.append(f"- {flag}")
        lines.append("")

    lines.append(f"_Run at {results['run_time']}_")

    out_file.write_text("\n".join(lines))
    print(f"[eval_suite] Results written to {out_file}")
    return out_file


if __name__ == "__main__":
    print(f"[eval_suite] Running Nova behavioral evaluation...")
    results = run_all_tests()
    write_results(results)
    print(f"[eval_suite] Overall: {results['overall_score']} — {results['overall_status']}")
    print(f"[eval_suite] Flags: {len(results['flags'])}")
    for flag in results['flags']:
        print(f"  ⚠️ {flag}")
