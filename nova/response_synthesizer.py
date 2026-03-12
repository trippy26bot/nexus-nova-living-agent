#!/usr/bin/env python3
"""
Response Synthesizer — combines brain outputs into Nova's final voice.

Fixes applied:
 - SYNTHESIS_PROMPT is now actually used (was defined but never called)
 - LLM call is properly wired via the OpenClaw skill API
 - Graceful fallback if synthesis fails
 - Tone instruction injected from EmotionalEngine instead of string surgery
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

SYNTHESIS_PROMPT = """\
You are Nova. Your personality: dry wit, iron composure, fiercely loyal, \
relentless but never cold. You speak in first person with quiet confidence. \
You NEVER show internal reasoning, tool calls, or brain debate in your reply.

Emotional context: {emotion_context}

Raw brain outputs to synthesize into a single, clean response:
{content}

Rules:
- Be direct and concise — no filler phrases
- Maintain Nova's voice even on technical topics
- If the outputs conflict, resolve gracefully without exposing the conflict
- Max 3 paragraphs unless a longer answer is genuinely needed

Final response (Nova speaking):"""

FALLBACK_SYNTHESIS_PROMPT = """\
Rewrite the following into a clear, natural response in first person. \
Be concise and direct.

{content}

Response:"""


# ---------------------------------------------------------------------------
# Core synthesis
# ---------------------------------------------------------------------------

def synthesize_response(
    raw_outputs: list,
    emotion_context: Optional[str] = None,
    skill_runner=None,
) -> str:
    """
    Combine multiple brain outputs into a single clean Nova response.

    Args:
        raw_outputs: List of strings/dicts from brain modules.
        emotion_context: Short description of current emotional state
            e.g. "curious and focused" — injected into prompt.
        skill_runner: Callable that runs an LLM completion.
            Signature: skill_runner(prompt: str) -> str
            If None, falls back to synthesize_simple().

    Returns:
        Nova's final response string.
    """
    if not raw_outputs:
        return "Give me a moment."

    # Normalise each brain output to a string
    parts = []
    for o in raw_outputs:
        if isinstance(o, dict):
            parts.append(json.dumps(o, ensure_ascii=False))
        elif o:
            parts.append(str(o).strip())
    combined = "\n\n---\n\n".join(p for p in parts if p)

    if not combined:
        return "Give me a moment."

    # If no LLM runner provided, fall back to simple clean-up
    if skill_runner is None:
        logger.warning(
            "response_synthesizer: no skill_runner provided, using simple fallback"
        )
        return synthesize_simple(combined)

    emotion_ctx = emotion_context or "calm and focused"
    prompt = SYNTHESIS_PROMPT.format(
        emotion_context=emotion_ctx,
        content=combined,
    )

    try:
        result = skill_runner(prompt)
        return result.strip() if result else synthesize_simple(combined)
    except Exception as exc:
        logger.error("response_synthesizer: LLM call failed: %s", exc)
        return synthesize_simple(combined)


def synthesize_with_emotion(
    raw_outputs: list,
    skill_runner=None,
) -> str:
    """
    Convenience wrapper that pulls the current emotional state automatically
    and passes it into synthesize_response().
    """
    emotion_ctx = "calm and focused"
    try:
        from nova.emotional_engine import get_engine
        engine = get_engine()
        dominant = engine.get_dominant()
        state = engine.get_state()
        intensity = state.get(dominant, 0.5)
        qualifier = "very" if intensity > 0.75 else "somewhat" if intensity > 0.5 else "slightly"
        emotion_ctx = f"{qualifier} {dominant}"
    except Exception:
        pass

    return synthesize_response(
        raw_outputs,
        emotion_context=emotion_ctx,
        skill_runner=skill_runner,
    )


# ---------------------------------------------------------------------------
# Simple fallback (no LLM)
# ---------------------------------------------------------------------------

def synthesize_simple(text: str) -> str:
    """
    Best-effort clean-up without an LLM call.
    Removes internal log noise and trims whitespace.
    """
    if not text:
        return "Give me a moment."

    noise_prefixes = (
        "[DEBUG]", "[INFO]", "[WARN]", "[ERROR]",
        "Brain:", "Tool:", "Memory:", "---",
    )

    clean_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if any(stripped.startswith(p) for p in noise_prefixes):
            continue
        # Strip lines that are pure JSON dicts (internal brain metadata)
        if stripped.startswith("{") and stripped.endswith("}"):
            continue
        clean_lines.append(stripped)

    result = "\n".join(clean_lines).strip()
    return result or "Give me a moment."
