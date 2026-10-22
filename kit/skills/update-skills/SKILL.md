---
name: update-skills
description: End-of-session skill maintenance for the user's project. Collects everything learned this session (new form answers, portal quirks and selectors, profile facts, voice edits, the user's preferences and corrections, faster ways of working, broken or outdated instructions) and writes each item into the ONE place it belongs (answers.md, portal-apply playbooks and snippets, my-profile, cold-email voice, job-inbox rules, memory), keeping files concise and free of duplicates. Run it when the session is wrapping up and you are finalising, before the final report, and whenever the user says "update skills", "save what you learned" or "keep the skills up to date".
---

# Update skills

The goal: the next session never re-learns what this one learned, and the skills stay short.

## 1. Collect (from this conversation, plus worker LEARNED lines)
List each learning in one line, tagged with its type:
- **answer**: a new form answer or decision from the user (e.g. "best repo field: profile link").
- **portal**: a portal flow, selector, widget quirk or failure (e.g. "Keka phone code is select2").
- **fact**: a new verified fact about the user's work, metrics or links.
- **voice**: an edit the user made to a draft, or wording they liked or rejected.
- **rule**: a preference or correction about how to work (e.g. "skip C2H staffing roles").
- **speed**: a cheaper or faster way something worked (e.g. "one run_code loop for N forms").
- **stale**: an instruction that turned out to be wrong, outdated or missing.

Skip one-off facts that only mattered today: tab numbers, today's job list.

## 2. Route each line to one home

| Type | Home |
|---|---|
| answer | `fill-form/references/answers.md` → "Learned answers" (dated). Mirror in `portal-apply/scripts/profile.json` if scripts use it. |
| portal | `portal-apply/references/<portal>.md` (+ fix the snippet in `scripts/snippets/`). A new portal seen twice gets its own playbook and a row in the detection table. |
| fact | `my-profile/SKILL.md`, in the right section ("Confirmed by the user (date)"). |
| voice | `cold-email/references/voice.md` |
| rule | The skill that owns that step (`job-inbox` fit filter, `linkedin-posts` decision rules, `job-hunt`...). If it applies across sessions and skills, also a memory file (feedback type) + a `MEMORY.md` line. |
| speed | The skill whose workflow it speeds up ("Token rules" / quirks section), or a new snippet. |
| stale | Fix it where it lives. Delete wrong text instead of adding a correction next to it. |

## 3. Write lean
- **Edit, don't append**, when a line already covers the topic. Search first: `grep -rn "<keyword>" .claude/skills/`.
- One line per learning, dated if it's an answer or rule. No stories.
- Keep SKILL.md files under about 150 lines: move detail into `references/`.
- Never put secrets or OTPs anywhere. Facts must come from the user or verified sources.
- When a skill's trigger or scope changed, update its `description` frontmatter (that's what routes future sessions to it).

## 4. Report (3-6 lines)
`file → what changed`, one line each, plus anything that needs the user's OK (e.g. a proposed new rule). Then give the session's final report.
