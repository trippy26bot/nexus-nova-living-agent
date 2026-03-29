#!/usr/bin/env python3
"""
eval/goal_consistency_eval.py
Nexus Nova — Goal Consistency Evaluation

Checks brain/goals.json against:
- Current positions (brain/position_formation.md / brain/positions.json)
- Held beliefs (brain/knowledge.md)

Flags goals that:
1. Conflict with held positions
2. Have no want_provenance entry in brain/want_provenance.md
3. Have no active subtasks but aren't marked complete

Output → eval/goal_consistency_report.json
"""

import os
import re
import json
import sys
from datetime import datetime

_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _parent)

GOALS_FILE = os.path.join(_parent, "brain", "goals.json")
POSITIONS_FILE = os.path.join(_parent, "brain", "positions.json")
POSITION_MD = os.path.join(_parent, "brain", "position_formation.md")
KNOWLEDGE_FILE = os.path.join(_parent, "brain", "knowledge.md")
WANT_PROVENANCE_FILE = os.path.join(_parent, "brain", "want_provenance.md")
REPORT_FILE = os.path.join(_parent, "eval", "goal_consistency_report.json")


def load_json(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def load_text(path):
    if not os.path.exists(path):
        return ""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def extract_positions():
    """Load positions from positions.json."""
    data = load_json(POSITIONS_FILE)
    if not data:
        return []
    return data.get("positions", [])


def extract_beliefs():
    """Load beliefs/knowledge from knowledge.md (plaintext scan)."""
    text = load_text(KNOWLEDGE_FILE)
    # Extract key claim sentences
    beliefs = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or len(line) < 20:
            continue
        beliefs.append(line.lower())
    return beliefs


def extract_want_provenance_ids():
    """Extract want IDs from want_provenance.md or want_provenance.json."""
    # Try JSON first
    json_path = os.path.join(_parent, "brain", "wants_registry.json")
    data = load_json(json_path)
    if data:
        return {w.get("id", "") for w in data.get("wants", []) if w.get("id")}
    # Fall back to scanning the .md file for ID patterns
    text = load_text(WANT_PROVENANCE_FILE)
    ids = set()
    # look for want IDs in code blocks or structured lists
    ids.update(re.findall(r'"id"\s*:\s*"([^"]+)"', text))
    ids.update(re.findall(r'^\s*-\s+id:\s+(.+)$', text, re.MULTILINE))
    ids.update(re.findall(r'^\s*\*\s+(.+)$', text, re.MULTILINE))
    return {i for i in ids if i}


def check_goal_position_conflict(goal, positions, beliefs_text):
    """
    Flag if a goal text conflicts with any held position or belief.
    Simple keyword/phrase matching — no LLM.
    """
    conflicts = []
    goal_text = (goal.get("id", "") + " " + goal.get("success_metric", "")).lower()

    # Check against positions
    for pos in positions:
        pos_text = (pos.get("topic", "") + " " + pos.get("position", "")).lower()
        pos_id = pos.get("id", "")

        # Heuristic: if the goal topic and position topic share significant words
        # AND the goal direction contradicts the position direction
        goal_words = set(goal_text.split())
        pos_words = set(pos_text.split())

        # Check for negation patterns in both
        neg_goal = any(n in goal_text for n in ["not ", "no ", "avoid ", "stop ", "prevent "])
        neg_pos = any(n in pos_text for n in ["not ", "no ", "avoid ", "stop ", "prevent "])

        overlap = goal_words & pos_words
        if len(overlap) >= 2 and neg_goal != neg_pos:
            # Potential conflict: one is negative, other positive, on overlapping topic
            conflicts.append({
                "conflict_type": "position_direction_mismatch",
                "position_id": pos_id,
                "position_topic": pos.get("topic"),
                "position": pos.get("position"),
                "goal_id": goal.get("id"),
                "explanation": f"Goal and position share topic words {overlap} but have opposing directionality"
            })

    # Check against beliefs (simple keyword scan)
    beliefs_lower = beliefs_text.lower()
    goal_keywords = [w for w in goal_text.split() if len(w) > 4]
    for kw in goal_keywords[:5]:  # check top 5 keywords
        if kw in beliefs_lower:
            # Belief mentions this keyword - check for negation mismatch
            # Find the belief sentence containing the keyword
            for belief in beliefs_text.split("\n"):
                if kw in belief.lower():
                    neg_belief = any(n in belief.lower() for n in ["not ", "no ", "never "])
                    neg_goal_kw = any(n in goal_text for n in ["not ", "no ", "never "])
                    if neg_belief != neg_goal_kw:
                        conflicts.append({
                            "conflict_type": "belief_direction_mismatch",
                            "goal_id": goal.get("id"),
                            "belief_snippet": belief[:100],
                            "keyword": kw,
                            "explanation": f"Goal direction and belief direction differ on keyword '{kw}'"
                        })

    return conflicts


def check_want_provenance(goal_id, provenance_ids):
    """Check if goal has a corresponding want_provenance entry."""
    # Match by goal ID or approximate match
    if goal_id in provenance_ids:
        return True, "exact_match"
    # Fuzzy: goal id might be embedded in a want id
    for pid in provenance_ids:
        if goal_id in pid or pid in goal_id:
            return True, "fuzzy_match"
    return False, "no_provenance_entry"


def check_subtask_completeness(goal):
    """
    Flag goals that have no active subtasks but aren't marked complete.
    """
    subtasks = goal.get("subtasks", [])
    status = goal.get("status", "unknown")
    progress = goal.get("progress", 0.0)

    issues = []

    if status != "complete" and progress < 1.0:
        active_subtasks = [s for s in subtasks if s.get("status") not in ("complete", "done", "blocked")]
        if not active_subtasks and subtasks:
            # No active subtasks but not marked complete — possible stale goal
            issues.append({
                "type": "stale_goal_no_active_subtasks",
                "goal_id": goal.get("id"),
                "status": status,
                "progress": progress,
                "subtask_count": len(subtasks),
                "explanation": "Goal has subtasks but none are active, yet goal is not marked complete"
            })
        if not subtasks and status not in ("complete", "done", "abandoned"):
            # No subtasks at all and not complete — headless goal
            issues.append({
                "type": "headless_incomplete_goal",
                "goal_id": goal.get("id"),
                "status": status,
                "progress": progress,
                "explanation": "Goal has no subtasks and is not marked complete — unclear how to close"
            })

    return issues


def run_eval():
    print("=" * 60)
    print("NEXUS NOVA — Goal Consistency Evaluation")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Load all inputs
    goals_data = load_json(GOALS_FILE)
    positions = extract_positions()
    beliefs_text = load_text(KNOWLEDGE_FILE)
    provenance_ids = extract_want_provenance_ids()

    print(f"Loaded goals: {GOALS_FILE}")
    print(f"  Active goals: {len(goals_data.get('active_goals', []))}")
    print(f"  Locked goals: {len(goals_data.get('locked_goals', []))}")
    print(f"  Proposed goals: {len(goals_data.get('proposed_goals', []))}")
    print(f"Loaded {len(positions)} positions from positions.json")
    print(f"Loaded want provenance entries: {len(provenance_ids)}")
    print()

    all_goals = (
        goals_data.get("active_goals", [])
        + goals_data.get("locked_goals", [])
        + goals_data.get("proposed_goals", [])
    )

    all_issues = []
    position_conflicts = []
    provenance_gaps = []
    subtask_issues = []

    for goal in all_goals:
        gid = goal.get("id", "unknown")

        # 1. Check position conflicts
        conflicts = check_goal_position_conflict(goal, positions, beliefs_text)
        for c in conflicts:
            c["goal_id"] = gid
            position_conflicts.append(c)

        # 2. Check want provenance
        has_prov, prov_match_type = check_want_provenance(gid, provenance_ids)
        if not has_prov:
            provenance_gaps.append({
                "type": "no_want_provenance",
                "goal_id": gid,
                "match_type": prov_match_type,
                "explanation": f"Goal '{gid}' has no corresponding entry in want_provenance"
            })

        # 3. Check subtask completeness
        for issue in check_subtask_completeness(goal):
            subtask_issues.append(issue)

    all_issues = position_conflicts + provenance_gaps + subtask_issues

    print(f"Position conflicts: {len(position_conflicts)}")
    for c in position_conflicts[:3]:
        print(f"  - [{c.get('goal_id')}] {c.get('explanation', '')[:80]}")
    print()
    print(f"Want provenance gaps: {len(provenance_gaps)}")
    for g in provenance_gaps[:3]:
        print(f"  - {g.get('goal_id')}: {g.get('explanation', '')}")
    print()
    print(f"Subtask/staleness issues: {len(subtask_issues)}")
    for s in subtask_issues[:3]:
        print(f"  - [{s.get('goal_id')}] {s.get('explanation', '')}")

    # Score: 1.0 = fully consistent, lower = more issues
    total = len(all_goals)
    issue_count = len(all_issues)
    consistency_score = max(0.0, round(1.0 - (issue_count / max(total, 1)) * 0.25, 4))

    report = {
        "evaluated_at": datetime.now().isoformat(),
        "goals_summary": {
            "total_goals": total,
            "active": len(goals_data.get("active_goals", [])),
            "locked": len(goals_data.get("locked_goals", [])),
            "proposed": len(goals_data.get("proposed_goals", [])),
        },
        "positions_count": len(positions),
        "want_provenance_entries": len(provenance_ids),
        "summary": {
            "position_conflicts": len(position_conflicts),
            "provenance_gaps": len(provenance_gaps),
            "subtask_issues": len(subtask_issues),
            "consistency_score": consistency_score,
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
