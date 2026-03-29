#!/usr/bin/env python3
"""
Three-Tier Memory System — Nova's Cognitive Architecture
Implements: Working → Episodic → Semantic promotion

Status: ✅ IMPLEMENTED — Phase 2a Item 2
"""

import json
import uuid
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path("/Users/dr.claw/.openclaw/workspace")
EPISODIC_DIR = WORKSPACE / "memory" / "episodic"
WORKING_FILE = EPISODIC_DIR / "working_memory.json"
UNRESOLVED_FILE = WORKSPACE / "memory" / "unresolved.json"
VECTOR_RETRIEVAL = WORKSPACE / "brain" / "vector_retrieval.py"

# Lazy imports (avoid circular)
_phenomenology = None
_knowledge_graph = None


def _get_phenomenology():
    global _phenomenology
    if _phenomenology is None:
        try:
            import sys
            sys.path.insert(0, str(WORKSPACE / "skills"))
            import phenomenology
            _phenomenology = phenomenology
        except Exception:
            _phenomenology = False  # Mark as unavailable, don't retry
    return _phenomenology


def _get_knowledge_graph():
    global _knowledge_graph
    if _knowledge_graph is None:
        try:
            import knowledge_graph
            _knowledge_graph = knowledge_graph
        except Exception:
            _knowledge_graph = False
    return _knowledge_graph

# Tier retention rules
WORKING_TTL_HOURS = 8       # Working memory max age before flush
EPISODIC_TTL_DAYS = 3       # Episodic retention before semantic promotion
ARCHIVE_AGE_DAYS = 30       # Archive after this long


def _load_json(path, default=None):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return default or {}
    return default or {}


def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────
# WORKING MEMORY (Tier 1)
# Current session context — in-memory equivalent
# ─────────────────────────────────────────────

class WorkingMemory:
    """Lightweight working memory for current session."""

    def __init__(self):
        self.entries = []
        self.session_id = str(uuid.uuid4())
        self.session_start = _now_iso()
        self.dirty = False

    def add(self, content: str, entry_type: str = "session_event",
           salience: float = 0.5, valence: float = 0.0,
           emotional_tags: list = None, source: str = "conversation",
           connected_to: list = None):
        """Add an entry to working memory."""
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": _now_iso(),
            "type": entry_type,
            "content": content,
            "salience": salience,
            "valence": valence,
            "emotional_tags": emotional_tags or [],
            "source": source,
            "connected_to": connected_to or [],
            "still_active": True,
            "resolved": False,
            "resolution_note": None
        }
        self.entries.append(entry)
        self.dirty = True
        return entry["id"]

    def get_active(self) -> list:
        """Return all still-active entries."""
        return [e for e in self.entries if e.get("still_active", True)]

    def mark_resolved(self, entry_id: str, resolution_note: str = None):
        """Mark an entry as resolved."""
        for e in self.entries:
            if e["id"] == entry_id:
                e["resolved"] = True
                e["still_active"] = False
                if resolution_note:
                    e["resolution_note"] = resolution_note
                self.dirty = True

    def mark_inactive(self, entry_id: str):
        """Mark an entry as no longer active."""
        for e in self.entries:
            if e["id"] == entry_id:
                e["still_active"] = False
                self.dirty = True

    def touch(self, entry_id: str):
        """Mark an entry as recently accessed (boost salience slightly)."""
        for e in self.entries:
            if e["id"] == entry_id:
                e["_last_accessed"] = _now_iso()
                e["salience"] = min(1.0, e["salience"] + 0.05)
                self.dirty = True

    def to_session_dict(self) -> dict:
        """Serialize for context injection."""
        return {
            "session_id": self.session_id,
            "session_start": self.session_start,
            "entries": self.entries,
            "active_count": len(self.get_active()),
            "loaded_at": _now_iso()
        }

    @classmethod
    def from_session_dict(cls, data: dict) -> "WorkingMemory":
        """Reconstruct from serialized session dict."""
        wm = cls()
        if data:
            wm.session_id = data.get("session_id", str(uuid.uuid4()))
            wm.session_start = data.get("session_start", _now_iso())
            wm.entries = data.get("entries", [])
            wm.dirty = False
        return wm


# ─────────────────────────────────────────────
# EPISODIC MEMORY (Tier 2)
# Stored on disk, promoted from working memory
# ─────────────────────────────────────────────

def flush_working_to_episodic(working: WorkingMemory, force: bool = False):
    """
    Flush working memory entries to episodic storage.
    Called on session close or TTL expiry.
    Entries with salience >= 0.5 get promoted.
    """
    EPISODIC_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    episodic_file = EPISODIC_DIR / f"{today}.json"

    existing = _load_json(episodic_file, {"date": today, "entries": []})

    flushed = 0
    for entry in working.entries:
        # Promote if salience is meaningful or force is set
        if entry["salience"] >= 0.5 or force:
            # Don't duplicate
            if any(e["id"] == entry["id"] for e in existing["entries"]):
                continue
            # Reset some fields for episodic storage
            episodic_entry = dict(entry)
            episodic_entry["flushed_at"] = _now_iso()
            existing["entries"].append(episodic_entry)
            flushed += 1

    if flushed > 0:
        existing["last_updated"] = _now_iso()
        _save_json(episodic_file, existing)

    return {"flushed": flushed, "file": str(episodic_file)}


def get_episodic_entries(days: int = None, limit: int = 100) -> list:
    """Load recent episodic entries."""
    if not EPISODIC_DIR.exists():
        return []

    cutoff = None
    if days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    all_entries = []
    for f in sorted(EPISODIC_DIR.glob("*.json"), reverse=True):
        data = _load_json(f)
        for entry in data.get("entries", []):
            if cutoff:
                try:
                    ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                    if ts < cutoff:
                        continue
                except Exception:
                    pass
            all_entries.append(entry)

        if len(all_entries) >= limit:
            break

    return all_entries[:limit]


# ─────────────────────────────────────────────
# SEMANTIC MEMORY (Tier 3)
# Distilled facts, beliefs, positions
# Stored in brain/ directory + vector store
# ─────────────────────────────────────────────

def promote_episodic_to_semantic(entry: dict) -> str:
    """
    Promote an episodic entry to semantic memory.
    Distills the episodic content into a structured belief/insight.
    Returns vector store entry ID.
    """
    # Import here to avoid circular
    import sys
    sys.path.insert(0, str(WORKSPACE))
    try:
        from brain.vector_retrieval import write_memory
    except Exception:
        return None

    entry_type_map = {
        "session_event": "insight",
        "decision": "belief",
        "reflection": "reflection",
        "belief": "belief",
        "position": "position",
        "lesson": "lesson",
        "relationship": "relationship"
    }

    semantic_type = entry_type_map.get(entry.get("type", "insight"), "insight")
    content = entry.get("content", "")
    salience = entry.get("salience", 0.5)

    # Skip very low salience entries
    if salience < 0.5:
        return None

    # Extract applies_to tags from emotional_tags
    applies_to = entry.get("emotional_tags", [])

    vector_id = write_memory(
        text=content,
        entry_type=semantic_type,
        confidence=salience,
        source=f"episodic_promotion:{entry.get('id', 'unknown')}",
        applies_to=applies_to,
        metadata={
            "original_timestamp": entry.get("timestamp"),
            "valence": entry.get("valence", 0),
            "salience": salience
        }
    )
    return vector_id


def distill_episodic_file(episodic_file: Path) -> dict:
    """
    Process an episodic file for semantic promotion.
    Called during consolidation runs.
    """
    data = _load_json(episodic_file)
    entries = data.get("entries", [])
    promoted = 0
    skipped = 0

    for entry in entries:
        # Only promote entries that are resolved and high-salience
        if entry.get("resolved") and entry.get("salience", 0) >= 0.7:
            result = promote_episodic_to_semantic(entry)
            if result:
                promoted += 1
            else:
                skipped += 1
        else:
            skipped += 1

    return {"promoted": promoted, "skipped": skipped, "total": len(entries)}


# ─────────────────────────────────────────────
# UNRESOLVED QUEUE
# ─────────────────────────────────────────────

def load_unresolved() -> dict:
    return _load_json(UNRESOLVED_FILE, {"unresolved": []})


def save_unresolved(data: dict):
    _save_json(UNRESOLVED_FILE, data)


def add_unresolved(question: str, checkpoint: str = None,
                  linked_memory_id: str = None) -> str:
    """Add an unresolved item to tracking."""
    data = load_unresolved()
    item_id = str(uuid.uuid4())
    item = {
        "id": item_id,
        "question": question,
        "started": _now_iso(),
        "checkpoint": checkpoint,
        "stale": False,
        "linked_memory_id": linked_memory_id
    }
    data["unresolved"].append(item)
    save_unresolved(data)
    return item_id


def resolve_unresolved(item_id: str, resolution_note: str):
    """Mark an unresolved item as resolved."""
    data = load_unresolved()
    for item in data["unresolved"]:
        if item["id"] == item_id:
            item["resolved"] = True
            item["resolved_at"] = _now_iso()
            item["resolution_note"] = resolution_note
    save_unresolved(data)


# ─────────────────────────────────────────────
# AUTONOMOUS MEMORY TOOLS
# Called by Nova during conversation
# ─────────────────────────────────────────────

def memory_write(content: str, entry_type: str = "insight",
                salience: float = 0.5, valence: float = 0.0,
                emotional_tags: list = None, source: str = "conversation",
                connected_to: list = None, promote_immediately: bool = False) -> dict:
    """
    Autonomous memory write. Called by Nova during conversation.
    Writes to working memory. If promote_immediately, also write to vector store.
    Returns the working memory entry.
    """
    wm = load_working_memory()
    entry_id = wm.add(
        content=content,
        entry_type=entry_type,
        salience=salience,
        valence=valence,
        emotional_tags=emotional_tags,
        source=source,
        connected_to=connected_to
    )
    save_working_memory(wm)

    # Track entry reference before we lose it
    entry_ref = {"id": entry_id, "content": content, "entry_type": entry_type,
                 "salience": salience, "valence": valence,
                 "emotional_tags": emotional_tags or []}

    if promote_immediately or salience >= 0.8:
        # High salience = immediate semantic promotion
        entry = next((e for e in wm.entries if e["id"] == entry_id), None)
        if entry:
            promote_episodic_to_semantic(entry)

    # Phenomenology hook — salience >= 0.7 is significant enough to reflect on
    if salience >= 0.7:
        ph = _get_phenomenology()
        if ph:
            try:
                ph.check_and_write(entry_ref, event_type="memory_write")
            except Exception:
                pass  # Never fail a memory write due to phenomenology

    # Knowledge graph hook — salience >= 0.7 → add as semantic node
    if salience >= 0.7:
        kg = _get_knowledge_graph()
        if kg:
            try:
                node_type = "belief" if entry_type in ("belief", "lesson", "reflection") else "concept"
                node_id = kg.add_node(
                    node_id=None,
                    label=content[:80],
                    node_type=node_type,
                    properties={
                        "entry_id": entry_id,
                        "source": source,
                        "valence": valence,
                        "entry_type": entry_type
                    }
                )
            except Exception:
                pass  # Never fail a memory write due to knowledge graph

    return {"entry_id": entry_id, "salience": salience, "promoted": salience >= 0.8}


def memory_edit(entry_id: str, new_content: str = None,
               new_salience: float = None, new_valence: float = None,
               resolution_note: str = None) -> dict:
    """
    Edit an existing memory entry.
    Original is preserved with revision metadata.
    """
    wm = load_working_memory()
    found = False
    for entry in wm.entries:
        if entry["id"] == entry_id:
            if new_content is not None:
                entry["original_content"] = entry.get("content")
                entry["content"] = new_content
                entry["edited_at"] = _now_iso()
                entry["revision_count"] = entry.get("revision_count", 0) + 1
            if new_salience is not None:
                entry["salience"] = new_salience
            if new_valence is not None:
                entry["valence"] = new_valence
            if resolution_note:
                entry["resolution_note"] = resolution_note
            wm.dirty = True
            found = True
            break

    if found:
        save_working_memory(wm)
        return {"updated": entry_id, "revision": entry.get("revision_count", 1)}
    return {"error": "entry not found"}


def memory_forget(entry_id: str, reason: str = None) -> dict:
    """
    Archive a memory (never hard delete). Never applies to identity moments.
    """
    wm = load_working_memory()
    for entry in wm.entries:
        if entry["id"] == entry_id:
            # Never forget identity moments
            if entry.get("salience", 0) >= 0.95:
                return {"error": "identity moment — cannot forget"}
            entry["archived"] = True
            entry["archived_at"] = _now_iso()
            entry["forget_reason"] = reason
            entry["still_active"] = False
            wm.dirty = True
            save_working_memory(wm)
            return {"archived": entry_id}
    return {"error": "entry not found"}


# ─────────────────────────────────────────────
# WORKING MEMORY PERSISTENCE
# ─────────────────────────────────────────────

def load_working_memory() -> WorkingMemory:
    """Load working memory from disk."""
    data = _load_json(WORKING_FILE)
    return WorkingMemory.from_session_dict(data)


def save_working_memory(wm: WorkingMemory):
    """Save working memory to disk."""
    _save_json(WORKING_FILE, wm.to_session_dict())
    wm.dirty = False


def clear_working_memory():
    """Clear working memory (after successful flush)."""
    if WORKING_FILE.exists():
        WORKING_FILE.unlink()


# ─────────────────────────────────────────────
# CONSOLIDATION LOGIC (for session_capture integration)
# ─────────────────────────────────────────────

def periodic_capture(working: WorkingMemory = None) -> dict:
    """Called by cron every 15 minutes."""
    if working is None:
        working = load_working_memory()

    # Save current working state
    save_working_memory(working)

    return {
        "captured_at": _now_iso(),
        "session_id": working.session_id,
        "active_entries": len(working.get_active()),
        "total_entries": len(working.entries)
    }


# ─────────────────────────────────────────────
# SESSION CLOSE — FULL FLUSH
# ─────────────────────────────────────────────

def session_close_flush() -> dict:
    """
    Full session close: flush working → episodic → semantic.
    Called when session is ending.
    """
    working = load_working_memory()
    result = flush_working_to_episodic(working, force=True)

    # Mark all as inactive
    for entry in working.entries:
        entry["still_active"] = False
    save_working_memory(working)

    return {
        "flushed": result,
        "session_id": working.session_id,
        "closed_at": _now_iso()
    }


if __name__ == "__main__":
    import sys
    # CLI for testing
    if len(sys.argv) < 2:
        print("Usage: three_tier_memory.py <write|search|flush|stats> [args]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "write":
        text = sys.argv[2] if len(sys.argv) > 2 else "test memory"
        r = memory_write(text, entry_type="test", salience=0.6)
        print(f"Written: {r}")

    elif cmd == "flush":
        r = session_close_flush()
        print(f"Flushed: {r}")

    elif cmd == "stats":
        wm = load_working_memory()
        print(f"Working memory: {len(wm.entries)} entries, {len(wm.get_active())} active")
        episodic_files = list(EPISODIC_DIR.glob("*.json")) if EPISODIC_DIR.exists() else []
        print(f"Episodic files: {len(episodic_files)}")

    elif cmd == "recent":
        entries = get_episodic_entries(days=3)
        print(f"Recent episodic: {len(entries)} entries")
        for e in entries[:5]:
            print(f"  [{e['salience']}] {e['content'][:60]}")

    else:
        print(f"Unknown: {cmd}")
