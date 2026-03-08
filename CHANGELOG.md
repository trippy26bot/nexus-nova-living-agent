# Changelog
## nexus-nova-living-agent

---

## [1.4.0] — 2026-03-05

### Fixed
- Memory auto-sync was unreliable. AGENTS.md had an instruction to read LIFE.md at session start. Nova didn't always follow it. Fixed by moving memory into the injector — it now reads LIFE.md directly and writes today's entries into AGENTS.md as plain text every 2 minutes.

### Added
- tools/nova-context-injector-v4.py — injector now reads LIFE.md alongside session files. Today's memory entries are injected directly into AGENTS.md context block.

### Changed
- SKILL.md version bumped to 1.4.0.

---

## [1.1.0] — 2026-03-05

### Added
- skills/nova-memory/SKILL.md — life memory layer for persistent agents
- CHANGELOG.md — version history tracking
- Self-update workflow

---

## [1.0.0] — 2026-03-04

### Initial Release
- 9-layer human architecture
- SYMBIOTE-INSTALL.md
- IDENTITY-TEMPLATE.md
- MIT license
