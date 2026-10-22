# LinkedIn Easy Apply

**Submit:** Claude may submit (the user's rule, 2026-10-06, reconfirmed 2026-10-12). Everything else in this skill stops before submit.

## Flow (3–5 pages)

1. Contact info: name/headline/location come from the profile; email and <your phone> are prefilled. Nothing to do.
2. Resume: a list of every PDF ever uploaded. LinkedIn preselects the **most recent**, which is often the wrong one. `li-walk` picks by file name.
3. Additional questions (0–2 pages): screeners. Answer from `answers.md`, ask the user about anything new.
4. Review → Submit application.

## Scripts

```bash
S=.claude/skills/portal-apply/scripts
python3 $S/snip.py li-walk '{"resume":"ai"}'           # opens Easy Apply, picks resume, walks to the first page with questions
python3 $S/snip.py li-answer '{"answers":[{"q":"notice period","a":"60"},{"q":"serving your notice","a":"No"}]}'
python3 $S/snip.py li-submit '{"resume":"ai"}'          # walks to Review, checks resume + no errors, submits
```
Run each printed file with `browser_run_code_unsafe` (`filename`). One Easy Apply per tab: opening another job in the same tab discards the open dialog, so give each job its own tab during a batch.

Tailored PDFs must be uploaded once (dialog "Upload resume") before `li-walk` can pick them by name.

## Selectors that work

- Dialog: `page.getByRole('dialog').first()` (CSS `[role=dialog]` via `document.querySelector` misses it; it's in a shadow root).
- Radios: `div[role=radio]` with `aria-label` = the question; click the div whose text is Yes/No. `getByRole('radio').check()` times out.
- Resume radios: click `label[for=<input id>]` (force); clicking the wrapper div doesn't select.

## Screener answers seen (all in answers.md)

| Question | Answer |
|---|---|
| Notice period (text) | the number of days only (numeric-only fields reject "60 days (negotiable)") |
| Serving notice? | No |
| N+ years of experience? (N ≥ 3) | No (truthful) |
| Years of X (number) | role-specific per answers.md; never inflate |
| Bachelor's degree? | Yes |
| Experience with a named tool | Yes only if `my-profile` lists it |
| Built X **deployed to production for real users** | Answer per `my-profile` status; if unsure, ask |
| Years of experience (numeric-only field) | the decimal from answers.md |
| Exposure dealing with customers | per `my-profile` |
| Immediate joiner | No |
| Pay bands | the band that starts at the saved number |

## Quirks log

- 2026-10-12: Easy Apply on GeoServe showed "Requirements added by the job poster: 4+ years Node.js" only on the job page, not the JD; read that block first.
- 2026-10-12: Unikloud was sent before the explicit submit step (the confirmation was already showing when the tab was re-opened). Always check `Applied` status on the job page before re-walking a dialog.

- 2026-10-13: In the new jobs UI, search cards are `[role=button][componentkey^="job-card-component-ref"]` with no anchors. Click a card, then read the right pane from "About the job". Pagination buttons carry aria-label "Page N". An external apply link is an `<a>` whose href contains `safety/go`, and decoding its `?url=` gives the destination without clicking. `li-walk` misses single-step dialogs where the only button is "Submit application". Screener radios may lack `role=radiogroup`, so click `label[for=<id>]`. "Years" text fields cap at 20 chars and some accept numbers only (use 1.8).
- 2026-10-18: `li-walk` resume arg is `"ai"` or `"fs"` (anything else is read as a file name). li-walk/li-answer act on the current tab, so when workers share the browser wrap them: `async (page0)=>{const page=page0.context().pages().filter(x=>x.url().includes(KEY)).pop(); ...}`. Text screeners read "How many years of work experience do you have **with** X", so match on "with X". Join-powered forms (`applicantTrackingSystemName=Join`) add a required "JOIN Terms & Conditions" Yes/No that li-answer misses (click it by text, then the ancestor's Yes) plus an optional monthly-salary field (200000). Media.net-style numeric comp fields: full rupees (800000 / 400000 / 0, notice 60). After submit the page shows "Application submitted"; check for that, not the modal. The search-results list is virtualised (no /jobs/view links): click each bold title and read the jobId from `currentJobId`.
