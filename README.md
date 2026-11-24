# Randstad Digital Resume Skill

A [Claude Code](https://claude.com/claude-code) skill that takes a PDF resume and rewrites it to follow
Randstad Digital's technical resume guidance. It saves the result as an editable Word document (`.docx`)
so you can review it before exporting a final PDF.

## Table of Contents

- [Overview](#overview)
- [Getting started](#getting-started)
  - [Setup on your computer](#setup-on-your-computer)
  - [Running the skill](#running-the-skill)

## Overview

Give Claude a resume PDF and the skill will:

- **Restructure it** into the Randstad layout:
  - name and contact info on two lines
  - categorized skills lines
  - company and location, then title and dates, right-aligned
  - Professional Experience, then Prior Experience
  - Education, Certifications, Projects, and Awards / Volunteer Work
- **Rewrite the bullets**:
  - each role starts with an overview bullet: scope, team, tech stack, methodology
  - every other bullet follows *Action → Ingredients → Impact*
  - each bullet runs about two full lines
  - "resume speak" throughout: no articles, and no "to improve…" phrasing ("improving…" instead)
- **Apply the formatting rules**: 1/8" margins, Arial 10.5 pt (never below 10 pt), and no tables,
  bars, or colors, so Applicant Tracking Systems can read it cleanly.
- **Never invent facts.** Where information is missing or unclear (team size, metrics, tools,
  conflicting dates), it inserts a **`[TODO: …]`** placeholder, highlighted in yellow, describing
  what belongs there.
- **Save an editable `.docx` to your Desktop.** It opens in Word, Pages, LibreOffice, and Google Docs
  on any OS. An existing file is never overwritten; new versions get ` (2)`, ` (3)`, and so on.

### Where the rules come from

The rules come from the documents in [`ResumeContext/`](ResumeContext/):

| File | Purpose |
|------|---------|
| `Randstad Direct Hire - Resume Guidance (Draft).pdf` | The written guidance: formatting, bullet composition, section rules |
| `Randstad Sample Tech Resume Template.pdf` | The blank template: section order and line layout |
| `Sample Resume (Dev).pdf` | A filled-in example |

[`references/guidance.md`](references/guidance.md) condenses these into a checklist that Claude follows.
When the two disagree, the PDFs take precedence.

### What's in this folder

```
RandstadDigitalResumeSkill/
├── SKILL.md                    # Instructions Claude follows when the skill runs
├── README.md                   # This file
├── ResumeContext/              # Source guidance, template, and sample (PDFs)
├── references/
│   ├── guidance.md             # Rules checklist distilled from ResumeContext
│   └── resume_schema.md        # JSON format the document generator accepts
└── scripts/
    └── build_resume_docx.py    # Builds the .docx (Python standard library only)
```

## Getting started

### Setup on your computer

**Requirements**

- [Claude Code](https://docs.claude.com/en/docs/claude-code/overview): the CLI, the desktop app's
  Code tab, or an IDE extension
- Python 3.8 or later on your `PATH` (macOS and most Linux distributions include it). The generator
  uses only the standard library, so you don't need `pip install`.

**Install**

1. Clone the repository:

   ```bash
   git clone https://github.com/NyarlaCat/randstad-digital-resume.git RandstadDigitalResumeSkill
   ```

2. Make the skill available to Claude Code by placing it in your personal skills folder,
   `~/.claude/skills/`. A symlink lets later `git pull` updates take effect automatically.

   macOS / Linux:

   ```bash
   mkdir -p ~/.claude/skills
   ```

   ```bash
   ln -s "$(pwd)/RandstadDigitalResumeSkill" ~/.claude/skills/randstad-digital-resume
   ```

   Windows (PowerShell):

   ```powershell
   New-Item -ItemType Junction -Path "$HOME\.claude\skills\randstad-digital-resume" -Target "$PWD\RandstadDigitalResumeSkill"
   ```

   You can also copy the folder there instead of linking it.

3. Start a new Claude Code session. Skills are loaded when a session starts. To confirm the install,
   ask Claude *"What skills do you have?"*; `randstad-digital-resume` should be in the list.

> **Tip:** To share the skill with a team through a single project, put the folder at
> `<project>/.claude/skills/randstad-digital-resume` instead.

### Running the skill

1. Open Claude Code and invoke the skill with your resume's path, either as a slash command:

   ```
   /randstad-digital-resume ~/Documents/MyResume.pdf
   ```

   or in plain language:

   ```
   Apply the Randstad resume guidance to ~/Documents/MyResume.pdf
   ```

   *Optional:* paste in or point to a job description. Claude will work its keywords into your
   bullets where your experience supports them.

2. **Wait for Claude to finish.** It reads the PDF, rewrites the content, builds the document, and
   checks every bullet: likely one or three-plus lines, leftover articles, "to + verb" phrasing, and
   weak openers like "Responsible for".

3. **Read the summary.** Claude reports the output path, what it changed, any judgment calls, and
   every `[TODO]` it left.

4. **Edit the file** on your Desktop (`<Your Name> - Randstad Resume.docx`). Fill in each
   highlighted TODO and remove the highlight.

5. **Iterate with Claude if you like.** For example: "these two bullets overlap, separate them", "move
   this job to Prior Experience", or "make this fit on one page". If you edited the file yourself,
   attach the updated `.docx` or PDF so Claude works from your version.

6. **Export to PDF** from your word processor when you're done.

**Tips**

- At the default settings, a two-line bullet holds about **244–250 characters**. Aim for roughly
  200–245 to allow for small rendering differences between word processors.
- Quick Look (the macOS spacebar preview) ignores right-aligned tab stops. Dates appear next to the
  titles there but line up correctly in Word, Pages, LibreOffice, and Google Docs.
- You can also run the generator directly on a JSON file that follows
  [`references/resume_schema.md`](references/resume_schema.md):

  ```bash
  python3 scripts/build_resume_docx.py resume.json --out ~/Desktop/Resume.docx --size 11
  ```

  Options: `--out PATH`, `--font NAME` (default Arial), `--size PT` (default 10.5, minimum 10),
  and `--margin INCHES` (default 0.125).
