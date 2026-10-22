---
name: portal-apply
description: Portal playbooks and ready-made Playwright scripts for the job portals the user applies through again and again (LinkedIn Easy Apply, Workday, Lever, Ashby, Greenhouse, Zoho Recruit, Phenom, Wellfound (scan listings, read JDs, swap the profile resume, fill the apply panel), Google Forms, Keka, Workable, Infosys, Flexiple and more). Detects the portal from the URL, loads that portal's playbook (field order, selectors, known quirks, which answers it needs) and runs tested scripts instead of re-discovering the form each time. Used by fill-form, apply-job and job-hunt whenever a form is on a known portal. Use directly when the user says "apply on Workday/LinkedIn/Lever/Wellfound...", "find Wellfound jobs", "fill this Workday form", or a fill is slow because the portal's widgets fight back.
---

# Portal playbooks

`fill-form` owns the rules (never submit except LinkedIn Easy Apply, never assume, save new answers). This skill owns the **how** for each portal, so a known portal is filled in a few calls instead of twenty.

## How to use it

1. **Detect the portal** from the apply URL with the table below, then read that playbook in `references/`.
2. **Get the answers** from `fill-form/references/answers.md` as usual. Anything the playbook marks ASK (or anything not saved) still goes to the user in one batch.
3. **Run the scripts.** Scripts live in `scripts/snippets/`. Most take arguments, so build a runnable copy first:
   ```bash
   S=.claude/skills/portal-apply/scripts
   python3 $S/snip.py <snippet> '<json args>'     # prints the path of the built file
   python3 $S/snip.py list                         # every snippet with its args
   ```
   Then call `mcp__playwright__browser_run_code_unsafe` with `filename` set to the printed path (relative to the repo root). The browser sandbox can't read files, which is why args are baked in at build time. `profile.json` is merged in as `ARGS.profile` automatically, so scripts know the user's name, phone, address, CTC, notice and job history without you passing them.
4. **Verify** with the portal's `dump` snippet (or `form-dump`) before handing over, exactly as `fill-form` step 7 says.
5. **Learn.** When a portal surprises you (a new widget, a renamed field, a new question), fix the playbook and the snippet in the same session, and add a line to its "Quirks log". New portal seen twice → give it a playbook.

## Portal detection

| URL contains | Portal | Playbook | Difficulty | Account |
|---|---|---|---|---|
| `linkedin.com/jobs` + "Easy Apply" button | LinkedIn Easy Apply | `linkedin-easy-apply.md` | easy | logged in |
| `myworkdayjobs.com`, `wd1..wd108.` | Workday | `workday.md` | hard | per company |
| `jobs.lever.co` | Lever | `lever.md` | **chat-only: never fill (the user 2026-10-14), give link + answers** | none |
| `jobs.ashbyhq.com` | Ashby | `ashby-greenhouse.md` | easy | none |
| `greenhouse.io` (`job-boards`, `boards`, `embed/job_app`) | Greenhouse | `ashby-greenhouse.md` | easy | none |
| `zohorecruit.` | Zoho Recruit | `zoho-recruit.md` | medium | none (CAPTCHA) |
| `careers.<company>.com/.../apply?jobSeqNo=` (NTT DATA, Adobe) | Phenom | `phenom.md` | medium | none |
| `wellfound.com/jobs` | Wellfound | `wellfound.md` (wf-scan, wf-jd, wf-resume, wf-apply) | easy | logged in; **one profile resume per batch** |
| `docs.google.com/forms`, `forms.gle` | Google Forms | `other-portals.md` | easy | none |
| `.keka.com/careers` | Keka | `other-portals.md` | easy | none (CAPTCHA) |
| `apply.workable.com`, Workable via LinkedIn | Workable | `other-portals.md` | easy | none |
| `career.infosys.com` | Infosys | `other-portals.md` | medium | yes |
| `app.flexiple.com` | Flexiple | `other-portals.md` | easy | yes |
| `darwinbox.in` | darwinbox | `darwinbox.md` | none yet | Choices.js, see playbook |
| `jobs.clanx.ai`, `binary.so`, `workatastartup.com`, `rippling`, `smartrecruiters`, `pyjamahr`, `hire.trakstar.com`, teamtailor | other | `other-portals.md` | varies | varies |
| `torre.ai/post` | Torre | `other-portals.md` | **give the user the link** (safety check blocks browser actions) | yes (exists) |
| `haystackapp.io/.../auto-apply`, `huntingcube.ai/browse` | **not a real form** | `other-portals.md` | skip | — |

## Rules that apply on every portal

- **Submit only LinkedIn Easy Apply** (the user's standing rule, reconfirmed 2026-10-12). Everything else stops before the final button; consent and terms boxes are left for the user.
- **Resume parsers lie.** Workday, Zoho, Infosys and Lever re-parse the PDF: names in capitals, jobs merged, <past employer> dropped, dates wrong. Always overwrite parsed fields from `profile.json`, then read them back.
- **Experience truth:** use the figures in `fill-form/references/answers.md` (years + months, decimal, whole-year). Never pick a higher band.
- **Read the poster's own requirement lines** (LinkedIn "Requirements added by the job poster", HuntingCube's "5-9 Years") before filling: they often contradict the JD and decide fit.

## Files

- `references/<portal>.md`: one playbook per portal (flow, field → answer map, selectors, quirks log).
- `scripts/profile.json`: canonical answers for scripts (mirror of `answers.md`; update both together).
- `scripts/snip.py`: builds runnable snippets with args into `.playwright-mcp/run/`.
- `scripts/snippets/*.js`: the snippets. Each starts with a header comment: what it does, its ARGS, and what it returns.
