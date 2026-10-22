---
name: tailor-resume
description: Build a one-page LaTeX resume for the user tailored to a specific job description. It maps the JD to their verified experience, writes applications/<company>_<role>/main.tex, validates it (1 page, no overflow, no unescaped LaTeX characters, no ATS parse faults), compiles it to a named PDF, and then always runs the ats-check skill to score keywords and ask the user about gaps. Use when the user pastes a JD, names a company or role to apply for, or asks to update or rebuild one of their tailored resumes.
---

# Tailor a resume to a JD

When the user pastes a JD **and** an application link, the `apply-job` skill runs this one as its first step, then fills the form.

## Layout

```
<workspace>/
├── main_resume/
│   ├── ai_engineer/main.tex        base AI Engineer resume (start here for AI/GenAI/ML JDs)
│   ├── fullstack_engineer/main.tex base Full Stack (backend-heavy) resume (start here for backend/full-stack/SDE JDs)
│   └── old/                        archived single resume, don't use
├── applications/<company>_<role>/
│   ├── main.tex                   the tailored source
│   └── First_Last_Resume_<Company>.pdf
└── .claude/skills/
    ├── my-profile/SKILL.md     all verified facts (load this first)
    ├── tailor-resume/scripts/build.sh
    ├── ats-check/                 ATS parse + keyword check (runs after every build)
    ├── fill-form/                 fills application forms from saved answers; never submits
    └── apply-job/                 orchestrator: link + JD → resume → ATS → form
```

**Each company folder holds exactly two files: `main.tex` and one PDF.** The build script enforces this. It compiles in a temp dir, deletes anything else in the folder, and leaves the preview image in temp.

Folder names are lowercase snake_case, `<company>_<role-slug>`, e.g. `deel_ai_backend` or `stripe_backend_eng`. The PDF name uses the company in its normal casing (`Deel`, `Stripe`).

## Workflow

1. **Load `my-profile`.** It is the only source of claims. Also check `applications/` for an earlier resume for a similar role; copying its `main.tex` is often the fastest start.
2. **Parse the JD** into three lists:
   - Must-haves: languages, databases, ORMs, years, domain.
   - Responsibilities, stated as themes: e.g. shipping with AI tools, end-to-end ownership, cost, security, remote collaboration.
   - Exact keywords for applicant tracking systems (e.g. "PostgreSQL", "ORM", "NodeJS", "Claude").
3. **Map each requirement to evidence** using the profile's bullet bank. For each gap, decide whether to:
   - cover it with adjacent evidence ("ORMs such as <ORM A>, <ORM B> the user has used" for an ORM the JD names but the user lacks),
   - leave it out, or
   - **ask the user** if they may have experience the profile doesn't record.
   Never invent tools, metrics, titles or dates, and never claim more years than the profile allows.
4. **Write `applications/<folder>/main.tex`**, starting from `main_resume/ai_engineer/main.tex` or `main_resume/fullstack_engineer/main.tex` (whichever fits the JD), or the closest earlier application. The base resumes already have the ATS-safe preamble; keep it.
   - **Summary:** 3–4 lines, written in the JD's language. Lead with their must-haves.
   - **Skills:** keep it above Experience. Reorder so the JD's stack comes first, and add a "Databases & ORMs" or security line when the JD emphasises them. Each category must fit one line where possible.
   - **Experience:** reverse chronological. Present <employer> as one block with the promotion. Put the most JD-relevant bullet first under each role. Bold the JD keywords and metrics, and keep metrics exactly as recorded in the profile.
   - **Projects:** default to the user's **high-priority projects** as flagged in `my-profile` (the "strongest first" order). Swap one out only when the JD clearly needs another, using the stack tags on each project in `my-profile`. Don't repeat a project already covered under Experience. Add a one-line Achievements or Open Source section only if space allows.
   - Keep the header identical to the base resume (LinkedIn is `<your LinkedIn URL>`). **No portfolio link unless `my-profile` lists one.** Only add "(Remote)" after India for remote roles.
   - Escape `% & $ # _` as `\% \& \$ \# \_`. Use `--` for date ranges and no unicode dashes.
5. **Build and validate:**
   ```bash
   .claude/skills/tailor-resume/scripts/build.sh applications/<folder> <Company>
   ```
   The script lints for unescaped characters, compiles with tectonic, requires **exactly 1 page**, fails on **overfull lines**, runs the **ATS parse gate** (`ats-check --parse-only`: hyphen-split words, ligature glyphs, missing email), writes the named PDF and prints a `preview:` PNG path.
6. **Look at the preview** with the Read tool on the printed PNG path. Check for:
   - orphan words on the last line of a bullet (tighten the bullet),
   - uneven section spacing,
   - large empty space at the bottom (room to add a bullet or an Achievements line).
7. **Fix and repeat until the script prints `OK` and the preview looks clean.** To trim for one page, in order:
   - shorten bullets that wrap by 1–2 words,
   - merge the <past employer> bullets into one,
   - cut the lowest-signal skills,
   - drop the second project's second bullet,
   - shorten the summary.
   Never shrink the margins or font below the template's.
8. **Run the `ats-check` skill (mandatory, every build).** Load it and follow its workflow on the built PDF, using the JD keyword file plus the matching role list (AI Engineer and/or Backend Engineer):
   - fix parse and structure faults;
   - strengthen thin keywords;
   - **ask the user with AskUserQuestion about every missing keyword before adding it**, then rebuild.
   Target: **ATS score 90+ and 85%+ keyword coverage** against the JD list. Below that, rebuild (the `apply-job` gate, step 3, says how).
9. **Report to the user:**
   - the PDF path,
   - what was emphasised and why,
   - JD gaps and how each was handled,
   - any claim they should verify,
   - the ATS score before and after `ats-check`, and the keywords they approved or declined.
   Then add a line for the new application under "Past applications" in `my-profile`.

## Updating the base resumes

The two base resumes are ordinary build folders, so build them with the same script:

```bash
.claude/skills/tailor-resume/scripts/build.sh main_resume/ai_engineer AI_Engineer
.claude/skills/tailor-resume/scripts/build.sh main_resume/fullstack_engineer Fullstack_Engineer
```

Then run `ats-check`: the AI resume against `ai_engineer.txt`, and the full-stack resume against `fullstack_engineer.txt` and `backend_engineer.txt`. Each must score 90+ with keyword coverage at 85% or higher. Don't touch `main_resume/old/`.

## Tooling

- `tectonic` (brew). Run the first build with network access so it can fetch LaTeX packages; later builds use the cache.
- `gh`, logged in as `<github-user>`, for looking up repos when the profile is missing something.
- If you learn a new verified fact (a new metric, job or project), update `my-profile` too.
