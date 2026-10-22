# Stages

Paths are relative to the workspace root. "Ask" = AskUserQuestion for choices, one chat message for free text.

## 0. Preflight
- Confirm the working directory is the workspace (it has `.claude/skills/job-setup`). If not, tell the user to open the workspace folder in Claude Code and stop.
- Detect OS (`uname`) and surface: VS Code if `$CLAUDE_CODE_ENTRYPOINT` or `$TERM_PROGRAM` mentions vscode, else terminal. Record both in the state file.
- List which template files still have `<...>` placeholders. If none do, this workspace is already set up: offer `doctor` instead.
- If personal files already exist (a resume PDF, an old tracker), ask whether to import them instead of starting blank.

## 1. Identity and contact
Ask (one chat message, all fields): full name, the email to put on resumes and forms, the account email if different, phone with country code, current city and country, full address (only if forms will need it; optional), LinkedIn URL, GitHub URL, portfolio URL (or "none"), work authorization and sponsorship needs, remote or relocation preferences, date of birth and gender **only if the user wants them saved** (some forms ask; default is to ask each time).
Write:
- `my-profile/SKILL.md` "Contact" section.
- `fill-form/references/answers.md` "Identity and contact" table.
- `portal-apply/scripts/profile.json` (`first`, `last`, `full`, `email`, `phone10`, `phone_intl`, `country_code`, `linkedin`, `github`, `address`, plus `dob` / `gender` if given).
- `.banned-links` if the user names a dead site or old domain that must never appear on a resume.

## 2. Resume import and career profile
- Ask for the current resume: a path to a PDF or .tex in the workspace, or pasted text. If none exists, interview them role by role instead (company, title, dates, what they built, one number per bullet).
- Read it. Build the `my-profile` sections: education, experience timeline (reverse chronological, dates `MM/YYYY`), projects, skills inventory, hackathons or certifications, and a first bullet bank grouped by JD theme.
- **Verify, don't polish.** For every metric, ask "is this exact and can you stand behind it?" Anything unsure goes in as `(unverified)`. Ask what they have NOT used so `my-profile` can list "Not claimed" items. Compute total experience in years and months from the dates and have them confirm.
- Ask which resume variants they need (for example "backend", "AI", "full stack"; one is fine). For each, create `main_resume/<variant>/main.tex` from `main_resume/main.tex.example` filled with their content, then run `tailor-resume/scripts/build.sh` equivalent compile and the `ats-check` skill on it. Follow `ats-check`'s rule: ask before adding any keyword.
- Write `fill-form/references/answers.md` "Experience", "Education" and "Resume to upload" sections and the `jobs` and `education` arrays in `profile.json`.

## 3. Job targets and search
Ask: target role titles (3 to 8), seniority and years of experience the user is comfortable applying to, locations and remote policy, industries they want or want to avoid, company stages (startup, scale-up, big company), must-have and deal-breaker items (night shifts, onsite days, staffing agencies), and minimum pay.
Write:
- `my-profile/SKILL.md` "Targets" section.
- `job-hunt/references/search.json`: `linkedin_queries`, `linkedin_locations` (look up the LinkedIn `geoId` by opening a LinkedIn jobs search for that city and reading the URL), `title_include`, `title_exclude`, `location_ok`.
- `career-ops/root/portals.yml` title and location filters (keep the company watchlist; remove regions the user excluded) and `career-ops/root/config/profile.yml` country and city.
- Ask for a LinkedIn saved-search URL if they have one and put it in `search.json` `saved_search`.

## 4. Pay, notice and availability answers
Ask: current pay and its breakup, expected pay, currency and unit style (LPA, annual, hourly), notice period and whether negotiable, earliest start rule ("today + N days"), whether they are serving notice, total experience wording for forms (years and months, decimal, "excluding internships" variant), English and other language levels, education marks they are happy to share, and anything they never want disclosed.
Write `answers.md` "Job and pay" and "Education" tables and the `ctc`, `notice_*`, `exp` blocks of `profile.json`. Add the rule "never pick a band above the saved experience" (already in the skills).

## 5. Working rules
Read `references/rules.md`. Show the defaults (all safe) and ask which to change, in one AskUserQuestion batch. Write the chosen rules into the workspace `CLAUDE.md` under "Working rules". Safe defaults:
never submit forms, drafts only for email, never publish posts, ask before adding keywords, Lever links only, orchestrate parallel work, run `update-skills` before finishing.

## 6. Writing voice and signature
- Ask for 2 to 5 writing samples: a blog or LinkedIn post, past emails that got replies, a README they wrote. If none, ask five style questions (short or long sentences, humor, formal or casual, words they hate, how they sign off).
- Write `cold-email/references/voice.md` from the template: how they write, how it maps to email, words to use and never use, and 2 to 3 proposed signature lines marked "not yet approved".
- Ask for the signature block and for public share links (Google Drive "anyone with the link") to each resume variant. If they have none yet, leave `<resume link>` and tell them to upload the PDFs and share them.
- Ask the LinkedIn post rules: pillars (3 topics they can speak on), emoji policy, whether the employer or clients may be named. Write `linkedin-post/references/playbook.md` pillars table and `linkedin-posts/README.md` notes.

## 7. Accounts and connections
- **Gmail**: check that a Gmail connector is available (in Claude Code run `/mcp`; in claude.ai connect Gmail). Needed for `job-inbox` and email drafts. If missing, show how to connect it; do not block.
- **Playwright browser**: check `mcp__playwright__*` tools exist. If not, give the one-line install from `references/tooling.md`. Then ask the user to sign in to LinkedIn, and to any job portals they use, in the Playwright browser window so the profile keeps the session.
- **Portal accounts**: ask whether Claude may create job-portal accounts (Workday and similar) with the user's email and one shared password. If yes, ask them to choose the password and save it in `.secrets/portal-logins.md` (gitignored). Never echo it back.
- Record choices in the state file.

## 8. Git and GitHub sync
- `git init` if there is no repo. Make sure `.gitignore` covers `.secrets/`, `.playwright-mcp/`, `node_modules/`, `setup-state.json` is allowed.
- Ask for the git identity to use here (`git config user.name/email` in this repo only). Ask whether the user commits from a second profile; if yes, note it in `my-profile` "Git identities" so no author name is treated as a stranger.
- Ask whether to sync to GitHub. If yes: **the repo must be private** (it will hold resumes, answers and contact details). Offer `gh repo create <name> --private --source=. --push` and run it only after an explicit yes. If `gh` is missing or not logged in, show `gh auth login`.
- Ask whether to enable auto-sync hooks (`scripts/sync.sh` pulls at session start and commits and pushes after each reply). Default: off. If on, merge the hooks from `templates/settings.sync.json` into `.claude/settings.json`.
- Never create or push a public repo from this skill.

## 9. Tooling check and install
Run `references/tooling.md`: report a table (tool, found or missing, how to install). Offer to run installs that are safe (npm deps for career-ops, a LaTeX engine) and show the command for anything needing sudo. Never run sudo.

## 10. Dry run
Ask for one real job link or JD. Run `tailor-resume` then `ats-check` and show the result. Do not fill any form or send any email. If the score or the profile exposes gaps, offer to go back to stage 2 or 4.
