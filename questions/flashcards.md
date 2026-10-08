# Flashcards

**Original study cards.** Not NVIDIA exam content. Cut on the table grid: Front / Back. Backs stay ≤ 30 words. Verified against USD 26.08.

Target: ≥ 160. This file currently holds **FC-001–FC-180** (complete, ≥160).

---

## Fundamentals (FC-001–FC-020)

| # | Front | Back |
|---|-------|------|
| FC-001 | What is OpenUSD besides a file type? | A scene-description system: layers, composition, schemas, APIs. Formats are one piece. |
| FC-002 | Python package name? | `pxr` — `from pxr import Usd`. |
| FC-003 | `Usd.GetVersion()` on this book? | `(0, 26, 8)` — OpenUSD 26.08 / usd-core 26.8. |
| FC-004 | Stage vs layer? | Stage = composed live scene. Layer = one opinion container (file or anonymous). |
| FC-005 | CreateInMemory fallbacks? | `upAxis` Y, `metersPerUnit` 0.01. |
| FC-006 | usdcat on usd-core? | Missing. Use `ExportToString()` / `Layer.Export`. |
| FC-007 | First-listed sublayer? | Stronger. Last-listed-wins is a CSS myth. |
| FC-008 | Session vs root Save? | Session opinions are not written into the root file. |
| FC-009 | `def` / `over` / `class`? | Define / overlay (does not define alone) / abstract class. |
| FC-010 | Attribute vs relationship? | Values vs prim/property targets. |
| FC-011 | `primvars:` `xformOp:` `inputs:`? | Property namespaces. |
| FC-012 | Five model kinds? | model, group, assembly, component, subcomponent. |
| FC-013 | Typed vs API schema? | IsA (Cube) vs Apply (`MaterialBindingAPI`). |
| FC-014 | `.usda` / `.usdc` / `.usd` / `.usdz`? | Text / crate / either (magic) / zip package. |
| FC-015 | `CreateNew("x.usd")` magic + formatId? | Magic `PXR-USDC`; formatId `usd`. |
| FC-016 | USDA first line? | `#usda 1.0` |
| FC-017 | `GetPrimAtPath` missing? | Invalid handle; `bool(prim)` False; does not raise. |
| FC-018 | Pcp in the stack? | Composition (prim index / opinions). |
| FC-019 | Hydra? | Imaging / render delegates — not in usd-core. |
| FC-020 | `defaultPrim` lives where? | Layer metadata, not on each prim. |

---

## Composition (FC-021–FC-060)

| # | Front | Back |
|---|-------|------|
| FC-021 | LIVERPS? | Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes. |
| FC-022 | LIVERPS letter E? | rElocates. Older talks said LIVRPS. |
| FC-023 | Local vs reference? | Local wins (L > R). |
| FC-024 | Inherit vs reference? | I > R. |
| FC-025 | Reference vs specialize? | R > S. Specialize is weakest. |
| FC-026 | Inherit vs variant? | I > V. |
| FC-027 | Local vs variant? | L > V — “variant did nothing.” |
| FC-028 | Prepend vs append refs? | Prepend is stronger. |
| FC-029 | Explicit `references = [...]`? | Replaces weaker list-ops. |
| FC-030 | Sublayer vs reference? | Sublayer: same namespace. Reference: bring in at a path. |
| FC-031 | Payload vs reference? | Payload weaker and unloadable. |
| FC-032 | `LoadNone` still loads? | References yes; payloads no. |
| FC-033 | Missing `defaultPrim` error? | `UnresolvedPrimPath`. Missing file: `InvalidAssetPath`. |
| FC-034 | Layer offset formula? | `stageTime = offset + scale * layerTime`. |
| FC-035 | Offset 10, samples 0 and 10? | Composed times 10 and 20. |
| FC-036 | Defaults and offsets? | Offsets remap samples, not the default. |
| FC-037 | `GetEditTargetForLocalLayer` offset 10, Set at 20? | Stores at layer time 10. Bare EditTarget stores 20. |
| FC-038 | Anonymous edit target? | `Tf.ErrorException` — not in local LayerStack. |
| FC-039 | When variants? | Named discrete options (look, LOD). Not continuous sliders. |
| FC-040 | Empty `GetVariantEditContext`? | Writes **local** opinions; fill the variant only after `SetVariantSelection`. |
| FC-041 | `GetVariantNames` vs `GetNames`? | Names on `VariantSet`; `GetNames` is on `VariantSets`. |
| FC-042 | Flatten vs FlattenLayerStack? | Flatten bakes arcs. FLS keeps references, bakes sublayers. |
| FC-043 | `instanceable` where? | On the **referencing** prim (instance root). |
| FC-044 | Prototype API 26.08? | `GetPrototype()`. `GetMaster` is gone. |
| FC-045 | Nested over on instance proxy? | `Tf.ErrorException` / ignored in USDA. De-instance or author the root. |
| FC-046 | Traverse and instances? | Skips proxy children; roots still listed. |
| FC-047 | PointInstancer hide one? | `InvisId(id, time)` / `invisibleIds`. Count unchanged. |
| FC-048 | `AddTarget` default on stronger layer? | **Prepends** — shifts protoIndices. Use `BackOfAppendList`. |
| FC-049 | PI: Gprim or Boundable? | Boundable, not Gprim. |
| FC-050 | Mute a stronger sublayer? | Its opinions vanish; weaker wins. |
| FC-051 | Relocate source over? | Ignored. Author at the **destination**. |
| FC-052 | `Open` with a mask? | Use `OpenMasked`, not `Open(path, mask=)`. |
| FC-053 | Stronger default vs weaker samples? | Default wins at all times; samples `[]`. |
| FC-054 | `Get()` samples only, no default? | `None`. |
| FC-055 | Work vs publish vs pin? | Edit work; pin immutable publish folders, not `.../work/`. |
| FC-056 | ComputeAllDependencies 3-tuple? | `(layers, assets, unresolved)` recursive. |
| FC-057 | ExtractExternalReferences? | One file: `(sublayers, refs+assets, payloads)`. |
| FC-058 | Ar.GetResolver() type? | Facade `Resolver`. Underlying often `DefaultResolver`. |
| FC-059 | `AnchorRelativePath` 26.08? | Gone. `CreateIdentifier` + anchor, or `ComputeAbsolutePath`. |
| FC-060 | ChangeBlock delays? | **Notices**, not writes. New-child `DefinePrim` can raise. |

---

## Data Modeling (FC-061–FC-080)

| # | Front | Back |
|---|-------|------|
| FC-061 | Mesh `points` type? | `point3f[]` — point role, not `color3f`. |
| FC-062 | Texture filename type? | `asset` (`Sdf.AssetPath`) so Ar can resolve it. |
| FC-063 | `purpose` / `subdivisionScheme` type? | `token`, not freeform `string`. |
| FC-064 | `Get()` with samples only? | `None`. Defaults and samples are separate. |
| FC-065 | Linear `Get(6)` samples 1→11 of 0…10? | `(5,0,0)`. Held keeps `(0,0,0)`. |
| FC-066 | Default interpolation? | `Usd.InterpolationTypeLinear`. |
| FC-067 | What is a primvar? | `primvars:` attribute plus interpolation metadata. |
| FC-068 | Add `displayColor` how? | `UsdGeom.PrimvarsAPI.CreatePrimvar`. |
| FC-069 | Per-face IDs interpolation? | `uniform`. Seams/UVs: `faceVarying`. |
| FC-070 | Indexing vs interpolation? | Independent. Indexing is a palette. |
| FC-071 | `primvars:st` namespace? | `primvars`. Mesh `points` namespace is empty. |
| FC-072 | Child inherits parent displayColor? | `FindPrimvarWithInheritance`. |
| FC-073 | Points changed — extent? | Does not auto-update. Compute then `Set`. |
| FC-074 | `ComputeExtentFromPlugins` writes? | No — it **returns**; you `Set` extent. |
| FC-075 | Triangle extent (0,0,0)(1,0,0)(0,1,0)? | `[(0,0,0), (1,1,0)]`. |
| FC-076 | CAD looks “melted”? | Fallback `subdivisionScheme` is `catmullClark`. Set `none`. |
| FC-077 | `purpose = guide` missing in view? | Default purpose pass omits `guide`/`proxy`. |
| FC-078 | Visibility fallback? | `inherited`. `ComputeVisibility` walks parents. |
| FC-079 | Cube size / Sphere radius fallbacks? | 2.0 and 1.0. |
| FC-080 | `GetCustomDataByKey` why? | `GetCustomData()` may inject `userDocBrief`. |

---

## Data Exchange (FC-081–FC-095)

| # | Front | Back |
|---|-------|------|
| FC-081 | USDA vs USDC trade-off? | Text: readable/mergeable. Crate: faster, smaller, not line-diff friendly. |
| FC-082 | Detect `.usd` encoding? | Magic: `#usda`, `PXR-USDC`, or `PK`. formatId follows extension. |
| FC-083 | `MakeValidIdentifier("Crate Box")`? | `Crate_Box`. `"2ball"` → `_ball`. |
| FC-084 | USD auto-converts units on reference? | **No.** Scale factor `asset_mpu / shot_mpu`; often `rotateX(-90)`. |
| FC-085 | OBJ `f 1 2 3` → indices? | `[0, 1, 2]` — OBJ is 1-based. |
| FC-086 | 100 cm point → meters? | `(1,0,0)` with `metersPerUnit = 1`. |
| FC-087 | `ComplianceChecker` 26.08? | **Gone.** Use `pxr.UsdValidation`. |
| FC-088 | Geom vs core StageMetadataChecker? | Geom: upAxis/meters. Core: `defaultPrim`. |
| FC-089 | glTF faces? | Triangulate. UV: `v_gltf = 1 - v_usd`. Meters, +Y. |
| FC-090 | PreviewSurface → glTF? | `pbrMetallicRoughness`. |
| FC-091 | USDA ↔ USDC lossless? | Yes. USD → glTF is lossy (no live variants). |
| FC-092 | Bind without Apply? | Writes `material:binding`; `HasAPI` False. |
| FC-093 | ComputeAllDependencies shape? | 3-tuple: layers, assets, unresolved. |
| FC-094 | UsdMtlx on usd-core? | `ImportError`. Need a full build. |
| FC-095 | USDZ zip method here? | STORE, `compress_type` 0. |

---

## Content Aggregation (FC-096–FC-110)

| # | Front | Back |
|---|-------|------|
| FC-096 | Native instance prototype API? | `GetPrototype()` → `/__Prototype_N`. No `GetMaster`. |
| FC-097 | Where `instanceable`? | Referencing prim (instance root), not every mesh. |
| FC-098 | Edit nested Seat on one instance? | De-instance that root, or primvar on the **root**. Not the proxy. |
| FC-099 | Proxy `OverridePrim`? | `Tf.ErrorException`. |
| FC-100 | Traverse instance children? | Skipped. `GetPrimAtPath` still finds proxies. |
| FC-101 | PointInstancer required fields? | `prototypes`, `protoIndices`, `positions`. Count = len(indices). |
| FC-102 | Hide one PI instance? | `InvisId(id, time)`. Count stays the same. |
| FC-103 | `AddTarget` default (stronger layer)? | Prepends — shifts indices. Pass `BackOfAppendList`. |
| FC-104 | PI Gprim? | No. It **is** Boundable. |
| FC-105 | Prototypes under `class`? | Traverse skips class descendants. |
| FC-106 | Mug kind component, IsComponent False? | Un-kinded ancestor broke the model chain. |
| FC-107 | assembly is-a? | `group` (and thus `model`). |
| FC-108 | Source Seat Set(3) on instances? | Broadcasts to every instance. Intended. |
| FC-109 | Unique variant on one instance? | Often a **second** prototype. |
| FC-110 | 80k seats vs one booth? | PI or native instances for seats; ordinary ref for the booth. |

---

## Visualization (FC-111–FC-120)

| # | Front | Back |
|---|-------|------|
| FC-111 | UsdPreviewSurface is a prim type? | No — Shader `info:id` string. |
| FC-112 | Bind sequence 26.08? | `MaterialBindingAPI.Apply` then `Bind`. |
| FC-113 | `ComputeSurfaceSource` type? | Tuple length 3, not a single shader. |
| FC-114 | PS auto-reads displayColor? | **No.** Connect `UsdPrimvarReader_float3` (`varname` token `displayColor`). |
| FC-115 | UV texture chain? | `UsdPrimvarReader_float2` (`st`) → `UsdUVTexture` → PS. |
| FC-116 | Direct bind relationship name? | `material:binding`. |
| FC-117 | Shader input namespace? | `inputs:diffuseColor`. |
| FC-118 | Binding purposes? | `preview` vs `full` (and all-purpose). |
| FC-119 | Face-level material? | `UsdGeom.Subset` + binding API. |
| FC-120 | `ComputeBoundMaterial`? | Tuple: Material + winning relationship. |

---

## Pipeline Development (FC-121–FC-140)

| # | Front | Back |
|---|-------|------|
| FC-121 | Work vs publish? | Work is still edited. Publish is an immutable snapshot shots **pin**. |
| FC-122 | Pin `.../work/chair.usda`? | Wrong. Pin `.../v017/chair.usda`. |
| FC-123 | `Hero_v003` as defaultPrim? | Version belongs in the **folder**. Keep identifier stable. |
| FC-124 | `assetInfo['identifier']`? | Catalog key — almost never rename per publish. |
| FC-125 | Extract vs Compute? | Extract = one file. Compute = recursive snowball. |
| FC-126 | Extract second list? | References **and** asset-valued attributes (textures). |
| FC-127 | Non-empty unresolved? | Fail the publish. |
| FC-128 | Unresolved path spelling? | Often absolutized — compare basenames. |
| FC-129 | `GetModelNameFromRootLayer`? | Reads `defaultPrim` (falls back to a root prim if unset). |
| FC-130 | Git vs layer stack? | Git versions work files. Stacks are not VCS. |
| FC-131 | `./tex` Resolve from wrong cwd? | False. Composition anchors to the **layer**. |
| FC-132 | Search path and `./`? | `./` is **not** a search-path lookup. |
| FC-133 | `@chair.usda@` no context? | `ErrorInvalidAssetPath`. Pass `pathResolverContext`. |
| FC-134 | Custom resolver load? | `plugInfo.json` + `PXR_PLUGINPATH_NAME` before init; match ABI. |
| FC-135 | `customData` vs `assetInfo`? | Studio bag vs catalog fields (`identifier`, `version`). |
| FC-136 | Flatten strips owner names? | **No.** Clear `customData` yourself. Absolutized paths leak. |
| FC-137 | Artist asset paths with a studio resolver? | Identifiers/URIs, not `/mnt/show/...`. |
| FC-138 | Context-dependent `tex/wood.png`? | True. `./tex/wood.png` is False. |
| FC-139 | Exporter hooks when? | Before Save: defaultPrim, units, upAxis, kind, identifier. |
| FC-140 | Plugin after `import pxr`? | Often **too late**. Set plugin path first. |

---

## Debugging (FC-141–FC-165)

| # | Front | Back |
|---|-------|------|
| FC-141 | ChangeBlock 3× create+set? | 6 notices without; 1 inside a block (Sdf specs). |
| FC-142 | Sphere.Define new child in block? | Can raise `Tf.ErrorException`. Use `Sdf.PrimSpec`. |
| FC-143 | Unregister ObjectsChanged? | `listener.Revoke()`. |
| FC-144 | Opinion not showing — first tool? | `GetPrimStack` / `GetPropertyStack` (strongest first). |
| FC-145 | CreateAttribute then Set notices? | Resync `/W.a`, then info-only `/W.a`. |
| FC-146 | Coalescing delegate class? | `UsdUtils.CoalescingDiagnosticDelegate` — construct **before** Open. |
| FC-147 | `sourceFileName` in tests? | `os.path.basename` — may be a full path (`stage.cpp`). |
| FC-148 | Trace vs MallocTag? | Trace = time. MallocTag = bytes. |
| FC-149 | MallocTag bytes on usd-core? | `GetTotalBytes()` is **0** after Initialize. |
| FC-150 | Trace default enabled? | False. |
| FC-151 | Enable USD_CHANGES in-process? | `Tf.Debug.SetDebugSymbolsByName("USD_CHANGES", True)`. |
| FC-152 | Process-start debug env? | `TF_DEBUG=USD_CHANGES`. |
| FC-153 | Unknown TfDebug name? | Empty list, no exception. |
| FC-154 | Missing file vs missing prim path? | `InvalidAssetPath` vs `UnresolvedPrimPath`. |
| FC-155 | LoadNone vs OpenMasked? | LoadNone still loads **refs**. Mask omits subtrees. |
| FC-156 | Stale extent visual? | Wrong culling/bounds after scaling points. |
| FC-157 | Z-up asset in Y-up shot? | Sideways/tiny until rotateX + scale. USD does not convert. |
| FC-158 | `USD_CHANGES` description? | `"USD change processing"`. |
| FC-159 | Initialize() False, IsInitialized True? | Normal on this wheel; still 0 bytes. |
| FC-160 | Eight-step opinion debug? | Mute, stack, LIVERPS, variant, instance, relocate, edit target, usdview LayerStack. |
| FC-161 | Relocate source opinion warning? | Invalid opinion at relocation source — ignored. |
| FC-162 | PI `InvisId` needs? | `(id, time)` — time is required. |
| FC-163 | Null prim `IsDefined()`? | Raises `RuntimeError`. Use `bool(prim)` / `IsValid()`. |
| FC-164 | Tokens.Z? | Missing. Use `UsdGeom.Tokens.z` → `"Z"`. |
| FC-165 | DistantLight intensity fallback? | 50000. Sphere light 1. Brightness ∝ intensity × 2^exposure. |

---

## Customizing USD (FC-166–FC-180)

| # | Front | Back |
|---|-------|------|
| FC-166 | Plugin vs DCC USD version? | Rebuild the plugin against **that** USD. ABI mismatch fails. |
| FC-167 | `Kind.Registry.Register`? | **Does not exist** in Python 26.08. Use `plugInfo.json`. |
| FC-168 | `SetKind("door")`? | `GetKind` is `door`; `IsComponent` becomes False. |
| FC-169 | `usdGenSchema` on usd-core? | Not on PATH. |
| FC-170 | Parse `schema.usda` registers Door? | **No.** Parse ≠ register. Needs a plugin. |
| FC-171 | Codeless schema still needs? | Generated USDA + `plugInfo.json`. Skips C++ wrappers only. |
| FC-172 | Cube registered fallback size? | 2.0. `IsConcrete` True. |
| FC-173 | MaterialBindingAPI schema kind? | Applied API — `Apply` then Bind. |
| FC-174 | Custom kind when? | New taxonomy the five built-ins cannot express. |
| FC-175 | Typed schema inherit in schema.usda? | `inherits = </Typed>`. API: `</APISchemaBase>`. |
| FC-176 | GLOBAL `libraryName`? | Schema library name for usdGenSchema/plugins. |
| FC-177 | SceneIndex on usd-core? | No `Hd`/`UsdImaging`. Needs an imaging build. |
| FC-178 | Procedural AssetResolver (Obj 3.8)? | `Resolve`/`OpenAsset` returns generated bytes, not only disk files. |
| FC-179 | Hide default plugins with PXR_PLUGINPATH? | Prepend studio **and** keep the USD prefix. |
| FC-180 | `PXR_BUILD_MATERIALX_PLUGIN`? | CMake flag for a source build — not in usd-core. |

---

*Flashcards complete: FC-001–FC-180 (≥160).*


