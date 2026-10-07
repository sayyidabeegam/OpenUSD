# NCP-OUSD Study Book — Complete Table of Contents

**Title:** *OpenUSD Development from Zero: A 14-Day Study Book for the NVIDIA-Certified Professional: OpenUSD Development (NCP-OUSD) Exam*

This is the authoritative structure. Chapter files follow `chapters/chNN_slug.md`.
"Obj" numbers refer to the official NVIDIA study guide objectives (v1.1.0, Oct 2025), e.g. Obj 1.3 = Composition objective 3.
Page estimates are targets for A4 at ~11 pt; quality takes priority over page count.

---

## Front Matter (~14 pp)

| § | Title | File | Pages |
|---|-------|------|-------|
| F1 | Title page and disclaimer ("Not affiliated with NVIDIA; practice questions are original") | `chapters/f1_title.md` | 2 |
| F2 | How to use this book (teaching order, callouts, symbols) | `chapters/f2_how_to_use.md` | 2 |
| F3 | The NCP-OUSD exam: format, blueprint, objectives list, exam-day strategy | `chapters/f3_exam_overview.md` | 4 |
| F4 | The 14-day study plan (printable tracker) | `chapters/f4_study_plan.md` | 3 |
| F5 | Setting up your lab: Python, `usd-core`, running scripts, command-line tools, usdview options | `chapters/f5_setup.md` | 3 |

---

## Part I — OpenUSD Fundamentals (Phase 2, ~48 pp)

| Ch | Title | Sections | Obj | Pages |
|----|-------|----------|-----|-------|
| 1 | What Is OpenUSD? | 1.1 Scene description vs. file format · 1.2 History: Pixar, open source, AOUSD · 1.3 Where USD is used (film, games, digital twins, AEC, robotics) · 1.4 The USD software stack: Tf, Gf, Vt, Ar, Sdf, Pcp, Usd, schema domains, Hydra · 1.5 The `pxr` Python package | — | 6 |
| 2 | The Stage | 2.1 What a stage is · 2.2 Creating, opening, saving (`CreateNew`, `Open`, `CreateInMemory`, `Save`, `Export`) · 2.3 Stage traversal (`Traverse`, `GetPrimAtPath`) · 2.4 Stage metadata (`defaultPrim`, `upAxis`, `metersPerUnit`, time codes) | 2.x, 5.4 | 7 |
| 3 | Layers | 3.1 What a layer is (`Sdf.Layer`) · 3.2 Root layer · 3.3 Session layer · 3.4 Sublayers and the layer stack · 3.5 Anonymous layers · 3.6 Opinions and "strongest wins" (first look) | 1.3, 1.5 | 8 |
| 4 | Prims and Prim Paths | 4.1 Prims · 4.2 Prim paths (`Sdf.Path`) · 4.3 Specifiers: `def`, `over`, `class` · 4.4 Typed vs. typeless prims · 4.5 Active/inactive prims · 4.6 Namespace hierarchy | 5.4 | 7 |
| 5 | Properties: Attributes, Relationships, Metadata | 5.1 Properties · 5.2 Attributes (default value, type, variability) · 5.3 Relationships and targets · 5.4 Metadata (prim, property, layer) · 5.5 Property namespaces (`primvars:`, `xformOp:`, `inputs:`) | 5.3, 5.4 | 8 |
| 6 | Schemas and Model Kinds | 6.1 What a schema is · 6.2 Typed (IsA) schemas · 6.3 API schemas: single-apply vs. multiple-apply · 6.4 Built-in schema domains (UsdGeom, UsdShade, UsdLux, UsdPhysics, UsdSkel) · 6.5 Model kinds: model, group, assembly, component, subcomponent | 3.3, 3.4 | 7 |
| 7 | USD File Formats and Reading USDA | 7.1 `.usda` (text) · 7.2 `.usdc` (Crate binary) · 7.3 `.usd` (either) · 7.4 `.usdz` (package) · 7.5 Reading USDA syntax line by line · 7.6 Converting formats (`usdcat`, `Sdf.Layer.Export`) | 4.3, 7.3 | 5 |

## Part II — Data Modeling (13%) (Phase 3, ~40 pp)

| Ch | Title | Sections | Obj | Pages |
|----|-------|----------|-----|-------|
| 8 | Usd vs. Sdf: Two Ways to See Data | 8.1 Composed view (`Usd`) vs. authored view (`Sdf`) · 8.2 Specs: `PrimSpec`, `AttributeSpec`, `RelationshipSpec` · 8.3 `Sdf.Path` operations · 8.4 Authoring with Sdf for speed · 8.5 `Sdf.ChangeBlock` (intro) | 5.4, 6.1 | 7 |
| 9 | Value Types | 9.1 `Sdf.ValueTypeNames` · 9.2 Scalars (bool, int, float, double, half, string) · 9.3 Tokens vs. strings · 9.4 Vectors and roles (`point3f`, `normal3f`, `color3f`, `texCoord2f`) · 9.5 Matrices (`matrix4d`) and quaternions · 9.6 Arrays and `Vt` · 9.7 `Gf` math types · 9.8 Asset paths (`asset`, `Sdf.AssetPath`) · 9.9 Choosing the right type | 5.2 | 8 |
| 10 | Time Samples and Animation Data | 10.1 Default value vs. time samples · 10.2 `Usd.TimeCode` and `Default()` · 10.3 `timeCodesPerSecond`, `framesPerSecond`, start/end · 10.4 Interpolation (held, linear; `SetInterpolationType`) · 10.5 Layer offsets (intro) · 10.6 Value clips (overview) · 10.7 Splines (version note) | 1.4, 5.2 | 7 |
| 11 | Primvars | 11.1 What a primvar is · 11.2 `UsdGeom.PrimvarsAPI` · 11.3 Interpolation: constant, uniform, varying, vertex, faceVarying · 11.4 Indexed primvars · 11.5 `elementSize` · 11.6 Primvar inheritance down namespace · 11.7 `displayColor` / `displayOpacity` | 5.1, 8.1 | 7 |
| 12 | Metadata in Depth | 12.1 Registered vs. custom metadata · 12.2 `customData` and `assetInfo` · 12.3 `documentation`, `hidden`, `kind` · 12.4 Layer metadata · 12.5 Representing pipeline metadata | 5.3, 7.6 | 5 |
| 13 | Built-in Schemas, Xforms, and Extents | 13.1 `UsdGeom.Imageable`, `Xformable`, `Boundable`, `Gprim` · 13.2 `extent` and why it matters · 13.3 `ComputeExtent` / `ComputeExtentFromPlugins` · 13.4 `UsdGeom.BBoxCache` · 13.5 What causes unexpected visual results | 5.5, 5.6, 6.4 | 6 |

## Part III — Composition (23%) (Phase 4, ~80 pp)

| Ch | Title | Sections | Obj | Pages |
|----|-------|----------|-----|-------|
| 14 | Composition Fundamentals | 14.1 What composition is · 14.2 Opinions and strength · 14.3 The seven arcs at a glance · 14.4 List editing: `prepend`, `append`, `delete`, explicit · 14.5 Layer stacks and the prim index · 14.6 Composition is not merging | 1.1, 1.6 | 8 |
| 15 | Sublayers, Layer Stacks, and Edit Targets | 15.1 Sublayer ordering · 15.2 Layer offsets on sublayers · 15.3 Edit targets (`Usd.EditTarget`, `SetEditTarget`) · 15.4 Layer muting (`MuteLayer`) · 15.5 Multi-user layering strategies | 1.3, 1.5 | 8 |
| 16 | References | 16.1 External references · 16.2 `defaultPrim` and references without prim paths · 16.3 Internal references · 16.4 Reference layer offsets: reusing animation at different times · 16.5 Why adding a reference may fail · 16.6 References vs. sublayers | 1.3, 1.4 | 9 |
| 17 | Payloads | 17.1 What a payload is · 17.2 Loading and unloading (`Load`, `Unload`, `InitialLoadSet`) · 17.3 `Usd.StageLoadRules` · 17.4 Population masks (`OpenMasked`) · 17.5 Payloads vs. references: strength and use cases | 1.3 | 7 |
| 18 | Variant Sets | 18.1 Variant sets and variants · 18.2 Selections and authoring inside variants · 18.3 Nested variants · 18.4 Fallback selections · 18.5 When variants are / are not appropriate · 18.6 Variant selection strength surprises | 1.7 | 9 |
| 19 | Inherits, Classes, and Specializes | 19.1 `class` prims · 19.2 Inherits and broadcast edits · 19.3 Specializes as weakest fallback · 19.4 Inherits vs. specializes: decision table · 19.5 Implied inherits across references | 1.1, 1.6 | 8 |
| 20 | Overs and Relocates | 20.1 `over` vs. typeless `def` · 20.2 Overriding referenced content · 20.3 Relocates: what and why · 20.4 Relocates authoring and limitations (version note) | 1.8, 6.2 | 5 |
| 21 | LIVERPS and Value Resolution | 21.1 LIVERPS spelled out (Local, Inherits, Variants, rElocates, References, Payloads, Specializes) · 21.2 Strength within a layer stack vs. across arcs · 21.3 Value resolution: defaults, time samples, fallbacks · 21.4 Layer offsets in resolution · 21.5 Value clips in resolution · 21.6 Ten worked LIVERPS puzzles | 1.1, 1.6, 1.8 | 12 |
| 22 | Composition Design and Debugging | 22.1 Splitting a monolithic asset into workstreams · 22.2 Multi-user scene layering · 22.3 Preparing an asset for external delivery (flatten, localize, package) · 22.4 Removing properties from instanced component prims · 22.5 Debugging composition: `GetPrimStack`, `GetPropertyStack`, `Usd.PrimCompositionQuery`, prim index dumps · 22.6 Why an opinion does not take effect: checklist | 1.2, 1.5, 1.8–1.11 | 14 |

## Part IV — Content Aggregation (10%) (Phase 5, ~30 pp)

| Ch | Title | Sections | Obj | Pages |
|----|-------|----------|-----|-------|
| 23 | Asset Structure and Model Hierarchy | 23.1 Principles of scalable asset structure · 23.2 Asset interfaces (entry layer, geo/mtl/payload layers) · 23.3 Model hierarchy and kinds in practice · 23.4 Modular, reusable components · 23.5 ASWF asset structure guidelines | 2.4, 7.2 | 8 |
| 24 | Native Scenegraph Instancing | 24.1 `instanceable` · 24.2 Prototypes (`GetPrototype`) · 24.3 Instance proxies · 24.4 Editing an instance proxy's look without breaking instancing · 24.5 Overriding instances: inherits, variants, primvars on instance roots · 24.6 Removing properties from instanced components | 1.10, 2.2, 2.4, 2.5 | 9 |
| 25 | Point Instancing | 25.1 `UsdGeom.PointInstancer` · 25.2 `prototypes`, `protoIndices`, `positions`, `orientations`, `scales` · 25.3 Adding a prototype · 25.4 Hiding instances efficiently (`invisibleIds`, `MakeInvisible`, `DeactivateId`) · 25.5 `ids` and stable identity | 2.1, 2.3 | 7 |
| 26 | Large Scene Optimization | 26.1 Choosing an instancing style at different scales · 26.2 Payloads for scalability · 26.3 Draw modes (`UsdGeom.ModelAPI`) and extents hints · 26.4 LOD with variants · 26.5 Aggregation decision table | 1.2, 2.4 | 6 |

## Part V — Data Exchange (15%) (Phase 6, ~36 pp)

| Ch | Title | Sections | Obj | Pages |
|----|-------|----------|-----|-------|
| 27 | Data Exchange Concepts | 27.1 Import, export, conversion · 27.2 Extraction → transformation → validation · 27.3 Conceptual data mapping documents (with template) · 27.4 Mapping USD to glTF and MaterialX · 27.5 Round-trip pipelines with a DCC | 4.1, 4.2, 4.4 | 8 |
| 28 | Units, Axes, and Naming | 28.1 `metersPerUnit` and `UsdGeom.LinearUnits` · 28.2 `upAxis` · 28.3 USD does not auto-convert units (why) · 28.4 Valid prim names (`Tf.MakeValidIdentifier`) · 28.5 Coordinate-system handedness | 4.7, 7.x | 6 |
| 29 | Writing Exporters, Converters, and Importers | 29.1 Exporter structure · 29.2 Converting a simple format (JSON/OBJ) to USD · 29.3 Materials and animation mapping · 29.4 Nonstandard data via custom attributes or schemas · 29.5 Importer design in a DCC · 29.6 Exporter hooks | 4.5, 4.7, 4.8 | 9 |
| 30 | Validating USD Assets | 30.1 Why validate · 30.2 `usdchecker` (built on UsdValidation since 26.03) · 30.3 The UsdValidation framework · 30.4 Legacy: `UsdUtils.ComplianceChecker` (removed in 26.08; may still appear in older material) · 30.5 Writing your own validator | 4.6 | 7 |
| 31 | File Formats in Depth | 31.1 USDA vs. USDC trade-offs (performance, readability, diff/merge, archival) · 31.2 USDZ packaging rules and `usdzip` · 31.3 Format detection for `.usd` · 31.4 Conversion tools (`usdcat`, `usdzip`) | 4.3, 7.3 | 6 |

## Part VI — Pipeline Development (14%) (Phase 7, ~34 pp)

| Ch | Title | Sections | Obj | Pages |
|----|-------|----------|-----|-------|
| 32 | Pipeline Architecture and Asset Management | 32.1 What a USD pipeline is · 32.2 Directory structures and naming conventions · 32.3 Versioning and publishing · 32.4 Dependencies (`UsdUtils.ComputeAllDependencies`) · 32.5 Diagramming and documenting asset structure · 32.6 Collaboration across departments | 7.2 | 9 |
| 33 | Asset Resolution | 33.1 Asset paths and `Ar` · 33.2 `Ar.GetResolver()`, resolve, anchoring · 33.3 Resolver contexts and search paths · 33.4 Validating asset paths · 33.5 Custom resolvers (overview) | 3.5, 6.3, 7.5, 7.7 | 8 |
| 34 | Exporter Hooks, Flattening, and Change Processing | 34.1 Exporter hooks to enforce pipeline structure · 34.2 `Usd.Stage.Flatten` vs. `UsdUtils.FlattenLayerStack` vs. `Sdf.Layer` export · 34.3 Removing proprietary dependencies · 34.4 Change notifications (`Tf.Notice`, `Usd.Notice`) · 34.5 `Sdf.ChangeBlock` for performance | 1.9, 6.1, 7.x | 9 |
| 35 | Build Configurations and DCC Integration | 35.1 Building USD (`build_usd.py`, CMake options) · 35.2 Matching plugin builds to USD versions · 35.3 DCC round-trips (importer/exporter integration) · 35.4 Physics and other domain schemas in pipelines | 3.1, 3.2, 7.4, 7.8 | 8 |

## Part VII — Customizing USD (6%) (Phase 8, ~20 pp)

| Ch | Title | Sections | Obj | Pages |
|----|-------|----------|-----|-------|
| 36 | The Plugin System | 36.1 Plugins and `plugInfo.json` · 36.2 `Plug.Registry` and `PXR_PLUGINPATH_NAME` · 36.3 Plugin types (schemas, file formats, resolvers, Hydra) | 3.1 | 5 |
| 37 | Custom Schemas | 37.1 When to create a schema · 37.2 `schema.usda` · 37.3 `usdGenSchema`; codeful vs. codeless schemas · 37.4 IsA (`UsdTyped`) vs. API (`UsdAPISchemaBase`) base classes · 37.5 Schemas for nonstandard import/export data | 3.4, 3.6, 4.5 | 8 |
| 38 | Kinds, Variant Fallbacks, File Formats, Resolvers, Scene Indices | 38.1 Custom model kinds (`Kind.Registry`) · 38.2 Variant fallback selections (plugInfo, `SetGlobalVariantFallbacks`) · 38.3 File format plugins (`SdfFileFormat`) · 38.4 Custom asset resolvers (`ArResolver`) · 38.5 Hydra scene index plugins (concepts) | 3.3, 3.5, 3.7, 3.8 | 7 |

## Part VIII — Visualization (8%) (Phase 9, ~28 pp)

| Ch | Title | Sections | Obj | Pages |
|----|-------|----------|-----|-------|
| 39 | UsdGeom: Geometry, Transforms, Cameras | 39.1 `Xform` and xformOps, `xformOpOrder` · 39.2 `XformCache`, local vs. world transforms · 39.3 Meshes: `points`, `faceVertexCounts`, `faceVertexIndices`, orientation, subdivision · 39.4 Normals · 39.5 `GeomSubset` · 39.6 Visibility and purpose · 39.7 Cameras | 5.1, 8.1 | 11 |
| 40 | UsdShade: Materials and Shaders | 40.1 `Material`, `Shader`, `NodeGraph` · 40.2 Inputs, outputs, connections · 40.3 `UsdPreviewSurface` · 40.4 Textures: `UsdUVTexture`, `UsdPrimvarReader_float2` · 40.5 Reading diffuse color from a primvar · 40.6 Material binding (`MaterialBindingAPI`, strength, purpose, collections) · 40.7 Exposing material parameters for overrides | 8.2, 8.3, 8.4 | 11 |
| 41 | UsdLux and Rendering | 41.1 Light types (Distant, Sphere, Rect, Disk, Cylinder, Dome) · 41.2 `LightAPI`, `ShadowAPI`, `ShapingAPI` · 41.3 Intensity, exposure, color temperature · 41.4 Hydra, render delegates, usdview (concepts) | 8.x | 6 |

## Part IX — Debugging and Performance (11%) (Phase 10, ~28 pp)

| Ch | Title | Sections | Obj | Pages |
|----|-------|----------|-----|-------|
| 42 | Stage Introspection and Composition Debugging | 42.1 Inspecting layers and layer stacks · 42.2 Missing prims · 42.3 Wrong opinions winning · 42.4 Broken references, payloads, variants · 42.5 Asset-path problems · 42.6 Unexpected visual results · 42.7 A systematic debugging procedure | 6.2, 6.3, 6.4 | 11 |
| 43 | Diagnostics and Profiling Tools | 43.1 Tf errors, warnings, status · 43.2 `TfDebug` and `TF_DEBUG` · 43.3 Diagnostic delegates (`UsdUtils.CoalescingDiagnosticDelegate`) · 43.4 `Trace` collector and reports · 43.5 `TfMallocTag` · 43.6 Pcp composition errors | 6.5 | 8 |
| 44 | Performance: Load and Render Times | 44.1 What makes stages slow · 44.2 USDC, payloads, masks, load rules · 44.3 Instancing for memory and speed · 44.4 `Sdf.ChangeBlock` and batched edits · 44.5 Render-time factors (extent, purpose, draw modes) · 44.6 Maximizing USD performance checklist | 6.1, 6.4 | 9 |

## Part X — Practice and Revision (Phases 11–14, ~110 pp)

| § | Title | File(s) | Pages |
|---|-------|---------|-------|
| X1 | Python Labs 1–37 | `python-labs/labNN_*.md` | 45 |
| X2 | USDA Reading Workbook (30 exercises) | `questions/usda_exercises.md` | 12 |
| X3 | Topic-wise Question Bank (~430 incl. fundamentals) | `questions/qbank_*.md` | 30 |
| X4 | Mock Exams 1–3 (65 Q each) + answer keys + score sheets | `mock-exams/mock0N_*.md` | 24 |
| X5 | Flashcards (≥ 160) | `questions/flashcards.md` | 8 |
| X6 | Cheat Sheets | `cheat-sheets/cs_*.md` | 10 |
| X7 | Final Certification Checklist | `cheat-sheets/final_checklist.md` | 2 |

### Python labs (progressive ★☆☆ → ★★★)

| Lab | Title | Ch | Obj |
|-----|-------|----|-----|
| 01 | Install and verify `usd-core` | F5 | — |
| 02 | Your first stage: Xform + Sphere, save as USDA | 2 | — |
| 03 | Open and traverse a stage | 2 | 5.4 |
| 04 | Root layer, session layer, export to string | 3 | 1.3 |
| 05 | Build a sublayer stack and see who wins | 3, 15 | 1.1 |
| 06 | Attributes and value types | 5, 9 | 5.2 |
| 07 | Relationships and targets | 5 | 5.4 |
| 08 | Metadata, customData, assetInfo, stage metadata | 12 | 5.3, 7.6 |
| 09 | Authoring with Sdf specs + `Sdf.ChangeBlock` | 8 | 6.1 |
| 10 | Time samples, interpolation, time codes | 10 | 5.2 |
| 11 | Build a mesh from scratch and compute its extent | 13, 39 | 5.6 |
| 12 | Primvars: interpolation and indexed primvars | 11 | 5.1, 8.1 |
| 13 | External and internal references, `defaultPrim` | 16 | 1.3 |
| 14 | Same animation at different time offsets | 16 | 1.4 |
| 15 | Payloads, load rules, population masks | 17 | 1.3 |
| 16 | Variant sets: create, author, select, nest | 18 | 1.7 |
| 17 | Classes and inherits: broadcast edits | 19 | 1.1 |
| 18 | Specializes vs. inherits side by side | 19 | 1.6 |
| 19 | Edit targets: author into layers and variants | 15 | 1.1, 1.5 |
| 20 | LIVERPS laboratory: predict, then verify | 21 | 1.6, 1.8 |
| 21 | Composition introspection toolkit | 22, 42 | 1.8, 6.2 |
| 22 | Build a component asset and an assembly | 23 | 2.4, 7.2 |
| 23 | Native instancing and instance proxies | 24 | 2.2, 2.5 |
| 24 | PointInstancer: add prototypes, hide instances | 25 | 2.1, 2.3 |
| 25 | Write a JSON/OBJ → USD converter | 29 | 4.7 |
| 26 | Units and up-axis handling | 28 | 4.7 |
| 27 | Write an asset validator | 30 | 4.6 |
| 28 | Dependencies, flattening, and USDZ packaging | 31, 34 | 1.9 |
| 29 | Asset resolution and asset-path validation | 33 | 7.7 |
| 30 | Change notices and change-block performance | 34 | 6.1 |
| 31 | A codeless custom schema (structure + plugInfo) | 37 | 3.4 |
| 32 | Custom kinds and variant fallbacks | 38 | 3.3 |
| 33 | Xforms, XformCache, and cameras | 39 | 8.x |
| 34 | UsdPreviewSurface + primvar-driven color + binding | 40 | 8.2–8.4 |
| 35 | Lights with UsdLux | 41 | 8.x |
| 36 | Debugging toolkit: diagnostics delegate, TfDebug, Trace | 43 | 6.5 |
| 37 | Capstone: a small multi-asset pipeline end to end | all | many |

### Cheat sheets

`cs_liverps.md` · `cs_usda_syntax.md` · `cs_python_api.md` · `cs_list_editing.md` · `cs_primvars.md` · `cs_instancing.md` · `cs_debugging.md` · `cs_file_formats_tools.md` · `cs_schemas_kinds.md` · `cs_exam_domains.md`

## Back Matter (~12 pp)

| § | Title | File | Pages |
|---|-------|------|-------|
| B1 | Glossary (~150 terms) | `chapters/b1_glossary.md` | 7 |
| B2 | References and further reading | `references/references.md` | 3 |
| B3 | Objective coverage matrix (Obj → chapter/lab/questions) | `chapters/b3_coverage.md` | 2 |

---

**Page budget:** the per-section estimates above add up to about 480 pages, which is a deliberate upper bound. The printed target is **320–400 pages**. If a build goes over 400 pages, first shrink the labs (X1: print the key steps and full output, and move long scripts to a compact appendix), then the question-bank layout (X3), then Part I. Never cut composition content (Part III).
