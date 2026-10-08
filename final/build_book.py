#!/usr/bin/env python3
"""Concatenate the NCP-OUSD study book Markdown and render HTML (and PDF).

Usage:
  .venv/bin/python final/build_book.py            # HTML only
  .venv/bin/python final/build_book.py --pdf      # HTML + WeasyPrint (Chrome fallback)
"""

from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = Path(__file__).resolve().parent

CALLOUT_MAP = {
    "EXAM TIP": "tip",
    "TRAP": "trap",
    "MISTAKE": "mistake",
    "VERSION": "version",
    "KEY": "key",
    "NOTE": "note",
    "VERIFY": "note",
}

PARTS = [
    ("Front matter", [
        "chapters/f1_title.md",
        "chapters/f2_how_to_use.md",
        "chapters/f3_exam_overview.md",
        "chapters/f4_study_plan.md",
        "chapters/f5_setup.md",
    ]),
    ("Part I — OpenUSD Fundamentals", [f"chapters/ch{n:02d}_*.md" for n in range(1, 8)]),
    ("Part II — Data Modeling", [f"chapters/ch{n:02d}_*.md" for n in range(8, 14)]),
    ("Part III — Composition", [f"chapters/ch{n:02d}_*.md" for n in range(14, 23)]),
    ("Part IV — Content Aggregation", [f"chapters/ch{n:02d}_*.md" for n in range(23, 27)]),
    ("Part V — Data Exchange", [f"chapters/ch{n:02d}_*.md" for n in range(27, 32)]),
    ("Part VI — Pipeline Development", [f"chapters/ch{n:02d}_*.md" for n in range(32, 36)]),
    ("Part VII — Customizing USD", [f"chapters/ch{n:02d}_*.md" for n in range(36, 39)]),
    ("Part VIII — Visualization", [f"chapters/ch{n:02d}_*.md" for n in range(39, 42)]),
    ("Part IX — Debugging and Performance", [f"chapters/ch{n:02d}_*.md" for n in range(42, 45)]),
    ("Part X — Python Labs", ["python-labs/lab*.md"]),
    ("USDA Reading Workbook", ["questions/usda_exercises.md"]),
    ("Question bank", [
        "questions/qbank_fundamentals.md",
        "questions/qbank_composition.md",
        "questions/qbank_data_exchange.md",
        "questions/qbank_pipeline.md",
        "questions/qbank_data_modeling.md",
        "questions/qbank_debugging.md",
        "questions/qbank_content_aggregation.md",
        "questions/qbank_visualization.md",
        "questions/qbank_customizing.md",
    ]),
    ("Mock exams", [
        "mock-exams/mock01_paper.md",
        "mock-exams/mock01_answers.md",
        "mock-exams/mock02_paper.md",
        "mock-exams/mock02_answers.md",
        "mock-exams/mock03_paper.md",
        "mock-exams/mock03_answers.md",
    ]),
    ("Flashcards", ["questions/flashcards.md"]),
    ("Cheat sheets", [
        "cheat-sheets/cs_liverps.md",
        "cheat-sheets/cs_usda_syntax.md",
        "cheat-sheets/cs_python_api.md",
        "cheat-sheets/cs_list_editing.md",
        "cheat-sheets/cs_primvars.md",
        "cheat-sheets/cs_instancing.md",
        "cheat-sheets/cs_debugging.md",
        "cheat-sheets/cs_file_formats_tools.md",
        "cheat-sheets/cs_schemas_kinds.md",
        "cheat-sheets/cs_exam_domains.md",
        "cheat-sheets/final_checklist.md",
    ]),
    ("Back matter", [
        "chapters/b1_glossary.md",
        "chapters/b3_coverage.md",
        "references/references.md",
    ]),
]


def expand(pattern: str) -> list[Path]:
    if "*" in pattern:
        found = sorted(ROOT.glob(pattern))
        if not found:
            raise SystemExit(f"no files for {pattern}")
        return found
    path = ROOT / pattern
    if not path.exists():
        raise SystemExit(f"missing {path}")
    return [path]


def convert_callouts(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    tag_re = re.compile(r"^>\s*\[!([A-Z ]+)\]\s?(.*)$")
    while i < len(lines):
        m = tag_re.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        raw_tag, rest = m.group(1).strip(), m.group(2)
        css = CALLOUT_MAP.get(raw_tag, "note")
        body = [rest] if rest else []
        i += 1
        while i < len(lines) and lines[i].startswith(">"):
            body.append(re.sub(r"^>\s?", "", lines[i]))
            i += 1
        inner = "\n".join(body).strip() or raw_tag
        out.append(
            f'<aside class="callout {css}">'
            f'<span class="callout-label">{html.escape(raw_tag)}</span>\n\n'
            f"{inner}\n</aside>"
        )
    return "\n".join(out)


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^\w\s-]", "", text, flags=re.U).strip().lower()
    return re.sub(r"[-\s]+", "-", text) or "section"


def chapter_class(path: Path) -> str:
    name = path.name
    if name.startswith("f1"):
        return "front-section"
    if name.startswith("f"):
        return "front-section"
    if name.startswith("mock") and "answers" in name:
        return "chapter mock-answers"
    if re.match(r"ch\d+_", name):
        return "chapter"
    if name.startswith("lab"):
        return "lab-entry"
    if name.startswith("mock"):
        return "chapter"
    if name.startswith("qbank") or name == "flashcards.md":
        return "practice"
    if name == "usda_exercises.md":
        return "practice usda"
    if name.startswith("cs_") or name.startswith("final_"):
        return "cheat"
    if name.startswith("b") or path.parent.name == "references":
        return "back-section"
    return "chapter"


def compact_for_print(md: str, path: Path) -> str:
    """Denser print edition. Source Markdown on disk is unchanged."""
    name = path.name
    if name.startswith("ch") and name[2:4].isdigit():
        md = compact_chapter(md)
    elif name.startswith("lab"):
        md = compact_lab(md, path)
    return md


def compact_chapter(md: str) -> str:
    """Run-in 13-step labels; drop in-chapter quizzes and further-reading URLs."""
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## Further reading"):
            break
        if line.startswith("### 12. Practice questions"):
            i += 1
            while i < len(lines) and not (
                lines[i].startswith("### 13.") or lines[i].startswith("## ")
            ):
                i += 1
            continue
        if line.startswith("### Chapter questions"):
            i += 1
            while i < len(lines) and not lines[i].startswith("## "):
                i += 1
            continue
        m = re.match(r"^### (\d+)\.\s+(.+)$", line)
        if m:
            title = m.group(2).strip()
            if not title.endswith((".", "?", "!")):
                title += "."
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i >= len(lines):
                out.append(f"**{title}**")
                break
            nxt = lines[i]
            if nxt.startswith(("#", "```", "-", "*", ">", "|")):
                out.append(f"**{title}**")
            else:
                out.append(f"**{title}** {nxt}")
                i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def compact_lab(md: str, path: Path) -> str:
    """Keep goal, steps, output; drop duplicated full scripts from the printed lab."""
    py_name = path.with_suffix(".py").name
    md = re.sub(
        r"## Full script[^\n]*\n+```python.*?```\n*",
        f"Run `python-labs/{py_name}` (script is in the repo; output below).\n\n",
        md,
        flags=re.S,
    )
    return md


def wrap_h1(md: str, path: Path) -> str:
    """Add a chapter label above the first ATX h1 when the filename is chNN/labNN."""
    label = None
    m = re.match(r"ch(\d+)_", path.name)
    if m:
        label = f"Chapter {int(m.group(1))}"
    m = re.match(r"lab(\d+)_", path.name)
    if m:
        label = f"Lab {int(m.group(1)):02d}"
    if not label:
        return md
    return re.sub(
        r"^# (.+)$",
        rf'# <span class="chap-label">{label}</span>\1',
        md,
        count=1,
        flags=re.M,
    )


def md_to_html(md: str) -> str:
    import markdown

    extensions = [
        "tables",
        "fenced_code",
        "attr_list",
        "sane_lists",
        "smarty",
        "toc",
        "md_in_html",
    ]
    try:
        import pymdownx.superfences  # noqa: F401
        extensions.extend(["pymdownx.superfences", "pymdownx.saneheaders"])
    except ImportError:
        pass
    return markdown.markdown(
        md,
        extensions=extensions,
        extension_configs={"toc": {"permalink": False}},
    )


def build_html() -> str:
    sections: list[str] = []
    toc_items: list[str] = []
    for part_title, patterns in PARTS:
        part_id = slugify(part_title)
        files: list[Path] = []
        for pat in patterns:
            files.extend(expand(pat))
        toc_items.append(
            f'<li class="toc-part"><a href="#{part_id}">{html.escape(part_title)}</a></li>'
        )
        seen: set[Path] = set()
        first_in_part = True
        for path in files:
            if path in seen:
                continue
            seen.add(path)
            text = path.read_text(encoding="utf-8")
            text = compact_for_print(text, path)
            text = wrap_h1(text, path)
            text = convert_callouts(text)
            body = md_to_html(text)
            first = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
            title = re.sub(r"<[^>]+>", "", first.group(1) if first else path.stem)
            title = re.sub(r"\s+", " ", title).strip()
            sid = slugify(f"{path.stem}-{title}")[:80]
            cls = chapter_class(path)
            banner = ""
            if first_in_part:
                cls = f"{cls} part-start"
                banner = (
                    f'<h1 class="part-title" id="{html.escape(part_id)}">'
                    f"{html.escape(part_title)}</h1>\n"
                )
                first_in_part = False
            if path.name.startswith("f1"):
                sections.append(
                    f'<article class="{cls}" id="title-page">{banner}{body}</article>'
                )
            else:
                sections.append(
                    f'<article class="{cls}" id="{html.escape(sid)}">{banner}{body}</article>'
                )
            toc_items.append(
                f'<li class="toc-leaf"><a href="#{html.escape(sid)}">'
                f"{html.escape(title)}</a></li>"
            )

    toc = "<nav id='toc'><h1>Contents</h1><ol>\n" + "\n".join(toc_items) + "\n</ol></nav>"
    css_href = "book.css"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>OpenUSD Development from Zero — NCP-OUSD Study Book</title>
<link rel="stylesheet" href="{css_href}"/>
</head>
<body>
{toc}
{"".join(sections)}
</body>
</html>
"""


def render_pdf(html_path: Path, pdf_path: Path) -> str:
    try:
        from weasyprint import HTML

        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        return "weasyprint"
    except Exception as exc:
        print(f"WeasyPrint unavailable ({exc!r}); trying Chrome.", file=sys.stderr)

    chrome = None
    for candidate in (
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
    ):
        if subprocess.call(["which", candidate], stdout=subprocess.DEVNULL) == 0:
            chrome = candidate
            break
    if not chrome:
        raise SystemExit("Neither WeasyPrint nor Chrome is available for PDF.")
    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]
    subprocess.check_call(cmd)
    return "chrome"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", action="store_true")
    args = parser.parse_args()

    html_path = FINAL / "book.html"
    html_path.write_text(build_html(), encoding="utf-8")
    print(f"wrote {html_path} ({html_path.stat().st_size} bytes)")

    if args.pdf:
        pdf_path = FINAL / "NCP-OUSD_Study_Book.pdf"
        engine = render_pdf(html_path, pdf_path)
        print(f"wrote {pdf_path} via {engine} ({pdf_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
