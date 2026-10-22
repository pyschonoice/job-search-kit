---
name: interview-prep
description: Full prep pack for a real interview lead (a recruiter or founder call, a scheduled round). Researches the company, the interviewers and their actual tech stack (site, demo, public web-app code, LinkedIn), then writes a pack into the Obsidian study vault (study/Interviews/<Company>/) covering a brief, an architecture walkthrough with end-to-end scenarios, a question bank with model answers in the user's voice, questions to ask, and a one-page cheat sheet. It reuses and extends shared primers (voice AI stack, latency and percentiles, reliability patterns, BFSI domain, my stories) and explains every concept in plain words, then technically, with an example and a failure scenario. Use when the user says "I got a call from X", "interview with X", "prep me for X", "tell me about X and the JD", "they'll grill me", or job-inbox finds an interview invite. After the round, it logs a debrief.
---

# Interview prep

A real lead is rare and worth hours of prep. The output is a **pack the user can study, revise and speak from**, not a chat message. Everything lives in the study vault so Obsidian links it with their study notes.

```
study/Interviews/
├── _Primers/                      shared, reused across companies (extend, never fork)
│   ├── <Domain A> Stack.md        one primer per domain the user's target roles need (e.g. a streaming stack, a payments stack)
│   ├── Latency and Percentiles.md p50/p95/p99, worked maths, tail causes, measuring
│   ├── Reliability Patterns.md    queues, idempotency, retries+jitter, circuit breakers, DLQ/replay, webhooks, rate limits, Little's Law, state machines
│   ├── <Domain B> and Compliance.md  domain vocabulary, regulations, the numbers interviewers expect you to know
│   └── My Stories.md              the user's verified STAR stories + what not to claim
└── <Company>/
    ├── 00 Brief.md                company, people, role, fit, gaps, comp, status log
    ├── 01 Their Architecture.md   stack (seen vs inferred), mermaid diagram, components, 4–5 end-to-end scenarios, failure table
    ├── 02 Question Bank.md        A intro · B my work · C domain tech · D system design · E backend · F LLM · G product · H founding fit · I gaps · J live coding
    ├── 03 Questions to Ask.md
    ├── 04 Cheat Sheet.md          one page, read 10 minutes before
    └── 05 Debrief.md              after each round
```

Use the user's first pack as the model for depth and tone for the next ones.

## The explanation format (the user asked for this explicitly)

No bare buzzwords. **Every concept** in a primer or architecture note gets:
1. **In plain words**: an everyday analogy (bank token queue, <your city> buses for jitter, lift button for idempotency).
2. **Technically**: the real mechanism and correct terms.
3. **Example**: concrete, ideally from the company's own domain.
4. **When it goes wrong**: the failure an interviewer will probe.
5. **Say it**: 1–3 lines the user can speak.

Question-bank entries get: **Why they ask** · **Answer** (first person, the user's voice, spoken length) · **Follow-ups** · **Traps**. System-design answers follow: clarify → estimate (Little's Law) → components → walk one request → deep dives → failure modes → metrics → bridge to their work.

## Workflow

### 1. Gather what's already known (2 min)
- Tracker: `python3 .claude/skills/job-inbox/scripts/tracker.py find <company>`. Find the role, date applied, contact and resume used.
- Dossier: `outreach/<slug>/research.md` (research-target). The JD: the job URL in the tracker (WebFetch), or `applications/<company>_<role>/`.
- Ask the user (one AskUserQuestion, only what you can't find): who called, the round type (screen / technical / system design / founder / take-home), the date, and anything said on the call.

### 2. Research (refresh, cite, date everything)
Run `research-target` in `interview` purpose for anything stale, then go deeper than outreach needs:
- **Company site**, fully rendered: JS sites need Playwright. Get every product tab, demo widget, About, Careers, Security, Blog. The plain fetch often returns only the title.
- **Their real stack from public assets.** Follow `references/stack-scan.md`. Read only the public JS the site already serves (provider names, route names, constants) and present it as **seen**. Never call their API endpoints, log in, probe or scan anything.
- **Interviewers' LinkedIn** (read-only; research-target's limits apply): the full experience page (`/details/experience/`). Their past systems predict their questions; say so in the brief.
- Team members, funding, customers, news.
- Append findings, with dates, to `outreach/<slug>/research.md`.

### 3. Write the pack
- **Primers first:** check `_Primers/` for each concept the role needs. **Extend the existing primer** in place (new section, same format). Create a new primer only for a new domain (e.g. "Payments Rails", "RAG Systems", "Kubernetes basics"). Read before editing: the user may have annotated notes in Obsidian.
- **00 Brief:** people table with "what it means for you", the JD condensed, fit line, gaps table with honest lines, comp from `fill-form/references/answers.md`, status log.
- **01 Their Architecture:** mark every claim **✅ seen** or **🔶 inferred**. Include a mermaid diagram, component sections linking to primer headings (`[[<Domain A> Stack#6. <Heading>]]`), **4–5 end-to-end scenarios** in their domain (happy path, the classic objection, escalation, their second product, a "things break" table), and their likely next challenges.
- **02 Question Bank:** 40–60 questions. Weight toward the interviewer's background and the JD's must-haves. Include likely live-coding snippets (tested, correct Python).
- **03 Questions to Ask:** grouped by audience (CTO, CEO), each with why it's good. Include tactful phrasings for sensitive findings. List what *not* to ask.
- **04 Cheat Sheet:** at most one screen. Their stack, the interviewers, their 5 numbers, 3 bridges, one-liners, gaps, comp, closing line.
- Link everything with `[[wikilinks]]`, including study syllabus names (`[[<Syllabus item>]]`) so the graph connects to the study tracks.

### 4. Tell the user (short)
Who the interviewers are and what they'll push on, the 3 bridges, the top 5 questions to rehearse, and the gaps. Point to the pack (`study/Interviews/<Company>/`, open `00 Brief.md` in Obsidian). Offer a mock round (`study` skill, mock mode, run from `02 Question Bank.md` in the interviewer's style).

### 5. Bookkeeping
- Tracker: `tracker.py update <id> --status interviewing --stage "<round>" --next_action "<round> on <date>" --next_action_due <date> --notes "..."`. Check the valid enums with `tracker.py update -h`.
- If the `study` skill has relevant syllabus items (the role's core topics), suggest studying those first in the next session.

### 6. After each round: debrief
Write `05 Debrief.md` (append one section per round): date, interviewers, questions actually asked, what went well and what was shaky, what they revealed (stack, team, comp), next steps. Move weak topics into the primers and the question bank, and tell the `study` skill (`next-time`). Update the tracker.

## Rules
- **Verified facts only** about the user (`my-profile`). Never invent metrics, vendors, client names or experience. Where their story needs a detail that isn't recorded, mark it **⚠️ fill from memory** and, once they answer, update `my-profile`.
- **Never round up experience** (1 yr 10 mo as of 2026-10). Don't name <employer> clients.
- In interviews they say "I went through your product and demo", never "I read your JS bundle".
- Regulatory and legal facts: give the real rule only if sure. Otherwise "my understanding is… (verify)".
- Industry numbers (latency budgets etc.) are labelled "typical", never presented as their measurements.
- Plain language first; no padding. A table or diagram beats a paragraph.

## Files
- `references/stack-scan.md`: how to read a company's public front-end for stack signals (Playwright snippet), and what's off-limits.
