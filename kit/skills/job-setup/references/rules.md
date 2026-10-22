# Working rules (written into the workspace CLAUDE.md)

Each rule has a safe default. Stage 5 shows the list; change only what the user asks.

| Rule | Default | Options |
|---|---|---|
| Form submits | **Never submit.** Fill, verify, stop. The user clicks Submit. | Allow submit on LinkedIn Easy Apply only (after resume pick and screeners are verified). |
| Email | **Drafts only** (Gmail drafts). The user sends every email. | Never loosen. |
| LinkedIn posts | **Fill the composer, never click Post / Comment / Repost** unless the user says "post it" for that post. | Never loosen. |
| New resume claims | **Ask before adding any keyword, tool or claim** not already in `my-profile`, even to raise the ATS score. | Never loosen. |
| Unsaved form answers | **Ask, never guess.** Save the answer afterwards with the date. | Never loosen. |
| Lever forms | **Do not fill.** Give the apply link and every answer in chat (Lever blocks automated fills). | Fill if the user says it works for them. |
| Screenshots | Do not send screenshots of filled forms; read values back with `browser_evaluate`. | Allow. |
| Parallel work | With 2+ independent tasks, use the `orchestrator` skill and `browser-worker` agents. | Off. |
| End of session | Run `update-skills` before the final report. | Off. |
| Portal accounts | Ask before creating one. | Allow Claude to create Workday-style accounts using the saved shared password. |
| Experience claims | Never state more experience than `my-profile` says; never pick a higher band. | Never loosen. |
| Secrets | Passwords and OTPs only in `.secrets/`. | Never loosen. |
