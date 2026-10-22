---
name: my-profile
description: The user's verified career knowledge base (contact details, every job and internship, every project with stack, metrics and evidence, skills inventory, pre-written bullet bank). Filled in by /job-setup. Load this whenever writing or tailoring a resume, cover letter, LinkedIn text or interview prep, or answering "what have I built / what can I claim".
---

# Career profile

This file is the source of truth for anything written about the user. **Never invent metrics, employers, dates or tools.** If a JD needs something that is not here, ask the user instead of guessing. `/job-setup` creates this file from the user's resume and answers; keep it current with `update-skills`.

> SETUP STATE: this is the blank template. If the sections below still contain `<...>` placeholders, run `/job-setup` first.

Last verified: <YYYY-MM-DD>

## Git identities
<Optional. If the user commits from more than one git profile, list them here and say whether other author names in their repos are theirs.>

## Contact (header)
- Name: <Full Name>
- Phone: <+CC-number>
- Resume email: <email used on resumes> (account email, if different: <email>, don't put it on a resume unless asked)
- LinkedIn: <url>
- GitHub: <url>
- Location: <city, country>. Work mode: <remote / hybrid / onsite>
- Portfolio / site: <url or "none, never use one">
- Other links (not normally on the resume): <X, blog, YouTube, ...>

## Application forms
Reusable form answers (pay, notice period, address, work authorization) live in `fill-form/references/answers.md`, the single source for anything typed into a job application form.

## Education
- <Degree>, <College>, <MM/YYYY – MM/YYYY>, <GPA>.

## Achievements / hackathons / certifications
- <Name, placement, event, date, one line on what was built.>

## Experience timeline (reverse chronological)
Total professional experience: **<N years M months>** (as of <date>). **Never claim a higher year count than this.**

### 1. <Company>, <City / Remote>
- Title: <title> (<MM/YYYY – MM/YYYY or present>)
- What the company does: <one line>
- Verified facts and metrics (copy exactly, never round up):
  - <fact + metric + evidence>
- Stack: <tools>

### 2. <Company> ...

## Projects (strongest first)

### <Project name>: <one-line description>
- Repo / live link: <url>
- Status: <live / in internal use / local only / not in production>. State exactly what is true; never claim users you don't have.
- Stack: <tools>
- Verified facts and metrics: <...>

## Skills inventory (only list what's here)
- **Languages:** <...>
- **Frameworks:** <...>
- **Data / infra:** <...>
- **AI / ML:** <...>
- **Tools:** <...>
- **Used but not strong / learning (mention only if the JD asks):** <...>
- **Not claimed:** <things the user has NOT used, so a tailored resume never lists them>

## Bullet bank by JD theme
Pick from here, then trim or reword for the JD. Metrics stay exactly as written.
- **<Theme, e.g. cost efficiency>:**
  - <bullet>

## Past applications
Base resumes: `main_resume/<variant>/`. Each tailored resume lives in `applications/<company>_<role>/`. Check it before starting a similar role; earlier resumes are good starting points. One line per application:
- `<folder>`: <Company>, <Role> (<key JD asks>). Emphasis: <what was stressed>.
