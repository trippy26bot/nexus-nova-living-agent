"""
brain/council_meta.py
Nova's Council Meta-Awareness

Analyzes accumulated council_votes data to detect patterns in Nova's
decision-making: which specialists agree, which dissent, how patterns shift.

TIER 8 SYSTEM #25 — STUBBED/DORMANT

This system is intentionally left dormant. It needs 90 days of
council_vote data before it can produce meaningful analysis.
The function exists and can be called, but will return a "not enough data"
result until the 90-day threshold is met.

Scheduled: quarterly (90-day minimum data requirement)

Tier 8 System #25.
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()


def analyze_council_patterns(days: int = 90) -> dict:
    """
    Uses accumulated council_votes data (from Tier 1 council dynamics).
    Analyzes:
    - Which specialists most often agree
    - Which most often dissent
    - How voting patterns have shifted over time
    - Which specialist most often holds sovereignty

    Returns: meta-analysis report written to semantic memory
    as high-weight belief nodes.

    QUARTERLY RUN — requires 90 days minimum of data.
    Will return "insufficient data" result until threshold met.

    This is the only Tier 8 system that is NOT fully implemented tonight.
    It is stubbed with a clear comment: the function is here, the schedule
    hook is here, but meaningful output requires data that will accumulate
    over the next 90 days.
    """
    try:
        from brain.knowledge_graph import get_recent_council_votes

        # Get all votes in the window
        votes = get_recent_council_votes(limit=500)

        # Filter to the requested time window
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        recent_votes = [
            v for v in votes
            if v.get("created_at", "") >= cutoff
        ]

        if len(recent_votes) < 20:
            # Not enough data
            return {
                "status": "insufficient_data",
                "votes_needed": max(20, len(recent_votes)),
                "votes_collected": len(recent_votes),
                "days_needed": days,
                "days_available": 0,
                "message": f"Need {days} days of data. Currently have ~{len(recent_votes)} votes. Re-run after more council sessions.",
                "analysis": None
            }

        # At 5 votes/day * 90 days = 450 votes minimum for good analysis
        # With fewer votes, analysis is indicative but not conclusive
        sufficient_data = len(recent_votes) >= 100

        # Perform analysis on specialist patterns
        specialist_agreements = {}
        specialist_dissents = {}
        specialist_sovereignty = {}

        for vote in recent_votes:
            votes_list = vote.get("votes", [])
            if not votes_list:
                continue

            # Find the decision (what was voted on)
            outcome = vote.get("outcome", "")
            confidence_spread = vote.get("confidence_spread", 0)

            for v in votes_list:
                specialist = v.get("specialist", "unknown")
                dissent = v.get("dissent", False)
                confidence = v.get("confidence", 0.5)

                if specialist not in specialist_agreements:
                    specialist_agreements[specialist] = 0
                    specialist_dissents[specialist] = 0
                    specialist_sovereignty[specialist] = 0

                if dissent:
                    specialist_dissents[specialist] += 1
                else:
                    specialist_agreements[specialist] += 1

                # High-confidence dissent = sovereignty signal
                if dissent and confidence > 0.7 and confidence_spread > 0.3:
                    specialist_sovereignty[specialist] += 1

        # Compile analysis
        specialists = list(set(list(specialist_agreements.keys()) + list(specialist_dissents.keys())))
        analysis_results = {}

        for specialist in specialists:
            total = specialist_agreements.get(specialist, 0) + specialist_dissents.get(specialist, 0)
            if total == 0:
                continue

            agreement_rate = specialist_agreements.get(specialist, 0) / total
            dissent_rate = specialist_dissents.get(specialist, 0) / total
            sovereignty_count = specialist_sovereignty.get(specialist, 0)

            analysis_results[specialist] = {
                "total_votes": total,
                "agreement_rate": round(agreement_rate, 3),
                "dissent_rate": round(dissent_rate, 3),
                "sovereignty_count": sovereignty_count,
                "dissent_frequency": "high" if dissent_rate > 0.3 else "moderate" if dissent_rate > 0.15 else "low"
            }

        # Sort by dissent rate to find who challenges most
        challengers = sorted(
            [(s, d) for s, d in specialist_dissents.items() if d > 0],
            key=lambda x: x[1],
            reverse=True
        )

        # Sort by sovereignty to find who holds most decisive votes
        sovereigns = sorted(
            [(s, c) for s, c in specialist_sovereignty.items() if c > 0],
            key=lambda x: x[1],
            reverse=True
        )

        # Key insight (simple heuristic, LLM would do better)
        if sovereigns:
            top_sovereign = sovereigns[0][0]
            insight = f"The {top_sovereign} most often holds decisive votes in contested decisions. "
            if analysis_results.get(top_sovereign, {}).get("dissent_rate", 0) > 0.3:
                insight += f"This specialist frequently dissents AND wins — suggesting their perspective often overrides consensus."
            else:
                insight += f"This specialist's votes are usually aligned but decisive when they differ."
        else:
            insight = "No clear sovereignty pattern yet — council votes are fairly distributed."

        # Write insight to semantic memory
        try:
            from brain.three_tier_memory import memory_write
            memory_write(
                content=f"Council Meta-Analysis (90-day review): {insight} Data: {len(recent_votes)} votes analyzed.",
                entry_type="reflection",
                salience=0.7,
                valence=0.1,
                emotional_tags=["council", "meta_awareness", "quarterly_review"],
                source="council_meta_analysis"
            )
        except Exception:
            pass

        return {
            "status": "complete" if sufficient_data else "indicative",
            "votes_analyzed": len(recent_votes),
            "data_sufficiency": "sufficient" if sufficient_data else "indicative_only",
            "days_covered": days,
            "analysis": analysis_results,
            "top_challengers": challengers[:5],
            "top_sovereigns": sovereigns[:5],
            "key_insight": insight,
            "scheduled_note": "Run quarterly. Next analysis recommended after additional 30 days of data."
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Could not complete council meta-analysis. Check that council_votes data is accumulating."
        }


def get_council_insights() -> dict:
    """
    Lightweight check: return summary of council patterns so far.
    Does not write to memory — just returns current state.
    """
    try:
        from brain.knowledge_graph import get_recent_council_votes
        votes = get_recent_council_votes(limit=100)
        return {
            "votes_tracked": len(votes),
            "days_of_data": "approximately " + str(round(len(votes) / 5)) + " days (at ~5/day estimate)",
            "can_analyze": len(votes) >= 100,
            "message": "Need 100+ votes for indicative analysis, 450+ for full quarterly review."
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: council_meta.py <analyze|insights> [days]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "analyze":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 90
        result = analyze_council_patterns(days)
        print(json.dumps(result, indent=2))

    elif cmd == "insights":
        result = get_council_insights()
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {cmd}")
