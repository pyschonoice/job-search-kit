---
name: funded-startups
description: Find Indian startups (or India-built teams) that raised money in the last N days (default 90), pick the ones that fit the user, identify the founders, find their email addresses the safe way (published, then a pattern proven from 2+ addresses, then a labelled guess), and hand the best ones to research-target + cold-email for researched Gmail drafts. Writes outreach/funded-startups-<YYYY-MM>.md. Use when the user says "find startups that raised money", "funded startups", "recently funded", "who raised this month", "founder emails for funded startups", or "do N startups and founder emails".
---

# Recently funded startups → founder emails → drafts

Freshly funded seed to Series B startups hire fast and care less about years of experience, which makes them the user's best cold-email targets. This skill finds them; `research-target` and `cold-email` do the dossiers and drafts, and all their rules apply (never send, never invent, `find-email` rules, signature, tracker).

## Files

- `scripts/domain_scan.py <domain> ...`: for each domain, prints the page title (to confirm it's the right company), MX hosts, and every address published on `/`, `/contact`, `/careers`, `/about`, `/privacy`, `/terms`, `/team`. Privacy policies often name the founder or CTO as grievance officer (e.g. `founder@company.com`), and JSON-LD structured data often holds a founder's sales address (e.g. `founder@company.com`). Always check the context of an address before using it.
- `scripts/commit_emails.py <github-org> <domain>`: proves the address format from public commits. 2+ people in the same format = `pattern` (e.g. 4 × `first@smallest.ai`).
- `references/example-run-2026-10.py`: the October 2026 run as one script. It holds the 50-row list and 25 drafts as data, and writes the list file plus each `research.md` and `email.md`, with a word count per draft. Copy it and swap in the new data rather than writing files by hand.
- `outreach/funded-startups-<YYYY-MM>.md` (repo root): the run's list. Read the latest one first and skip companies already in it.

## Rules

- **No SMTP probing.** `outreach/tools/verify.py` asks mail servers whether mailboxes exist. `find-email` forbids that, so don't use it.
- WebSearch won't look up a named person's email. Don't try; use the order below.
- Address labels and use: `published` (on their site, a posting, or a press release) → use it. `pattern` (2+ proofs) → use it and say so. `guess` → **only after the user OKs it**, asked once for the whole batch. Otherwise fall back to the company's published `hello@`/`founders@`/`careers@`, and write the email so it still works if forwarded.
- Skip anything in the tracker (`job-inbox/scripts/tracker.py find`) or `outreach/` already, and anything that rejected the user in the last 6 months.

## Workflow

1. **Collect deals** for the window. The best sources are the weekly roundups, which list every deal with sector, round and lead investor:
   - Inc42 "Funding Galore": the tag page `https://inc42.com/tag/funding-galore/` lists each week's article (WebFetch each one: "list every startup in the funding table").
   - Entrackr weekly reports: `https://entrackr.com/report` (page 2 for older weeks).
   - YC batches with Indian teams: the YC directory, filtered by location (India) and batch, plus third-party batch lists (frontrun.vc, roundfunded).
   - Supplements: YourStory daily roundups, Tracxn/Dealroom snippets.
2. **Filter for fit.** Keep software companies in the domains listed in `my-profile` (target roles and industries) with a real engineering team. Drop consumer brands, hardware and operations-heavy businesses unless the user targets them. Note the city: <your city> or remote India first; others are OK, flagged.
3. **Founders.** One WebSearch per company (`"<company>" raises <round> founders`) gives the founders, roles, the round and what they'll use the money for. Usually there are 8 searches per batch, run in parallel.
4. **Domains and published addresses.** Run `domain_scan.py` on the likely domains (several guesses per company is fine; it filters out dead ones). Confirm the title matches; a similar name can be a different company (unveilr.ai isn't Unveilr). Then `commit_emails.py` for any company with a public GitHub org.
5. **Rank** by fit with `my-profile`: the user's strongest domains first (per `my-profile`) → adjacent domains → the rest. Take the top N (default 25) for full research and drafts.
6. **Write the list** to `outreach/funded-startups-<YYYY-MM>.md`: a table of #, company, round + date + lead, what they do, city, founder(s) + role, address + label + source, fit (★), and a "draft?" column. Below it, the sources used.
7. **Ask once** (AskUserQuestion, batched): which `guess` addresses to use, and any fit doubts (wrong city, 3+ years asked).
8. **Drafts:** for each top-N company run `research-target` (a light dossier is fine: company in 3 lines, the person, and 1–3 hooks from the funding news, product page and blog) and `cold-email` (pattern A; pattern B if they have a posted role). Show all drafts, take one round of edits, save them as Gmail drafts, and log each to the tracker as `cold_email` / `lead` / "draft in Gmail".
9. **Report:** counts, top 10 one line each, guesses awaiting OK, and when to send (Tue–Thu, 9–11 am IST, about 10 a day).

## Hooks that work for funded startups

- What they said they'll use the money for (e.g. "expand into a new channel", "build out the platform team"), bridged to the matching thing the user has built (a real project or metric from `my-profile`).
- A specific product claim on their site (latency, languages, compliance, integrations) that the user has dealt with in production.
- Never "congrats on the raise" as the whole hook; the raise is context, the bridge is the point.
