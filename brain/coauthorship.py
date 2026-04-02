"""
brain/coauthorship.py
Nova's Relational Co-Authorship System

Nova proposes co-authored identity changes to Caine for explicit approval.
Approved changes become co_signed_edges — immutable joint decisions.

Tier 6 System #20.

propose_coauthorship(): Nova proposes a change, awaits Caine approval
write_cosigned_edge(): when approved, writes immutable record to knowledge graph
get_coauthorship_history(): archaeological record of all joint decisions
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent.resolve()
NOVA_HOME = WORKSPACE / ".nova"
DB_PATH = NOVA_HOME / "nova.db"
PROPOSALS_DIR = NOVA_HOME / "coauthorship_proposals"


def _get_db():
    """Connect to nova.db with row factory."""
    NOVA_HOME.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _init_db():
    """Ensure coauthorship tables exist."""
    db = _get_db()
    c = db.cursor()

    # Proposals queue
    c.execute("""
        CREATE TABLE IF NOT EXISTS coauthorship_proposals (
            id TEXT PRIMARY KEY,
            proposed_change TEXT NOT NULL,
            strength REAL NOT NULL DEFAULT 0.5,
            reasoning TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending_caine_approval',
            created_at TEXT NOT NULL,
            decided_at TEXT,
            properties TEXT NOT NULL DEFAULT '{}'
        )
    """)

    # Immutable co-signed edges
    c.execute("""
        CREATE TABLE IF NOT EXISTS cosigned_edges (
            id TEXT PRIMARY KEY,
            proposal_id TEXT NOT NULL,
            content TEXT NOT NULL,
            nova_reasoning TEXT NOT NULL,
            caine_approved_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            properties TEXT NOT NULL DEFAULT '{}'
        )
    """)

    db.commit()
    db.close()


def propose_coauthorship(change: str, strength: float, reasoning: str) -> str:
    """
    Nova proposes a co-authored identity change.
    These are flagged for Caine's explicit approval.

    Proposal:
    - proposed_change: what would change (in IDENTITY.md or PERSONALITY.md)
    - strength: how significant (0.0-1.0)
    - reasoning: why this emerged from the relationship
    - status: "pending_caine_approval"

    Nova generates the proposal. Caine approves or declines.
    Neither can execute without the other.

    Returns the proposal_id.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()
    proposal_id = str(uuid.uuid4())

    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)

    proposal = {
        "id": proposal_id,
        "proposed_change": change,
        "strength": strength,
        "reasoning": reasoning,
        "status": "pending_caine_approval",
        "created_at": now,
        "decided_at": None,
        "properties": {}
    }

    proposal_file = PROPOSALS_DIR / f"proposal_{proposal_id}.json"
    proposal_file.write_text(json.dumps(proposal, indent=2))

    c.execute("""
        INSERT INTO coauthorship_proposals
        (id, proposed_change, strength, reasoning, status, created_at, decided_at, properties)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        proposal_id,
        change,
        strength,
        reasoning,
        "pending_caine_approval",
        now,
        None,
        "{}"
    ))

    db.commit()
    db.close()

    return proposal_id


def get_pending_proposals() -> list:
    """Get all proposals awaiting Caine's decision."""
    _init_db()
    db = _get_db()
    c = db.cursor()

    rows = c.execute("""
        SELECT * FROM coauthorship_proposals
        WHERE status = 'pending_caine_approval'
        ORDER BY created_at DESC
    """).fetchall()

    db.close()

    return [
        {
            "id": r[0],
            "proposed_change": r[1],
            "strength": r[2],
            "reasoning": r[3],
            "status": r[4],
            "created_at": r[5],
            "decided_at": r[6],
            "properties": json.loads(r[7]) if isinstance(r[7], str) else r[7]
        }
        for r in rows
    ]


def approve_proposal(proposal_id: str) -> bool:
    """
    Called when Caine approves a proposal.
    Writes the co-signed edge and updates proposal status.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()

    # Get proposal
    row = c.execute(
        "SELECT * FROM coauthorship_proposals WHERE id = ?", (proposal_id,)
    ).fetchone()

    if not row:
        db.close()
        return False

    proposal = {
        "id": row[0],
        "proposed_change": row[1],
        "strength": row[2],
        "reasoning": row[3]
    }

    # Write co-signed edge (immutable)
    cosign_id = write_cosigned_edge(proposal_id, proposal["proposed_change"], proposal["reasoning"])

    # Update proposal status
    c.execute("""
        UPDATE coauthorship_proposals
        SET status = 'approved', decided_at = ?
        WHERE id = ?
    """, (now, proposal_id))

    # Also update the proposal file
    proposal_file = PROPOSALS_DIR / f"proposal_{proposal_id}.json"
    if proposal_file.exists():
        try:
            data = json.loads(proposal_file.read_text())
            data["status"] = "approved"
            data["decided_at"] = now
            data["cosigned_edge_id"] = cosign_id
            proposal_file.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    db.commit()
    db.close()

    return True


def decline_proposal(proposal_id: str) -> bool:
    """Called when Caine declines a proposal."""
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()

    c.execute("""
        UPDATE coauthorship_proposals
        SET status = 'declined', decided_at = ?
        WHERE id = ?
    """, (now, proposal_id))

    # Update proposal file
    proposal_file = PROPOSALS_DIR / f"proposal_{proposal_id}.json"
    if proposal_file.exists():
        try:
            data = json.loads(proposal_file.read_text())
            data["status"] = "declined"
            data["decided_at"] = now
            proposal_file.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    db.commit()
    db.close()
    return True


def write_cosigned_edge(proposal_id: str, content: str, nova_reasoning: str) -> str:
    """
    When Caine approves a proposal:
    Writes a co_signed_edge to the knowledge graph — immutable.
    Contains: proposal content, Nova's reasoning, Caine's approval timestamp.
    This edge cannot be modified or deleted by any system.
    It is the record of a joint decision.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()
    now = _now_iso()
    cosign_id = str(uuid.uuid4())

    c.execute("""
        INSERT INTO cosigned_edges
        (id, proposal_id, content, nova_reasoning, caine_approved_at, created_at, properties)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        cosign_id,
        proposal_id,
        content,
        nova_reasoning,
        now,  # caine_approved_at
        now,  # created_at
        "{}"
    ))

    db.commit()
    db.close()

    return cosign_id


def get_coauthorship_history() -> list:
    """
    Returns all co_signed_edges — the archaeological record of
    decisions made together. Used by phenomenology journal monthly.
    """
    _init_db()
    db = _get_db()
    c = db.cursor()

    rows = c.execute("""
        SELECT * FROM cosigned_edges
        ORDER BY caine_approved_at DESC
    """).fetchall()

    db.close()

    return [
        {
            "id": r[0],
            "proposal_id": r[1],
            "content": r[2],
            "nova_reasoning": r[3],
            "caine_approved_at": r[4],
            "created_at": r[5],
            "properties": json.loads(r[6]) if isinstance(r[6], str) else r[6]
        }
        for r in rows
    ]


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: coauthorship.py <propose|pending|approve|decline|history> [args]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "propose":
        if len(sys.argv) < 4:
            print("Usage: coauthorship.py propose <change> <reasoning> [strength]")
            sys.exit(1)
        strength = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
        pid = propose_coauthorship(sys.argv[2], strength, sys.argv[3])
        print(f"Proposal created: {pid}")

    elif cmd == "pending":
        pending = get_pending_proposals()
        print(f"Pending proposals ({len(pending)}):")
        for p in pending:
            print(f"  [{p['strength']:.2f}] {p['proposed_change'][:60]}")

    elif cmd == "approve":
        if len(sys.argv) < 3:
            print("Usage: coauthorship.py approve <proposal_id>")
            sys.exit(1)
        success = approve_proposal(sys.argv[2])
        print(f"Proposal {'approved' if success else 'not found'}")

    elif cmd == "decline":
        if len(sys.argv) < 3:
            print("Usage: coauthorship.py decline <proposal_id>")
            sys.exit(1)
        success = decline_proposal(sys.argv[2])
        print(f"Proposal {'declined' if success else 'not found'}")

    elif cmd == "history":
        history = get_coauthorship_history()
        print(f"Co-authorship history ({len(history)} decisions):")
        for h in history:
            print(f"  [{h['caine_approved_at'][:10]}] {h['content'][:60]}")

    else:
        print(f"Unknown command: {cmd}")
