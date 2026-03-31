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
from brain.knowledge_graph import add_node, add_edge, _load_graph

# Add sample entities: Caine builds Nova
caine_id = add_node(node_id="caine", label="Caine", node_type="person",
                     properties={"role": "operator"})
nova_id = add_node(node_id="nova", label="Nova", node_type="agent",
                   properties={"type": "framework"})
rel_id = add_edge(from_id=caine_id, to_id=nova_id, edge_type="builds")

graph = _load_graph()
entities = list(graph.get("nodes", {}).keys())
print(f"    Knowledge Graph initialized: {len(entities)} entity(s)")
print(f"    Nodes: {', '.join(entities)}")

# ── 3. Overnight skill availability ─────────────────────────────────────────
print("\n[4] Overnight skills available...")
skills_dir = WORKSPACE / "skills"
skill_scripts = [f.stem for f in skills_dir.glob("*.py")]
overnight_skills = ["dream_generator", "overnight_synthesis",
                    "memory_consolidation", "drift_detector"]
available = [s for s in overnight_skills if s in skill_scripts]
print(f"    Overnight skills: {', '.join(available)}")

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
