#!/usr/bin/env bash
# Run a vendored career-ops script against the user's config.
#   co.sh <script> [args...]     e.g. co.sh scan --json --quiet --since 7
# <script> is a file in tools/career-ops without .mjs (scan, check-liveness, detect-reposts,
# verify-portals, scan-hn, company-funded, keyword-match, jd-skill-gap, ...).
set -euo pipefail
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$SKILL/../../.." && pwd)"
CO="$REPO/tools/career-ops"
[ $# -ge 1 ] || { echo "usage: co.sh <script> [args...]" >&2; exit 64; }
script="$1"; shift
[ -f "$CO/$script.mjs" ] || { echo "no such script: tools/career-ops/$script.mjs" >&2; exit 64; }
[ -d "$CO/node_modules" ] || (cd "$CO" && npm install --no-audit --no-fund >&2)
export CAREER_OPS_ROOT="$SKILL/root"
mkdir -p "$CAREER_OPS_ROOT/data"
cd "$CAREER_OPS_ROOT"   # career-ops writes its state files into the cwd/root, never into the repo root
exec node "$CO/$script.mjs" "$@"
