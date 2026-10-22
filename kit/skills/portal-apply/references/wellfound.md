# Wellfound (`wellfound.com/jobs/<id>-<slug>`)

**Account:** the user's, logged in in the Playwright profile (check: the nav shows Home · Profile · Jobs · Applied · Messages). **Submit:** the user ("Send application"). **Best for:** startups, often with salary bands and the founder's name on the page.

## The one thing to get right: the resume

Wellfound has **no per-application upload**. Every application sends whatever resume is on the profile *at the moment the user clicks Send*. So:

- Use **one resume for the whole batch**. Build it to cover every job in the batch (start from the closest earlier tailored resume, run `ats-check` against each JD's keyword file, and aim for 90+ on all of them). Name the PDF neutrally (`First_Last_Resume_AI_Engineer.pdf`, never the name of one company), because every company sees the file name.
- Upload it with `wf-resume` **before** filling panels, in a spare tab.
- If a batch really needs two different resumes (AI vs full-stack), the user has to send batch 1 before you swap the resume for batch 2. Say so in the report.
- Record in `answers.md` which file the profile holds now. The 2026-10-12 batch left it as `applications/wellfound_ai_startups/First_Last_Resume_AI_Engineer.pdf`.

## Flow

```bash
S=.claude/skills/portal-apply/scripts
# 1. scan listing pages -> filtered rows (company, size, years, salary, age, url)
python3 $S/snip.py wf-scan '{"pages":["https://wellfound.com/role/l/ai-engineer/bangalore","https://wellfound.com/role/l/software-engineer/bangalore","https://wellfound.com/role/l/backend-engineer/bangalore","https://wellfound.com/role/l/machine-learning-engineer/bangalore"],"maxYears":3,"maxAgeDays":31}'
# 2. read the shortlisted JDs (sidebar facts, years phrases, hiring contact, team)
python3 $S/snip.py wf-jd '{"urls":["https://wellfound.com/jobs/..."],"chars":3500}'
# 3. set the batch resume (spare tab)
python3 $S/snip.py wf-resume '{"resume":"<workspace>/applications/<folder>/First_Last_Resume_AI_Engineer.pdf"}'
# 4. per job, in its own tab: dump the panel, then fill it
python3 $S/snip.py wf-apply '{"url":"https://wellfound.com/jobs/...","dump":true}'
python3 $S/snip.py wf-apply '{"url":"https://wellfound.com/jobs/...","answers":[{"q":"interests you","a":"..."}]}'
```
Run each built file with `mcp__playwright__browser_run_code_unsafe` (`filename` = the printed path). `wf-scan` and `wf-jd` use `fetch`, so they never navigate, but they **must run from a wellfound.com tab** (from about:blank they fail with "Failed to fetch"). **Parallel workers:** `snip.py` always writes the same `.playwright-mcp/run/<snippet>.js`, so workers overwrite each other's args; copy the built file to a per-job name (`w<jobid>-*.js`, under the repo, not the scratchpad) and wrap it to pick its own tab by URL. `wf-apply` and `wf-resume` navigate the current tab, so open a new tab first (`browser_tabs new`).

Pagination: append `?page=2` and so on. Other useful pages: `/role/r/ai-engineer` (remote), `/role/l/ai-engineer/india`, `/company/<slug>/jobs` (one company's openings), `/company/<slug>/people` (founders and team, fetchable).

## Before you fill: dedupe and fit

- **Dedupe against the tracker** (`tracker.py find <company>`). Wellfound's own `/jobs/applications` page renders client-side and comes back empty through `fetch`, so the tracker is the source of truth. Watch for companies the user already applied to through another channel (Prodigal, Scalio, Metaforms, FOXO, cardboard.ai and Seekho all showed up again on 2026-10-12).
- **Read the years twice.** The listing's "N years of exp" chip and the JD body often disagree (Ema: no chip, 7+ in the JD). `wf-jd` prints every "N years" phrase.
- "Recruiter recently active" and "Posted today" are good signals. Listings 1+ years old are usually dead, even when they still show "Apply".
- Company size comes from the listing (`wf-scan`), not the job page. Under ~50 people means the startup push asks for a founder email too: `/company/<slug>/people` gives founder names; find the email with `research-target`.

## Panel fields

The panel (`[role=dialog]`, "YOUR APPLICATION") holds only the company's custom questions:

| Seen | Field | Answer |
|---|---|---|
| most jobs | "What interests you about working for this company?" (textarea) | Written per company, 120–200 words, the user's voice (`cold-email/references/voice.md`): open with their product or a line from their JD, give one or two real numbers from `my-profile`, name any gap honestly ("I haven't used Pipecat yet"), end with "about 1.75 years in, all of it on production systems". No sign-off block. |
| jobs with no custom questions | "Cover Letter" (textarea `userNote`, placeholder "Write a note to <Company>") | Same kind of note. Match it with `{"q":"cover letter"}`. |
| some | Phone* (text) | Filled automatically from `profile.json` (`<your phone>`). |
| rare | yes/no select | Map from `answers.md`; otherwise ASK. |

## Checking status (don't get fooled)

- **Applied:** the job page shows a **"✓ Applied"** button, or the dialog says **"Success! Your application has been sent."** `wf-apply` checks both and stops.
- Don't search the page text for "Applied": the top nav always has an "Applied" link. That false positive happened on 2026-10-12.
- A tab title starting with `*` means the panel has unsaved input. When the `*` disappears, the panel was usually sent (or closed), so re-check with the button.

## Quirks

- Experience and location chips render as separate text nodes (`"+"`, `"2"`, `"2"`, `"years"`, `" of exp"`, where the first "2" is "+2 more cities"). Plain `innerText` glues them into "<your city>+22 years", which is why the snippets walk text nodes.
- The Upload button on `/profile/edit/resume` keeps showing the old file name until you reload. `wf-resume` reloads before reading it back.
- "Apply now" can be present but do nothing if the profile is missing required sections. `wf-apply` reports "no Apply button" or an empty panel; ask the user to finish their profile.

## Quirks log

- 2026-10-12: First scripted batch (timepay.ai Voice AI Engineer, Avoca AI SE (Product), Fibr AI Product Engineer, Evam Labs AI Engineer). One shared resume (ATS 100/100/100/91). Avoca's panel was Phone only; the others asked "What interests you". The user sent all four the same evening. Botsync's panel (dump test, not sent) had only the Cover Letter textarea.
- 2026-10-06: Metaforms (panel = LinkedIn URL only), FOXO, Recro and Fx31 notes, all filled by hand before these snippets existed.
- 2026-10-18: A "Hey <First name>, is this information still correct?" modal can block "Apply now"; Escape closes it (don't click Complete). Some panels have no note field at all (Certa: phone + yes/no radios + referrer textarea). Hidden custom radios: `check()` and label clicks don't stick; scrollIntoView the input, then `page.mouse.click` at the centre of `input.parentElement` (div.styles_radio). `wf-apply` doesn't handle radios yet. Listing scans need maxAgeDays ≥ 14 to show much in <your city>; `/role/l/*/india` adds remote-India roles.
