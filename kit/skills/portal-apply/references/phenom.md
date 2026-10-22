# Phenom (NTT DATA, Adobe and other `careers.<company>.com` sites)

**Account:** none. **Submit:** the user. Multi-step: My Information → My Experience → (Application Questions) → Voluntary Disclosures → Review.

## Getting in

The job page's "Apply now" button is covered by the Phenom chatbot widget, so clicks time out. Read its href and navigate instead:
```js
const href = await page.locator('a[data-ph-at-id="apply-link"]').first().getAttribute('href');
```
NTT DATA: `https://careers.nttdata.com/global/en/hvhapply?jobSeqNo=<seq>` redirects to `/apply?...&step=1`.

## Fields

- Resume/CV upload (DOC/DOCX/PDF/TXT, **1 MB max** on NTT), optional cover letter.
- Legal first/last name, Country/Region code (select India), Phone `<your phone>` ("+code number" format), Personal email, Address line 1, City, State, PIN.
- Experience/education repeaters like Workday; use `profile.json` jobs.
- "How did you hear": Adobe = Job Boards > LinkedIn.
- Datepickers for education dates are optional; leave blank.

## Quirks log

- 2026-10-06 Adobe Conversation AI Engineer: 5 steps, refilled to Review; legal age Yes, background check Yes, right-to-work docs Yes, work daily at <your city> location Yes.
- 2026-10-12 NTT DATA AI engineers - Advisor: opened step 1, not pursued ("Advisor" grade, years not stated).

- 2026-10-18 Ecolab (`jobs.ecolab.com/global/en/apply?jobSeqNo=EIYEIEUS<REQ>EXTERNALENGLOBAL`, 5 MB resume limit): the parser fills phone as <your phone> with +91 already picked, so overwrite with 10 digits; it titled <employer> "GenAI Engineer Intern", so fix it. Step 3 questionnaire ids `jsqData.QUESTIONNAIRE-3-72.a`–`h` (non-compete, sponsorship, authorised, 18+, salary, prior Ecolab process, relatives, conflicts). Step 4: gender `voluntary_SA_USA.gender` plus a required T&C box `termsAndConditions.applicantAcknowledgment` (left for the user). Upload with `locator('input[type=file]').setInputFiles`; a dangling `waitForEvent('filechooser')` hung the MCP call for 30 minutes.
