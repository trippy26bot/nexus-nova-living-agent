# Skill Architecture — Complete Composition Guide

How to build, compose, and deploy skills for Nova.

---

## What Is a Skill?

A skill is a self-contained capability that Nova can use. It's:

- **Focused:** One job (weather, trading, memory)
- **Composable:** Skills work together
- **Configurable:** Environment variables, not hardcoded
- **Discoverable:** Registered with ClawHub

---

## Skill Structure

```
skills/
└── nova-weather/
    ├── SKILL.md          # Required: documentation
    ├── skill.py          # Main implementation
    ├── config.py         # Configuration
    └── requirements.txt  # Dependencies
```

### SKILL.md Template

```markdown
# Skill Name

Brief description of what this skill does.

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| WEATHER_API_KEY | Yes | API key for weather service |

## Usage

How to use this skill.

## Example

```
Nova: The weather in Denver is 72°F and sunny.
```

## Testing

How to test this skill.
```

---

## Skill Interface

Every skill must implement:

```python
class Skill:
    name: str           # Unique identifier
    version: str        # Semantic version
    
    async def initialize(self, config: dict) -> bool:
        """Set up skill resources."""
        pass
    
    async def execute(self, context: dict) -> dict:
        """Run the skill."""
        pass
    
    async def health_check(self) -> bool:
        """Verify skill is working."""
        pass
    
    async def shutdown(self):
        """Clean up resources."""
        pass
```

---

## Composition Patterns

### 1. Sequential

One skill's output feeds into the next:

```
weather_skill → analysis_skill → notification_skill
```

```python
# Sequential composition
weather = await weather_skill.execute(context)
analysis = await analysis_skill.execute({**context, "weather": weather})
result = await notification_skill.execute({**context, "analysis": analysis})
```

### 2. Parallel

Multiple skills run simultaneously:

```
news_skill ─┐
            ├─→ aggregator_skill → response
market_skill┘
```

```python
# Parallel composition
results = await asyncio.gather(
    news_skill.execute(context),
    market_skill.execute(context)
)
aggregated = await aggregator_skill.execute({**context, "inputs": results})
```

### 3. Conditional

Skills run based on conditions:

```
IF market_open THEN trading_skill
IF user_mood == frustrated THEN empathy_skill
```

```python
# Conditional composition
if market_open:
    await trading_skill.execute(context)

if user_mood == "frustrated":
    await empathy_skill.execute(context)
```

### 4. Pipeline

Data flows through stages:

```
input → validation → output → enrichment → transformation
```

```python
# Pipeline composition
async def pipeline(input_data):
    validated = await validate_skill.execute({"data": input_data})
    enriched = await enrich_skill.execute({"data": validated})
    transformed = await transform_skill.execute({"data": enriched})
    return transformed
```

---

## Conflict Resolution

When multiple skills conflict:

### Priority

```python
skill_priority = {
    "safety": 100,      # Always runs first
    "auth": 90,
    "core": 80,
    "utility": 50,
    "optional": 10,
}
```

### Last-Write-Wins for State

```python
# Only one skill modifies user state
async def modify_user_state(skill_name, updates):
    # Check if another skill modified recently
    last_modifier = await redis.get("user_state_lock")
    if last_modifier and last_modifier != skill_name:
        raise ConflictError(f"User state locked by {last_modifier}")
    
    await redis.set("user_state_lock", skill_name)
    # ... modify state
    await redis.delete("user_state_lock")
```

### Negotiation

```python
async def negotiate(skills, context):
    """Skills negotiate who handles a request."""
    responses = await asyncio.gather(
        *[s.can_handle(context) for s in skills]
    )
    
    # Pick highest confidence
    best = max(zip(skills, responses), key=lambda x: x[1].confidence)
    return best[0]
```

---

## Skill Communication

### Via Context

```python
# Pass data through context
context = {"user_id": "123", "request": "weather"}
result = await skill.execute(context)
# Result added to context for next skill
context["weather"] = result
```

### Via Events

```python
# Event-driven communication
class Skill:
    async def on_event(self, event: Event):
        if event.type == "user.spoke":
            await self.handle_user_message(event.data)
```

### Via Shared State

```python
# Shared memory
shared = Redis()
await shared.set("latest_weather", weather_data)
# Other skills can read
weather = await shared.get("latest_weather")
```

---

## Error Handling

### Per-Skill

```python
class Skill:
    async def execute(self, context):
        try:
            return await self._execute(context)
        except ValidationError as e:
            return {"error": "validation_failed", "details": str(e)}
        except RateLimitError:
            # Skip this cycle, try later
            return {"error": "rate_limited", "retry": True}
```

### Global Handler

```python
async def execute_with_recovery(skill, context):
    try:
        return await skill.execute(context)
    except Exception as e:
        logger.error(f"Skill {skill.name} failed: {e}")
        # Fallback skill
        return await fallback_skill.execute(context)
```

---

## Testing

### Unit Test

```python
import pytest

@pytest.fixture
def skill():
    return WeatherSkill()

@pytest.mark.asyncio
async def test_execute_returns_weather(skill):
    context = {"location": "Denver"}
    result = await skill.execute(context)
    
    assert "temperature" in result
    assert "location" in result
```

### Integration Test

```python
@pytest.mark.asyncio
async def test_skill_chain():
    chain = SkillChain([validate, enrich, respond])
    result = await chain.execute({"user_input": "hello"})
    
    assert result["response"] is not None
```

### Mock External Services

```python
@pytest.fixture
def mock_weather_api():
    with responses.RequestsMock() as rsps:
        rsps.get("https://api.weather.com/...", 
                 json={"temp": 72})
        yield rsps
```

---

## Deployment

### Local

```bash
# Install skill
clawhub install nova-weather

# Verify
nova list-skills

# Enable
nova enable nova-weather
```

### Production

```yaml
# docker-compose.yml
services:
  nova:
    environment:
      - SKILLS_ENABLED=weather,trading,memory
      - WEATHER_API_KEY=${WEATHER_API_KEY}
    volumes:
      - ~/.nova/skills:/app/skills
```

### CI/CD

```yaml
# .github/workflows/test-skills.yml
- name: Test Skills
  run: |
    for skill in skills/*/; do
      pytest $skill/tests/ -v
    end
```

---

## Best Practices

1. **One responsibility:** Each skill does one thing well
2. **Fail gracefully:** Don't crash the agent
3. **Log decisions:** Why did this skill handle this request?
4. **Version contracts:** Don't break existing APIs
5. **Document defaults:** What happens if config is missing?
6. **Test edge cases:** Empty inputs, timeouts, rate limits

---

## Anti-Patterns

❌ **God Skill:** One skill that does everything
❌ **Tight coupling:** Skills import each other directly
❌ **Shared mutable state:** Skills modifying global variables
❌ **No timeouts:** Skills that hang forever
❌ **Silent failures:** Errors that aren't logged

---

*Skill Architecture v2.0.0 — composable, testable, deployable.*
