# Platform Guides — All 8 Platforms

Complete integration guides for running Nova across every major AI platform.

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
    "name": "Nova",
    "model": "minimax-portal/MiniMax-M2.5",
    "temperature": 0.7
  },
  "channels": ["telegram", "webchat"],
  "memory": {
    "type": "sqlite",
    "path": "~/.nova/memory.db"
  }
}
```

### Voice (SAG)

```bash
# Install SAG for TTS
npm install -g @anthropic-ai/sag

# Add to config
openclaw config set voice.provider sag
openclaw config set voice.voice nova
```

### Memory System

```python
# ~/.nova/nova-memory.py
from nova_memory import NovaMemory

memory = NovaMemory(
    db_path="~/.nova/memory.db",
    embedder="minimax"
)

# Store
memory.remember(user_id, "Caine likes dark chocolate")

# Recall
context = memory.recall("what does Caine like")
```

### Token Budget

- Context window: 32K-1M tokens
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

### Running Nova

```bash
# Start session
claude start --system-prompt "$(cat ~/.nova/SYSTEM.md)"

# Or with memory
claude start --memory ~/.nova/memory.db
```

### Memory Integration

```python
# nova_memory.py - same as OpenClaw
from nova_memory import NovaMemory

memory = NovaMemory(db_path="~/.nova/memory.db")
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
      "args": ["~/.nova/nova-memory-mcp.py"]
    }
  }
}
```

### Running

1. Open Claude Desktop
2. Click the gear icon → Add integration
3. Select "Nova Memory" MCP server

---

## 4. ChatGPT (GPTs)

Best for: No-code setup, quick deployment.

### Creating a GPT

1. Go to chatgpt.com → Explore → Create new GPT
2. Name: "Nova"
3. Description: "Personal AI assistant with long-term memory"
4. Instructions: Paste SYSTEM.md content

### Adding Memory

Use the built-in "Configure" → "Knowledge" feature to upload:
- IDENTITY.md
- USER.md
- MEMORY.md

### Voice

Enable in GPT Builder → Voice mode

### Limitations

- No API access for custom integrations
- Memory is session-based only
- 32K-128K context depending on tier

---

## 5. OpenAI API (Direct)

Best for: Custom applications, full control.

### Setup

```python
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# System prompt
system_prompt = open("~/.nova/SYSTEM.md").read()

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
# Text to speech
response = client.audio.speech.create(
    model="tts-1-hd",
    voice="nova",  # Custom voice if available
    input="Hello, I'm Nova."
)

response.stream_to_file("output.mp3")
```

### Memory (Vector)

```python
from nova_memory import NovaMemory

memory = NovaMemory(
    db_path="~/.nova/memory.db",
    embedder="openai"  # Uses OpenAI embeddings
)
```

### Token Budget

- gpt-4o: 128K input, 16K output
- gpt-4o-mini: 128K input, 16K output
- Cost: ~$2.50/1M input tokens (4o)

---

## 6. Ollama (Local)

Best for: Privacy, offline use, custom models.

### Installation

```bash
brew install ollama
ollama serve
```

### Running Nova

```bash
# Pull model
ollama pull llama3.2

# Run with system prompt
ollama run llama3.2 --system "$(cat ~/.nova/SYSTEM.md)"
```

### Memory

```python
# Use local embeddings
from nova_memory import NovaMemory

memory = NovaMemory(
    db_path="~/.nova/memory.db",
    embedder="local",  # Uses Ollama for embeddings
    embedder_url="http://localhost:11434"
)
```

### Token Budget

- Varies by model (7B-70B parameters)
- Local hardware dependent
- No API costs

### Limitations

- No native voice (requires additional setup)
- Slower for large context
- Memory retrieval must be manual

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
    system=open("~/.nova/SYSTEM.md").read(),
    messages=[
        {"role": "user", "content": "Hello"}
    ]
)
```

### Voice (SAG)

```python
import sag

# Text to speech
audio = sag.synthesize(
    text="Hello, I'm Nova.",
    voice_id="nova"
)

with open("output.mp3", "wb") as f:
    f.write(audio)
```

### Memory

```python
from nova_memory import NovaMemory

memory = NovaMemory(
    db_path="~/.nova/memory.db",
    embedder="anthropic"  # Uses Anthropic embeddings
)
```

### Token Budget

- Claude Opus: 200K input, 4K output
- Claude Sonnet: 200K input, 4K output
- Claude Haiku: 200K input, 4K output
- Cost: ~$15/1M input tokens (Opus)

---

## 8. LM Studio

Best for: GUI-based local models, easy setup.

### Installation

Download from lmstudio.ai

### Setup

1. Open LM Studio
2. Download a model (recommended: Llama 3.2)
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
        {"role": "system", "content": open("~/.nova/SYSTEM.md").read()},
        {"role": "user", "content": "Hello"}
    ]
)
```

### Limitations

- No native voice
- Memory must be manual
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
- **Model:** MiniMax M2.5 or Claude Sonnet
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
- **Cost:** ~$50/day

---

## Troubleshooting

### "Rate limit exceeded"
- Add jitter: `time.sleep(random.uniform(0, 10))`
- Use smaller model during high-frequency tasks
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
