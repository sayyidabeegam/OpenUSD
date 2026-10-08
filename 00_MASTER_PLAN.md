# 00 — MASTER PLAN: NCP-OUSD 14-Day Study Book

Single source of truth for progress. Update at the end of every work session.
Skill: `.cursor/skills/openusd-certification/` · Structure: `01_TABLE_OF_CONTENTS.md` · Sources: `references/00_SOURCE_PLAN.md` · Objectives: `references/NVIDIA_EXAM_OBJECTIVES.md`

| Item | Value |
|------|-------|
| Current phase | **Phase 16 — A4 PDF** (Phase 15 complete) |
| Next work unit | Phase 16: print checklist / remaining densify — PDF **866 pp** vs original 320–400 target |
| Learner level | Complete beginner in OpenUSD |
| USD version verified against | **USD 26.08** (`usd-core` 26.8 in `.venv`, Python 3.12.3). This is also the latest OpenUSD release (2026-07-20) |
| Final PDF status | WeasyPrint A4 **866 pp** (was 1516 → 1320 → 866). Still above 320–400; chapters dominate |
| Last updated | 2026-10-08 |

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
| 4 | Composition (Ch 14–22) | **Done** | Ch 14–22 written and code-verified |
| 5 | Content aggregation (Ch 23–26) | **Done** | Ch 23–26 written and code-verified |
| 6 | Data exchange (Ch 27–31) | **Done** | Ch 27–31 written and code-verified |
| 7 | Pipeline development (Ch 32–35) | **Done** | Ch 32–35 written and code-verified |
| 8 | Customizing USD (Ch 36–38) | **Done** | Ch 36–38 written and code-verified |
| 9 | Visualization (Ch 39–41) | **Done** | Ch 39–41 written and code-verified |
| 10 | Debugging & performance (Ch 42–44) | **Done** | Ch 42–44 written and code-verified |
| 11 | Python labs (≥ 30; plan: 37) | **Done** | Labs 01–37 written, executed, code-verified |
| 12 | Question bank + USDA workbook + flashcards | **Done** | 432 bank + 30 USDA + 180 flashcards |
| 13 | Mock exams (3 × 65) | **Done** | Mock 1 medium, Mock 2 medium-hard, Mock 3 hard |
| 14 | Final revision (cheat sheets, checklist, glossary) | **Done** | 11 sheets + checklist + glossary 167 + coverage + references |
| 15 | Technical audit | **Done** | `final/AUDIT_REPORT.md`. Checkers pass; V-008/V-009 closed; A-013/A-014 closed or accepted |
| 16 | PDF generation | **In progress** | Compact print edition **866 pp**. Source Markdown unchanged |

---

## 4. Chapter Status

Status values: `—` not started · `draft` · `code-verified` · `done` · `audited`

| Ch | Title | File | Status |
|----|-------|------|--------|
| F1 | Title & disclaimer | `chapters/f1_title.md` | done |
| F2 | How to use this book | `chapters/f2_how_to_use.md` | done |
| F3 | The NCP-OUSD exam | `chapters/f3_exam_overview.md` | done |
| F4 | 14-day study plan | `chapters/f4_study_plan.md` | done |
| F5 | Setting up your lab | `chapters/f5_setup.md` | **done** (V-008 closed) |
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
| 14 | Composition Fundamentals | `chapters/ch14_composition_fundamentals.md` | code-verified |
| 15 | Sublayers, Layer Stacks, Edit Targets | `chapters/ch15_sublayers_edit_targets.md` | code-verified |
| 16 | References | `chapters/ch16_references.md` | code-verified |
| 17 | Payloads | `chapters/ch17_payloads.md` | code-verified |
| 18 | Variant Sets | `chapters/ch18_variants.md` | code-verified |
| 19 | Inherits, Classes, Specializes | `chapters/ch19_inherits_specializes.md` | code-verified |
| 20 | Overs and Relocates | `chapters/ch20_overs_relocates.md` | code-verified |
| 21 | LIVERPS and Value Resolution | `chapters/ch21_liverps_value_resolution.md` | code-verified |
| 22 | Composition Design and Debugging | `chapters/ch22_composition_design_debugging.md` | code-verified |
| 23 | Asset Structure and Model Hierarchy | `chapters/ch23_asset_structure.md` | code-verified |
| 24 | Native Scenegraph Instancing | `chapters/ch24_native_instancing.md` | code-verified |
| 25 | Point Instancing | `chapters/ch25_point_instancing.md` | code-verified |
| 26 | Large Scene Optimization | `chapters/ch26_large_scenes.md` | code-verified |
| 27 | Data Exchange Concepts | `chapters/ch27_data_exchange_concepts.md` | code-verified |
| 28 | Units, Axes, and Naming | `chapters/ch28_units_axes_naming.md` | code-verified |
| 29 | Exporters, Converters, Importers | `chapters/ch29_exporters_importers.md` | code-verified |
| 30 | Validating USD Assets | `chapters/ch30_validation.md` | code-verified |
| 31 | File Formats in Depth | `chapters/ch31_file_formats_depth.md` | code-verified |
| 32 | Pipeline Architecture & Asset Management | `chapters/ch32_pipeline_architecture.md` | code-verified |
| 33 | Asset Resolution | `chapters/ch33_asset_resolution.md` | code-verified |
| 34 | Exporter Hooks, Flattening, Change Processing | `chapters/ch34_flattening_change_processing.md` | code-verified |
| 35 | Build Configurations & DCC Integration | `chapters/ch35_build_dcc.md` | code-verified |
| 36 | The Plugin System | `chapters/ch36_plugins.md` | code-verified |
| 37 | Custom Schemas | `chapters/ch37_custom_schemas.md` | code-verified |
| 38 | Kinds, Fallbacks, File Formats, Resolvers, Scene Indices | `chapters/ch38_kinds_fallbacks_plugins.md` | code-verified |
| 39 | UsdGeom | `chapters/ch39_usdgeom.md` | code-verified |
| 40 | UsdShade | `chapters/ch40_usdshade.md` | code-verified |
| 41 | UsdLux and Rendering | `chapters/ch41_usdlux.md` | code-verified |
| 42 | Stage Introspection & Composition Debugging | `chapters/ch42_introspection_debugging.md` | code-verified |
| 43 | Diagnostics and Profiling Tools | `chapters/ch43_diagnostics_profiling.md` | code-verified |
| 44 | Performance: Load and Render Times | `chapters/ch44_performance.md` | code-verified |
| B1 | Glossary | `chapters/b1_glossary.md` | **done** (167 terms) |
| B2 | References | `references/references.md` | **done** |
| B3 | Objective coverage matrix | `chapters/b3_coverage.md` | **done** |

---

## 5. Python Labs

**Completed: 37 / 37** (minimum required: 30). Mark a lab done only after it has been run and its real output captured.

| Lab | Title | Status | Lab | Title | Status |
|-----|-------|--------|-----|-------|--------|
| 01 | Install & verify usd-core | done | 20 | LIVERPS laboratory | done |
| 02 | First stage | done | 21 | Composition introspection | done |
| 03 | Open & traverse | done | 22 | Component & assembly | done |
| 04 | Root/session layers | done | 23 | Native instancing | done |
| 05 | Sublayer stack | done | 24 | PointInstancer | done |
| 06 | Attributes & value types | done | 25 | JSON/OBJ → USD converter | done |
| 07 | Relationships | done | 26 | Units & up-axis | done |
| 08 | Metadata | done | 27 | Asset validator | done |
| 09 | Sdf specs & ChangeBlock | done | 28 | Dependencies, flatten, USDZ | done |
| 10 | Time samples | done | 29 | Asset resolution | done |
| 11 | Mesh + extent | done | 30 | Notices & change blocks | done |
| 12 | Primvars | done | 31 | Codeless custom schema | done |
| 13 | References | done | 32 | Custom kinds & fallbacks | done |
| 14 | Time-offset references | done | 33 | Xforms & cameras | done |
| 15 | Payloads & masks | done | 34 | PreviewSurface & binding | done |
| 16 | Variant sets | done | 35 | UsdLux lights | done |
| 17 | Classes & inherits | done | 36 | Debugging toolkit | done |
| 18 | Specializes vs inherits | done | 37 | Capstone pipeline | done |
| 19 | Edit targets | done | | | |

---

## 6. Questions, Exercises, Flashcards

| Set | File | Target | Done |
|-----|------|--------|------|
| Fundamentals (FUN) | `questions/qbank_fundamentals.md` | 30 | 30 |
| Composition (COMP) | `questions/qbank_composition.md` | 92 | 92 |
| Data Exchange (DE) | `questions/qbank_data_exchange.md` | 60 | 60 |
| Pipeline Development (PD) | `questions/qbank_pipeline.md` | 56 | 56 |
| Data Modeling (DM) | `questions/qbank_data_modeling.md` | 52 | 52 |
| Debugging (DBG) | `questions/qbank_debugging.md` | 44 | 44 |
| Content Aggregation (CA) | `questions/qbank_content_aggregation.md` | 40 | 40 |
| Visualization (VIS) | `questions/qbank_visualization.md` | 32 | 32 |
| Customizing USD (CUST) | `questions/qbank_customizing.md` | 24 | **26** |
| **Question bank total** | | **430** | **432** |
| In-chapter practice questions | `chapters/*` | about 2–3 per concept + 8–15 per chapter | 0 |
| USDA reading exercises | `questions/usda_exercises.md` | 30 | 30 |
| Flashcards | `questions/flashcards.md` | ≥ 160 | 180 |

## 7. Mock Exams

Each paper has 65 questions in 120 minutes, split by blueprint: COMP 15, DE 10, PD 9, DM 8, DBG 7, CA 7, VIS 5, CUST 4.

| Mock | Paper | Answer key | Status | Learner score | Weakest domains |
|------|-------|------------|--------|---------------|-----------------|
| 1 | `mock-exams/mock01_paper.md` | `mock-exams/mock01_answers.md` | **done** | — | — |
| 2 | `mock-exams/mock02_paper.md` | `mock-exams/mock02_answers.md` | **done** | — | — |
| 3 | `mock-exams/mock03_paper.md` | `mock-exams/mock03_answers.md` | **done** | — | — |

## 8. Cheat Sheets & Final Checklist

| Item | File | Status |
|------|------|--------|
| LIVERPS & value resolution | `cheat-sheets/cs_liverps.md` | **done** |
| USDA syntax | `cheat-sheets/cs_usda_syntax.md` | **done** |
| Python API quick reference | `cheat-sheets/cs_python_api.md` | **done** |
| List editing | `cheat-sheets/cs_list_editing.md` | **done** |
| Primvars & interpolation | `cheat-sheets/cs_primvars.md` | **done** |
| Instancing decisions | `cheat-sheets/cs_instancing.md` | **done** |
| Debugging toolkit | `cheat-sheets/cs_debugging.md` | **done** |
| File formats & CLI tools | `cheat-sheets/cs_file_formats_tools.md` | **done** |
| Schemas & kinds | `cheat-sheets/cs_schemas_kinds.md` | **done** |
| Exam domains one-pager | `cheat-sheets/cs_exam_domains.md` | **done** |
| Final certification checklist | `cheat-sheets/final_checklist.md` | **done** |

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
| V-009 | Version-facts rows marked † in `content-standards.md` | Skill | **Resolved** (CHANGELOG 2026-10-08): UsdValidation 24.08/24.11/25.02; relocates 24.05/24.08/26.03; UsdLux `inputs:` 21.02; MaterialBindingAPI 22.11; GetMaster deprecate 20.11 / remove 21.08; UTF-8 24.03; splines 24.03/25.05/25.08 |
| V-007 | Exact URLs for NVIDIA Learn OpenUSD, scalable asset structure principles, ASWF guidelines | References | **Resolved** (see source plan S14, S16, S17) |
| V-008 | Best way for a reader to get usdview (NVIDIA prebuilt OpenUSD binaries vs. building from source) | F5, Ch 41 | **Resolved**: NVIDIA 25.08 py3.12 Win/Linux prebuilts include usdview (`usdview_gui.bat` / `.sh`); no macOS package; lags book 26.08; usd-core has no usdview |

## 11. Final PDF Status

| Step | Status |
|------|--------|
| Build script (`final/build_book.py`) | **Done** (Markdown → HTML → WeasyPrint; Chrome fallback) |
| Stylesheet (`final/book.css`, A4) | **Done** (grayscale callouts; compact pass 2) |
| Diagrams (`final/assets/diagrams/`) | — (monospace diagrams in chapters) |
| Technical audit (`final/AUDIT_REPORT.md`) | **Done** (2026-10-08) |
| PDF render (`final/NCP-OUSD_Study_Book.pdf`) | **Done** (WeasyPrint 70.0) |
| Print checklist passed | Partial: A4 + embedded fonts + page numbers. Over original 320–400 budget |
| Page count | **866** (1516 → 1320 CSS → 866 print-compact). Target was 320–400; 13-step chapters cannot hit that without cutting Part III |

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
| 2026-10-08 | 7 | Wrote Ch 20 (overs vs typeless def, referenced overrides, relocates authoring/limits; Obj 1.8/6.2) and Ch 21 (LIVERPS, two-step strength, value resolution, layer offsets, clips, ten puzzles; Obj 1.1/1.6/1.8). Both code-verified. Re-verified Ch 14–19 and 22: all pass. **Phase 4 complete.** |
| 2026-10-08 | 7 | Wrote Ch 24 (native instancing, prototypes, proxies, instance-root overrides, Obj 1.10). Re-verified Ch 23, 25–28, 39. **Phase 5 complete.** Next: Ch 29 exporters. |
| 2026-10-08 | 8 | Wrote Ch 29 (JSON/OBJ converter, PreviewSurface+MaterialBindingAPI, custom attrs, DCC importer, exporter hooks; Obj 4.5/4.7/4.8) and Ch 30 (UsdValidation, usdchecker stand-in, ComplianceChecker gone, pipeline_check; Obj 4.6). Both code-verified. Next: Ch 31. |
| 2026-10-08 | 9 | Wrote Ch 31 (USDA vs USDC sizes, USDZ ZIP_STORED, magic bytes, usdcat/usdzip stand-ins; Obj 4.3/7.3). **Phase 6 complete.** Wrote Ch 32 (pipeline work/publish/pin, folders, ComputeAllDependencies vs ExtractExternalReferences, Obj 7.2). Both code-verified. Next: Ch 33. |
| 2026-10-08 | 9 | Wrote Ch 33 (Ar Resolve vs layer anchor, DefaultResolverContext, Obj 7.7 validation, custom resolver integration; Obj 3.5/6.3/7.5/7.7). `AnchorRelativePath` gone on 26.08. Code-verified. Next: Ch 34. |
| 2026-10-08 | 9 | Wrote Ch 34 (pipeline hooks, Flatten vs FlattenLayerStack vs Export, ModifyAssetPaths, ObjectsChanged, ChangeBlock 1-vs-3 notices; Obj 1.9/6.1). `listener.Revoke()`; DefinePrim may fail inside ChangeBlock. Code-verified. Next: Ch 35. |
| 2026-10-08 | 9 | Wrote Ch 35 (`GetVersion` (0,26,8), plugin ABI matching, DCC round-trip payloads, UsdPhysics Apply; Obj 3.1/3.2/7.4/7.8). **Phase 7 complete.** Next: Ch 36. |
| 2026-10-08 | 10 | Wrote Ch 36 (`plugInfo.json`, `Plug.Registry`, `RegisterPlugins` resource plugin, four plugin jobs; Obj 3.1), Ch 37 (`schema.usda`, codeless vs codeful, `UsdTyped` vs `UsdAPISchemaBase`, Obj 3.4/3.6/4.5), Ch 38 (Kind.Registry no Python Register, variant fallbacks, SdfFileFormat, Ar/Hydra concepts; Obj 3.3/3.5/3.7/3.8). **Phase 8 complete.** Next: Ch 40. |
| 2026-10-08 | 11 | Wrote Ch 40 (UsdShade Material/Shader/NodeGraph, connections, PreviewSurface, UVTexture + PrimvarReader_float2, Obj 8.4 displayColor reader, MaterialBindingAPI Apply/Bind/purpose/strength/collections, interface inputs; Obj 8.2/8.3/8.4) and Ch 41 (UsdLux types, LightAPI built-in vs ShadowAPI/ShapingAPI Apply, intensity×2^exposure, color temperature enable, Hydra/usdview concepts; Obj 8.x). Bind without Apply still writes the rel; Distant intensity fallback 50000; `UsdImaging`/`Hd` absent from usd-core. **Phase 9 complete.** Next: Ch 42. |
| 2026-10-08 | 12 | Wrote Ch 42 (layer stack/mute/edit target, missing prims, property stack/blocks/time, InvalidAssetPath vs UnresolvedPrimPath, ComputeAllDependencies unresolved, visual purpose/scheme, eight-step procedure; Obj 6.2/6.3/6.4), Ch 43 (Tf.Status/Warn/ErrorException, TfDebug USD_CHANGES, CoalescingDiagnosticDelegate, Trace Collector/Reporter, MallocTag 0 bytes on usd-core, Pcp errors; Obj 6.5), Ch 44 (USDC vs usda wrapper id, LoadNone vs OpenMasked, instancing GetPrototype, ChangeBlock 6→1 notices, ModelAPI drawMode cards, perf checklist; Obj 6.1/6.4). **Phase 10 complete.** All chapters Ch 1–44 code-verified. Next: Python labs. |
| 2026-10-08 | 13 | Wrote Python labs 01–09 (verify usd-core, first stage, traverse, session vs root, sublayer mute, value types, relationships, metadata/customData, Sdf+ChangeBlock 6→1 notices). Each `.py` executed; each `.md` passes `check_code_blocks.py`. Next: labs 10–12. |
| 2026-10-08 | 14 | Wrote Python labs 10–18 (time samples Get() None / linear vs held; Mesh extent via ComputeExtentFromPlugins + subdivisionScheme none; indexed vertex displayColor; defaultPrim vs UnresolvedPrimPath vs explicit vs internal refs; LayerOffset stageTime=offset+scale*layerTime; LoadNone still loads references, OpenMasked not Open(path,mask); VariantSets.GetNames vs GetVariantNames; inherit broadcast + local override; I beats R, R beats S, local beats both). Each `.py` executed; each `.md` passes `check_code_blocks.py`. |
| 2026-10-08 | 15 | Wrote Python labs 19–21 (GetEditTargetForLocalLayer maps offset 10 so Set at 20 stores at 10, bare EditTarget stores 20, EditContext restores, anonymous layer not in stack; LIVERPS L/I/V beat R, S loses; GetPrimStack/GetPropertyStack/ResolveInfo/PrimCompositionQuery). Each `.py` executed; each `.md` passes `check_code_blocks.py`. Next: labs 22–24. |
| 2026-10-08 | 16 | Wrote Python labs 22–27 (model hierarchy: Mug kind component but IsComponent False; native instancing GetPrototype / GetMaster gone / de-instance; PointInstancer append BackOfAppendList + InvisId mask; JSON/OBJ converter cm→m and OBJ 1-based faces; units not converted on reference, factor 100 + rotateX −90; UsdValidation StageMetadataChecker, ComplianceChecker absent). Each `.py` executed; each `.md` passes `check_code_blocks.py`. Next: labs 28–30. |
| 2026-10-08 | 17 | Wrote Python labs 28–37 and **closed Phase 11** (37/37). Deps 3-tuple + Flatten vs FLS + USDZ STORE; Ar naive vs anchored Resolve + search path; ObjectsChanged resync/info + ChangeBlock 1-vs-3 + DefinePrim trap; schema.usda parse ≠ register; Kind.Registry no Register; xformOpOrder + Gf.Camera FOV; PreviewSurface Apply-then-Bind; Distant 50000 vs Sphere 1; CoalescingDiagnosticDelegate + Trace + MallocTag 0 bytes; capstone component/assembly/validate/deps. Each `.py` executed; each `.md` passes `check_code_blocks.py`. Next: Phase 12 question bank (COMP first). |
| 2026-10-08 | 18 | Wrote `questions/qbank_composition.md` **COMP-001–COMP-092** (domain complete). Original items only; mapped to Obj 1.1–1.11. USDA/Python-reading answers re-run on usd-core 26.8 (I beats R/V/S; LoadNone still loads refs; Flatten bakes refs / FlattenLayerStack keeps them; OpenMasked not Open(mask=); GetPrototype / no GetMaster; instance-proxy OverridePrim raises; GetVariantEditContext with empty selection authors local; stronger default hides weaker samples). `check_usda_blocks.py` 11/11; python stems `.norun`. Next: DE question bank. |
| 2026-10-08 | 19 | Wrote `questions/qbank_data_exchange.md` **DE-001–DE-060** (domain complete, Obj 4.1–4.8). Verified: CreateNew `.usd` crate magic `PXR-USDC` / formatId `usd`; USDA copied to `.usd` still text; MakeValidIdentifier `Crate Box`→`Crate_Box`, `2ball`→`_ball`; units not converted on reference (size 1.0, factor 100); ComplianceChecker gone; geom vs core StageMetadataChecker; Bind without Apply HasAPI False; ComputeAllDependencies 3-tuple; no UsdMtlx/usdcat. Next: PD question bank. |
| 2026-10-08 | 20 | Wrote `questions/qbank_pipeline.md` **PD-001–PD-056** (domain complete, Obj 7.1–7.8). Work/publish/pin; Compute vs Extract 3-tuples; Ar Resolver vs DefaultResolver; AnchorRelativePath gone; search path ignores `./`; Open pathResolverContext; customData ByKey vs userDocBrief; Flatten keeps secrets. USDA block parses. Next: DM question bank. |
| 2026-10-08 | 21 | Wrote `questions/qbank_data_modeling.md` **DM-001–DM-052** (domain complete, Obj 5.1–5.6). Point/color/asset roles; Get() None with samples only; linear vs held; PrimvarsAPI + indexed displayColor; FindPrimvarWithInheritance; ComputeExtentFromPlugins then Set; catmullClark fallback; null prim IsDefined raises; ComputeVisibility vs Get. Next: DBG question bank. |
| 2026-10-08 | 22 | Wrote `questions/qbank_debugging.md` **DBG-001–DBG-044** (domain complete, Obj 6.1–6.5). ChangeBlock delays notices (6 vs 1; DefinePrim trap); stacks/mute/LIVERPS/proxy; InvalidAssetPath vs UnresolvedPrimPath; CoalescingDiagnosticDelegate before Open; Trace vs MallocTag 0 bytes; USD_CHANGES / TF_DEBUG. Next: CA question bank. |
| 2026-10-08 | 23 | Wrote `questions/qbank_content_aggregation.md` **CA-001–CA-040** (domain complete, Obj 2.1–2.5). Native GetPrototype / Traverse skips proxies; instance-root primvars vs proxy OverridePrim raises; PI AddTarget prepend trap + BackOfAppendList; InvisId mask count still 3; Boundable not Gprim; broken model chain IsComponent False. Next: VIS question bank. |
| 2026-10-08 | 24 | Wrote `questions/qbank_visualization.md` **VIS-001–VIS-032** (Obj 8.1–8.4) and `questions/qbank_customizing.md` **CUST-001–CUST-024** (Obj 3.1–3.8). Apply-then-Bind; ComputeSurfaceSource len 3; PrimvarReader_float3 varname displayColor; no UsdMtlx; Kind.Registry.Register gone; parse schema ≠ register; SceneIndex needs imaging build. Next: FUN question bank (last Phase 12 domain). |
| 2026-10-08 | 25 | Wrote `questions/qbank_fundamentals.md` **FUN-001–FUN-030** — **qbank 430/430**. Wrote USDA exercises **U-001–U-010** (sublayer, I vs R, L vs V, over, UnresolvedPrimPath, offset samples, LoadNone, R vs S, mute, inherit broadcast). 14 USDA blocks parse. Next: U-011–U-020. |
| 2026-10-08 | 26 | Finished USDA **U-001–U-030** (29 parseable blocks). Relocates source ignored; instance nested over size 1; implied inherit 0.9; mug IsComponent False. Wrote flashcards **FC-001–FC-060** (FUN+COMP). Next: FC-061–FC-120. |
| 2026-10-08 | 27 | Closed Phase 12: flashcards **FC-001–FC-180** (≥160). Re-verified NCP-OUSD blueprint on the official NVIDIA page (60–70 Q, 120 min, $200, eight domain weights unchanged). Wrote **Mock 1** paper + answer key (`mock-exams/mock01_paper.md`, `mock01_answers.md`): 65 original stems, COMP 15 / DE 10 / PD 9 / DM 8 / DBG 7 / CA 7 / VIS 5 / CUST 4. 19 USDA blocks parse. Facts re-run on usd-core 26.8 (I vs R vs S, LoadNone, Flatten vs FLS, relocates dest over, Tokens.z, Distant 50000, Apply/HasAPI, OpenMasked). Next: Mock 2 paper. |
| 2026-10-08 | 28 | Wrote **Mock 2** paper + answer key (medium-hard). Mute reveals weaker sublayer; local beats variant; stronger-layer list-op delete; empty VariantEditContext authors local; EditTargetForLocalLayer maps t=20→10; default AddTarget does **not** Front-prepend on 26.08 (use explicit FrontOfPrependList); PointInstancer Boundable not Gprim; ComputeVisibility vs Get inherited; UsdMtlx ImportError. 13 USDA blocks parse. Next: Mock 3 paper. |
| 2026-10-08 | 29 | Wrote **Mock 3** paper + answer key (hard) and **closed Phase 13**. Weak-stack local beats inherit; I beats V; wrong relocate path ignored (sibling over); payload local over exists under LoadNone; session 9 vs root 1; shot variant selection beats asset; inherit broadcast; `inputs:intensity`; ObjectsChanged resync vs info; GetForwardedTargets; linear/held Get(99) hold last sample; mute drops layer from GetLayerStack. 8 USDA blocks parse. Next: Phase 14 cheat sheets. |
| 2026-10-08 | 30 | Phase 14: six A4 cheat sheets — LIVERPS, USDA syntax, Python API, list editing, primvars, instancing. Facts from usd-core 26.8 (two-step LIVERPS, `payload` singular, `GetPrototype`, PI `AddTarget` position, `FindPrimvarWithInheritance`). Next: `cs_debugging.md`, `cs_file_formats_tools.md`, `cs_schemas_kinds.md`. |
| 2026-10-08 | 31 | Finished remaining cheat sheets (`cs_debugging`, `cs_file_formats_tools`, `cs_schemas_kinds`, `cs_exam_domains`) and `final_checklist.md` (every Obj 1.1–8.4 + exam-day logistics). CLI listed as `.norun` with Python stand-ins. Next: glossary `chapters/b1_glossary.md`. |
| 2026-10-08 | 32 | **Closed Phase 14.** Glossary `chapters/b1_glossary.md` (167 terms, USD 26.08). Coverage matrix `chapters/b3_coverage.md` (Obj 1.1–8.4 → chapter/lab/bank/mock). Printed references `references/references.md` (S01–S19). Next: Phase 15 technical audit. |
| 2026-10-08 | 33 | **Phase 15 Parts 1–2.** USDA 392/0 fail (1 skip: Ch 25 fragment). Python chapters 247/0, labs 37/0 + 37 `.py` exit 0. Closed V-008 (NVIDIA 25.08 Win/Linux usdview; no macOS prebuilt) and V-009 (CHANGELOG † rows). Fixed A-001–A-011 (cs_primvars `.norun`, F5 usdview, CUST-025/026 for Obj 3.8, mock 5.1/8.1 dual-tags). Bank **432**. Open: A-013 cross-refs, A-014 full key re-solve. |
| 2026-10-08 | 33 | **Closed Phase 15.** Part 3: 1022 `§` cites and 364 Lab cites resolve; high-risk key facts re-run on 26.8. Next: Phase 16 PDF. |
| 2026-10-08 | 34 | Phase 16 first PDF: installed markdown/pymdown/weasyprint; `final/build_book.py` + `book.css`. WeasyPrint A4, fonts embedded. 1516 pp then compact CSS **1320 pp** (target 320–400). Next: shrink labs then qbank layout. |
| 2026-10-08 | 35 | Print-compact: run-in 13-step labels; drop in-chapter quizzes + further reading from PDF only; labs print output not full scripts; qbank 2-col. **866 pp**. Two-column chapters abandoned (WeasyPrint too slow). Source files unchanged. |
