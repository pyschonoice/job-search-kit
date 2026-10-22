---
name: ats-check
description: ATS parsing and keyword check for any of the user's resumes. It reads the compiled PDF the way an applicant tracking system does, fixes parse faults (hyphen-split words, ligature glyphs, non-standard headers, hidden URLs), scores keyword coverage against the target role or JD, and then ASKS the user which missing keywords they actually has before adding any. Runs after every tailor-resume build and after any edit to the base resumes in main_resume/ Also use when the user asks to "check ATS", "score my resume", "rate my resume" or "raise my ATS score".
---

# ATS check

Every resume built in this repo goes through this skill before it is reported as done: each `tailor-resume` build, each edit to the base resumes in `main_resume/ai_engineer` and `main_resume/fullstack_engineer`, and any one-off resume. The goal is two things:

1. **The parser reads exactly what the user wrote.** Formatting faults are fixed without asking.
2. **ATS score is 90+ and weighted keyword coverage is 85% or higher** (above the 75–80% industry target), without inventing anything. Every new keyword **needs the user's approval** first.

## Files

```
.claude/skills/ats-check/
├── scripts/ats_check.py      the checker (uses macOS PDFKit through pdftext.swift)
├── scripts/pdftext.swift     PDF text extractor; compiled once to $TMPDIR/ats_pdftext_bin
└── references/
    ├── ai_engineer.txt         role keyword list (core/nice tiers)
    ├── backend_engineer.txt    role keyword list
    └── fullstack_engineer.txt  full-stack list (use with backend_engineer.txt)
```

## Run it

```bash
S=.claude/skills/ats-check
python3 $S/scripts/ats_check.py <resume.pdf> \
  --keywords $S/references/ai_engineer.txt [$S/references/backend_engineer.txt] [<jd_keywords.txt>] \
  --profile .claude/skills/my-profile/SKILL.md
```

- **Choosing lists:** use the role lists that match the target, run separately so each gets its own score. `main_resume/ai_engineer` uses `ai_engineer.txt`; `main_resume/fullstack_engineer` uses `fullstack_engineer.txt` and `backend_engineer.txt`.
- **For a JD:** also write the JD's exact terms to a keyword file in the scratchpad (same `tier | keyword | aliases` format). Use `core` for must-haves and `nice` for preferred. Keep the JD's spelling ("NodeJS" if they write NodeJS). Never save it inside the application folder, because build.sh keeps only two files there.
- **`--parse-only`** runs only the parse and structure checks. `tailor-resume/scripts/build.sh` calls it automatically and fails the build on any parse FAIL.

The report has four parts: parse and structure (FAIL/WARN), quantified bullets, keyword hits with *where* each appears, and an `ATS SCORE /100`. The score is made of:
- parse: 25
- structure: 20
- quantified bullets: 15 (target 60%+ of bullets with a number)
- keywords: 40 (full marks at 85% weighted coverage)

## Workflow

### 1. Fix parse and structure faults (no approval needed)

These only change formatting, never claims.

| Fault | Fix |
|---|---|
| hyphen-split word (`scal-` + `able`) | The preamble must have `\hyphenpenalty=10000 \exhyphenpenalty=10000 \emergencystretch=3em`. If one still splits, reword the line. |
| ligature glyphs (`ﬁ ﬀ ﬃ`) | The preamble must use fontspec with `Ligatures={NoCommon,TeX}` (see the template below). `microtype`'s `\DisableLigatures` does **not** work: tectonic is XeTeX. |
| non-standard header | Use only SUMMARY, SKILLS, EXPERIENCE, PROJECTS, EDUCATION, plus ACHIEVEMENTS, OPEN SOURCE or CERTIFICATIONS. Never "Internships" or "Project Experience": internships go under Experience. |
| URL not visible | Show `<your LinkedIn URL>` and `github.com/<github-user>` as visible link text, not just the words "LinkedIn" and "GitHub". |
| unusual characters | Replace them with ASCII or `--`. |

The template preamble (already in `main_resume/ai_engineer/main.tex`; copy it into any resume that still has `fontenc`/`inputenc`):

```latex
\usepackage{fontspec}
\setmainfont{lmroman10-regular.otf}[BoldFont=lmroman10-bold.otf, ItalicFont=lmroman10-italic.otf, BoldItalicFont=lmroman10-bolditalic.otf, Ligatures={NoCommon,TeX}]
...
\hyphenpenalty=10000
\exhyphenpenalty=10000
\emergencystretch=3em
```

### 2. Strengthen keywords already on the page (no approval needed)

If a core keyword appears in only one place, move it into Skills **and** a bullet where the existing claim supports it. Examples:
- "model evaluation" is in a bullet but missing from Skills;
- "MCP" is in Skills, but the bullet doesn't say "tool calling".

This only rephrases what is already there. Also use the JD's exact spelling for things already claimed.

### 3. Ask the user about every missing keyword (approval required)

**Never add a keyword, tool, metric or claim that isn't already on the page without asking first.** The profile is not the whole truth. The user may have used things it doesn't record, and they decide.

Group the MISS lines by the script's label and ask with `AskUserQuestion` (`multiSelect: true`, up to 4 options per question, up to 4 questions):

- `<in profile>`: verified evidence exists in `my-profile`. Offer each one with the exact bullet or skills change you'd make. Most are one-click yes.
- `<not in profile>`: the profile says nothing. Ask "Have you used X? Where?".
- `<profile: NOT verified>`: the profile lists it as not verified (e.g. Kubernetes, AWS, Kafka). Still ask, because things change, but say that the profile currently says no.

Lead with core keywords, since they're worth double. Skip keywords that make no sense for the target role. After they answer:

- Add only what they approved, in their words, in Skills plus one bullet where possible.
- For any **new** fact (a tool, project or metric that's not in `my-profile`), ask for the detail you need (where, what, any number), then **update `my-profile`** so later resumes can use it. Remove the item from its "Not verified" list if they confirm it.
- Anything they decline stays out. Don't ask again for the same target.

### 4. Rebuild, re-check, report

Rebuild (`build.sh` for applications; the base resumes in `main_resume/` use build.sh too), then re-run the checker. Report to the user:
- the score before and after, for each keyword list;
- the parse faults that were fixed;
- the keywords added (approved) and still missing (declined or unanswered);
- the quantified-bullet ratio, and which bullets still have no number (ask them for a real number rather than inventing one).

## Rules

- One page, no shrinking of margins or font. If additions overflow, trim low-signal skills or merge bullets (the `tailor-resume` trim order).
- Metrics stay exactly as recorded. Never round up or add numbers they didn't give.
- Never keyword-stuff: no white text, no keyword dump lines, no repeating a term more than about 3 times. Each keyword should sit in Skills and in a real bullet.
- Never claim more experience than the profile allows. Years-of-experience gaps are reported, not hidden.
