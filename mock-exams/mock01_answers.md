# Mock Exam 1 — Answer Key

**Original practice exam. Not actual NVIDIA exam content.**

Paper: `mock-exams/mock01_paper.md`. Verified against **USD 26.08** (`usd-core` 26.8). USDA/Python items were re-run before this key was written.

Scoring: 1 point per question (multiple-select must match **all** correct letters). Total **65**. This book’s Mock 1 review bar is **≥ 70% overall (46/65)** and no domain under 50%. NVIDIA does not publish a passing score.

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
| **Total** | M1-001–M1-065 | **/65** | | |

Copy the weakest domains into `00_MASTER_PLAN.md` §9 before Mock 2.

---

## Answers

**M1-001 — Answer: B.** Obj 1.6. LIVERPS: Local, Inherits, VariantSets, rElocates, References, Payloads, **Specializes** (weakest). A referenced `reach` beats a specializes class. A is the class-is-always-strong myth. C: USD does not average. D: specializes are not next to local. Review: Ch 14, Ch 21.

**M1-002 — Answer: D.** Obj 5.2. `Get()` with no time argument reads the **default**. Samples-only attributes have no default, so `Get()` is `None` (not the first sample). A/B/C confuse default with time-sampled evaluation. Review: Ch 10.

**M1-003 — Answer: B.** Obj 4.3. USDA is UTF-8 text (Git-friendly). USDC crate is smaller/faster for the farm. A reverses the pair. C/D: USDZ is a ZIP package, not a department merge format. Review: Ch 7, Ch 31.

**M1-004 — Answer: B.** Obj 1.5. Verified: first sublayer in `subLayers` is strongest, so `height = 4`. Last-listed is weakest (A). No averaging (C). Two overs on the same field is normal composition (D). Review: Ch 15.

**M1-005 — Answer: A, C.** Obj 2.4. `GetPrototype()` is the 26.08 name. `GetMaster` **does not exist** on `Usd.Prim`. B/D invent APIs. Review: Ch 24.

**M1-006 — Answer: A.** Obj 7.2. Extract is a **one-file** split `(sublayers, refs+assets, payloads)`. Compute walks the **closure** `(layers, assets, unresolved)`. They are not aliases. Review: Ch 32.

**M1-007 — Answer: B.** Obj 8.3. Apply the API schema, then `Bind`. `Bind` without Apply can still write the relationship, but `HasAPI` stays false (A/C). There is no `Gprim.BindMaterial` (D). Review: Ch 40.

**M1-008 — Answer: B.** Obj 6.1. Lab 09: three `CreateAttribute().Set()` pairs → **6** notices; two Sdf specs inside `ChangeBlock` → **1**. The block coalesces change processing. C is the opposite: `DefinePrim` of a **new** child inside a live block can raise. Review: Ch 8, Ch 34, Ch 44.

**M1-009 — Answer: B.** Obj 1.1. Verified: inherit `7` beats referenced `2`. A reverses LIVERPS. C/D are invented. Review: Ch 19, Ch 21.

**M1-010 — Answer: C.** Obj 5.1 / 8.1. Vertex interpolation: one value per vertex → 4. Face interpolation would be 2 (B). FaceVarying would be 6 corners (D). Constant is 1 (A). Review: Ch 11.

**M1-011 — Answer: C.** Obj 4.3. `CreateNew("hero.usd")` writes crate bytes `PXR-USDC` but `formatId` is `usd` (the `.usd` plugin). B names formatId `usdc` (wrong for `.usd`). A is a `.usda` file. D is ZIP. Review: Ch 7, Ch 31.

**M1-012 — Answer: A, B.** Obj 1.3. References compose with the parent; payloads are the deferred working set (`LoadNone` leaves `/Heavy/Shade` out). Sublayers are the shot’s layer stack, not a per-prim unload switch (C). Specializes are a weak opinion arc, not “optional geo” (D). Review: Ch 16, Ch 17.

**M1-013 — Answer: B.** Obj 7.2. Work stays editable; publish is an immutable cache; the shot pins a versioned identifier. In-place overwrite of publish (A) and “pin = delete work” (C) break pipelines. Farm caches want USDC, not USDA diffs (D). Review: Ch 32.

**M1-014 — Answer: B.** Obj 3.3. `Kind.Registry.Register` **does not exist**. Kinds come from the kind plugin / `plugInfo.json`. Review: Ch 6, Ch 38.

**M1-015 — Answer: B.** Obj 2.3. Verified: `GetInstanceCount()` stays **3**; `invisibleIds` masks drawing, it does not shrink the count. Review: Ch 25.

**M1-016 — Answer: B.** Obj 1.4. Verified: `Sdf.LayerOffset(offset=10, scale=2)` maps layer times 0 and 10 to composed **10 and 30** (`offset + scale * layerTime`). Review: Ch 10, Ch 16.

**M1-017 — Answer: A, C.** Obj 5.6. Compute via `ComputeExtentFromPlugins`, then `Set` on `extent`. Keep `points` and `extent` in sync. Zero extent (B) and “delete and hope” (D) produce wrong bounds / warnings. Review: Ch 13.

**M1-018 — Answer: A, B.** Obj 8.2. Verified: Distant intensity fallback **50000**; Sphere **1**. Exposure fallback is `0`. Review: Ch 41.

**M1-019 — Answer: B.** Obj 6.3. Missing asset file → `InvalidAssetPath`. Opened layer but missing prim → `UnresolvedPrimPath`. A/D swap them. Review: Ch 42.

**M1-020 — Answer: C.** Obj 1.7. Verified: no selection → `binWidth.Get()` is `None` (the attribute is not even composed / not valid). Variants do not auto-pick first or last. (Trap: a **Cube** `size` would still show the schema fallback `2.0` with `HasAuthoredValue() False` — this stem used a custom double to avoid that.) Review: Ch 18.

**M1-021 — Answer: A, B.** Obj 4.7. Verified: `Flatten()` bakes references; `FlattenLayerStack` keeps references and drops sublayers. C reverses FLS. D is false. Review: Ch 34.

**M1-022 — Answer: B.** Obj 7.5. `Ar.GetResolver()` is the **Resolver** facade; `Ar.GetUnderlyingResolver()` is **DefaultResolver** on usd-core. `GetResolver()` is not itself DefaultResolver (C). Review: Ch 33.

**M1-023 — Answer: B.** Obj 2.4. Verified: `/Wagon` is an instance; `/Wagon/Body` is an instance proxy; `/Wagon/Seat` is **not** composed; `OverridePrim` on the proxy raises; `GetMaster` is gone. `Traverse` lists `/Wagon` but not the nested Seat. Review: Ch 24.

**M1-024 — Answer: B.** Obj 1.8. Verified: destination `/Bot/Arm` size **4**; the `over` at the **source** path `/Bot/Rig/Arm` is ignored (composition warning). Relocates are layer metadata. Review: Ch 20.

**M1-025 — Answer: B, C.** Obj 5.4. Verified: `Tokens.z` exists; `Tokens.Z` does **not**. Review: Ch 9, Ch 39.

**M1-026 — Answer: C.** Obj 8.4. Verified: `ComputeSurfaceSource()` is a tuple of **len 3** (even on an empty material). Review: Ch 40.

**M1-027 — Answer: B.** Obj 7.3. FlattenLayerStack collapses the **layer stack** (sublayers) and leaves references. `Flatten()` bakes references (A is backwards). Review: Ch 31, Ch 34.

**M1-028 — Answer: B.** Obj 1.3. Verified: `LoadNone` still loads **references** (`/Hero/Shade` true) and defers **payloads** (`/Heavy/Shade` false). Review: Ch 17.

**M1-029 — Answer: B.** Obj 6.1. Verified: `DefinePrim` of a brand-new child inside `Sdf.ChangeBlock` can raise `Tf.ErrorException`. Review: Ch 34, Ch 44.

**M1-030 — Answer: B.** Obj 4.3. Verified: USDZ members use `compress_type` **0** (`ZIP_STORED`). Review: Ch 31.

**M1-031 — Answer: B.** Obj 2.1. `Usd.Relationship.AddTarget` prepends by default (`ListPositionFrontOfPrependList`). Existing `protoIndices` of `0` silently retarget. Append a new proto with `Usd.ListPositionBackOfAppendList`. Review: Ch 25.

**M1-032 — Answer: B.** Obj 1.1. Verified: referenced `2` beats specializes `7`. M1-009 used **inherits** (which win); this stem uses **specializes** (which lose). Review: Ch 19, Ch 21.

**M1-033 — Answer: A.** Obj 5.2. Verified: stronger local **default** `9.0` hides weaker samples (`GetTimeSamples()` is `[]`). Samples do not automatically beat a stronger default. Review: Ch 10, Ch 21.

**M1-034 — Answer: B.** Obj 3.4. Opening `schema.usda` parses a layer; it does **not** register Usd schema types. Plugins + `Plug.Registry` / `PXR_PLUGINPATH_NAME` do. Review: Ch 37.

**M1-035 — Answer: A.** Obj 7.6. `customData` is the dictionary for producer keys renderers should ignore. Do not overload `kind`, `upAxis`, or displayColor. Review: Ch 12.

**M1-036 — Answer: B.** Obj 1.8. When an over “does nothing,” walk LIVERPS and the layer stack (mute, edit target, stronger local/inherit/variant). Do not reach for removed APIs. Review: Ch 22, Ch 42.

**M1-037 — Answer: A.** Obj 8.4. `UsdPrimvarReader_float3` with `inputs:varname = displayColor` feeds PreviewSurface diffuse. UVTexture reads `st` for textures, not displayColor. Review: Ch 40.

**M1-038 — Answer: A, B.** Obj 6.5. This pip wheel typically reports **0** malloc-tag bytes. Trace Collector/Reporter still works. Trace does not require UsdImaging to import. Review: Ch 43.

**M1-039 — Answer: A, C.** Obj 4.4. Validate identifiers and keep the original name in `customData`. Author units/upAxis and document that **referencing does not auto-convert**. Dropping `defaultPrim` (B) causes `UnresolvedPrimPath` on nameless references. Review: Ch 27, Ch 29.

**M1-040 — Answer: B.** Obj 1.1. Verified: prepended `r1` (`radius = 2`) beats appended `r2` (`8`). Review: Ch 14.

**M1-041 — Answer: B.** Obj 5.3. `customData` is a dictionary; `documentation` / `userDocBrief` are the human-readable metadata fields. Review: Ch 5, Ch 12.

**M1-042 — Answer: B.** Obj 2.4. Verified: `GetKind()` is `component` but `IsComponent()` is **False** because `/Clutter` is not a model — the model hierarchy is broken. Review: Ch 6, Ch 23.

**M1-043 — Answer: B.** Obj 7.4. Plugin ABI must match the USD the DCC loaded. `Usd.GetVersion() == (0, 26, 8)` describes this venv, not a free pass for older plugins. Review: Ch 35.

**M1-044 — Answer: B.** Obj 1.2. Use `Usd.Stage.OpenMasked` with a `StagePopulationMask`. `Open(path, mask=...)` is not the API (`LoadNone` is a load rule, not a mask). Review: Ch 17, Ch 44.

**M1-045 — Answer: A.** Obj 6.5. Install `UsdUtils.CoalescingDiagnosticDelegate` **before** `Open` so warnings group. Review: Ch 43.

**M1-046 — Answer: B.** Obj 4.5. Verified: USDA `rel material:binding` without `apiSchemas` → `HasAPI` **False**, `HasRelationship` **True**. Review: Ch 29, Ch 40.

**M1-047 — Answer: A, B.** Obj 8.3. `preview` is the lookdev purpose; empty `allPurpose` is the fallback. `weakerThanDescendants` lets **child** binds win, not the ancestor (C reversed). `physics` is not a required UsdShade purpose (D). Review: Ch 40.

**M1-048 — Answer: B.** Obj 3.7. SceneIndex / Hydra imaging is not in the usd-core wheel (`UsdImaging`, `Hd` absent). Review: Ch 38.

**M1-049 — Answer: A, C.** Obj 1.5. Per-department sublayers plus edit targets. One shared root (B) and muting the root (D) fight collaboration. Review: Ch 15, Ch 22.

**M1-050 — Answer: A.** Obj 5.2. Verified: linear `Get(4) = (4, 0, 0)`; held `Get(4) = (0, 0, 0)` (holds the previous sample). Review: Ch 10.

**M1-051 — Answer: A, C.** Obj 7.7. Naive `Resolve("./…")` is cwd; composition anchors to the layer. Use `ComputeAbsolutePath` / `CreateIdentifier`. `AnchorRelativePath` is **gone** in 26.08 (B). Paths starting `./` are **not** search-path lookups (D). Review: Ch 33.

**M1-052 — Answer: B.** Obj 2.2. Color the **instance root** (or inherit onto that instance). `OverridePrim` on a descendant proxy **raises**. Editing the prototype tints every instance. Review: Ch 24.

**M1-053 — Answer: B.** Obj 1.9. Verified: no `defaultPrim` → `GetModelNameFromRootLayer` returns the **first root prim** (`First`). Empty layer returns `''`. Review: Ch 16, Ch 32.

**M1-054 — Answer: A, C.** Obj 4.6. `UsdValidation` imports. `ComplianceChecker` is **gone**. The pip wheel ships **no** `usdchecker` CLI. Review: Ch 30.

**M1-055 — Answer: B.** Obj 6.2. Same LIVERPS fact as M1-001/M1-032, framed as a debug: specializes lose to references, so the artist still sees `1`. Review: Ch 21, Ch 42.

**M1-056 — Answer: A, B.** Obj 3.5. Custom Ar plugin + `plugInfo.json` + plugin path; `GetResolver()` stays the facade. Kinds do not register resolvers. Review: Ch 33, Ch 38.

**M1-057 — Answer: A, C.** Obj 1.11. Split heavy geo behind payloads; department sublayers; pin published USDC. Daily Flatten-only (D) throws composition away. Review: Ch 22.

**M1-058 — Answer: B.** Obj 4.1. glTF has no LIVERPS; materials, units, and hierarchy need an explicit mapping. Review: Ch 27.

**M1-059 — Answer: B.** Obj 7.2. Pin a **versioned** identifier that still resolves the same bytes. Floating `latest/` is the classic break. Review: Ch 32.

**M1-060 — Answer: B.** Obj 5.5. Verified: `CreateInMemory` fallbacks are upAxis **Y** and metersPerUnit **0.01**. Unexpected small/Y-up assets often start here. Review: Ch 2, Ch 13.

**M1-061 — Answer: B.** Obj 4.8. `.usd` `formatId` follows the **extension plugin**; the bytes may still be USDA text (`#usda 1.0`) or crate (`PXR-USDC`). Review: Ch 7, Ch 31.

**M1-062 — Answer: B.** Obj 2.5. Remove or block properties at the **instance root** (or de-instance that one root). Descendant proxy `OverridePrim` is not the edit site. Review: Ch 22, Ch 24.

**M1-063 — Answer: B.** Obj 6.4. Imageable **purpose** filters what a viewer draws. A `proxy` gprim is hidden when the viewer shows only `render`. Review: Ch 13, Ch 42.

**M1-064 — Answer: A, B.** Obj 4.7. Exporters should set `defaultPrim`, `metersPerUnit`, and `upAxis`. Do not invent USDA for `Kind.Registry.Register` or `GetMaster`. Review: Ch 28, Ch 29.

**M1-065 — Answer: A, C.** Obj 7.8. Map to typed prims/API schemas; keep unknowns in custom attributes/`customData`; honor payloads vs references. Do not Flatten as the only import (loses non-destructive round-trip). `UsdMtlx` is not in usd-core. Review: Ch 29, Ch 35.

---

## Domain repair (if you missed several)

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
