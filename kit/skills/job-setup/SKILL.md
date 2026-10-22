---
name: job-setup
description: Onboarding and setup for this job-search workspace. Runs inside Claude Code (terminal or VS Code). "quick" gets the user applying in about 5 minutes (identity, resume import, safe defaults, local git). "full" is the complete guided onboarding in stages (identity, career profile, job targets, pay answers, working rules, writing voice, accounts, git and GitHub sync, tooling, dry run). "doctor" re-checks everything and reports what is missing. Resumable. Use when the user says "/job-setup", "set me up", "onboard me", "continue setup", "setup doctor", or when any other skill finds a blank template (`<...>` placeholders) in my-profile, answers.md or voice.md.
---

# Job setup

Turns this blank workspace into the user's own. Everything personal lives in files **inside the workspace**; the skills only read them. Never invent an answer: ask, then write it down.

## Modes

| Command | What it does |
|---|---|
| `/job-setup` | No state yet: ask which mode (quick or full). State exists: resume where it stopped. |
| `/job-setup quick` | Stages 0, 1, 2, 5 (defaults), 8 (local git only), 9 (check). About 5 minutes. Ends with a list of what full setup would still add. |
| `/job-setup full` | All stages 0 to 10 in order. Skippable and resumable. 20 to 30 minutes. |
| `/job-setup doctor` | Re-run stage 9 and a placeholder scan. Report only; fix on request. |
| `/job-setup <stage>` | Re-run one stage (e.g. `/job-setup voice`). |

## How to run it (rules for you)

1. **Read `setup-state.json`** at the workspace root first (create it if missing, see `references/state.md`). Tell the user in one line where they are ("Stage 3 of 10: job targets").
2. **Ask in batches.** Choices go through AskUserQuestion (max 4 questions per call, recommended option first). Free text (name, phone, address, links) is asked in one plain chat message listing the fields; wait for the reply. Never ask one field per turn.
3. **Never assume.** If the user skips a question, write `<ask>` in that spot, not a guess. Mark the stage `skipped` or `partial` in the state file.
4. **Write files as you go**, then update `setup-state.json` (stage status + date). The user can quit any time and `/job-setup` resumes.
5. **Show, then save.** After each stage, show a 3 to 6 line summary of what you wrote and where. Ask only if something needs a decision.
6. **Secrets** (passwords, OTPs, tokens) only go into `.secrets/` (gitignored). Never into skills, CLAUDE.md, the tracker or commits.
7. **Nothing leaves the machine** without a yes: no GitHub repo creation, no email, no form submit during setup.
8. Stage details, questions and exact target files are in `references/stages.md`. Tooling checks are in `references/tooling.md`. Working-rule options are in `references/rules.md`.

## Stages (full mode)

| # | Stage | Writes |
|---|---|---|
| 0 | Preflight: workspace folder, OS, Claude Code surface (terminal / VS Code), existing files | `setup-state.json` |
| 1 | Identity and contact | `my-profile`, `fill-form/references/answers.md`, `portal-apply/scripts/profile.json` |
| 2 | Resume import and career profile | `my-profile`, `main_resume/<variant>/main.tex` |
| 3 | Job targets and search | `job-hunt/references/search.json`, `career-ops/root/portals.yml`, `my-profile` (targets) |
| 4 | Pay, notice and availability answers | `answers.md`, `profile.json` |
| 5 | Working rules | workspace `CLAUDE.md` |
| 6 | Writing voice and email signature | `cold-email/references/voice.md` |
| 7 | Accounts and connections | `.secrets/portal-logins.md`, Gmail and Playwright checks |
| 8 | Git and GitHub sync | local repo, `.gitignore`, optional private remote, optional sync hooks |
| 9 | Tooling check and install | npm, LaTeX engine, Playwright, career-ops deps |
| 10 | Dry run on one sample job | an `applications/<company>_<role>/` folder, nothing submitted |

## Finish

End every run with: what is done, what was skipped, the one command to try next (`/job-hunt`, `apply this: <link>`, or `tailor a resume for this JD`), and the reminder that the user stays in control of every submit and send. Then run `update-skills`.
