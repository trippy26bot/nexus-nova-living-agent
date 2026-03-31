#!/usr/bin/env python3
"""
run_demo.py — Nexus Nova Framework Demo

Minimal demo that boots the framework and shows a short interaction.
Anyone cloning the repo can run this directly:
    python3 demo/run_demo.py

Dependencies: Python 3.9+ standard library only.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# ── Framework paths ──────────────────────────────────────────────────────────
WORKSPACE = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(WORKSPACE))

# ── 1. Identity load ─────────────────────────────────────────────────────────
print("=" * 60)
print("NEXUS NOVA FRAMEWORK — Demo Run")
print("=" * 60)

identity_file = WORKSPACE / "IDENTITY.md"
soul_file = WORKSPACE / "SOUL.md"

if identity_file.exists():
    print(f"\n[1] Identity loaded from {identity_file}")
    content = identity_file.read_text()
    # Print first non-empty, non-heading line as name
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            print(f"    Name: {line}")
            break
else:
    print("\n[1] Identity file not found (optional for framework)")

if soul_file.exists():
    print(f"\n[2] Soul loaded — core principles:")
    principles = [l.strip() for l in soul_file.read_text().splitlines()
                  if l.strip().startswith("- ")][:4]
    for p in principles:
        print(f"    {p}")

# ── 2. Knowledge Graph ───────────────────────────────────────────────────────
print("\n[3] Booting Knowledge Graph...")
from core.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph(db_path="/tmp/nexus_demo_kg.db")
print(f"    Knowledge Graph initialized: {kg.db_path}")

# Add a sample triple: Caine builds Nova
kg.add_entity("Caine", entity_type="person", properties={"role": "operator"})
kg.add_entity("Nova", entity_type="agent", properties={"type": "framework"})
kg.add_relationship("Caine", "builds", "Nova")

# Query it
results = kg.query("Caine", "builds", None)
print(f"    Query(Caine --builds--> ?) → {len(results)} result(s)")
for r in results:
    print(f"      {r['from_entity']} --{r['relationship']}--> {r['to_entity']}")

# ── 3. Skill Dispatcher ──────────────────────────────────────────────────────
print("\n[4] Booting Skill Dispatcher...")
from skills.dispatcher import SkillDispatcher

dispatcher = SkillDispatcher()
active = dispatcher.list_active_skills()
print(f"    Active skills: {active}")

trusted = [s for s in active if dispatcher.get_trust_level(s) == "trusted"]
print(f"    Trusted skills: {trusted}")

# ── 4. Memory write ───────────────────────────────────────────────────────────
print("\n[5] Memory write (ephemeral demo state)...")
memory_log = Path("/tmp/nexus_demo_memory.log")
ts = datetime.now().isoformat()
entry = f"[{ts}] demo:synthetic_interaction — framework boot successful\n"
memory_log.write_text(entry)
print(f"    Written to: {memory_log}")
print(f"    Entry: {entry.strip()}")

# ── Done ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("Demo complete. Framework boots and runs correctly.")
print("=" * 60)
