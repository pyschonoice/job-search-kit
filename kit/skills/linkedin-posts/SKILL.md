---
name: linkedin-posts
description: Find LinkedIn hiring posts (search, last 24h or week), keep the ones that fit the user, and act on each - fill the linked form (never submit), or draft an email to the address in the post, or find the poster's / company HR email and draft to that. Also handles a single LinkedIn post URL the user pastes ("apply to this post", "fill this", "there are two links, figure out the right one"). Use when the user says "check LinkedIn posts", "scroll LinkedIn for hiring posts", "find hiring posts", pastes linkedin.com/posts/... links, or when job-hunt reaches its "LinkedIn hiring posts" source.
---

# LinkedIn hiring posts

Lean loop: **scrape compact → decide in chat → act → log**. Rules from `fill-form` (never submit; never assume), `cold-email` (voice, signature, never send) and `job-inbox` (tracker) all apply.

```bash
L=.claude/skills/linkedin-posts/scripts/li.py
python3 $L build [--hours 24|168] [--queries "q1" "q2"]   # -> .playwright-mcp/run/li-posts.js
python3 $L resolve https://lnkd.in/xxxx ...               # real target of short links
python3 $L seen "<key>" ...                               # after handling (kept or skipped)
```

## 1. Get posts
- **Pasted post URLs:** WebFetch each one (no browser needed) and ask for: company, role, location, experience, every link and email, and how to apply. Then `li.py resolve` every `lnkd.in` link. Several URLs → one turn, all in parallel.
- **Feed** ("scroll my feed"): `li.py build --feed --scrolls 40` (about 80 posts, about 3 minutes). The feed scrolls inside `<main>` and unmounts old posts, so the snippet collects at every step and needs the tab in front. Hiring posts in the feed are rare (1-2 fits per 80), so pair a feed run with a search run when the user wants volume.
- **Search:** `li.py build`, then `browser_run_code_unsafe` with `filename` = that path. It returns `{kept:[{key, who, age, head, yrs, loc, emails, links}], dropped:{reason:n}}`. It already filters out: posts that aren't hiring, aggregator/"N job openings" lists, internships and fresher roles, ads and noise (Promoted, 'starting a new position', tutor gigs), non-engineering roles (PM, frontend-only, support, analyst), minimum experience above 4 years, senior/lead/manager in the post text (not the poster's headline), and .NET/Java/SAP/QA/mobile stacks. `NOT LOGGED IN` → ask the user to log in to LinkedIn in the Playwright window.

## 2. Pick the right link (posts often carry two)
- Resolve every short link first. **Wrong links:** credit-card or other affiliate ads (Rivo, onelink.me, bit.ly promos), WhatsApp/Telegram job channels, the poster's own course or newsletter, a generic careers index. **Right link:** an ATS or form (keka, lever, ashby, greenhouse, workday, forms.gle, binary.so, the company's careers job page).
- If the post says "email only", the email is the application. A careers page with per-role forms as well → **referral email first** (it gets more interviews), and fill the forms but leave them unsubmitted.

## 3. Decide (in chat, one short table)
Fit rule: `job-inbox` step 5. The user's overrides (2026-10-13): apply even when 3+ or 4 years are asked; skip contract-to-hire roles through staffing firms that want immediate joiners; skip HR/people-team posts. Check `tracker.py find <company>` before acting: if they already applied, add an email only when the post asks for one.

## 4. Act
| Post gives | Do |
|---|---|
| Form or ATS link | `fill-form` (+ `portal-apply` playbook). Several forms → `orchestrator` (one browser-worker per form), or one `browser_run_code_unsafe` loop. Multi-page Google Forms: fill page → click Next → dump the next page, in one call per page; stop on the page that shows Submit. |
| Email address | Draft with `cold-email` voice and signature, subject as the post asks. Resume link: AI Engineer for AI roles, Fullstack for backend/full stack. |
| Neither (DM only) | `research-target` steps 2-3 for the poster's or company HR email; if none, write a LinkedIn DM text in chat for the user. |

## 5. Log
`tracker.py add`: the form row as `saved` + "form filled, the user to submit"; the email row as `cold_email`/`lead` + "draft in Gmail" (or `referral` with the referrer in `contact`). Put the post author and which link was wrong in `notes`. Then `li.py seen` every key you handled or skipped.

## Token rules (learned 2026-10-13)
- Never `browser_snapshot` a LinkedIn page: one snapshot costs more than the whole scrape. Use the snippet.
- `browser_run_code_unsafe` echoes its code: keep long logic in snippet files and pass `filename`.
- Read forms with one `evaluate` dump (label, type, options), not snapshots. Google Forms: options are `[role=checkbox|radio][aria-label]` (a "confirm" box is usually a checkbox); resume upload goes through the Drive picker iframe (`Browse` → filechooser) and needs the Google login, which the Playwright profile has.
- If the Playwright profile is locked ("Browser is already in use"), another session holds it: ask the user before killing it, because it may hold unsubmitted forms.
