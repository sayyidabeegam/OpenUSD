# Book Style Guide (A4, print-first)

Source files are Pandoc Markdown. These conventions are what the PDF build ([pdf-build.md](pdf-build.md)) styles; follow them exactly so the output stays consistent.

## Page and typography targets

- A4 (210 × 297 mm); margins 22 mm inner/outer, 20 mm top, 24 mm bottom.
- Body: serif, 10.5–11 pt, line height ~1.4. Headings: sans-serif. Code: monospace 8.5–9 pt.
- Running header: chapter title. Footer: page number (outer corner).
- Each Part and Chapter starts on a new page.
- Grayscale only. Distinguish things with borders, patterns, weight, icons-as-text (e.g. "EXAM TRAP"), never color alone.

## Headings

- `#` chapter (`# Chapter 17 — Composition Fundamentals {#ch17}`), `##` section (`## 17.2 Opinions`), `###` template step, `####` rarely.
- Parts are separate files: `# Part III — Composition {.part}`.

## Callout boxes (Pandoc fenced divs)

| Class | Label printed | Use for |
|-------|---------------|---------|
| `.note` | NOTE | Clarifications |
| `.exam-tip` | EXAM TIP | What the exam rewards |
| `.exam-trap` | EXAM TRAP | Likely distractors |
| `.warning` | CAUTION | Things that silently break scenes |
| `.version` | VERSION NOTE | Version-sensitive behavior (state version) |
| `.mental-model` | MENTAL MODEL | One-line recall rule |
| `.takeaways` | EXAM TAKEAWAYS | End-of-concept / chapter summary |
| `.chapter-meta` | — | Chapter header block |

```markdown
::: {.exam-trap}
Payloads are weaker than references in LIVERPS, but both are stronger than specializes.
:::
```

## Code blocks

- Runnable Python: ` ```python ` — must be self-contained.
- Non-runnable Python fragment: ` ```{.python .norun} `.
- Complete USDA file: ` ```usda ` — starts with `#usda 1.0`.
- USDA fragment or intentionally broken USDA: ` ```{.usda .norun} `.
- Shell: ` ```bash `. Output: ` ```text ` preceded by a line `**Expected output:**`.
- Max ~60 lines per block; max line length 88 characters (fits A4 at 9 pt).
- No line numbers inside blocks; refer to lines by content ("the `prepend references` line").

## Diagrams

- Default: Graphviz DOT in `chapters/diagrams/chNN_<name>.dot`, rendered to SVG at build. Use `color=black`, `fillcolor=gray90/gray75` only, `fontname="Helvetica"`.
- Small structures may use ASCII trees in ` ```text ` blocks (prim hierarchies, layer stacks).
- Every diagram has a numbered caption: `Figure 17.1 — Layer stack strength order (strongest at top)`.
- Strength order diagrams always put the strongest at the top and say so in the caption.

## Tables

- Numbered caption above: `Table 25.1 — LIVERPS arcs`.
- ≤ 5 columns for A4 portrait; short cell text, explanations in prose.

## Cross-references and terms

- Chapters: "Chapter 25"; sections: "Section 25.3"; labs: "Lab 20"; objectives: "[Obj 1.6]".
- API names in backticks with module prefix as used in Python: `Usd.Stage.Open`, `UsdGeom.Mesh.Define`.
- Write "OpenUSD" for the project/ecosystem, "USD" acceptable in running text after first use.
