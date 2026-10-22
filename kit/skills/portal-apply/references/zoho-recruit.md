# Zoho Recruit (`<company>.zohorecruit.in/jobs/Careers/<id>`)

**Account:** none (an optional "Easy Apply" sign-in exists; skip it). **Submit:** the user, after typing the CAPTCHA.

## Flow

Job page → decline cookies → "I'm interested" → the form loads **inside an iframe** on the same page.

Sections: Basic Info (first/last name, mobile with +91 picker, email) · Address (City) · Professional Details (Skill Set chips, Current Job Title, Relevant Experience years + months, Overall Experience years, Current Salary ₹, Current Work location, Expected Salary ₹, Official Notice Period, Notice Period Status, LWD) · Social (LinkedIn) · Attachment (Resume) · CAPTCHA.

```bash
python3 .claude/skills/portal-apply/scripts/snip.py zoho-fill '{"resume":"ai","skills":["Python","Generative AI","LLM","RAG","FastAPI","AI Agents"],"dropdowns":[{"label":"Relevent Experience in Years","value":"1"},{"label":"Relevent Experience - Months","value":"10"},{"label":"Overall Experience in Years","value":"2"},{"label":"Official Notice Period","value":"60 Days"},{"label":"Notice Period Status","value":"Not serving NP"}],"text":[{"label":"LWD","value":"MM/DD/YYYY of today+60"}]}'
```

## Answers (example run)

- Relevant experience (years + months), overall (whole years), notice period, status "Not serving NP"; **LWD** mandatory → today + notice days (answers.md).
- Salary fields take the full number (e.g. 1200000), no unit.
- Current Job Title options are junk (Fresher / Project-Lead / Project-Manager): leave "-None-".
- City autocomplete only knows West Bengal localities for "Bengal…"; typed "<your city>" is accepted as free text.

## Quirks

- Field `aria-ref`s go stale after each dropdown pick; select dropdowns by label (script) or by index, not by snapshot ref.
- Two file inputs: the first is "Autofill" (overwrites everything); upload the resume into the **last** one.
- Confirmation: "Acknowledgment for your Application for the position - <role>" from careers@<company>.com, plus a candidate-portal invite.
