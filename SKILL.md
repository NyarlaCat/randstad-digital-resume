---
name: randstad-digital-resume
description: Reformat and rewrite a candidate's PDF resume to follow the Randstad Digital Technical Resume Guidance (wide margins, two-line header, categorized horizontal skills, company/title layout, overview-first bullets, Action→Ingredients→Impact two-line bullets in resume speak, Prior Experience section, one-line education). Outputs an editable .docx on the user's Desktop with highlighted [TODO] placeholders wherever information is missing. Use when the user asks to apply Randstad resume guidance/format to a resume, or to "Randstad-ify" / reformat a resume PDF for Randstad Digital.
---

# Randstad Digital Resume Reformatter

Turn a PDF resume into an editable `.docx` that follows Randstad Digital's technical resume guidance.
A human will edit the result before exporting the final PDF, so **accuracy beats polish**: never invent
facts — leave a `[TODO: ...]` placeholder instead.

All paths below are relative to this skill's base directory.

## Inputs
- **Required**: path to the candidate's resume PDF.
- **Optional**: a job description (text, file, or URL). If given, weave its explicit keywords into bullets
  where the resume supports them. If none is given, skip keyword tailoring and say so in the summary.

## Workflow

1. **Load the rules.** Read `references/guidance.md`. For any doubt about layout or wording, open the
   source PDFs in `ResumeContext/` (the guidance draft, the blank template, and the dev sample).
2. **Read the resume PDF** with the Read tool (it renders PDFs natively). Capture every fact:
   contact info, skills, each company/title/location/dates, every bullet, education, certs,
   awards, affiliations, projects.
3. **Note today's date** and sort roles into:
   - *Professional Experience*: ended within the last 7–10 years (or current) → keeps bullets.
   - *Prior Experience*: ended more than ~10 years ago → one line, no bullets. For roles 7–10 years
     old, use judgment (relevance, space) and mention the choice in the summary.
4. **Rewrite the content** into the JSON shape in `references/resume_schema.md`, applying the rules:
   - Header: name + one contact line in template order (Phone | Email | City, ST ZIP | LinkedIn/portfolio).
   - Drop any Objective/Summary section (not in the template).
   - Skills: categorized horizontal lines; keep the candidate's categories unless clearly improvable.
   - First bullet of every role = overview (scope, team size, stack, product type, methodology, reach).
     Build it from facts in the resume; put `[TODO: ...]` for each missing overview element
     (e.g. `[TODO: team size/composition]`, `[TODO: methodology, e.g. Agile/Scrum]`).
   - Remaining bullets: strong past-tense verb → ingredients → impact, ~two full lines
     (~200–245 characters at default settings; 250+ wraps to a third line),
     no articles, infinitives → present participles, no "Responsible for"/"Helped"/"Participated".
     Merge thin bullets, move content that belongs in the overview into it, and move awards
     to the Awards section.
   - If a bullet has no impact or no ingredients in the source, keep what is there and append a
     placeholder such as `[TODO: quantify impact, e.g. % reduction or users served]`.
   - Education/certs: one line each; drop descriptive sub-bullets. Remove unfinished degrees
     (flag in summary rather than silently deleting if completion status is unclear — use a TODO).
   - Affiliations / volunteer / recognitions → Awards / Recognitions / Volunteer Work.
     Side projects / freelance → Passion Projects / Freelancing (same format as experience).
5. **Placeholders — the golden rule.** Whenever the right content is ambiguous or absent, do **not**
   make it up. Write `[TODO: <what kind of info belongs here>]`. Also use a TODO for contradictions
   in the source (e.g. overlapping dates), quoting what the source says.
   Never invent: metrics, team sizes, technologies, dates, titles, employers, degrees.
6. **Write the JSON** to a temporary file (the session scratchpad if one exists, otherwise `/tmp`),
   then build the document:
   ```bash
   python3 scripts/build_resume_docx.py /path/to/resume.json
   ```
   Defaults: Arial 10.5 pt, 1/8" margins, US Letter, output to
   `~/Desktop/<Name> - Randstad Resume.docx` (never overwrites — adds ` (2)`, ` (3)`…).
   Options: `--out PATH`, `--font NAME`, `--size PT` (≥10), `--margin IN`.
7. **Act on lint output.** The script prints warnings for bullets likely 1 line or 3+ lines,
   articles, infinitives, and weak openers. Fix the real ones in the JSON and rebuild (delete the
   earlier draft from the Desktop first only if *you* created it in this run). Warnings on bullets
   that are short only because source detail is missing are fine — they carry TODOs.
8. **Verify** the file opens: on macOS `textutil -convert txt -stdout <file.docx>`; optionally
   `qlmanage -t -s 1200 -o <tmpdir> <file.docx>` and view the PNG to check layout.
9. **Report to the user**: output path; key changes made (sections dropped/moved/merged);
   the list of TODOs grouped by section; any judgment calls (e.g. 7–10-year roles, skills you think
   should be curated but left in). Remind them TODOs are yellow-highlighted and the file opens in
   Word, Pages, LibreOffice, or Google Docs; export to PDF when done.

## Why .docx
It is the one editable format every major word processor on macOS, Windows, and Linux opens with
layout intact (right-aligned tab stops, bullets, margins). The generator uses only the Python
standard library, so there is nothing to install.
