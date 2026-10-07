# OpenUSD Development (NCP-OUSD) — 14-Day Study Book
## Complete Table of Contents (plan)

Page estimates are A4 targets; quality takes priority. Objective tags refer to `references/NVIDIA_EXAM_OBJECTIVES.md`. Lab numbers refer to Part X.

**Estimated total: ~370 pages** (front matter 14 · chapters ~245 · labs ~50 · USDA workshop ~12 · question bank ~40 · mock exams ~45 · revision ~30 · appendices ~25; some overlap absorbed in final layout).

---

## Front Matter (~14 pp)

| File | Title |
|------|-------|
| front-01_title-and-disclaimer.md | Title page, version, tested `usd-core` version, disclaimer (independent study material; practice questions are original, not NVIDIA exam questions) |
| front-02_how-to-use-this-book.md | How to use this book: reading order, the 13-step concept pattern, callout legend, code conventions, running labs offline |
| front-03_exam-at-a-glance.md | Exam format, blueprint table with weights, objective list summary, candidate profile, exam-day logistics |
| front-04_14-day-study-plan.md | The 14-day schedule with daily checklists and progress table |
| front-05_setup.md | Installing Python and `usd-core`, verifying the install, command-line tools, note on usdview |

---

## Part I — Getting Started with OpenUSD (Phase 2, ~38 pp)

**Ch 1 — Welcome to OpenUSD** (4 pp)
1.1 What is USD / OpenUSD (Pixar origins, open-sourcing, AOUSD) · 1.2 Scene description vs file format vs runtime · 1.3 Non-destructive layered editing · 1.4 Where OpenUSD is used (VFX, games, manufacturing, AEC, robotics, digital twins) · 1.5 The OpenUSD module map (Tf, Gf, Vt, Ar, Sdf, Pcp, Usd, UsdGeom, UsdShade, UsdLux, Hydra)

**Ch 2 — Your OpenUSD Workbench** (5 pp) — Labs 1
2.1 Installing `usd-core` · 2.2 The `pxr` Python package · 2.3 Command-line tools: usdcat, usdtree, usdchecker, usdzip, usddiff, usdresolve, usdedit · 2.4 usdview (what it is, how to get it) · 2.5 Reading API docs (C++ names → Python names)

**Ch 3 — Stages and Layers** (6 pp) — Labs 1–2
3.1 Stage · 3.2 Layer · 3.3 Root layer · 3.4 Session layer · 3.5 Sublayers (first look) · 3.6 Edit target (first look) · 3.7 In-memory vs on-disk stages, Save vs Export

**Ch 4 — Prims and the Scenegraph** (6 pp) — Lab 3
4.1 Prim · 4.2 Prim paths and `Sdf.Path` · 4.3 Pseudo-root and hierarchy · 4.4 Specifiers: `def`, `over`, `class` · 4.5 Typed vs typeless prims (over vs typeless def) · 4.6 Active/inactive prims · 4.7 Traversal basics

**Ch 5 — Properties: Attributes and Relationships** (6 pp) — Labs 4–5
5.1 Property · 5.2 Attribute · 5.3 Relationship and targets · 5.4 Property namespaces (`primvars:`, `xformOp:`, `inputs:`) · 5.5 Authored value vs fallback value · 5.6 Custom vs schema properties · 5.7 Variability (`uniform` vs varying)

**Ch 6 — Metadata** (4 pp) — Lab 6
6.1 Metadata vs properties · 6.2 Layer metadata (defaultPrim, upAxis, metersPerUnit, timeCodesPerSecond) · 6.3 Prim metadata (kind, active, hidden, documentation, assetInfo, customData) · 6.4 Property metadata · 6.5 Reading/writing metadata in Python

**Ch 7 — Schemas** (5 pp) — Lab 7
7.1 Schema · 7.2 Typed (IsA) schemas: concrete vs abstract · 7.3 API schemas: single-apply vs multiple-apply, `apiSchemas` metadata · 7.4 Schema registry and fallback values · 7.5 Built-in schema families tour

**Ch 8 — Model Kinds (first look)** (3 pp)
8.1 Kind · 8.2 component, group, assembly, subcomponent · 8.3 Why kinds matter (preview of Ch 29)

**Ch 9 — USD File Formats** (5 pp) — Lab 8 — [Obj 4.3, 7.3]
9.1 `.usda` (text) · 9.2 `.usdc` (crate, binary) · 9.3 `.usd` (either; how to detect) · 9.4 `.usdz` (package; constraints) · 9.5 USDA vs USDC trade-offs: performance, readability, diffs, archival · 9.6 Converting with usdcat and Python

---

## Part II — Data Modeling (13%) (Phase 3, ~34 pp)

**Ch 10 — Usd and Sdf: Two Views of the Same Data** (6 pp) — Lab 9 — [Obj 6.1]
10.1 Composed view (Usd) vs layer view (Sdf) · 10.2 `Sdf.Layer`, `Sdf.PrimSpec`, `Sdf.AttributeSpec`, `Sdf.RelationshipSpec` · 10.3 When to author with Sdf · 10.4 `Sdf.ChangeBlock` and batching edits · 10.5 Change processing and `Usd.Notice` (first look)

**Ch 11 — Value Types** (6 pp) — Lab 10 — [Obj 5.2]
11.1 `Sdf.ValueTypeNames` · 11.2 Scalars (bool, int, float, double, half) · 11.3 Vectors and `Gf` (Vec2/3/4 f/d/h) · 11.4 Matrices (`matrix4d`) and quaternions · 11.5 token vs string vs asset · 11.6 Arrays and `Vt` · 11.7 Roles: color3f, point3f, normal3f, vector3f, texCoord2f · 11.8 Choosing value types

**Ch 12 — Time: TimeCodes, Time Samples, Interpolation** (6 pp) — Lab 11
12.1 TimeCode and `Usd.TimeCode.Default()` · 12.2 timeCodesPerSecond, framesPerSecond, start/end time codes · 12.3 Default value vs time samples · 12.4 Held vs linear interpolation, `Usd.Stage.SetInterpolationType` · 12.5 Layer offsets (first look) · 12.6 Splines proposal (version note) · 12.7 Time-sampled velocities (first look)

**Ch 13 — Value Clips** (3 pp)
13.1 What clips are and why · 13.2 Clip metadata and `Usd.ClipsAPI` · 13.3 Where clips sit in value resolution

**Ch 14 — Primvars** (5 pp) — Lab 12 — [Obj 5.1, 8.1]
14.1 Primvar · 14.2 `UsdGeom.PrimvarsAPI` · 14.3 Interpolation: constant, uniform, varying, vertex, faceVarying · 14.4 Indexed primvars and elementSize · 14.5 Primvar inheritance down the hierarchy · 14.6 displayColor, displayOpacity, st

**Ch 15 — Inspecting Properties and Custom Metadata** (4 pp) — [Obj 5.3, 5.4, 7.6]
15.1 `GetProperties`, `GetAttributes`, `GetRelationships`, `GetPropertyNames` · 15.2 `GetNamespace` and namespaced queries · 15.3 `HasAuthoredValue`, `HasValue`, `GetResolveInfo` (preview) · 15.4 customData, assetInfo, and registered custom metadata

**Ch 16 — Geometry Data Integrity** (4 pp) — [Obj 5.5, 5.6, 6.4]
16.1 Keeping points/topology/extent in sync · 16.2 `UsdGeom.Boundable.ComputeExtentFromPlugins` · 16.3 Causes of unexpected visual results (orientation, normals, stale extent, purpose, visibility, wrong interpolation)

---

## Part III — Composition (23%) (Phase 4, ~62 pp)

**Ch 17 — Composition Fundamentals** (6 pp)
17.1 Opinion · 17.2 Composition arc · 17.3 Layer stack · 17.4 Strength · 17.5 List editing: prepend, append, delete, explicit · 17.6 Prim index (concept)

**Ch 18 — Sublayers and Layer Stacks** (6 pp) — Lab 13 — [Obj 1.1, 1.3, 1.5]
18.1 Sublayer order and strength · 18.2 Layer offsets on sublayers · 18.3 Session layer strength · 18.4 Edit targets and `Usd.EditContext` · 18.5 Muting layers · 18.6 Multi-user layering strategies (department layers)

**Ch 19 — References** (7 pp) — Lab 14 — [Obj 1.3, 1.4]
19.1 External references · 19.2 defaultPrim and references without prim paths · 19.3 Internal references · 19.4 Layer offsets: reusing one animation at different time offsets · 19.5 Reasons adding a reference may fail · 19.6 Encapsulation (what a reference does not bring)

**Ch 20 — Payloads** (5 pp) — Lab 15 — [Obj 1.3]
20.1 Payload vs reference · 20.2 Load/unload, `Usd.Stage.LoadAll` / `LoadNone` · 20.3 Load rules and working set management · 20.4 Payload placement in asset structure

**Ch 21 — Variants** (6 pp) — Lab 16 — [Obj 1.7]
21.1 Variant set and variant · 21.2 Variant selection · 21.3 Authoring variants with edit contexts · 21.4 Nested variants · 21.5 When variants are / are not appropriate · 21.6 Variant fallbacks (preview of Ch 48)

**Ch 22 — Inherits and Class Prims** (5 pp) — Lab 17
22.1 Inherits · 22.2 `class` specifier · 22.3 Broadcasting edits to many instances · 22.4 Inherits across references (implied inherits)

**Ch 23 — Specializes** (4 pp) — Lab 18
23.1 Specializes · 23.2 Specializes vs inherits · 23.3 Material library use case

**Ch 24 — Relocates** (4 pp) — Lab 19
24.1 Relocates · 24.2 Syntax and layer metadata · 24.3 Restrictions · 24.4 Version note

**Ch 25 — LIVERPS and Value Resolution** (8 pp) — Lab 20 — [Obj 1.1, 1.6, 1.8]
25.1 LIVERPS (LIVRPS) in simple terms · 25.2 Recursion: LIVERPS inside referenced layer stacks · 25.3 Attribute value resolution (value clips, time samples, default, fallback) · 25.4 Metadata and relationship resolution differences · 25.5 Changing the strength of an opinion · 25.6 Worked puzzles

**Ch 26 — Composition in Practice** (5 pp) — Lab 22 — [Obj 1.5, 1.9, 1.11]
26.1 Splitting a monolithic asset into workstreams · 26.2 Layering strategies for collaboration · 26.3 Preparing an internal asset for external delivery (preview of Ch 44)

**Ch 27 — Debugging Composition** (6 pp) — Lab 21 — [Obj 1.8, 6.2]
27.1 `Usd.Prim.GetPrimStack` · 27.2 `Usd.Property.GetPropertyStack` · 27.3 `Usd.Attribute.GetResolveInfo` · 27.4 `Usd.PrimCompositionQuery` · 27.5 Prim index dumps · 27.6 usdview Composition and Layer Stack tabs · 27.7 Pcp composition errors

---

## Part IV — Content Aggregation (10%) (Phase 5, ~26 pp)

**Ch 28 — Asset Structure Principles** (6 pp) — Lab 22 — [Obj 7.2]
28.1 Asset interface and entry-point layer · 28.2 Parallel layer organization (geo, mtl, look) · 28.3 Payload-wrapped components · 28.4 Workstream layers · 28.5 Documenting asset structure guidelines

**Ch 29 — Model Hierarchy and Kinds** (5 pp) — Lab 23
29.1 Model hierarchy rules · 29.2 `Usd.ModelAPI`, `IsModel`, `IsGroup`, `IsComponent` · 29.3 Kind registry · 29.4 Traversal pruning with kinds

**Ch 30 — Native Scenegraph Instancing** (6 pp) — Lab 24 — [Obj 1.10, 2.2, 2.4, 2.5]
30.1 Instanceable and instancing keys · 30.2 Prototypes · 30.3 Instance proxies · 30.4 What can and cannot be edited · 30.5 Changing an instance's color without breaking instancing · 30.6 Removing properties from instanced components (deactivation, variants, de-instancing trade-offs)

**Ch 31 — Point Instancing** (5 pp) — Lab 25 — [Obj 2.1, 2.3]
31.1 `UsdGeom.PointInstancer` · 31.2 prototypes, protoIndices, positions, orientations, scales, ids · 31.3 Adding a prototype · 31.4 Hiding instances efficiently (`invisibleIds`, `InvisIds`/`VisIds`; deactivation vs invisibility) · 31.5 Masks and computing instance transforms

**Ch 32 — Instancing Strategy and Large Scenes** (4 pp) — Lab 26 — [Obj 1.2, 2.4]
32.1 Choosing native vs point vs no instancing by scale · 32.2 Payloads, population masks, draw modes, extentsHint

---

## Part V — Data Exchange (15%) (Phase 6, ~34 pp)

**Ch 33 — Data Exchange Fundamentals** (5 pp) — [Obj 4.2]
33.1 Extract, transform, load · 33.2 Fidelity and lossy conversion · 33.3 Conceptual data mapping documents · 33.4 Example mapping: MaterialX ↔ UsdShade

**Ch 34 — Writing a Converter / Exporter to USD** (6 pp) — Lab 27 — [Obj 4.7]
34.1 Converter architecture · 34.2 Mapping source data to prims and schemas · 34.3 Fast authoring with Sdf and change blocks · 34.4 Stage metadata on export

**Ch 35 — Units, Up Axis, and Coordinate Systems** (4 pp) — Lab 28
35.1 metersPerUnit and `UsdGeom.LinearUnits` · 35.2 upAxis · 35.3 No automatic unit conversion across references · 35.4 kilogramsPerUnit (UsdPhysics overview) · 35.5 Handedness and orientation

**Ch 36 — Naming, Materials, and Animation in Interchange** (5 pp) — Lab 29
36.1 Valid identifiers, `Tf.MakeValidIdentifier`, UTF-8 names (version note) · 36.2 Material interchange via UsdPreviewSurface · 36.3 Animation: time samples, UsdSkel overview, velocities

**Ch 37 — Importers, Round-Trips, and DCC Integration** (5 pp) — [Obj 3.6, 4.4, 4.5, 4.8, 7.4, 7.8]
37.1 Importer design · 37.2 Round-trip pipelines and stable identity · 37.3 Preserving nonstandard data (custom attributes, API schemas) · 37.4 Extending an existing importer

**Ch 38 — Exporting USD to Other Formats** (4 pp) — [Obj 4.1, 7.1]
38.1 USD → glTF mapping concepts · 38.2 Fidelity checks · 38.3 USDZ for AR delivery

**Ch 39 — Validation** (5 pp) — Lab 30 — [Obj 4.6]
39.1 usdchecker · 39.2 The `UsdValidation` framework (registry, validators, contexts, fixers) · 39.3 Legacy `UsdUtils.ComplianceChecker` (removed in 26.08; version note) · 39.4 Writing a custom validator for DCC exports

---

## Part VI — Pipeline Development (14%) (Phase 7, ~30 pp)

**Ch 40 — Pipeline Architecture** (5 pp) — [Obj 7.2]
40.1 Pipeline stages: author, publish, assemble, render · 40.2 Diagramming and documenting pipelines · 40.3 UI/UX for artists

**Ch 41 — Asset Resolution (Ar)** (6 pp) — [Obj 3.5, 6.3, 7.5, 7.7]
41.1 Asset paths and `@...@` syntax · 41.2 Anchored relative paths · 41.3 `Ar.GetResolver`, default resolver search paths · 41.4 Resolver contexts and `Usd.Stage.Open` · 41.5 Custom resolvers (concept) · 41.6 Validating asset paths

**Ch 42 — Asset Management, Versioning, Publishing** (5 pp) — Lab 31 — [Obj 7.7]
42.1 Naming conventions · 42.2 Directory structures · 42.3 Versioning and publishing · 42.4 Dependency analysis (`UsdUtils.ComputeAllDependencies`) · 42.5 Version control with USDA

**Ch 43 — Exporter Hooks and Pipeline Transformations** (5 pp) — Lab 33
43.1 Post-export hooks · 43.2 Restructuring data to pipeline conventions · 43.3 `Usd.Notice` and change processing · 43.4 Batching with `Sdf.ChangeBlock`

**Ch 44 — Flattening, Packaging, Delivery** (5 pp) — Lab 32 — [Obj 1.9]
44.1 `Usd.Stage.Flatten` vs `Sdf.Layer` flattening vs `UsdUtils.FlattenLayerStack` · 44.2 Removing proprietary dependencies · 44.3 Localizing and packaging (usdzip, `UsdUtils` packaging) · 44.4 Delivery checklist

**Ch 45 — Build Configurations and Collaboration** (4 pp) — [Obj 3.2]
45.1 Building USD from source (`build_usd.py`, options, dependencies) · 45.2 Matching versions across DCCs and plugins · 45.3 Environment variables (`PXR_PLUGINPATH_NAME`, `TF_DEBUG`) · 45.4 Collaboration practices

---

## Part VII — Customizing USD (6%) (Phase 8, ~14 pp)

**Ch 46 — The Plugin System** (4 pp) — [Obj 3.1]
46.1 `Plug.Registry` · 46.2 `plugInfo.json` · 46.3 Plugin discovery paths · 46.4 Building a plugin against a specific USD version

**Ch 47 — Custom Schemas** (5 pp) — Lab 34 — [Obj 3.4, 3.6]
47.1 `schema.usda` · 47.2 `usdGenSchema` · 47.3 Codeless schemas · 47.4 Typed (UsdTyped) vs API (UsdAPISchemaBase) base classes

**Ch 48 — Kinds, Variant Fallbacks, File Formats, Resolvers, Scene Index** (5 pp) — Lab 35 — [Obj 3.3, 3.5, 3.7, 3.8]
48.1 Custom model kinds via plugInfo · 48.2 Variant fallback selections (`Usd.Stage.SetGlobalVariantFallbacks`, plugInfo) · 48.3 File format plugins (`SdfFileFormat`) · 48.4 Custom asset resolvers, including in-memory generated content · 48.5 SceneIndex plugins (concept)

---

## Part VIII — Visualization (8%) (Phase 9, ~28 pp)

**Ch 49 — UsdGeom: Xformables and Transforms** (5 pp) — Lab 36
49.1 xformOps and xformOpOrder · 49.2 `UsdGeom.XformCommonAPI` · 49.3 resetXformStack · 49.4 `UsdGeom.XformCache`, `ComputeLocalToWorldTransform`

**Ch 50 — Gprims, Meshes, and Points** (6 pp) — Lab 37 — [Obj 8.1]
50.1 Gprim and Imageable (visibility, purpose) · 50.2 Mesh topology: points, faceVertexCounts, faceVertexIndices · 50.3 Normals and orientation · 50.4 Subdivision scheme · 50.5 `UsdGeom.Subset` · 50.6 Points and curves overview · 50.7 Extent and bounding boxes (`UsdGeom.BBoxCache`)

**Ch 51 — Cameras** (3 pp) — Lab 38
51.1 `UsdGeom.Camera` attributes · 51.2 `Gf.Camera` conversion

**Ch 52 — UsdShade: Materials and Shaders** (7 pp) — Lab 39 — [Obj 8.2, 8.3, 8.4]
52.1 Material, Shader, NodeGraph · 52.2 Inputs, outputs, connections · 52.3 UsdPreviewSurface · 52.4 Reading displayColor through UsdPrimvarReader · 52.5 Textures with UsdUVTexture and st · 52.6 `MaterialBindingAPI`, binding strength, collection-based binding · 52.7 Exposing material parameters for overrides

**Ch 53 — UsdLux: Lights** (4 pp) — Lab 40
53.1 LightAPI and `inputs:` attributes (version note) · 53.2 DistantLight, DomeLight, SphereLight, RectLight, DiskLight, CylinderLight · 53.3 ShadowAPI and ShapingAPI · 53.4 Light linking via collections

**Ch 54 — Hydra and Rendering Overview** (3 pp) — [Obj 3.7]
54.1 Hydra architecture · 54.2 Render delegates · 54.3 Scene index chain (concept)

---

## Part IX — Debugging and Performance (11%) (Phase 10, ~22 pp)

**Ch 55 — Stage and Layer Introspection** (5 pp) — Lab 41
55.1 `Usd.PrimRange`, predicates, `Usd.TraverseInstanceProxies` · 55.2 `GetUsedLayers`, `GetLayerStack` · 55.3 `ExportToString` · 55.4 usdcat, usdtree, usddiff for inspection

**Ch 56 — Troubleshooting Playbook** (6 pp) — Lab 42 — [Obj 6.2, 6.3, 6.4]
56.1 Missing prims · 56.2 Wrong opinions winning · 56.3 Broken references and payloads · 56.4 Variant selection problems · 56.5 Asset path problems · 56.6 Unexpected visual results

**Ch 57 — Diagnostics and Profiling** (5 pp) — [Obj 6.5]
57.1 TfDebug and `TF_DEBUG` · 57.2 Diagnostic delegates (`UsdUtils.CoalescingDiagnosticDelegate`) · 57.3 Trace (`Trace.Collector`, reports) · 57.4 TfMallocTag · 57.5 Interpreting Pcp errors

**Ch 58 — Performance** (6 pp) — Lab 43 — [Obj 6.1]
58.1 Load times: formats, payloads, population masks · 58.2 Authoring performance: change blocks, Sdf · 58.3 Render times: instancing, purpose, draw modes · 58.4 Maximizing USD Performance checklist

---

## Part X — Python Labs (Phase 11, ~50 pp)

43 progressive labs. Each lab: Goal · Objectives covered · Prerequisites · Steps · Full script (`python-labs/labNN_*.py`) · Expected output · Check-your-understanding · Extension challenge.

| Lab | Title | Chapter |
|-----|-------|---------|
| 01 | Hello Stage: create, define, save | 2–3 |
| 02 | Reading layers: ExportToString and USDA | 3 |
| 03 | Prim paths and traversal | 4 |
| 04 | Attributes: create, set, get, fallback vs authored | 5 |
| 05 | Relationships and targets | 5 |
| 06 | Metadata: kind, customData, documentation, assetInfo | 6 |
| 07 | Schemas: typed vs API, ApplyAPI, HasAPI, IsA | 7 |
| 08 | File formats: usda/usdc/usdz conversion | 9 |
| 09 | Sdf authoring and change blocks | 10 |
| 10 | Value types: Gf, Vt, tokens, matrices | 11 |
| 11 | Time samples and interpolation | 12 |
| 12 | Primvars and interpolation modes | 14 |
| 13 | Sublayers and edit targets | 18 |
| 14 | References and time-offset animation | 19 |
| 15 | Payloads and load control | 20 |
| 16 | Variant sets | 21 |
| 17 | Inherits and class prims | 22 |
| 18 | Specializes vs inherits | 23 |
| 19 | Relocates (version-gated) | 24 |
| 20 | LIVERPS puzzle: predict and verify | 25 |
| 21 | Composition debugging toolkit | 27 |
| 22 | Building a component asset interface | 26, 28 |
| 23 | Model hierarchy and kind validation | 29 |
| 24 | Native instancing and instance proxies | 30 |
| 25 | PointInstancer: prototypes and hiding | 31 |
| 26 | Population masks and load rules | 32 |
| 27 | Converter: JSON/OBJ subset → USD | 34 |
| 28 | Units and up-axis correction | 35 |
| 29 | Name sanitization | 36 |
| 30 | Custom validator for exported assets | 39 |
| 31 | Dependency analysis | 42 |
| 32 | Flatten and package for delivery | 44 |
| 33 | Exporter hook: restructure to pipeline conventions | 43 |
| 34 | Codeless custom schema | 47 |
| 35 | Custom kinds and variant fallbacks | 48 |
| 36 | Xforms and world transforms | 49 |
| 37 | Mesh from scratch: topology, normals, extent | 50 |
| 38 | Camera setup | 51 |
| 39 | UsdPreviewSurface with primvar-driven color | 52 |
| 40 | Lights | 53 |
| 41 | Stage introspection script | 55 |
| 42 | Debug a broken scene | 56 |
| 43 | Performance measurement | 58 |

---

## Part XI — USDA Reading Workshop (Phase 12, ~12 pp)

25 exercises: read a USDA snippet (often multi-file), predict composed results, then check the answer. Groups: syntax basics (5), properties and types (4), composition and LIVERPS (8), instancing (3), shading and geometry (3), broken files to diagnose (2).

## Part XII — Question Bank (Phase 12, ~40 pp)

| Section | Questions |
|---------|-----------|
| Fundamentals | 20 |
| Composition | 55 |
| Data Exchange | 36 |
| Pipeline Development | 34 |
| Data Modeling | 32 |
| Debugging and Troubleshooting | 26 |
| Content Aggregation | 24 |
| Visualization | 20 |
| Customizing USD | 14 |
| **Total** | **261** |

## Part XIII — Mock Exams (Phase 13, ~45 pp)

Mock Exam 1 (65 Q, medium) · Mock Exam 2 (65 Q, medium-hard) · Mock Exam 3 (65 Q, hard) · Answer keys with explanations and per-domain score tables · How to analyze your results.

## Part XIV — Final Revision (Phase 14, ~30 pp)

Cheat sheets (10, one page each) · Flashcards (≥ 150) · Final certification checklist (one item per objective) · Last-48-hours plan · Exam-day checklist.

---

## Appendices (~25 pp)

A. Glossary · B. Python API quick reference (Usd, Sdf, UsdGeom, UsdShade, UsdLux, Gf, Vt, Tf, Ar, UsdUtils, Plug) · C. USDA syntax reference · D. Objective-to-chapter traceability matrix · E. References (bibliography) · F. Version notes and tested environment
