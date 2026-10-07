# Source and Reference Plan

How sources are used, ranked, verified, and cited. The printed references section is generated later as `references/references.md`.

## Source hierarchy

When sources disagree, the higher tier wins. Record every conflict in the verification log.

| Tier | Source type | Used for |
|------|-------------|----------|
| 1 | NVIDIA NCP-OUSD certification page + official study guide | Blueprint, weights, objectives, exam format |
| 2 | Official OpenUSD documentation and API reference (openusd.org), OpenUSD source on GitHub | API names, behavior, terminology, composition rules |
| 3 | The installed `usd-core` itself (`help()`, `dir()`, running code) | Final say on what actually runs in the verified version |
| 4 | NVIDIA Learn OpenUSD curriculum and NVIDIA Omniverse USD docs | Teaching structure, examples, recommended study paths |
| 5 | AOUSD / ASWF USD Working Group material | Asset structure guidelines, industry conventions |
| 6 | Reputable community references (e.g. the USD Survival Guide) | Extra explanations only; never the sole source for a claim |

Third-party "practice exam" sites are **not** used as sources for content or questions.

## Primary sources

| ID | Source | URL | Status |
|----|--------|-----|--------|
| S01 | NVIDIA — OpenUSD Development Professional Certification | https://www.nvidia.com/en-us/learn/certification/openusd-development-professional/ | **Verified 2026-10-07** (weights, 60–70 Q, 120 min, $200, English, 2-yr validity) |
| S02 | NVIDIA — NCP-OUSD Exam Study Guide (v1.1.0, Oct 2025, PDF) | https://dam-cdn.nvd.orangelogic.com/AssetLink/sjrg2vjhic7285sph487x53f5e54erf7.pdf | **Verified 2026-10-07** (objectives 1.1–8.4, reading lists) |
| S03 | OpenUSD documentation home | https://openusd.org/release/index.html | **Verified 2026-10-07** (docs are for 26.08) |
| S04 | OpenUSD Glossary (LIVERPS, layer offset, edit target, flatten, primvar, over, …) | https://openusd.org/release/glossary.html | **Verified 2026-10-07** (spells it LIVERPS: Local, Inherits, VariantSets, Relocates, References, Payload, Specializes) |
| S05 | OpenUSD tutorials (Traversing a Stage, Referencing Layers, Authoring Variants, Transformations/Time-Sampled Animation/Layer Offsets, Generating New Schema Classes, Converting Between Layer Formats, Inspecting and Authoring Properties) | https://openusd.org/release/tut_usd_tutorials.html | **Verified 2026-10-07** |
| S06 | OpenUSD C++ API reference (UsdStage, UsdPrim, UsdReferences, PcpPrimIndex, SdfChangeBlock, UsdGeomPointInstancer, UsdShadeMaterialBindingAPI, UsdLux, Ar, Kind, Plug) | https://openusd.org/release/api/index.html | To verify |
| S07 | USD Toolset (usdcat, usdchecker, usdzip, usdview, usdresolve, usdtree) | https://openusd.org/release/toolset.html | **Verified 2026-10-07** (usdcat, usdchecker, usdzip, usdview, usdresolve, usdtree, usdstitch, usddiff, usdedit, usdrecord, …) |
| S08 | USD FAQ (sublayers vs. references, over vs. typeless def, .usd format detection, "just a file format?") | https://openusd.org/release/usdfaq.html | **Verified 2026-10-07** |
| S09 | USDZ file format specification | https://openusd.org/release/spec_usdz.html | **Verified 2026-10-07** (spec v1.3) |
| S10 | UsdPreviewSurface specification | https://openusd.org/release/spec_usdpreviewsurface.html | **Verified 2026-10-07** |
| S11 | Maximizing USD Performance | https://openusd.org/release/maxperf.html | **Verified 2026-10-07** |
| S12 | OpenUSD source repository (release notes, `build_usd.py`, change log) | https://github.com/PixarAnimationStudios/OpenUSD | **Verified 2026-10-07** (CHANGELOG read; latest 26.08) |
| S13 | `usd-core` on PyPI (install, version history) | https://pypi.org/project/usd-core/ | **Verified 2026-10-07** (installed usd-core 26.8) |
| S14 | NVIDIA Learn OpenUSD (Setting the Stage, Scene Description Blueprints, Composition Basics, Beyond the Basics, Creating Composition Arcs, Understanding Model Kinds, Asset Structure Principles and Content Aggregation, Asset Modularity and Instancing, Developing Data Exchange Pipelines) | https://docs.nvidia.com/learn-openusd/latest/index.html | **Verified 2026-10-07** (states it prepares for the certification) |
| S15 | NVIDIA Omniverse USD documentation and code samples (e.g. Add a Payload) | https://docs.omniverse.nvidia.com/usd/latest/index.html | **Verified 2026-10-07** |
| S16 | Principles of Scalable Asset Structure in OpenUSD (NVIDIA whitepaper) | https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html | **Verified 2026-10-07** |
| S17 | ASWF USD Working Group — asset structure guidelines | https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md | **Verified 2026-10-07** (moved here from the ASWF wiki) |
| S18 | Alliance for OpenUSD (AOUSD) | https://aousd.org | To verify |
| S19 | USD Survival Guide (community, tier 6) | https://lucascheller.github.io/VFX-UsdSurvivalGuide/ | To verify |
| S20 | "USD Composition" SIGGRAPH 2019 course notes (listed in study guide) | URL to locate | To verify |

## Source map by book part

| Part | Main sources |
|------|-------------|
| Front matter / exam | S01, S02 |
| I Fundamentals | S03, S04, S05, S14, S13 |
| II Data Modeling | S06 (Sdf types, UsdAttribute, UsdGeomPrimvar, UsdGeomBoundable/Xformable), S04, S05 |
| III Composition | S04 (LIVERPS, list editing, layer offset, edit target), S05, S06 (UsdReferences, EditTarget, Flatten, PcpPrimIndex), S08, S14, S20 |
| IV Content Aggregation | S06 (scenegraph instancing, PointInstancer, Kind, model hierarchy), S14, S16, S17 |
| V Data Exchange | S07, S08, S09, S06 (UsdUtils, stage up-axis/units), S14 |
| VI Pipeline Development | S06 (Flatten, SdfChangeBlock, UsdNotice, Ar), S08, S12, S16, S17 |
| VII Customizing USD | S05 (Generating New Schema Classes), S06 (Plug, Kind, Ar, SdfFileFormat), S12 |
| VIII Visualization | S06 (UsdGeomMesh, GeomSubset, UsdShade, UsdLux), S10 |
| IX Debugging | S06 (UsdProperty::GetPropertyStack, UsdUtilsCoalescingDiagnosticDelegate, TfDiagnosticMgr, MuteLayer, Pcp errors), S07, S11 |

## Verification procedure

For each chapter:

1. List every factual claim that is not obvious (API names, defaults, strength rules, version changes).
2. Confirm each one against a tier 1–2 source **and** by running code against the installed `usd-core` (tier 3) where possible.
3. If a claim cannot be confirmed, either drop it or mark it `> [!VERIFY]` and add it to the master plan's VERIFY table.
4. Mark version-specific behavior with `> [!VERSION]`, stating the verified USD version.
5. Add the sources used to the chapter's "Further reading" list and to the log below.

## Citation format (printed book)

`[S06] OpenUSD API Reference — UsdReferences. Pixar Animation Studios. https://openusd.org/release/api/class_usd_references.html (accessed YYYY-MM-DD).`

Chapters cite with the bracketed ID, e.g. "(see [S04] Glossary: LIVERPS)". The book must never rely on a citation in place of an explanation.

## Copyright and originality

- Paraphrase; do not copy documentation passages or NVIDIA sample questions. Short quotes (≤ 2 sentences) need attribution.
- All practice questions, mock exams, and flashcards are original. Every question file carries the header: "Original practice material. Not actual NVIDIA exam content."
- Code examples are original and written for this book; they may follow idioms shown in the official docs.

## Verification log

| Date | Source | What was checked | Result |
|------|--------|------------------|--------|
| 2026-10-07 | S01 | Domain weights, exam format, price, validity, prerequisites | Weights match the user-supplied blueprint exactly (23/15/14/13/11/10/8/6) |
| 2026-10-07 | S02 | Objective lists 1.1–8.4, recommended courses and readings, sample-question topics | Captured in TOC objective mapping and `NVIDIA_EXAM_OBJECTIVES.md`; sample questions not reproduced |
| 2026-10-07 | S12 (CHANGELOG.md) | Latest release; ComplianceChecker, UsdValidation, LocalizeAsset, relocates | Latest 26.08 (2026-07-20). ComplianceChecker: warns in 26.05, removed from usdchecker in 26.03, removed entirely in 26.08. UsdValidation since 24.08. LocalizeAsset since 24.03. Relocates initial work in 24.05 |
| 2026-10-07 | S01 | Delivery details | Certiverse account required. The en-us page says 120 minutes in both places; an earlier session saw a "90-minute" search snippet for the en-eu page, so re-check before booking |
| 2026-10-07 | S03–S05, S07–S11, S14–S17 | URLs reachable, content matches the planned use | Verified. S18 (AOUSD), S19 (Survival Guide), S20 (SIGGRAPH 2019 notes) still to check |
| 2026-10-07 | Installed usd-core 26.8 | API probes for the VERIFY list | See master plan §10 |
