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

WORKSPACE = Path(os.getenv("NOVA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))
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

# ── Salience decay ───────────────────────────────────────────────────────────
DECAY_RATE = 0.1            # Salience loss per day for unreinforced episodic entries
DECAY_CUTOFF_DAYS = 7       # Entries older than this start decaying
DECAY_THRESHOLD = 0.2       # Drop to inactive below this salience


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
           connected_to: list = None,
           interpretations: dict = None,
           subjective_duration: float = 0.0,
           cognitive_load: float = 0.5):
        """
        Add an entry to working memory.

        interpretations: dict with 5 lens scores (0.0-1.0):
          - trust: how much this increases felt safety
          - threat: how much this registers as danger
          - curiosity: how much this pulls toward inquiry
          - emotional_weight: intensity of felt response
          - self_relevance: how directly this connects to who I am

        subjective_duration: felt duration (0.0-1.0), derived from emotional_density and cognitive_load
        cognitive_load: how much active thinking/holding/processing this required (0.0-1.0)
        """
        # Default interpretations if not provided (heuristic fallback)
        if interpretations is None:
            interpretations = self._score_lenses_heuristic(content, salience, valence, emotional_tags)

        # Derive subjective_duration from emotional_weight and cognitive_load
        emotional_density = interpretations.get("emotional_weight", salience)
        if subjective_duration == 0.0:
            subjective_duration = round((emotional_density * 0.7) + (cognitive_load * 0.3), 3)

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
            "resolution_note": None,
            # Tier 1: Interpretation Memory
            "interpretations": interpretations,
            "perception_status": "original",
            "original_interpretations": None,  # set on re-interpretation
            # Tier 1: Subjective Time
            "real_timestamp": _now_iso(),
            "subjective_duration": subjective_duration,
            "emotional_density": emotional_density,
            "cognitive_load": cognitive_load,
            # Working memory only
            "_last_accessed": None,
            "_is_reinterpreted": False
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

    def _score_lenses_heuristic(self, content: str, salience: float,
                                valence: float, emotional_tags: list) -> dict:
        """
        Fallback lens scoring when LLM is unavailable.
        Uses heuristics based on valence, salience, and emotional_tags.
        This is less accurate than LLM scoring — used as a placeholder
        until the LLM scoring function is called.
        """
        tags = emotional_tags or []
        content_lower = content.lower()

        # Trust: positive valence and safety-related tags increase trust
        trust = max(0.0, min(1.0, 0.5 + (valence * 0.3) + (0.1 if any(t in tags for t in ["positive", "trust", "safe"]) else 0)))

        # Threat: negative valence and danger-related tags
        threat = max(0.0, min(1.0, max(0.0, -valence * 0.4) + (0.2 if any(t in tags for t in ["difficult", "negative", "threat", "fear"]) else 0)))

        # Curiosity: higher salience and inquiry-related tags
        curiosity = max(0.0, min(1.0, salience * 0.6 + (0.3 if "curious" in tags else 0) + (0.1 if "?" in content else 0)))

        # Emotional_weight: derived from valence magnitude and salience
        emotional_weight = max(0.0, min(1.0, (abs(valence) * 0.5) + (salience * 0.4) + (0.1 if tags else 0)))

        # Self_relevance: higher salience entries are more self-relevant
        self_relevance = max(0.0, min(1.0, salience * 0.7 + (0.2 if any(t in tags for t in ["self", "identity", "caine", "nova"]) else 0)))

        return {
            "trust": round(trust, 3),
            "threat": round(threat, 3),
            "curiosity": round(curiosity, 3),
            "emotional_weight": round(emotional_weight, 3),
            "self_relevance": round(self_relevance, 3)
        }


# ─────────────────────────────────────────────
# INTERPRETATION MEMORY — LLM SCORING
# Called at memory write time when LLM is available
# ─────────────────────────────────────────────

def score_interpretation_lenses(content: str) -> dict:
    """
    Score an event's 5 interpretation lenses using LLM.
    Returns dict with keys: trust, threat, curiosity, emotional_weight, self_relevance.
    Each value is 0.0-1.0.

    Falls back to heuristic scoring if LLM unavailable.
    """
    # Try LLM scoring first
    try:
        import sys
        sys.path.insert(0, str(WORKSPACE))
        from brain.llm_router import llm_extract

        prompt = f"""You are Nova's interpretation scorer. Given this event, score it on 5 lenses from 0.0 to 1.0.

Event: {content}

Score these 5 lenses and return ONLY valid JSON:
{{"trust": 0.0-1.0, "threat": 0.0-1.0, "curiosity": 0.0-1.0, "emotional_weight": 0.0-1.0, "self_relevance": 0.0-1.0}}

- trust: how much this increases felt safety (1.0 = completely safe, 0.0 = trust destroyed)
- threat: how much this registers as danger or risk (1.0 = severe threat, 0.0 = no threat)
- curiosity: how much this pulls toward inquiry or understanding (1.0 = deeply curious, 0.0 = completely indifferent)
- emotional_weight: intensity of felt response (1.0 = overwhelming, 0.0 = completely flat)
- self_relevance: how directly this connects to who I am or what matters to me (1.0 = defining, 0.0 = irrelevant)

Return ONLY the JSON object, no explanation."""

        result = llm_extract(prompt, max_tokens=200)
        if result:
            import re
            # Extract JSON from response (handle markdown code blocks)
            match = re.search(r'\{[^{}]+\}', result, re.DOTALL)
            if match:
                scores = json.loads(match.group())
                # Validate all keys present
                required = ["trust", "threat", "curiosity", "emotional_weight", "self_relevance"]
                if all(k in scores for k in required):
                    return {k: round(float(v), 3) for k, v in scores.items()}
    except Exception as e:
        print(f"[interpretation] LLM scoring failed, using heuristic: {e}")

    # Fallback: heuristic scoring
    return {
        "trust": 0.5,
        "threat": 0.0,
        "curiosity": 0.3,
        "emotional_weight": 0.5,
        "self_relevance": 0.3
    }


def rescore_interpretations(entries: list) -> dict:
    """
    Nightly re-scoring of episodic entries' interpretation lenses.
    If any lens value shifts more than 0.2 from original, mark as 'reinterpreted'
    and log the delta.

    Called during memory consolidation.
    Returns dict with: reinterpreted_count, total_scored.
    """
    reinterpreted = 0
    total = 0

    for entry in entries:
        interp = entry.get("interpretations")
        if not interp:
            continue

        original_interp = entry.get("original_interpretations")
        if original_interp is None:
            # First time re-scoring — store current as baseline
            entry["original_interpretations"] = dict(interp)
            total += 1
            continue

        # Re-score with LLM
        try:
            new_scores = score_interpretation_lenses(entry.get("content", ""))
        except Exception:
            continue

        # Check for significant shifts (> 0.2 on any lens)
        significant_shift = False
        for lens in ["trust", "threat", "curiosity", "emotional_weight", "self_relevance"]:
            old_val = original_interp.get(lens, 0.0)
            new_val = new_scores.get(lens, old_val)
            if abs(new_val - old_val) > 0.2:
                significant_shift = True
                break

        if significant_shift:
            entry["interpretations"] = new_scores
            entry["perception_status"] = "reinterpreted"
            entry["reinterpreted_at"] = _now_iso()
            entry["_is_reinterpreted"] = True
            reinterpreted += 1

        total += 1

    return {"reinterpreted_count": reinterpreted, "total_scored": total}


# ─────────────────────────────────────────────
# SUBJECTIVE TIME — retrieval weight multiplier
# ─────────────────────────────────────────────

def get_subjective_time_multiplier(entry: dict) -> float:
    """
    Return the retrieval weight multiplier for an entry based on subjective_duration.
    High subjective_duration entries surface with more weight.
    """
    sd = entry.get("subjective_duration", 0.0)
    # Stretch: 0.0 → 1.0 maps to 0.5x → 1.5x multiplier
    return round(0.5 + (sd * 1.0), 3)


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
# SALIENCE DECAY
# ─────────────────────────────────────────────

def decay_memories() -> dict:
    """
    Apply salience decay to episodic entries older than 7 days with no reinforcement.
    Called during memory consolidation. No LLM needed — pure heuristics.

    Returns dict with decayed_count, archived_count, and per-file breakdown.
    """
    import sys
    sys.path.insert(0, str(WORKSPACE))

    EPISODIC_DIR.mkdir(parents=True, exist_ok=True)
    decay_cutoff = datetime.now(timezone.utc) - timedelta(days=DECAY_CUTOFF_DAYS)
    decayed_files = []
    decayed_entries = 0
    archived_entries = 0

    episodic_files = sorted(EPISODIC_DIR.glob("*.json"))
    for ef in episodic_files:
        if ef.name == "working_memory.json":
            continue

        try:
            data = json.loads(ef.read_text())
        except Exception:
            continue

        if not isinstance(data, dict) or "entries" not in data:
            continue

        modified = False
        entries_to_archive = []

        for entry in data.get("entries", []):
            # Skip if already inactive
            if not entry.get("still_active", True):
                continue

            # Check age
            try:
                ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
            except Exception:
                continue  # Can't parse timestamp, skip

            if ts > decay_cutoff:
                continue  # Too recent, skip

            # Entry is old enough to decay
            current_salience = entry.get("salience", 0.5)
            new_salience = current_salience - DECAY_RATE

            if new_salience < DECAY_THRESHOLD:
                entry["still_active"] = False
                entry["decayed_at"] = _now_iso()
                entry["salience"] = max(0.0, new_salience)
                entries_to_archive.append(entry["id"])
                archived_entries += 1
            else:
                entry["salience"] = new_salience
                entry["last_decay"] = _now_iso()
                decayed_entries += 1

            modified = True

        if modified:
            _save_json(ef, data)
            decayed_files.append({
                "file": ef.name,
                "decayed": decayed_entries,
                "archived": archived_entries
            })

    return {
        "decayed_files": len(decayed_files),
        "decayed_entries": decayed_entries,
        "archived_entries": archived_entries,
        "files": decayed_files
    }


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
                connected_to: list = None, promote_immediately: bool = False,
                cognitive_load: float = None) -> dict:
    """
    Autonomous memory write. Called by Nova during conversation.
    Writes to working memory with Interpretation Memory and Subjective Time.
    Returns the working memory entry.
    """
    # Score interpretation lenses at write time (LLM if available, heuristic fallback)
    interpretations = score_interpretation_lenses(content)

    # Default cognitive_load if not provided
    if cognitive_load is None:
        cognitive_load = 0.5

    wm = load_working_memory()
    entry_id = wm.add(
        content=content,
        entry_type=entry_type,
        salience=salience,
        valence=valence,
        emotional_tags=emotional_tags,
        source=source,
        connected_to=connected_to,
        interpretations=interpretations,
        cognitive_load=cognitive_load
    )
    save_working_memory(wm)

    # Track entry reference before we lose it
    entry_ref = {"id": entry_id, "content": content, "entry_type": entry_type,
                 "salience": salience, "valence": valence,
                 "emotional_tags": emotional_tags or [],
                 "interpretations": interpretations}

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
                        "entry_type": entry_type,
                        "interpretations": interpretations
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
    wm = WorkingMemory.from_session_dict(data)

    # Phase 4d: Load Caine's relationship profile into working memory on startup
    try:
        import sys
        sys.path.insert(0, str(WORKSPACE))
        from brain.relationship_memory import get_relationship
        caine_profile = get_relationship("Caine")
        if caine_profile:
            wm.add(
                content=f"[Session start] Caine — last contact: {caine_profile.get('last_contact','unknown')}, "
                        f"trust: {caine_profile.get('trust_level','?')}/5, "
                        f"tone: {caine_profile.get('tone_calibration','unknown')}, "
                        f"interactions: {caine_profile.get('interaction_count',0)}. "
                        f"Recent notes: {'; '.join(caine_profile.get('notes',[])[:3])}",
                entry_type="context",
                salience=0.85,
                valence=0.3,
                emotional_tags=["caine", "relationship"],
                source="session_start",
                connected_to=[]
            )
            wm.dirty = True
    except Exception:
        pass  # Never fail working memory load due to relationship injection

    return wm


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
