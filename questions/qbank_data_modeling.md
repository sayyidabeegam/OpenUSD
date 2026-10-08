# Question Bank — Data Modeling (DM)

**Original practice questions.** Not actual NVIDIA exam content. Mapped to NCP-OUSD study-guide objectives 5.1–5.6 (Data Modeling, 13%).

Verified against **USD 26.08** (`usd-core` 26.8). Domain target: 52 questions. This file currently holds **DM-001–DM-052** (domain complete).

Work the stems first. Answers and explanations are grouped at the end.

---

**DM-001** · Obj 5.2 · Difficulty: Easy · Type: Single choice

Which `Sdf.ValueTypeNames` type should store Mesh `points`?

A. `Color3fArray` — RGB and XYZ are interchangeable
B. `Point3fArray` (`point3f[]`) — point **role** so transforms treat them as positions
C. `String` of comma-separated numbers
D. `IntArray` of packed floats

---

**DM-002** · Obj 5.2 · Difficulty: Easy · Type: Single choice

A texture filename on a shader input should be which value type?

A. `string`
B. `asset` (`Sdf.AssetPath`) so Ar can resolve it
C. `token`
D. `matrix4d`

---

**DM-003** · Obj 5.2 · Difficulty: Medium · Type: Single choice

`subdivisionScheme` and `purpose` are closed vocabularies. Preferred type?

A. `string` so any spelling is legal
B. `token` (`Sdf.ValueTypeNames.Token`)
C. `asset`
D. `bool`

---

**DM-004** · Obj 5.2 · Difficulty: Medium · Type: Multiple select
Select two.

Which pair of roles is **not** interchangeable even though both are 3-floats?

A. `point3f` (positions; translate with the prim)
B. `normal3f` (normals; inverse-transpose)
C. They are identical at runtime; roles are comments only
D. `color3f` is also a point and should go in `points`

---

**DM-005** · Obj 5.2 · Difficulty: Medium · Type: Single choice

A translate op has **only** time samples at 1 and 11, no default. What does `attr.Get()` (no argument) return?

A. The first sample
B. `None`
C. `(0, 0, 0)` schema fallback
D. Linear midpoint

---

**DM-006** · Obj 5.2 · Difficulty: Medium · Type: Python-reading

Samples at t=1 `(0,0,0)` and t=11 `(10,0,0)`. Stage interpolation starts as linear. What is `Get(6)` before and after `SetInterpolationType(Held)`?

A. Linear `(5,0,0)`; held `(0,0,0)` (previous sample)
B. Both `(5,0,0)`
C. Both `None`
D. Linear `None`; held `(10,0,0)`

---

**DM-007** · Obj 5.2 · Difficulty: Easy · Type: Single choice

Default stage interpolation type on a new stage?

A. `Usd.InterpolationTypeHeld`
B. `Usd.InterpolationTypeLinear`
C. Spline
D. None — you must set it or `Get(t)` raises

---

**DM-008** · Obj 5.1 · Difficulty: Easy · Type: Single choice

A primvar is which kind of property?

A. Any relationship
B. An attribute in the `primvars:` namespace with interpolation metadata
C. Layer metadata only
D. A kind of composition arc

---

**DM-009** · Obj 5.1 · Difficulty: Medium · Type: Single choice

Preferred API to add `displayColor` on a mesh (Obj 5.1)?

A. `CreateAttribute("displayColor", ...)` without a namespace
B. `UsdGeom.PrimvarsAPI.CreatePrimvar("displayColor", Color3fArray, interpolation)`
C. `SetKind("primvar")`
D. `AddReference` to a color layer

---

**DM-010** · Obj 5.1 · Difficulty: Medium · Type: Single choice

Per-face ID integers on a mesh of 10 faces should use which interpolation?

A. `vertex`
B. `uniform`
C. `constant` with 10 values
D. `faceVarying` is required for any per-face data

---

**DM-011** · Obj 5.1 · Difficulty: Medium · Type: Single choice

UV seams (different UVs on a shared point) need which interpolation?

A. `vertex`
B. `faceVarying`
C. `constant`
D. `uniform`

---

**DM-012** · Obj 5.1 · Difficulty: Medium · Type: Python-reading

Lab 12 authors vertex `displayColor` with values red/green and `SetIndices([0,1,0,1])`. What prints?

A. `indexed: False` because vertex cannot be indexed
B. `indexed: True`, indices `[0, 1, 0, 1]`, two palette values
C. Four color values and no indices
D. `CreatePrimvar` raises

---

**DM-013** · Obj 5.1 · Difficulty: Easy · Type: Single choice

Indexing and interpolation are related how?

A. Indexed means interpolation must be `vertex`
B. Independent — indexing is a palette; interpolation is how indices/values map to topology
C. Indexed means `constant`
D. You cannot index `displayColor`

---

**DM-014** · Obj 5.1 · Difficulty: Medium · Type: Single choice

`primvars:st` on a Mesh: `GetNamespace()` of that attribute?

A. `""` (empty)
B. `primvars`
C. `st`
D. `inputs`

---

**DM-015** · Obj 5.1 · Difficulty: Medium · Type: Single choice

A parent Xform authors constant `primvars:displayColor`. A child Mesh does not. `PrimvarsAPI(child).FindPrimvarWithInheritance("displayColor")`?

A. Invalid — primvars never inherit
B. Finds the inherited primvar (verified non-null with the parent’s value)
C. Only works for `st`
D. Raises `Tf.ErrorException`

---

**DM-016** · Obj 5.6 · Difficulty: Easy · Type: Single choice

You change Mesh `points`. What happens to `extent` automatically?

A. It recomputes
B. Nothing — you must `ComputeExtentFromPlugins` (or equivalent) **then `Set`**
C. `kind = component` updates it
D. Saving USDA fills it

---

**DM-017** · Obj 5.6 · Difficulty: Medium · Type: Single choice

`ComputeExtentFromPlugins(boundable, time)` return value vs authored extent?

A. It writes the attribute for you
B. It **returns** a min/max pair; `GetExtentAttr().Set(...)` authors it
C. It returns world-space boxes only
D. It is removed in 26.08

---

**DM-018** · Obj 5.6 · Difficulty: Medium · Type: Python-reading

Triangle points `(0,0,0)`, `(1,0,0)`, `(0,1,0)`. After compute-and-set, extent is?

A. `[(0,0,0), (1,1,0)]`
B. `[(0,0,0), (1,1,1)]`
C. `None` forever
D. A 4×4 matrix

---

**DM-019** · Obj 5.5 · Difficulty: Medium · Type: Single choice

A CAD tessellation looks “melted” in the viewer. Likely cause (Obj 5.5)?

A. `subdivisionScheme` fallback **`catmullClark`**; set `"none"`
B. Missing `customData`
C. USDA instead of USDC
D. `metersPerUnit = 1`

---

**DM-020** · Obj 5.5 · Difficulty: Medium · Type: Multiple select
Select two.

Which authored mistakes commonly cause **unexpected visuals**?

A. Stale `extent` after moving points (wrong bounds / culling)
B. `vertex` length array with `faceVarying` interpolation (UV/color seams wrong)
C. `ComputeAllDependencies` returning three lists
D. `formatId` of `.usd` being `usd`

---

**DM-021** · Obj 5.5 · Difficulty: Medium · Type: Single choice

A mesh is in the stage but missing in the default render. `purpose` fallback is `default`. You authored `purpose = guide`. Why?

A. Purpose does not affect imaging
B. `guide` (and often `proxy`) is omitted from the default purpose pass; switch purpose or the draw mask
C. `guide` deletes the prim
D. You must Flatten first

---

**DM-022** · Obj 5.5 · Difficulty: Easy · Type: Single choice

Imageable `visibility` fallback is:

A. `invisible`
B. `inherited`
C. `visible` as an authored default on every gprim
D. `None`

---

**DM-023** · Obj 5.4 · Difficulty: Easy · Type: Single choice

`prim.GetAttribute("points")` vs `prim.GetRelationship("points")` on a Mesh?

A. Both valid
B. `GetAttribute` is valid (`HasAttribute` True); points is not a relationship
C. Points are always relationships
D. You must use `GetMaster()`

---

**DM-024** · Obj 5.4 · Difficulty: Medium · Type: Single choice

`prim.GetAttribute("nope").IsValid()` for a missing name?

A. Raises KeyError
B. `False` (the handle exists but is invalid)
C. `True` with value `None`
D. Defines the attribute

---

**DM-025** · Obj 5.4 · Difficulty: Medium · Type: Single choice

`UsdGeom.Mesh.Define` then `GetProperties()` includes names like `accelerations` you never authored. Why?

A. A bug
B. **Schema** properties appear on the composed prim even without specs; use `HasAuthoredValue` / property stacks to see what is authored
C. Flatten ran implicitly
D. `GetProperties` only lists authored specs — so they were authored

---

**DM-026** · Obj 5.4 · Difficulty: Medium · Type: Multiple select
Select two.

Usd (composed) vs Sdf (authored) for Obj 5.4:

A. `Usd.Attribute.Get()` is the composed value
B. `Sdf.AttributeSpec` on a layer is what that layer authored
C. They are always identical
D. Sdf cannot create attributes

---

**DM-027** · Obj 5.4 · Difficulty: Easy · Type: Single choice

`UsdGeom.Tokens.Z` vs `UsdGeom.Tokens.z` for up-axis?

A. `Tokens.Z` exists
B. `Tokens.z` is `"Z"`; `Tokens.Z` is **missing** (AttributeError)
C. Both missing; only the string `"z"` works
D. Tokens are integers

---

**DM-028** · Obj 5.3 · Difficulty: Easy · Type: Single choice

Studio key `dept = "layout"` on a prim belongs in:

A. `customData`
B. `faceVertexCounts`
C. `metersPerUnit`
D. A specialize arc

---

**DM-029** · Obj 5.3 · Difficulty: Medium · Type: Single choice

`GetCustomData()` after setting one key may also show `userDocBrief`. Read `dept` with:

A. `GetCustomData()["dept"]` only after asserting dict length 1
B. `GetCustomDataByKey("dept")`
C. `GetAssetInfo()`
D. `GetTypeName()`

---

**DM-030** · Obj 5.3 · Difficulty: Medium · Type: Single choice

`kind`, `documentation`, `hidden` vs `customData`?

A. All four are unregistered dictionaries
B. `kind` / `documentation` / `hidden` are **registered** metadata; `customData` is the open dictionary
C. `hidden` is an attribute of type bool named `hidden`
D. `kind` is a relationship

---

**DM-031** · Obj 5.3 · Difficulty: Medium · Type: Multiple select
Select two.

Layer metadata (not prim `customData`) includes:

A. `defaultPrim`, `upAxis`, `metersPerUnit`, `subLayers`
B. `timeCodesPerSecond`, `startTimeCode`
C. `primvars:displayColor`
D. `xformOp:translate`

---

**DM-032** · Obj 5.2 · Difficulty: Medium · Type: Single choice

Cube `size` fallback vs Sphere `radius` fallback (no authored value)?

A. Both 1
B. Cube `2.0`, Sphere `1.0`
C. Both `None`
D. Cube `1`, Sphere `50000`

---

**DM-033** · Obj 5.2 · Difficulty: Easy · Type: Single choice

UVs should use which role array?

A. `color3f[]`
B. `texCoord2f[]` (`TexCoord2fArray`)
C. `point3f[]`
D. `matrix4d[]`

---

**DM-034** · Obj 5.5 · Difficulty: Hard · Type: Single choice

Hydra culls a mesh that is clearly in front of the camera after you scaled `points` 100× but left `extent` at the old 1-unit box. Diagnosis?

A. Wrong `formatId`
B. Stale **extent** used as a bounds hint (Obj 5.5 / 5.6)
C. Linear interpolation
D. `Get()` returned None so the mesh has no points

---

**DM-035** · Obj 5.4 · Difficulty: Medium · Type: Single choice

`GetPrimAtPath("/NoSuch")` when that path does not exist. What is safe?

A. `IsDefined()` always returns False
B. `bool(prim)` is `False` and `IsValid()` is `False`; calling `IsDefined()` on the null prim **raises** `RuntimeError`
C. The call to `GetPrimAtPath` itself raises
D. The prim is defined but empty

---

**DM-036** · Obj 5.1 · Difficulty: Medium · Type: Single choice

`elementSize = 3` on a float primvar means?

A. Always 3 vertices
B. Three array entries make **one** logical element (e.g. a float3 packed as floats)
C. Interpolation is uniform
D. Indexed is True

---

**DM-037** · Obj 5.2 · Difficulty: Medium · Type: Single choice

World transform matrix type in USD schemas is typically:

A. `matrix3f`
B. `matrix4d` (`Matrix4d`)
C. `quatf` only
D. `int[]`

---

**DM-038** · Obj 5.5 · Difficulty: Medium · Type: Multiple select
Select two.

A gprim is `invisible` at the parent and the child never authored visibility. What do you expect, and what API family is this?

A. Child stays invisible via **inherited** visibility (`UsdGeom.Imageable`)
B. Child is always visible because Mesh overrides Imageable
C. Setting parent `visibility = inherited` (the fallback) does not hide; you need `invisible` to hide
D. Visibility is a LIVERPS arc

---

**DM-039** · Obj 5.6 · Difficulty: Easy · Type: Single choice

`extent` is stored in which space?

A. World
B. **Local** axis-aligned min/max (`float3[]` length 2)
C. Camera
D. UV

---

**DM-040** · Obj 5.2 · Difficulty: Medium · Type: Single choice

`int` vs `int64` vs `float` vs `double` — picking a type for a large frame counter that must match other DCCs exactly?

A. Always `float` (everything is float in USD)
B. Prefer the width the source uses (`int64` if the DCC is 64-bit counts); do not silently downcast
C. Always `token`
D. Store numbers in `string` for safety

---

**DM-041** · Obj 5.4 · Difficulty: Easy · Type: Single choice

`Sdf.Path("/World/Chair/Seat").GetParentPath()`?

A. `/World`
B. `/World/Chair`
C. `/Seat`
D. `.`

---

**DM-042** · Obj 5.4 · Difficulty: Medium · Type: Single choice

`GetProperty("points")` on a Mesh returns what class of object?

A. Only `Usd.Relationship`
B. A valid `Usd.Attribute` (same as `GetAttribute("points")`)
C. `None`
D. `Sdf.Layer`

---

**DM-043** · Obj 5.2 · Difficulty: Medium · Type: Single choice

`subdivisionScheme` variability vs `points` variability?

A. Both varying
B. Scheme is **uniform** (no time samples in the usual schema); points are **varying** (can be sampled)
C. Scheme is varying; points are uniform
D. Variability does not exist on Usd attributes

---

**DM-044** · Obj 5.1 · Difficulty: Easy · Type: Single choice

Whole-object red `displayColor` uses which interpolation and roughly how many values (elementSize 1)?

A. `faceVarying`, one per corner
B. `constant`, one `color3f`
C. `vertex`, one per point even if they match
D. `uniform` with zero values

---

**DM-045** · Obj 5.5 · Difficulty: Medium · Type: Single choice

Parent visibility is `invisible`. Child attribute `Get()` is still `inherited`. `ComputeVisibility()` on the child?

A. `visible` because Get() is inherited
B. `invisible` — compute walks the namespace; Get() is only the local authored/fallback token
C. `None`
D. Raises

---

**DM-046** · Obj 5.6 · Difficulty: Medium · Type: Single choice

`UsdGeom.BBoxCache` vs the `extent` attribute?

A. They are unrelated
B. BBoxCache computes world/local bounds; it **uses authored extent** when present as a hint — stale extent still hurts
C. BBoxCache overwrites extent on disk
D. BBoxCache exists only in usdview

---

**DM-047** · Obj 5.3 · Difficulty: Easy · Type: Single choice

`hidden` metadata on a prim is meant to:

A. Delete the prim from the layer
B. Hint UIs/outliners to hide it; it is **not** the same as `visibility = invisible`
C. Unload payloads
D. Mute the layer

---

**DM-048** · Obj 5.2 · Difficulty: Medium · Type: Single choice

Value **clips** vs time samples on the attribute (Obj 5.2 overview)?

A. Clips replace LIVERPS
B. Clips are an extra value source for animation intervals; samples/defaults still follow strength — clips are not a LIVERPS letter
C. Clips are the only way to animate in 26.08
D. `Get()` with clips always returns the first clip sample even at Default

---

**DM-049** · Obj 5.5 · Difficulty: Medium · Type: Multiple select
Select two.

Mesh `doubleSided` fallback is `False`. Unexpected “black backfaces” can come from:

A. Single-sided mesh with inverted winding / wrong normals
B. `doubleSided` still False and the camera seeing the back
C. `ComputeAllDependencies` unresolved
D. `formatId usd`

---

**DM-050** · Obj 5.4 · Difficulty: Medium · Type: Single choice

To list **only authored** attributes on a prim in the current edit target’s layer, which view?

A. `prim.GetAttributes()` — that list is schema+authored mixed
B. Walk `Sdf.PrimSpec` / `GetAuthoredProperties` / `HasAuthoredValue` filters
C. `GetPrototype()`
D. `FindLoadable()`

---

**DM-051** · Obj 5.1 · Difficulty: Medium · Type: Single choice

`displayOpacity` is typically authored as:

A. `float[]` primvar (often with `displayColor`)
B. A relationship to a number
C. Layer `metersPerUnit`
D. `token` `opaque`

---

**DM-052** · Obj 5.2 · Difficulty: Easy · Type: Single choice

Attribute **splines** (Ts) on USD 26.08 relative to the exam’s time-sample core?

A. Splines replaced time samples; `Set` at a time now writes a spline
B. Time samples remain the core encoding; splines exist but this book treats them as a version note, not the primary Obj 5.2 tool
C. Splines are required for linear interpolation
D. `Get()` None is caused by splines always

---

## Answers

**DM-001 — Answer: B.** Point role matters under transforms. Review: §9.4, §9.9.

**DM-002 — Answer: B.** `asset` is the resolvable type. Review: §9.8.

**DM-003 — Answer: B.** Closed vocabularies are tokens. Review: §9.3.

**DM-004 — Answer: A, B.** Roles differ; C and D are false. (Select two true statements: A and B.) Review: §9.4.

**DM-005 — Answer: B.** Verified lab 10: `Get()` is None without a default. Review: §10.1.

**DM-006 — Answer: A.** Verified: linear midpoint 5; held previous sample 0. Review: §10.4, lab 10.

**DM-007 — Answer: B.** Verified `InterpolationTypeLinear`. Review: §10.4.

**DM-008 — Answer: B.** `primvars:` + interpolation. Review: §11.1.

**DM-009 — Answer: B.** PrimvarsAPI sets namespace and interpolation. Review: §11.2.

**DM-010 — Answer: B.** uniform = per face. Review: §11.3.

**DM-011 — Answer: B.** Seams → faceVarying. Review: §11.3.

**DM-012 — Answer: B.** Verified lab 12. Review: §11.4.

**DM-013 — Answer: B.** Indexing ⊥ interpolation. Review: §11.4.

**DM-014 — Answer: B.** Verified: `primvars:st` namespace `primvars`. Review: §5.5, §11.1.

**DM-015 — Answer: B.** Verified FindPrimvarWithInheritance. Review: §11.6.

**DM-016 — Answer: B.** Extent is authored, not automatic. Review: §13.2, lab 11.

**DM-017 — Answer: B.** Compute returns; Set writes. Review: §13.3.

**DM-018 — Answer: A.** Verified `[(0,0,0),(1,1,0)]`. Review: lab 11.

**DM-019 — Answer: A.** Fallback catmullClark. Review: §13.5, lab 11.

**DM-020 — Answer: A, B.** Stale extent and wrong interpolation. Review: §13.5, §11.3.

**DM-021 — Answer: B.** Purpose tokens filter draws. Review: §13.1, §13.5.

**DM-022 — Answer: B.** Verified fallback `inherited`. Review: §13.1.

**DM-023 — Answer: B.** points is an attribute. Review: §5.2–5.3.

**DM-024 — Answer: B.** Invalid handle, no raise. Review: §4.2, §5.4.

**DM-025 — Answer: B.** Schema property list ≠ authored specs. Review: §6.2, §8.1.

**DM-026 — Answer: A, B.** Two views. Review: §8.1–8.2.

**DM-027 — Answer: B.** Verified: `Tokens.Z` missing; `Tokens.z` is `Z`. Review: lab 08, §28.2.

**DM-028 — Answer: A.** Obj 5.3. Review: §12.2.

**DM-029 — Answer: B.** Avoid extra schema keys. Review: lab 08.

**DM-030 — Answer: B.** Registered vs open dictionary. Review: §12.1–12.3.

**DM-031 — Answer: A, B.** Stage/layer fields. Review: §12.4, §2.4.

**DM-032 — Answer: B.** Verified Cube 2, Sphere 1. Review: §13.1, lab 31.

**DM-033 — Answer: B.** texCoord2f[]. Review: §9.4, §11.3.

**DM-034 — Answer: B.** Bounds hint vs true points. Review: §13.2, §13.5.

**DM-035 — Answer: B.** Verified: `bool`/`IsValid()` are False; `IsDefined()` raises `RuntimeError` on a null prim. Review: §4.1.

**DM-036 — Answer: B.** elementSize packs logical elements. Review: §11.5.

**DM-037 — Answer: B.** matrix4d. Review: §9.5.

**DM-038 — Answer: A, C.** A hidden parent hides children through inherited visibility. The fallback token `inherited` does not itself hide; author `invisible`. Not a composition arc. Review: §13.1.

**DM-039 — Answer: B.** Local AABB. Review: §13.2.

**DM-040 — Answer: B.** Match source width. Review: §9.2, §9.9.

**DM-041 — Answer: B.** `/World/Chair`. Review: §8.3.

**DM-042 — Answer: B.** Verified `GetProperty("points")` is a valid Attribute. Review: §5.1.

**DM-043 — Answer: B.** Verified uniform vs varying. Review: §5.2, §10.1.

**DM-044 — Answer: B.** constant one color. Review: §11.3, §11.7.

**DM-045 — Answer: B.** Verified: child `Get()` is `inherited`; `ComputeVisibility()` is `invisible`. Review: §13.1.

**DM-046 — Answer: B.** Extent is the authored hint BBoxCache can use. Review: §13.4.

**DM-047 — Answer: B.** `hidden` ≠ Imageable visibility. Review: §12.3.

**DM-048 — Answer: B.** Clips are not a LIVERPS letter. Review: §10.6, §21.5.

**DM-049 — Answer: A, B.** Winding/sides, not deps or formatId. Review: §13.5.

**DM-050 — Answer: B.** Schema GetAttributes is not “authored only.” Review: §8.1–8.2.

**DM-051 — Answer: A.** Companion primvar to displayColor. Review: §11.7.

**DM-052 — Answer: B.** Samples remain core. Review: §10.7.

---

*Data Modeling domain complete: DM-001–DM-052 (target 52).*

