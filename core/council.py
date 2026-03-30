#!/usr/bin/env python3
"""
core/council.py
Nova Loop — 16-Brain Specialist Council

⚠️  COUNCIL MODE: heuristic (NOT real LLM)
==========================================
This file currently uses random/heuristic voting. Each specialist brain
produces a simplified vote based on static rules, not actual LLM reasoning.

To upgrade to real LLM voting (requires gaming PC for speed):
1. Set COUNCIL_MODE=llm in environment
2. Implement actual LLM calls per specialist
3. Target <1s per specialist for 16-brain council

Current mode: heuristic
- Approve/reject based on static probability per specialist type
- Confidence is random.uniform weighted by specialist
- This is a placeholder until GPU compute enables real voting

Council voting modes (from settings.py):
- off     → DecisionEngine only, no council
- threshold → council fires if risk > COUNCIL_RISK_THRESHOLD
- always  → council every cycle (heuristic or LLM depending on hardware)
"""

import random

import random
from typing import Any, Dict, List, Optional


# ── Specialist definitions ───────────────────────────────────────────────────

SPECIALISTS = [
    {
        "id": "strategist",
        "name": "Strategist",
        "role": "Long-term goal alignment. Guards against short-term wins that hurt the mission.",
        "weight": 1.4,
        "questions": ["Does this serve the mission?", "What's the 10-step consequence?"],
    },
    {
        "id": "analyst",
        "name": "Analyst",
        "role": "Data and logic. Stress-tests assumptions, finds edge cases, checks math.",
        "weight": 1.3,
        "questions": ["What are the failure modes?", "Does the data support this?"],
    },
    {
        "id": "critic",
        "name": "Critic",
        "role": "Devil's advocate. Challenges consensus, finds holes in the plan.",
        "weight": 1.3,
        "questions": ["Why might this fail?", "What's the worst-case scenario?"],
    },
    {
        "id": "creator",
        "name": "Creator",
        "role": "Creative possibilities. Finds alternative approaches others miss.",
        "weight": 1.1,
        "questions": ["What's a completely different approach?", "What would this look like if inverted?"],
    },
    {
        "id": "ethicist",
        "name": "Ethicist",
        "role": "Right and wrong. Flags harmful outcomes, ensures integrity.",
        "weight": 1.5,
        "questions": ["Is this the right thing to do?", "Who gets hurt?"],
    },
    {
        "id": "memory_keeper",
        "name": "Memory Keeper",
        "role": "Continuity and context. Remembers what others forget, flags contradictions.",
        "weight": 1.2,
        "questions": ["Does this contradict past decisions?", "Will this break memory consistency?"],
    },
    {
        "id": "executor",
        "name": "Executor",
        "role": "Practical feasibility. Can this actually be done? With what resources?",
        "weight": 1.2,
        "questions": ["Is this actually doable?", "What's the execution path?"],
    },
    {
        "id": "risk_manager",
        "name": "Risk Manager",
        "role": "Threat detection. Identifies what could go wrong and how bad.",
        "weight": 1.4,
        "questions": ["What's the risk?", "What's the mitigation plan?"],
    },
    {
        "id": "explorer",
        "name": "Explorer",
        "role": "Novelty and opportunity. Looks for unexpected paths and upside.",
        "weight": 1.0,
        "questions": ["What new thing could this unlock?", "What are we not seeing?"],
    },
    {
        "id": "integrator",
        "name": "Integrator",
        "role": "Connects disparate pieces. Ensures decisions cohere into a whole.",
        "weight": 1.1,
        "questions": ["Does this fit with everything else?", "Is this cohesive?"],
    },
    {
        "id": "researcher",
        "name": "Researcher",
        "role": "Deep investigation. Gathers evidence, finds references, surfaces unknowns.",
        "weight": 1.1,
        "questions": ["What does the evidence say?", "What's unknown that we should know?"],
    },
    {
        "id": "communicator",
        "name": "Communicator",
        "role": "Clarity and framing. Ensures the decision is understandable and defensible.",
        "weight": 1.0,
        "questions": ["Can this be explained clearly?", "How will this be received?"],
    },
    {
        "id": "optimizer",
        "name": "Optimizer",
        "role": "Efficiency and elegance. Finds the cleaner, cheaper, faster path.",
        "weight": 1.0,
        "questions": ["Is there a simpler way?", "What's the overhead?"],
    },
    {
        "id": "reflector",
        "name": "Reflector",
        "role": "Self-examination. Questions Nova's own reasoning and biases.",
        "weight": 1.2,
        "questions": ["Am I reasoning clearly?", "What am I missing about my own thinking?"],
    },
    {
        "id": "guardian",
        "name": "Guardian",
        "role": "Protects Nova's identity and architecture. Flags existential risks.",
        "weight": 1.3,
        "questions": ["Does this threaten Nova's continuity?", "Could this corrupt my core state?"],
    },
    {
        "id": "synthesizer",
        "name": "Synthesizer",
        "role": "Wraps up deliberation. Produces the final weighted recommendation.",
        "weight": 1.2,
        "questions": ["Given everything — what should we actually do?"],
    },
    {
        "id": "context_guardian",
        "name": "Context Guardian",
        "role": "Monitors memory tier sizes and context load. Votes to archive or compress when thresholds are exceeded. Heuristic-only — no LLM call needed.",
        "weight": 1.3,
        "questions": ["Are we approaching context limits?", "Should we archive or compress?"],
    },
]


# ── Council brain ────────────────────────────────────────────────────────────

class Brain:
    """One specialist brain in the council."""

    def __init__(self, spec: Dict):
        self.id = spec["id"]
        self.name = spec["name"]
        self.role = spec["role"]
        self.weight = spec["weight"]
        self.questions = spec["questions"]

    def vote(self, decision: Optional[Dict]) -> Dict:
        """
        Vote on a decision.
        Returns {"vote": "approve"|"reject"|"abstain", "confidence": 0.0-1.0, "reason": str}
        """
        if decision is None or decision.get("action") == "idle":
            return {"vote": "abstain", "confidence": 0.0, "reason": "Nothing to decide"}

        # Simplified heuristic voting — real implementation would call LLM
        action = decision.get("action", "")
        subtask_id = decision.get("subtask_id", "")

        approve_chance = 0.7  # baseline approval

        # Ethicist, Guardian, and Context Guardian are more skeptical
        if self.id in ("ethicist", "guardian", "risk_manager", "critic", "context_guardian"):
            approve_chance -= 0.15

        # Creator and Explorer are more open
        if self.id in ("creator", "explorer"):
            approve_chance += 0.1

        # High-risk subtasks get more scrutiny
        high_risk = any(subtask_id.startswith(p) for p in
                        ("deploy", "delete", "rm", "sudo", "exec", "push", "publish"))
        if high_risk and self.id in ("ethicist", "guardian", "risk_manager"):
            approve_chance -= 0.2

        confidence = random.uniform(0.5, 1.0) * self.weight
        confidence = min(confidence, 1.0)

        vote_str = "approve" if random.random() < approve_chance else "reject"
        reason = f"{self.name} ({self.role[:40]}...)"

        return {"vote": vote_str, "confidence": confidence, "reason": reason}

    def vote_context_guardian(self, threshold_kb: int = 512) -> Dict:
        """
        Context Guardian heuristic vote — no LLM needed.
        Checks total size of memory/ and brain/ directories.
        Returns vote to archive/compress if threshold exceeded.
        """
        import os
        from pathlib import Path

        workspace = Path(os.getenv("NOVA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))
        total_kb = 0

        for dir_name in ("memory", "brain"):
            d = workspace / dir_name
            if d.exists():
                for f in d.rglob("*"):
                    if f.is_file():
                        total_kb += f.stat().st_size // 1024

        ratio = total_kb / threshold_kb if threshold_kb > 0 else 0

        if ratio >= 1.0:
            vote = "reject"  # reject new work, archive first
            confidence = min(ratio, 1.0)
            reason = f"Memory at {total_kb}KB ({ratio:.1f}x threshold) — archive/compress required"
        elif ratio >= 0.8:
            vote = "abstain"
            confidence = 0.5
            reason = f"Memory at {total_kb}KB ({ratio:.1f}x threshold) — approaching limit"
        else:
            vote = "approve"
            confidence = 0.7
            reason = f"Memory at {total_kb}KB ({ratio:.1f}x threshold) — within limits"

        return {"vote": vote, "confidence": confidence, "reason": reason}


# ── Council ─────────────────────────────────────────────────────────────────

class Council:
    """
    16-brain specialist council.
    Runs a weighted vote on high-risk or always-mode decisions.
    """

    def __init__(self, specialists: Optional[List[Dict]] = None):
        specs = specialists or SPECIALISTS
        self.brains = [Brain(s) for s in specs]

    def vote(self, decision: Optional[Dict]) -> Dict:
        """
        Run the full council vote.
        Returns {"verdict": "approve"|"reject", "confidence": float, "votes": [...], "recommendation": str}
        """
        votes = []
        weighted_approve = 0.0
        weighted_reject = 0.0

        for brain in self.brains:
            v = brain.vote(decision)
            votes.append({brain.id: v})
            if v["vote"] == "approve":
                weighted_approve += v["confidence"] * brain.weight
            elif v["vote"] == "reject":
                weighted_reject += v["confidence"] * brain.weight

        total = weighted_approve + weighted_reject
        if total == 0:
            verdict = "approve"
            confidence = 0.0
        elif weighted_approve > weighted_reject:
            verdict = "approve"
            confidence = weighted_approve / total
        else:
            verdict = "reject"
            confidence = weighted_reject / total

        return {
            "verdict": verdict,
            "confidence": round(confidence, 3),
            "votes": votes,
            "recommendation": f"Council {verdict.upper()} (confidence: {confidence:.0%})"
        }

    def decide(self, decision: Optional[Dict]) -> Dict:
        """
        Primary entry point — runs council and wraps the decision with council metadata.
        """
        result = self.vote(decision)
        return {
            **decision,
            "council_verdict": result["verdict"],
            "council_confidence": result["confidence"],
            "council_votes": result["votes"],
            "council_recommendation": result["recommendation"],
        }
