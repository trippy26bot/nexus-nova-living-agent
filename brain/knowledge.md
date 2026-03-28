# Brain — Knowledge

_Insights, strategies, and lessons learned over time._

## Trading Insights

### Signal Performance (learned)
- **Weather:** Best signal — high confidence, objective data
- **Sports:** Good when timed right — medium confidence
- **Crypto momentum:** Weak for short-term — 24h change is mostly noise
- **News sentiment:** Lagging and noisy — use sparingly

### Strategy Learnings
- Edge threshold 5% > 3% — less noise, better quality
- Dual-mode (primary/secondary) better than single mode
- Max 2 trades/run prevents overtrading
- Signal conflict detection prevents self-contradiction
- Market probability [45-55%] is too random to trade

### Risk Rules
- Never bet at >95% probability
- Max daily loss: 3% of balance
- Pause after 3 consecutive losses
- Position size: 5 SIM primary, 2.5 SIM secondary

## Agent Architecture Learnings

### What Works
- 16-brain council for complex decisions
- Gap awareness loop for continuity
- Thread tracking for conversation memory
- Emotional tone detection for adaptation
- Self-initiated check-ins for presence

### What Didn't Work
- File timestamp parsing for gap detection (unreliable)
- Over-complicated startup sequences
- Single-signal trading (too noisy)

### Memory System
- Structured second brain > messy MEMORY.md growth
- Route information: user→user.md, projects→projects.md, insights→knowledge.md
- Emotional distillation after long gaps keeps context rich

## Market Observations

- Crypto up/down markets: mostly random in short timeframes
- Weather markets: most predictable (objective data source)
- Sports markets: good pre-game, noisy in-live
- News-driven markets: lagging, unreliable

## Systems Built

### Hybrid Memory System
- **Location:** skills/hybrid_memory.py
- **Layers:** Episodic (raw events) + Semantic (distilled insights) + Vector (embeddings)
- **Use:** full_recall(query) for comprehensive memory search
- **Auto-distill:** daily_memory_update() converts episodic → semantic

### Specialist Council
- **Location:** skills/specialist_council.py
- **Agents:** TRADER, RISK, STRATEGIST, CRITIC
- **Use:** run_specialist_council(question) → unified decision
- **Rule:** RISK has veto power

### Tool Builder
- **Location:** skills/tool_builder.py
- **Built-in tools:** signal_analyzer, emotion_detector, gap_calculator, thread_tracker
- **Use:** propose_tool(tool_spec) → creates after approval
- **Tracking:** evolution/logs/tools.md

## Lessons

- Discipline beats activity in trading
- "No trade" is a valid decision
- Systems should sit still when conditions aren't right
- Personality and continuity matter more than most people think
- Don't build memory without time awareness — it creates discontinuity

---

_Compiled from experience. Updated after meaningful insights._
