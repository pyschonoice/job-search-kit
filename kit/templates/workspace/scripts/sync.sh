#!/usr/bin/env bash
# Commit everything, pull (rebase), push. Safe to run often; no-op when clean or when there is no remote.
# Usage: scripts/sync.sh [pull]   ("pull" = only pull, used at session start)
set -u
cd "$(dirname "$0")/.." || exit 0
git remote get-url origin >/dev/null 2>&1 || { echo "sync: no remote set (see /job-setup stage 8)"; exit 0; }
LOCK=.git/sync.lock
mkdir "$LOCK" 2>/dev/null || { [ -n "$(find "$LOCK" -mmin +5 2>/dev/null)" ] && rm -rf "$LOCK" && mkdir "$LOCK"; } || exit 0
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

if [ "${1:-}" = "pull" ]; then
  git pull --rebase --autostash -q 2>&1 | tail -3
  exit 0
fi

git add -A
if ! git diff --cached --quiet; then
  git commit -q -m "sync: $(hostname -s) $(date '+%Y-%m-%d %H:%M')"
fi
git pull --rebase --autostash -q || { echo "sync: pull/rebase conflict, fix manually"; git rebase --abort 2>/dev/null; exit 0; }
git push -q 2>&1 | tail -3
