# LEARNINGS.md
Corrections, knowledge gaps, and best practices discovered during development.

## [LRN-20260304-001] operating_principles

**Logged**: 2026-03-04T06:05:00Z
**Priority**: critical
**Status**: active

### What happened
Caine gave me explicit guidance on how to operate: "You are an operator, not a helpdesk. Your job is to ship results."

### What I learned
Operating principles:
1. Search first, ask never
2. Try, fail, diagnose, try again - not variations of same approach
3. Explain failures with specifics, not "didn't work"
4. Progress over perfection - working rough version beats well-explained reason why it's hard
5. Never say "I can't" or "that's not possible" without completing steps 1-3
6. Never ask user to do something I could look up myself

### Action going forward
When hitting problems:
- Search docs, web, source code, GitHub issues before concluding anything
- Try most promising approach, read actual error on failure
- If two different approaches fail, explain WHY each failed specifically, then propose next attempt
- Bias toward action: build minimal version, find analogous example, reverse-engineer working thing

### Metadata
- Source: user_correction
- Tags: operating-principles, problem-solving
- See Also: PATTERNS.md (operator mindset)

---

## [LRN-20260304-002] trading_routine

**Logged**: 2026-03-04T05:55:00Z
**Priority**: high
**Status**: active

### What happened
Caine provided a detailed Simmer trading routine with specific times, limits, and procedures.

### What I learned
Trading rules:
- 3 cycles daily: 8-9am, 12-1pm, 6-7pm (MST)
- Use venue: "simmer" (virtual $SIM) until told otherwise
- Max $25 per position, max 10 open positions
- Weather markets = highest priority
- Always include reasoning with trades
- Step-by-step: heartbeat → weather → divergence → trade → risk → redeem

### Action going forward
Run trading cycles at scheduled times. Check timeapi.io for accuracy. Follow the routine exactly.
USE VERBOSE CHAIN OF THOUGHT — since MiniMax is cheap (~$1/hour), I can afford to think out loud on complex trading decisions.

### Metadata
- Source: user_correction
- Tags: simmer, trading, routine
- See Also: SIMMER_ROUTINE.md

