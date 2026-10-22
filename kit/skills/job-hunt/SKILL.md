---
name: job-hunt
description: the user's daily job hunt in one command. Finds fresh postings from LinkedIn (their saved <your city> search and hiring posts), company job boards, HN Who's Hiring, Reddit, YC Work at a Startup and more, filters them for fit, skips anything already tracked, then gets at least 10 different jobs ready: forms filled with the right resume (fill-form, never submitted) and personal emails to hiring contacts saved as Gmail drafts (cold-email, never sent). Logs everything in the tracker and stops for the user only when needed. Use when the user says "hunt", "daily hunt", "find jobs", "apply to 10 jobs", "do today's applications", "find new postings" or "start the job hunt".
---

# Daily job hunt

One command, at least **10 different jobs ready to go**, and the user only clicks Submit and Send. This skill only orchestrates. Each step's rules live in its own skill: `fill-form` and `apply-job` (forms, never submit), `tailor-resume` and `ats-check` (resumes), `research-target` and `cold-email` (emails, never sent), `job-inbox` (the tracker). **Run the batch through `orchestrator`**: one `browser-worker` per form/email, in parallel, each in its own tab; you stay the single writer of the tracker.

## What counts toward the 10

- A **job** is one distinct opening (company + role) that wasn't in the tracker before today.
- It's **ready** when its form is filled and waiting in a browser tab for the user to submit, or, when there's no form, an email to a real hiring contact for that opening is saved as a Gmail draft.
- Every job with a findable contact gets **both**: the form and a hiring-manager email (playbook pattern B). That combination gets the most replies.
- StartupsMap cold leads (no posting) are extra and don't count toward the 10. Add up to 5 a day once the 10 are done.
- If fewer than 10 good-fit jobs exist today, stop at what's real and say so. **Never pad the list with poor fits.**

## Current focus: startup bias (set by the user 2026-10-12)

Keep the normal hunt (LinkedIn saved search, company boards, HN, Reddit), but tilt the mix toward startups:
- **Target mix of the 10:** about **6–7 startups** (seed to Series C, or under ~300 people, including funded companies from `outreach/funded-startups-2026-10.md`) and **3–4 from the usual direction** (larger product companies and the saved search). If there aren't enough good startup fits, fill from the usual direction; never pad.
- **Sources:** in step 1, check YC Work at a Startup and Wellfound **before** Reddit, not as a last resort.
- **Ranking (step 2):** among equal fits, a startup ranks above a large company. A recently funded startup (round in the last 90 days) gets an extra bump.
- **Contacts:** every startup under ~50 people gets a founder email (pattern A or B) along with the form, because founders reply more than ATS systems do.
- Remove this section when the user says the startup push is over.

## Hard rules (from the skills this one calls)

- **Never submit a form and never send an email.** the user does both.
- **Never assume.** Questions go to the user in **one batched round** (step 5), not one at a time.
- **Never invent claims**, never claim more experience than `my-profile` states.
- **Everything goes in the tracker** (`job-inbox/scripts/tracker.py`). No job is "ready" until its row is written.
- LinkedIn is read-only apart from filling Easy Apply forms. Respect the safety limits in `references/sources.md`.

## Files

- `scripts/hunt.py`: pulls LinkedIn (guest API, same keywords and <your city> geoId as the user's saved search), company boards (Ashby, Greenhouse, Lever, with JD text), the **career-ops scan** (source `careerops`: about 65 boards in `career-ops/root/portals.yml` across Greenhouse, Ashby, Lever, Workday, Rippling, Workable and Zoho Recruit; titles and locations only, so read the JD), HN and freehire.me (public API over ~3M ATS-crawled postings; <your city> + remote-India, config `freehire` in `search.json`). Freehire links often go to startup.jobs or Telegram reposts, so resolve the real ATS before filling, and recheck the posting is live (titles can be stale); filters titles, locations and years asked; drops anything tracked or seen; ranks; writes `hunts/<date>.json` and `.md`.
- `references/search.json`: keywords, filters, the user's saved-search URL and the original 17-board watchlist. Edit it to tune the hunt.
- `career-ops` skill: the bigger board watchlist (`root/portals.yml`), the liveness checker, repost detection and `discover-ats`. **New companies go there**, not into `search.json`.
- `references/sources.md`: every source, how to reach it, and how hard each form type is.
- `hunts/<date>.md` (repo root): the day's log. `hunts/seen.txt`: URLs already handled or rejected.

## Workflow

### 0. Start of day (2 minutes)
```bash
T=.claude/skills/job-inbox/scripts/tracker.py
python3 $T due
```
- Follow-ups due → hand them to `cold-email` step 8 (drafts only), and do them at the end of the run.
- `saved` rows with "form filled, the user to submit" still open from yesterday → list them in the report so the user submits them first. They don't count toward today's 10.
- Load the tools: Playwright (`browser_navigate`, `browser_snapshot`, `browser_tabs`, `browser_fill_form`, `browser_click`, `browser_file_upload`, `browser_evaluate`, `browser_wait_for`) and Gmail (`create_draft`, `search_threads`, `get_thread`). Open LinkedIn; if it isn't logged in, ask the user to log in in the browser window once, then continue.
- **Logins: never skip a source because it needs one.** When a source needs a login (Instahyre, Cutshort, Hirist, Wellfound, YC Work at a Startup, LinkedIn, or any company portal), open its login page in the Playwright browser, ask the user to log in there (AskUserQuestion: "Log in to <site> in the browser tab, then pick Done"), wait for their answer, check that you're logged in (`browser_snapshot`), then continue. Batch the login prompts at the start of the run so they log in to everything at once.

### 1. Collect (script, then browser)
```bash
python3 .claude/skills/job-hunt/scripts/hunt.py run --days 1      # --days 3 on Mondays
```
Then add candidates from the browser sources in `references/sources.md`, in this order, until there are about **25 candidates**:
1. The user's **LinkedIn saved search** (`saved_search`): every card from the last 24h. Note Easy Apply vs the external apply link.
2. **LinkedIn hiring posts** (last 24h): a post with an email or a form link is a candidate with a contact.
3. **YC Work at a Startup**, then **Wellfound** (startup bias, see above).
4. **Reddit** hiring posts from this week.

Read each candidate's JD (the JSON has descriptions for every source except `careerops`, whose rows have an empty description and `yrs ?`: open those JDs and check the years asked). Drop any that fails the fit filter in `job-inbox` step 5 (role, 0–3 years with a "2+" stretch, <your city> or remote from India, not frontend-only or Java/Go/.NET-only, not already tracked). Append the drop reasons to `hunts/<date>.md`, and mark rejected URLs seen: `hunt.py seen <url> ...`.

### 2. Shortlist
Rank by: fit with `my-profile` (the target roles and domains listed in `my-profile` rank highest) → form difficulty (`sources.md`: easy first) → freshness → fewer applicants. Take the **top 12–14** (a buffer, because some forms break or turn out to want 5+ years).

Post the shortlist in chat as a numbered table (company, role, why it fits in five words, form type, contact found?) and **carry on without waiting**. The user can interrupt to drop any.

### 3. Contacts (in parallel with step 4)
For each shortlisted job, look for a hiring contact the cheap way first: an email in the posting or hunt JSON, the poster of a LinkedIn or Reddit post, the "Meet the hiring team" box on LinkedIn, then `research-target` step 2–3 for a founder (small startup) or the hiring manager. Use `research-target` in full only for the top 5 and for every startup under ~50 people. The rest get a light dossier (company 3 lines + person + one hook).

### 4. Resumes (no rebuild unless needed)
For each job, score the matching base resume against the JD with `ats-check` (AI roles: `main_resume/ai_engineer`; backend, full-stack and SDE roles: `main_resume/fullstack_engineer`).
- **ATS 85+ and coverage 80%+:** upload the base resume.
- **Below that:** run `tailor-resume` → `ats-check` with `apply-job`'s gate (90+ / 85%, at most 2 rebuild rounds today; note the gap and use the best version).
- Keyword additions still need the user's approval (`ats-check`). Collect them for step 5 instead of asking one job at a time.

### 5. Pre-flight the forms, then ask once
First, check that every shortlisted posting is still open, in one call (no browser needed for most ATS links):
```bash
bash .claude/skills/career-ops/scripts/co.sh check-liveness <url1> <url2> ...
```
An `expired` posting is dropped: record it as `closed` in the hunt log, mark it seen, and pull the next job from the buffer. Open an `uncertain` one in the browser and decide there. This matters most for freehire, HN and old `careerops` rows.

Open each form in **its own tab** (`browser_tabs` new), read every field and every step (`fill-form` steps 2–3; on known portals use `portal-apply`'s `form-dump` / `li-walk` and its playbook's answer map), and map answers from `fill-form/references/answers.md`. Collect every field marked ASK across **all** jobs, plus the resume keyword questions, `guess`-confidence emails and red flags. Ask in as few AskUserQuestion calls as possible (four questions per call; group the same question across jobs, e.g. "Relocation to Pune for X and Y?"). Save the answers to `answers.md` so tomorrow needs fewer questions.

Workday and other hard forms: ask the user to sign in or create the account in that tab, then continue; if he'd rather skip them, swap in the next job from the buffer.

### 6. Fill (tab by tab)
For each job, follow `fill-form` steps 5–7: write the long answers ("why us" from the dossier), fill, upload the chosen PDF, verify with `browser_evaluate`, and **stop before Submit. Leave the tab open.** Known portals go through `portal-apply` (playbook + scripts): **Lever is chat-only: never fill it; give the user the link plus every answer in the report (Lever blocks automated fills, 2026-10-14).** Others: e.g. `li-walk` → `li-answer` → `li-submit` for Easy Apply (Claude submits Easy Apply only, the user's standing rule; first confirm the company has a public footprint (a working site or a findable founder), otherwise fill it and hold for the user (SHARQ, 2026-10-13)), `workday-myinfo` / `workday-experience` / `workday-questions` for Workday, `zoho-fill`. Pre-flight (step 5) with `form-dump`.

If a form breaks (an error, a CAPTCHA you can't pass, an expired posting), note it, mark it `closed` or skipped, and pull the next job from the buffer.

### 7. Emails
For every job with a contact, run `cold-email` (pattern B or E, or A or C for a startup with no form). Show all drafts together, take one round of edits, then save them as Gmail drafts. Then do the follow-ups from step 0.

### 8. Log everything
For each job (after `find`):
```bash
python3 $T add --company "<Company>" --role "<Exact title>" --category <company_site|linkedin_easy_apply|job_board|cold_email> \
  --platform <Ashby|Lever|LinkedIn|...> --status saved --stage "form filled, the user to submit" \
  --date_found <today> --next_action "Submit the form<, then send the Gmail draft to Name>" --next_action_due <today> \
  --job_url <posting or form link> --resume <pdf path> --ats_score <n> --location <city> --work_mode <mode> \
  --contact "<Name (title)>" --contact_email <addr> --notes "hunt <date>; <source>; draft <id>; tab <n>"
```
Email-only jobs: `--category cold_email --status lead --stage "draft in Gmail"`. Then mark every handled URL seen (`hunt.py seen ...`) and append a "Done" section to `hunts/<date>.md`: the job, tab number, resume, ATS score, draft ID, and anything skipped with its reason.

When the user says he's submitted and sent ("done", "submitted all"), check the Gmail Sent folder and the confirmation emails (`job-inbox`), then update each row: `--status applied --date_applied <today> --stage ""` and, for emails, `cold-email` step 7.

### 9. Report (short)
1. **Ready to submit:** a numbered list with the browser tab, company, role, resume (base or tailored, ATS score) and anything to eyeball, e.g. "notice 60 days vs 30 asked". Then: "Submit each tab, then tell me 'submitted'."
2. **Drafts to send:** count, plus a one-line list (to, subject). Suggest sending them Tuesday to Thursday, 9–11 am, spread out.
3. **Follow-ups drafted:** one line each.
4. **Carried over:** yesterday's unsubmitted forms.
5. **Today's count:** N/10 jobs ready, plus extra cold leads, and why it's short if under 10.
6. **Tracker:** rows added and updated. **Sources** that produced today's jobs: one line, so the mix can be tuned over time.

## Tuning over time

- Every Sunday (or when the user asks), run `tracker.py stats` and look at which channels and sources produce replies, then adjust `search.json` (keywords, boards) and the ranking.
- Add every new company board you find to `career-ops/root/portals.yml`: `bash .claude/skills/career-ops/scripts/co.sh discover-ats "Name" --summary`, then `--write` (see the `career-ops` skill). Good sources: tracker companies, `funded-startups` results, and companies behind LinkedIn hiring posts.
- Weekly: run `bash .claude/skills/career-ops/scripts/co.sh detect-reposts`. A role reposted again and again is probably a ghost job, so rank it lower and prefer a cold email to a person there. Run `co.sh verify-portals` whenever the scan prints "unreachable (slug?)".
- Not running it every day? The run still works; use `--days` to cover the gap (max 7).
