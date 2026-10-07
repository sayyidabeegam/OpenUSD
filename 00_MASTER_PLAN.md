# 00 — MASTER PLAN: NCP-OUSD 14-Day Study Book

Single source of truth for progress. Update at the end of every work session.
Skill: `.cursor/skills/openusd-certification/` · Structure: `01_TABLE_OF_CONTENTS.md` · Sources: `references/00_SOURCE_PLAN.md` · Objectives: `references/NVIDIA_EXAM_OBJECTIVES.md`

| Item | Value |
|------|-------|
| Current phase | **Phase 4 — Composition** (Phases 1–3 complete) |
| Next work unit | Phase 4: Ch 14 — Composition fundamentals |
| Learner level | Complete beginner in OpenUSD |
| USD version verified against | **USD 26.08** (`usd-core` 26.8 in `.venv`, Python 3.12.3). This is also the latest OpenUSD release (2026-07-20) |
| Final PDF status | Not started |
| Last updated | 2026-10-07 |

---

## 1. Exam Blueprint (verified)

**Verified on 2026-10-07** against the official NVIDIA certification page and the official study guide PDF (v1.1.0, Oct 2025). Re-verify before Phase 13 and before the exam.

| Fact | Value |
|------|-------|
| Exam | NVIDIA-Certified Professional: OpenUSD Development (NCP-OUSD) |
| Level | Professional (NVIDIA describes it as intermediate-level) |
| Questions | 60–70 |
| Duration | 120 minutes |
| Delivery | Online, remotely proctored (requires a Certiverse account) |
| Price | $200 |
| Language | English |
| Validity | 2 years; recertify by retaking the exam |
| Stated prerequisites | 2–3 years of OpenUSD + Python/C++ experience, **or** completion of the study-guide materials |

| # | Domain | Weight | Official objectives | Book part | Study days |
|---|--------|--------|---------------------|-----------|------------|
| 1 | Composition | 23% | 1.1–1.11 | III (Ch 14–22) | 5, 6, 7 |
| 2 | Data Exchange | 15% | 4.1–4.8 | V (Ch 27–31) | 9 |
| 3 | Pipeline Development | 14% | 7.1–7.8 | VI (Ch 32–35) | 10 |
| 4 | Data Modeling | 13% | 5.1–5.6 | II (Ch 8–13) | 3, 4 |
| 5 | Debugging & Troubleshooting | 11% | 6.1–6.5 | IX (Ch 42–44) | 12 |
| 6 | Content Aggregation | 10% | 2.1–2.5 | IV (Ch 23–26) | 8 |
| 7 | Visualization | 8% | 8.1–8.4 | VIII (Ch 39–41) | 11 |
| 8 | Customizing USD | 6% | 3.1–3.8 | VII (Ch 36–38) | 11 |
| — | Fundamentals (not a scored domain) | — | — | I (Ch 1–7) | 1, 2 |

Objective numbering follows the study guide's section order: 1 Composition, 2 Content Aggregation, 3 Customizing USD, 4 Data Exchange, 5 Data Modeling, 6 Debugging, 7 Pipeline Development, 8 Visualization. Several objectives appear in more than one domain (e.g. 1.10 = 2.5, 4.3 = 7.3, 5.1 = 8.1, 1.8 = 6.2). The book teaches each one once and cross-references it.

> NVIDIA's pages spell the strength order "LIVERPS" (Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes). Older material says "LIVRPS", which is the same order without relocates. The book uses LIVERPS and explains both spellings.

---

## 2. 14-Day Study Schedule

Assumes about **4 hours per day** (study about 2.5 h, labs about 1 h, questions/flashcards about 0.5 h). Days 1–4 build foundations; composition gets three days because it is the largest domain and everything else depends on it.

| Day | Focus | Read | Labs | Practice | Done |
|-----|-------|------|------|----------|------|
| 1 | Orientation, setup, stage & layers | F1–F5, Ch 1–3 | 01–05 | FUN questions 1–15; flashcards (fundamentals) | [ ] |
| 2 | Prims, properties, schemas, file formats | Ch 4–7 | 06–07 | FUN 16–30; USDA ex. 1–4 | [ ] |
| 3 | Data modeling I: Usd/Sdf, value types, time samples | Ch 8–10 | 08–10 | DM questions 1–26 | [ ] |
| 4 | Data modeling II: primvars, metadata, extents | Ch 11–13 | 11–12 | DM 27–52; USDA ex. 5–8; **DM checkpoint** | [ ] |
| 5 | Composition I: fundamentals, sublayers, references, payloads | Ch 14–17 | 13–15, 19 | COMP 1–30 | [ ] |
| 6 | Composition II: variants, inherits/specializes, overs/relocates | Ch 18–20 | 16–18 | COMP 31–60; USDA ex. 9–14 | [ ] |
| 7 | Composition III: LIVERPS, value resolution, design & debugging; week-1 review | Ch 21–22 | 20–21 | COMP 61–92; LIVERPS cheat sheet; **week-1 review** | [ ] |
| 8 | Content aggregation | Ch 23–26 | 22–24 | CA 1–40; USDA ex. 15–18 | [ ] |
| 9 | Data exchange | Ch 27–31 | 25–28 | DE 1–60 | [ ] |
| 10 | Pipeline development | Ch 32–35 | 29–30 | PD 1–56; USDA ex. 19–22 | [ ] |
| 11 | Customizing USD + visualization | Ch 36–41 | 31–35 | CUST 1–24; VIS 1–32 | [ ] |
| 12 | Debugging & performance; **Mock Exam 1** | Ch 42–44 | 36 | DBG 1–44; Mock 1 (120 min) + review | [ ] |
| 13 | Weak-area repair; **Mock Exam 2** | Weak chapters | 37 (capstone) | Mock 2 + review; USDA ex. 23–30; all flashcards | [ ] |
| 14 | Final revision; **Mock Exam 3** | Cheat sheets | — | Mock 3 + review; final checklist; light review only in the evening | [ ] |

**Readiness target:** at least 80% on Mock 3 and at least 70% in every domain. If you fall short, add review days before booking the exam.

---

## 3. Build Phases

| # | Phase | Status | Notes |
|---|-------|--------|-------|
| 1 | Research & curriculum | **Done** | Blueprint verified; usd-core 26.8 installed; core sources verified; verification scripts tested |
| 2 | Beginner fundamentals (F1–F5, Ch 1–7) | **Done** | F1–F5 + Ch 1–7 written and code-verified (37 Python blocks) |
| 3 | Data modeling (Ch 8–13) | **Done** | Ch 8–13 written and code-verified |
| 4 | Composition (Ch 14–22) | **In progress** | Part II done; Ch 14 next |
| 5 | Content aggregation (Ch 23–26) | Not started | |
| 6 | Data exchange (Ch 27–31) | Not started | |
| 7 | Pipeline development (Ch 32–35) | Not started | |
| 8 | Customizing USD (Ch 36–38) | Not started | |
| 9 | Visualization (Ch 39–41) | Not started | |
| 10 | Debugging & performance (Ch 42–44) | Not started | |
| 11 | Python labs (≥ 30; plan: 37) | Not started | |
| 12 | Question bank + USDA workbook + flashcards | Not started | |
| 13 | Mock exams (3 × 65) | Not started | |
| 14 | Final revision (cheat sheets, checklist, glossary) | Not started | |
| 15 | Technical audit | Not started | |
| 16 | PDF generation | Not started | |

---

## 4. Chapter Status

Status values: `—` not started · `draft` · `code-verified` · `done` · `audited`

| Ch | Title | File | Status |
|----|-------|------|--------|
| F1 | Title & disclaimer | `chapters/f1_title.md` | done |
| F2 | How to use this book | `chapters/f2_how_to_use.md` | done |
| F3 | The NCP-OUSD exam | `chapters/f3_exam_overview.md` | done |
| F4 | 14-day study plan | `chapters/f4_study_plan.md` | done |
| F5 | Setting up your lab | `chapters/f5_setup.md` | code-verified (1 VERIFY open: V-008) |
| 1 | What Is OpenUSD? | `chapters/ch01_what_is_openusd.md` | code-verified |
| 2 | The Stage | `chapters/ch02_stage.md` | code-verified |
| 3 | Layers | `chapters/ch03_layers.md` | code-verified |
| 4 | Prims and Prim Paths | `chapters/ch04_prims_paths.md` | code-verified |
| 5 | Properties: Attributes, Relationships, Metadata | `chapters/ch05_properties.md` | code-verified |
| 6 | Schemas and Model Kinds | `chapters/ch06_schemas_kinds.md` | code-verified |
| 7 | USD File Formats and Reading USDA | `chapters/ch07_file_formats.md` | code-verified |
| 8 | Usd vs. Sdf | `chapters/ch08_usd_vs_sdf.md` | code-verified |
| 9 | Value Types | `chapters/ch09_value_types.md` | code-verified |
| 10 | Time Samples and Animation Data | `chapters/ch10_time_samples.md` | code-verified |
| 11 | Primvars | `chapters/ch11_primvars.md` | code-verified |
| 12 | Metadata in Depth | `chapters/ch12_metadata.md` | code-verified |
| 13 | Built-in Schemas, Xforms, Extents | `chapters/ch13_schemas_extents.md` | code-verified |
| 14 | Composition Fundamentals | `chapters/ch14_composition_fundamentals.md` | — |
| 15 | Sublayers, Layer Stacks, Edit Targets | `chapters/ch15_sublayers_edit_targets.md` | — |
| 16 | References | `chapters/ch16_references.md` | — |
| 17 | Payloads | `chapters/ch17_payloads.md` | — |
| 18 | Variant Sets | `chapters/ch18_variants.md` | — |
| 19 | Inherits, Classes, Specializes | `chapters/ch19_inherits_specializes.md` | — |
| 20 | Overs and Relocates | `chapters/ch20_overs_relocates.md` | — |
| 21 | LIVERPS and Value Resolution | `chapters/ch21_liverps_value_resolution.md` | — |
| 22 | Composition Design and Debugging | `chapters/ch22_composition_design_debugging.md` | — |
| 23 | Asset Structure and Model Hierarchy | `chapters/ch23_asset_structure.md` | — |
| 24 | Native Scenegraph Instancing | `chapters/ch24_native_instancing.md` | — |
| 25 | Point Instancing | `chapters/ch25_point_instancing.md` | — |
| 26 | Large Scene Optimization | `chapters/ch26_large_scenes.md` | — |
| 27 | Data Exchange Concepts | `chapters/ch27_data_exchange_concepts.md` | — |
| 28 | Units, Axes, and Naming | `chapters/ch28_units_axes_naming.md` | — |
| 29 | Exporters, Converters, Importers | `chapters/ch29_exporters_importers.md` | — |
| 30 | Validating USD Assets | `chapters/ch30_validation.md` | — |
| 31 | File Formats in Depth | `chapters/ch31_file_formats_depth.md` | — |
| 32 | Pipeline Architecture & Asset Management | `chapters/ch32_pipeline_architecture.md` | — |
| 33 | Asset Resolution | `chapters/ch33_asset_resolution.md` | — |
| 34 | Exporter Hooks, Flattening, Change Processing | `chapters/ch34_flattening_change_processing.md` | — |
| 35 | Build Configurations & DCC Integration | `chapters/ch35_build_dcc.md` | — |
| 36 | The Plugin System | `chapters/ch36_plugins.md` | — |
| 37 | Custom Schemas | `chapters/ch37_custom_schemas.md` | — |
| 38 | Kinds, Fallbacks, File Formats, Resolvers, Scene Indices | `chapters/ch38_kinds_fallbacks_plugins.md` | — |
| 39 | UsdGeom | `chapters/ch39_usdgeom.md` | — |
| 40 | UsdShade | `chapters/ch40_usdshade.md` | — |
| 41 | UsdLux and Rendering | `chapters/ch41_usdlux.md` | — |
| 42 | Stage Introspection & Composition Debugging | `chapters/ch42_introspection_debugging.md` | — |
| 43 | Diagnostics and Profiling Tools | `chapters/ch43_diagnostics_profiling.md` | — |
| 44 | Performance: Load and Render Times | `chapters/ch44_performance.md` | — |
| B1 | Glossary | `chapters/b1_glossary.md` | — |
| B2 | References | `references/references.md` | — |
| B3 | Objective coverage matrix | `chapters/b3_coverage.md` | — |

---

## 5. Python Labs

**Completed: 0 / 37** (minimum required: 30). Mark a lab done only after it has been run and its real output captured.

| Lab | Title | Status | Lab | Title | Status |
|-----|-------|--------|-----|-------|--------|
| 01 | Install & verify usd-core | — | 20 | LIVERPS laboratory | — |
| 02 | First stage | — | 21 | Composition introspection | — |
| 03 | Open & traverse | — | 22 | Component & assembly | — |
| 04 | Root/session layers | — | 23 | Native instancing | — |
| 05 | Sublayer stack | — | 24 | PointInstancer | — |
| 06 | Attributes & value types | — | 25 | JSON/OBJ → USD converter | — |
| 07 | Relationships | — | 26 | Units & up-axis | — |
| 08 | Metadata | — | 27 | Asset validator | — |
| 09 | Sdf specs & ChangeBlock | — | 28 | Dependencies, flatten, USDZ | — |
| 10 | Time samples | — | 29 | Asset resolution | — |
| 11 | Mesh + extent | — | 30 | Notices & change blocks | — |
| 12 | Primvars | — | 31 | Codeless custom schema | — |
| 13 | References | — | 32 | Custom kinds & fallbacks | — |
| 14 | Time-offset references | — | 33 | Xforms & cameras | — |
| 15 | Payloads & masks | — | 34 | PreviewSurface & binding | — |
| 16 | Variant sets | — | 35 | UsdLux lights | — |
| 17 | Classes & inherits | — | 36 | Debugging toolkit | — |
| 18 | Specializes vs inherits | — | 37 | Capstone pipeline | — |
| 19 | Edit targets | — | | | |

---

## 6. Questions, Exercises, Flashcards

| Set | File | Target | Done |
|-----|------|--------|------|
| Fundamentals (FUN) | `questions/qbank_fundamentals.md` | 30 | 0 |
| Composition (COMP) | `questions/qbank_composition.md` | 92 | 0 |
| Data Exchange (DE) | `questions/qbank_data_exchange.md` | 60 | 0 |
| Pipeline Development (PD) | `questions/qbank_pipeline.md` | 56 | 0 |
| Data Modeling (DM) | `questions/qbank_data_modeling.md` | 52 | 0 |
| Debugging (DBG) | `questions/qbank_debugging.md` | 44 | 0 |
| Content Aggregation (CA) | `questions/qbank_content_aggregation.md` | 40 | 0 |
| Visualization (VIS) | `questions/qbank_visualization.md` | 32 | 0 |
| Customizing USD (CUST) | `questions/qbank_customizing.md` | 24 | 0 |
| **Question bank total** | | **430** | **0** |
| In-chapter practice questions | `chapters/*` | about 2–3 per concept + 8–15 per chapter | 0 |
| USDA reading exercises | `questions/usda_exercises.md` | 30 | 0 |
| Flashcards | `questions/flashcards.md` | ≥ 160 | 0 |

## 7. Mock Exams

Each paper has 65 questions in 120 minutes, split by blueprint: COMP 15, DE 10, PD 9, DM 8, DBG 7, CA 7, VIS 5, CUST 4.

| Mock | Paper | Answer key | Status | Learner score | Weakest domains |
|------|-------|------------|--------|---------------|-----------------|
| 1 | `mock-exams/mock01_paper.md` | `mock-exams/mock01_answers.md` | — | — | — |
| 2 | `mock-exams/mock02_paper.md` | `mock-exams/mock02_answers.md` | — | — | — |
| 3 | `mock-exams/mock03_paper.md` | `mock-exams/mock03_answers.md` | — | — | — |

## 8. Cheat Sheets & Final Checklist

| Item | File | Status |
|------|------|--------|
| LIVERPS & value resolution | `cheat-sheets/cs_liverps.md` | — |
| USDA syntax | `cheat-sheets/cs_usda_syntax.md` | — |
| Python API quick reference | `cheat-sheets/cs_python_api.md` | — |
| List editing | `cheat-sheets/cs_list_editing.md` | — |
| Primvars & interpolation | `cheat-sheets/cs_primvars.md` | — |
| Instancing decisions | `cheat-sheets/cs_instancing.md` | — |
| Debugging toolkit | `cheat-sheets/cs_debugging.md` | — |
| File formats & CLI tools | `cheat-sheets/cs_file_formats_tools.md` | — |
| Schemas & kinds | `cheat-sheets/cs_schemas_kinds.md` | — |
| Exam domains one-pager | `cheat-sheets/cs_exam_domains.md` | — |
| Final certification checklist | `cheat-sheets/final_checklist.md` | — |

---

## 9. Weak Areas (learner)

Fill in after chapter checkpoints and mock exams. The agent should give extra practice for anything listed here.

| Date | Source (quiz/mock) | Domain / topic | Score | Action |
|------|--------------------|----------------|-------|--------|
| — | — | — | — | — |

## 10. Open VERIFY Items

Claims that must be confirmed against official docs or the installed USD before the audit.

| ID | Topic | Where | Status |
|----|-------|-------|--------|
| V-001 | Which command-line tools ship with pip `usd-core` | F5, Ch 7, Ch 31 | **Resolved**: none. Teach the tools as `.norun` blocks and give Python equivalents |
| V-002 | Relocates authoring API in USD 26.08 | Ch 20, Ch 21 | **Resolved**: layer metadata `Sdf.Layer.relocates` (plus `HasRelocates`/`ClearRelocates`); no `Usd.Prim` API. Composition behavior to be tested in Lab 20 |
| V-003 | UsdValidation vs. `ComplianceChecker` | Ch 30 | **Resolved**: `pxr.UsdValidation` has `ValidationRegistry`, `Validator`, `ValidatorSuite`, `ValidationContext`, `ValidationError`, `ValidationFixer`; `UsdUtils.ComplianceChecker` is absent |
| V-004 | Whether `usdGenSchema` runs from `usd-core` | Ch 37, Lab 31 | **Resolved**: not included. Lab 31 shows `schema.usda` and the generated `plugInfo.json` structure, and checks registration with `Usd.SchemaRegistry` where possible |
| V-005 | Python bindings for `TfMallocTag` and `Trace` | Ch 43, Lab 36 | **Resolved**: `Trace.Collector`, `Trace.Reporter`, `Tf.MallocTag.Initialize/GetCallTree/GetTotalBytes`, `Tf.Debug` all present |
| V-006 | Version in which `UsdUtils.LocalizeAsset` was added | Ch 22, Ch 34 | **Resolved**: 24.03 (CHANGELOG) |
| V-009 | Version-facts rows marked † in `content-standards.md` | Skill | Partly resolved: `GetPrototype` present and `GetMaster` absent in 26.08; the release numbers for the other rows still need checking |
| V-007 | Exact URLs for NVIDIA Learn OpenUSD, scalable asset structure principles, ASWF guidelines | References | **Resolved** (see source plan S14, S16, S17) |
| V-008 | Best way for a reader to get usdview (NVIDIA prebuilt OpenUSD binaries vs. building from source) | F5, Ch 41 | Open |

## 11. Final PDF Status

| Step | Status |
|------|--------|
| Build script (`final/build_book.py`) | — |
| Stylesheet (`final/book.css`, A4) | — |
| Diagrams (`final/assets/diagrams/`) | — |
| Technical audit (`final/AUDIT_REPORT.md`) | — |
| PDF render (`final/NCP-OUSD_Study_Book.pdf`) | — |
| Print checklist passed | — |
| Page count | — |

Toolchain notes (2026-10-07): system has Python 3.12.3, pip, and Google Chrome. `usd-core` 26.8 is installed in `.venv`. pandoc, WeasyPrint, and LaTeX are not installed. In Phase 16, install `markdown`, `pymdown-extensions`, and `weasyprint` into `.venv`, with Chrome headless as the fallback PDF renderer.

---

## 12. Change Log

| Date | Session | Change |
|------|---------|--------|
| 2026-10-07 | 1 | Verified blueprint and exam facts against the official NVIDIA page and study guide v1.1.0. Created the skill, the directory structure, this master plan, `01_TABLE_OF_CONTENTS.md`, the 14-day schedule, and `references/00_SOURCE_PLAN.md`. |
| 2026-10-07 | 1 | Found an earlier parallel run of the same request with a different chapter numbering. Kept this plan (user's choice) and moved the earlier files to `_archive/prior_session_2026-10-07/`, including a draft Ch 1 that can be mined when writing Ch 1. Merged into the skill: verification scripts (`scripts/`), question-format and mock-exam rules, print checks, and a version-facts table. Remapped `references/NVIDIA_EXAM_OBJECTIVES.md` to the new chapter numbers. Checked key version facts against the OpenUSD CHANGELOG. Changed Ch 30 to teach UsdValidation, with ComplianceChecker covered as legacy. |
| 2026-10-07 | 2 | **Phase 1 complete.** Installed usd-core 26.8 (USD 26.08) in `.venv`. Probed the APIs and resolved V-001 through V-005 and V-007. Verified 14 source URLs. Smoke-tested `check_code_blocks.py` and `check_usda_blocks.py`. Updated the skill's environment notes: usd-core has no command-line tools, so the book teaches Python equivalents. |
| 2026-10-07 | 3 | Wrote front matter F1–F5 (about 590 lines). F5 Python blocks pass `check_code_blocks.py` (2 run, 3 argument-driven scripts checked by hand). Corrected a draft claim: in a fresh session `CreateNew` silently starts an empty layer over an existing file; it raises an error only if the layer is already open. |
| 2026-10-07 | 4 | Wrote Part I in full: Ch 1–7 (plus earlier F1–F5). All chapter Python/USDA blocks pass the checkers (37 Python). Proceeding into Part II without pausing. |
| 2026-10-07 | 5 | Wrote Ch 8 (Usd vs Sdf, Obj 6.1 ChangeBlock) and Ch 9 (value types, Obj 5.2). Both code-verified. Next: Ch 10 time samples. |
| 2026-10-07 | 6 | Finished Part II: Ch 10–13 (time samples & layer offsets Obj 1.4, primvars Obj 5.1/8.1, metadata Obj 5.3/7.6, extents Obj 5.6). 24 Python + 25 USDA blocks verified. |
