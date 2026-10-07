---
name: openusd-certification
description: Builds a complete, print-ready 14-day study book for the NVIDIA Certified Professional OpenUSD Development (NCP-OUSD) exam, incrementally and file-by-file, for an absolute beginner. Manages research, curriculum, chapters, Python labs, USDA examples, question bank, mock exams, revision material, technical audit, and A4 PDF generation, tracked in 00_MASTER_PLAN.md. Use when working in the OpenUSD-Certification project, or when the user asks to continue the book, write the next chapter/lab/question set/mock exam, audit content, or build the PDF.
---

# OpenUSD Certification Study Book (NCP-OUSD)

Produces ONE professional, offline-complete, A4 printable study book for a complete beginner preparing for NCP-OUSD. All work lives in files at the project root and is tracked in `00_MASTER_PLAN.md`.

## Golden rules

1. **Never generate the whole book in one response.** Do one work unit (see sizing below), save it, update the master plan, report, and stop.
2. **`00_MASTER_PLAN.md` is the single source of truth.** Read it first every session; update it last every session.
3. **Primary sources only for facts**: the official NVIDIA NCP-OUSD page and study guide, NVIDIA Learn OpenUSD, openusd.org docs/API, and the OpenUSD GitHub repo. See `references/SOURCE_PLAN.md`.
4. **Offline-complete**: every chapter explains its own material. URLs go in the references section, never as a substitute for an explanation.
5. **No invented APIs.** Every Python example uses real `pxr` APIs, includes imports, runs as-is, and shows expected output. Follow [technical-accuracy.md](technical-accuracy.md).
6. **Never claim practice questions are real NVIDIA exam questions.** All questions are original. Do not copy NVIDIA's sample questions; reference them only by source name.
7. **Teach from zero.** Assume the reader has never heard of USD. Use the 13-step concept template in [teaching-template.md](teaching-template.md).
8. **Print-first formatting**: A4, black/white friendly, meaning never carried by color alone. Follow [book-style-guide.md](book-style-guide.md).

## Session protocol

Every session follows this loop:

```
- [ ] 1. Read 00_MASTER_PLAN.md (phase tracker, next pending unit, weak areas, open issues)
- [ ] 2. Read chapters/00_TABLE_OF_CONTENTS.md entry for the unit
- [ ] 3. Check the unit's objectives (references/NVIDIA_EXAM_OBJECTIVES.md) and sources (references/SOURCE_PLAN.md)
- [ ] 4. Write the unit's files
- [ ] 5. Verify: run scripts/check_code_blocks.py and scripts/check_usda_blocks.py on new files (when usd-core is installed)
- [ ] 6. Update 00_MASTER_PLAN.md: status, counts, session log, new issues
- [ ] 7. Report what was created, verification results, and the next unit; then STOP
```

If the user says "continue" without detail, take the first `pending` unit in the master plan in phase order.

## Work unit sizing (one per response)

| Unit type | Size per response |
|-----------|-------------------|
| Chapter | 1 chapter (2 if both are short, < 5 pages each) |
| Python labs | 3–5 labs |
| USDA reading exercises | 8–10 exercises |
| Question bank | 1 domain, or ~30 questions |
| Mock exam | Half an exam (questions) or answer key + explanations |
| Flashcards | ~40 cards |
| Cheat sheets | 2–3 sheets |
| Audit | 1 part (group of chapters) |
| PDF build | 1 build + review cycle |

## Phases

| Phase | Name | Main outputs |
|-------|------|--------------|
| 1 | Research and curriculum | Master plan, TOC, schedule, source plan, objectives file |
| 2 | Beginner fundamentals | Chapters in Part I |
| 3 | Data modeling | Part II |
| 4 | Composition | Part III |
| 5 | Content aggregation | Part IV |
| 6 | Data exchange | Part V |
| 7 | Pipeline development | Part VI |
| 8 | Customizing USD | Part VII |
| 9 | Visualization | Part VIII |
| 10 | Debugging and performance | Part IX |
| 11 | Python labs | `python-labs/` (≥ 30 labs; plan has 43) |
| 12 | Question bank | `questions/` (topic-wise + USDA reading) |
| 13 | Mock exams | `mock-exams/` (≥ 3 full exams with explained answers) |
| 14 | Final revision | `cheat-sheets/`, flashcards (≥ 150), final checklist |
| 15 | Technical audit | Audit report + fixes ([technical-accuracy.md](technical-accuracy.md)) |
| 16 | PDF generation | `final/` PDF ([pdf-build.md](pdf-build.md)) |

Phases 2–10 may write the in-chapter labs references and practice questions as they go; Phase 11–13 produce the standalone collections. A phase is `done` only when every unit in it is `done` in the master plan.

## File layout and naming

```
00_MASTER_PLAN.md
chapters/00_TABLE_OF_CONTENTS.md
chapters/front-NN_<slug>.md            # front matter (how to use, exam overview, schedule)
chapters/chNN_<slug>.md                # e.g. ch17_composition-fundamentals.md
chapters/usda/chNN_<name>.usda         # USDA files used by a chapter
chapters/diagrams/chNN_<name>.dot      # Graphviz sources (grayscale)
python-labs/labNN_<slug>.py            # runnable lab script
python-labs/labNN_<slug>.md            # lab write-up for the book
questions/qb_<domain>.md               # topic-wise questions + answers
questions/usda-reading-exercises.md
mock-exams/mock-exam-N.md              # questions only
mock-exams/mock-exam-N_answers.md      # answer key with explanations
cheat-sheets/cs_<topic>.md
cheat-sheets/flashcards.md
cheat-sheets/final-checklist.md
references/SOURCE_PLAN.md
references/NVIDIA_EXAM_OBJECTIVES.md
references/bibliography.md             # book's references appendix
final/                                 # build outputs only
```

Use two-digit numbers (`ch01`, `lab07`) so files sort correctly. Chapter numbers must match the TOC.

## Writing a chapter

1. Open the chapter's TOC entry: sections, objectives, linked labs.
2. For each concept, apply the 13-step template from [teaching-template.md](teaching-template.md). Small sub-concepts may merge steps, but steps 1, 2, 3, 7 or 8, 10, 11, and 13 are never skipped.
3. Include at least one grayscale diagram (Graphviz DOT or ASCII) per chapter where structure matters (composition, hierarchy, pipelines).
4. End the chapter with: Chapter summary, Exam takeaways box, 5–10 practice questions with answers and explanations, and "Labs for this chapter".
5. Tag every exam objective covered as `[Obj 1.6]` in the section where it is taught.

## Assessments

Follow [assessment-formats.md](assessment-formats.md) for question, mock exam, flashcard, and cheat sheet formats, including domain weighting for mock exams.

## Reporting format (end of every session)

```markdown
## Session report
- Unit completed: <phase / unit>
- Files created/updated: <list>
- Verification: <code blocks run / passed / skipped and why>
- Master plan updated: yes
- Open issues: <list or none>
- Next unit: <unit>
```

## Additional resources

- Concept and chapter templates: [teaching-template.md](teaching-template.md)
- Formatting conventions for print: [book-style-guide.md](book-style-guide.md)
- Question, mock exam, flashcard formats: [assessment-formats.md](assessment-formats.md)
- API accuracy rules and audit checklist: [technical-accuracy.md](technical-accuracy.md)
- PDF toolchain and build steps: [pdf-build.md](pdf-build.md)
- Verification scripts: `scripts/check_code_blocks.py`, `scripts/check_usda_blocks.py`
