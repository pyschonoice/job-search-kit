# Tooling check

Run these and print one table: tool, status, install command. Skip what the user's chosen stages do not need.

| Tool | Check | Needed for | Install |
|---|---|---|---|
| Claude Code | already running | everything | https://claude.com/claude-code |
| git | `git --version` | stage 8 | macOS: `xcode-select --install`; Linux: `apt install git` |
| gh (GitHub CLI) | `gh auth status` | optional private sync | `brew install gh` / https://cli.github.com, then `gh auth login` |
| Node 18+ | `node -v` | career-ops scripts, Playwright | `brew install node` / https://nodejs.org |
| Python 3.9+ | `python3 -V` | tracker, hunt, ats-check | `brew install python` / `apt install python3` |
| tectonic | `tectonic --version` | compiling LaTeX resumes (`tailor-resume/scripts/build.sh`) | `brew install tectonic` / `cargo install tectonic` / https://tectonic-typesetting.github.io |
| PDF text reader | macOS: `swiftc --version` (Xcode CLT); Linux: `pdftotext -v` | `ats-check` | macOS: `xcode-select --install`; Linux: `apt install poppler-utils` |
| Playwright MCP | tools named `mcp__playwright__*` exist | form filling, scraping | `claude mcp add playwright -- npx -y @playwright/mcp@latest` |
| Gmail connector | `/mcp` lists a Gmail server, or tools named `mcp__*Gmail*` exist | `job-inbox`, email drafts | connect Gmail in Claude settings (Connectors) |
| career-ops deps | `tools/career-ops/node_modules` exists | `career-ops` skill, `job-hunt` board scan | `cd tools/career-ops && npm install --no-audit --no-fund` |

Rules: never run `sudo`. Offer to run non-sudo installs and wait for a yes. If a tool is missing, the dependent skill still works in a reduced way (for example no LaTeX engine: tailor-resume writes `main.tex` and the user compiles elsewhere).
