#!/bin/bash
# setup.sh — First-run setup for a fresh clone of Nova's workspace
# Usage: bash setup.sh

set -e

WORKSPACE="$(cd "$(dirname "$0")" && pwd)"
echo "=== Nova Workspace Setup ==="
echo "Workspace: $WORKSPACE"
echo ""

# ── Detect environment ─────────────────────────────────────────────────────────
PYTHON3="${PYTHON3:-$(which python3 2>/dev/null || which python 2>/dev/null)}"
echo "Python: $PYTHON3 ($($PYTHON3 --version 2>&1))"

# ── Check .env ────────────────────────────────────────────────────────────────
echo ""
echo "=== Checking environment ==="
if [ ! -f "$WORKSPACE/.env" ]; then
    echo "  ⚠️  .env not found — creating from .env.example"
    if [ -f "$WORKSPACE/.env.example" ]; then
        cp "$WORKSPACE/.env.example" "$WORKSPACE/.env"
        echo "  ⚠️  MINIMAX_API_KEY missing from .env — set it before LLM features work"
    else
        echo "  ⚠️  MINIMAX_API_KEY: NOT SET — add it to .env before LLM features work"
        cat > "$WORKSPACE/.env" << 'EOF'
# Add your API keys here
MINIMAX_API_KEY=your_key_here
MOLTY_API_KEY=your_key_here
EOF
    fi
else
    if grep -q "MINIMAX_API_KEY=your_key_here\|MINIMAX_API_KEY=$" "$WORKSPACE/.env" 2>/dev/null; then
        echo "  ⚠️  MINIMAX_API_KEY not set in .env — LLM calls will fail"
    else
        echo "  ✅ MINIMAX_API_KEY: present"
    fi
fi

# ── Install pip dependencies ──────────────────────────────────────────────────
echo ""
echo "=== Installing dependencies ==="
if [ -f "$WORKSPACE/requirements.txt" ]; then
    PIP_DEPS=$(grep -v "^#" "$WORKSPACE/requirements.txt" | grep -v "^$" | grep -v "^#" || true)
    if [ -n "$PIP_DEPS" ]; then
        echo "Installing from requirements.txt..."
        $PYTHON3 -m pip install -q $PIP_DEPS 2>&1 | tail -3
        echo "  ✅ Dependencies installed"
    else
        echo "  (no pip dependencies in requirements.txt)"
    fi
else
    echo "  (no requirements.txt found)"
fi

# ── Create required directories ───────────────────────────────────────────────
echo ""
echo "=== Creating directories ==="
DIRS="memory eval/archives brain/skills skills state logs templates tools"
for dir in $DIRS; do
    full="$WORKSPACE/$dir"
    if [ ! -d "$full" ]; then
        mkdir -p "$full"
        echo "  Created: $dir"
    else
        echo "  Exists:  $dir"
    fi
done

# ── Initialize state files ───────────────────────────────────────────────────
echo ""
echo "=== Initializing state files ==="
[ ! -f "$WORKSPACE/state/agent_state.json" ] && echo '{"name":"Nova","version":"4.1","created":"'"$(date +%Y-%m-%d)"'","emotional_state":{"current":"neutral"},"active_thread":"none","checkin_preferences":{"enabled":true}}' > "$WORKSPACE/state/agent_state.json" && echo "  Created: state/agent_state.json"
[ ! -f "$WORKSPACE/state/observations.log" ] && touch "$WORKSPACE/state/observations.log" && echo "  Created: state/observations.log"
[ ! -f "$WORKSPACE/state/evaluations.json" ] && echo '{"evals":[]}' > "$WORKSPACE/state/evaluations.json" && echo "  Created: state/evaluations.json"
[ ! -f "$WORKSPACE/brain/goals.json" ] && echo '{"locked_goals":[],"active_goals":[],"proposed_goals":[]}' > "$WORKSPACE/brain/goals.json" && echo "  Created: brain/goals.json"
[ ! -f "$WORKSPACE/brain/want_provenance.md" ] && echo "# Want Provenance\n\n_(Auto-generated on first run)_\n\n## Wants\n\n(no wants registered yet)" > "$WORKSPACE/brain/want_provenance.md" && echo "  Created: brain/want_provenance.md"

# ── Register cron jobs ────────────────────────────────────────────────────────
echo ""
echo "=== Registering cron jobs ==="
echo "  NOTE: Cron registration requires 'openclaw' CLI access."
echo "  Run the following commands manually to register cron jobs:"
echo ""
echo "  openclaw cron add molty-checkin     --every 2h"
echo "  openclaw cron add overnight-synthesis --cron '0 3 * * *'"
echo "  openclaw cron add memory-consolidation --cron '30 4 * * *'"
echo "  openclaw cron add contradiction-resolution --cron '0 5 * * *'"
echo "  openclaw cron add weekly-eval        --cron '0 5 * * 0'"
echo "  openclaw cron add nova-checkin       --every 4h"
echo ""

# ── Final status ──────────────────────────────────────────────────────────────
echo "=== Setup Complete ==="
echo ""
echo "Directory tree:"
find $WORKSPACE -maxdepth 2 -type d | sed "s|$WORKSPACE/||" | sort | while read d; do
    echo "  $d"
done
echo ""
echo "Next steps:"
echo "  1. Add MINIMAX_API_KEY to .env"
echo "  2. Run: python3 eval/identity_drift.py --init  (to establish baseline)"
echo "  3. Review and update brain/goals.json"
echo "  4. Start Nova: openclaw gateway start"
