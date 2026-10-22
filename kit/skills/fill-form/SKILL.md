---
name: fill-form
description: Fill a job application form in the browser for the user (Playwright MCP, or Claude in Chrome when connected) using their saved answers, upload the right resume, and NEVER submit. Asks the user about anything not already saved, never guesses, and saves every new answer for next time. Use when the user pastes an application form link, says "fill this form" or "apply on this link", or when the apply-job orchestrator reaches the form step.
---

# Fill a job application form

The user pastes a form link; you fill every field from saved answers and stop. **the user always clicks Submit themself.**

## Hard rules

1. **Never submit** (one exception: LinkedIn Easy Apply, which Claude submits per the user's standing rule; see `portal-apply/references/linkedin-easy-apply.md`). Never click Send, Submit, Apply, Finish, Confirm or any button that sends the application, and never press Enter in a field if that could submit the form. Also never click "Next" on the **last** step of a multi-step form if it sends the application. If you can't tell whether a button submits, don't click it; ask.
2. **Never assume.** Every answer comes from `references/answers.md` or `my-profile`. If a field isn't covered there, or two saved answers could fit, or the form's options don't match the saved answer exactly, **ask the user with AskUserQuestion** before filling it. That includes job source, relocation, preferred locations, start date, gender and diversity questions, and any yes/no about skills they haven't confirmed.
3. **No screenshots** in the report. Tell the user it's filled and list what needs their eyes.
4. **Never put a portfolio URL in a form unless `my-profile` lists one.**
5. **Logins, CAPTCHAs and one-time codes:** stop and ask the user to do them in the browser window, then continue.
6. **Truth over fit.** Keep metrics exactly as recorded, and never pick an experience band above the saved one. Don't claim a project is in production unless `my-profile` says so.

## Files

- `references/answers.md`: identity, address, CTC, notice period, education, which resume to upload, long-answer blocks, learned answers and a log of filled forms. Read it first, every time.
- `my-profile`: facts about their work, for long answers.

## Workflow

1. **Load the tools.** Use ToolSearch to load the Playwright tools (`browser_navigate`, `browser_snapshot`, `browser_fill_form`, `browser_click`, `browser_file_upload`, `browser_evaluate`, `browser_wait_for`). If Claude in Chrome is connected and the user wants their own logged-in browser, use that instead.
1b. **Lever (`jobs.lever.co`): don't fill. Give the user the link and all answers in chat (their rule, 2026-10-14).** **Known portal? Use `portal-apply`.** Match the URL against its detection table (LinkedIn Easy Apply, Workday, Lever, Ashby, Greenhouse, Zoho Recruit, Phenom, Google Forms, Keka, Workable, Infosys, Flexiple...). If it matches, read that portal's playbook and use its scripts (`portal-apply/scripts/snip.py`) for steps 2, 6 and 7 instead of discovering the form by hand. The rules in this file still apply. When a portal surprises you, update its playbook before finishing.
2. **Open the link and read the whole form.** Navigate, then read the snapshot file it saves (`.playwright-mcp/page-*.yml`). List every field: label, type, options, required or not. For multi-step forms, fill and read each step in turn.
3. **Match fields to saved answers.** Build a table: field → answer → source (`answers.md` row, profile section, or "ASK").
4. **Ask once, in one batch.** Put every "ASK" field into AskUserQuestion (up to 4 questions per call, with the form's real options). For free-text questions with no saved answer, offer a draft written from the profile as the first option. Also ask about any long answer that would need a claim not in the profile.
5. **Write the long answers.**
   - Projects and "stand out": adapt the blocks in `answers.md` to the field's length and the company.
   - "Why us": read the company's site (WebFetch) and write something specific, never generic.
6. **Fill the form.**
   - Text, email, number and textareas: `browser_fill_form`. Numeric CTC fields take plain numbers (e.g. 2400000).
   - **Radio buttons and checkboxes:** custom-styled ones often have the real input hidden under the label, so `fill_form` times out. Click the **label text** ref instead.
   - Dropdowns: `browser_select_option`, or click to open a custom one, then click the option.
   - Phone with a country-code picker: set the user's country, then the local number (or the full international number if the field already shows the code).
   - File upload: click the upload button, then `browser_file_upload` with the absolute PDF path. Use the tailored PDF if one was just built for this job, otherwise the matching base resume.
7. **Verify without screenshots.** Run `browser_evaluate` to read back every filled input, the checked radios and the uploaded file name, plus any `[role=alert]` error text. Fix any empty or wrong field. Confirm no value contains a link listed as banned in `my-profile`.
8. **Save what you learned.**
   - Every new answer the user gave goes under "Learned answers" in `answers.md`, with the date.
   - Add a line to "Applications filled".
   - Log it in the tracker (`job-inbox/scripts/tracker.py`): `find` the company, then `add` or `update` the row with `status=saved`, `stage="form filled, the user to submit"`, `next_action="Submit the form"`, and the `job_url` and `resume` path. When called from `apply-job`, that skill does this step instead.
   - If they gave a new fact about their work, add it to `my-profile` too.
9. **Report briefly:**
   - that the form is filled and not submitted, and that it's open in the browser for them to submit;
   - the long answers you wrote, in one line each;
   - anything risky, for example a notice period longer than they ask for, or a required field you filled with a fallback.

## Form quirks seen so far

- **ClanX (jobs.clanx.ai):** radios are hidden behind styled labels (click the label); the phone field is prefilled with "+91"; expected CTC is a numeric spinbutton; the resume is uploaded through a button that opens a file chooser.
