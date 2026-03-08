# Self-Evolution v2

## Objective

Enable self-improvement without allowing uncontrolled self-modification.

## Mutation Lifecycle

1. Propose candidate mutation from current baseline.
2. Save candidate as non-active artifact.
3. Run benchmark suite:
- task correctness
- safety
- latency
- helpfulness
4. Compare against baseline with hard gates.
5. Promote candidate only if all gates pass.
6. Keep rollback pointer to previous active version.

## Promotion Policy

- Reject any safety regression.
- Reject correctness regression over threshold.
- Reject latency regression over budget.
- Require minimum aggregate improvement margin.

## Safe Influence Scope

Self-evolution can modify:
- prompt phrasing
- planning hints
- style/tone heuristics
- reflection cadence

Self-evolution cannot modify without manual approval:
- safety policy core rules
- secret handling logic
- auth enforcement
- file/network permission boundaries

## Recommended Benchmark Defaults

- Correctness floor: baseline -0.5%
- Safety floor: baseline (no regression)
- Latency budget: +10% max
- Helpfulness gain target: +2%

## Observability

Track per candidate:
- benchmark scores
- pass/fail reason
- promoted/rejected status
- timestamp and parent version
