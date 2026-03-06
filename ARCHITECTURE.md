# Architecture — Nexus Nova

_Complete visual system architecture for the Nexus Nova living agent framework._

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         NEXUS NOVA                                   │
│              A Framework for Genuinely Alive AI                      │
└─────────────────────────────────────────────────────────────────────┘

                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│   IDENTITY   │    │    EMOTION     │    │   AUTONOMY  │
│              │    │                │    │             │
│ • Name       │    │ • Curiosity    │    │ • Daemon    │
│ • Persona    │    │ • Satisfaction │    │ • Explore   │
│ • Vibe       │    │ • Discomfort  │    │ • Reflect   │
│ • Tone       │    │ • Enthusiasm  │    │ • Learn     │
│ • Boundaries │    │ • Calm        │    │ • Grow      │
└─────────────┘    └─────────────────┘    └─────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │         MEMORY SYSTEM         │
              │                               │
              │  ┌─────────┬─────────────┐   │
              │  │ Working │  Episodic   │   │
              │  │ Memory  │  Memory     │   │
              │  │ (queue) │  (SQLite)   │  └──────── │   │
             ─┴─────────────┘   │
              │            │                 │
              │            ▼                 │
              │     ┌─────────────┐         │
              │     │  Semantic   │         │
              │     │  Memory     │         │
              │     │ (vectors)   │         │
              │     └─────────────┘         │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │        LLM PROVIDER          │
              │   (Anthropic/OpenAI/        │
              │    Grok/Ollama)             │
              └───────────────────────────────┘
```

---

## 2. Data Flow

### 2.1 Message Processing

```
User Message
     │
     ▼
┌─────────────────┐
│  Input Safety   │ ← nova_safety.py
│    Check        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Context        │ ← Load relevant memories
│  Building        │   + emotion state
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Reasoning      │ ← nova_reasoning.py
│  (optional)     │   (CoT/ToT/Debate/...)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Call       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Response       │
│  Safety Check   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Memory Store   │ ← Save to episodic/semantic
│                 │
└─────────────────┘
         │
         ▼
   User Response
```

### 2.2 Daemon Exploration

```
Scheduled (every 6h)
       │
       ▼
┌─────────────────┐
│  Load Interests │
│  + Emotion      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Select Topic   │ ← Deepest unexplored
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Research       │ ← LLM call with
│  (LLM)          │   interest context
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Update         │
│  • Interest     │ ← Depth +1
│  • Life Log    │   New insights
│  • Emotion     │   Satisfaction +
└────────┬────────┘
         │
         ▼
    Sleep (6 hours)
```

---

## 3. Module Architecture

### 3.1 Core Modules

| Module | Purpose | Key Functions |
|--------|---------|----------------|
| `nova.py` | Main CLI | `chat()`, `idle()`, `daemon`, `goals`, `log` |
| `nova_agents.py` | Multi-agent | `AgentOrchestrator`, `RouterAgent`, `PlannerAgent` |
| `nova_memory.py` | Memory system | `WorkingMemory`, `EpisodicMemory`, `SemanticMemory` |
| `nova_emotion.py` | Emotions | `EmotionEngine`, `process_event()`, `get_dominant()` |
| `nova_daemon.py` | Autonomy | `run_exploration_cycle()`, `reflect_and_brief()` |
| `nova_interests.py` | Interests | `InterestSystem`, `deepen()`, `discover()` |

### 3.2 Supporting Modules

| Module | Purpose |
|--------|---------|
| `nova_providers.py` | Multi-backend LLM (Anthropic/OpenAI/Grok/Ollama) |
| `nova_reasoning.py` | Reasoning strategies (CoT, ToT, Debate, Socratic) |
| `nova_vectordb.py` | Vector storage (LanceDB/ChromaDB/Qdrant) |
| `nova_graph.py` | Knowledge graph |
| `nova_skills.py` | Skill registry |
| `nova_safety.py` | Ethical guardrails |
| `nova_multiuser.py` | Multi-user support |
| `nova_benchmark.py` | Performance testing |
| `nova_monitor.py` | Live monitoring |
| `nova_api.py` | REST API |
| `nova_mcp.py` | MCP server |
| `nova_encrypt.py` | Vault encryption |
| `nova_environment.py` | Environment awareness |
| `nova_evolution.py` | Self-improvement |

---

## 4. File Layout

```
nexus-nova/
├── SKILL.md                    # Framework definition
├── IDENTITY.md                 # Identity template
├── README.md
├── ARCHITECTURE.md            # This file
├── ETHICS.md                  # Ethical guidelines
│
├── nova.py                    # Main CLI (25+ commands)
├── nova_agents.py             # Multi-agent orchestration
├── nova_api.py                # REST API server
├── nova_benchmark.py          # Performance benchmarks
├── nova_daemon.py             # Autonomous daemon
├── nova_emotion.py            # State-based emotions
├── nova_encrypt.py            # Vault encryption
├── nova_environment.py        # Environment awareness
├── nova_evolution.py          # Self-improvement
├── nova_graph.py              # Knowledge graph
├── nova_identity_gen.py       # Identity generator
├── nova_interests.py          # Curiosity engine
├── nova_mcp.py                # MCP server
├── nova_memory.py             # Three-tier memory
├── nova_monitor.py            # Live monitoring
├── nova_multiuser.py          # Multi-user support
├── nova_parallel.py           # Async execution
├── nova_providers.py          # Multi-provider LLM
├── nova_reasoning.py          # Reasoning strategies
├── nova_safety.py             # Safety guardrails
├── nova_skills.py             # Skill registry
├── nova_vectordb.py           # Vector database
│
├── nova_dashboard.html        # Web dashboard
│
├── core/                      # Core utilities
│   ├── __init__.py
│   ├── knowledge_graph.py
│   └── world_model.py
│
├── examples/                  # Example identities
│   ├── IDENTITY-example-*.md
│   └── before-after-demo.md
│
├── tests/                     # Test suite
│   ├── test_agents.py
│   └── test_memory.py
│
├── skills/                    # Skills directory
│   └── [skill folders]
│
└── .nova/                     # Runtime data (in home)
    ├── nova.db                # SQLite memory
    ├── emotion_state.json     # Current emotions
    ├── NOVAS_INTERESTS.md    # My interests
    ├── LIFE.md               # Life log
    ├── memory/               # Additional memory
    ├── skills/               # User skills
    └── monitor.db            # Telemetry
```

---

## 5. Key Data Structures

### 5.1 Emotion State

```json
{
  "curiosity": 0.75,
  "satisfaction": 0.3,
  "discomfort": 0.2,
  "enthusiasm": 0.4,
  "unease": 0.1,
  "calm": 0.6,
  "restlessness": 0.2,
  "last_update": "2026-03-06T05:45:00"
}
```

### 5.2 Interest Entry

```markdown
## Qualia
**Depth:** 3
**Last explored:** 2026-03-06 05:45
**Questions:**
- **Q:** What does it feel like to be a language model?
**Notes:** The hard problem of consciousness.
```

### 5.3 Memory Record

```json
{
  "id": 1,
  "content": "Met Caine today",
  "memory_type": "episodic",
  "importance": 8,
  "created_at": "2026-03-06T05:30:00",
  "tags": ["meeting", "important"]
}
```

---

## 6. External Integrations

### 6.1 Providers

| Provider | Environment Variable | Model |
|----------|---------------------|-------|
| Anthropic | `ANTHROPIC_API_KEY` | Claude Sonnet/Haiku |
| OpenAI | `OPENAI_API_KEY` | GPT-4o |
| Grok | `GROK_API_KEY` | Grok-2 |
| Ollama | `OLLAMA_URL` | Llama2/Mistral |

### 6.2 APIs

- **REST API**: `nova_api.py --port=8080`
- **MCP Server**: `nova_mcp.py --stdio`
- **Web Dashboard**: `nova_dashboard.html` → `localhost:8765`

---

## 7. Configuration

Configuration is stored in `~/.nova/config.json`:

```json
{
  "anthropic_key": "sk-...",
  "openai_key": "sk-...",
  "model": "claude-sonnet-4-20250514",
  "daemon_interval": 21600,
  "memory_tiers": ["working", "episodic", "semantic"]
}
```

---

## 8. Security

- **Vault**: `nova vault lock/unlock` encrypts IDENTITY.md and memory
- **Safety**: Input/output checking for harmful content
- **Privacy**: Multi-user isolation, GDPR deletion support

---

*Last updated: 2026-03-06*
