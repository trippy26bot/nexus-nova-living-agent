#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: scanner/secure_install.sh <skill_dir> [min_score]"
  exit 1
fi

SKILL_DIR="$1"
MIN_SCORE="${2:-80}"

python3 scanner/skill_scanner.py "$SKILL_DIR" --min-score "$MIN_SCORE" --fail-on-high

echo "Scan passed. Proceeding with install workflow for: $SKILL_DIR"
# Hook your OpenClaw install command here.
# Example:
# openclaw skill install "$SKILL_DIR"
