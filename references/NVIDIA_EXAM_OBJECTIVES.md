# NCP-OUSD Official Exam Objectives

Source: *NVIDIA-Certified Professional: OpenUSD Development Exam Study Guide*, version 1.1.0 (© 2025 NVIDIA, doc 4379350, Oct 2025). Retrieved 2026-10-07. Objectives listed as published (numbering is NVIDIA's). Domain weights cross-checked against the certification page on 2026-10-07: **match**.

The "Chapters" column is this book's mapping (see `01_TABLE_OF_CONTENTS.md`). Some objectives appear in two domains in the official guide; both are kept.

## 1. Composition — 23%

| Obj | Objective | Chapters |
|-----|-----------|----------|
| 1.1 | Change the strength of an opinion | 14, 19, 21 |
| 1.2 | Choose an appropriate instancing style for data at different scales | 22, 26 |
| 1.3 | Compare referencing, payloads, and sublayers, and identify their use cases | 3, 15, 16, 17 |
| 1.4 | Create a scene with multiple elements referencing the same animation at different time offsets | 10, 16 |
| 1.5 | Design scene layering strategies to facilitate multi-user workflows | 15, 22 |
| 1.6 | Explain LIVERPS in simple terms | 14, 21 |
| 1.7 | Identify situations where variants are/are not appropriate for structuring assets | 18 |
| 1.8 | Identify why opinions from one layer do not take effect in a composed stage | 20, 21, 22 |
| 1.9 | Prepare an internal asset to be delivered to external parties | 22, 34 |
| 1.10 | Remove properties from instanced component prims in an assembly stage | 22, 24 |
| 1.11 | Split a monolithic asset to model multiple collaborative workstreams | 22 |

## 2. Content Aggregation — 10%

| Obj | Objective | Chapters |
|-----|-----------|----------|
| 2.1 | Add a new prototype to a PointInstancer | 25 |
| 2.2 | Edit the color of an instance proxy mesh without changing its instancing status | 24 |
| 2.3 | Hide instances of a PointInstancer efficiently | 25 |
| 2.4 | Implement and manage USD instances for efficient asset reuse in large scenes | 23, 24, 26 |
| 2.5 | Remove properties from instanced component prims in an assembly stage | 24 |

## 3. Customizing USD — 6%

| Obj | Objective | Chapters |
|-----|-----------|----------|
| 3.1 | Build a USD plug-in against a given version of USD | 35, 36 |
| 3.2 | Build USD from scratch with custom dependencies | 35 |
| 3.3 | Create custom model kinds when appropriate | 6, 38 |
| 3.4 | Create custom schemas for proprietary data models | 6, 37 |
| 3.5 | Integrate a custom resolver to manage asset paths dynamically | 33, 38 |
| 3.6 | Use USD schemas to support nonstandard attributes/structures during import/export | 37 |
| 3.7 | Write a SceneIndex plug-in to generate renderable geometry directly as Hydra prims | 38 |
| 3.8 | Write an AssetResolver that generates in-memory renderable primitives | 38 |

## 4. Data Exchange — 15%

| Obj | Objective | Chapters |
|-----|-----------|----------|
| 4.1 | Convert OpenUSD assets to common 3D formats (e.g. glTF) and ensure fidelity | 27 |
| 4.2 | Document conceptual mappings between USD and another data model (e.g. MaterialX) | 27 |
| 4.3 | Explain trade-offs between USDC and USDA (performance, readability, archival) | 7, 31 |
| 4.4 | Implement a round-trip pipeline in a DCC to and from USD | 27, 35 |
| 4.5 | Use USD schemas to support nonstandard attributes/structures during import/export | 29, 37 |
| 4.6 | Write a validator for the integrity of an OpenUSD asset exported from a DCC | 30 |
| 4.7 | Write an exporter or converter to USD | 28, 29 |
| 4.8 | Write or extend a USD importer in a DCC | 29, 35 |

## 5. Data Modeling — 13%

| Obj | Objective | Chapters |
|-----|-----------|----------|
| 5.1 | Add a primvar to a mesh | 11 |
| 5.2 | Choose appropriate value types to store attribute data | 9, 10 |
| 5.3 | Represent custom metadata | 5, 12 |
| 5.4 | Retrieve properties of a prim | 2, 4, 5, 8 |
| 5.5 | Understand what causes unexpected visual results | 13 |
| 5.6 | Update the extent attribute of a mesh after updating its points | 13 |

## 6. Debugging and Troubleshooting — 11%

| Obj | Objective | Chapters |
|-----|-----------|----------|
| 6.1 | Identify when SdfChangeBlocks can alleviate performance bottlenecks | 8, 34, 44 |
| 6.2 | Identify why opinions from one layer do not take effect in a composed stage | 20, 42 |
| 6.3 | Resolve issues related to asset management | 33, 42 |
| 6.4 | Understand what causes unexpected visual results | 13, 42, 44 |
| 6.5 | Work with diagnostics for debugging and profiling (TfDebug, diagnostic delegates, Trace, TfMallocTag, ...) | 43 |

## 7. Pipeline Development — 14%

| Obj | Objective | Chapters |
|-----|-----------|----------|
| 7.1 | Convert OpenUSD assets to common 3D formats (e.g. glTF) and ensure fidelity | 27 |
| 7.2 | Document asset structure guidelines | 23, 32 |
| 7.3 | Explain trade-offs between USDC and USDA | 7, 31 |
| 7.4 | Implement round-trip pipelines between a DCC and USD | 35 |
| 7.5 | Integrate custom resolvers to manage asset paths dynamically | 33 |
| 7.6 | Represent custom metadata | 12 |
| 7.7 | Validate asset paths are formatted correctly | 33 |
| 7.8 | Write or extend a USD importer in a DCC | 35 |

## 8. Visualization — 8%

| Obj | Objective | Chapters |
|-----|-----------|----------|
| 8.1 | Add a primvar to a mesh | 11, 39 |
| 8.2 | Assign UsdPreviewSurface materials for asset visualization | 40 |
| 8.3 | Bind materials to a mesh | 40 |
| 8.4 | Create a UsdPreviewSurface shading network that reads diffuse color from a primvar | 40 |

## Topics named in the study guide's reading lists (must be covered)

Value clips, layer offsets, edit targets, change processing, flatten, default prim, references without prim paths, scenegraph instancing, kind hierarchy, model hierarchy, UsdShadeNodeGraph, UsdGeomPointInstancer, file format plug-ins, usdGenSchema, PlugRegistry, Ar asset resolution, conceptual data mapping, usdchecker, usdcat, usdzip, USDZ spec, "What file format is my .usd file?", Maximizing USD Performance, stage upAxis and linear units, UsdGeomPoints, `UsdProperty::GetNamespace`, `UsdGeomModelAPI::GetExtentsHint`, `UsdGeomBoundable::ComputeExtentFromPlugins`, timecodes, list editing, primvars, spline animation proposal, attribute interpolation, `UsdStage::SetInterpolationType`, UsdGeomXformable, UsdGeomXformCache, over vs typeless def, usdview LayerStack tab, UsdGeomModelAPI draw modes, `UsdProperty::GetPropertyStack`, UsdUtilsCoalescingDiagnosticDelegate, TfDiagnosticMgr delegates, `UsdStage::Open` pathResolverContext, variant management, working set management (load/unload), `UsdStage::MuteLayer`, reasons adding a reference may fail, Pcp composition errors, sublayers vs references FAQ, scalable asset structure principles, ASWF asset structure guidelines, UsdPhysics (overview), SdfChangeBlock, UsdNotice, timesampled velocities, UsdGeomSubset, UsdShadeMaterialBindingAPI, UsdLuxLightAPI, UsdLuxShadowAPI, UsdLuxShapingAPI, UsdLuxDistantLight, imageable purpose, Gprim.

## Exam format facts (certification page, 2026-10-07)

- 60–70 questions, 120 minutes, online, remotely proctored (Certiverse account required), English, $200, valid two years.
- Level: Professional (described as intermediate-level).
- Study guide sample items include single-answer and "Select two/three options" questions, often with USDA snippets.
- Discrepancy: a search-engine snippet of the en-eu page summary said "90-minute" while the same page's details list says 120 minutes; the en-us page says 120 in both places. Re-check before booking.
