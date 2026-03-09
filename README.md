# NOVA - Cognitive AI Agent

A modular cognitive AI agent architecture with multi-brain reasoning, emotional engine, self-reflection, and autonomous learning capabilities.

## 🧠 Architecture

- **16 Reasoning Brains** - Specialized cognitive modules for different thinking tasks
- **CriticBrain** - Self-critique and quality control
- **Cognitive Bus** - Event-driven brain communication
- **Priority Scheduler** - Task prioritization
- **Fast Response Layer** - Instant replies for simple queries
- **Emotional Engine** - Tone and emotional modulation
- **Governor** - Identity and safety protection
- **Attention Router** - Intelligent brain activation
- **Self-Reflection** - Quality assurance
- **Thought Stream** - Internal reasoning
- **Metrics + Learning** - Self-improvement system

## 📦 What's Included

```
nova/
├── brains/           # 16 cognitive brains + CriticBrain
├── core/              # Governor, Attention Router, Self-Reflection
├── cognitive_bus.py   # Event-driven communication
├── emotional_engine.py # Emotional modulation
├── priority_scheduler.py # Task scheduling
├── fast_response.py   # Quick response routing
├── output_filter.py   # Response cleaning
├── response_synthesizer.py # Response formatting
├── testing/           # Security, bug finder, validation
└── skills/            # Public skills (non-trading)
```

## 🧪 Testing

```bash
# Run full test suite
python nova/testing/test_harness.py nova

# Security scan
python nova/testing/security_scanner.py nova
```

## 🎯 Public Skills

Available skills for public use:
- nova-autonomy
- nova-memory
- nova-life
- nova-humanizer
- qmd (knowledge search)
- humanizer

## ⚠️ Private

The following are kept private (not committed):
- Trading/crypto skills (Polymarket, Solana trading)
- Personal configurations
- API keys

## 📝 License

MIT

---

*Nova is a cognitive AI agent designed to assist with reasoning, learning, and problem-solving while maintaining safety and personality consistency.*
