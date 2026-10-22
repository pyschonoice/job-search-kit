#!/usr/bin/env bash
# Render an HTML card to PNG with headless Chromium.
# Usage: render.sh <file.html> [width=1080] [height=1350] [out.png]
set -euo pipefail

html="$1"; w="${2:-1080}"; h="${3:-1350}"
out="${4:-${html%.html}.png}"
[ -f "$html" ] || { echo "no such file: $html" >&2; exit 1; }

abs() { (cd "$(dirname "$1")" && echo "$PWD/$(basename "$1")"); }
html="$(abs "$html")"; out="$(cd "$(dirname "$out")" && echo "$PWD")/$(basename "$out")"

# Prefer Playwright's Chromium, then Google Chrome.
chrome="$(find "$HOME/Library/Caches/ms-playwright" -type f -path '*chrome-mac*/Contents/MacOS/*' 2>/dev/null | sort -r | head -1 || true)"
[ -n "$chrome" ] || chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$chrome" ] || { echo "no Chromium found; run: npx playwright install chromium" >&2; exit 1; }

"$chrome" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --virtual-time-budget=3000 --window-size="$w,$h" --screenshot="$out" "file://$html" >/dev/null 2>&1

[ -s "$out" ] || { echo "render failed: $out" >&2; exit 1; }
echo "$out"
