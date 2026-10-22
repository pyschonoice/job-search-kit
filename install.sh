#!/usr/bin/env bash
# Job Search Kit installer.
#   ./install.sh [workspace-dir] [--update] [--yes]
# Default workspace: ~/job-search
#   (no flag)  fresh install; refuses to overwrite an existing workspace's skills
#   --update   refresh skills/agents/tools from this kit; keeps your personal files
#   --yes      no prompts
# Safe: never touches anything outside the workspace folder, never uses sudo, never sends data anywhere.
set -euo pipefail
KIT="$(cd "$(dirname "$0")" && pwd)"
SRC="$KIT/kit"
WS=""; UPDATE=0; YES=0
for a in "$@"; do
  case "$a" in
    --update) UPDATE=1 ;;
    --yes|-y) YES=1 ;;
    -h|--help) sed -n 2,9p "$0"; exit 0 ;;
    *) WS="$a" ;;
  esac
done
WS="${WS:-$HOME/job-search}"
case "$WS" in "~"*) WS="$HOME${WS#\~}" ;; esac
[ -d "$SRC/skills" ] || { echo "Run this from the unzipped kit folder (kit/skills not found)."; exit 1; }
VERSION="$(cat "$KIT/VERSION" 2>/dev/null || echo dev)"

# Personal files: filled in by /job-setup, never overwritten by --update.
PERSONAL="
skills/my-profile/SKILL.md
skills/fill-form/references/answers.md
skills/cold-email/references/voice.md
skills/portal-apply/scripts/profile.json
skills/job-hunt/references/search.json
skills/career-ops/root/portals.yml
skills/career-ops/root/config/profile.yml
skills/linkedin-post/references/playbook.md
"

ask() { [ "$YES" = 1 ] && return 0; read -r -p "$1 [y/N] " r; [ "$r" = y ] || [ "$r" = Y ]; }

echo "Job Search Kit $VERSION"
echo "Workspace: $WS"

if [ -d "$WS/.claude/skills" ] && [ "$UPDATE" = 0 ]; then
  echo "A workspace with skills already exists there."
  echo "Run again with --update to refresh the skills and keep your personal files."
  exit 1
fi
[ "$UPDATE" = 1 ] && [ ! -d "$WS/.claude/skills" ] && { echo "--update needs an existing workspace at $WS"; exit 1; }
[ "$UPDATE" = 1 ] || ask "Create the workspace at $WS?" || { echo "Cancelled."; exit 0; }

mkdir -p "$WS/.claude"

if [ "$UPDATE" = 1 ]; then
  STAMP="$(date +%Y%m%d-%H%M%S)"
  BAK="$WS/.claude/skills.bak.$STAMP"
  cp -R "$WS/.claude/skills" "$BAK"
  echo "Backed up current skills to $BAK"
  rm -rf "$WS/.claude/skills.new"; cp -R "$SRC/skills" "$WS/.claude/skills.new"
  for f in $PERSONAL; do
    if [ -f "$WS/.claude/$f" ]; then mkdir -p "$(dirname "$WS/.claude/skills.new/${f#skills/}")"; cp "$WS/.claude/$f" "$WS/.claude/skills.new/${f#skills/}"; fi
  done
  rm -rf "$WS/.claude/skills"; mv "$WS/.claude/skills.new" "$WS/.claude/skills"
else
  cp -R "$SRC/skills" "$WS/.claude/skills"
fi

mkdir -p "$WS/.claude/agents"; cp -R "$SRC/agents/." "$WS/.claude/agents/"
mkdir -p "$WS/tools"
if command -v rsync >/dev/null; then
  rsync -a --exclude node_modules "$SRC/tools/career-ops" "$WS/tools/"
else
  mkdir -p "$WS/tools/career-ops"; cp -R "$SRC/tools/career-ops/." "$WS/tools/career-ops/"
fi

# Workspace files (CLAUDE.md, .gitignore, tracker, folders): never overwrite existing ones.
( cd "$SRC/templates/workspace" && find . -type f ! -name settings.sync.json | while read -r f; do
    if [ ! -e "$WS/$f" ]; then mkdir -p "$WS/$(dirname "$f")"; cp "$f" "$WS/$f"; fi
  done )
mkdir -p "$WS/templates"; cp "$SRC/templates/workspace/settings.sync.json" "$WS/templates/settings.sync.json"
chmod +x "$WS/scripts/sync.sh" 2>/dev/null || true
chmod +x "$WS/.claude/skills/career-ops/scripts/co.sh" "$WS/.claude/skills/tailor-resume/scripts/build.sh" 2>/dev/null || true

if [ ! -f "$WS/setup-state.json" ]; then
cat > "$WS/setup-state.json" <<JSON
{
  "version": 1,
  "kit_version": "$VERSION",
  "mode": null,
  "started": "$(date +%Y-%m-%d)",
  "stages": {
    "0_preflight": "todo", "1_identity": "todo", "2_resume_import": "todo", "3_targets": "todo",
    "4_pay_answers": "todo", "5_rules": "todo", "6_voice": "todo", "7_accounts": "todo",
    "8_git": "todo", "9_tooling": "todo", "10_dry_run": "todo"
  },
  "choices": {}
}
JSON
else
  sed -i.bak "s/\"kit_version\": *\"[^\"]*\"/\"kit_version\": \"$VERSION\"/" "$WS/setup-state.json" 2>/dev/null && rm -f "$WS/setup-state.json.bak"
fi

if [ ! -d "$WS/.git" ]; then
  if command -v git >/dev/null && ask "Run 'git init' in the workspace (local only, nothing is pushed)?"; then
    git -C "$WS" init -q && echo "Initialized a local git repo."
  fi
fi

echo
echo "Installed. Quick tool check:"
for t in git node python3 tectonic gh; do
  if command -v "$t" >/dev/null; then echo "  ok       $t"; else echo "  missing  $t   (optional for some skills; /job-setup stage 9 explains)"; fi
done
cat <<EOF2

Next:
  1. Open the folder in Claude Code:
       Terminal:  cd "$WS" && claude
       VS Code:   File > Open Folder > $WS, then open the Claude Code panel
  2. Type  /job-setup        (quick, about 5 minutes, or full guided onboarding)
  3. Later:  /job-setup doctor   to re-check everything.

Keep the workspace private: it will hold your resume, contact details and answers.
EOF2
