# Book Build, Audit, and PDF

## Toolchain (Phase 16)

Default pipeline: Markdown → HTML → PDF.

1. `.venv/bin/pip install markdown pymdown-extensions weasyprint pygments`
2. `final/build_book.py` concatenates files in TOC order (front matter, chapters, labs, USDA workbook, question bank, mock exams, flashcards, cheat sheets, checklist, glossary, references, index) into `final/book.html`, converting callouts to `<aside class="callout tip|trap|mistake|version|key|note">`.
3. Render with WeasyPrint: `final/book.css` → `final/NCP-OUSD_Study_Book.pdf`.
4. Fallback if WeasyPrint system libraries (Pango) are missing: `google-chrome --headless --no-pdf-header-footer --print-to-pdf=final/NCP-OUSD_Study_Book.pdf final/book.html` (TOC page numbers then need a two-pass build or are omitted — note in master plan).

Build scripts live in `final/` and are re-runnable; never hand-edit generated HTML/PDF.

## Page and typography spec

| Item | Spec |
|------|------|
| Page | A4 (210 × 297 mm), `@page { size: A4; margin: 22mm 20mm 24mm 22mm; }` (wider inner margin for binding) |
| Body | Serif, 10.5–11 pt, line-height 1.45 (e.g. "Source Serif 4", "DejaVu Serif" fallback) |
| Headings | Sans-serif, bold; chapter title 22 pt, h2 15 pt, h3 12 pt |
| Code | Monospace 8.5–9 pt, light gray background (#f2f2f2), 0.5 pt black border, no syntax colors that carry meaning (grayscale Pygments style) |
| Tables | 0.5 pt rules, header row bold with gray fill, `page-break-inside: avoid` for small tables |
| Callouts | Bold label text ("EXAM TIP", "TRAP", …) + distinct border style (solid / dashed / double / thick-left) so they differ in black & white |
| Running header | Chapter title (left/right alternating) |
| Footer | Page number, centered or outer edge |
| Chapters | Start on a new (right-hand) page; "Chapter N" label above title |
| TOC | Generated with page numbers (`target-counter`) |
| Diagrams | Monochrome SVG in `final/assets/diagrams/` or framed monospace diagrams; ≥ 8 pt text; grayscale fills only |
| Links | Printed URLs shown in full in references; no "click here" |

## Book order

Front matter (title, how to use, exam overview, 14-day plan, setup) → Parts I–IX (chapters) → Part X: Python labs → USDA reading workbook → Question bank (questions, then answers) → Mock exams (papers, then answer keys) → Flashcards → Cheat sheets → Final certification checklist → Glossary → References → Index.

## Technical audit (Phase 15) → `final/AUDIT_REPORT.md`

```
Audit checklist (per part):
- [ ] Re-run every .py lab and every chapter Python block; diff against printed output
- [ ] Parse every USDA block
- [ ] Grep for suspicious APIs; confirm each against installed pxr (dir()/help())
- [ ] All [!VERIFY] callouts resolved or removed
- [ ] [!VERSION] callouts state the verified version
- [ ] Every official objective (1.1–8.4) is covered by ≥ 1 chapter section, ≥ 1 lab or exercise, ≥ 3 questions
- [ ] Question answer keys re-checked; distribution matches blueprint
- [ ] No claim that questions are real NVIDIA exam questions
- [ ] Terminology consistent (LIVERPS spelling, "prim", "opinion", "layer stack")
- [ ] Cross-references (Ch/§/Lab numbers) all valid
```

Record findings as a table: `| ID | File | Issue | Severity | Fix | Status |`.

## Print checklist (Phase 16)

- [ ] A4 size confirmed in PDF properties
- [ ] Page numbers on every body page; TOC page numbers correct
- [ ] No code line overflows the margin; no table cut off
- [ ] Callouts distinguishable in grayscale (print a test page or render to grayscale)
- [ ] Every chapter starts on a new page; no orphan headings at page bottom
- [ ] Mock exam answer keys start on a separate page from papers
- [ ] Fonts embedded (`pdffonts`, or inspect PDF properties)
- [ ] Widows/orphans controlled (`orphans: 3; widows: 3;` in CSS)
- [ ] Spot-check 10 random pages rendered in grayscale
- [ ] Total page count recorded in the master plan
