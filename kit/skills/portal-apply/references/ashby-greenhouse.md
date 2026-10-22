# Ashby and Greenhouse

Both: no account, easy, **the user submits**. Pre-flight with `form-dump`, fill with `browser_fill_form` (labels are clean), upload with the file input.

## Ashby (`jobs.ashbyhq.com/<co>/<id>/application`)

- Often just Name, Email, Resume Some add screeners (nationality, visa, years of X, target comp, notice): answer from `answers.md`.
- Yes/No questions are toggle buttons: click the button text.
- A consent / certification checkbox at the end (OpenAI, Bjak, G2): leave for the user.
- Confirmation email comes from `no-reply@ashbyhq.com` with **no company name** ("We've Received Your Application"); log which tab you filled when so job-inbox can match it by time.
- Public API for pre-flight: `curl -s https://api.ashbyhq.com/posting-api/job-board/<slug>` (JD + location + `jobUrl`).

## Greenhouse (`job-boards.greenhouse.io/<co>/jobs/<id>`, `embed/job_app?for=<co>&token=<id>`)

- Standard: First/Last name, Email, Phone (country picker → India), Resume, LinkedIn, Website (leave empty), custom questions, EEO (Male / Asian / not a veteran, from answers.md).
- **School** is a searchable select: <your university> isn't listed; it's optional, leave blank and tell the user.
- Custom selects are React-select: click, type, Enter.
- Location questions ("Willing to work from office in <your city>") and "Current Company" industry lists: ASK unless saved.
- Public API: `curl -s https://boards-api.greenhouse.io/v1/boards/<slug>/jobs/<id>` (JD in `content`, HTML-escaped).

## Quirks log

- 2026-10-06 Razorpay FDE: "Current Company" is an industry list, left for the user.
- 2026-10-06 Telnyx FDE: languages field free text "English (C1)".
- 2026-10-06 Elastic: privacy acknowledgement checkbox left for the user.

## Learned 2026-10-13
- Ashby JD pages render client-side, so WebFetch returns only the title. Read the JD with Playwright `body.innerText`.
- Ashby resume input is `#_systemfield_resume`; some forms also have an autofill file input, so target the id. Custom fields use uuid ids.
- Ashby slugs are case-sensitive (`Wisdom-AI`, not `wisdomai`). Check `api.ashbyhq.com/posting-api/job-board/<Slug>`.
- A company page can embed Ashby (`kognitos.com/<Co>/<id>` → careers page → `jobs.ashbyhq.com/<Co>/<id>/application`), and the job id is the Ashby posting id.
- Greenhouse embeds: when a careers page (e.g. abnormal.ai) doesn't show the form inline, or the job URL redirects to the company site (Rubrik), go to `job-boards.greenhouse.io/embed/job_app?for=<board>&token=<id>`. Custom dropdowns (school, CGPA bands, employer) are react-selects: School missing → "Other"; employer not listed → "Other".
- Greenhouse phone: click `#country`, type India, pick "India +91" with `getByRole('option',{name:/^India/})` (the first match for "India" can be British Indian Ocean Territory +246; check the dial code reads +91), then fill `#phone` with 10 digits (`getByLabel('Country')` is ambiguous). City is an autocomplete: type <your city>, pick "<your city>, Karnataka, India".
- Greenhouse react-select: `getByLabel(q).click()` then `getByRole('option',{name})`. Some selects (e.g. race) appear only after the previous answer, and some forms require a "preferred last name".

## Learned 2026-10-15
- `input[type=file]` `.first()` is the **autofill** input, not the resume field (Sarvam): it leaves `#_systemfield_resume` empty and overwrites Name with the parsed name. Upload to `#_systemfield_resume` only, then fill Name last and read back both.
- Form fields without a browser: POST `https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobPosting` with query `jobPosting(organizationHostedJobsPageName, jobPostingId) { applicationForm { sections { fieldEntries { ... on FormFieldEntry { isRequired field } } } } }`.
