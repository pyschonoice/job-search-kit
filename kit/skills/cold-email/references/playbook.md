# Cold email playbook

Patterns distilled from cold emails that are known to have worked for engineers and from published reply-rate data. Pick **one** pattern per email. Don't stack them.

## What the evidence says

- **Short wins.** 50–125 words is the sweet spot. Studies of millions of sales emails put the reply-rate peak there (about 2x the rate of 200+ word emails). Hiring emails behave the same way: the people reading them are busy founders and managers. ([Nick Singh](https://www.nicksingh.com/posts/cold-email-tips-to-land-your-dream-job-with-examples), [Next Play](https://nextplayso.substack.com/p/the-guide-to-getting-a-job-with-cold))
- **Email the person who can say yes.** At a startup that's a founder; at a bigger company it's the hiring manager. Emails sent straight to hiring managers get reported reply rates around 15–25%, against 2–5% for portal applications. These are vendor numbers, so read them as direction, not truth. ([Colin Keeley](https://www.colinkeeley.com/blog/cold-email-your-way-into-an-internshipjob-at-any-startup), [pitchhired](https://pitchhired.com/blog/cold-email-reply-rates-job-search-data))
- **Specific beats polite.** An opening about a real detail of their work lifts replies sharply over a generic opening. A "signal" (a recent launch, a post, a hiring push) works best. ([autobound](https://www.autobound.ai/blog/cold-email-guide-2026))
- **One clear ask.** Name the role or the conversation. "Let me know if you're interested" and "happy to connect" give the reader nothing to do.
- **Persistence works, politely.** Tristan Walker got their Foursquare job after eight follow-ups. Most guides land on 2–3 touches, each with something new. We do **two** follow-ups.
- **Timing.** Tuesday to Thursday, around 9–11 am in the reader's time zone. Avoid weekends and Indian holidays.

Famous short examples worth keeping in mind:
> "Hey, my name's Niraj Pant. I understand your time is valuable. I'll only write three bullet points. Programming since 8th grade. Have most experience working in Java/Obj-C/Android/iOS. Want to intern for Snapchat this summer as a high school junior. How?" (got a reply from Snapchat's CEO)

> "Hey Ryan - [product] is so good. Used it last week for [reason] and was impressed (especially by how good the notification selection/timing is). Question: how are you doing on copywriting at the moment?" (product-first opener)

## The skeleton (every pattern follows it)

1. **Them** (1 sentence): the hook from the dossier. Something specific they built, wrote or launched, with the detail that caught the user's eye.
2. **Bridge + proof** (1–2 sentences): why that connects to what the user has built, with **one** real number from `my-profile`.
3. **Ask** (1 sentence): specific and small.
4. **Sign-off:** the standard signature block from `voice.md` ("Thank You," / name / phone / email / resume, linkedin, github links), with the right resume link.

Word budget: 60–120 words in the body. A subject line of 3–7 words.

## Patterns

The company details in these examples (ZOKO, Seekho, Retape and the people named) are **made up to show the shape**. Real emails take every fact about the company from its dossier. The user's facts are real.

### A. Founder note: no posted role (startups under ~50 people)
For StartupsMap leads and small startups. Ask to be considered for an engineering role, or for 15 minutes.

> Subject: your WhatsApp + voice handoff
>
> Hi Arjun,
>
> Noticed ZOKO now lets brands run order updates and support on one WhatsApp number, and the hard part there is keeping context when a customer jumps between channels.
>
> That's what I work on at <employer>: I built the context layer that feeds WhatsApp messages into live voice agents mid-call, across <scale metric>.
>
> Are you hiring backend or AI engineers this quarter? I'd like to be considered, and I'm happy to do a take-home first.
>
> Thank You,
> The user
> ...(standard signature block, voice.md)

### B. Posted role: email the hiring manager after applying
Use after the form is filled (or with it). Reference the role by its exact title and say the application is in.

> Subject: SDE-2 backend: agents in production
>
> Hi Priya,
>
> Saw Seekho is hiring an SDE-2 for backend. Your post about moving recommendations to an event-driven pipeline was the reason I applied rather than scrolled past.
>
> I run <stack> services at <employer> (<scale metric>), and before that I built <project> on my own, with <one concrete mechanism>.
>
> I've applied through the careers page. Would you be open to a short chat about the team?
>
> Thank You,
> The user
> ...(standard signature block, voice.md)

### C. "I tried it": the most memorable pattern, for top targets only
The user spends 10–20 minutes with the product (demo number, sandbox, docs, public API) and reports one real observation: something that impressed them, a rough edge, or a small idea. **Only use observations the user actually made.** Never invent a bug or an experience. Ask them to try it, or skip this pattern.

> Subject: called your demo agent
>
> Hi Sahil,
>
> I called Retape's demo line this morning. The agent handled me interrupting mid-sentence better than most I've tested, but it lost my account number after I switched topics.
>
> That exact problem (keeping state across turns and channels) is my day job at <employer>, where our agents take <scale metric> for BFSI clients.
>
> I'd like to work on this with you. Open to a 15-minute call this week?
>
> Thank You,
> The user
> ...(standard signature block, voice.md)

### D. Shared ground: a warm start
Use when the dossier shows real common ground: <your university>, <employer> or <employer>, the same hackathon, the same niche tool. Lead with it in one clause, then use skeleton A or B.

> Hi Ankit, fellow <your university> grad here (CSE, 2025).

### E. Recruiter, short and factual
Recruiters want fit facts fast. Give the role, three facts and an ask. No hook needed, but still no keyword lists.

> Subject: GenAI Engineer (R-1234): the user
>
> Hi Neha,
>
> I've applied for the GenAI Engineer role (R-1234). Quick fit check: production AI voice and chat agents at <employer> for BFSI and D2C clients (<scale metric>), <one more real number>, and <N> years of experience in <your city>. Notice period is <notice>.
>
> Could you check whether my profile is a match for the hiring manager?
>
> Thank You,
> The user
> ...(standard signature block, voice.md)

## Follow-ups (reply in the same thread)

- **Follow-up 1, after 4–5 working days.** Add something new: a short thought on their latest launch, a link to something relevant the user built, or a sharper ask. Never just "bumping this" or "just following up".
  > Hi Arjun, one more thought since my last note: <new, specific thing>. Still keen to talk if you're hiring for backend this quarter.
- **Follow-up 2, after 7–10 more working days.** Close the loop, kindly and briefly.
  > Hi Arjun, I'll stop filling your inbox after this one. If the timing's wrong now, I'd still like to stay in touch for later. Good luck with <specific thing>.
- After that, mark the row `ghosted`. Don't send a fourth email.

## LinkedIn companion note (optional, 300 characters max)

Send the connection request after the email, not instead of it:
> Hi Priya, I emailed you about the SDE-2 backend role at Seekho. I build production AI agents at <employer> (<scale metric>). Would be glad to connect.

## Subject lines

- 3–7 words, lowercase except names, specific to them: "your checkout latency", "tried your demo", "SDE-2 backend: payments in production", "<their product> + a caching trick".
- Never: "Application for ...", "Job opportunity", "Request for ...", "Introduction", "Quick question" (too generic), all caps, emojis, or a fake "Re:".

## Quality gate (check every draft before saving)

- [ ] The first sentence is about **them**, and it's specific enough that it couldn't be sent to another company.
- [ ] The body is 60–120 words (recruiter pattern: up to 90).
- [ ] Exactly **one** number, and it's true per `my-profile` (a number copied exactly from `my-profile`).
- [ ] No keyword list, no phrase from the "Never" list in `voice.md`.
- [ ] One ask, a question they can answer with yes or no.
- [ ] Every fact about them is in the dossier with a source.
- [ ] No claims beyond `my-profile`: experience as stated in `my-profile`, and nothing described as in production unless `my-profile` says so.
- [ ] Reads naturally aloud. If a line sounds like a cover letter, rewrite it.
- [ ] Mentions nothing from Glassdoor or AmbitionBox, and nothing personal beyond professional public info.
