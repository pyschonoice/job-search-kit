# Job-search workspace

This folder is a personal job-search workspace driven by Claude Code skills in `.claude/skills/`. Run `/job-setup` once (quick or full). Everything personal lives in files here; the skills only read them.

## Where things are
- `.claude/skills/my-profile/SKILL.md` verified career facts (the single source for anything written about the user).
- `.claude/skills/fill-form/references/answers.md` every saved form answer.
- `.claude/skills/cold-email/references/voice.md` writing voice and email signature.
- `main_resume/<variant>/main.tex` base resumes; `applications/<company>_<role>/` tailored resumes (`main.tex` + one PDF).
- `tracker/applications.csv` the universal tracker (owned by the `job-inbox` skill). `hunts/`, `outreach/`, `linkedin-posts/` are outputs.
- `.secrets/` gitignored. Passwords and OTPs go here only.

## Skills (what to say)
- "apply to this: <link>" plus a JD → `apply-job` (resume, ATS check, form fill, stop before Submit).
- "daily hunt" → `job-hunt`. "check my mail" → `job-inbox`. "cold email <person/company>" → `cold-email`.
- "tailor a resume for this JD" → `tailor-resume`. "check ATS" → `ats-check`. "LinkedIn post about X" → `linkedin-post`.
- "prep me for <company>" → `interview-prep`. "let's study" → `study`.

## Working rules
<!-- /job-setup stage 5 edits this list. Safe defaults below. -->
- **Never submit a job application form.** Fill, verify, stop; the user clicks Submit.
- **Email is drafts only.** Save Gmail drafts; the user sends every email.
- **Never publish LinkedIn posts or comments** unless the user says "post it" for that specific post.
- **Ask before adding any keyword, tool or claim** that is not already in `my-profile`, even to raise an ATS score.
- **Never guess a form answer.** Ask (AskUserQuestion), then save it to `answers.md` with the date.
- **Lever forms (jobs.lever.co): do not fill.** Give the apply link and every answer in chat.
- **Never state more experience than `my-profile` says**, and never pick a higher experience band.
- **Secrets only in `.secrets/`.** Never copy a password into skills, the tracker, or a commit.
- With 2 or more independent tasks, use the `orchestrator` skill and `browser-worker` agents (one Playwright tab each); the main agent is the only writer of the tracker, `answers.md` and skills.
- Before the final report of a session, run the `update-skills` skill.
