# Saved form answers

The single source for anything typed into a job application form. Every answer here was given or approved by the user. Facts about work (jobs, projects, metrics) live in `my-profile`; this file holds the form-shaped answers.

**Adding to this file:** when a form asks something new and the user answers it, save the answer under "Learned answers" with the date, so the next form doesn't need to ask. Never save a guess.

> SETUP STATE: blank template. `/job-setup` fills the `<...>` placeholders. Until then, ask the user for any field you need.

## Identity and contact

| Field | Answer |
|---|---|
| Full name | <Full Name> (first: <First>, last: <Last>) |
| Email | <email for applications> (never <account email, if different>) |
| Phone / WhatsApp | <+CC number>. If the form has a separate country-code picker, choose <country> (+CC) and enter the rest. |
| Current address | <full address> |
| Address, split fields | Line 1: <...> · Line 2 / locality: <...> · City: <...> · State: <...> · PIN / ZIP: <...> · Country: <...> |
| Current location | <city, state, country> |
| Citizenship and work authorization | <e.g. citizen of X, no sponsorship needed in X / needs sponsorship in Y> |
| Remote / relocation | <open to remote? relocation? else **ask**> |
| LinkedIn | <url> |
| GitHub | <url> |
| Portfolio / personal website | <url, or "None. Leave empty if optional; if required, use GitHub and tell the user."> |

## Job and pay

| Field | Answer |
|---|---|
| Current employer and title | <...> |
| Total experience | <N years M months>. Pick the matching band; a single number: <decimal>. Years + months fields: <N> and <M>. Never pick a higher band. |
| Notice period | <e.g. 60 days, negotiable>. With bands, pick the one containing the number. |
| Current pay | <amount + breakup>. Bands: pick the one containing it. Numeric field: <full number> |
| Expected pay | <amount>. Numeric field: <full number> |
| Job source | Varies, so **ask** every time unless the user already said it |
| Referral | None unless the user names one. If the field needs text, write "NA". |

## Education

| Field | Answer |
|---|---|
| Degree | <...> |
| College | <...> |
| Dates | <MM/YYYY – MM/YYYY> (graduation year <YYYY>) |
| GPA | <...> |
| School marks / other exams | <only what the user wants shared> |

## Resume to upload

- <Role family A>: `main_resume/<variant_a>/<File>.pdf`
- <Role family B>: `main_resume/<variant_b>/<File>.pdf`
- When a tailored resume exists for the job, always upload that one: `applications/<folder>/<Name>_Resume_<Company>.pdf`

## Long-answer blocks

Adapt these to the field's length and the company. Facts and numbers must stay exactly as written.

**Top projects** (written format, when a video demo isn't available):
1. *<Project>:* <what it is, key decision, exact metric, honest status>
2. ...

**What makes you stand out** (rewrite the first line for the company): <3-4 sentences, true facts only>

**Why this company:** always written fresh. Read the company's site first and name something specific about their product, then tie it to real work from `my-profile`. Never reuse another company's answer.

## Learned answers

Answers the user gave on earlier forms that may come up again. Add new ones here with the date.

<!-- - YYYY-MM-DD: **Field:** answer. -->

## Applications filled

One line per form: date, company, role, URL, resume uploaded, status. The user always submits themself.

<!-- - YYYY-MM-DD: **Company, Role** via <portal>, <url>. Uploaded <resume>. Filled, not submitted. -->
