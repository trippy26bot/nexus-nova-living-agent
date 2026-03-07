# Security Hardening v2

## Threat Model Focus

- Malicious third-party skills
- Prompt-instruction injection in skill docs
- Dynamic module code execution
- Secrets exfiltration
- Unauthenticated API abuse
- Unsafe auto-update chain

## Controls

### 1. Pre-Install Scanning

- Run `scanner/skill_scanner.py` before skill install.
- Enforce install gating via `scanner/secure_install.sh` (non-zero exit on policy fail).
- Block critical patterns in manifests/scripts.
- Flag high/medium risks for manual review.
- Include AST and entropy checks for obfuscation/evasion patterns.

### 2. Runtime Sandbox

- Enforce read-only rootfs where possible.
- Use tmpfs for transient writes.
- Disable network by default.
- Block secret env vars from skill runtime.
- Cap CPU/memory/pids/process count.
- Deny `/proc`, `/sys`, and `/dev` where possible.

### 3. API Hardening

- Bind localhost by default.
- Require token auth for non-health endpoints.
- Rate limit per client bucket.
- Return JSON errors with explicit status.

### 4. Dynamic Skill Loading

- Disable Python skill execution by default.
- Require trust gate env var + scanner pass for enablement.
- Prevent implicit loading of unknown/unscanned modules.

### 5. Encryption

- Use random per-vault salt.
- Store salt/iteration metadata in vault config.
- Remove insecure fallback cryptography path.

### 7. Runtime Monitoring

- Run `sandbox/audit_watcher.py` or equivalent alert pipeline.
- Alert on shell spawn, sensitive file access, and request bursts.

### 6. Update Safety

- No hard reset auto-overwrite.
- Require fast-forward pull and clean worktree.
- Prefer signed releases or pinned commits.

## Operational Practices

- Keep audit logs for scanner results and runtime policy violations.
- Run in a dedicated user/container when possible.
- Treat skill installation as untrusted code handling.
