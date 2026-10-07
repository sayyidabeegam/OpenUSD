# Source and Reference Plan

How facts are sourced, verified, and cited. The book must be understandable offline; sources back the content, they never replace explanations.

## Source tiers

| Tier | Use | Examples |
|------|-----|----------|
| 1 — Exam authority | Blueprint, objectives, format | NVIDIA certification page, NVIDIA study guide PDF |
| 2 — Technical authority | Definitions, API behavior, specs | openusd.org docs + API reference, OpenUSD GitHub source and CHANGELOG |
| 3 — Official curriculum | Teaching sequence, examples to cross-check | NVIDIA Learn OpenUSD, NVIDIA OpenUSD docs, NVIDIA DLI courses |
| 4 — Secondary (cross-check only) | Production context, idioms | ASWF USD working group guidelines, USD Survival Guide, AOUSD materials |

Rules:
- Every technical claim must be checkable against tier 1–2, or confirmed by running code against `usd-core`.
- Tier 4 is never the only source for a claim.
- When sources disagree, prefer the API reference and actual `usd-core` behavior, and add a `.version` note.
- Never copy NVIDIA sample questions or course text; paraphrase and cite.

## Tier 1 — Exam authority (verified 2026-10-07)

| Source | URL | Status |
|--------|-----|--------|
| NCP-OUSD certification page | https://www.nvidia.com/en-us/learn/certification/openusd-development-professional/ | Verified: blueprint and format |
| NCP-OUSD Exam Study Guide v1.1.0 (PDF) | https://dam-cdn.nvd.orangelogic.com/AssetLink/sjrg2vjhic7285sph487x53f5e54erf7.pdf | Verified: objectives and reading lists captured in `NVIDIA_EXAM_OBJECTIVES.md` |

Re-verify both at the start of Phase 14 (final revision) in case NVIDIA updates the blueprint.

## Tier 2 — Technical authority

Checked 2026-10-07. openusd.org currently serves the **26.08** documentation; the latest `usd-core` on PyPI is **26.8**.

| Source | URL | Used for | Status |
|--------|-----|----------|--------|
| OpenUSD documentation home | https://openusd.org/release/index.html | Entry point | Site verified (26.08 docs) |
| Glossary ("USD Terms and Concepts") | https://openusd.org/release/glossary.html | Definitions: LIVERPS, layer offset, edit target, list editing, value clips, flatten, over, relocates, model hierarchy, gprim | Verified |
| Tutorials | https://openusd.org/release/tut_usd_tutorials.html | Referencing layers, authoring variants, traversing, properties, xforms/time samples/layer offsets, generating schemas | Verified |
| API reference (C++, mirrors Python) | https://openusd.org/release/api/index.html | UsdStage, UsdPrim, UsdAttribute, UsdReferences, SdfLayer, SdfChangeBlock, UsdNotice, PointInstancer, etc. | Verified |
| Toolset (usdcat, usdchecker, usdzip, usdview, ...) | https://openusd.org/release/toolset.html | Command-line tools | Verified |
| USD FAQ | https://openusd.org/release/usdfaq.html | .usd format detection, sublayers vs references, over vs typeless def | Verified |
| Maximizing USD Performance | https://openusd.org/release/maxperf.html | Performance chapter | Verified |
| UsdPreviewSurface spec | https://openusd.org/release/spec_usdpreviewsurface.html | Materials | Verified |
| USDZ spec (v1.3) | https://openusd.org/release/spec_usdz.html | Packaging | Verified |
| Rendering user guide (incl. primvars) | https://openusd.org/release/user_guides/render_user_guide.html | Primvars, rendering | Verified |
| Schema domains user guides | https://openusd.org/release/user_guides/schemas/index.html | UsdLux, UsdRender, UsdVol, UsdMedia, UsdUI | Verified |
| OpenUSD GitHub | https://github.com/PixarAnimationStudios/OpenUSD | Source truth, build_usd.py, plugInfo examples | Verified (via CHANGELOG fetch) |
| CHANGELOG | https://github.com/PixarAnimationStudios/OpenUSD/blob/release/CHANGELOG.md | Version notes | Verified; findings in `technical-accuracy.md` |
| usd-core on PyPI | https://pypi.org/project/usd-core/ | Lab environment (core libraries only; no imaging/usdview) | Verified (v26.8; Python 3.9–3.14) |

## Tier 3 — Official curriculum

| Source | URL | Status |
|--------|-----|--------|
| NVIDIA Learn OpenUSD | https://docs.nvidia.com/learn-openusd/latest/index.html | Verified |
| Learn OpenUSD module 1, Setting the Stage | https://docs.nvidia.com/learn-openusd/latest/stage-setting/index.html | Verified. Other modules are under the same site; collect per-module URLs when writing each Part |
| Learn OpenUSD: Asset Structure Principles | https://docs.nvidia.com/learn-openusd/latest/asset-structure/asset-structure-principles/why-necessary.html | Verified (search) |
| NVIDIA OpenUSD docs | https://docs.omniverse.nvidia.com/usd/latest/index.html | Linked from Learn OpenUSD |
| NVIDIA OpenUSD developer resources | https://developer.nvidia.com/usd | Linked from Learn OpenUSD |
| Principles of Scalable Asset Structure in OpenUSD | https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html | Verified (search) |
| Data Aggregation Best Practices | https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/best-practices.html | Verified (search) |
| Conceptual Data Mapping (index, guidance, template) | https://docs.omniverse.nvidia.com/usd/latest/technical_reference/conceptual_data_mapping/index.html | Verified (search) |
| Example: glTF and OpenUSD Conceptual Data Mapping | https://docs.omniverse.nvidia.com/usd/latest/technical_reference/conceptual_data_mapping/glTF_concept_mapping_example.html | Verified (search); key source for Obj 4.1/4.2 |
| OpenUSD Code Samples (named in study guide) | NVIDIA docs | To locate (Phase 4) |

## Tier 4 — Secondary

| Source | Use | Status |
|--------|-----|--------|
| ASWF USD-WG Guidelines for Structuring USD Assets — https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md | Asset structure, naming | Verified (search) |
| ASWF USD-WG assets repo — https://github.com/usd-wg/assets | Test assets for importers/exporters | Verified (search) |
| USD Survival Guide (Luca Scheller) — https://lucascheller.github.io/VFX-UsdSurvivalGuide/ | Production idioms, cross-check | Verified |
| SIGGRAPH 2019 "USD Composition" course notes (named in study guide) | Composition depth | To locate (Phase 4) |
| AOUSD — https://aousd.org | History and governance | To verify (Ch 1) |

## Learn OpenUSD module → book chapter map

| Learn OpenUSD module | Book chapters |
|----------------------|---------------|
| 1 Setting the Stage | 1–6 |
| 2 Scene Description Blueprints (schemas) | 7, 10, 11 |
| 3 Composition Basics | 17–19 |
| 4 Beyond the Basics (primvars, value resolution, custom properties, kinds) | 8, 14, 15, 25, 29 |
| 5 Creating Composition Arcs | 18–27 |
| 6 Asset Structure Principles and Content Aggregation | 28, 29 |
| 7 Developing Data Exchange Pipelines | 33–39 |
| 8 Asset Modularity and Instancing | 29–32 |

## Per-part source focus

| Part | Primary sources to read before writing |
|------|----------------------------------------|
| I Foundations | Glossary; tutorials (Hello World, inspecting properties); Learn OpenUSD 1–2; toolset; FAQ (file formats) |
| II Data Modeling | Sdf types API page; UsdAttribute interpolation; UsdGeomPrimvar; tutorials (xforms/time samples); value clips glossary; spline proposal |
| III Composition | Glossary (LIVERPS, list editing, layer offset, edit target, relocates); referencing/variants tutorials; UsdReferences; Pcp errors; SIGGRAPH 2019 notes; CHANGELOG (relocates) |
| IV Content Aggregation | Scenegraph instancing; Kind; model hierarchy; PointInstancer; asset structure principles; Learn OpenUSD 6, 8 |
| V Data Exchange | Conceptual data mapping; usdchecker; usdcat; usdzip; USDZ spec; stage upAxis/linear units; UsdGeomBoundable extents |
| VI Pipeline | Ar; flatten; edit targets; SdfChangeBlock; UsdNotice; sublayers-vs-references FAQ; ASWF guidelines; UsdUtils dependencies |
| VII Customizing | PlugRegistry; usdGenSchema; file format plug-in guide; Kind registry; variant fallbacks; Ar resolver; Hydra scene index docs |
| VIII Visualization | UsdGeom, UsdShade, UsdLux docs; UsdPreviewSurface spec; MaterialBindingAPI; GeomSubset; imageable purpose |
| IX Debugging | UsdPrim/UsdProperty stacks; diagnostic delegates; TfDebug; Trace; MuteLayer; working set; maxperf |

## Citation format in the book

- In chapters: "Sources for this chapter" lists source names only (e.g. "OpenUSD Glossary — LIVERPS").
- Full entries in `references/bibliography.md` (Appendix E): `[S-NN] Title. Publisher. URL. Accessed YYYY-MM-DD.`
- Record the `usd-core` version all code was tested with in the book's front matter and Appendix F.

## Phase 1 follow-up tasks

- [x] Verify Tier 2 URLs (2026-10-07)
- [x] Locate asset structure, data mapping, ASWF sources
- [ ] Locate OpenUSD Code Samples and SIGGRAPH 2019 notes (deferred to Phase 4)
- [ ] Collect remaining Learn OpenUSD module URLs (per Part, when writing it)
- [x] Read CHANGELOG for version-sensitive items (see technical-accuracy.md)
- [x] Create `references/bibliography.md` with S-NN IDs
