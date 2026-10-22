---
name: cold-email
description: Write personal, memorable cold emails for the user's job search and save them as Gmail drafts that they send themself. Researches the company and person first (research-target), writes in the user's own voice (references/voice.md) using proven patterns (references/playbook.md), checks every claim against my-profile, and logs every draft and send in the tracker. Also writes follow-ups and LinkedIn notes. Use when the user says "cold email X", "write to the founder of X", "email the hiring manager", "draft outreach", "follow up with X", "work through the StartupsMap leads", or when job-hunt finds a contact for a posting. Never sends.
---

# Cold email

The user names a company (and maybe a person or a posting). You research, write, save a **Gmail draft**, and log it. **the user always sends themself.**

## Hard rules

1. **Never send.** Only `create_draft` (and `update_draft` for edits the user asks for). Never `send_message`, `reply` or `forward`.
2. **Never invent.** Facts about the user come only from `my-profile` and `fill-form/references/answers.md`. Facts about them come only from the dossier, with sources. "I tried your product" only if the user actually did.
3. **Never assume.** If the person, the email address (a `guess`), the role or the angle is unclear, ask the user with AskUserQuestion, batched into one round per run.
4. **Respect the tracker.** Before writing, run `find`. Don't email a company that rejected the user in the last 6 months, or one with an open application, unless they say so (a hiring-manager email for an open application is fine: pattern B). Never email the same person twice outside the follow-up schedule.
5. **Everything is logged.** Every draft gets a tracker row; every send moves it to `cold_sent`.
6. No portfolio link unless `my-profile` lists one. No attachments (they hurt deliverability). Every email ends with the standard signature block in `references/voice.md` ("Signature"), carrying the public Drive link of the AI Engineer or Fullstack resume, whichever fits.

## Files

- `references/voice.md`: how the user writes, and the phrases they never uses. Read it every time.
- `references/playbook.md`: the patterns (A founder note, B hiring manager after applying, C "I tried it", D shared ground, E recruiter), follow-ups, LinkedIn notes, subject lines and the **quality gate**.
- `outreach/<company-slug>_<first-name>/` (repo root): `research.md` (from `research-target`) and `email.md` (drafts and history).

## Workflow

### 1. Check the tracker
```bash
T=.claude/skills/job-inbox/scripts/tracker.py
python3 $T find "<company>"
```
Note any existing row (a lead, an application, a rejection). Reuse its `id` below.

### 2. Research
Run `research-target` for the company and person unless `outreach/<slug>/research.md` is under 30 days old. You need: the person, a usable address (`published` or `pattern`; a `guess` only with the user's OK), and the three hooks.

If the dossier raises a red flag (layoffs, salary delays, rating under 3), tell the user in one line and ask before drafting.

### 3. Pick the pattern
| Situation | Pattern |
|---|---|
| Startup lead, no posted role | A (founder note), or C if the user tried the product |
| A posted role, after or with the form | B (hiring manager) or E (recruiter) |
| Real shared ground found | D opener + A or B |
| Top target the user is excited about | C: ask them to spend 10 minutes with the product first and tell you what they noticed |

### 4. Write
- Follow the skeleton in `playbook.md`: them → bridge + proof → ask → sign-off.
- Pick the **one** proof point from `my-profile` that matches their world best: match the company's domain to the user's closest project or job (for example infra company → the cost or latency win; fintech → the data-integrity work; consumer product → the shipped product). Use the exact number as written in `my-profile`.
- Write the subject line last.
- Run the **quality gate** in `playbook.md`. Count the words (`echo "<body>" | wc -w`). Fix anything that fails.

### 5. Show the user, then save the draft
Show each draft in chat (to, subject, body, the hook's source, the address confidence). For several drafts at once, show them all, then ask one AskUserQuestion: "save all", "let me edit", "skip some".

Then save the draft to Gmail (`mcp__claude_ai_Gmail__create_draft`, plain-text `body`, `to` = the address). Check the result's `viewUrl` uses `<your email>`; if the connector is on another account, stop and tell the user. Keep `id` and `threadId`.

Write `outreach/<slug>/email.md`:
```markdown
# <Company> / <Person> — <email> (<confidence>)
## Draft 1 — <YYYY-MM-DD> — pattern <X> — gmail draft <id>
Subject: ...
<body>
## Follow-up plan
- F1 due <date, +5 working days after send>
- F2 due <date, +12 working days after send>
```

### 6. Log to the tracker
- **New lead (no posting):**
  ```bash
  python3 $T add --company "<Company>" --role "Cold outreach (<angle>)" --category cold_email --platform Email \
    --status lead --stage "draft in Gmail" --next_action "Send the Gmail draft to <First name>" --next_action_due <today> \
    --contact "<Name> (<title>)" --contact_email <addr> --job_url <site> --location <city> \
    --notes "draft <draft id>; outreach/<slug>/"
  ```
- **Existing lead row** (e.g. StartupsMap): `update <id>` with the same `--stage`, `--next_action`, `--next_action_due`, `--contact`, `--contact_email`, `--notes`.
- **Posting with an application row** (pattern B or E): `update <id> --contact ... --contact_email ... --next_action "Send the Gmail draft to <First name> after submitting" --notes "HM email draft <id>"`. Keep its status and category; one opportunity, one row.

### 7. When the user says they sent it (or job-inbox sees it in Sent)
Find the sent message (`search_threads` with `in:sent to:<addr>`) to get the thread ID, then:
```bash
python3 $T update <id> --status cold_sent --date_applied <send date> --gmail_thread <thread id> \
  --stage "email 1 sent" --next_action "Follow-up 1 to <First name>" --next_action_due <send date + 5 working days>
```
For a posting row, don't change the status; just set `--gmail_thread`, `--stage "applied + emailed <name>"` and the follow-up `next_action`.

### 8. Follow-ups
When `tracker.py due` lists a follow-up (or the user asks):
- Re-read `email.md` and refresh the dossier's "Recent" section (anything new this week makes the best follow-up).
- Write follow-up 1 or 2 from `playbook.md`, under 60 words, and save it as a **reply draft** in the same thread: `create_draft` with `replyToMessageId` = the last message ID in the thread (from `get_thread`).
- Log it: `update <id> --stage "F1 draft in Gmail" --next_action "Send follow-up 1" --next_action_due <today>`. After the user sends: `--stage "F1 sent" --next_action "Follow-up 2" --next_action_due <+7-10 working days>`.
- After F2 has gone unanswered for 7 days: `--status ghosted`.
- A reply from them: `--status replied`, and help the user draft the answer (as a draft, never sent).

### 9. Batch mode (StartupsMap leads, or job-hunt hand-offs)
- `python3 $T list --status lead --category cold_email` → rank by fit with the target roles and domains in `my-profile`.
- Research all of them, then write all drafts, then **one** review round with the user, then save all drafts and update all rows. Spread the sends: suggest the user send at most ~10 a day, Tuesday to Thursday mornings, so their Gmail isn't flagged.

## Report

One line per draft: company, person, address confidence, pattern, subject, and "draft saved". Then which rows changed in the tracker, and when to send (the next weekday morning, 9–11 am IST).

## Learning

When the user edits a draft before sending, compare it with what you wrote and add the lesson to `voice.md` (a new "Do"/"Don't" row or a phrase). When a pattern gets replies, note it in `playbook.md` with the date. `tracker.py stats` shows the reply rate for each channel.
