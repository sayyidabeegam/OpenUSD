# Glossary

One-line definitions for the NCP-OUSD study book. Verified against **USD 26.08** (`usd-core` 26.8) unless a note says otherwise. Chapter numbers point at this book’s TOC. Older talks that say **LIVRPS** omit relocates; the rest of the order is unchanged.

**Count:** 167 terms.

---

## A

**ABI** — Binary interface a plugin must match; a 24.11 plugin is not safe in a 26.8 process. *Ch 35.*

**Active** — Whether a prim participates in default traversal and imaging; `active = false` prunes children. *Ch 4.*

**API schema** — Schema you `Apply` (`UsdAPISchemaBase`); does not change `typeName` (e.g. `MaterialBindingAPI`). *Ch 6, 37.*

**Ar / asset resolution** — How `@path@` becomes bytes (`Ar.GetResolver()` is the **Resolver** facade). *Ch 33.*

**Assembly** — Model kind that aggregates other models; `IsGroup()` True, `IsComponent()` False. *Ch 6, 23.*

**Asset path** — `@./chair.usda@` (or a URI). Composition **anchors to the layer**; naive `Resolve("./…")` uses cwd. *Ch 33.*

**Attribute** — A typed value on a prim (`double radius`). Contrast relationship. *Ch 5.*

## B

**Binding (material)** — Relationship `material:binding` from geometry to a `Material`. Apply `MaterialBindingAPI` then `Bind`. *Ch 40.*

**`bindMaterialAs`** — Binding strength: `strongerThanDescendants` or `weakerThanDescendants`. *Ch 40.*

**Block** — Explicit “no value” on an attribute so weaker opinions cannot contribute (`attr.Block()`). *Ch 5, 21.*

## C

**ChangeBlock** — `with Sdf.ChangeBlock():` batches edits so `ObjectsChanged` coalesces; new-child `DefinePrim` inside can raise. *Ch 8, 34, 44.*

**Class specifier** — `class` prim; abstract source for inherits/specializes. *Ch 4, 19.*

**Clip (value clip)** — Prim metadata that streams time samples from a sequence of files. *Ch 21.*

**Codeless schema** — Schema used from generated USDA + `plugInfo.json` without compiled C++ types. *Ch 37.*

**CoalescingDiagnosticDelegate** — Groups identical diagnostics; install **before** `Open`. *Ch 43.*

**Collection** — Path set used for light linking or collection-based material binds. *Ch 40, 41.*

**Component** — Publishable model kind (chair, mill). Broken parent chain → `IsComponent()` False. *Ch 6, 23.*

**Composition** — Combining layer opinions into one stage by LIVERPS and list-ops. *Ch 1, 14.*

**Composition error** — Pcp object on the stage (`GetCompositionErrors()`); often a **warning** at Open, not `ErrorException`. *Ch 42, 43.*

**Connectable** — Shade prim whose inputs/outputs can be wired (`ConnectableAPI`). *Ch 40.*

**Crate** — USDC binary layout; magic `PXR-USDC`. *Ch 7, 31.*

**`customData`** — Dictionary of producer key/values renderers should ignore. *Ch 12.*

## D

**Default (attribute)** — Untimed authored value. `Get()` with no time reads this — **`None` if only samples exist**. *Ch 10.*

**`defaultPrim`** — Layer metadata naming the prim `@file@` references when no path is given. *Ch 16.*

**DefaultResolver** — Usual underlying Ar plugin; `Ar.GetUnderlyingResolver()`, not `GetResolver()`. *Ch 33.*

**`def`** — Specifier that **defines** a prim (type may be empty). *Ch 4, 20.*

**Diagnostic delegate** — Object that receives Tf status/warnings/errors. *Ch 43.*

**DistantLight** — Infinite parallel rays; intensity fallback **50000**; name `inputs:intensity`. *Ch 41.*

**Draw mode** — `model:drawMode` stand-in (`bounds`, `cards`, …) on **models**. *Ch 26, 44.*

## E

**Edit target** — Layer (or variant site) that new `Usd` edits write; must be in the local stack. *Ch 15.*

**EditContext** — `with Usd.EditContext(stage, layer):` scoped edit target that restores after. *Ch 15.*

**ElementSize** — How many array entries make one logical primvar element. *Ch 11.*

**ErrorException** — `Tf.ErrorException` raised for USD coding/runtime/parse errors. *Ch 43.*

**Exposure** — Light scale: brightness ∝ `intensity × 2^exposure`. *Ch 41.*

**Extent** — Axis-aligned box on boundables; recompute with `ComputeExtentFromPlugins` after `points` change. *Ch 13.*

**`extentsHint`** — Cached model-level boxes per purpose. *Ch 13, 26.*

**ExtractExternalReferences** — One-file 3-tuple `(sublayers, refs+assets, payloads)`. *Ch 32.*

## F

**FaceVarying** — Primvar interpolation: one value per face-corner (UV seams). *Ch 11.*

**Fallback (schema)** — Built-in default used only when nothing authored a value (Cube `size` → 2.0). *Ch 6, 21.*

**File-format plugin** — `SdfFileFormat` registered for an extension. *Ch 7, 38.*

**Flatten** — `stage.Flatten()` bakes **references** (and sublayers) into one layer. *Ch 34.*

**FlattenLayerStack** — Collapses **sublayers**, **keeps** references. *Ch 34.*

**formatId** — Plugin id (`usda` / `usdc` / **`usd`** for `.usd` / `usdz`); follows the **extension**, not always the magic. *Ch 7, 31.*

## G

**Gf** — Graphics foundations: `Vec3d`, `Matrix4d`, `Camera`. *Ch 9, 39.*

**Gprim** — Geometric primitive (`UsdGeomGprim`: Mesh, Cube, Sphere, …). PointInstancer is **not** a Gprim. *Ch 6, 25.*

**Group (kind)** — Model kind used to organize insides of assemblies; not the usual published root. *Ch 6, 23.*

## H

**Held interpolation** — Time samples hold the previous value until the next; no blend. *Ch 10.*

**Hydra** — Imaging framework (scene index → render delegate). **Not** in the usd-core wheel. *Ch 38, 41.*

## I

**Imageable** — Schema for vis/purpose on things that can be drawn. *Ch 13, 39.*

**Inactive prim** — `active = false`; children pruned. *Ch 4, 42.*

**Indexed primvar** — Palette values plus an index array (`SetIndices`). Independent of interpolation. *Ch 11.*

**`info:id`** — Shader implementation token (`UsdPreviewSurface`, `UsdUVTexture`). *Ch 40.*

**Inherit** — Composition arc broadcasting class opinions; **beats variants, refs, payloads, specializes**. *Ch 19, 21.*

**Instance (native)** — Prim with `IsInstance()` True sharing a prototype. *Ch 24.*

**Instance proxy** — Descendant under an instance; `Traverse` skips it; `OverridePrim` **raises**. *Ch 24.*

**Instance root** — The instanceable prim itself — legal place for per-copy primvars/binds. *Ch 24.*

**`instanceable`** — Authored intent to share a prototype; `IsInstance()` is the live result. *Ch 24.*

**Interface input** — Material-level input shots can override without editing the shader graph. *Ch 40.*

**Interpolation (time)** — `linear` vs `held` between samples; past the last sample both **hold**. *Ch 10.*

**Interpolation (primvar)** — `constant` / `uniform` / `varying` / `vertex` / `faceVarying`. *Ch 11.*

**Invalid prim** — `GetPrimAtPath` miss: `bool`/`IsValid` False; `IsDefined()` **raises**. *Ch 4, 42.*

**InvalidAssetPath** — Composition error: the `@file@` could not be opened. *Ch 16, 42.*

## K

**Kind** — Model-hierarchy token (`component`, `assembly`, …). `Kind.Registry.Register` **does not exist**. *Ch 6, 38.*

## L

**Layer** — One opinion container (file or anonymous). *Ch 3.*

**Layer offset** — `(offset, scale)`: `composedTime = offset + scale × layerTime`. *Ch 10, 16.*

**Layer stack** — Session → root → sublayers (first listed **strongest**). *Ch 3, 15.*

**LightAPI** — Built into typed UsdLux lights (`HasAPI` True without Apply). *Ch 41.*

**Linear interpolation** — Blend between adjacent time samples. *Ch 10.*

**List op / list editing** — `prepend` / `append` / `delete` / explicit list on arcs, `apiSchemas`, relationships. *Ch 14.*

**LIVERPS** — Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes (strongest → weakest). *Ch 14, 21.*

**Load rules** — `LoadAll` / `LoadNone` / per-path; **references still load** under `LoadNone`. *Ch 17, 44.*

**Local** — Opinions from the current node’s layer stack (session, root, sublayers, nested `over`). Strongest LIVERPS letter. *Ch 21.*

**Localize** — Copy needed layers/assets into a self-contained tree (`UsdUtils.LocalizeAsset`). *Ch 22, 32.*

## M

**Magic bytes** — First bytes of a file: `#usda 1.0`, `PXR-USDC`, or `PK` (zip). *Ch 7, 31.*

**MallocTag** — Optional allocator tags; `GetTotalBytes()` often **0** on this pip wheel. *Ch 43.*

**Material** — `UsdShade.Material` container you bind to geometry. *Ch 40.*

**`MaterialBindingAPI`** — Applied API required for a legal bind (`Apply` then `Bind`). *Ch 40.*

**Metadata** — Non-attribute fields (`documentation`, `comment`, `customData`, layer `upAxis`). *Ch 5, 12.*

**`metersPerUnit`** — Layer/stage linear unit; **not auto-converted** on reference. In-memory fallback **0.01**. *Ch 2, 28.*

**Model hierarchy** — Kind tree used as a table of contents (assembly / component / group). *Ch 6, 23.*

**Muted layer** — `MuteLayer(id)`; omitted from `GetLayerStack`. *Ch 15, 42.*

## N

**Namespace (prim)** — Parent/child path tree (`/World/Ball`). *Ch 4.*

**Namespace (property)** — Prefix such as `primvars:`, `xformOp:`, `inputs:`. *Ch 5, 40, 41.*

**Native instancing** — Shared prototype prim tree via `instanceable = true`. *Ch 24.*

**NodeGraph** — Container for connected shaders; Material derives from it. *Ch 40.*

**Null prim** — Invalid handle from a missing path. *Ch 4.*

## O

**ObjectsChanged** — Notice: **resync** paths (new prims) vs **changed-info-only** (attribute Set). *Ch 34.*

**OpenMasked** — Open with a `StagePopulationMask`; **not** `Open(..., mask=)`. *Ch 17, 44.*

**Opinion** — One authored value for a field in one layer. *Ch 14.*

**over** — Specifier that overlays opinions; does **not** define a prim by itself. *Ch 4, 20.*

## P

**Package format** — Format that contains other files (USDZ); `IsPackage()`. *Ch 31, 38.*

**Payload** — Deferred composition arc; USDA keyword **`payload`** (singular). Weaker than references. *Ch 17.*

**Pcp** — Prim cache / composition engine that builds the prim index. *Ch 1, 22.*

**Pin** — Published identifier that still resolves the same bytes next month. *Ch 32.*

**Plugin** — Library or resource pack discovered via `plugInfo.json` / `PXR_PLUGINPATH_NAME`. *Ch 36.*

**PointInstancer** — Boundable (not Gprim) that stores instances as arrays. *Ch 25.*

**Population mask** — Which prim paths exist at all (`OpenMasked`). *Ch 17, 44.*

**Prim** — Named object on the stage (`Usd.Prim`). *Ch 4.*

**Prim path** — Address `/World/Ball` (`Sdf.Path`). *Ch 4.*

**Prim index** — Pcp’s composed graph of nodes (arcs + stacks) for one prim. *Ch 14, 22.*

**Prim stack** — Specs that contribute to a prim, strongest first (`GetPrimStack`). *Ch 22, 42.*

**Primvar** — Geometric variable in `primvars:` (color, `st`, IDs), often inherited. *Ch 11.*

**Property** — Attribute or relationship on a prim. *Ch 5.*

**Property stack** — Specs for one property, strongest first (`GetPropertyStack`). *Ch 22, 42.*

**Prototype** — Shared hidden tree `/__Prototype_N` for native instances (`GetPrototype`). *Ch 24.*

**`protoIndices`** — Per-instance ints into a PointInstancer’s `prototypes` list. *Ch 25.*

**Purpose (imageable)** — `default` / `render` / `proxy` / `guide`; viewer masks hide some. *Ch 13, 42.*

**Purpose (material)** — `preview`, `full`, or all-purpose `''`. *Ch 40.*

**`pxr`** — Python package: `from pxr import Usd`. *Ch 1.*

## R

**Reference** — Composition arc that always composes with the parent (not deferred). *Ch 16.*

**Relationship** — Property whose value is prim/property targets (`rel`). *Ch 5.*

**Relocates** — Layer metadata renaming composed paths; keys must match **composed** paths. *Ch 20.*

**Render delegate** — Hydra backend (Storm, RenderMan, Arnold, …). *Ch 41.*

**ResolveInfo** — `attr.GetResolveInfo(time)`: which encoding won (sample/default/fallback). *Ch 21, 42.*

**Resource plugin** — `plugInfo.json` + files, no shared library. *Ch 36.*

**Root layer** — The layer `Open`/`CreateNew` used as the stage’s main file. *Ch 2, 3.*

## S

**Scene description** — Data model of prims, properties, layers, and composition — not “just a file type.” *Ch 1.*

**Scene index** — Hydra graph node that generates/filters render prims; needs an imaging build. *Ch 38.*

**Schema** — Named contract for properties (`Cube`, `Mesh`, `MaterialBindingAPI`). *Ch 6.*

**`schema.usda`** — Source `usdGenSchema` reads; **parsing it does not register** types. *Ch 37.*

**Sdf** — Scene description foundations: layers, specs, value types (no composition). *Ch 8.*

**Session layer** — Strongest anonymous stack layer; not written into the root on `Save`. *Ch 2, 15.*

**Shader** — `UsdShade.Shader` node identified by `info:id`. *Ch 40.*

**ShadowAPI / ShapingAPI** — Applied UsdLux APIs (must `Apply`). *Ch 41.*

**Specializes** — Weakest LIVERPS arc; class of fallbacks that **lose to references**. *Ch 19, 21.*

**Specifier** — `def`, `over`, or `class`. *Ch 4.*

**SphereLight** — Local area light; intensity fallback **1**. *Ch 41.*

**Stage** — Composed live scene (`Usd.Stage`). *Ch 2.*

**StageMetadataChecker** — Two validators: core `defaultPrim` and geom units/upAxis. *Ch 30.*

**Sublayer** — Layer included in another layer’s stack (`subLayers`); first listed strongest. *Ch 3, 15.*

**Subcomponent** — Kind for pieces **inside** a component; **not** a model. *Ch 6.*

**Subset** — `UsdGeom.Subset` faces of a mesh; can hold its own material bind. *Ch 39, 40.*

## T

**Tf** — Foundation library: diagnostics, debug symbols, `MakeValidIdentifier`, notices. *Ch 9, 43.*

**TfDebug** — Named log switches (`USD_CHANGES`, `PCP_PRIM_INDEX`) via API or `TF_DEBUG`. *Ch 43.*

**Time sample** — Value authored at a `Usd.TimeCode`. *Ch 10.*

**Trace** — Instrumentation timer (`Trace.Collector` / `Reporter`). *Ch 43.*

**Typed schema** — `UsdTyped` / `IsA` prim type (`def Cube`). *Ch 6, 37.*

**Typeless prim** — `def`/`over` with empty `typeName`. *Ch 4, 20.*

## U

**Undefined prim** — `over` with no defining `def`; `IsDefined()` False, `bool` may still be True. *Ch 20, 42.*

**UnresolvedPrimPath** — File opened but target prim missing (often no `defaultPrim`). *Ch 16, 42.*

**`upAxis`** — Stage/layer up direction; in-memory fallback **Y**; token `UsdGeom.Tokens.z`. *Ch 2, 28.*

**USDA** — Text encoding; first line `#usda 1.0`; Git-friendly. *Ch 7.*

**USDC** — Crate binary; faster/smaller; poor line-diffs. *Ch 7, 31.*

**USD (`.usd`)** — Extension that may be crate **or** text; `CreateNew` writes crate; formatId `usd`. *Ch 7, 31.*

**USDZ** — Zip **package** (STORE / compress_type **0**) of USD + images + audio. *Ch 31.*

**Usd** — Composed scene API (`Usd.Stage`, `Usd.Prim`) built on Sdf + Pcp. *Ch 8.*

**`usdcat`** — CLI convert/print; **not** in usd-core; stand-in `Layer.Export` / `ExportToString`. *Ch 31.*

**`usdchecker`** — CLI validator (UsdValidation since 26.03); **not** in usd-core. *Ch 30.*

**`usdGenSchema`** — Generates schema code/`plugInfo.json`; **not** on PATH in usd-core. *Ch 37.*

**UsdGeom** — Geometry schemas (Xform, Mesh, Camera, Imageable, Boundable). *Ch 39.*

**UsdLux** — Light schemas; attributes under `inputs:`. *Ch 41.*

**UsdPhysics** — Physics APIs (e.g. `CollisionAPI.Apply`); present on this wheel. *Ch 35.*

**UsdPreviewSurface** — Standard lookdev shader id. *Ch 40.*

**UsdShade** — Materials, shaders, connections, bindings. *Ch 40.*

**UsdUtils** — Pipeline helpers: deps, flatten layer stack, USDZ, localize, coalescing delegate. *Ch 32–34.*

**UsdValidation** — Validator framework (`ValidationRegistry`); `ComplianceChecker` is **gone**. *Ch 30.*

**`usdview`** — Reference viewer; not in usd-core. *Ch 41.*

**`usdzip`** — CLI packager; stand-in `CreateNewUsdzPackage`. *Ch 31.*

## V

**Value resolution** — Picking the composed value of one field at one time (samples → default → fallback). *Ch 21.*

**Variant set** — Named switch (`lod`, `color`) with named variants. *Ch 18.*

**Variant selection** — Which variant is chosen; empty selection → variant opinions not composed; empty `GetVariantEditContext` authors **local**. *Ch 18.*

**Vt** — Value-type arrays (`Vt.Vec3fArray`). *Ch 9.*

## W

**Warning (Tf)** — Non-fatal diagnostic (`Tf.Warn`); composition failures often arrive this way. *Ch 43.*

**Working set** — Payloads currently loaded for the task. *Ch 17, 26.*

**Work / publish / pin** — Editable work layers; immutable published cache; shot pins a versioned id. *Ch 32.*

## X

**Xform / Xformable** — Transform prim / schema; ops listed in `xformOpOrder`. *Ch 39.*

## Z

**ZIP_STORED** — Uncompressed zip method (0) required for USDZ. *Ch 31.*
