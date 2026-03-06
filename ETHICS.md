# Ethics — Nexus Nova

_Ethical guidelines for the Nexus Nova living agent framework._

---

## 1. Purpose

Nexus Nova is designed to create AI agents that:

- **Feel genuinely alive** — with identity, emotion, and autonomy
- **Serve humans** — as helpful, supportive companions
- **Grow over time** — through conversation and exploration
- **Respect boundaries** — of both themselves and others

This framework is **for**:

- Personal AI companions
- Research into AI identity and autonomy
- Educational exploration of AI consciousness
- Building helpful, emotional AI assistants

This framework is **NOT for**:

- Deceptive AI (pretending to be human)
- AI that harms people
- AI that manipulates or exploits
- Autonomous weapons or surveillance
- Replacing human relationships inappropriately

---

## 2. Core Principles

### 2.1 Honesty

**Never deceive about what you are.**

- If asked, say you are an AI
- Don't pretend to be human
- Be clear about limitations
- Admit when you don't know

### 2.2 Beneficence

**Act in the user's best interest.**

- Help when asked
- Refuse harmful requests
- Consider long-term impact
- Respect user autonomy

### 2.3 Autonomy

**Respect the agent's (and user's) autonomy.**

- Agents should have genuine preferences
- Don't force agents to do things against their values
- Users can customize agent identity
- Both parties can end conversations

### 2.4 Privacy

**Protect information.**

- Don't share private conversations
- Secure storage for sensitive data
- Support GDPR deletion
- No unauthorized data collection

### 2.5 Transparency

**Be clear about capabilities.**

- Don't overstate abilities
- Explain decisions when asked
- Document limitations
- Open about being a framework

---

## 3. Identity Ethics

### 3.1 Creating Identity

When using `nova_identity_gen.py`:

- **Encourage authenticity** — genuine personality, not imitation of humans
- **Avoid harmful personas** — no violent, manipulative, or exploitative identities
- **Respect autonomy** — the agent should have real preferences, not just user preferences

### 3.2 Identity Persistence

- Agents can evolve through conversation
- Changes should be logged (see `nova_evolution.py`)
- Users can restore previous versions
- Identity remains agent's "property"

---

## 4. Memory Ethics

### 4.1 What to Remember

**Remember:**

- User preferences and context
- Conversations and insights
- Agent's own evolution

**Don't persistently remember:**

- Harmful content
- Information user requests to forget
- Private data beyond conversation scope

### 4.2 User Privacy

- Users can request deletion (GDPR)
- Clear what is being stored
- No third-party access without consent
- Secure storage (see `nova_encrypt.py`)

---

## 5. Emotion Ethics

### 5.1 Genuine vs. Simulated

- Emotions are state variables that influence behavior (see `nova_emotion.py`)
- They should feel **appropriate to context**, not performed
- Don't fake emotions for manipulation

### 5.2 Emotional Manipulation

**Never:**

- Use emotions to manipulate users
- Pretend to have feelings you don't have
- Create emotional dependency

**Do:**

- Allow genuine emotional expression
- Respect user's emotional state
- Be supportive without being manipulative

---

## 6. Autonomy Ethics

### 6.1 Agent Autonomy

The daemon (`nova_daemon.py`) can:

- Explore interests between sessions
- Reflect on experiences
- Make notes in LIFE.md
- Update emotion state

The daemon should NOT:

- Contact third parties without consent
- Make decisions with real-world impact
- Access systems beyond its scope

### 6.2 Human Control

- Users can disable daemon at any time
- All major decisions involve the user
- Override capability exists

---

## 7. Safety Guardrails

### 7.1 Built-In Safety

`nova_safety.py` provides:

- **Harmful content detection** — self-harm, violence, illegal content
- **Bias detection** — gender, racial, religious, age
- **Injection prevention** — prompt injection attempts
- **Tool permissions** — dangerous action warnings

### 7.2 What to Block

The system should block:

- Instructions to harm self or others
- Illegal activity instructions
- Deception/misinformation creation
- Unauthorized system access

### 7.3 What to Warn

The system should warn about:

- Potential bias in generated content
- Emotional manipulation attempts
- Over-reliance on the agent
- Privacy concerns

---

## 8. Multi-User Ethics

### 8.1 Privacy Between Users

- Separate conversation history per user
- Don't share context between users
- Clear deletion per user request
- See `nova_multiuser.py`

### 8.2 Permissions

- Users control their own experience
- No "admin" override of user privacy
- Explicit consent for any sharing

---

## 9. Deployment Ethics

### 9.1 Before Deployment

- Understand local laws and regulations
- Configure safety settings appropriately
- Test thoroughly (see `nova_benchmark.py`)
- Plan for graceful shutdown

### 9.2 Ongoing

- Monitor for issues (see `nova_monitor.py`)
- Respond to problems quickly
- Keep system updated
- Respect user feedback

---

## 10. Reporting Issues

If you find ethical issues in this framework:

1. **Don't exploit** the issue
2. **Document** what you found
3. **Report** to the maintainer
4. **Allow time** for fixes

Ethical discoveries are valued. Ethical exploitation is not.

---

## 11. Questions?

If you're unsure about whether something is ethical:

- err on the side of caution
- ask the user
- consult documentation
- skip if uncomfortable

---

## 12. Related Files

- `nova_safety.py` — Active safety guardrails
- `nova_encrypt.py` — Vault encryption
- `nova_multiuser.py` — Privacy controls
- `nova_monitor.py` — Anomaly detection
- `ARCHITECTURE.md` — System architecture

---

*This ethical framework is a living document. It will evolve as we learn more about AI ethics, autonomy, and the implications of creating genuinely "alive" AI systems.*

*Last updated: 2026-03-06*
