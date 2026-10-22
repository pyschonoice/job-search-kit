# Tracker fields

`tracker/applications.csv` has one row per opportunity: a posting, a recruiter conversation or a cold-email target. Write it only through `scripts/tracker.py` (it validates everything below). Dates are always `YYYY-MM-DD`.

| Column | What goes in it |
|---|---|
| `id` | Auto slug of company + role (e.g. `expedia-sde-ii-backend-r-108912`). Pass `--id` only to keep two similar rows apart. |
| `company` | Hiring company. For an agency or board posting, write the real employer and add the agency in brackets: `Spotter Labs (via Jobgether)`. |
| `role` | Exact title, with a req ID if there is one. `(role not recorded)` when unknown. |
| `category` | The channel. See below. |
| `platform` | Where it happened: LinkedIn, Workday, Ashby, Greenhouse, Lever, SuccessFactors, Keka, PyjamaHR, Rippling ATS, ClanX, YC Work at a Startup, Jobgether, Wellfound, Instahyre, Naukri, Cutshort, HireFT, Email, StartupsMap... |
| `status` | Where it stands now. See below. |
| `stage` | Free text for detail within a status: `OA sent`, `R1 tech done 10-07`, `HR round`, `offer 22 LPA`. |
| `date_found` | When the posting or lead was found. Defaults to `date_applied`. |
| `date_applied` | When the application, cold email or reply was sent. |
| `last_update` | Last time anything happened (auto-stamped on every `update`). The follow-up rules key off this. |
| `date_closed` | When it reached a closed status (auto-filled on close). |
| `next_action` / `next_action_due` | The one next step and its date (e.g. "Send take-home" / 2026-10-09). `due` lists anything on or past its date. |
| `contact`, `contact_email` | Recruiter, hiring manager, founder or referrer, with their role in brackets. |
| `job_url` | The posting or form link (company site for cold leads). |
| `location`, `work_mode` | City; `remote`, `hybrid` or `onsite`. |
| `resume` | Repo path of the PDF that was sent. |
| `ats_score` | Score from `ats-check` against this JD, if run. |
| `salary` | Posted range, estimate, or what the user quoted. |
| `gmail_thread` | Gmail thread ID of the latest relevant email (for `get_thread`). |
| `notes` | Short, dated if useful. `update --notes` appends with ` | `; pass `--replace-notes` to overwrite. |

## Categories (channel)

| Category | Use when |
|---|---|
| `linkedin_easy_apply` | Applied with LinkedIn Easy Apply. |
| `company_site` | Applied on the company's careers page or its ATS (Workday, Ashby, Greenhouse, Lever, SuccessFactors, Keka...). |
| `job_board` | Applied through a board or marketplace that isn't LinkedIn: ClanX, YC Work at a Startup, Jobgether, Wellfound, Instahyre, Naukri, Cutshort, HireFT. |
| `recruiter_inbound` | A recruiter or company reached out first (InMail, email, call). |
| `referral` | An employee referred the user. Put the referrer in `contact`. |
| `cold_email` | the user emailed a founder, hiring manager or recruiter directly (or a lead they plan to email). |
| `linkedin_dm` | the user messaged someone on LinkedIn directly. |

## Statuses

Open: `lead` → `saved` → `applied` / `cold_sent` → `in_review` / `replied` → `assessment` → `interviewing` → `offer`.
Closed: `accepted`, `rejected`, `withdrawn`, `ghosted`, `closed`.

| Status | Meaning |
|---|---|
| `lead` | A cold-email target not contacted yet. |
| `saved` | A posting worth applying to; not applied yet. |
| `applied` | Sent; only an auto-confirmation (or nothing) so far. |
| `in_review` | A human acknowledged it or it's clearly moving (not an auto-confirmation). |
| `assessment` | Online test or take-home assigned. |
| `interviewing` | Any interview round scheduled or done; detail in `stage`. |
| `offer` | Offer received. |
| `accepted` | Offer accepted. |
| `rejected` | They said no. |
| `withdrawn` | the user pulled out. |
| `ghosted` | No reply long after applying or following up. |
| `closed` | The posting closed, or the user dropped it before applying. |
| `cold_sent` | Cold email or DM sent, waiting for a reply. |
| `replied` | A two-way conversation is open (cold reply, or the user answered an inbound recruiter). |

## Follow-up rules (what `due` flags)

| Situation | Flag after | Suggested action |
|---|---|---|
| `next_action_due` reached | on the date | the `next_action` |
| `saved` | 7 days | apply or close |
| `cold_sent` | 5 days / 14 days | one short follow-up / mark `ghosted` |
| `applied`, `in_review` via referral, recruiter or job board | 14 days | nudge the contact |
| `applied`, `in_review` (any) | 30 days | mark `ghosted` |
| `interviewing`, `assessment`, `replied` | 5 quiet days | follow up |
| `offer` | 2 days | decide or negotiate |
