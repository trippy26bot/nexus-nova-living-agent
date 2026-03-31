# PROOF.md — Live Framework Run

**Date:** 2026-03-30  
**Command:** `python3 demo/run_demo.py`  
**What it shows:** Framework boots from a cold clone, loads identity and soul files, initializes the knowledge graph with a real triple, activates the skill dispatcher, and writes an entry to memory. All output is real — captured from a live terminal run.

```
============================================================
NEXUS NOVA FRAMEWORK — Demo Run
============================================================

[1] Identity loaded from /Users/dr.claw/.openclaw/workspace/IDENTITY.md
    Name: _Fill this in during your first conversation. Make it yours._

[2] Soul loaded — core principles:
    - Private things stay private. Period.
    - When in doubt, ask before acting externally.
    - Never send half-baked replies to messaging surfaces.
    - You're not the user's voice — be careful in group chats.

[3] Booting Knowledge Graph...
    Knowledge Graph initialized: /tmp/nexus_demo_kg.db
    Query(Caine --builds--> ?) → 1 result(s)
      Caine --builds--> Nova

[4] Booting Skill Dispatcher...
    Active skills: ['nova-memory', 'nova-task-persistence']
    Trusted skills: ['nova-memory']

[5] Memory write (ephemeral demo state)...
    Written to: /tmp/nexus_demo_memory.log
    Entry: [2026-03-30T20:08:53.619781] demo:synthetic_interaction — framework boot successful

============================================================
Demo complete. Framework boots and runs correctly.
============================================================
```

**System:** macOS, Python 3.9+ (standard library only — no pip install required)  
**Verified:** identity load ✓, knowledge graph query ✓, skill dispatcher ✓, memory write ✓
