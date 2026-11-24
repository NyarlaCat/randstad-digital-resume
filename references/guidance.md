# Randstad Digital Technical Resume Guidance — Rules Checklist

Distilled from `ResumeContext/Randstad Direct Hire - Resume Guidance (Draft).pdf`,
`ResumeContext/Randstad Sample Tech Resume Template.pdf`, and `ResumeContext/Sample Resume (Dev).pdf`.
If anything here seems to conflict with those PDFs, the PDFs win — re-read them.

The format is deliberately plain: it is built to parse cleanly in Applicant Tracking Systems (ATS)
and Vendor Management Systems (VMS).

## Layout (handled by `scripts/build_resume_docx.py`)
- **Wide body**: margins ~1/8 inch on all sides.
- **Font**: never below 10 pt (11–12 is fine depending on font). No bars, tables, logos, colors, or
  multi-line gaps; limit page breaks.
- **Header**: name, then contact info — **two lines max total**. Template order:
  `Phone | Email | Location (City, State ZIP) | Portfolio/LinkedIn (optional)`.
- **Company line**: Company (left) ... Location (right). **Title line** below: Title (left) ... Dates (right).
  Multiple roles at one company = one company line, then each Title/Dates line with its own bullets.
- **Bullets** start directly under the first letter of company/title and run nearly to the right edge.

## Section order (from the template)
1. Name + contact (2 lines)
2. **SKILLS** — categorized lines running horizontally: `Category: skill, skill, skill` (no bullets)
3. **PROFESSIONAL EXPERIENCE** — jobs within the last 7–10 years, with bullets
4. **PRIOR EXPERIENCE** — jobs older than 7–10 years: `Company – Title ........ Start – End`, one line, **no bullets**
5. **EDUCATION** — `Institution – Degree, Major ........ Month/Year`, one line each (two max)
6. **CERTIFICATIONS** — `Organization – Certification ........ Year`, one line each
7. **PASSION PROJECTS / FREELANCING** — same format as Professional Experience
8. **AWARDS / RECOGNITIONS / VOLUNTEER WORK** (optional) — `• Item ........ Date`

There is **no Objective / Summary section** in the template. Drop it.

## Bullet rules
- **First bullet under each title = overview of the charge**: responsibilities, team size/composition,
  tech stack, type of app/product (dashboard, data viz, business system, etc.), methodology
  (Agile/Scrum/etc.), scope of distribution/usage.
- **Every other bullet = Action → Ingredients → Impact**
  - *Action*: strong primary **past-tense** action verb (current role may still use past tense per the samples).
  - *Ingredients*: technologies, tools, methods, practices, standards, metrics.
  - *Impact*: qualitative or quantitative result ("major reduction", "50% decrease").
- **Exactly two lines** per bullet — not one, not three. Fill both lines with detail.
  At the default Arial 10.5 pt / 1/8" margins, two full lines hold **~244–250 characters**
  (~123 per line); aim for ~200–245 so Word/Pages wrapping differences don't spill to a third line.
- **Resume speak**: no articles (a, an, the); turn infinitives into present participles
  ("to improve X" → ", improving X"; "in order to keep" → ", keeping").
- Avoid weak openers: "Responsible for", "Helped", "Worked on", "Participated in".
- Awards and recognitions don't fit Action→Ingredients→Impact; move them to the Awards section.

## Content rules
- **Keywords**: if a job description is supplied, weave its explicit keywords *into bullets* (a list
  alone is not enough). Never add a keyword the source resume doesn't support.
- **Curate keywords**: outdated (10+ years) or surface-level skills should go. Only remove when the
  source makes it clear; otherwise leave it and mention it in the summary to the user.
- **Education**: unfinished degrees are removed entirely.
- **Transparency**: list the full chronology. Jobs older than 7–10 years go to Prior Experience
  without bullets — never delete them.
