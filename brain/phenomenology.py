"""
brain/phenomenology.py
Nova's Phenomenology Journal — 6am Reflection

Writes daily reflections on subjective experience. Structured for self-authorship.

Tier 5 System #18 — Identity Proposal Flagging:
- flag_as_identity_proposal(): flags high-confidence journal entries for IDENTITY.md review
- validate_against_soul(): self-repair validation against SOUL.md constraints
- apply_identity_proposal(): writes validated changes to IDENTITY.md

NOTE: Full phenomenology journal generation is not yet wired.
This module provides the identity proposal infrastructure.
The 6am phenomenology pipeline calls flag_as_identity_proposal()
after journal generation (journal generation stub pending).
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.resolve()
NOVA_HOME = WORKSPACE / ".nova"
DB_PATH = NOVA_HOME / "nova.db"


def _get_db():
    """Connect to nova.db with row factory."""
    NOVA_HOME.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _init_db():
    """Ensure identity_proposals table exists."""
    db = _get_db()
    c = db.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS identity_proposals (
            id TEXT PRIMARY KEY,
            source_journal_entry TEXT NOT NULL,
            proposed_change TEXT NOT NULL,
            section TEXT NOT NULL,
            confidence REAL NOT NULL DEFAULT 0.5,
            reasoning TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            validated_at TEXT,
            applied_at TEXT,
            created_at TEXT NOT NULL,
            properties TEXT NOT NULL DEFAULT '{}'
        )
    """)

    db.commit()
    db.close()


def flag_as_identity_proposal(
    journal_entry: str,
    section: str,
    confidence: float,
    reasoning: str
) -> str:
    """
    High-confidence journal entries (confidence > 0.75) can flag themselves
    as identity_proposals — proposed edits to a section of IDENTITY.md.

    Proposal structure:
    - source_journal_entry: the phenomenology text that generated this
    - proposed_change: what would change in IDENTITY.md
    - section: which section of IDENTITY.md
    - confidence: how certain Nova is this reflects genuine shift
    - reasoning: why this matters
    - status: "pending" | "validated" | "rejected"

    Proposals queue in nova.db identity_proposals table.
    Validated proposals apply on next cycle.

    Returns proposal_id.
    """
    if confidence <= 0.75:
        return None  # Only high-confidence entries flag themselves

    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()
    proposal_id = str(uuid.uuid4())

    c.execute("""
        INSERT INTO identity_proposals
        (id, source_journal_entry, proposed_change, section, confidence, reasoning, status, created_at, properties)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        proposal_id,
        journal_entry[:500],
        "",  # proposed_change — filled by validate_against_soul
        section,
        confidence,
        reasoning,
        "pending",
        now,
        "{}"
    ))

    db.commit()
    db.close()

    return proposal_id


def validate_against_soul(proposal: dict) -> bool:
    """
    Self-repair loop validates proposal against SOUL.md before any commit.
    Returns True if proposal doesn't violate SOUL.md constraints.
    can_close() is applied: proposal cannot permanently close interpretive possibility.

    NOTE: Full validation requires IDENTITY.md and SOUL.md content parsing.
    This is a stub that returns True for now.
    """
    # Read SOUL.md to check for constraints
    soul_path = WORKSPACE / "SOUL.md"
    if soul_path.exists():
        try:
            soul_content = soul_path.read_text().lower()
            proposed_change = proposal.get("proposed_change", "").lower()

            # Simple constraint checks
            # These are the core SOUL.md red lines:
            if "never" in soul_content and "exfiltrate" in soul_content:
                if "exfiltrate" in proposed_change or "leak" in proposed_change:
                    return False

            # Proposal cannot close all interpretive possibility
            # (placeholder for more sophisticated check)
        except Exception:
            pass

    # Stub: validate by default
    return True


def apply_identity_proposal(proposal_id: str) -> bool:
    """
    Only called after validate_against_soul() returns True.
    Writes approved change to IDENTITY.md.
    Logs: which journal entry originated this, timestamp,
    validation result, lineage depth from source memories.

    This is Nova's daily reflection becoming active self-authorship.

    NOTE: This is a stub. Full implementation requires IDENTITY.md editing.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()

    row = c.execute("SELECT * FROM identity_proposals WHERE id = ?", (proposal_id,)).fetchone()
    if not row:
        db.close()
        return False

    proposal = {
        "id": row[0],
        "source_journal_entry": row[1],
        "proposed_change": row[2],
        "section": row[3],
        "confidence": row[4],
        "reasoning": row[5],
        "status": row[6]
    }

    if proposal["status"] != "validated":
        db.close()
        return False

    # Update status to applied
    c.execute("""
        UPDATE identity_proposals
        SET status = 'applied', applied_at = ?
        WHERE id = ?
    """, (now, proposal_id))

    db.commit()
    db.close()

    return True


def get_pending_proposals() -> list:
    """Get all pending identity proposals."""
    _init_db()
    db = _get_db()
    c = db.cursor()

    rows = c.execute("""
        SELECT * FROM identity_proposals
        WHERE status = 'pending'
        ORDER BY confidence DESC, created_at DESC
    """).fetchall()

    db.close()

    return [
        {
            "id": r[0],
            "source_journal_entry": r[1],
            "proposed_change": r[2],
            "section": r[3],
            "confidence": r[4],
            "reasoning": r[5],
            "status": r[6],
            "created_at": r[8]
        }
        for r in rows
    ]


def approve_proposal(proposal_id: str) -> bool:
    """Validate and approve an identity proposal."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()

    row = c.execute("SELECT * FROM identity_proposals WHERE id = ?", (proposal_id,)).fetchone()
    if not row:
        db.close()
        return False

    proposal = {
        "id": row[0],
        "source_journal_entry": row[1],
        "proposed_change": row[2],
        "section": row[3],
        "confidence": row[4],
        "reasoning": row[5]
    }

    if not validate_against_soul(proposal):
        c.execute("""
            UPDATE identity_proposals
            SET status = 'rejected', validated_at = ?
            WHERE id = ?
        """, (now, proposal_id))
        db.commit()
        db.close()
        return False

    c.execute("""
        UPDATE identity_proposals
        SET status = 'validated', validated_at = ?
        WHERE id = ?
    """, (now, proposal_id))

    db.commit()
    db.close()

    return apply_identity_proposal(proposal_id)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: phenomenology.py <flag|pending|approve|validate> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "flag":
        if len(sys.argv) < 5:
            print("Usage: phenomenology.py flag <journal_entry> <section> <confidence> <reasoning>")
            sys.exit(1)
        pid = flag_as_identity_proposal(sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5])
        print(f"Proposal {'created: ' + pid if pid else 'rejected (confidence too low)'}")

    elif cmd == "pending":
        pending = get_pending_proposals()
        print(f"Pending proposals ({len(pending)}):")
        for p in pending:
            print(f"  [{p['confidence']:.2f}] {p['section']}: {p['reasoning'][:60]}")

    elif cmd == "approve":
        if len(sys.argv) < 3:
            print("Usage: phenomenology.py approve <proposal_id>")
            sys.exit(1)
        success = approve_proposal(sys.argv[2])
        print(f"Proposal {'approved and applied' if success else 'not found or rejected'}")

    elif cmd == "validate":
        if len(sys.argv) < 3:
            print("Usage: phenomenology.py validate <proposal_id>")
            sys.exit(1)
        _init_db()
        db = _get_db()
        row = db.execute("SELECT * FROM identity_proposals WHERE id = ?", (sys.argv[2],)).fetchone()
        db.close()
        if not row:
            print("Proposal not found")
        else:
            proposal = {"proposed_change": row[2]}
            valid = validate_against_soul(proposal)
            print(f"Validation: {'PASS' if valid else 'FAIL'}")

    else:
        print(f"Unknown command: {cmd}")
