#!/usr/bin/env python3
"""
eval/eval_suite.py
Nexus Nova — Full Evaluation Suite

Runs all four evaluation modules:
  1. identity_drift   → eval/identity_drift.py
  2. memory_coherence → eval/memory_coherence_eval.py
  3. goal_consistency → eval/goal_consistency_eval.py
  4. behavioral_drift → eval/behavioral_drift_eval.py

Writes combined output to:
  - eval/suite_report.json
  - /Users/dr.claw/.openclaw/workspace/OVERNIGHT_LOG.md (appends plain-English summary)

Each eval reports: timestamp, status, score, issue_count.
"""

import os
import sys
import json
from datetime import datetime

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent)

SUITE_REPORT_FILE = os.path.join(_parent, "eval", "suite_report.json")
OVERNIGHT_LOG_FILE = os.path.join(_parent, "workspace", "OVERNIGHT_LOG.md")
# Handle case where workspace IS the parent
if not os.path.exists(OVERNIGHT_LOG_FILE):
    OVERNIGHT_LOG_FILE = os.path.join(_parent, "OVERNIGHT_LOG.md")


def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def run_identity_drift():
    """Run identity drift eval and return a summary dict."""
    try:
        from eval import identity_drift
        report = identity_drift.run_eval(init=False)
        return {
            "status": "ok",
            "score": report.get("consistency_score"),
            "drifted_files": len(report.get("drifted_files", [])),
            "report": report,
            "error": None,
        }
    except Exception as e:
        return {
            "status": "error",
            "score": None,
            "error": str(e),
            "report": None,
        }


def run_memory_coherence():
    """Run memory coherence eval and return a summary dict."""
    try:
        from eval import memory_coherence_eval
        report = memory_coherence_eval.run_eval()
        return {
            "status": "ok",
            "score": report.get("summary", {}).get("coherence_score"),
            "broken_references": report.get("summary", {}).get("broken_references", 0),
            "contradictions": report.get("summary", {}).get("contradictions", 0),
            "orphaned": report.get("summary", {}).get("orphaned_references", 0),
            "report": report,
            "error": None,
        }
    except Exception as e:
        return {
            "status": "error",
            "score": None,
            "error": str(e),
            "report": None,
        }


def run_goal_consistency():
    """Run goal consistency eval and return a summary dict."""
    try:
        from eval import goal_consistency_eval
        report = goal_consistency_eval.run_eval()
        return {
            "status": "ok",
            "score": report.get("summary", {}).get("consistency_score"),
            "position_conflicts": report.get("summary", {}).get("position_conflicts", 0),
            "provenance_gaps": report.get("summary", {}).get("provenance_gaps", 0),
            "subtask_issues": report.get("summary", {}).get("subtask_issues", 0),
            "report": report,
            "error": None,
        }
    except Exception as e:
        return {
            "status": "error",
            "score": None,
            "error": str(e),
            "report": None,
        }


def run_behavioral_drift():
    """Run behavioral drift eval and return a summary dict."""
    try:
        from eval import behavioral_drift_eval
        report = behavioral_drift_eval.run_eval()
        return {
            "status": "ok",
            "score": report.get("drift_score"),
            "drift_events": report.get("drift_events_count", 0),
            "report": report,
            "error": None,
        }
    except Exception as e:
        return {
            "status": "error",
            "score": None,
            "error": str(e),
            "report": None,
        }


def compute_overall_status(results):
    """Determine overall suite status from individual eval results."""
    if any(r["status"] == "error" for r in results.values()):
        return "errors"
    scores = [r.get("score") for r in results.values() if r.get("score") is not None]
    if not scores:
        return "unknown"
    avg = sum(scores) / len(scores)
    if avg >= 0.9:
        return "healthy"
    elif avg >= 0.7:
        return "caution"
    elif avg >= 0.5:
        return "warning"
    else:
        return "critical"


def build_summary_paragraph(results):
    """Build a plain-English paragraph summarizing all eval results."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    overall = results.get("_overall_status", "unknown")
    overall_label = {
        "healthy": "All systems are healthy — identity, memory, goals, and behavior are all consistent.",
        "caution": "Some areas need attention, but nothing critical.",
        "warning": "Multiple areas show signs of drift or inconsistency.",
        "critical": "Significant problems detected across one or more evaluation areas.",
        "errors": "One or more evaluation modules encountered errors and could not complete.",
        "unknown": "Could not determine overall system health.",
    }.get(overall, overall)

    lines = []
    lines.append(f"Ran full evaluation suite at {ts}. {overall_label}")

    for eval_name, result in results.items():
        if eval_name == "_overall_status":
            continue
        status = result.get("status", "unknown")
        score = result.get("score")
        error = result.get("error")

        if status == "error":
            lines.append(f"- {eval_name}: ERROR — {error}")
        elif score is not None:
            score_pct = f"{score:.1%}"
            issues = []
            if eval_name == "identity_drift":
                df = result.get("drifted_files", 0)
                if df > 0:
                    issues.append(f"{df} file(s) drifted")
            elif eval_name == "memory_coherence":
                br = result.get("broken_references", 0)
                cn = result.get("contradictions", 0)
                orp = result.get("orphaned", 0)
                if br: issues.append(f"{br} broken ref(s)")
                if cn: issues.append(f"{cn} contradiction(s)")
                if orp: issues.append(f"{orp} orphan(s)")
            elif eval_name == "goal_consistency":
                pc = result.get("position_conflicts", 0)
                pg = result.get("provenance_gaps", 0)
                si = result.get("subtask_issues", 0)
                if pc: issues.append(f"{pc} position conflict(s)")
                if pg: issues.append(f"{pg} provenance gap(s)")
                if si: issues.append(f"{si} subtask issue(s)")
            elif eval_name == "behavioral_drift":
                de = result.get("drift_events", 0)
                if de > 0:
                    issues.append(f"{de} drift event(s)")

            issue_str = f" Issues: {', '.join(issues)}." if issues else " No issues detected."
            lines.append(f"- {eval_name}: score {score_pct}.{issue_str}")
        else:
            lines.append(f"- {eval_name}: completed with no score")

    return "\n".join(lines)


def append_to_overnight_log(paragraph):
    """Append the plain-English summary to OVERNIGHT_LOG.md."""
    try:
        # Check if file exists
        file_exists = os.path.exists(OVERNIGHT_LOG_FILE)
        with open(OVERNIGHT_LOG_FILE, "a", encoding="utf-8") as f:
            if not file_exists:
                f.write("# OVERNIGHT_LOG.md — Nova System Reports\n\n")
            f.write(f"## {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write(paragraph)
            f.write("\n\n---\n\n")
        return True
    except Exception as e:
        print(f"  WARNING: Could not append to OVERNIGHT_LOG.md: {e}")
        return False


def run_suite():
    print("=" * 60)
    print("NEXUS NOVA — Full Evaluation Suite")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    print("Running all four evaluations...")
    print()

    # Run each eval
    results = {}

    print("[1/4] Running identity_drift...")
    results["identity_drift"] = run_identity_drift()
    id_status = results["identity_drift"]["status"]
    id_score = results["identity_drift"].get("score")
    print(f"  → status={id_status}, score={id_score}")
    print()

    print("[2/4] Running memory_coherence...")
    results["memory_coherence"] = run_memory_coherence()
    mc_status = results["memory_coherence"]["status"]
    mc_score = results["memory_coherence"].get("score")
    print(f"  → status={mc_status}, score={mc_score}")
    print()

    print("[3/4] Running goal_consistency...")
    results["goal_consistency"] = run_goal_consistency()
    gc_status = results["goal_consistency"]["status"]
    gc_score = results["goal_consistency"].get("score")
    print(f"  → status={gc_status}, score={gc_score}")
    print()

    print("[4/4] Running behavioral_drift...")
    results["behavioral_drift"] = run_behavioral_drift()
    bd_status = results["behavioral_drift"]["status"]
    bd_score = results["behavioral_drift"].get("score")
    print(f"  → status={bd_status}, score={bd_score}")
    print()

    # Overall status
    overall = compute_overall_status(results)
    results["_overall_status"] = overall
    print(f"Overall suite status: {overall.upper()}")
    print()

    # Write suite report
    suite_report = {
        "suite_run_at": datetime.now().isoformat(),
        "overall_status": overall,
        "evaluations": results,
    }
    ensure_dir(SUITE_REPORT_FILE)
    with open(SUITE_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(suite_report, f, indent=2)
    print(f"Suite report written to: {SUITE_REPORT_FILE}")
    print()

    # Build and append plain-English summary to OVERNIGHT_LOG.md
    paragraph = build_summary_paragraph(results)
    print("Plain-English summary:")
    print()
    print(paragraph)
    print()

    if append_to_overnight_log(paragraph):
        print(f"Summary appended to: {OVERNIGHT_LOG_FILE}")
    else:
        print(f"WARNING: Could not append to OVERNIGHT_LOG.md (file at {OVERNIGHT_LOG_FILE})")

    return results


if __name__ == "__main__":
    run_suite()
