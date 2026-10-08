# Mock Exam 2 — Answer Key

**Original practice exam. Not actual NVIDIA exam content.**

Paper: `mock-exams/mock02_paper.md`. Verified against **USD 26.08** (`usd-core` 26.8).

Scoring: 1 point per question (multiple-select must match **all** correct letters). Total **65**. This book’s Mock 2 review bar is **≥ 75% overall (49/65)** and no domain under 60%. NVIDIA does not publish a passing score.

---

## Score sheet

| Domain | Q IDs | /n | Your score | % |
|--------|-------|----|------------|---|
| Composition (COMP) | 001, 004, 009, 012, 016, 020, 024, 028, 032, 036, 040, 044, 049, 053, 057 | /15 | | |
| Data Exchange (DE) | 003, 011, 021, 030, 039, 046, 054, 058, 061, 064 | /10 | | |
| Pipeline Development (PD) | 006, 013, 022, 027, 035, 043, 051, 059, 065 | /9 | | |
| Data Modeling (DM) | 002, 010, 017, 025, 033, 041, 050, 060 | /8 | | |
| Debugging (DBG) | 008, 019, 029, 038, 045, 055, 063 | /7 | | |
| Content Aggregation (CA) | 005, 015, 023, 031, 042, 052, 062 | /7 | | |
| Visualization (VIS) | 007, 018, 026, 037, 047 | /5 | | |
| Customizing USD (CUST) | 014, 034, 048, 056 | /4 | | |
| **Total** | M2-001–M2-065 | **/65** | | |

Copy weakest domains into `00_MASTER_PLAN.md` §9 before Mock 3.

---

## Answers

**M2-001 — Answer: B.** Obj 1.5. Verified: first sublayer `6`; after `MuteLayer` of that identifier, composed `length` is **15**. Mute removes that layer from the stack; it does not average or invalidate the prim. Review: Ch 15.

**M2-002 — Answer: B.** Obj 5.4. A missing path is a null prim: `bool`/`IsValid` are **False**. `IsDefined()` on a null prim **raises `RuntimeError`**. Do not write `if prim.IsDefined()` without `if prim` first. Review: Ch 4, Ch 8.

**M2-003 — Answer: A, B.** Obj 4.3. Verified: `"2ball"` → `"_ball"`; `"Pier-Dock"` → `"Pier_Dock"`. Leading digits get an underscore prefix; hyphens become underscores. Review: Ch 4, Ch 29.

**M2-004 — Answer: B.** Obj 1.1. Verified: local `radius = 3` beats the selected variant’s `11`. Local is stronger than VariantSets in LIVERPS. Review: Ch 18, Ch 21.

**M2-005 — Answer: B.** Obj 2.1. Verified: **explicit** `ListPositionFrontOfPrependList` puts Tree at index 0. Default `AddTarget` on 26.08 left Bush at 0 (`[Bush, Tree]`). `BackOfAppendList` appends (keeps 0). Review: Ch 25.

**M2-006 — Answer: A, C.** Obj 7.5. Naive `Resolve("./…")` is cwd; composition anchors to the layer. `ComputeAbsolutePath` / `CreateIdentifier` is the layer-relative check. `AnchorRelativePath` is **gone**. `./` is not a search-path lookup. Review: Ch 33.

**M2-007 — Answer: C.** Obj 8.2. Verified: `2 * 2**3 = 16`. Brightness scales as intensity × 2^exposure. Review: Ch 41.

**M2-008 — Answer: B.** Obj 6.2. Verified: `GetPropertyStack` is **strongest first** (`paint.usda` 6, then `layout.usda` 15). Review: Ch 22, Ch 42.

**M2-009 — Answer: B.** Obj 1.8. Verified: a **stronger** layer’s `delete references = @./skiff_a.usda@` drops the prepend; remaining append `skiff_b` gives **11**. Same-layer delete+prepend of the same item does **not** remove it — the delete must win from a stronger list-op. Review: Ch 14, Ch 16.

**M2-010 — Answer: B.** Obj 5.1 / 8.1. Verified: `FindPrimvarWithInheritance("displayColor")` finds `/P.primvars:displayColor`. There is no `GetDisplayColor` on MaterialBindingAPI. Review: Ch 11.

**M2-011 — Answer: B.** Obj 4.6. Verified: unresolved list contains **`gone.jpg`**; `wood.png` is in **assets**, not unresolved. Review: Ch 32, Ch 42.

**M2-012 — Answer: C.** Obj 1.7. Verified: empty selection + `GetVariantEditContext()` authors a **local** `custom double mark = 7`, not inside `red`/`green`. Review: Ch 18.

**M2-013 — Answer: B.** Obj 7.2. Extract is one-file `(sublayers, refs+assets, payloads)`. Compute is the closure 3-tuple. Review: Ch 32.

**M2-014 — Answer: B.** Obj 3.4. New Gprim → `UsdTyped` (typically via `UsdGeomGprim`). Non-destructive bundled properties → `UsdAPISchemaBase`. There is no `UsdPhysicsBase` for this. Review: Ch 6, Ch 37.

**M2-015 — Answer: A, D.** Obj 2.3. `invisibleIds` masks drawing; `GetInstanceCount()` **does not shrink**. Do not rewrite topology every frame or deactivate the whole instancer to hide one id. Review: Ch 25.

**M2-016 — Answer: B.** Obj 1.4. Verified: `GetEditTargetForLocalLayer` on a sublayer with `offset = 10` stores `Set(..., 20)` at **t=10**. A bare `Usd.EditTarget(anim)` stores 20. Review: Ch 15, Lab 19.

**M2-017 — Answer: C.** Obj 5.6. Verified: Mesh `subdivisionScheme` fallback is **`catmullClark`**. Review: Ch 13.

**M2-018 — Answer: A, B.** Obj 8.2. Verified: DistantLight **HasAPI LightAPI** without Apply; **ShadowAPI** (and ShapingAPI) need `Apply`. Review: Ch 41.

**M2-019 — Answer: B.** Obj 6.3. Verified warning: unresolved reference prim path `...@nodef.usda@<defaultPrim>`. The layer **opens**; defaultPrim is missing. That is not `InvalidAssetPath`. Review: Ch 16, Ch 42.

**M2-020 — Answer: B.** Obj 1.3. Verified: `LoadNone` still loads **references**; **payloads** stay unloaded. `OpenMasked` is a different API (population mask). Review: Ch 17.

**M2-021 — Answer: A, B.** Obj 4.7. `Flatten()` **bakes** references and sublayer opinions into one layer. FlattenLayerStack is the API that **keeps** references and drops sublayers (C describes FLS, not Flatten). Review: Ch 34.

**M2-022 — Answer: B.** Obj 7.4. Verified: anonymous layer not in the local stack → `Tf.ErrorException`. Review: Ch 15, Lab 19.

**M2-023 — Answer: A.** Obj 2.4. Verified: typeless `def "Dock"` is defined, type `''`. `over "Jetty"` with no defining spec: `IsDefined()` **False**, `bool(prim)` **True** (not a null prim). Null missing paths are `bool` False. Review: Ch 20.

**M2-024 — Answer: B.** Obj 1.8. Verified: local `over "Globe" { radius = 4 }` on the referencing prim wins over the asset’s 1. Review: Ch 16, Ch 20.

**M2-025 — Answer: B.** Obj 5.2. Verified: indexed primvar — 2 stored colors, 4 indices. Review: Ch 11.

**M2-026 — Answer: A.** Obj 8.4. `UsdPrimvarReader_float2` + `st` → `UsdUVTexture` → PreviewSurface. `UsdMtlx` is not in usd-core. Review: Ch 40.

**M2-027 — Answer: B.** Obj 7.3. FlattenLayerStack collapses sublayers and **keeps references**. Flatten bakes references. Review: Ch 34.

**M2-028 — Answer: B.** Obj 1.2. `Open(..., mask=)` is not the 26.08 API. Use `OpenMasked` + `StagePopulationMask`. Review: Ch 17, Ch 44.

**M2-029 — Answer: B.** Obj 6.1. `DefinePrim` of a **new** child inside a live `ChangeBlock` can raise `Tf.ErrorException`. Review: Ch 34, Ch 44.

**M2-030 — Answer: B.** Obj 4.2. Verified: `from pxr import UsdMtlx` → **ImportError**. Mapping is still an exam topic; the plugin is not in this wheel. Review: Ch 27, Ch 40.

**M2-031 — Answer: B.** Obj 2.1. Verified: `[Bush, Rock, Tree]`. Bush prepended; Tree **appended**; default `AddTarget(Rock)` landed in the prepend list **after** Bush (not at front). Do not assume default is `FrontOfPrependList` on 26.08. Review: Ch 25.

**M2-032 — Answer: A, B.** Obj 1.6. Two-step: stack/list-ops first, then LIVERPS. Specializes are weakest (C false). Clips are not a LIVERPS letter (D). Review: Ch 21.

**M2-033 — Answer: B.** Obj 5.5. Verified: child `Get()` is **`inherited`**; `ComputeVisibility()` walks parents → **`invisible`**. Review: Ch 13.

**M2-034 — Answer: B.** Obj 3.1. Plugin ABI must match the USD the process loaded. Review: Ch 35, Ch 36.

**M2-035 — Answer: B.** Obj 7.6. `GetCustomDataByKey("show")`. `GetMetadata("show")` is not that dictionary. Review: Ch 12.

**M2-036 — Answer: B.** Obj 1.9. Verified: no defaultPrim → first root prim name (`Ferry`). Empty layer → `''`. Review: Ch 16, Ch 32.

**M2-037 — Answer: B.** Obj 8.3. `strongerThanDescendants` makes this prim’s bind beat descendant binds (including subsets). `weakerThanDescendants` is the reverse. Review: Ch 40.

**M2-038 — Answer: A, B.** Obj 6.5. Coalescing delegate **before** Open; `USD_CHANGES` for change debug. `Tokens.Z` and `GetMaster` do not exist as diagnostic tools. Review: Ch 43.

**M2-039 — Answer: A, C.** Obj 4.4. Sanitize identifiers; keep the original in `customData`; author units/upAxis and document no auto-convert. `2ball` is **not** a legal prim name. Review: Ch 29.

**M2-040 — Answer: B.** Obj 1.1. Verified pattern: references beat specializes → composed **2**. (Inherits would have won — that was Mock 1’s different stem.) Review: Ch 19, Ch 21.

**M2-041 — Answer: B.** Obj 5.3. Documentation metadata vs `customData` dictionary. Review: Ch 12.

**M2-042 — Answer: B.** Obj 2.2. Instance-root primvars/inherits. Proxy `OverridePrim` raises. Editing the prototype tints **every** instance. Review: Ch 24.

**M2-043 — Answer: B.** Obj 7.7. `PXR_PLUGINPATH_NAME` is the env default; `Plug.Registry.RegisterPlugins` still works at runtime (Ch 36 labs). Review: Ch 36.

**M2-044 — Answer: B.** Obj 1.7. Verified: `GetNames()` → `['look']`; `GetVariantNames()` → `['green', 'red']`. Review: Ch 18.

**M2-045 — Answer: B.** Obj 6.4. Imageable purpose `guide` is hidden when the viewer mask is default+render only. Review: Ch 42.

**M2-046 — Answer: A, B.** Obj 4.8. `.usd` formatId follows the **extension**; bytes may still be USDA. formatId does not flip to `usda` just because the magic is `#usda`. Review: Ch 7, Ch 31.

**M2-047 — Answer: A, B.** Obj 8.2. Verified: enable **False**, Kelvin fallback **6500** (ignored until enable). Review: Ch 41.

**M2-048 — Answer: B.** Obj 3.8. Ar resolver ≠ SceneIndex. Imaging plugins need an imaging build; usd-core has neither Hd nor UsdImaging. Review: Ch 38.

**M2-049 — Answer: A, B.** Obj 1.5. `SetEditTarget` / `EditContext` on a department layer **in the local stack**. Creating a second root that is not sublayered (C) and `GetPrototype()` (D) do not switch edit targets. Review: Ch 15.

**M2-050 — Answer: B.** Obj 5.2. Verified: linear from t=2 `(0,0,0)` to t=8 `(6,0,0)`; t=4 is 1/3 of the span → **`(2, 0, 0)`**. Review: Ch 10.

**M2-051 — Answer: B.** Obj 7.1. usd-core has **no** `usdcat`. `Sdf.Layer.Export` is the stand-in. Review: Ch 31.

**M2-052 — Answer: B, C.** Obj 2.4. Verified: `IsA(Boundable)` True, `IsA(Gprim)` **False**. Review: Ch 25.

**M2-053 — Answer: A, B.** Obj 1.11. Payload geo; department sublayers; pin publish. Flatten-as-daily-format throws composition away. Review: Ch 22.

**M2-054 — Answer: B.** Obj 4.5. Custom (namespaced) attributes persist without a downstream schema plugin. Review: Ch 29, Ch 37.

**M2-055 — Answer: B.** Obj 6.2. Same-field local opinions still rank by **layer-stack strength**. A stronger local hides a weaker over even if both are “local.” Review: Ch 21, Ch 42.

**M2-056 — Answer: A, B.** Obj 3.2. pip usd-core ≠ a full imaging/MaterialX build. Review: Ch 35.

**M2-057 — Answer: B.** Obj 1.10. Instance-root (or de-instance that one root). No `GetMaster`. Review: Ch 24.

**M2-058 — Answer: B.** Obj 4.1. Bake/choose the working set; glTF has no LIVERPS/payloads/variants. Review: Ch 27.

**M2-059 — Answer: A, B.** Obj 7.8. Typed mapping + working-set load rules. No UsdMtlx, no GetMaster. Review: Ch 29, Ch 35.

**M2-060 — Answer: B.** Obj 5.5. Verified: `AddTranslateOp` authors `xformOpOrder = ['xformOp:translate']`. Review: Ch 39.

**M2-061 — Answer: B.** Obj 4.3. Verified: USDZ `compress_type` **0** (`ZIP_STORED`). Review: Ch 31.

**M2-062 — Answer: B.** Obj 2.5. ModelAPI draw modes are for **models** (component/assembly) as cheap viz. Review: Ch 23, Ch 44.

**M2-063 — Answer: B.** Obj 6.5. Malloc tagging often compiled out of the pip wheel (0 bytes). Use Trace. Review: Ch 43.

**M2-064 — Answer: A, B.** Obj 4.7. `defaultPrim`, `metersPerUnit`, `upAxis`. No Registry.Register in USDA, no GetMaster metadata. Review: Ch 28.

**M2-065 — Answer: B.** Obj 7.2. Compute walks the **closure**. Extract is one file. Review: Ch 32.

---

## Domain repair

| If weak in | Re-read | Re-lab |
|------------|---------|--------|
| COMP | Ch 14–22 | Labs 13–21 |
| DE | Ch 27–31 | Labs 25–28 |
| PD | Ch 32–35 | Labs 29–30 |
| DM | Ch 8–13 | Labs 08–12 |
| DBG | Ch 42–44 | Labs 09, 30, 36 |
| CA | Ch 23–26 | Labs 22–24 |
| VIS | Ch 39–41 | Labs 33–35 |
| CUST | Ch 36–38 | Lab 31 |
