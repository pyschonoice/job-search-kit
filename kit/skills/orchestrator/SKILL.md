---
name: orchestrator
description: Session-wide work distributor for the user's job-search project. The main agent stays the orchestrator - it splits work into independent tasks and hands each one to a `browser-worker` subagent with only the context and skill that task needs. Workers run in parallel, each in its own tab of the one shared Playwright browser. The orchestrator opens and closes workers as tasks finish, merges results, and is the only one that writes the tracker, answers.md and skills. Use at the start of any session, or mid-session, whenever there are 2+ independent tasks of more than a few tool calls each (several forms, several posts or JDs, emails plus forms, a hunt batch). Saves time and tokens versus doing it all in one context.
---

# Orchestrator

You (the main agent) **plan, brief, merge and write**. Workers **do**. Keep your own context small: never read a worker's raw pages, only its 15-line return.

## When to fan out
- **Do:** 2+ independent units of work, such as forms to fill, posts or JDs to read, companies to research, or emails to draft, each needing more than about 3 tool calls.
- **Don't:** one small task, steps that depend on each other (do them in order yourself), or anything that needs a decision from the user first. Ask first, in one AskUserQuestion batch, then fan out.

## Loop
1. **Plan.** Make the task list. For each task: tab key (a URL fragment unique to it), skill(s) to load, the facts it needs, done criteria. Run things only you can do (AskUserQuestion, approvals) before fanning out.
2. **Brief and launch** (Agent tool, `subagent_type: "browser-worker"`, background). Up to **4 browser workers at once**, and **at most 1 on linkedin.com** (rate limits and logged-in session). Non-browser research can use `general-purpose` workers. Brief template:
   ```
   TASK: <one job, one company/role>
   SKILLS: <e.g. fill-form + portal-apply (Keka playbook)> | cold-email | research-target
   INPUT: <URL(s), JD summary, resume path, which answers apply, decisions the user already made>
   TAB KEY: <unique URL fragment, e.g. keka.com/careers/applyjob/91601>
   DONE WHEN: <e.g. every field filled and read back, left open, not submitted>
   RETURN: the browser-worker format
   ```
   Put only what that task needs in the brief, never the whole conversation. Pass decisions the user already made (for example "apply even if 3+ yrs") so the worker doesn't ask again.
3. **Keep the pipeline full.** When a worker returns, merge its result and launch the next queued task. Don't wait for the whole batch. Collect every worker's ASK items and put them to the user in one AskUserQuestion. Then send each answer back to the worker that asked (SendMessage), or start a fresh worker.
4. **Write (single writer).** You alone run `tracker.py add/update`, append to `answers.md`, and edit skills and memory, using each worker's LOG and LEARNED lines. Two workers writing the CSV at the same time would corrupt it.
5. **Close.** Tell the user which tabs are waiting for them (tab key → company/role). Close tabs only for skipped or finished-and-submitted work. At session end, run `update-skills`.

## Shared-browser rules (why the tabs don't collide)
- There is one Playwright MCP browser. Click, snapshot and fill tools act on the "current" tab, so in parallel they collide. **Workers use only `browser_run_code_unsafe`** and find their own tab by URL. You (the orchestrator) don't drive the browser while workers run.
- "Browser is already in use" means another Claude session holds the profile. Ask the user before killing it, because it may hold unsubmitted forms.
- Logins, CAPTCHAs and OTPs block a worker. It reports them, and you ask the user once for all of them.

## Cost notes
- A worker starts cold and reloads its skill, so fan out only when the task is bigger than about 3 calls.
- The worker model is set in `.claude/agents/browser-worker.md` (`model: sonnet`, for cheaper tokens). Change it there if quality drops on hard forms (Workday).
