# Job sources

Ordered by yield for the user (AI/GenAI and backend roles, 0–3 years, <your city> or remote-from-India). `hunt.py` covers the "script" rows; the skill covers the rest in the Playwright browser, where the user is logged in.

| Source | How | Login | Why it's worth it |
|---|---|---|---|
| **The user's LinkedIn saved search** | Browser: `saved_search` in `search.json` (<your city>, last 24h) | yes | Their own preferences. Shows Easy Apply vs external apply, and "people you can reach out to". |
| LinkedIn jobs (guest API) | script `linkedin` | no | Same search without a login: descriptions, applicant counts, seniority. |
| Company job boards (Ashby, Greenhouse, Lever) | script `boards` | no | Direct forms that fill cleanly. Add companies to `boards` in `search.json`. |
| **career-ops scan** (~65 boards: Greenhouse, Ashby, Lever, Workday, Rippling, Workable, Zoho Recruit…) | script `careerops` (runs `tools/career-ops/scan.mjs` through the `career-ops` skill) | no | The widest direct-ATS coverage, at zero tokens. Filters by title, location and age, but returns no JD text. Add companies with `co.sh discover-ats "Name" --write` or by editing `career-ops/root/portals.yml`. |
| HN "Who is hiring" (monthly) | script `hn` | no | Founders post emails directly. Filtered to India / worldwide-remote. |
| freehire.me (aggregator, public API) | script `freehire` | no | Postings crawled from company ATS boards (Workday, Greenhouse, startup.jobs, Torre…). Queries <your city> + remote-India, non-senior tech categories, `open_within_days`; config in `search.json` → `freehire` (`skip_sources` drops IBM/Oracle). Also handy for finding a company's ATS board: the `source` field names it. |
| **LinkedIn hiring posts** | Browser: `https://www.linkedin.com/search/results/content/?keywords=<q>&datePosted=%22past-24h%22&sortBy=%22date_posted%22` with q = `hiring "AI engineer" bangalore`, `hiring backend engineer bangalore email`, `hiring "GenAI" "send your resume"` | yes | Founders and recruiters post with their email. The richest source of addresses. **Run the `linkedin-posts` skill** (scripted, pre-filtered, compact). |
| **Reddit** | Browser (plain requests are blocked): `https://www.reddit.com/r/developersIndia/search/?q=hiring&sort=new&t=week`, plus `r/developersIndia` posts flaired Hiring, `r/bangalore` search "hiring", `r/forhire` (`[Hiring]`, filter India/remote), `r/MachineLearningJobs` (search with `restrict_sr=1` and `flair:Hiring` to reach the monthly megathread) | no | Small companies posting directly, often with an email or a DM handle. **2026-10-18:** the only real yield is the r/developersIndia monthly "Who's hiring" megathread (top-level comments: `shreddit-comment[depth=0]`); r/bangalore and r/forhire returned nothing usable, and MLJobs is mostly US/contract, so skip those. |
| YC Work at a Startup | Browser: `https://www.workatastartup.com/companies?demographic=any&hasEquity=any&hasSalary=any&industry=any&interviewProcess=any&jobType=fulltime&layout=list-compact&locations=IN&role=eng&sortBy=created_desc&tab=any&usVisaNotRequired=any` | yes | YC startups hiring in India; founders reply on the platform. The user has an account (applied to Strac and AiPrise). **Limit: 5 applications a week.** Before shortlisting YC jobs, count this week's YC rows in the tracker and pick only the best ones that fit in the remaining quota. |
| Wellfound | Browser, scripted: `portal-apply` `wf-scan` over `/role/l/{ai-engineer,software-engineer,backend-engineer,machine-learning-engineer}/bangalore` (+ `?page=2`), then `wf-jd`, `wf-resume`, `wf-apply`. Playbook: `portal-apply/references/wellfound.md` | yes | Startup roles with salary bands and founder names. One profile resume serves the whole batch. |
| Instahyre, Cutshort, Hirist | Browser search, <your city>, 0–3 years. Login: `https://www.instahyre.com/login/`, `https://cutshort.io/login`, `https://www.hirist.tech/login`. Prompt the user to log in; never skip | yes | Indian startups; Hirist shows the recruiter's name. |
| Search-engine dorks | WebSearch: `site:jobs.ashbyhq.com <your city> "AI Engineer"`, `site:jobs.lever.co <your city> backend engineer`, `site:job-boards.greenhouse.io <your city> software engineer`, `site:wellfound.com/jobs <your city> AI engineer` | no | Unreliable: WebSearch ignores `site:` and returns aggregators (2026-10-13). Prefer probing ATS APIs directly (below). Add any good company to `career-ops/root/portals.yml` (`co.sh discover-ats`). |
| Gmail job alerts | `job-inbox` step 5 (LinkedIn, Glassdoor, Instahyre, Cutshort alerts) | no | Already filtered by LinkedIn's matching. |
| StartupsMap leads | `tracker.py list --status lead --category cold_email` | no | Cold-email targets with founder emails (no posting). Tops up the day's count. |

## Probing a company's board

```bash
curl -s https://api.ashbyhq.com/posting-api/job-board/<slug> | head -c 300
curl -s https://boards-api.greenhouse.io/v1/boards/<slug>/jobs | head -c 300
curl -s "https://api.lever.co/v0/postings/<slug>?mode=json" | head -c 300
```
The slug is usually the lowercase company name; the careers page's apply links show the real one.

## Form difficulty (affects ranking)

- **Easy:** Ashby, Lever, Greenhouse, Keka, Rippling, ClanX, YC WaaS, LinkedIn Easy Apply. No account needed, or already logged in.
- **Medium:** company-built forms, Darwinbox, PyjamaHR, SmartRecruiters.
- **Hard:** Workday, SuccessFactors, iCIMS, Taleo. Each needs a per-company account and long multi-step forms. Do these only when the fit is excellent; ask the user to create or sign in to the account.

## LinkedIn safety

Logged-in browsing is read-only apart from filling Easy Apply forms (never submitted). Keep it human-paced: no more than ~150 page loads and ~25 profile views a day. Stop and tell the user if LinkedIn shows a checkpoint, a CAPTCHA or a "limit reached" notice.
