# Question Bank — Data Exchange (DE)

**Original practice questions.** Not actual NVIDIA exam content. Mapped to NCP-OUSD study-guide objectives 4.1–4.8 (Data Exchange, 15%).

Verified against **USD 26.08** (`usd-core` 26.8). Domain target: 60 questions. This file currently holds **DE-001–DE-060** (domain complete).

Work the stems first. Answers and explanations are grouped at the end.

---

**DE-001** · Obj 4.3 · Difficulty: Easy · Type: Single choice

Which statement best captures the USDA vs USDC trade-off?

A. USDA is binary and faster to load; USDC is text for Git diffs
B. USDA is UTF-8 text (readable, mergeable, larger); USDC is crate binary (faster I/O, smaller, not line-diff friendly)
C. They are identical encodings with different extensions
D. USDC cannot store time samples; USDA can

---

**DE-002** · Obj 4.3 · Difficulty: Medium · Type: Single choice

`Usd.Stage.CreateNew("scene.usd")` then `Save()`. What are the **magic bytes** and `GetFileFormat().formatId`?

A. Magic `#usda 1.0`, formatId `usda`
B. Magic `PXR-USDC`, formatId `usdc`
C. Magic `PXR-USDC`, formatId `usd` (id follows the `.usd` plugin; magic follows crate bytes)
D. Magic `PK`, formatId `usdz`

---

**DE-003** · Obj 4.3 · Difficulty: Medium · Type: Multiple select
Select two.

A pipeline copies a valid USDA file to `text.usd`. Which are true on USD 26.08?

A. The file still opens; prims and values are there
B. `formatId` is `usd` (extension plugin), while magic starts with `#usda`
C. `formatId` becomes `usda` because the bytes are text
D. USD refuses to open USDA bytes under a `.usd` name

---

**DE-004** · Obj 4.3 · Difficulty: Easy · Type: Single choice

You must pick an encoding for a **layout department layer** that artists merge in Git, versus a **published cache** opened thousands of times on the farm. Best pair?

A. Git: USDC; farm: USDA
B. Git: USDA; farm: USDC
C. Both USDA — binary is never used in film
D. Both `.usdz` — zip is always smallest

---

**DE-005** · Obj 4.3 · Difficulty: Medium · Type: Single choice

How should an ingest tool decide whether `shot.usd` is text or crate?

A. Trust the extension: `.usd` always means crate
B. Read magic: `#usda` → text, `PXR-USDC` → crate, `PK` → zip
C. Call `Sdf.FileFormat.FindByExtension("usd")` and assume crate
D. `formatId == "usdc"` is necessary and sufficient for crate `.usd` files

---

**DE-006** · Obj 4.7 · Difficulty: Easy · Type: Single choice

`Tf.MakeValidIdentifier("Crate Box")` returns what?

A. `Crate Box` (spaces are legal prim names)
B. `Crate_Box`
C. `crateBox`
D. `""` (invalid; the call raises)

---

**DE-007** · Obj 4.7 · Difficulty: Medium · Type: Single choice

`Tf.MakeValidIdentifier("2ball")` and `Tf.IsValidIdentifier("2ball")`?

A. `"2ball"`, `True`
B. `"_ball"`, `False` for the original string (identifiers cannot start with a digit)
C. `"ball2"`, `True`
D. Both calls raise `Tf.ErrorException`

---

**DE-008** · Obj 4.7 · Difficulty: Easy · Type: Single choice

`Usd.Stage.CreateInMemory()` with no metrics authored. What do `GetStageUpAxis` and `GetStageMetersPerUnit` return?

A. `Y` and `1.0`
B. `Y` and `0.01`
C. `Z` and `1.0`
D. `None` and `None`

---

**DE-009** · Obj 4.7 · Difficulty: Medium · Type: Single choice

A meters, Z-up chair is **referenced** into a centimeters, Y-up shot. The chair's Cube `size` is 1 in the asset. Composed `size` on the shot?

A. `100` — USD multiplies by the metersPerUnit ratio automatically
B. `1.0` — composition does not convert units; you author scale (and often rotateX) on the referencing prim
C. `0.01`
D. `None` — mixed metrics are a composition error

---

**DE-010** · Obj 4.7 · Difficulty: Medium · Type: Single choice

Asset `metersPerUnit = 1` (meters), shot `metersPerUnit = 0.01` (centimeters). Correct scale **factor** to apply on the referencing prim so 1 m becomes 100 shot units?

A. `shot / asset = 0.01`
B. `asset / shot = 100`
C. Always `1` because Cube size is already 1
D. `2.54` (inches)

---

**DE-011** · Obj 4.7 · Difficulty: Medium · Type: Multiple select
Select two.

A Z-up meters asset is referenced into a Y-up centimeters shot. Besides the scale factor, which authoring is the usual axis fix?

A. `AddRotateXOp().Set(-90)` on the referencing prim
B. Change the **composed** stage's `upAxis` metadata — that rotates every referenced asset
C. Read **asset** metrics by opening the asset layer, not by reading the shot's composed `GetStageUpAxis`
D. Set `instanceable = true` so USD converts axes

---

**DE-012** · Obj 4.7 · Difficulty: Medium · Type: Single choice

An OBJ face line is `f 1 2 3`. What should `faceVertexIndices` store?

A. `[1, 2, 3]` (OBJ is already 0-based)
B. `[0, 1, 2]` (OBJ is 1-based; USD Mesh indices are 0-based)
C. `[3, 2, 1]` (USD requires clockwise winding)
D. The converter should skip faces; only `v` lines matter

---

**DE-013** · Obj 4.7 · Difficulty: Medium · Type: Python-reading

A JSON record has a point `[100, 0, 0]` in **centimeters**. The converter scales into meters and authors `metersPerUnit = 1`. What is `points[1]` if that point is the second vertex?

A. `(100.0, 0.0, 0.0)` with `metersPerUnit = 0.01`
B. `(1.0, 0.0, 0.0)` with `metersPerUnit = 1`
C. `(0.01, 0.0, 0.0)` with `metersPerUnit = 100`
D. Leave centimeters in the points and hope Hydra reads `units: "cm"` from JSON

---

**DE-014** · Obj 4.7 · Difficulty: Medium · Type: Single choice

After writing Mesh `points`, what must the exporter still do for a complete boundable?

A. Nothing; `extent` updates itself
B. `ComputeExtentFromPlugins` (or equivalent) **then `Set`** on `extent`
C. Set `kind = component` — that computes extent
D. Export as USDA so usdview fills extent

---

**DE-015** · Obj 4.5 · Difficulty: Easy · Type: Single choice

A CAD `partId` has no UsdGeom attribute. How should a first exporter carry it (Obj 4.5)?

A. Drop it; USD forbids unknown fields
B. A namespaced custom attribute such as `factory:partId` (`Sdf.ValueTypeNames.String`)
C. Store it in the prim **name** only
D. Put it in `faceVertexIndices`

---

**DE-016** · Obj 4.5 · Difficulty: Medium · Type: Multiple select
Select two.

When is a **custom schema** (not only a loose attribute) the right import/export tool?

A. Many DCCs and tools must share a typed `Door` prim with known properties and fallbacks
B. A single one-off vendor id that will never be queried as a type
C. You need `HasAPI` / `IsA` checks and documentation in `schema.usda`
D. You parsed `schema.usda` in memory — that already registers `Door` for `IsA`

---

**DE-017** · Obj 4.5 · Difficulty: Medium · Type: Single choice

On usd-core 26.8 you `ImportFromString` a `schema.usda` that defines `class "Door"`. `FindConcretePrimDefinition("Door")`?

A. The Door definition — parse registers schemas
B. `None` — parse ≠ register; `usdGenSchema` / a plugin is required
C. It raises `Tf.ErrorException`
D. It returns Cube's definition as a fallback

---

**DE-018** · Obj 4.6 · Difficulty: Easy · Type: Single choice

`hasattr(UsdUtils, "ComplianceChecker")` on USD 26.08?

A. `True` — that is still the public validator
B. `False` — use `pxr.UsdValidation` (`ValidationRegistry`)
C. `True` only if `usdchecker` is on PATH
D. `ComplianceChecker` moved to `UsdGeom`

---

**DE-019** · Obj 4.6 · Difficulty: Medium · Type: Single choice

A stage is missing `upAxis`, `metersPerUnit`, and `defaultPrim`. `usdGeomValidators:StageMetadataChecker` vs `usdValidation:StageMetadataChecker` report which names?

A. Geom: `MissingDefaultPrim`; core: missing meters and upAxis
B. Geom: `MissingMetersPerUnitMetadata` and `MissingUpAxisMetadata`; core: `MissingDefaultPrim`
C. Both checkers report all three
D. Neither runs without the `usdchecker` CLI

---

**DE-020** · Obj 4.6 · Difficulty: Medium · Type: Multiple select
Select two.

You are writing a **publish validator** for DCC exports (Obj 4.6). Which checks belong?

A. Stage metadata: `defaultPrim`, `upAxis`, `metersPerUnit`
B. `UsdUtils.ComputeAllDependencies` unresolved list is empty (or listed as known)
C. Every prim's `GetMaster()` is non-null
D. Reject USDA files; only USDC can be valid

---

**DE-021** · Obj 4.6 · Difficulty: Easy · Type: Single choice

usd-core has no `usdchecker` binary. Can you still validate?

A. No — Obj 4.6 requires the CLI
B. Yes — call `UsdValidation` validators from Python
C. Only by flattening first
D. Only inside usdview

---

**DE-022** · Obj 4.1 · Difficulty: Medium · Type: Single choice

USD Mesh faces may be quads. Core glTF mesh primitives expect what?

A. Quads are legal in core glTF 2.0
B. Triangles — the converter must **triangulate** n-gons
C. Only points (no indices)
D. USD `faceVertexCounts` copied unchanged

---

**DE-023** · Obj 4.1 · Difficulty: Medium · Type: Single choice

USD `primvars:st` (UV) → glTF `TEXCOORD_0`. Which extra transform is the usual fidelity rule?

A. `u_gltf = 1 - u_usd` (flip U)
B. `v_gltf = 1 - v_usd` (glTF UV origin is top-left)
C. Scale UVs by `metersPerUnit`
D. Drop UVs; glTF has no texcoords

---

**DE-024** · Obj 4.1 · Difficulty: Medium · Type: Multiple select
Select two.

Converting a composed USD shot to glTF 2.0 **without extensions**, which USD concepts are typically **lost** (must be documented in the mapping)?

A. Variant sets, payloads, and layer stacks as first-class composition
B. Triangle mesh positions after triangulation
C. Native USD composition arcs as live, editable arcs in the `.gltf`
D. A single baked node tree with TRS

---

**DE-025** · Obj 4.1 · Difficulty: Easy · Type: Single choice

glTF 2.0 core assumes which units and up axis?

A. Centimeters, Z-up (like many DCCs)
B. Meters, +Y up
C. Inches, Y-up
D. Whatever `metersPerUnit` is in the USD file — glTF reads that metadata

---

**DE-026** · Obj 4.2 · Difficulty: Medium · Type: Single choice

UsdPreviewSurface `metallic` / `roughness` map most directly onto which glTF field group?

A. `KHR_materials_unlit` only
B. `pbrMetallicRoughness` (`metallicFactor` / `roughnessFactor` and the packed metal-rough texture)
C. MaterialX `ND_standard_surface` with no remainder
D. USDZ `compress_type`

---

**DE-027** · Obj 4.2 · Difficulty: Medium · Type: Single choice

MaterialX `nodedef` / node graph corresponds most closely to which UsdShade idea?

A. `UsdGeom.Mesh` extents
B. A `UsdShade.Shader` / node-graph network with connections, not a single PreviewSurface input block
C. `Sdf.LayerOffset`
D. `Kind.Registry`

---

**DE-028** · Obj 4.2 · Difficulty: Easy · Type: Multiple select
Select two.

Why write a **conceptual data mapping document** before coding a translator (Obj 4.2)?

A. It records source concept → USD (or glTF/MaterialX) target, transforms, and **known loss**
B. NVIDIA requires the document as an exam submission file
C. Teams can review mappings (units, color space, UV flip) before code freezes the wrong rule
D. Mapping documents replace validators

---

**DE-029** · Obj 4.4 · Difficulty: Medium · Type: Single choice

A DCC round-trip (USD → DCC → USD) silently drops payloads and custom `factory:partId`. What is the first design fix?

A. Always `Flatten()` on import so the DCC only sees one layer
B. Extraction → transformation → validation: preserve composition arcs and namespaced attributes; **diff** `ComputeAllDependencies` and attribute values in CI
C. Convert to OBJ in the middle so loss is obvious
D. Store everything in `displayColor`

---

**DE-030** · Obj 4.4 · Difficulty: Medium · Type: Multiple select
Select two.

Healthy DCC **import** of a USD assembly should usually:

A. Keep references/payloads as instances or deferred loads when the DCC can
B. Flatten on import “to make Maya simpler,” discarding the assembly structure
C. Round-trip custom attributes and applied API schemas the studio cares about
D. Rewrite every prim name through a new random identifier

---

**DE-031** · Obj 4.8 · Difficulty: Medium · Type: Single choice

You are extending a DCC **importer** (Obj 4.8). A referenced chair root is type `Xform`. The importer currently calls `UsdGeom.Xform.Define` on the same path before adding the reference. Why is that a bug?

A. `Xform.Define` is illegal in importers
B. Defining a typed Xform on the path can **override/replace** the incoming type; use a **typeless** `DefinePrim` then `AddReference` so the asset's type wins
C. You must `Sphere.Define` first
D. Importers may only use `Sdf.Layer.Open`

---

**DE-032** · Obj 4.8 · Difficulty: Medium · Type: Single choice

A DCC importer must bind a UsdPreviewSurface material that the exporter wrote with `Bind` but **without** `MaterialBindingAPI.Apply`. On USD 26.08, `HasAPI(MaterialBindingAPI)` is `False` even though the relationship exists. What should the importer do?

A. Ignore the binding; `HasAPI` False means there is no material
B. Read `material:binding` (or Apply then Bind on export); do not treat `HasAPI` as the only signal
C. Switch to OpenGL bind points
D. Call `GetMaster()` on the mesh

---

**DE-033** · Obj 4.7 · Difficulty: Medium · Type: Single choice

Tessellated CAD should set Mesh `subdivisionScheme` to what so Hydra does not Catmull-Clark the tessellation?

A. Leave the fallback (`catmullClark`)
B. `"none"`
C. `"loop"`
D. `"bilinear"` is required for all CAD

---

**DE-034** · Obj 4.3 · Difficulty: Easy · Type: Single choice

USDZ packaging on this book's verified path uses which zip compression for files?

A. DEFLATE (`compress_type` 8)
B. STORE (`compress_type` 0)
C. LZMA
D. Uncompressed only for USDA, DEFLATE for PNG

---

**DE-035** · Obj 4.1 · Difficulty: Medium · Type: Single choice

A USD asset is Y-up centimeters. You convert to glTF (meters, Y-up). Besides shrinking points by 100×, what else belongs in the fidelity checklist?

A. Nothing; glTF reads `metersPerUnit`
B. Scale positions (and extents / `POSITION` min/max); keep +Y; triangulate; flip V; report dropped variants
C. Rotate −90 about X because glTF is Z-up
D. Write the USDA as extras and skip mesh export

---

**DE-036** · Obj 4.7 · Difficulty: Easy · Type: Single choice

`UsdGeom.LinearUnits.meters` and `.centimeters` are:

A. `1.0` and `0.01`
B. `100` and `1`
C. Tokens `"m"` and `"cm"`
D. Undefined on usd-core

---

**DE-037** · Obj 4.6 · Difficulty: Medium · Type: Python-reading

```{.python .norun}
print(hasattr(UsdUtils, "ComplianceChecker"))
print(shutil.which("usdchecker"))
```

On the book's usd-core 26.8 environment, what prints?

A. `True` then a path to usdchecker
B. `False` then `None`
C. `True` then `None`
D. AttributeError

---

**DE-038** · Obj 4.4 · Difficulty: Hard · Type: Single choice

Round-trip CI opens the DCC export and calls `UsdUtils.ComputeAllDependencies`. The return value is a 3-tuple. What are the three lists?

A. Prim paths, property names, time samples
B. Layers, asset paths, **unresolved** identifiers
C. USDA files, USDC files, USDZ files
D. References, payloads, sublayers only

---

**DE-039** · Obj 4.8 · Difficulty: Medium · Type: Single choice

usd-core cannot import `UsdMtlx`. A DCC that must round-trip MaterialX graphs needs what?

A. Nothing; PreviewSurface is MaterialX
B. A **full OpenUSD build** (or the DCC's USD) with the MaterialX plugin; mapping documented separately from PreviewSurface
C. Rename `.mtlx` to `.usda`
D. `Tf.MakeValidIdentifier` on the MaterialX XML

---

**DE-040** · Obj 4.7 · Difficulty: Medium · Type: Single choice

Exporter hooks (Obj 4.7 / 4.8) should typically enforce which **stage** fields before publish?

A. `defaultPrim`, `upAxis`, `metersPerUnit`, and (for components) `kind`
B. `relocates` on every layer
C. `instanceable = true` on the default prim
D. Empty `subLayers` so the file is “simple”

---

**DE-041** · Obj 4.1 · Difficulty: Medium · Type: Single choice

USD time samples are in **timeCodes**. glTF animation input is **seconds**. Conversion rule?

A. Copy timeCodes unchanged
B. `seconds = timeCode / timeCodesPerSecond` (and author that metadata on the USD stage)
C. `seconds = timeCode * metersPerUnit`
D. glTF cannot animate transforms at all

---

**DE-042** · Obj 4.1 · Difficulty: Easy · Type: Single choice

USD `doubleSided = true` on a gprim maps to which glTF material flag?

A. There is no equivalent; drop it
B. `material.doubleSided`
C. `extras.upAxis`
D. `KHR_lights_punctual`

---

**DE-043** · Obj 4.1 · Difficulty: Medium · Type: Multiple select
Select two.

A fidelity checklist for USD → glTF should include which **reports of loss** (not silent drops)?

A. Variant selections baked; other variants omitted
B. Layer/payload structure flattened to one node tree
C. Triangulated positions (this is success, not loss, if documented as the transform)
D. USDA ↔ USDC encoding (this is a different, lossless hop)

---

**DE-044** · Obj 4.2 · Difficulty: Medium · Type: Single choice

UsdShade `Material` with a `surface` output connected to `UsdPreviewSurface` vs a MaterialX `standard_surface` graph: what belongs in the mapping document?

A. They are bitwise identical; no row needed
B. PreviewSurface is a small fixed PBR; MaterialX nodedefs are a broader graph — list each input, color space, and what has **no** PreviewSurface peer
C. MaterialX is only textures; UsdShade is only lights
D. Both are glTF `extras` only

---

**DE-045** · Obj 4.2 · Difficulty: Easy · Type: Single choice

A mapping table row should contain at least:

A. Only the USD token name
B. Source concept, target concept, transform (units/UV/color), and loss/notes
C. Only Python API names
D. NVIDIA exam objective IDs

---

**DE-046** · Obj 4.3 · Difficulty: Medium · Type: Single choice

usd-core has no `usdcat`. What is the Python equivalent to rewrite `a.usda` as crate?

A. There is none
B. `Sdf.Layer.FindOrOpen("a.usda").Export("a.usdc")` (encoding follows the destination extension)
C. `stage.Flatten()` — flatten always writes USDC
D. Rename the file to `.usdc`

---

**DE-047** · Obj 4.3 · Difficulty: Medium · Type: Single choice

For **archival** of a human-readable show bible (comments, layer structure you may need to recover in 20 years), which encoding is the usual pick?

A. USDC only (smaller is always better archives)
B. USDA (or USDA + a crate publish), because text remains inspectable without the crate parser
C. USDZ STORE only
D. OBJ

---

**DE-048** · Obj 4.4 · Difficulty: Medium · Type: Single choice

A DCC exporter writes a flattened crate and drops the payload that pointed at `Chair_payload.usdc`. Round-trip test using `ComputeAllDependencies` will show what?

A. Nothing — flatten is lossless for dependencies
B. The payload layer disappears from the layer list; the test should **fail** if the pipeline required that payload to survive
C. Unresolved always includes `Chair_payload.usdc` even after flatten
D. Flatten adds a fake payload automatically

---

**DE-049** · Obj 4.4 · Difficulty: Medium · Type: Multiple select
Select two.

A round-trip harness (Obj 4.4) should compare which of the following after DCC export?

A. Key attribute `Get()` values (including custom namespaces)
B. `ComputeAllDependencies` layer/asset/unresolved lists
C. `GetMaster()` paths
D. Whether the file still starts with `#usda` only — crate exports are automatic failures

---

**DE-050** · Obj 4.5 · Difficulty: Medium · Type: Single choice

`customData` dictionary vs a typed `factory:partId` attribute vs a `Door` schema. Which guideline matches Obj 4.5?

A. Always use `customData` for anything non-UsdGeom
B. Queryable, typed, per-prim payload → attribute or schema; opaque bag of editor notes → `customData`; shared studio type → schema
C. Schemas cannot be used during import/export
D. `customData` is deleted on Flatten

---

**DE-051** · Obj 4.6 · Difficulty: Medium · Type: Single choice

You write a studio validator that flags meshes with points but no `extent`. Where does it run in the exchange pipeline?

A. Only inside usdview
B. After transformation, **before publish** (validation stage of extract → transform → validate)
C. Before extraction, on the DCC native scene only
D. It replaces the mapping document

---

**DE-052** · Obj 4.6 · Difficulty: Hard · Type: Single choice

After authoring `upAxis` and `metersPerUnit` but **not** `defaultPrim`, lab 27's two checkers return which counts?

A. Geom 0, core still has `MissingDefaultPrim` (1)
B. Both still 3 errors
C. Core 0, geom still missing defaultPrim
D. Both 0 because Sphere.Define sets defaultPrim

---

**DE-053** · Obj 4.7 · Difficulty: Medium · Type: Single choice

Lab 26 applies `rotateX(-90)` **then** `scale(factor)`. Why order matters for a Z-up asset into Y-up cm?

A. Order never matters for xformOps
B. `xformOpOrder` is applied in list order; rotate then scale matches “stand the asset up, then size it in shot units”
C. Scale must always be first in USD
D. USD ignores `xformOpOrder` on referencing prims

---

**DE-054** · Obj 4.7 · Difficulty: Easy · Type: Single choice

`Tf.IsValidIdentifier("Crate_Box")` vs `"Crate Box"`?

A. `True`, `True`
B. `True`, `False`
C. `False`, `False`
D. `False`, `True`

---

**DE-055** · Obj 4.8 · Difficulty: Medium · Type: Single choice

A DCC importer calls `Usd.Stage.Open(path, Usd.Stage.LoadNone)` and never `Load`s. Chair assets were published as **payloads**. Artists see empty roots. Why?

A. `LoadNone` is an illegal argument, so the stage is empty
B. Payloads stay unloaded until `Load`/`LoadAll`; the importer must set a load policy. References would still load under `LoadNone`
C. `LoadNone` unloads references and payloads equally
D. Empty roots mean `defaultPrim` was missing, not a load-set issue

---

**DE-056** · Obj 4.8 · Difficulty: Medium · Type: Multiple select
Select two.

Extending a DCC importer for animation (Obj 4.8) should:

A. Read time samples **and** defaults (`Get()` vs `Get(time)`); missing default is not “zero”
B. Apply layer offsets when evaluating referenced clips
C. Drop all samples and keep one default at frame 0
D. Require USDA; refuse USDC

---

**DE-057** · Obj 4.1 · Difficulty: Medium · Type: Single choice

glTF custom vertex attributes must be named how, if you park a USD primvar that has no core glTF slot?

A. Any name
B. Prefix `_` (e.g. `_factory_partId` analog at vertex rate) or use `extras` at mesh/node
C. USD colon namespaces (`factory:partId`) are legal glTF attribute names
D. Only via MaterialX

---

**DE-058** · Obj 4.3 · Difficulty: Easy · Type: Single choice

`Sdf.FileFormat.FindByExtension("usd").formatId` on 26.08?

A. `usdc`
B. `usd`
C. `usda`
D. `None`

---

**DE-059** · Obj 4.7 · Difficulty: Medium · Type: Single choice

Handedness: USD and glTF are both **right-handed**. A converter that also mirrors X “because game engines are left-handed” without a documented axis policy is:

A. Required for all glTF
B. An undocumented extra transform that breaks fidelity unless the mapping says so
C. How `upAxis = Z` is implemented
D. Performed automatically by `AddReference`

---

**DE-060** · Obj 4.4 · Difficulty: Medium · Type: Single choice

`UsdPhysics` APIs on a collider mesh survive a DCC that only knows PreviewSurface and Mesh. Round-trip result?

A. Physics is core glTF, so it always survives
B. Loss unless the importer/exporter maps it (custom schema/API) or you keep a sidecar USD; document it as out of scope
C. Flatten restores physics
D. `kind = component` encodes physics

---

## Answers

**DE-001 — Answer: B.** Text vs crate is the core trade-off. They are different encodings; USDC stores the same scene data including samples. Review: §7.1–7.2, §31.1.

**DE-002 — Answer: C.** Verified: `CreateNew("scene.usd")` writes crate magic `PXR-USDC` but `formatId` is `usd`. Review: §31.3.

**DE-003 — Answer: A, B.** Verified: copied USDA bytes under `.usd` open with radius 2; `formatId` stays `usd`; magic `#usda`. Review: §31.3.

**DE-004 — Answer: B.** Mergeable text for work layers; crate for high-frequency published I/O. Review: §31.1.

**DE-005 — Answer: B.** Extension `.usd` is ambiguous. `FindByExtension("usd")` is `usd`, not the encoding. Crate `.usd` does **not** report `formatId usdc`. Review: §31.3.

**DE-006 — Answer: B.** Verified: `"Crate Box"` → `Crate_Box`. Spaces are not valid identifiers. Review: §28.4, lab 25.

**DE-007 — Answer: B.** Verified: `MakeValidIdentifier("2ball")` is `_ball`; `IsValidIdentifier("2ball")` is False. Review: §28.4.

**DE-008 — Answer: B.** Verified: fallback Y, 0.01. Review: §28.1–28.2, lab 26.

**DE-009 — Answer: B.** Verified: composed Cube size stays `1.0`. USD does not auto-convert. Review: §28.3, lab 26.

**DE-010 — Answer: B.** Verified: factor `asset_mpu / shot_mpu` = 100. Review: §28.3, lab 26.

**DE-011 — Answer: A, C.** Z-up into Y-up → rotateX −90 on the **referencing** prim; read the asset file's metrics. Changing shot `upAxis` does not rotate referenced geometry. Review: §28.2–28.3, lab 26.

**DE-012 — Answer: B.** Verified in lab 25: `f 1 2 3` → `[0, 1, 2]`. Review: §29.2.

**DE-013 — Answer: B.** Verified: 100 cm → `(1.0, 0.0, 0.0)` meters, `metersPerUnit = 1`. Review: §29.2, lab 25.

**DE-014 — Answer: B.** Verified: `GetExtentAttr()` is None until you compute and Set. Review: §13.3, §29.2.

**DE-015 — Answer: B.** Namespaced custom attributes are the lightweight Obj 4.5 path (`factory:partId` in lab 25). Review: §29.4.

**DE-016 — Answer: A, C.** Shared typed prims need schemas and `IsA`. A one-off id can stay a custom attribute. Parsing USDA does **not** register Door (D is false). Review: §29.4, §37.1, lab 31.

**DE-017 — Answer: B.** Verified: Door stays unregistered after parse; `usdGenSchema` is missing on usd-core. Review: §37.1, lab 31.

**DE-018 — Answer: B.** Verified: `ComplianceChecker` is gone. Review: §30.4, lab 27.

**DE-019 — Answer: B.** Verified lab 27 error names. Review: §30.3.

**DE-020 — Answer: A, B.** Metadata checkers plus unresolved-dependency checks are the integrity baseline. `GetMaster()` is gone on 26.08 and is not a validator. USDA files can be valid. Review: §30.5, §32.4.

**DE-021 — Answer: B.** Python `UsdValidation` is enough. Review: §30.2–30.3.

**DE-022 — Answer: B.** Core glTF primitives are triangles. Review: §27.4.

**DE-023 — Answer: B.** V flip is the documented UV convention. Review: §27.4.

**DE-024 — Answer: A, C.** Composition is not a glTF core concept; you bake a node tree (D is what you *keep*, not what you lose). Triangle positions after triangulation are the intended geometry carry. Review: §27.4.

**DE-025 — Answer: B.** Meters, +Y. glTF does not read USD stage metadata. Review: §27.4.

**DE-026 — Answer: B.** PreviewSurface metal/rough → glTF PBR metal-rough. Review: §27.4.

**DE-027 — Answer: B.** MaterialX is a nodedef graph; UsdShade Shader/NodeGraph is the cousin, not Mesh extents. Review: §27.4.

**DE-028 — Answer: A, C.** Mapping documents are the Obj 4.2 artifact. They do not replace validators or exam paperwork. Review: §27.3.

**DE-029 — Answer: B.** Round-trip is extract/transform/validate plus automated diffs. Flatten-on-import is a common source of loss. Review: §27.2, §27.5, §35.3.

**DE-030 — Answer: A, C.** Keep structure and custom/API data. Random names and flatten-by-default fight round-trip. Review: §27.5, §29.5.

**DE-031 — Answer: B.** Lab 26: typeless `DefinePrim` so the asset type comes through. Review: §28.3, §29.5.

**DE-032 — Answer: B.** Verified: Bind without Apply writes the rel, `HasAPI` False. Review: §40.x, lab 34.

**DE-033 — Answer: B.** Fallback is catmullClark; tessellated CAD wants `none`. Review: §13, lab 11 / 25.

**DE-034 — Answer: B.** Verified lab 28: `compress_type` 0 STORE. Review: §31.2.

**DE-035 — Answer: B.** Scale to meters, keep Y-up, triangulate, flip V, document dropped composition. glTF is not Z-up. Review: §27.4, §28.3.

**DE-036 — Answer: A.** Verified: 1.0 and 0.01. Review: §28.1.

**DE-037 — Answer: B.** Verified: False, None. Review: §30.2, lab 27.

**DE-038 — Answer: B.** Verified lab 28: 3-tuple (layers, assets, unresolved). Review: §32.4.

**DE-039 — Answer: B.** `UsdMtlx` ImportError on usd-core. Review: §27.1, §35.1.

**DE-040 — Answer: A.** Exporter hooks author pipeline metadata. Review: §29.6, §34.1.

**DE-041 — Answer: B.** glTF sampler input is seconds; divide by `timeCodesPerSecond`. Core glTF can animate TRS (not “cannot animate”). Review: §27.4.

**DE-042 — Answer: B.** `doubleSided` is a core glTF material flag. Review: §27.4.

**DE-043 — Answer: A, B.** Variants and layer/payload structure are composition losses. Triangulation is a documented transform of geometry, not a silent concept drop. USDA↔USDC is lossless and not a glTF issue. Review: §27.4, §31.1.

**DE-044 — Answer: B.** PreviewSurface ≠ full MaterialX graph; the mapping table lists gaps. Review: §27.4.

**DE-045 — Answer: B.** That is the Chapter 27 template. Review: §27.3.

**DE-046 — Answer: B.** `Export` picks encoding from the destination extension (verified Ch 31). Flatten is composition, not format. Rename does not transcode. Review: §31.4.

**DE-047 — Answer: B.** Archival readability favors USDA. Review: §31.1.

**DE-048 — Answer: B.** Flatten bakes payloads away; a round-trip that required the payload must fail. Review: §27.5, §34.2.

**DE-049 — Answer: A, B.** Values plus dependency lists. `GetMaster` is gone; crate vs USDA is not an automatic fail. Review: §27.5, §32.4, §35.3.

**DE-050 — Answer: B.** Match the container to how the data will be queried. Review: §29.4, §12.2.

**DE-051 — Answer: B.** Validation is the third pipeline stage, at publish. Review: §27.2, §30.5.

**DE-052 — Answer: A.** Stretch in lab 27: skip `SetDefaultPrim` → core still `MissingDefaultPrim`; geom is 0 once axis and meters are set. `Sphere.Define` does not set defaultPrim. Review: lab 27, §30.3.

**DE-053 — Answer: B.** Ops apply in `xformOpOrder`; lab 26 authors rotateX then scale. Review: §28.3, lab 26, §39.

**DE-054 — Answer: B.** Verified: `Crate_Box` True, `Crate Box` False. Review: §28.4.

**DE-055 — Answer: B.** Verified: `LoadNone` leaves references loaded and payloads unloaded. Importers that pass `LoadNone` must Load what artists need. Review: §17.2, §29.5.

**DE-056 — Answer: A, B.** Defaults vs samples and layer offsets are composition/time rules importers must honor. Review: §10, §16.4, §29.5.

**DE-057 — Answer: B.** glTF requires `_` prefix on custom vertex attributes; colons are not legal names there. Review: §27.4.

**DE-058 — Answer: B.** Verified: `FindByExtension("usd").formatId` is `usd`. Review: §31.3.

**DE-059 — Answer: B.** Extra mirrors must be in the mapping document. USD/glTF are right-handed; reference does not mirror. Review: §27.4, §28.5.

**DE-060 — Answer: B.** Domain schemas survive only if the DCC maps them or you keep USD as source of truth. Review: §27.5, §35.4.

---

*Data Exchange domain complete: DE-001–DE-060 (target 60).*

