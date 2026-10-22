# Job Search Kit

A job-search workspace for [Claude Code](https://claude.com/claude-code) (terminal or the VS Code extension). It finds postings, tailors an ATS-safe LaTeX resume to each job, scores it, fills application forms, drafts personal cold emails, reads your inbox for what needs action, and keeps one tracker of everything.

**You stay in control.** By default Claude never clicks Submit, never sends an email (it saves Gmail drafts), never publishes a post, and never adds a claim to your resume without asking you.

## What is inside

| Skill | What it does |
|---|---|
| `job-setup` | Guided onboarding inside Claude: **quick** (about 5 minutes) or **full** (10 stages), resumable, plus a **doctor** check |
| `my-profile` | Your verified career facts: the single source for everything written about you |
| `tailor-resume` | JD in, one-page ATS-safe LaTeX resume out (validated, compiled, named) |
| `ats-check` | Reads the PDF like an ATS, fixes parse faults, scores keyword coverage, asks before adding any keyword |
| `apply-job` | Link + JD in: resume, ATS score, form filled, stopped before Submit |
| `fill-form` + `portal-apply` | Saved answers and tested playbooks for LinkedIn Easy Apply, Workday, Greenhouse, Ashby, Lever, Wellfound, Zoho, Keka, Darwinbox, Google Forms and more |
| `job-hunt` | Daily hunt across LinkedIn, company boards, HN, Reddit, YC and more; filters for fit; gets applications ready |
| `career-ops` | Zero-token board scanner, liveness and repost checks (vendored, MIT) |
| `research-target` + `cold-email` | Researches a company and person, writes a short email in your voice, saves a Gmail draft |
| `job-inbox` | Reads Gmail for recruiter mail, interviews, rejections; owns the tracker |
| `linkedin-post` + `linkedin-posts` | Finds hiring posts to act on; drafts your own posts and images (never publishes) |
| `funded-startups` | Turns a funding-news list into researched outreach leads |
| `interview-prep` + `study` | Interview prep packs and a DSA / system design study tracker (Obsidian-friendly) |
| `orchestrator` + `browser-worker` | Runs independent tasks in parallel, one browser tab each |
| `update-skills` | End-of-session upkeep so the next session never re-learns anything |

## Install

You need [Claude Code](https://claude.com/claude-code). Then:

```bash
unzip job-search-kit-*.zip && cd job-search-kit      # or: git clone this repo
./install.sh                    # creates ~/job-search   (or: ./install.sh ~/my-folder)
```

Then open the new folder in Claude Code:

- **Terminal:** `cd ~/job-search && claude`
- **VS Code:** File > Open Folder > `job-search`, then open the Claude Code panel

Type **`/job-setup`** and pick quick or full. That is the whole setup.

### Quick vs full

| | Quick (`/job-setup quick`) | Full (`/job-setup full`) |
|---|---|---|
| Time | about 5 minutes | 20 to 30 minutes |
| Identity and contact | yes | yes |
| Resume import into a verified profile | light | thorough, metric by metric |
| Safe working rules | defaults | you choose each one |
| Job targets and search config | later | yes |
| Pay, notice and form answers | later | yes |
| Writing voice and email signature | later | yes |
| Gmail, browser sign-ins, portal accounts | later | yes |
| Git and private GitHub sync | local git only | local or private remote, optional auto-sync |
| Tooling install and dry run | check only | check, install, dry run on one real job |

Stages can be skipped and resumed any time (`/job-setup` picks up where you stopped; `/job-setup voice` re-runs one stage).

### Update to a new kit version

```bash
./install.sh ~/job-search --update
```

Skills, agents and tools are refreshed; your personal files (`my-profile`, `answers.md`, `voice.md`, search config) are kept, and the old skills are backed up first.

## What it needs

| Tool | For | Required? |
|---|---|---|
| Claude Code | everything | yes |
| Node 18+ and Python 3.9+ | scanners, tracker, scripts | yes |
| [tectonic](https://tectonic-typesetting.github.io) | compiling LaTeX resumes | recommended |
| Playwright MCP | filling forms, scraping boards | recommended |
| Gmail connector | inbox reading, email drafts | recommended |
| `gh` (GitHub CLI) | optional private sync of your workspace | optional |
| macOS Xcode tools or `poppler-utils` | the ATS PDF check | recommended |

`/job-setup` stage 9 checks all of these and shows the install command for anything missing. It never runs `sudo`.

## Privacy

- Everything about you lives in files inside **your** workspace folder. The kit contains no personal data.
- Keep your workspace **private**. If you sync it to GitHub, `/job-setup` only offers a private repo.
- Passwords go in `.secrets/` (gitignored), nowhere else.
- Some portal playbooks and filters assume job boards common in India and the US. Edit `job-hunt/references/search.json` and `career-ops/root/portals.yml` for your region (stage 3 does this with you).

## Repository layout

```
install.sh            installer (create / --update)
kit/skills/           the skills
kit/agents/           browser-worker subagent
kit/tools/career-ops/ vendored scanners (MIT, see NOTICE.md)
kit/templates/        workspace files: CLAUDE.md, tracker, .gitignore, sync script, resume template
scripts/release.sh    maintainer: audit, zip, tag, GitHub release
```

## Contributing

This repo is read-only for others. Fork it and make it yours; pull requests and issues are not monitored.

## License

MIT. See `LICENSE` and `NOTICE.md`.
