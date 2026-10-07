# Assessment Formats

All questions are **original**. Every collection file starts with:

::: {.note}
These practice questions are original study material written for this book. They are not actual NVIDIA exam questions and do not reproduce exam content.
:::

## Question types (match the real exam's styles)

The official study guide shows single-answer and "Select two/three options" multiple-select items, often with USDA snippets. Use this mix:

| Type | Share | Notes |
|------|-------|-------|
| Single answer (A–D) | ~60% | One unambiguously correct answer |
| Multiple select ("Select two/three") | ~25% | State the number to select |
| USDA/Python reading ("What is the composed value...?") | ~15% | Include the full snippet |

## Question format

```markdown
### Q<ID>  [Domain: Composition] [Obj 1.6] [Difficulty: 2/3]

Question text.

A. ...
B. ...
C. ...
D. ...

<!-- answers live in the answer section, never directly under the question -->
```

Answer format (in the answers section / answer file):

```markdown
**Q<ID> — Answer: B**
Why B is correct: ...
Why the others are wrong: A ... C ... D ...
Concept: Chapter 25, Section 25.2
```

IDs: `CMP-001` Composition, `CAG-` Content Aggregation, `CUS-` Customizing, `DEX-` Data Exchange, `DMO-` Data Modeling, `DBG-` Debugging, `PIP-` Pipeline, `VIS-` Visualization, `FND-` Fundamentals, `USDA-` reading exercises.

Quality rules:
- Distractors are plausible misconceptions, not nonsense.
- No "all of the above"/"none of the above".
- Every answer explanation must be verifiable against the chapter text and, for code, by running it.
- Difficulty: 1 = recall, 2 = apply, 3 = analyze/debug.

## Topic-wise question bank targets

| File | Count |
|------|-------|
| `qb_fundamentals.md` | 20 |
| `qb_composition.md` | 55 |
| `qb_data-exchange.md` | 36 |
| `qb_pipeline.md` | 34 |
| `qb_data-modeling.md` | 32 |
| `qb_debugging.md` | 26 |
| `qb_content-aggregation.md` | 24 |
| `qb_visualization.md` | 20 |
| `qb_customizing.md` | 14 |
| `usda-reading-exercises.md` | 25 exercises |

## Mock exams (≥ 3)

- 65 questions each, 120-minute time box (matches official format: 60–70 questions, 120 min).
- Domain distribution per exam (blueprint-weighted):

| Domain | Weight | Questions |
|--------|--------|-----------|
| Composition | 23% | 15 |
| Data Exchange | 15% | 10 |
| Pipeline Development | 14% | 9 |
| Data Modeling | 13% | 8 |
| Debugging and Troubleshooting | 11% | 7 |
| Content Aggregation | 10% | 7 |
| Visualization | 8% | 5 |
| Customizing USD | 6% | 4 |
| **Total** | | **65** |

- Questions shuffled across domains; no question reused between mocks or from the question bank.
- Mock 1 ≈ medium, Mock 2 ≈ medium-hard, Mock 3 ≈ hard (more debugging/reading items).
- Answer file includes a scoring table per domain so the reader can record weak areas in the master plan. Suggested readiness target: ≥ 80% on Mock 3 (this is the book's own target, not NVIDIA's passing score, which is not published on the certification page).

## Flashcards (≥ 150)

Two-column table, printable and foldable:

```markdown
| # | Front | Back |
|---|-------|------|
| 001 | What does the "E" in LIVERPS stand for? | Relocates (Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes) |
```

Distribution roughly follows exam weights; tag the domain in a section heading per group.

## Cheat sheets

One A4 page each (two at most). Planned sheets:

- `cs_liverps-and-value-resolution.md`
- `cs_composition-arcs-comparison.md`
- `cs_python-api-core.md` (Usd, Sdf, Gf, Vt, Tf)
- `cs_usda-syntax.md`
- `cs_usdgeom-usdshade-usdlux.md`
- `cs_instancing.md`
- `cs_command-line-tools.md`
- `cs_debugging-playbook.md`
- `cs_pipeline-and-data-exchange.md`
- `cs_customizing-usd.md`

## Final certification checklist

`cheat-sheets/final-checklist.md`: one checkbox per official objective (from `references/NVIDIA_EXAM_OBJECTIVES.md`), each linking to its chapter, plus exam-day logistics (ID, Certiverse account, remote proctoring environment).
