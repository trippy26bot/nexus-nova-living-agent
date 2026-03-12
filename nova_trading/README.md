# Nova Trading System

Prediction market trading with guard rails.

## Quick Start

```bash
# Dry run (default)
python nova_trader.py

# Go live (after testing)
python nova_trader.py --live
```

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│  Polymarket Signal  │     │   Simmer Executor   │
│   (read only)       │     │   (requires keys)   │
│                     │     │                     │
│ Gamma API           │     │ CLOB API            │
│ No auth needed      │     │ Needs private key   │
└─────────────────────┘     └─────────────────────┘
         │                           │
         └───────────┬───────────────┘
                     ▼
          ┌─────────────────────┐
          │   Pre-Trade Guard   │
          │   (guards.py)      │
          │                    │
          │ - End date check   │
          │ - Accepting orders │
          │ - Staleness check  │
          └─────────────────────┘
```

## Files

| File | Purpose |
|------|---------|
| `nova_trader.py` | Main entry point, scan → execute loop |
| `guards.py` | Pre-trade validation (blocks bad markets) |
| `executor.py` | Order execution with guard enforcement |
| `strategy.py` | Parameter tuning, persistence |

## Guard Checks

Every trade passes through:

1. **End date** - Event must be in the future
2. **Accepting orders** - Market must be open
3. **Active** - Not archived/disabled
4. **Staleness** - Data fresh (<60s)
5. **Signal score** - Meets threshold

## Strategy

- Refines every 25 trades
- Adjusts bet size based on win rate
- Persists to `~/.nova/trading_strategy.json`

## Keys

Set up in `~/.nova/keys.json`:

```json
{
  "simmer": {
    "api_key": "...",
    "private_key": "0x...",
    "funder_address": "0x..."
  }
}
```
