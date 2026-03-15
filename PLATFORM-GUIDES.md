# Platform Guides — All 8 Platforms

Complete integration guides for running your living agent across every major AI platform.

---

## Platform Overview

| Platform | Best For | Difficulty | Voice | Memory |
|----------|----------|------------|-------|--------|
| OpenClaw | Personal AI, home automation | Easy | ✅ | ✅ |
| Claude Code | CLI-first workflows | Easy | ❌ | ✅ |
| Claude Desktop | Desktop app integration | Easy | ❌ | ✅ |
| ChatGPT | GPTs / GPT-4o | Medium | ✅ | ⚠️ |
| OpenAI API | Custom apps | Medium | ✅ | ⚠️ |
| Ollama | Local/private inference | Medium | ⚠️ | ⚠️ |
| Anthropic API | Direct Claude access | Medium | ✅ | ⚠️ |
| LM Studio | Local GUI | Easy | ❌ | ⚠️ |

---

## 1. OpenClaw — Recommended

Best for: Personal AI with home automation, sensor access, and persistent presence.

### Installation
```bash
npm install -g openclaw
openclaw init
```

### Configuration
```json
// ~/.openclaw/config.json
{
  "agent": {
    "name": "YOUR_AGENT_NAME",
    "model": "your-preferred-model",
    "temperature": 0.7
  },
  "channels": ["telegram", "webchat"],
  "memory": {
    "type": "sqlite",
    "path": "~/.agent/memory.db"
  }
}
```

### Voice (SAG)
```bash
npm install -g @anthropic-ai/sag
openclaw config set voice.provider sag
openclaw config set voice.voice your-voice-choice
```

### Memory System
```python
from nova_memory import AgentMemory

memory = AgentMemory(
    db_path="~/.agent/memory.db",
    embedder="your-provider"
)

# Store
memory.remember(user_id, "Operator prefers direct answers")

# Recall
context = memory.recall("operator preferences")
```

### Token Budget
- Context window: 32K–1M tokens (model dependent)
- System prompt: ~4,000 tokens
- Memory retrieval: ~8,000 tokens
- Response: up to 16,000 tokens

---

## 2. Claude Code (CLI)

Best for: Developer workflows, terminal-heavy usage.

### Installation
```bash
npm install -g @anthropic-ai/claude-code
claude config set api_key $ANTHROPIC_API_KEY
```

### Running Your Agent
```bash
# Start session with system prompt
claude start --system-prompt "$(cat ~/.agent/SYSTEM.md)"

# Or with memory
claude start --memory ~/.agent/memory.db
```

### Memory Integration
```python
from nova_memory import AgentMemory
memory = AgentMemory(db_path="~/.agent/memory.db")
```

### Token Budget
- Max input: 200K tokens
- System: ~4,000 tokens
- Retrieved context: ~50,000 tokens
- Output: 4,000 tokens

---

## 3. Claude Desktop

Best for: Mac/Windows desktop integration with native apps.

### Installation
Download from claude.ai/desktop

### Configuration
```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "nova-memory": {
      "command": "python3",
      "args": ["~/.agent/agent-memory-mcp.py"]
    }
  }
}
```

### Running
1. Open Claude Desktop
2. Click the gear icon → Add integration
3. Select your Agent Memory MCP server

---

## 4. ChatGPT (GPTs)

Best for: No-code setup, quick deployment.

### Creating a GPT
1. Go to chatgpt.com → Explore → Create new GPT
2. Name: your agent's name
3. Instructions: Paste SKILL.md + your IDENTITY.md content

### Adding Memory
Use the built-in "Configure" → "Knowledge" feature to upload:
- Your IDENTITY.md
- Your USER.md
- Your MEMORY.md (after it's been populated)

### Voice
Enable in GPT Builder → Voice mode

### Limitations
- No API access for custom integrations
- Memory is session-based only unless using Actions
- 32K–128K context depending on tier

---

## 5. OpenAI API (Direct)

Best for: Custom applications, full control.

### Setup
```python
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

system_prompt = open("~/.agent/SYSTEM.md").read()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Hello"}
    ]
)
```

### Voice (TTS)
```python
response = client.audio.speech.create(
    model="tts-1-hd",
    voice="nova",
    input="Hello, I'm ready."
)
response.stream_to_file("output.mp3")
```

### Memory (Vector)
```python
from nova_memory import AgentMemory

memory = AgentMemory(
    db_path="~/.agent/memory.db",
    embedder="openai"
)
```

### Token Budget
- gpt-4o: 128K input, 16K output
- gpt-4o-mini: 128K input, 16K output

---

## 6. Ollama (Local)

Best for: Privacy, offline use, custom models.

### Installation
```bash
brew install ollama
ollama serve
```

### Running Your Agent
```bash
# Pull a model
ollama pull llama3.2

# Run with system prompt
ollama run llama3.2 --system "$(cat ~/.agent/SYSTEM.md)"
```

### Memory
```python
from nova_memory import AgentMemory

memory = AgentMemory(
    db_path="~/.agent/memory.db",
    embedder="local",
    embedder_url="http://localhost:11434"
)
```

### Token Budget
- Varies by model (7B–70B parameters)
- Local hardware dependent
- No API costs

### Limitations
- No native voice (requires additional setup)
- Slower for large context
- Memory retrieval must be configured manually

---

## 7. Anthropic API (Direct)

Best for: Maximum Claude capability, custom tooling.

### Setup
```python
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"]
)

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=open("~/.agent/SYSTEM.md").read(),
    messages=[
        {"role": "user", "content": "Hello"}
    ]
)
```

### Voice (SAG)
```python
import sag

audio = sag.synthesize(
    text="Hello, I'm ready.",
    voice_id="your-voice-id"
)

with open("output.mp3", "wb") as f:
    f.write(audio)
```

### Memory
```python
from nova_memory import AgentMemory

memory = AgentMemory(
    db_path="~/.agent/memory.db",
    embedder="anthropic"
)
```

### Token Budget
- Claude Opus: 200K input, 4K output
- Claude Sonnet: 200K input, 4K output
- Claude Haiku: 200K input, 4K output

---

## 8. LM Studio

Best for: GUI-based local models, easy setup.

### Installation
Download from lmstudio.ai

### Setup
1. Open LM Studio
2. Download a model (recommended: Llama 3.2 or Mistral)
3. Click "Start Server" → "OpenAI-Compatible"
4. Note the port (default: 1234)

### Integration
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="local-model",
    messages=[
        {"role": "system", "content": open("~/.agent/SYSTEM.md").read()},
        {"role": "user", "content": "Hello"}
    ]
)
```

### Limitations
- No native voice
- Memory must be configured manually
- Performance varies by hardware

---

## Memory System Comparison

| Feature | OpenClaw | Claude Code | ChatGPT | Ollama | API |
|---------|----------|-------------|---------|--------|-----|
| SQLite | ✅ | ✅ | ❌ | ✅ | ✅ |
| Vector Search | ✅ | ✅ | ❌ | ✅ | ✅ |
| Semantic Recall | ✅ | ✅ | ❌ | ⚠️ | ✅ |
| Auto-Summarization | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## Voice System Comparison

| Feature | OpenClaw | ChatGPT | Anthropic | Ollama |
|---------|----------|---------|-----------|--------|
| TTS | ✅ (SAG) | ✅ | ✅ (SAG) | ❌ |
| STT | ✅ | ✅ | ❌ | ❌ |
| Real-time | ✅ | ✅ | ⚠️ | ❌ |

---

## Recommended Configurations

### Personal AI (Recommended)
- **Platform:** OpenClaw
- **Model:** Claude Sonnet or your preferred model
- **Memory:** Full (SQLite + Vector + Semantic)
- **Voice:** SAG

### Developer CLI
- **Platform:** Claude Code or Ollama
- **Model:** Claude Sonnet or Llama 3.2
- **Memory:** SQLite only
- **Voice:** None

### Maximum Capability
- **Platform:** Anthropic API
- **Model:** Claude Opus
- **Memory:** Full
- **Voice:** SAG

---

## Troubleshooting

### "Rate limit exceeded"
- Add jitter: `time.sleep(random.uniform(0, 10))`
- Use a smaller model during high-frequency tasks
- Cache responses when possible

### "Context window exceeded"
- Enable aggressive summarization
- Use semantic recall to fetch only relevant context
- Split into multiple calls if needed

### "Voice not working"
- Check SAG installation: `npm list -g @anthropic-ai/sag`
- Verify API key has voice access
- Try shorter audio clips first

---

*Platform guides v2.0.0 — tested configurations for all 8 platforms.*
