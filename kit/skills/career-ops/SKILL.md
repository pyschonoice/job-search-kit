---
name: career-ops
description: Zero-token job-search scripts vendored from the open-source career-ops project (tools/career-ops). Scans ~65 company job boards (Greenhouse, Ashby, Lever, Workday, Rippling, Workable, Zoho Recruit and 100+ other ATS providers) from one watchlist, checks whether a posting is still live before a form gets filled, flags ghost or reposted jobs, and finds a company's ATS board from its name so it can be added to the watchlist. Used by job-hunt (step 1 source `careerops`, liveness check in step 5). Use directly when the user says "scan the boards", "is this job still open", "check these links", "add <company> to the watchlist", "find <company>'s job board", "ghost jobs" or "reposts".
---

# career-ops (vendored scripts)

The scripts come from [career-ops-hq/career-ops](https://github.com/career-ops-hq/career-ops) (MIT, `tools/career-ops/UPSTREAM` has the pinned commit). Only the parts that run without an LLM are used. Its A–H evaluation, CV builder, tracker and email modes are **not** used: `tailor-resume`, `ats-check`, `fill-form`, `cold-email` and `job-inbox` already cover those, with the user's rules.

Always run through the wrapper, which sets `CAREER_OPS_ROOT` to `root/` in this skill (config + state) and installs deps the first time:
```bash
CO=.claude/skills/career-ops/scripts/co.sh
bash $CO <script> [args]     # script = file name in tools/career-ops without .mjs
```

## Files

- `root/portals.yml`: the watchlist + filters. Title filters mirror `job-hunt/references/search.json`. Location allows <your city> / India / remote and blocks other countries. Postings older than 30 days are dropped.
- `root/config/profile.yml`: country and city only. The user's real profile stays in `my-profile`.
- `root/data/` (gitignored, per device): `scan-history.tsv` (scanner dedupe + repost history), `pipeline.md` (last scan's new offers), `portal-health.tsv`.

## What to use

| Need | Command | Notes |
|---|---|---|
| Scan every board | `bash $CO scan --json --quiet --since 21` | `job-hunt`'s `hunt.py` already calls this (source `careerops`), so don't run it separately during a hunt. `--dry-run` previews without writing. `--company "Rippling"` scans one company. A URL comes back once, then again after 7 days if it wasn't handled (`recheck_after_days`). |
| Is a posting still open? | `bash $CO check-liveness <url> [url...]` | Uses the free API first, then Playwright. Exit code 1 if any posting is expired or uncertain. Works on Greenhouse, Ashby, Lever, Workday, LinkedIn and more. `--file urls.txt` checks a batch. |
| Ghost jobs / reposts | `bash $CO detect-reposts` | Same role re-listed with new URLs on separate scan dates within 90 days. Needs a few weeks of scan history. A repost is a weaker lead: still fine to apply, but prefer a cold email to a person over the ATS. |
| Find a company's board | `bash $CO discover-ats "Name" ["Name" ...] --summary` | Probes Greenhouse, Ashby, Lever, Workable, SmartRecruiters, Recruitee, BambooHR, Breezy, Pinpoint, Rippling and Join. `--write` appends what it resolves to `root/portals.yml`. Indian companies on Keka, Darwinbox or Naukri RMS show as unresolved: those stay browser sources. |
| Check the watchlist | `bash $CO verify-portals` | Finds dead slugs. `--add <name>` tries slug variants. Run it when a scan prints "unreachable (slug?)". |
| Funding news | `bash $CO company-funded --months 3 --dry-run` | TechCrunch, PR Newswire and HN funding posts, mostly US. Extra input for `funded-startups`, which stays the main India source. |

## Adding companies to the watchlist

1. Collect the names: a company the user applied to, a funded startup, or a company from a LinkedIn post.
2. `bash $CO discover-ats "A" "B" --summary` → check the result looks right → rerun with `--write`.
3. Or add an entry by hand to `root/portals.yml`:
   ```yaml
     - name: "Company"            # display name, ends up in the tracker
       careers_url: https://jobs.ashbyhq.com/slug   # or <tenant>.wd3.myworkdayjobs.com/<site>, ats.rippling.com/<slug>/jobs ...
       notes: "why it's here"
       enabled: true
   ```
   Supported URL shapes: `tools/career-ops/templates/portals.example.yml`, "Provider auto-detection". Keka and Darwinbox aren't supported.
4. `bash $CO scan --dry-run --company "Company"` to confirm it returns jobs.

`job-hunt/references/search.json` `boards` still feeds `hunt.py`'s own boards source, which brings back JD text. Put new companies in `portals.yml`, not `search.json`.

## Updating from upstream

```bash
git clone --depth 1 https://github.com/career-ops-hq/career-ops /tmp/co-up   # scratchpad dir, not the repo
```
Then copy over the same file set as the original vendoring: root `*.mjs` (not `test-all.mjs`), root `*.json` (`tracker-aliases.json`, `funding.json`, `package.json`), `lib/`, `providers/`, `templates/`, `config/`, `data-static/`, `utils/`, `plugins/`, `batch/` (not `logs`), English `modes/*.md` plus `modes/{interview,heuristics,pdf,oferta-signals,regional}`, and `scripts/{check-syntax,export-ats-text}.mjs`. Next, update `UPSTREAM`, run `npm install`, then `bash $CO scan --dry-run` to confirm it still works. Never overwrite `root/`.

## Rules

- These scripts only read public job boards. They never submit, never send and never write the tracker. The tracker stays with `job-inbox`'s `tracker.py`.
- Don't use the career-ops LLM modes (`modes/*.md` evaluation, CV, cover letter, `batch/`) in place of the user's skills. The exception: `modes/interview-prep.md` and `modes/interview/` are fine references when preparing for an interview, as long as every claim comes from `my-profile`.
