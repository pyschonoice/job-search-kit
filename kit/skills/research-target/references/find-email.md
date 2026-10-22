# Finding the right email address

Work down this list and stop at the first hit. Record where each address came from and label it.

## Confidence labels

| Label | Meaning | Use it? |
|---|---|---|
| `published` | The person or company put this exact address in public: a posting, HN or Reddit post, LinkedIn post, careers/contact page, YC page, the StartupsMap PDF, a talk slide, their own site. | Yes |
| `pattern` | Not published, but the domain's format is proven by **two or more** published addresses of other people there (e.g. `rahul@` and `priya@` → first name). | Yes, say so in the report |
| `guess` | Built from a common format with no proof. | **Only after the user OKs it.** Otherwise use the best published generic address. |

## 1. Published addresses (check all that apply)

- The **job posting** itself, and `hunts/<date>.json` `emails` (hunt.py pulls them from descriptions).
- **HN "Who is hiring"** comment for the company (often `founders@` or a person's address).
- **LinkedIn posts** by the person or company with "hiring" ("send your resume to ..."). Search the person's recent activity.
- **Reddit** hiring posts (r/developersIndia and others in `job-hunt/references/sources.md`).
- **Careers, contact, about and team pages**, page footers, `/security.txt`, the press kit.
- **YC company page** and the founder's personal site, Substack or X bio.
- **StartupsMap PDF** (`<your city> Startups Contacts - StartupsMap.pdf`, repo root) and existing tracker `contact_email` values.
- WebSearch: `"@<domain>"` and `"<first name>" "@<domain>"` (surfaces addresses quoted in articles, slides and directories).

## 2. Prove the pattern

Collect 2+ addresses of other people at the same domain (from step 1, or from the company GitHub org's public commits, using company-domain addresses only: `https://api.github.com/repos/<org>/<repo>/commits?per_page=50` → `commit.author.email`). Then fit the pattern: `first`, `first.last`, `firstlast`, `f.last`, `flast`, `first_last`, `last`. Never use a personal Gmail or other non-company address that a person didn't publish for contact.

## 3. Guess (last resort)

```bash
python3 .claude/skills/research-target/scripts/email_guess.py "Firstname Lastname" company.com \
  --known "Rahul Verma=rahul@company.com" "Neha Gupta=neha@company.com"   # optional: published addresses from step 2
```
It checks the domain has MX records (so mail can be delivered) and prints candidates, most common first: for Indian startups that's `first@` (by far), then `first.last@`, then `firstlast@`. Mark the result `guess`.

## Generic addresses

`founders@`, `careers@`, `jobs@`, `hiring@` and `hello@` reach a human at small startups. Use one when there's no better address, and write the email so it still works if forwarded ("could you pass this to whoever runs backend hiring?"). Avoid `support@`, `privacy@`, `sales@`.

## Never

- Don't send test emails or SMTP-probe a server to "verify" an address.
- Don't use paid enrichment tools (Apollo, Hunter, RocketReach) unless the user is logged in and asks.
- Don't scrape an address from a breach, a leaked list or a private document.
