#!/usr/bin/env bash
# Validate and compile a tailored resume.
# Usage: build.sh <application-folder> <CompanyName>
#   e.g. build.sh applications/deel_ai_backend Deel
# The folder ends up holding exactly two files: main.tex and <First_Last>_Resume_<CompanyName>.pdf.
# Build artifacts and the preview image go to a temp dir (path printed as "preview:").
set -uo pipefail

dir="${1:?usage: build.sh <application-folder> <CompanyName>}"
company="${2:?usage: build.sh <application-folder> <CompanyName>}"
tex="$dir/main.tex"
[[ -f "$tex" ]] || { echo "FAIL: $tex not found"; exit 1; }
command -v tectonic >/dev/null || { echo "FAIL: tectonic not installed (brew install tectonic)"; exit 1; }

work=$(mktemp -d "${TMPDIR:-/tmp}/resume_build.XXXXXX")
fail=0

# 1. Pre-compile lint: characters LaTeX silently eats or chokes on.
#    An unescaped % comments out the rest of the line (drops text with no error).
body=$(sed -n '/\\begin{document}/,/\\end{document}/p' "$tex" | grep -v '^[[:space:]]*%')
if echo "$body" | grep -nE '[^\\]%'; then
  echo "FAIL: unescaped % above (use \\%)"; fail=1
fi
if echo "$body" | grep -nE '[^\\]&'; then
  echo "FAIL: unescaped & above (use \\&)"; fail=1
fi
if echo "$body" | grep -nE '[^\\]\$[0-9]'; then
  echo "WARN: possible unescaped \$ above (use \\\$)"
fi
if echo "$body" | grep -nE '—|–'; then
  echo "WARN: unicode dash above; prefer -- or ---"
fi
# Dead links hurt. Put a regex of links that must never appear (an offline portfolio, an old
# domain) in .banned-links at the workspace root, one pattern per line. Optional.
if [[ -f .banned-links ]] && echo "$body" | grep -nEf .banned-links; then
  echo "FAIL: banned link above (see .banned-links)"; fail=1
fi
[[ $fail == 0 ]] || { rm -rf "$work"; exit 1; }

# 2. Compile in the temp dir so no .log/.aux/.pdf leftovers land in the folder.
cp "$tex" "$work/main.tex"
( cd "$work" && tectonic --keep-logs main.tex >build.out 2>&1 ) || {
  cat "$work/build.out"; echo "FAIL: compile error"; rm -rf "$work"; exit 1; }

log="$work/main.log"
pages=$(grep -oE 'Output written on main\.(pdf|xdv) \([0-9]+ page' "$log" | grep -oE '[0-9]+ page' | grep -oE '[0-9]+')
echo "pages: ${pages:-?}"
[[ "${pages:-0}" == "1" ]] || { echo "FAIL: resume must be exactly 1 page"; fail=1; }

# 3. Overfull boxes = text running into the margin.
if grep -q 'Overfull \\hbox' "$log"; then
  grep -A1 'Overfull \\hbox' "$log" | head -20
  echo "FAIL: overfull line(s) above"; fail=1
fi

# 3b. ATS parse gate: hyphen-split words, ligature glyphs, missing email, page count.
ats="$(dirname "$0")/../../ats-check/scripts/ats_check.py"
if [[ -f "$ats" ]]; then
  python3 "$ats" "$work/main.pdf" --parse-only || { echo "FAIL: ATS parse faults above (see ats-check skill)"; fail=1; }
fi

# 4. Preview image of page 1 (stays in temp) for a visual check.
command -v qlmanage >/dev/null && qlmanage -t -s 1600 -o "$work" "$work/main.pdf" >/dev/null 2>&1 && echo "preview: $work/main.pdf.png"

# 5. Deliver: exactly main.tex + one named PDF in the folder.
# File name prefix: First_Last from portal-apply/scripts/profile.json (written by /job-setup).
prof="$(cd "$(dirname "$0")/../.." && pwd)/portal-apply/scripts/profile.json"
name=$(python3 -c "import json,sys;d=json.load(open('$prof'));print((d['first']+'_'+d['last']).replace(' ','_') if d.get('first') else 'Resume')" 2>/dev/null || echo Resume)
out="$dir/${name}_Resume_${company}.pdf"
find "$dir" -maxdepth 1 -type f ! -name main.tex -delete
cp -f "$work/main.pdf" "$out"

[[ $fail == 0 ]] && echo "OK: $out" || exit 1
