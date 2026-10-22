---
name: apply-job
description: End-to-end job application for the user. They paste an application link and a JD; this builds a tailored resume (tailor-resume), parses and scores it for ATS (ats-check), rebuilds until the score is high, then fills the application form with saved answers (fill-form) and stops before Submit. Asks the user whenever anything is unclear and never assumes. Use when the user pastes a job link together with a JD, or says "apply to this", "do the full application" or "resume and form for this job".
---

# Apply to a job

The user pastes **a form link and a JD**. You run four skills in order. Each one owns its own rules, so load it and follow it; this skill only sets the order, the gates and the hand-offs.

```
JD + link
  → 1. tailor-resume  (build the resume)
  → 2. ats-check      (parse + score)
  → 3. gate: good enough? if not, rebuild and re-score (back to 1)
  → 4. fill-form      (fill everything, upload the PDF, NEVER submit)
  → 5. report + log to the tracker (job-inbox)
```

## Rules that hold across every step

- **Never submit the form.** the user always submits it themself.
- **Never assume, always ask.** Use AskUserQuestion for any missing fact, unclear JD requirement, new keyword, or form field without a saved answer. Batch the questions per step so the user answers once per step, not once per field.
- **Never invent claims.** The only sources are `my-profile` and `fill-form/references/answers.md`. New facts the user gives go into those files.
- **Never use a portfolio URL unless `my-profile` lists one.**
- **No screenshots** in reports.

## 0. Read the inputs

- If the user pasted only a link, read the JD from the page (Playwright snapshot or WebFetch) and show them the role and company in one line before building.
- If they pasted only a JD, ask for the form link (or build the resume and stop before step 4).
- Note the company, the role and whether it's remote. Check the tracker first (`python3 .claude/skills/job-inbox/scripts/tracker.py find <company>`), then "Applications filled" in `fill-form/references/answers.md` and the past applications in `my-profile`, to see if this job was already started, or if the user was already rejected there. If a row exists, tell them its status before building.

## 1. Build the resume: `tailor-resume`

Follow `tailor-resume` fully: it writes `applications/<company>_<role>/main.tex` from the closer base resume (`main_resume/ai_engineer` or `main_resume/fullstack_engineer`), builds it and checks the preview. Ask the user about any JD requirement the profile can't back up.

## 2. Parse and score: `ats-check`

Run `ats-check` on the built PDF:
- against a JD keyword file you write to the scratchpad from the JD's exact terms;
- and against the matching role list(s) (`ai_engineer.txt`, `backend_engineer.txt`, `fullstack_engineer.txt`).

Fix parse faults without asking. Ask the user about every missing keyword before adding it, as `ats-check` requires.

## 3. Gate: is it good enough?

The resume passes when **all** of these hold for the JD keyword list:
- **ATS score 90+**,
- **weighted keyword coverage 85%+**,
- **zero parse FAILs**,
- **one page**, with a clean preview.

If any fail, **remake** the resume and score it again (back to step 1 with the gaps in hand):
1. Strengthen what's already true: move JD terms into Skills **and** a bullet, use the JD's exact spelling, and lead each role with its most JD-relevant bullet.
2. Swap in better-matching evidence from `my-profile`: a different project, or a different bullet from the bullet bank.
3. Ask the user about the remaining missing keywords (approval needed).
4. Add numbers to bullets that have none, using only recorded metrics; ask them for real numbers otherwise.

Stop after **3 rebuild rounds**. If it still doesn't pass, it's usually because the JD wants things the user doesn't have (years, Kubernetes, a domain). Tell them the score and the exact gaps, and **ask** whether to go ahead with the form anyway. Don't stuff keywords to hit a number.

## 4. Fill the form: `fill-form`

Follow `fill-form` with the link (it routes known portals such as LinkedIn, Workday, Lever, Ashby, Greenhouse and Zoho to `portal-apply`'s playbooks and scripts), uploading **this job's tailored PDF** (`applications/<folder>/First_Last_Resume_<Company>.pdf`). Write the long answers ("why us", "stand out", projects) for this company and JD, leading with the work the JD cares about most. Ask about every field without a saved answer. Save each new answer to `answers.md`. **Do not submit.**

## 5. Report

Keep it short:
- **Resume:** the PDF path, the ATS score and keyword coverage (and the first-round score, if a rebuild was needed), and the keywords they approved or declined.
- **Form:** "filled, not submitted, open in the browser", plus one line per long answer and anything risky (e.g. a notice period longer than the job asks for).
- **Saved:** new answers or facts written to `answers.md` or `my-profile`.

Then log the application:
- **the tracker** (`job-inbox` owns it; fields in `job-inbox/references/fields.md`). Add the row, or update the existing one, with `status=saved`, `stage="form filled, the user to submit"`, `next_action="Submit the form"`, `next_action_due=<today>`, plus `category`, `platform`, `job_url`, `resume`, `ats_score`, `salary`, `location`, `work_mode`:
  ```bash
  python3 .claude/skills/job-inbox/scripts/tracker.py add --company "<Company>" --role "<Role>" --category company_site --platform <ATS> --status saved --stage "form filled, the user to submit" --next_action "Submit the form" --next_action_due <today> --job_url <link> --resume applications/<folder>/First_Last_Resume_<Company>.pdf --ats_score <score>
  ```
  When the user says they submitted (or `job-inbox` sees the confirmation email), update it to `applied` with `date_applied`.
- one line under "Applications filled" in `answers.md`;
- the past-applications line in `my-profile` (`tailor-resume` step 9).

## Related

- `job-inbox`: reads Gmail for replies, rejections, interviews and postings worth applying to, and keeps the tracker current. When it surfaces a posting the user wants, it hands off to this skill.
- `job-hunt`: the daily routine that finds postings and runs this flow for 10+ jobs at once, with batched questions.
- `cold-email`: after the form is filled, drafts an email to the hiring manager or recruiter (pattern B or E) as a Gmail draft, on the same tracker row.
