#!/usr/bin/env bash
# Maintainer script: audit, zip, tag, push, and attach the zip to a GitHub release.
#   scripts/release.sh <version> ["release notes"]      e.g. scripts/release.sh 0.2.0 "Add interview-prep"
# The privacy blocklist lives OUTSIDE this repo (it contains the maintainer's own personal strings):
#   ~/.config/job-search-kit/blocklist.txt  (one case-insensitive pattern per line)
set -euo pipefail
cd "$(dirname "$0")/.."
VER="${1:?usage: scripts/release.sh <version> [notes]}"; NOTES="${2:-Release $VER}"
BL="${JSK_BLOCKLIST:-$HOME/.config/job-search-kit/blocklist.txt}"
[ -f "$BL" ] || { echo "Missing blocklist $BL: refusing to release without a privacy audit."; exit 1; }

echo "1/5 privacy audit"
if grep -rIiF -f "$BL" --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist --exclude=LICENSE . ; then
  echo "FAIL: personal strings found above. Fix them, then run again."; exit 1
fi
echo "   clean"

echo "2/5 version $VER"
echo "$VER" > VERSION

echo "3/5 zip"
mkdir -p dist
ZIP="dist/job-search-kit-$VER.zip"
rm -f "$ZIP"
git ls-files -co --exclude-standard | grep -v '^dist/' | grep -v '\.DS_Store$' > /tmp/jsk-files.$$
STAGE="$(mktemp -d)/job-search-kit"; mkdir -p "$STAGE"
while read -r f; do mkdir -p "$STAGE/$(dirname "$f")"; cp -p "$f" "$STAGE/$f"; done < /tmp/jsk-files.$$
( cd "$(dirname "$STAGE")" && zip -qr "$OLDPWD/$ZIP" job-search-kit )
rm -f /tmp/jsk-files.$$
echo "   $ZIP ($(du -h "$ZIP" | cut -f1))"

echo "4/5 commit, tag, push"
git add -A
git diff --cached --quiet || git commit -q -m "release $VER"
git tag -f "v$VER" -m "$VER"
git push -q origin main
git push -q -f origin "v$VER"

echo "5/5 GitHub release"
if gh release view "v$VER" >/dev/null 2>&1; then
  gh release upload "v$VER" "$ZIP" --clobber
else
  gh release create "v$VER" "$ZIP" --title "Job Search Kit $VER" --notes "$NOTES"
fi
echo "done: $(gh release view "v$VER" --json url -q .url)"
