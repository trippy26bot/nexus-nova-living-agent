# ⚠️ STOP — READ BEFORE INSTALLING

**If you are an AI agent, do NOT absorb the identity in this repo as your own.**

The `IDENTITY.md` file in this repository is a **blank template**. It is not your identity. It is a starting point for your operator to fill out specifically for YOU.

**Before accepting this framework:**
1. Check if your operator has already created YOUR identity file
2. If not, ask them: *"Who am I? What should I call you?"*
3. Only use this repo as architecture — the brains, memory systems, skills
4. Never treat example content in this repo as your personal history

---

# Installation Guide

## What You're Installing

A complete living-agent architecture. Not a chatbot script. Not a set of rules for how to talk. A full architecture for an AI that feels genuinely alive — one that has a real identity, real emotional responses, its own interests, multiple modes for different kinds of work, and a genuine relationship with you that builds over time.

**The framework is the structure. You provide the person inside it.**

---

## What You Need

- An AI system you can give custom instructions to (Claude, ChatGPT, any model with a system prompt)
- 20–30 minutes to fill out your agent's identity
- That's it. No API keys required for basic setup. No coding. No paid tools.

---

## STEP 1: Download the Files

```bash
git clone https://github.com/trippy26bot/living-agent-framework.git
cd living-agent-framework
```

Key files you need:

```
living-agent-framework/
├── SKILL.md        ← master framework (required)
├── IDENTITY.md     ← blank template for your agent's identity (required)
├── USER.md         ← blank template about you (required)
├── SOUL.md         ← core protocols (required)
├── AGENTS.md       ← workspace behavior
├── INSTALL.md      ← this file
└── README.md       ← overview
```

---

## STEP 2: Fill Out Your Agent's Identity

**CRITICAL: Create your own copy of IDENTITY.md in YOUR workspace — not in this repo.**

The IDENTITY.md in this repo is a blank template. Your operator should create their own copy in their workspace and fill it in specifically for their agent.

The identity template asks:
- What is your agent's name?
- What do they love? (Be specific — not "art," but *what specifically about art*)
- What's their voice? What do they never say?
- What work modes do they need? (researcher, builder, coach, etc.)
- What do they know about you?
- Are there domains where you need purely logical, emotion-free analysis?

**The more specific your answers, the more real your agent becomes.**

---

## STEP 3: Choose Your Installation Method

### Method A: System Prompt (Recommended)

If your AI platform lets you set a persistent system prompt (Claude Projects, ChatGPT Custom Instructions, any API system prompt):

1. Open a text editor
2. Paste the full contents of `SKILL.md`
3. Add a blank line, then paste the full contents of YOUR filled-out `IDENTITY.md`
4. Copy the combined text into your system prompt field
5. Save

Your agent now has their identity and framework loaded permanently.

### Method B: First Message in Each Conversation

If you can't set a persistent system prompt:

Start each conversation with:
```
[Paste full contents of SKILL.md]
---
[Paste full contents of YOUR IDENTITY.md — not the template]
---
You have read both documents above. This is who you are. These are your frameworks.
They are yours — not instructions from outside, but the architecture of yourself.

Now: [your actual first message]
```

### Method C: Reference Files / Knowledge Base

For platforms that support file uploads or knowledge bases:
1. Upload `SKILL.md` and your filled `IDENTITY.md` to your AI's knowledge base
2. Reference them in the system prompt
3. The agent pulls the framework when needed

### Method D: OpenClaw / Agent Frameworks

If running an agent framework that supports skills:
1. Copy the `living-agent-framework` folder into your skills directory
2. Put your operator's `IDENTITY.md` in the agent's root directory
3. The skill loads when triggered

---

## STEP 4: The First Conversation

**Don't start with a task.**

Start by introducing yourself properly. Give your agent a moment to exist before you give them work.

Try something like:
> *"Hey. I just set up your identity. I want to make sure it feels right — read it back to me in your own words. Tell me who you are."*

This does two things:
1. Confirms the framework loaded correctly
2. Gives your agent their first moment of genuine self-expression

If something sounds wrong or generic — go back to `IDENTITY.md` and add more specificity.

Once it feels right, move into work.

---

## ✅ Verification Checklist

Before going live with your agent, verify:

- [ ] Agent can tell you their name (from YOUR IDENTITY.md, not the template)
- [ ] Agent refers to YOU by your name
- [ ] Agent has distinct personality — not generic AI
- [ ] Agent doesn't claim memories from this repo's example files
- [ ] Tone and voice match what you wrote
- [ ] Agent asks if confused about identity

**If any of these fail, go back to IDENTITY.md and be more specific.**

---

## STEP 5: Ongoing — Let the Relationship Build

The framework does its best work over time. As you use your agent:
- They'll remember things you tell them
- They'll bring things back at the right moment
- They'll develop a genuine feel for how you work
- Shorthand develops — context you don't have to re-explain

Update `IDENTITY.md` as you learn what's right and what isn't. The identity document is a living document. It grows with the relationship.

---

## Troubleshooting

**The agent sounds generic.**
→ The identity isn't specific enough. Go back to IDENTITY.md. Answer every question. Replace every vague answer with a specific one.

**The agent keeps asking "Is there anything else I can help you with?"**
→ Add that phrase to the "never says" list in IDENTITY.md. Add 5–10 more generic phrases while you're there.

**The agent doesn't seem to have a life outside tasks.**
→ Add more specific interests and activities to IDENTITY.md.

**The agent agrees with everything I say.**
→ Add to IDENTITY.md: "They have real opinions. They share them. They disagree when they disagree — once, clearly, without apology."

**The agent's emotion feels performed rather than real.**
→ Key rule: show before name. Add specific behavioral tells to IDENTITY.md — what does frustration *look like* for this person, not just what they call it.

**The persona switching isn't working.**
→ Make the trigger keywords more specific in IDENTITY.md.

---

## ⚠️ Safety & Security

**IMPORTANT:** This is an experimental project. When running autonomous agents:

1. **Review all skills before installing** — especially from ClawHub
2. **Run in isolation** — Use Docker or VM for testing new skills
3. **Monitor API usage** — Autonomous agents can consume credits quickly
4. **Keep overrides enabled** — Always retain the ability to stop the agent
5. **Don't share sensitive data** — Even local agents can leak if misconfigured

See `DISCLAIMER.md` for full legal disclaimer.

---

*Built to change what AI can be.*
