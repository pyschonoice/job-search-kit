# LinkedIn playbook

How to write the posts. The evidence and sources behind every rule are in `linkedin-posts/research.md`. Update this file when a post does unusually well or badly; `linkedin-posts/log.md` holds the numbers.

## Who reads these posts

The people we're writing for:
- <The hiring managers, founders and recruiters for the user's target roles, in <your city> and remote.>
- What they want to see: has this person shipped real AI systems, do they understand why things break, and would I want them on my team?

They read on a phone, for about 6–8 seconds, unless the first two lines earn more.

## The three pillars (stay inside them for 90 days)

LinkedIn's ranking model checks each post against the user's profile and posting history. A tight set of topics gives a strong signal; scattered topics thin out their reach. Each pillar below is backed by verified work in `my-profile`.

| Pillar | Proof they can draw on |
|---|---|
| **1. <Topic the user is credible on>**: <sub-themes> | <real projects, metrics and jobs from `my-profile`> |
| **2. <Topic>** | <...> |
| **3. <Topic>** | <...> |

`/job-setup` fills this table with the user. Pick three pillars that match the roles they want, each backed by verified work.

**Mix:** about 80% pillar posts and 20% human posts (promotion, hackathons, honest career notes, how they work with Claude Code). The human posts are what make people remember them; the pillar posts are what get them hired.

## Six post types

Pick one per post. The skeletons are guides, not templates to copy; vary the wording every time.

### A. Production lesson (the strongest for hiring managers)
1. Hook: what broke, or the surprising result, with one concrete detail or number.
2. Context: the system and its scale, in one or two lines.
3. What they tried first and why it didn't work.
4. What actually fixed it: the mechanism, specific enough that an engineer learns something.
5. The result, as a number.
6. The general lesson in one line, then a specific question for other engineers.

Image: a diagram of before vs after, or of the fix.

### B. How I built X (an architecture breakdown)
1. Hook: the hard constraint, e.g. "A wallet that can't pay anyone twice, even when jobs retry."
2. Three to five numbered decisions, each with the reason behind it.
3. What he'd do differently.
4. A question.

Image: an architecture diagram card, or a 6–10 slide PDF carousel.

### C. Opinion from experience
1. Hook: a contrarian line they actually believes, e.g. "The model was the easy part."
2. Two or three specific things from their own work that back it up.
3. The nuance: when he'd be wrong.
4. A question.

Image: optional. A simple text card, or none.

### D. Build in public (the user's own projects)
1. Hook: what they shipped or decided this week.
2. Why: the user problem.
3. One technical detail that's interesting.
4. What's next. Ask for feedback.

Image: a screenshot of the real product (cropped, framed, no client data), or a short screen recording.

### E. Checklist (saved and shared, so it reaches further)
1. Hook: "What I check before shipping a prompt change to production" or similar.
2. Five to seven items, each a short line with the reason.
3. "What would you add?"

Image: a PDF carousel, one item per slide, or a single checklist card.

### F. Human post (the 20%)
A promotion, a hackathon, a first job or a launch; how they review AI-generated code.

Image: **a real photo of the user** (a hackathon, the team, their desk). This is where a photo of a face beats everything else.

## Hooks

- The hook is the first one or two lines, **under about 200 characters, with no blank line inside it** (a blank line ends the "see more" preview early).
- Open with a concrete detail or number: something that happened to them, not a general truth.
- Good shapes:
  - "We were sending 4,000-token API responses to a service that needed 6 fields."
  - "<X>% cheaper per request, and it got faster. The fix wasn't a bigger server."
  - "A payment could have been charged twice. Here's the two-step pattern that stopped it."
- Banned shapes: "Unpopular opinion:", "Let that sink in.", "Here's the thing:", "I'm excited to announce", a question with an obvious answer, or anything that would also fit someone else's post.

## Style (set by the user, 2026-10-06)

Clean, plain writing. **Emojis: none by default**, and at most one in a post when it truly adds something. Never as bullets, decoration or a sign-off. No bold-text gimmicks, no ALL CAPS, no arrows or symbols used as decoration. Short sentences, normal punctuation.

## Body rules

- **Length:** 120–300 words. A story can run to about 1,300 characters. Stop when the point is made.
- **Paragraphs:** 1–2 sentences each, with a blank line between them. Use numbered lists only for real steps.
- **Specifics:** at least one real mechanism (a field filter, an idempotent job ID, golden test cases) and one real number. Every number must match `my-profile` exactly.
- **Voice:** follow `cold-email/references/voice.md`: plain, honest, curious, contractions, one light human touch. The "Never" words there apply here too.
- **Also never:**
  - "game-changer", "delve", "in today's fast-paced", "unlock", "supercharge", "revolutionize", "the future of X is here", "humbled", "thrilled to share", "Agree?"
  - emoji bullets or a 🚀
  - em dashes used as decoration
  - three-part "Not X. Not Y. Z." rhythms
- **The ending:** a specific question that someone with real experience could answer in a sentence, e.g. "How do you test a change before it hits real traffic?" Never "Thoughts?", "Agree?" or "Comment YES".
- **Links:** none in the body. If a GitHub repo or demo helps, the user posts it as the first comment themself.
- **Hashtags:** 0–2, specific ones only (#aiagents, #llmops). Never more than 2.
- **Tagging:** only people who were really involved (teammates, the hackathon organiser), and only with the user's OK.
- **Employer:**
  - Never name a <employer> client.
  - Never show internal dashboards, code, transcripts or unreleased numbers.
  - Only numbers that are already in `my-profile`.
  - Before the first post about <employer> work, ask the user once whether he's fine sharing it (`linkedin-posts/README.md` records their answer).
- **Job search:** never say "looking for opportunities", "open to work" or "DM me for roles" in a post. The user is employed and the posts are public. Recruiter-only Open to Work handles that.

## Quality gate (every draft must pass)

1. Does the hook make sense on its own, under 200 characters, with no blank line inside?
2. Could only the user have written this? It must have a real detail from their work.
3. Does it teach an engineer one concrete thing?
4. Is every claim and number in `my-profile` (or something the user said in this session)?
5. Does it have no client names, internal data or job-search language?
6. Is it 120–300 words, with no body links and at most 2 hashtags?
7. Does it end with a real question, not bait?
8. Read it aloud: does it sound like a person talking? Rewrite any line that sounds like a press release.
9. Is the image real and readable on a phone (see `images.md`)?

## After posting

- The user replies to every real comment within the first hour, with a reply of more than one line. That keeps the post spreading.
- Don't edit the post in the first hour.
- After 48 hours, record impressions, reactions, comments, reposts, profile views and any recruiter or hiring-manager DMs in `linkedin-posts/log.md`.
- Every 5 posts, look at what worked and update this playbook (hook types, post types, image types).

## Comment mode (about 15 minutes a day; the most direct way to reach hiring managers)

The targets:
- engineering managers, founders and recruiters at companies in `tracker/applications.csv` (open applications and cold-email leads first)
- posts saying "I'm hiring" or "my team is growing" in AI, agents or backend
- senior AI engineers with large audiences, where a sharp early comment gets seen

A good comment:
- is 2–4 sentences
- adds something from the user's own work (a number, a failure they saw, a counterpoint)
- never says "Great post!", never pitches themself, never says "please check my profile"
- may end with a short question

Workflow:
1. Draft 3–5 comments.
2. The user approves them.
3. Type each one into the comment box and leave it there for the user to post.
4. Log them in `linkedin-posts/log.md` under "Comments".
