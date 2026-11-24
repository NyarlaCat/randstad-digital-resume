#!/usr/bin/env python3
"""
Render a resume JSON file (see references/resume_schema.md) into a .docx laid out
per the Randstad Digital Technical Resume Guidance.

Standard library only -- no pip installs needed. The .docx opens in Microsoft Word,
LibreOffice, Apple Pages, and Google Docs on any OS.

Usage:
    python3 build_resume_docx.py resume.json [--out PATH] [--font Arial] [--size 10.5]

Prints the output path on success, plus lint warnings (bullet length, articles,
weak openers) and a list of every [TODO: ...] placeholder left for the human editor.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import zipfile
from xml.sax.saxutils import escape

# ---- Page geometry (US Letter, twips: 1 inch = 1440) ----
PAGE_W, PAGE_H = 12240, 15840
DEFAULT_MARGIN_IN = 0.125          # guidance: ~1/8 inch on all sides
BULLET_INDENT = 270                # bullet glyph sits at the left margin, under company/title

TODO_RE = re.compile(r"(\[TODO:[^\]]*\])")
ARTICLE_RE = re.compile(r"\b(a|an|the)\b", re.IGNORECASE)
INFINITIVE_RE = re.compile(
    r"\bin order to\b|\bto (improve|increase|reduce|support|maintain|ensure|enable|help|keep|"
    r"provide|create|build|deliver|drive|streamline|automate|meet|allow)\b",
    re.IGNORECASE,
)
WEAK_OPENERS = ("responsible for", "helped", "worked on", "assisted", "participated",
                "was ", "duties", "tasked with", "actively participated")


def x(s):
    return escape(str(s), {'"': "&quot;"})


# ---------------------------------------------------------------- run / paragraph XML
FONT = {"name": "Arial", "size": 21}   # set in main(); written on every run so even
                                       # minimal renderers (e.g. macOS Quick Look) honor it


def run(text, bold=False, size=None, highlight=False):
    f = x(FONT["name"])
    size = size or FONT["size"]
    rpr = f'<w:rFonts w:ascii="{f}" w:hAnsi="{f}" w:eastAsia="{f}" w:cs="{f}"/>'
    if bold:
        rpr += "<w:b/><w:bCs/>"
    if size:
        rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
    if highlight:
        rpr += '<w:highlight w:val="yellow"/>'
        rpr += '<w:shd w:val="clear" w:color="auto" w:fill="FFFF00"/>'
    rpr = f"<w:rPr>{rpr}</w:rPr>"
    parts = str(text).split("\t")
    body = '<w:tab/>'.join(f'<w:t xml:space="preserve">{x(p)}</w:t>' for p in parts)
    return f"<w:r>{rpr}{body}</w:r>"


def runs(text, bold=False, size=None):
    """Split text so every [TODO: ...] placeholder is bold + yellow-highlighted."""
    out = []
    for piece in TODO_RE.split(str(text)):
        if not piece:
            continue
        if TODO_RE.fullmatch(piece):
            out.append(run(piece, bold=True, size=size, highlight=True))
        else:
            out.append(run(piece, bold=bold, size=size))
    return "".join(out)


class Builder:
    def __init__(self, font, size_pt, margin_in):
        self.font = font
        self.sz = int(round(size_pt * 2))           # half-points
        self.margin = int(round(margin_in * 1440))
        self.text_w = PAGE_W - 2 * self.margin
        self.body = []

    def p(self, content, style=None, keep_next=False, bullet=False, right_tab=False,
          before=0, after=0, align=None):
        ppr = ""
        if style:
            ppr += f'<w:pStyle w:val="{style}"/>'
        if keep_next:
            ppr += "<w:keepNext/>"
        if bullet:
            ppr += '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
        if right_tab:
            ppr += f'<w:tabs><w:tab w:val="right" w:pos="{self.text_w}"/></w:tabs>'
        ppr += f'<w:spacing w:before="{before}" w:after="{after}" w:line="240" w:lineRule="auto"/>'
        if bullet:
            ppr += f'<w:ind w:left="{BULLET_INDENT}" w:hanging="{BULLET_INDENT}"/>'
        if align:
            ppr += f'<w:jc w:val="{align}"/>'
        self.body.append(f"<w:p><w:pPr>{ppr}</w:pPr>{content}</w:p>")

    def heading(self, text):
        self.p(runs(text.upper(), bold=True, size=self.sz + 2), style="SectionHeading",
               keep_next=True, before=60, after=0)   # tight: guidance says limit page breaks

    def two_col(self, left, right, bold_left=True, bold_right=True, keep_next=True, before=0):
        self.p(runs(left, bold=bold_left) + (run("\t") + runs(right, bold=bold_right) if right else ""),
               right_tab=True, keep_next=keep_next, before=before)

    def bullet(self, text, right=None):
        content = runs(text)
        if right:
            content += run("\t") + runs(right)
        self.p(content, bullet=True, right_tab=bool(right))


# ---------------------------------------------------------------- lint
class Linter:
    def __init__(self, size_pt, text_w_twips):
        # Rough average glyph width for Arial/Calibri-class fonts in mixed-case prose.
        usable_pt = (text_w_twips - BULLET_INDENT) / 20
        # 0.45 em/char calibrated against real output: at Arial 10.5 pt with 1/8" margins a
        # two-line bullet holds ~244-250 characters (~123 per line).
        self.cpl = int(usable_pt / (size_pt * 0.45))
        self.warnings = []
        self.todos = []

    def scan_todos(self, where, text):
        for t in TODO_RE.findall(str(text)):
            self.todos.append(f"{where}: {t}")

    def bullet(self, where, text):
        self.scan_todos(where, text)
        clean = TODO_RE.sub("", text).strip()
        # TODO text will be replaced by (usually shorter) real content, so judge length without it;
        # don't flag "one line" when a TODO is present -- it will grow once filled in.
        has_todo = bool(TODO_RE.search(text))
        n = len(clean) if has_todo else len(text)
        if n < int(self.cpl * 0.9) and not has_todo:
            self.warnings.append(f"{where}: likely ONE line (~{n} chars, aim for ~{self.cpl + 1}-{2 * self.cpl}) -> {text[:70]}...")
        elif n > 2 * self.cpl:
            self.warnings.append(f"{where}: likely 3+ lines (~{n} chars, max ~{2 * self.cpl}) -> {text[:70]}...")
        if ARTICLE_RE.search(clean):
            arts = sorted({m.group(0).lower() for m in ARTICLE_RE.finditer(clean)})
            self.warnings.append(f"{where}: contains article(s) {arts} -> {text[:70]}...")
        if INFINITIVE_RE.search(clean):
            self.warnings.append(f"{where}: infinitive found ('{INFINITIVE_RE.search(clean).group(0)}'); use present participle -> {text[:70]}...")
        low = clean.lower()
        if any(low.startswith(w) for w in WEAK_OPENERS):
            self.warnings.append(f"{where}: weak opener; start with strong past-tense action verb -> {text[:70]}...")


# ---------------------------------------------------------------- document assembly
def render_entry(b, lint, entry, label):
    """Experience / project entry: company line, then role(s) with bullets."""
    company = entry.get("company") or entry.get("name", "")
    right = entry.get("location") or ""
    roles = entry.get("roles")
    if not roles and ("title" in entry or "bullets" in entry):
        roles = [{"title": entry.get("title", ""), "dates": entry.get("dates", ""),
                  "bullets": entry.get("bullets", [])}]
        if not entry.get("title"):
            # project-style entry with no title: put dates on the name line if no location
            right = right or entry.get("dates", "")
    lint.scan_todos(label, company + " " + right)
    b.two_col(company, right, before=80)
    for r in roles or []:
        where = f"{label} / {r.get('title') or company}"
        if r.get("title"):
            lint.scan_todos(where, r.get("title", "") + " " + r.get("dates", ""))
            b.two_col(r.get("title", ""), r.get("dates", ""), before=20)
        bullets = r.get("bullets", [])
        for i, t in enumerate(bullets):
            lint.bullet(f"{where} bullet {i + 1}", t)
            b.bullet(t)


def build_document(data, b, lint):
    # Header: name + one contact line (guidance: max two lines total)
    name = data.get("name", "[TODO: candidate name]")
    lint.scan_todos("Header", name)
    b.p(runs(name, bold=True, size=b.sz + 12))
    contact = data.get("contact", [])
    contact_line = " | ".join(contact) if isinstance(contact, list) else str(contact)
    lint.scan_todos("Header", contact_line)
    if len(contact_line) > lint.cpl + 10:
        lint.warnings.append("Header: contact line may wrap; guidance wants header on max two lines total")
    b.p(runs(contact_line, size=max(20, b.sz - 1)))

    titles = {
        "skills": "Skills",
        "experience": "Professional Experience",
        "prior_experience": "Prior Experience",
        "education": "Education",
        "certifications": "Certifications",
        "projects": "Passion Projects / Freelancing",
        "awards": "Awards / Recognitions / Volunteer Work",
    }
    titles.update(data.get("section_titles", {}))

    if data.get("skills"):
        b.heading(titles["skills"])
        for s in data["skills"]:
            items = s.get("items", [])
            text = ", ".join(items) if isinstance(items, list) else str(items)
            lint.scan_todos("Skills", s.get("category", "") + " " + text)
            b.p(runs(f"{s.get('category', '')}: ", bold=True) + runs(text))

    if data.get("experience"):
        b.heading(titles["experience"])
        for e in data["experience"]:
            render_entry(b, lint, e, e.get("company", "Experience"))

    if data.get("prior_experience"):
        b.heading(titles["prior_experience"])
        for e in data["prior_experience"]:
            left = f"{e.get('company', '')} – {e.get('title', '')}"
            lint.scan_todos("Prior Experience", left + " " + e.get("dates", ""))
            b.two_col(left, e.get("dates", ""), keep_next=False)

    if data.get("education"):
        b.heading(titles["education"])
        for e in data["education"]:
            lint.scan_todos("Education", json.dumps(e))
            content = runs(f"{e.get('institution', '')} – ") + runs(e.get("degree", ""), bold=True)
            if e.get("date"):
                content += run("\t") + runs(e["date"], bold=True)
            b.p(content, right_tab=True)

    if data.get("certifications"):
        b.heading(titles["certifications"])
        for c in data["certifications"]:
            lint.scan_todos("Certifications", json.dumps(c))
            content = runs(f"{c.get('organization', '')} – ") + runs(c.get("name", ""), bold=True)
            if c.get("date"):
                content += run("\t") + runs(c["date"])
            b.p(content, right_tab=True)

    if data.get("projects"):
        b.heading(titles["projects"])
        for e in data["projects"]:
            render_entry(b, lint, e, e.get("company") or e.get("name", "Project"))

    if data.get("awards"):
        b.heading(titles["awards"])
        for a in data["awards"]:
            lint.scan_todos("Awards", json.dumps(a))
            b.bullet(a.get("text", ""), right=a.get("date"))

    for sec in data.get("extra_sections", []):
        b.heading(sec.get("heading", "[TODO: section heading]"))
        for line in sec.get("bullets", []):
            lint.scan_todos(sec.get("heading", "Extra"), line)
            b.bullet(line)
        for line in sec.get("lines", []):
            lint.scan_todos(sec.get("heading", "Extra"), line)
            b.p(runs(line))


# ---------------------------------------------------------------- package parts
NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')


def document_xml(b):
    m = b.margin
    sect = (f'<w:sectPr><w:pgSz w:w="{PAGE_W}" w:h="{PAGE_H}"/>'
            f'<w:pgMar w:top="{m}" w:right="{m}" w:bottom="{m}" w:left="{m}" '
            f'w:header="0" w:footer="0" w:gutter="0"/></w:sectPr>')
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:document {NS}><w:body>{"".join(b.body)}{sect}</w:body></w:document>')


def styles_xml(font, sz):
    f = x(font)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles {NS}>
 <w:docDefaults>
  <w:rPrDefault><w:rPr><w:rFonts w:ascii="{f}" w:hAnsi="{f}" w:eastAsia="{f}" w:cs="{f}"/>
   <w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/><w:lang w:val="en-US"/></w:rPr></w:rPrDefault>
  <w:pPrDefault><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:pPrDefault>
 </w:docDefaults>
 <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>
 <w:style w:type="paragraph" w:customStyle="1" w:styleId="SectionHeading">
  <w:name w:val="Section Heading"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
  <w:pPr><w:keepNext/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:b/><w:bCs/></w:rPr>
 </w:style>
 <w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/></w:style>
</w:styles>'''


def numbering_xml():
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering {NS}>
 <w:abstractNum w:abstractNumId="0">
  <w:multiLevelType w:val="singleLevel"/>
  <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/>
   <w:pPr><w:ind w:left="{BULLET_INDENT}" w:hanging="{BULLET_INDENT}"/></w:pPr>
   <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/></w:rPr></w:lvl>
 </w:abstractNum>
 <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>'''


CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="xml" ContentType="application/xml"/>
 <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
 <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
 <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
 <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
</Types>'''

ROOT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
 <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
</Relationships>'''

DOC_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
 <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>'''


def core_xml(title, creator):
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <dc:title>{x(title)}</dc:title><dc:creator>{x(creator)}</dc:creator>
 <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
 <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>'''


def default_out_path(name):
    safe = re.sub(r"[^\w\- ]+", "", TODO_RE.sub("", name)).strip() or "Candidate"
    safe = re.sub(r"\s+", " ", safe).title()
    base = os.path.join(os.path.expanduser("~"), "Desktop", f"{safe} - Randstad Resume")
    path, n = base + ".docx", 2
    while os.path.exists(path):          # never overwrite a file a human may have edited
        path, n = f"{base} ({n}).docx", n + 1
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json_path")
    ap.add_argument("--out", help="Output .docx path (default: ~/Desktop/<Name> - Randstad Resume.docx)")
    ap.add_argument("--font", default="Arial")
    ap.add_argument("--size", type=float, default=10.5, help="Body font size in pt (min 10)")
    ap.add_argument("--margin", type=float, default=DEFAULT_MARGIN_IN, help="Margin in inches")
    a = ap.parse_args()

    if a.size < 10:
        sys.exit("Guidance requires no less than 10 pt font.")
    with open(a.json_path, encoding="utf-8") as fh:
        data = json.load(fh)

    FONT.update(name=a.font, size=int(round(a.size * 2)))
    b = Builder(a.font, a.size, a.margin)
    lint = Linter(a.size, b.text_w)
    build_document(data, b, lint)

    out = os.path.expanduser(a.out) if a.out else default_out_path(data.get("name", ""))
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", ROOT_RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/document.xml", document_xml(b))
        z.writestr("word/styles.xml", styles_xml(a.font, b.sz))
        z.writestr("word/numbering.xml", numbering_xml())
        z.writestr("docProps/core.xml", core_xml(f"{data.get('name', '')} Resume", data.get("name", "")))

    print(f"OUTPUT: {out}")
    print(f"(~{lint.cpl} chars per bullet line at {a.size}pt {a.font})")
    if lint.warnings:
        print(f"\nLINT WARNINGS ({len(lint.warnings)}):")
        for w in lint.warnings:
            print("  - " + w)
    print(f"\nTODO PLACEHOLDERS ({len(lint.todos)}):")
    for t in lint.todos:
        print("  - " + t)


if __name__ == "__main__":
    main()
