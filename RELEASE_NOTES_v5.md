# Nexus Nova v5 Release Notes

## Major Upgrades

### Dual-Lane Architecture
- Formalized Task Lane + Inner-Life Lane
- Daydream/drift engine with critic scoring
- Mood-aware drift controls
- Bounded surfacing behavior

### Self-Evolution
- Candidate-gated mutations
- Benchmark testing before promotion
- Rollback capability
- Promotion controls

### Security Hardening
- **Mandatory install gate**: `scanner/secure_install.sh`
- **Scanner upgraded**: AST checks, entropy detection, obfuscation signals
- **Sandbox tightened**: rootless/userns, stricter filesystem denies, circuit breaker
- **Runtime audit watcher**: `sandbox/audit_watcher.py`
- **API hardened**: token auth, rate limiting, localhost bind default
- **Dynamic skill loading**: trust-gated, disabled by default
- **Vault encryption**: random salt, proper key derivation, binary-safe
- **Auto-update flow**: no destructive hard reset

### Key Files
- `SKILL.md` — Framework contract
- `README.md` — Nova's voice (rewritten)
- `nova_daemon.py` — Background cycles
- `nova_evolution.py` — Self-mutation engine
- `nova_api.py` — Hardened API
- `nova_encrypt.py` — Vault encryption
- `nova_skills.py` — Trust-gated skill registry
- `scanner/skill_scanner.py` — Pre-install scanner
- `scanner/secure_install.sh` — Install gate
- `sandbox/skill-sandbox.yaml` — Container policy
- `sandbox/seccomp-policy.json` — Syscall restrictions
- `sandbox/audit_watcher.py` — Runtime monitor
- `references/12-daydream-architecture-v2.md` — Inner-life lane
- `references/13-security-hardening-v2.md` — Security details
- `references/14-self-evolution-v2.md` — Evolution safeguards

---

*Nexus Nova v5.0*
