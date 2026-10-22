# Other portals

Short playbooks. Promote one to its own file once it needs scripts.

## Google Forms (`docs.google.com/forms`, `forms.gle`)
- Dump questions: each `[role=listitem]` has a `[role=heading]` question, `[role=radio]`/`[role=checkbox]` options (`aria-label` = option text), text inputs, and "Add file" for uploads. The Playwright profile is signed in to Google (2026-10-13): click `div[role=button][aria-label="Add file"]`, then in the `docs.google.com/picker` frame click "Browse" inside `Promise.all([page.waitForEvent('filechooser'), ...])` and `setFiles`; poll the item text for ".pdf". Yes/No "I confirm" items are often **checkboxes**, not radios. Fill by question text with `[role=listitem]` filtered by heading text, in one run_code call.
- **Read every option before filling**: a form can reveal a budget far below the expected pay only on its last screen. If so, drop it and tell the user.
- Submit: the user.

## Keka (`<co>.keka.com/careers/applyjob/<id>`)
- Resume parse mangles experience: fix titles/dates, delete junk skill tags. Experience, CTC, joining days and location from `answers.md`, consent ticked (it's part of the form), CAPTCHA left for the user.
- Selectors (2026-10-13, Zenskar): phone code is a select2 → `jQuery('select[name="mobilePhone.countryCode"]').val(<+91 option>).trigger('change')`. Skill chips: `#skills-container > div[id^=skill-]`, name in `span.mr-3`, remove with its `.ki-close` click (parser glues junk like "pytest Cloud & DevOps"). Exp dates: `#experienceDateOfJoining_N` opens a jQuery-UI datepicker → select `.ui-datepicker-month` / `.ui-datepicker-year`, click day `a`. "Currently working": `#isCurrentlyWorking_N`. "Unable to process this file" banner shows even when the parse worked.

## Forage AI careers (`careers.forage.ai/job-opportunities/<slug>/`)
- HubSpot form in `iframe[title="Form 0"]`: First name, Last name, email, "Which job opening" (free text, make it unique per role), Current CTC (number), CV file. Fill all roles in one `browser_run_code_unsafe` loop with `contentFrame()` + `setInputFiles`. No consent box; Submit is the only button.

## Workable (`apply.workable.com`, often behind LinkedIn "Apply")
- **Decline the cookie banner first** or dropdowns won't open. EPF/experience bands: pick the band containing 1y10m (13–24 months); joining "31–60 days".

## Infosys (`career.infosys.com`)
- Needs a registered, logged-in account. Single page: resume (autofill), DOB (Angular datepicker: `mat-datepicker` snippet), preferred interview city "<your city>", preferred work location (multi-select, stays open: Escape), employer, total experience (number 1.8), notice 60, current CTC in lakhs 12, graduation % and **PAN: ask the user** (not saved), phone 91 + <your phone>, skills chips ("Technology|…|Python - Open Source", "…|PostgreSQL"; Django/FastAPI not in list: type 5 chars slowly, then pick), gender Male, Ex-Infoscion toggle off.

## Flexiple (`app.flexiple.com`)
- Google sign-in, confirm the email. **One application covers future matched roles**: apply to the best single role, not every Flexiple post. Questions: current CTC LPA, expected CTC LPA, notice + earliest join date. Profile resume is shared by all applications.

## ClanX (`jobs.clanx.ai`)
- Radios hidden behind styled labels (click the label); phone prefilled +91; expected CTC numeric spinbutton.

## Binary (`binary.so`)
- Numeric-only ESOP field (0); CTC text from `answers.md` (breakup as saved). It may show a previous submission: nothing to do.

## YC Work at a Startup
- Wellfound has its own playbook now: `wellfound.md`.
- YC WaaS: founder message only; **5 applications a week** (count tracker rows).

## Rippling, SmartRecruiters, Darwinbox, PyjamaHR, iCIMS, Taleo, SuccessFactors
- Rippling (`ats.rippling.com/<co>/jobs/<id>`): standard fields + EEO + SMS consent No. Resume upload autofills name/email/phone/location (check them). Dropdowns are `div#field-N`: click it, then `getByRole('option',{name,exact:true})`. Strong No…Strong Yes questions are custom radios (read `aria-checked`). The SMS opt-in needs a click on its text. Some input names start with a digit, so quote them: `[name="..."]`. Others: dump first; treat as medium/hard.

## Trakstar Hire (`<co>.hire.trakstar.com/jobs/<id>/?apply=true`), 2026-10-18
- Plain form: `#id_candidate_first_name`, `_last_name`, `_email`, `_phone`, `#id_resume`. `fill` + `setInputFiles` work. Leave the invisible reCAPTCHA and "Apply with Indeed" alone.

## Teamtailor (`careers.<co>.com/jobs/<id>-<slug>`)
- Expired ads show "This position is no longer active" with no apply control, so check for that text before planning a fill.

## Torre (`torre.ai/post/<id>`), 2026-10-18
- Account exists (email sign-up at accounts.torre.ai: name + email + phone, no password, no verification). Post → APPLY → `/applications/<post>/candidates/<id>`; step 1 is LinkedIn URL / Upload CV (hidden file input) / no résumé. The final APPLY sits at the bottom, so never click it.
- **The session's safety check blocked Claude's browser actions once the Torre apply flow was open** (even read-only ones). Hand Torre jobs to the user with the link instead of filling them.

## startup.jobs (aggregator, freehire source `startupjobs`)
- Blocks scripted fetches (403). In the browser, "Apply for this job" opens a new tab on the real ATS. If it posts to `startup.jobs/apply/<id>` instead, find the company's ATS page directly.

## Not real application forms (skip)
- `haystackapp.io/.../auto-apply/trial`: an auto-apply product's trial signup behind a LinkedIn "Apply" button.
- `huntingcube.ai/browse/job-apply`: recruiter aggregator; check the "N-M Years" chip (5–9 for Aegion roles while LinkedIn showed none).

## Learned 2026-10-13
- **YC WaaS:** the directory shows no posting dates, and "Showing N startups" counts companies (most say "No specific jobs listed"). Apply opens a modal with one textarea (50-char minimum) plus Send. It uses the profile resume, which the page exposes only as `resume_fingerprint`, so check it visually on `/application/personal`. In-page fetch of company pages fails (CORS), so use goto.
- **RoundOne (roundone.ai careers):** a chat-style apply. The CV parse fills name/email/phone (name in UPPERCASE, so retype it), "Looks right" only confirms, then a final Submit. An AI voice screen follows.
- **Fabric (app.fabrichq.ai/jobs):** 4 steps: Start (name/email/phone, +91 preset) → Apply Now → resume → work preference → AI interview. Stop at step 1 for the user.
- Resume-parsing portals (Darwinbox, RoundOne) uppercase the name from the resume header, so always retype it in normal case.

## YC Work at a Startup (`workatastartup.com/jobs/<id>`), 2026-10-18
- Logged in. Apply is an `<a>`: `p.getByText('Apply',{exact:true}).first().click()` (getByRole('button') times out). The modal is a single textarea ("Reach out to <name> at <company>", min 50 chars): `p.locator('textarea').first().fill()`. Address the note to the **modal's** name (it can differ from the listed founders: Peakflo → Mrinal, Raven → Sriyansh). The user clicks Send.
- A "qualifications might not match" warning is normal for 3+ yr tags. **Quota: 5 applications a week**, so count YC rows in the tracker first.
- Finding jobs: `locations=IN` hides most companies ("no specific jobs listed"); `remote=yes` (no location) lists ~250 companies, so scroll ~25 times and keep only roles naming IN or plain Remote. Cards: `a[href*="jobs/"]`; founders' LinkedIns on `/companies/<slug>`. The listing has no posted date.
