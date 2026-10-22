# Classifying job-search email

Patterns seen in the user's inbox (<your email>). Add new ones when you learn them.

## Application systems (update the tracker)

| Sender | Confirmation looks like | Rejection looks like |
|---|---|---|
| `<company>@myworkday.com` (Expedia, Visa, Cisco, HPE, Lowe's, Nike, Airbus `ag@`) | Subject "Thank you for your application for <role> - R-xxxx", "You have successfully applied", "Thank you for your online submission", "Your application is under review" (auto, so still `applied`) | Subject **"Thank you for your interest in <company>"** or "Thanks for Considering <company>"; body "move forward with other candidates" / "regret to inform". The two Expedia subjects look alike; **the subject decides it**, so open the body when unsure. |
| `no-reply@ashbyhq.com` | "Thanks for applying to <company>!" | "<role> Application Update - <company>" with "isn't an ideal fit" |
| `donotreply@successfactors.com` (NetApp) | "<company> has your application!" | "Your Application at <company>" with "will not be able to consider you" |
| `no-reply@ats.rippling.com` | "Thank you for applying to <company>" + "will review it promptly" | Same subject, body "While we were impressed..." → rejection. **Open the body.** |
| `no-reply@kekamail.com` | "Application for <role> received" | — |
| `*@*.pyjamahr.com` | — | "Thank you for applying at <company>!" + "After going through your..." → rejection |
| `*@recruitee-email.com` (ClanX) | "<role> - Confirmation of your application", replies in 5–7 working days | — |
| `support@match.jobgether.com` | "Next Steps for Your Job Application" (Jobgether screens first; still `applied`) | — |
| `workatastartup@ycombinator.com` | "Your application for <company> - <role>" | — |
| `messages@binary.so` | — | "RE: Update on your application" + "won't be moving forward" |
| `no-reply@deel.com` | "Your application has been received!" | — |
| `alerts@ta.idfcfirstbank.com` | OTP only, so the application may not have been submitted | — |

## LinkedIn

| Sender | Meaning | Action |
|---|---|---|
| `jobs-noreply@linkedin.com`, "your application was sent to <company>" | Easy Apply confirmation | `add` as `linkedin_easy_apply`, `applied` (role is usually only in the body) |
| `jobs-noreply@linkedin.com`, "Your application to <role> at <company>" | Status update: viewed, or "not moving forward" | **Open the body**: viewed → note it; declined → `rejected` |
| `mailer-daemon@googlemail.com`, "Delivery Status Notification (Failure)" | A cold email bounced ("Address not found" or "Message blocked"). The thread is the one the user sent. | **Tracker update:** find the row by `contact_email`, set `stage="email bounced"`, `next_action="Find a working address (research-target) and resend"`. List bounces under Do today. |
| `inmail-hit-reply@linkedin.com` | Recruiter InMail (body has the full text and a reply link) | **Act now.** `recruiter_inbound`. Draft a reply from `answers.md`. |
| `messaging-digest-noreply@linkedin.com`, "<Name> just messaged you" | A DM. The body shows the sender's title and company, not the text. | **Act now** if the person works somewhere relevant (e.g. at a company the user applied to → ask for a referral). |
| `jobs-noreply@linkedin.com`, "apply now to <saved job>" | Reminder about a saved job | Posting candidate |
| `jobalerts-noreply@linkedin.com`, `messages-noreply@linkedin.com` "is hiring" | Job alerts | Posting candidates (fit filter) |
| `updates-noreply@`, `notifications-noreply@`, `newsletters-noreply@` | Feed noise | Ignore |

## Humans

Any email from a person at a company domain (recruiter, talent partner, founder), calendar invitations ("Invitation:", "Updated invitation:"), and replies to the user's sent mail. **Always "act now"** unless the user already replied (check the thread for a `SENT` message after theirs).

## Postings (fit filter in SKILL.md)

LinkedIn job alerts, Glassdoor ("<role> at <company> and N more jobs"), HireFT (match %), company talent communities (`*@noreply*.jobs2web.com`, `RecruitingNoReply@<company>.com`, `noreply@<company>.com`), Instahyre, Wellfound, Cutshort.

## Noise (count it, suggest unsubscribing)

Expert-network gig pitches for paid AI studies and coding-eval contract work (the user is not interested, so do not track them), `noreply@jobalertshub.com` (government and PSU notices), Internshala (MBA ads, trainings), `jobalerts@info.apna.co`, UNIPREP "employer viewed your profile", Glassdoor community posts, Substack newsletters, Steam, Amazon/Swiggy/Furlenco orders, bank transaction alerts.

## Work admin worth surfacing

Mails from the current employer's tools (e.g. <employer> via Lawcubator: mandatory POSH training with a deadline), <your university> (degree/DMC), offer letters, background verification, relieving letters.
