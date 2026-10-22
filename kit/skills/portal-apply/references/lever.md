> **The user's rule (2026-10-14): do NOT fill Lever forms.** Lever rejects automated-filled submissions ("There was an error verifying your application", Gushwork 2026-10-13). Give the user the apply link and every answer in chat; they fill it themself. The notes below are only for drafting the answers.

# Lever (`jobs.lever.co/<company>/<id>/apply`)

**Account:** none. **Submit:** the user. Leave the "contact me about future opportunities" checkbox for them.

## Fields

Resume (required) · Full name · Email · Phone · Current location (autocomplete) · Current company · LinkedIn (often required) · Twitter · GitHub · Portfolio (leave empty) · Other website · custom "cards" (textareas, radios, selects) · EEO block on US roles.

```bash
python3 .claude/skills/portal-apply/scripts/snip.py lever-fill '{"resume":"fs","cards":[{"q":"<your city>","a":"Yes. I live in <your city> and work from here today."},{"q":"current compensation","a":"Current: <current pay + breakup>. Expected: <expected pay>."},{"q":"how quickly can you join","a":"My notice period is <notice period>."}]}'
```
Card questions are matched by regex on the question text, so write `cards` from the pre-flight dump. Long answers (AI build, "why us") come from `answers.md` blocks, adapted.

## Quirks

- Uploading the resume re-parses it and **clears Current location**; the script uploads first and sets location last, picking "<City>, <District>, <State>, <CTRY>".
- Phone is stored without the space (`<your phone>`), fine.
- "There was an error verifying your application" after Submit = Lever's bot check. The page reloads (HTTP 400) and **drops the resume** while keeping text. Re-attach (`lever-fill` with only `resume`) and let the user retry/finish the captcha. (Safe Security, 2026-10-12.)
- A hidden template error "File exceeds the maximum upload size of 100MB" is always in the DOM; ignore it.

## Quirks log

- 2026-10-12 Safe Security SDE I: 6 required cards (<your city> OK, fast-paced, stack, AI build, CTC, joining).
- 2026-10-11 Hevo SDE I, 2026-10-06 Omnidian, Weekday client: standard fields only.

- 2026-10-13 (Gushwork): cards can include a tech-stack **checkbox list**, which `lever-fill` text cards don't handle. Click each checkbox label. Referral textarea: give the real source (e.g. "Gushwork careers page (Lever)").
