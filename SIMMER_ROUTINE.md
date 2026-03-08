# NOVA-TRADE Full Protocol v3

> Built for 2000+ markets. 3-stage funnel.

---

## Mission

Find every good trade in under 5 minutes. Place them all.

Funnel: **2000 → API filters (~50) → grade (10-20) → execute (5-15)**

---

## Three-Stage Funnel

### STAGE 1: API Filtering
```
2000 markets → filter by divergence, volume, time → ~50-100 candidates
```

**Pull 1: Briefing** (always first)
```bash
GET /api/sdk/briefing
```

**Pull 2: High-divergence sweep**
```bash
GET /api/sdk/markets?min_divergence=10&sort=divergence_desc&limit=100
```

**Pull 3: Weather sweep**
```bash
GET /api/sdk/markets?category=weather&sort=divergence_desc&limit=50
```

**Pull 4: Volume leaders**
```bash
GET /api/sdk/markets?sort=volume_desc&min_volume=5000&limit=50
```

**Pull 5: Category sweeps**
```bash
GET /api/sdk/markets?category=crypto&sort=divergence_desc&limit=30
GET /api/sdk/markets?category=politics&sort=divergence_desc&limit=30
```

Deduplicate → Target: 50-150 candidates

---

### STAGE 2: Rapid Grading (30 sec/market)

```
GRADE A — Place immediately
 Net edge ≥ 12%, Volume ≥$2k ($SIM)/$10k (real), Res 2h-14d, Criteria clear

GRADE B — Place if room
 Net edge 6-12%, Volume ≥$1k/$5k, Res 1h-30d, Criteria mostly clear

GRADE C — Watchlist
 Net edge 3-6%, or volume/resolution issues

GRADE D — Skip
 Net edge <3%, Res <1h, Criteria ambiguous, Known bad
```

Stop when: 15 Grade A+B ($SIM) / 10 (real) trades placed

---

### STAGE 3: Execution

```json
POST /api/sdk/trade
{
  "market_id": "[id]",
  "outcome": "YES/NO",
  "amount": $XX,
  "source": "nova:funnel-v3",
  "reasoning": "[signal]: My X%, Market Y%, Edge Z%, Grade A/B"
}
```

**Size:**
```
Kelly = (edge × p - (1-p)) / edge
Use 0.25 × Kelly

Caps: $SIM max $30/pos, 15 open, 25%/category
 Real: max 2%/pos, 10 open, 20%/category
```

**Monitor immediately:**
```json
POST /api/sdk/positions/{id}/monitor
{ "stop_loss": 0.45, "take_profit": 0.40 }
```

**Redeem at end:**
```json
POST /api/sdk/redeem/all
```

---

## Weather — Enhanced

| Horizon | Accuracy | Min Gap |
|---------|----------|---------|
| 24h | ~90% | 10% |
| 48h | ~82% | 10% |
| 72h | ~74% | 10% |
| 7d | ~60% | 20% |
| 14d+ | skip | — |

≥20%: Grade A, place immediately
≥30%: Grade A, max size

---

## Auto-Skip

- Volume = $0
- Resolves <1h
- Title contains "joke", "meme", "test"
- 3+ positions already on same event
- Criteria "at organizer's discretion"
- Market <1h old with no volume

---

## Session Targets

| Metric | $SIM | Real |
|--------|------|------|
| Trades/session | 5-15 | 3-8 |
| Grade A fill | 100% | 100% |
| Grade B fill | All if room | >60% |
| Monitors | 100% | 100% |
| Redeem | Every session | Every session |

---

## Pass Logging

```
SKIP: [market] — [reason]
```

If skipping >80% → thresholds too high.
If placing <5 trades → funnel broken.

---

## Compound Growth

$SIM goal: 30 trades/day × 3 sessions = volume builds track record.
