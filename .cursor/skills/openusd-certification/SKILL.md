---
name: openusd-certification
description: Builds a complete, print-ready 14-day study book for the NVIDIA Certified Professional OpenUSD Development (NCP-OUSD) exam, incrementally and file by file — research, curriculum, beginner-level chapters, Python labs, USDA exercises, question bank, mock exams, flashcards, cheat sheets, technical audit, and A4 PDF generation. Use when working in the OpenUSD-Certification project, or when the user mentions NCP-OUSD, the OpenUSD study book, 00_MASTER_PLAN.md, a chapter, lab, question bank, mock exam, or "continue the book".
---

# OpenUSD Certification Study Book (NCP-OUSD)

Produces ONE professional, offline-usable, A4 printable study book for a **complete beginner**.
All state lives in files. `00_MASTER_PLAN.md` is the single source of truth for progress.

## Golden rules

1. **Never generate the whole book in one pass.** Work in units (see "Work units"): write a unit to its file, verify it, then update the master plan. By default, stop after each unit with a short report. **Continuous mode** (the user has asked for this, 2026-10-07): don't stop between units. Keep processing units, optionally in parallel subagents with one unit set each and no shared files. The orchestrator alone edits `00_MASTER_PLAN.md`.
2. **Read before writing.** Every session starts by reading `00_MASTER_PLAN.md` and `01_TABLE_OF_CONTENTS.md`. Follow the TOC numbering exactly; if the TOC must change, change it first and log why.
3. **Accuracy beats volume.** Only real OpenUSD APIs. Every Python example is executed against the installed `usd-core` before it is marked done. Never invent APIs, flags, env vars, or metadata keys. If unsure, check official docs or mark `> [!VERIFY]` and log it in the master plan.
4. **Official sources first.** NVIDIA NCP-OUSD page + official study guide, then openusd.org docs/API, then NVIDIA Learn OpenUSD. See `references/00_SOURCE_PLAN.md`.
5. **Offline-complete.** Each chapter teaches fully on its own. URLs go in "Further reading" and the references section only; never "see link for details" for essential content.
6. **Original questions only.** Never claim or imply any question is a real NVIDIA exam question. Do not copy NVIDIA's published sample questions; write original questions that test the same objectives.
7. **Version honesty.** Mark version-sensitive behavior with `> [!VERSION]` stating the USD version the book was verified against and what changed (e.g. `GetMaster`→`GetPrototype`, `MaterialBindingAPI` must be applied, UsdLux `inputs:` namespacing, relocates, UsdValidation).
8. **Beginner first.** Define every term before using it. No forward references without a one-line definition.

## Session workflow

```
Session checklist:
- [ ] 1. Read 00_MASTER_PLAN.md (status, current phase, weak areas, open VERIFY items)
- [ ] 2. Pick the NEXT unchecked work unit in the current phase (or the one the user names)
- [ ] 3. Read the relevant TOC entry + official objectives it maps to
- [ ] 4. Research: consult sources for that unit; note any source used
- [ ] 5. Write the file(s) following teaching-template.md and content-standards.md
- [ ] 6. Run every Python snippet/lab with .venv/bin/python; paste REAL output
- [ ] 7. Self-check against the Quality gate below
- [ ] 8. Update 00_MASTER_PLAN.md (status, counts, change log, VERIFY items)
- [ ] 9. Stop. Report: files written, counts, issues, next unit
```

## Work units (max per response)

| Unit | Size limit |
|------|-----------|
| Chapter | 1 chapter (split large chapters into `a`/`b` parts across two responses) |
| Python labs | 3 labs (`.py` + `.md`), all executed |
| Questions | 1 domain file, ≤ 40 questions per response |
| USDA exercises | ≤ 10 exercises |
| Mock exam | 1 exam paper OR its answer key (65 questions) |
| Flashcards | ≤ 60 cards |
| Cheat sheets | ≤ 3 sheets |
| Audit | 1 part of the book |
| PDF | 1 build + fix iteration |

## Phases

| # | Phase | Output | Exit criteria |
|---|-------|--------|---------------|
| 1 | Research & curriculum | master plan, TOC, source plan, `.venv` with `usd-core` | Blueprint verified on official page; USD version recorded |
| 2 | Beginner fundamentals | `chapters/` Part I | Ch 1–7 done |
| 3 | Data modeling | Part II | Ch 8–13 done |
| 4 | Composition | Part III | Ch 14–22 done |
| 5 | Content aggregation | Part IV | Ch 23–26 done |
| 6 | Data exchange | Part V | Ch 27–31 done |
| 7 | Pipeline development | Part VI | Ch 32–35 done |
| 8 | Customizing USD | Part VII | Ch 36–38 done |
| 9 | Visualization | Part VIII | Ch 39–41 done |
| 10 | Debugging & performance | Part IX | Ch 42–44 done |
| 11 | Python labs | `python-labs/` | ≥ 30 labs, all executed, outputs captured |
| 12 | Question bank | `questions/` | Weighted bank + USDA exercises + ≥ 150 flashcards |
| 13 | Mock exams | `mock-exams/` | ≥ 3 papers × 65 Q, separate answer keys |
| 14 | Final revision | `cheat-sheets/`, checklist | Cheat sheets, final checklist, glossary |
| 15 | Technical audit | `final/AUDIT_REPORT.md` | All code re-run, all VERIFY items closed |
| 16 | PDF generation | `final/` | A4 PDF passes print checklist |

Chapter writing (phases 2–10) may include the labs referenced by that chapter; phase 11 completes and normalizes the full lab set.

## Project layout and naming

```
00_MASTER_PLAN.md                 progress tracker (always update)
01_TABLE_OF_CONTENTS.md           authoritative book structure
chapters/chNN_slug.md             e.g. ch16_references.md
python-labs/labNN_slug.py         runnable lab
python-labs/labNN_slug.md         lab write-up for the book
questions/qbank_<domain>.md       e.g. qbank_composition.md
questions/usda_exercises.md
questions/flashcards.md
mock-exams/mockNN_paper.md        questions only
mock-exams/mockNN_answers.md      answers + explanations
cheat-sheets/cs_<topic>.md
references/00_SOURCE_PLAN.md      sources + verification log
references/NVIDIA_EXAM_OBJECTIVES.md  official objectives 1.1–8.4 → chapters
references/references.md          book's printed references section
final/                            build script, CSS, assets, PDF, audit report
.venv/                            Python env with usd-core (not part of the book)
```

## Environment

- `.venv` has **usd-core 26.8 (USD 26.08)**, installed 2026-10-07. This is the "verified against" version. If you upgrade it, re-run the audit.
- usd-core installs **no command-line tools** (no `usdcat`, `usdchecker`, `usdzip`, `usdtree`, `usdview`) and no `UsdImaging`, `UsdMtlx`, or `usdGenSchema`. Teach each tool's purpose and syntax as a `.norun` block, then give a runnable Python equivalent (e.g. `Sdf.Layer.Export` for `usdcat -o`, `UsdValidation` for `usdchecker`, `UsdUtils.CreateNewUsdzPackage` for `usdzip`).
- Available and verified: `UsdValidation`, `Trace`, `Tf.MallocTag`, `Tf.Debug`, `UsdUtils.CoalescingDiagnosticDelegate`, `UsdUtils.LocalizeAsset`, `Usd.PrimCompositionQuery`, `Usd.Prim.GetPrototype`. Relocates are authored as layer metadata (`Sdf.Layer.relocates`). `UsdUtils.ComplianceChecker` and `GetMaster` do not exist.
- Package installs need network access outside the sandbox (the sandbox proxy blocks PyPI).

## Quality gate (every unit)

- [ ] Follows `teaching-template.md` (all 13 steps per concept, in order)
- [ ] `scripts/check_code_blocks.py` passes: every Python block runs and matches its real output
- [ ] `scripts/check_usda_blocks.py` passes: every USDA block parses
- [ ] Mapped to official objective IDs (e.g. `Obj 1.3`)
- [ ] Callouts used: EXAM TIP, TRAP, MISTAKE, VERSION, KEY (see content-standards.md)
- [ ] No color-only meaning; diagrams are grayscale or monochrome
- [ ] Master plan updated

## Additional resources

- Teaching order and chapter skeleton: [teaching-template.md](teaching-template.md)
- Code, USDA, question, mock exam, flashcard rules, version facts, verification scripts: [content-standards.md](content-standards.md)
- Scripts (execute, don't read): `scripts/check_code_blocks.py`, `scripts/check_usda_blocks.py` (shared parser: `scripts/mdblocks.py`)
- Typography, PDF pipeline, audit and print checklists: [book-build.md](book-build.md)
