---
name: linkedin-post
description: Write LinkedIn posts for the user that get them noticed by hiring managers and recruiters. Picks a topic from their verified work (my-profile) inside their three content pillars, writes in their own voice using the research-backed playbook, makes 1–3 real images when the post needs them (diagram, code, checklist or screenshot cards rendered to PNG, PDF carousels, or their own photos), saves everything under linkedin-posts/, and puts the post into LinkedIn's composer for the user to publish. Also drafts comments on hiring managers' posts and tracks results. Use when the user says "write a LinkedIn post", "post about X", "what should I post", "make a carousel", "LinkedIn content", "draft comments", or "log my post stats".
---

# LinkedIn post

The user wants posts that make hiring managers and recruiters at AI-first companies think "this person would be good on our team". You find the topic, write the post, make the images, and set it up. **the user presses Post.**

## Hard rules

1. **Never publish.** Fill LinkedIn's composer (text and images) and stop. Never click "Post", "Repost", "Send" or "Comment". Publishing is the user's call every time, unless they say "post it" for one specific post in this session.
2. **Never invent.** Every fact, number, tool and date comes from `my-profile` or from the user in this session. Numbers stay exactly as written ("up to 95%", not "95%"). If a post needs a detail that isn't there (a failure they hit, a before/after figure), ask them.
3. **Never assume.** If the topic, an image, the confidentiality of a work detail, or anyone being tagged is unclear, ask with AskUserQuestion, in one round per run.
4. **Protect their job.**
   - Never name <employer> clients, and never show internal dashboards, code, transcripts or prompts.
   - Don't use unreleased numbers.
   - Never write "looking for opportunities" or "open to work" in a post.
   - Their first <employer>-based post needs their explicit OK; the answer is recorded in `linkedin-posts/README.md`.
5. **Real images only.** Use diagrams and code cards they can stand behind, screenshots of their own products, and photos they give you. Never AI-generated people, stock images or memes.
6. **No portfolio link** unless `my-profile` lists one. GitHub and demo links go in the first comment, which the user adds themself.

## Files

- `references/playbook.md`: who reads the posts, the three pillars, six post types, hooks, body rules, banned words, the **quality gate**, what to do after posting, and comment mode. Read it every time.
- `references/images.md`: which image fits which post type, specs, how to make cards and PDF carousels.
- `cold-email/references/voice.md`: how the user writes. The "Never" phrases apply to posts too.
- `templates/card.html`: the image card (layouts: diagram, code, statement, checklist, frame). `scripts/render.sh` turns it into a PNG.
- `linkedin-posts/` (repo root):
  - `README.md`: settings and decisions
  - `research.md`: the evidence behind the playbook
  - `ideas.md`: the backlog of topics
  - `log.md`: every post and its numbers
  - `posts/<YYYY-MM-DD>_<slug>/`: `post.md` plus the images

## Workflow

### 1. Pick the topic
- If the user names one, use it. If they say "what should I post", read `linkedin-posts/ideas.md` and `log.md`, then offer 3 options in one AskUserQuestion. Each option needs a pillar, a post type, a one-line hook and an image plan.
  - Rotate the pillars.
  - Don't repeat a post type twice in a row.
  - Keep about 1 in 5 posts as a human post.
- Check `log.md` so you don't repeat a topic from the last 30 days. A follow-up angle on an old topic is fine.

### 2. Gather the substance
- Pull the facts from `my-profile`.
- For depth, read the real code (local repo paths listed in `my-profile`) for the mechanism: the actual function, the job ID pattern, the filter.
- Ask the user for the one human detail that makes the post their: what broke first, what surprised them, what he'd do differently. Give them two or three guesses to pick from, so they can answer in one click.

### 3. Write
- Follow the post type's skeleton in `playbook.md`, in the user's voice.
- Write 2 hook options, and pick the stronger one as the lead.
- Run the **quality gate**. Count the words (`wc -w`) and the hook's characters.

### 4. Make the images (when the post needs them)
- Follow `images.md`: 1–3 images, or one PDF carousel.
- Render each image, then **look at each PNG with Read** before showing it. Fix any overflow, small text or empty space.
- Write one line of alt text per image.

### 5. Save and show
Save `linkedin-posts/posts/<YYYY-MM-DD>_<slug>/post.md`:
```markdown
# <slug> — pillar <n> — type <A–F> — status: draft
Planned: <weekday date>, 8:30 AM IST
## Hook options
1. ...
2. ...
## Post
<final text, exactly as it will be pasted>
## Images
- img1.png — alt: "..."
## First comment (the user posts it themself; optional)
<link or extra detail>
## Sources
- <my-profile line / repo file for every fact>
```
Show the user the post, the images and the planned time. Then ask: "set it up in LinkedIn", "edit", or "save for later".

### 6. Set it up in LinkedIn (only when the user says so)
1. Open linkedin.com/feed with the Playwright browser. If it isn't logged in, ask the user to log in in that window and wait.
2. Click "Start a post" and paste the text exactly. Keep the line breaks: type the text, or set it in the editor and check it.
3. Add the images with the media button (`browser_file_upload` with absolute paths), in order. For a carousel, use "Add a document", upload the PDF and give it a title.
4. Add alt text to each image if the editor offers it.
5. **Stop.** Tell the user it's ready in the composer, and remind them: the best time is 8–9 AM IST, Tuesday to Thursday; reply to comments in the first hour; don't edit for an hour; add the first-comment link if there is one.
6. Don't take screenshots of the composer for them; just say it's ready.

### 7. Log it
- Add a row to `linkedin-posts/log.md` with status `ready`.
- When the user says it's live, change the status to `posted` and add the URL and date.
- After 48 hours, or when they say "log my post stats", read the numbers from the post's analytics in the browser and fill in the row: impressions, reactions, comments, reposts, profile views, and any DMs from recruiters or hiring managers.
- Mark the idea `used` in `ideas.md`.

## Comment mode
When the user says "draft comments" or "do my 15 minutes", follow "Comment mode" in `playbook.md`.
1. Find 3–5 fresh posts by hiring managers, founders or recruiters at tracked companies (`tracker/applications.csv`), or "I'm hiring" posts in AI or backend.
2. Draft the comments and show them together.
3. Once they approve, type each one into its comment box and leave it there for them to post.
4. Log them in `log.md` under "Comments".

## Learning
- When the user edits a draft, compare it with what you wrote and add the lesson to `cold-email/references/voice.md` (under a "LinkedIn" heading; add it if it is missing) or to `playbook.md`.
- Every 5 logged posts, compare them: which hook type, post type, image type and day did best? Write the conclusion with a date at the end of `playbook.md`, and adjust `ideas.md`.

## Report
One short block:
- the post's hook
- pillar and type
- word count
- the images, with their paths
- the planned slot
- whether it's in the composer or saved for later

Then the next idea from the backlog.
