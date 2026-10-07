# 00 — MASTER PLAN: NCP-OUSD 14-Day Study Book

Single source of truth for the project. Managed by the `openusd-certification` skill. Read first and update last in every session.

**Current phase:** Phase 1 — Research and curriculum (planning deliverables done; follow-up research tasks open)
**Next unit:** Phase 1 follow-up: verify URLs in `references/SOURCE_PLAN.md`, set up `usd-core` venv, write `references/bibliography.md`. Then Phase 2 → Ch 1.
**Last updated:** 2026-10-07

Status values: `pending` · `in-progress` · `draft` (written, not verified) · `verified` (code/usda checked) · `done` (verified + audited)

---

## 1. Exam blueprint (verified 2026-10-07)

Verified against the NVIDIA certification page and Study Guide v1.1.0. Objectives: `references/NVIDIA_EXAM_OBJECTIVES.md`.

| # | Domain | Weight | ≈ Questions (of 65) | Book Part | Official objectives |
|---|--------|--------|---------------------|-----------|---------------------|
| 1 | Composition | 23% | 15 | III | 1.1–1.11 |
| 2 | Data Exchange | 15% | 10 | V | 4.1–4.8 |
| 3 | Pipeline Development | 14% | 9 | VI | 7.1–7.8 |
| 4 | Data Modeling | 13% | 8 | II | 5.1–5.6 |
| 5 | Debugging and Troubleshooting | 11% | 7 | IX | 6.1–6.5 |
| 6 | Content Aggregation | 10% | 7 | IV | 2.1–2.5 |
| 7 | Visualization | 8% | 5 | VIII | 8.1–8.4 |
| 8 | Customizing USD | 6% | 4 | VII | 3.1–3.8 |

Exam format: 60–70 questions · 120 minutes · online, remotely proctored (Certiverse) · English · $200 · valid 2 years · single-answer and multiple-select items. Passing score not published on the certification page.

Re-verify the blueprint at the start of Phase 14: `pending`.

---

## 2. 14-day study schedule (for the reader)

About 5–6 hours per day. Time splits are approximate: about 50% reading, 30% labs, 20% questions. Study time per domain roughly follows exam weight; Composition gets 3 days.

| Day | Focus | Chapters | Labs | Practice | Hours |
|-----|-------|----------|------|----------|-------|
| 1 | Foundations I: stage, layers, prims, properties | 1–5 | 01–05 | Ch 1–5 practice Qs | 5 |
| 2 | Foundations II: metadata, schemas, kinds, file formats | 6–9 | 06–08 | USDA ex. 1–5; Fundamentals QB (20) | 5 |
| 3 | Data Modeling | 10–16 | 09–12 | USDA ex. 6–9; Data Modeling QB (32) | 6 |
| 4 | Composition I: fundamentals, sublayers, references, payloads | 17–20 | 13–15 | Ch practice Qs | 6 |
| 5 | Composition II: variants, inherits, specializes, relocates | 21–24 | 16–19 | USDA ex. 10–13 | 6 |
| 6 | Composition III: LIVERPS, practice, debugging | 25–27 | 20–21 | USDA ex. 14–17; Composition QB (55) | 6 |
| 7 | Content Aggregation + week-1 review | 28–32 | 22–26 | Content Aggregation QB (24); flashcards 1–80 | 6 |
| 8 | Data Exchange | 33–39 | 27–30 | Data Exchange QB (36) | 6 |
| 9 | Pipeline Development | 40–45 | 31–33 | Pipeline QB (34) | 6 |
| 10 | Customizing USD + **Mock Exam 1** | 46–48 | 34–35 | Customizing QB (14); Mock 1 (120 min) + review | 6 |
| 11 | Visualization | 49–54 | 36–40 | USDA ex. 21–23; Visualization QB (20) | 5 |
| 12 | Debugging & Performance + **Mock Exam 2** | 55–58 | 41–43 | USDA ex. 24–25; Debugging QB (26); Mock 2 + review | 6 |
| 13 | Weak areas + **Mock Exam 3** | Re-read weak chapters | Redo 2–3 weak labs | Mock 3 + review; flashcards 81–160 | 6 |
| 14 | Final revision | Cheat sheets | — | Final checklist; all flashcards; rest before exam | 4 |

Daily routine: (1) 10-minute flashcard warm-up, (2) read chapters, (3) run labs, (4) answer questions closed-book, (5) log weak areas in Section 9.

---

## 3. Phase tracker (book production)

| Phase | Name | Status | Output |
|-------|------|--------|--------|
| 1 | Research and curriculum | in-progress | Skill, dirs, this plan, TOC, schedule, source plan, objectives ✅; follow-ups open |
| 2 | Beginner fundamentals | pending | Front matter + Ch 1–9 |
| 3 | Data modeling | pending | Ch 10–16 |
| 4 | Composition | pending | Ch 17–27 |
| 5 | Content aggregation | pending | Ch 28–32 |
| 6 | Data exchange | pending | Ch 33–39 |
| 7 | Pipeline development | pending | Ch 40–45 |
| 8 | Customizing USD | pending | Ch 46–48 |
| 9 | Visualization | pending | Ch 49–54 |
| 10 | Debugging and performance | pending | Ch 55–58 |
| 11 | Python labs | pending | 43 labs |
| 12 | Question bank | pending | 261 Qs + 25 USDA exercises |
| 13 | Mock exams | pending | 3 × 65 Qs + answers |
| 14 | Final revision | pending | 10 cheat sheets, 160 flashcards, checklist |
| 15 | Technical audit | pending | Audit log (Section 10) |
| 16 | PDF generation | pending | `final/*.pdf` |

### Phase 1 checklist

- [x] Verify blueprint against official page (match)
- [x] Capture official objectives (`references/NVIDIA_EXAM_OBJECTIVES.md`)
- [x] Create skill and directory structure
- [x] Create this master plan
- [x] Complete table of contents (`chapters/00_TABLE_OF_CONTENTS.md`)
- [x] 14-day schedule (Section 2)
- [x] Source/reference plan (`references/SOURCE_PLAN.md`)
- [ ] Verify "To verify" URLs and locate "To locate" sources
- [ ] Set up `.venv` with `usd-core`; record version in Section 12
- [ ] Read CHANGELOG for version-sensitive items
- [ ] Create `references/bibliography.md`

---

## 4. Chapter tracker

Pages = target. Q = in-chapter practice questions written.

| Ch | Title | Domain | Objectives | Pages | Status | Q |
|----|-------|--------|------------|-------|--------|---|
| F1–F5 | Front matter | — | — | 14 | pending | — |
| 1 | Welcome to OpenUSD | Fundamentals | — | 4 | pending | 0 |
| 2 | Your OpenUSD Workbench | Fundamentals | — | 5 | pending | 0 |
| 3 | Stages and Layers | Fundamentals | — | 6 | pending | 0 |
| 4 | Prims and the Scenegraph | Fundamentals | — | 6 | pending | 0 |
| 5 | Properties: Attributes and Relationships | Fundamentals | — | 6 | pending | 0 |
| 6 | Metadata | Fundamentals | — | 4 | pending | 0 |
| 7 | Schemas | Fundamentals | — | 5 | pending | 0 |
| 8 | Model Kinds (first look) | Fundamentals | — | 3 | pending | 0 |
| 9 | USD File Formats | Fundamentals / DEX | 4.3, 7.3 | 5 | pending | 0 |
| 10 | Usd and Sdf | Data Modeling | 6.1 | 6 | pending | 0 |
| 11 | Value Types | Data Modeling | 5.2 | 6 | pending | 0 |
| 12 | Time: TimeCodes, Samples, Interpolation | Data Modeling | — | 6 | pending | 0 |
| 13 | Value Clips | Data Modeling | — | 3 | pending | 0 |
| 14 | Primvars | Data Modeling | 5.1, 8.1 | 5 | pending | 0 |
| 15 | Inspecting Properties, Custom Metadata | Data Modeling | 5.3, 5.4, 7.6 | 4 | pending | 0 |
| 16 | Geometry Data Integrity | Data Modeling | 5.5, 5.6, 6.4 | 4 | pending | 0 |
| 17 | Composition Fundamentals | Composition | — | 6 | pending | 0 |
| 18 | Sublayers and Layer Stacks | Composition | 1.1, 1.3, 1.5 | 6 | pending | 0 |
| 19 | References | Composition | 1.3, 1.4 | 7 | pending | 0 |
| 20 | Payloads | Composition | 1.3 | 5 | pending | 0 |
| 21 | Variants | Composition | 1.7 | 6 | pending | 0 |
| 22 | Inherits and Class Prims | Composition | — | 5 | pending | 0 |
| 23 | Specializes | Composition | — | 4 | pending | 0 |
| 24 | Relocates | Composition | — | 4 | pending | 0 |
| 25 | LIVERPS and Value Resolution | Composition | 1.1, 1.6, 1.8 | 8 | pending | 0 |
| 26 | Composition in Practice | Composition | 1.5, 1.9, 1.11 | 5 | pending | 0 |
| 27 | Debugging Composition | Composition / DBG | 1.8, 6.2 | 6 | pending | 0 |
| 28 | Asset Structure Principles | Content Aggregation | 7.2 | 6 | pending | 0 |
| 29 | Model Hierarchy and Kinds | Content Aggregation | — | 5 | pending | 0 |
| 30 | Native Scenegraph Instancing | Content Aggregation | 1.10, 2.2, 2.4, 2.5 | 6 | pending | 0 |
| 31 | Point Instancing | Content Aggregation | 2.1, 2.3 | 5 | pending | 0 |
| 32 | Instancing Strategy and Large Scenes | Content Aggregation | 1.2, 2.4 | 4 | pending | 0 |
| 33 | Data Exchange Fundamentals | Data Exchange | 4.2 | 5 | pending | 0 |
| 34 | Writing a Converter / Exporter | Data Exchange | 4.7 | 6 | pending | 0 |
| 35 | Units, Up Axis, Coordinate Systems | Data Exchange | — | 4 | pending | 0 |
| 36 | Naming, Materials, Animation in Interchange | Data Exchange | — | 5 | pending | 0 |
| 37 | Importers, Round-Trips, DCC Integration | Data Exchange | 3.6, 4.4, 4.5, 4.8, 7.4, 7.8 | 5 | pending | 0 |
| 38 | Exporting USD to Other Formats | Data Exchange | 4.1, 7.1 | 4 | pending | 0 |
| 39 | Validation | Data Exchange | 4.6 | 5 | pending | 0 |
| 40 | Pipeline Architecture | Pipeline | 7.2 | 5 | pending | 0 |
| 41 | Asset Resolution (Ar) | Pipeline | 3.5, 6.3, 7.5, 7.7 | 6 | pending | 0 |
| 42 | Asset Management, Versioning, Publishing | Pipeline | 7.7 | 5 | pending | 0 |
| 43 | Exporter Hooks, Pipeline Transformations | Pipeline | — | 5 | pending | 0 |
| 44 | Flattening, Packaging, Delivery | Pipeline | 1.9 | 5 | pending | 0 |
| 45 | Build Configurations and Collaboration | Pipeline | 3.2 | 4 | pending | 0 |
| 46 | The Plugin System | Customizing | 3.1 | 4 | pending | 0 |
| 47 | Custom Schemas | Customizing | 3.4, 3.6 | 5 | pending | 0 |
| 48 | Kinds, Fallbacks, File Formats, Resolvers, Scene Index | Customizing | 3.3, 3.5, 3.7, 3.8 | 5 | pending | 0 |
| 49 | UsdGeom: Xformables and Transforms | Visualization | — | 5 | pending | 0 |
| 50 | Gprims, Meshes, and Points | Visualization | 8.1 | 6 | pending | 0 |
| 51 | Cameras | Visualization | — | 3 | pending | 0 |
| 52 | UsdShade: Materials and Shaders | Visualization | 8.2, 8.3, 8.4 | 7 | pending | 0 |
| 53 | UsdLux: Lights | Visualization | — | 4 | pending | 0 |
| 54 | Hydra and Rendering Overview | Visualization | 3.7 | 3 | pending | 0 |
| 55 | Stage and Layer Introspection | Debugging | — | 5 | pending | 0 |
| 56 | Troubleshooting Playbook | Debugging | 6.2, 6.3, 6.4 | 6 | pending | 0 |
| 57 | Diagnostics and Profiling | Debugging | 6.5 | 5 | pending | 0 |
| 58 | Performance | Debugging | 6.1 | 6 | pending | 0 |
| App | Appendices A–F | — | — | 25 | pending | — |

**Chapters done: 0 / 58** · Objectives with a chapter: 50 / 50 (planned) · Objectives taught: 0 / 50

---

## 5. Python labs tracker (target ≥ 30; planned 43)

| Lab | Title | Ch | Status | Tested version |
|-----|-------|----|--------|----------------|
| 01 | Hello Stage | 2–3 | pending | |
| 02 | Reading layers | 3 | pending | |
| 03 | Prim paths and traversal | 4 | pending | |
| 04 | Attributes | 5 | pending | |
| 05 | Relationships | 5 | pending | |
| 06 | Metadata | 6 | pending | |
| 07 | Schemas | 7 | pending | |
| 08 | File formats | 9 | pending | |
| 09 | Sdf authoring and change blocks | 10 | pending | |
| 10 | Value types | 11 | pending | |
| 11 | Time samples | 12 | pending | |
| 12 | Primvars | 14 | pending | |
| 13 | Sublayers and edit targets | 18 | pending | |
| 14 | References and time offsets | 19 | pending | |
| 15 | Payloads | 20 | pending | |
| 16 | Variant sets | 21 | pending | |
| 17 | Inherits and classes | 22 | pending | |
| 18 | Specializes vs inherits | 23 | pending | |
| 19 | Relocates | 24 | pending | |
| 20 | LIVERPS puzzle | 25 | pending | |
| 21 | Composition debugging | 27 | pending | |
| 22 | Component asset interface | 26, 28 | pending | |
| 23 | Model hierarchy validation | 29 | pending | |
| 24 | Native instancing | 30 | pending | |
| 25 | PointInstancer | 31 | pending | |
| 26 | Population masks, load rules | 32 | pending | |
| 27 | Converter to USD | 34 | pending | |
| 28 | Units and up axis | 35 | pending | |
| 29 | Name sanitization | 36 | pending | |
| 30 | Custom validator | 39 | pending | |
| 31 | Dependency analysis | 42 | pending | |
| 32 | Flatten and package | 44 | pending | |
| 33 | Exporter hook | 43 | pending | |
| 34 | Codeless schema | 47 | pending | |
| 35 | Kinds and variant fallbacks | 48 | pending | |
| 36 | Xforms | 49 | pending | |
| 37 | Mesh from scratch | 50 | pending | |
| 38 | Camera | 51 | pending | |
| 39 | UsdPreviewSurface + primvar color | 52 | pending | |
| 40 | Lights | 53 | pending | |
| 41 | Introspection script | 55 | pending | |
| 42 | Debug a broken scene | 56 | pending | |
| 43 | Performance measurement | 58 | pending | |

**Labs done: 0 / 43**

---

## 6. Question bank tracker

| File | Target | Written | Verified |
|------|--------|---------|----------|
| qb_fundamentals.md | 20 | 0 | 0 |
| qb_composition.md | 55 | 0 | 0 |
| qb_data-exchange.md | 36 | 0 | 0 |
| qb_pipeline.md | 34 | 0 | 0 |
| qb_data-modeling.md | 32 | 0 | 0 |
| qb_debugging.md | 26 | 0 | 0 |
| qb_content-aggregation.md | 24 | 0 | 0 |
| qb_visualization.md | 20 | 0 | 0 |
| qb_customizing.md | 14 | 0 | 0 |
| usda-reading-exercises.md | 25 | 0 | 0 |
| In-chapter practice questions | ~400 | 0 | 0 |

**Question bank: 0 / 261** · USDA exercises: 0 / 25

---

## 7. Mock exam tracker

| Mock | Difficulty | Questions | Answers + explanations | Status | Reader score |
|------|------------|-----------|------------------------|--------|--------------|
| 1 | Medium | 0 / 65 | 0 / 65 | pending | — |
| 2 | Medium-hard | 0 / 65 | 0 / 65 | pending | — |
| 3 | Hard | 0 / 65 | 0 / 65 | pending | — |

Per-exam distribution: CMP 15 · DEX 10 · PIP 9 · DMO 8 · DBG 7 · CAG 7 · VIS 5 · CUS 4.

---

## 8. Revision material tracker

| Item | Target | Done | Status |
|------|--------|------|--------|
| Flashcards | 160 | 0 | pending |
| Cheat sheets | 10 | 0 | pending |
| Final certification checklist | 1 | 0 | pending |
| Glossary (Appendix A) | ~150 terms | 0 | pending |
| API quick reference (Appendix B) | 1 | 0 | pending |
| USDA syntax reference (Appendix C) | 1 | 0 | pending |
| Traceability matrix (Appendix D) | 1 | 0 | pending |

---

## 9. Weak areas log (reader fills during study)

| Date | Source (chapter / QB / mock) | Domain | Topic | Score / symptom | Action | Resolved |
|------|------------------------------|--------|-------|-----------------|--------|----------|
| | | | | | | |

---

## 10. Technical audit log (Phase 15)

| Part | Python blocks run / skipped / failed | USDA checked / failed | Labs pass | Issues | Status |
|------|--------------------------------------|-----------------------|-----------|--------|--------|
| I–IX | — | — | — | — | pending |

---

## 11. Final PDF status (Phase 16)

| Item | Status |
|------|--------|
| Toolchain installed (pandoc, graphviz, weasyprint) | pending |
| `final/book-order.txt` | pending |
| `final/print.css` | pending |
| `final/metadata.yaml` | pending |
| First build | pending |
| Page count | — (target 250–400) |
| Print review checklist | pending |
| Final PDF: `final/OpenUSD-NCP-OUSD-Study-Book.pdf` | pending |

---

## 12. Environment

| Item | Value |
|------|-------|
| Python | 3.12.3 (system) |
| usd-core | not installed yet |
| Tested OpenUSD version | — |
| pandoc / graphviz / weasyprint | not installed |

---

## 13. Open issues

1. `usd-core` not installed: code verification unavailable until the venv is set up.
2. Several URLs in the source plan are unverified or not yet located.
3. Confirm exam duration (120 min on en-us page; one regional snippet said 90) before booking.
4. Advanced C++-only objectives (3.1, 3.2, 3.7, 3.8) will be taught conceptually with `.norun` C++/plugInfo examples; Python verification only where possible.

---

## 14. Session log

| Date | Phase | Work done | Files |
|------|-------|-----------|-------|
| 2026-10-07 | 1 | Verified blueprint and format on official page; captured Study Guide v1.1.0 objectives; created skill, directories, master plan, TOC, schedule, source plan | `.cursor/skills/openusd-certification/*`, `00_MASTER_PLAN.md`, `chapters/00_TABLE_OF_CONTENTS.md`, `references/SOURCE_PLAN.md`, `references/NVIDIA_EXAM_OBJECTIVES.md` |
