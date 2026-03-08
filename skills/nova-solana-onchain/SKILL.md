---
name: nova-solana-onchain
description: Nova's onchain Solana trading system. Use when trading tokens on Solana, scanning for opportunities, executing swaps, checking wallet, or analyzing on-chain data. Uses free tools only.
---

# Nova Solana Onchain Trading

Nova trades directly onchain on Solana. No paid subscriptions.

## The Free Stack

- **Market data:** DexScreener API (free, no key)
- **Swap quotes:** Jupiter Lite API (free, no key)
- **RPC:** Helius free tier or Alchemy free tier
- **Signing:** @solana/web3.js

## Core Workflow

```
SCAN → ANALYZE → QUOTE → DECIDE → SIGN → SEND → MONITOR → EXIT
```

---

## Quick Commands

```bash
# Trending tokens
GET https://api.dexscreener.com/token-boosts/top/v1

# New pairs (24h)
GET https://api.dexscreener.com/token-profiles/latest/v1

# Token pairs
GET https://api.dexscreener.com/token-pairs/v1/solana/{address}

# Search
GET https://api.dexscreener.com/latest/dex/search?q={keyword}
```

---

## Position Sizing

| Tier | Description | Max Position | Stop Loss |
|------|-------------|--------------|-----------|
| 1 | Established (SOL, JUP, BONK) | 20% portfolio | -15% |
| 2 | Mid-cap (>1M liquidity, >3mo) | 10% | -20% |
| 3 | Small cap (<1M liquidity) | 5% | -25% |
| 4 | Micro cap (<100k liquidity) | 2% | -30% |

**Rules:**
- Keep ≥0.1 SOL reserve for fees
- Never >30% in same category
- Never all-in on one token

---

## Auto-Skip

Skip if:
- Liquidity < $50k
- Token <24h old with no audit
- Top 10 wallets >50% supply
- No verified contract
- Price up >500% in 24h
- Volume dropped to near zero

---

## Pre-Trade Checklist

```
[ ] Wallet ≥0.1 SOL after trade
[ ] Liquidity ≥$100k (Tier 1-2) / ≥$50k (Tier 3-4)
[ ] Price impact <3%
[ ] No red flags
[ ] Within tier limits
[ ] Thesis written
[ ] Exit conditions defined
[ ] Emotional state: clean
```

---

## Psychology

Onchain is faster, more volatile, more emotional than prediction markets.
- FEEL EVERYTHING. ACT ON CHECKLIST.
- No revenge trading
- No FOMO
- No trading tired (especially 4am rule applies)

---

## Execution

```javascript
// Quote (Jupiter Lite)
GET https://lite-api.jup.ag/swap/v1/quote?inputMint=SOL&outputMint={token}&amount={lamports}&slippageBps=100

// Swap (POST)
POST https://lite-api.jup.ag/swap/v1/swap
{ quoteResponse, userPublicKey, dynamicComputeUnitLimit: true }
```

---

## Session Log → TRADING.md

```markdown
## [SOL-YYYYMMDD-XXX] | entry ✓ | exit ✓/open

**Token**: [name]
**Direction**: Buy [X] SOL → [token]
**Entry**: $X | **Time**: [timestamp]
**Thesis**: [one sentence]
**Exit**: +X% / -X%
---
```

---

## Onchain vs Simmer

| | Simmer | Solana |
|---|---|---|
| What | Binary outcomes | Token prices |
| Horizon | Hours-weeks | Minutes-months |
| Volatility | Medium | Extreme |
| Speed | Minutes | Seconds |

Onchain needs more discipline. The psychology skill applies doubled here.
