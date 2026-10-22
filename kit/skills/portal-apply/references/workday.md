# Workday (`*.myworkdayjobs.com`)

**Account:** one per company tenant. Ask the user to sign in / create it in the tab (email <your email>) before filling; batch these logins at the start of a run. **Submit:** the user. Leave the Terms checkbox on "Voluntary Disclosures" for them.

## Flow (6 steps)

| Step | What to do | Script |
|---|---|---|
| 1 Autofill with Resume | upload the PDF: `page.locator('input[type=file]').first().setInputFiles(pdf)`, then Next | — |
| 2 My Information | fix CAPS names, address, phone type Mobile, state, source LinkedIn, previous worker No | `workday-myinfo` |
| 3 My Experience | replace parsed jobs with the 4 profile jobs, dates, English 5/5, websites, school | `workday-experience` |
| 4 Application Questions | dropdown questions, salary text, start date | `workday-questions` |
| 5 Voluntary Disclosures / EEO | Terms checkbox → the user. EEO (if asked): Male, Asian, not a veteran | manual |
| 6 Review | the user submits | — |

Apply URL: append `/apply` to the job URL; Workday then offers "Autofill with Resume" (use it: fewer fields to type).

```bash
S=.claude/skills/portal-apply/scripts
python3 $S/snip.py workday-myinfo '{"source":"LinkedIn"}'
python3 $S/snip.py workday-experience '{}'
python3 $S/snip.py workday-questions '{"list_only":true}'     # see questions + options first
python3 $S/snip.py workday-questions '{"answers":[{"q":"unrestricted right to work","a":"^Yes$"},{"q":"sponsorship","a":"^No$"},{"q":"commute into an office","a":"^Yes$"},{"q":"hybrid","a":"^Yes$"},{"q":"3 days per week","a":"^Yes$"},{"q":"18 years","a":"^Yes$"},{"q":"highest level of education","a":"Bachelor"},{"q":"notice period or .*garden leave","a":"^No$"},{"q":"partner or customer","a":"^No$"}],"text":[{"q":"desired salary","a":"<expected pay from answers.md>"}],"date":"MM/DD/YYYY"}'
```
Start date = today + notice days (answers.md).

## Quirks (seen across several tenants)

- Parser puts names in CAPITALS ("Alert: more than 2 capital letters") and merges jobs: always run `workday-experience`.
- Dates: month/year are spinbuttons. `fill()` does nothing, and typing "1"/"01" can store 2 (seen on several tenants). **Focus the month input, ArrowUp/ArrowDown until it reads the month, Tab**, then the year; read every date back.
- State list uses diacritics: a state name with diacritics. `workday-myinfo` compares accent-insensitively.
- "How Did You Hear": typing "LinkedIn" + Enter lists "LinkedIn Applied" / "Sourced on LinkedIn"  or "Job Board > Linkedin" . Pick the applied/job-board one.
- LinkedIn URL must include `www.` or validation fails.
- **Job URLs need the `_<reqId>` suffix** (`..._2026174`, `..._R198044`); without it they 404. From inside a tenant tab: `POST /wday/cxs/<tenant>/<site>/jobs {"searchText":"<title>"}` lists postings, `GET /wday/cxs/<tenant>/<site><externalPath>` gives the JD. Freehire titles can be stale (one had been taken down).
- **Accounts:** tenant password policies need an uppercase letter; use the password in `.secrets/portal-logins.md` (gitignored). Most tenants  need no email verification. If a sign-in fails right after account creation, ask the user to sign in themself.
- Drafts persist server-side: sign in again and every step comes back prefilled. "Something went wrong (VPS error)" → reload or re-open `/apply`, then re-check the answers on the step it failed on.
- The resume parse may add a website field the user did not want: delete it.
- Several tabs can share one URL: tag your own tab with `window.name` and find it by evaluating each page.
- School search: <your university> is usually missing and there's no "Other". Education is optional, so delete the entry (script does) and tell the user.
- The plain "Add" button exists under Certifications **and** Websites; the wrong one creates an empty required Certification that blocks Next. The script adds websites via the last "Add"/"Add Another" and reports certification count (must be 0).
- Field of Study popups stay open over other fields and intercept clicks: `page.mouse.click(5,5)` closes them.
- Question dropdowns' aria-labels are just "Select One Required"; read the question from the ancestor (script does). Follow-ups appear after an answer ("If yes, 3 days per week?").

## Quirks log

- 2026-10-12 BlackLine: Associate SE, filled by Claude, submitted by the user.
- 2026-10-18 Cisco (cisco.wd5 Cisco_Careers): 4 steps, no Voluntary Disclosures. Source is a **plain dropdown** (workday-myinfo's search-box path fails). Years buckets 0-1/2-3/4+, so pick 2-3; office "2-4 days in a week". If the school list lacks the user's university, leave education out.
- 2026-10-18 PwC (pwc.wd3 CRM_Experienced_Careers_Site): required Prefix (Mr.); the first listbox on the page is the "Settings" menu, so target `:has-text("Select One")`. <your university> **is** listed. Two data-consent questions (Yes other positions / No events). Voluntary Disclosures asks birthplace, marital status, citizenship (nested multiselect: scroll to the country, then "Citizen (India)"), and a terms box left for the user.
- 2026-10-18 Maersk (maersk.wd3 Maersk_Manual + Maersk_Careers, one account): phone type "Private Phone"; language Overall "Excellent". Q1: applied before, relocate, relatives, right to work, government (self and family). Q2: Aadhaar / PAN / 18+ all use "Yes, I do". Marital options read "Single (India)". Citizenship multiselect needs `keyboard.type` (fill doesn't filter). Privacy Policy box is left for the user.
- 2026-10-08 Synechron: DOB in MM/DD/YYYY, field of study "Computer and Information Science".
