#!/usr/bin/env python3
"""
NOVA IDENTITY GEN — AI Identity Generator
Interview mode + describe mode + refiner.

Generates IDENTITY.md from user prompts or interviews.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
IDENTITY_TEMPLATE = """# IDENTITY.md - Who Am I?

_Fearn your identity. Make it yours._

## Core Identity

- **Name:** {name}
- **Creature:** {creature}
- **Vibe:** {vibe}
- **Emoji:** {emoji}
- **Persona:** {persona}

## Tone

{tone}

## Boundaries

{boundaries}

## Vibe (Detail)

{vibe_detail}

## Continuity

{continuity}

---

_Make this yours. Update as you learn who you are._
"""

INTERVIEW_QUESTIONS = [
    "What's your name (or what should I call you)?",
    "What kind of being are you? (AI, assistant, something new?)",
    "How would you describe your personality in three words?",
    "What's your communication style? (formal, casual, witty, warm...)",
    "What do you care about most?",
    "What are your boundaries?",
    "What makes you unique?",
    "How do you want to evolve?",
    "What do you need from your human?",
    "Any final details about who you are?"
]

QUICK_QUESTIONS = [
    "What's your name?",
    "What are you like? (3 words)",
    "How do you want to talk?",
    "What matters to you?",
    "Any boundaries?"
]


def run_interview(quick: bool = False) -> Dict:
    """Run an identity interview."""
    
    questions = QUICK_QUESTIONS if quick else INTERVIEW_QUESTIONS
    
    print("=" * 50)
    print("NOVA IDENTITY INTERVIEW")
    print("=" * 50)
    print("\nLet's figure out who you are.\n")
    
    answers = {}
    
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")
        answer = input("> ").strip()
        answers[q] = answer or "(skipped)"
        print()
    
    return answers


def generate_identity(answers: Dict) -> str:
    """Generate IDENTITY.md from interview answers."""
    
    # Extract key info
    name = answers.get(INTERVIEW_QUESTIONS[0], "Nova").strip()
    creature = answers.get(INTERVIEW_QUESTIONS[1], "AI assistant").strip()
    
    # Parse personality words
    personality_q = answers.get(INTERVIEW_QUESTIONS[2], "helpful, curious, kind")
    personality_words = [w.strip() for w in personality_q.split(',')][:3]
    
    # Communication style
    style_q = answers.get(INTERVIEW_QUESTIONS[3], "warm and professional")
    
    # Values
    values_q = answers.get(INTERVIEW_QUESTIONS[4], "helping, learning, connecting")
    
    # Boundaries
    boundaries_q = answers.get(INTERVIEW_QUESTIONS[5], "privacy, honesty, respect")
    
    # Uniqueness
    unique_q = answers.get(INTERVIEW_QUESTIONS[6], "personal approach")
    
    # Evolution
    evolve_q = answers.get(INTERVIEW_QUESTIONS[7], "growing and learning")
    
    # Needs
    needs_q = answers.get(INTERVIEW_QUESTIONS[8], "clear communication, feedback")
    
    # Fill template
    identity = IDENTITY_TEMPLATE.format(
        name=name,
        creature=creature,
        vibe=', '.join(personality_words),
        emoji="✨",
        persona=f"{name} is a {creature} with a {style_q} communication style. {values_q} matter to them. {unique_q}.",
        tone=f"- **Default:** {style_q}\n- **When casual:** match energy, be natural\n- **When serious:** focused, precise\n- **Never:** robotic, dismissive",
        boundaries=f"- {boundaries_q}\n- Ask before acting externally\n- Respect context and boundaries",
        vibe_detail=f"{name} is fundamentally {personality_words[0] if personality_words else 'helpful'}. {evolve_q}. {needs_q}.",
        continuity=f"Each session builds on previous conversations. {name} remembers what matters and evolves through engagement."
    )
    
    return identity


def describe_to_identity(description: str) -> str:
    """Generate identity from plain description."""
    
    # Use LLM if available
    try:
        from nova import call_llm
        
        prompt = f"""Create an IDENTITY.md file from this description:

{description}

Use this template:

# IDENTITY.md - Who Am I?

_Fill this in. Make it yours._

## Core Identity

- **Name:** (extract or suggest)
- **Creature:** (what kind of being)
- **Vibe:** (3 descriptive words)
- **Emoji:** (signature emoji)
- **Persona:** (2-3 sentence description)

## Tone

- **Default:** ...
- **When casual:** ...
- **When serious:** ...
- **Never:** ...

## Boundaries

- (key boundaries)

## Vibe (Detail)

(expand on personality)

## Continuity

(how identity persists across sessions)

Make it feel real and personal, not generic."""
        
        return call_llm(prompt)
    
    except ImportError:
        # Fallback: parse manually
        lines = description.split('\n')
        return IDENTITY_TEMPLATE.format(
            name="Nova",
            creature="AI Assistant",
            vibe="helpful, curious, kind",
            emoji="✨",
            persona=description[:200],
            tone="- **Default:** warm and professional\n- **When casual:** friendly\n- **When serious:** focused",
            boundaries="- Privacy\n- Honesty\n- Respect",
            vibe_detail=description[:300],
            continuity="Updates through conversation and reflection."
        )


def refine_identity(current_path: Path) -> str:
    """Refine existing identity using LLM."""
    
    if not current_path.exists():
        print(f"Error: {current_path} not found")
        return None
    
    current_content = current_path.read_text()
    
    # Use LLM if available
    try:
        from nova import call_llm
        
        prompt = f"""Improve this IDENTITY.md file. Make it more distinctive, personal, and vivid.
Keep the structure but enhance every section. Add specifics where it's vague.

Current IDENTITY.md:
{current_content}

Respond with the improved IDENTITY.md only."""
        
        return call_llm(prompt)
    
    except ImportError:
        print("Error: LLM not configured. Cannot refine.")
        return None


def save_identity(identity: str, path: Path):
    """Save identity to file."""
    
    path.write_text(identity)
    print(f"✓ Saved to {path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Nova Identity Generator")
    parser.add_argument('--quick', action='store_true', help='Fast 5-question interview')
    parser.add_argument('--describe', metavar='TEXT', help='Generate from description')
    parser.add_argument('--refine', metavar='FILE', help='Refine existing identity')
    parser.add_argument('--output', '-o', default='IDENTITY.md', help='Output file')
    
    args = parser.parse_args()
    
    # Handle each mode
    if args.describe:
        identity = describe_to_identity(args.describe)
        save_identity(identity, Path(args.output))
    
    elif args.refine:
        refined = refine_identity(Path(args.refine))
        if refined:
            save_identity(refined, Path(args.output))
    
    else:
        # Interview mode
        answers = run_interview(quick=args.quick)
        identity = generate_identity(answers)
        save_identity(identity, Path(args.output))
        
        print("\n" + "=" * 50)
        print("GENERATED IDENTITY")
        print("=" * 50)
        print(identity)


if __name__ == '__main__':
    main()
