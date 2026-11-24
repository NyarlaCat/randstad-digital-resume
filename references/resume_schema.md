# Resume JSON schema for `build_resume_docx.py`

All fields are optional except `name`. Empty/missing sections are omitted from the output.
Any text may contain `[TODO: ...]` placeholders; the script renders them **bold + yellow highlight**
so a human editor can find them, and lists every one at the end of its output.

```json
{
  "name": "JANE DOE",
  "contact": ["555-555-5555", "jane@example.com", "Pittsburgh, PA 15210", "linkedin.com/in/janedoe"],

  "skills": [
    {"category": "Languages", "items": ["TypeScript", "Java", "Go"]},
    {"category": "Frontend", "items": ["React", "Redux", "Storybook"]}
  ],

  "experience": [
    {
      "company": "Acme Corp",
      "location": "Remote",
      "roles": [
        {
          "title": "Software Engineer",
          "dates": "January 2023 – Present",
          "bullets": [
            "Overview bullet: charge, team size, stack, product type, methodology, scope ...",
            "Action verb + ingredients + impact, filling two full lines ..."
          ]
        },
        {
          "title": "Associate Software Engineer",
          "dates": "June 2021 – January 2023",
          "bullets": ["..."]
        }
      ]
    }
  ],

  "prior_experience": [
    {"company": "Old Co", "title": "Developer", "dates": "2010 – 2014"}
  ],

  "education": [
    {"institution": "State University", "degree": "B.S., Computer Science", "date": "May 2012"}
  ],

  "certifications": [
    {"organization": "AWS", "name": "Solutions Architect – Associate", "date": "2022"}
  ],

  "projects": [
    {"company": "Open-source CLI tool", "location": "github.com/x/y",
     "roles": [{"title": "Maintainer", "dates": "2023 – Present", "bullets": ["..."]}]},
    {"name": "Freelance client site", "dates": "2022", "bullets": ["..."]}
  ],

  "awards": [
    {"text": "Peer-voted Company Value Award – Acme Corp", "date": "2023"}
  ],

  "extra_sections": [
    {"heading": "Publications", "bullets": ["..."], "lines": ["..."]}
  ],

  "section_titles": {"projects": "Freelance Work"}
}
```

Notes
- Use an en dash `–` in date ranges.
- `section_titles` overrides heading text; keys: `skills`, `experience`, `prior_experience`,
  `education`, `certifications`, `projects`, `awards`.
- Use `extra_sections` only for content that truly fits none of the template's sections
  (it renders after Awards).
