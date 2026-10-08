# Question Bank — Visualization (VIS)

**Original practice questions.** Not actual NVIDIA exam content. Mapped to NCP-OUSD study-guide objectives 8.1–8.4 (Visualization, 8%).

Verified against **USD 26.08** (`usd-core` 26.8). Domain target: 32 questions. This file holds **VIS-001–VIS-032** (domain complete).

Work the stems first. Answers and explanations are grouped at the end.

---

**VIS-001** · Obj 8.1 · Difficulty: Easy · Type: Single choice

How should you add `displayColor` to a mesh for Hydra/usdview (Obj 8.1)?

A. A relationship named `color`
B. `UsdGeom.PrimvarsAPI.CreatePrimvar("displayColor", Color3fArray, interpolation)`
C. Layer metadata `displayColor`
D. `kind = color`

---

**VIS-002** · Obj 8.1 · Difficulty: Easy · Type: Single choice

The primvar attribute name on the prim is:

A. `displayColor`
B. `primvars:displayColor`
C. `inputs:displayColor`
D. `info:displayColor`

---

**VIS-003** · Obj 8.1 · Difficulty: Medium · Type: Single choice

Per-vertex colors on a mesh of N points: interpolation and array length?

A. `constant`, length 1
B. `vertex`, length N (or N indices if indexed)
C. `uniform`, length N
D. `faceVarying` is required for vertex colors

---

**VIS-004** · Obj 8.1 · Difficulty: Medium · Type: Multiple select
Select two.

Lab 12 indexed `displayColor`:

A. Interpolation `vertex`
B. Indices `[0, 1, 0, 1]` and two palette colors
C. Indexing forces `constant`
D. `CreateAttribute("displayColor")` without PrimvarsAPI is the recommended path

---

**VIS-005** · Obj 8.1 · Difficulty: Medium · Type: Single choice

UVs for texturing a PreviewSurface usually live as:

A. `primvars:st` (`texCoord2f[]`), interpolation `vertex` or `faceVarying`
B. Shader `info:id` 
C. `points`
D. `customData['uv']`

---

**VIS-006** · Obj 8.2 · Difficulty: Easy · Type: Single choice

`UsdPreviewSurface` is:

A. A typed prim `def PreviewSurface`
B. An **`info:id`** string on a **`UsdShade.Shader`**, not a prim type
C. A Hydra render delegate
D. A variant set

---

**VIS-007** · Obj 8.2 · Difficulty: Medium · Type: Single choice

A drawable PreviewSurface material needs which connection?

A. Mesh `points` connected to the shader
B. Material **`outputs:surface`** connected to the shader’s `outputs:surface`
C. Only `Bind` — no connections
D. `outputs:displacement` is required in usdview

---

**VIS-008** · Obj 8.2 · Difficulty: Easy · Type: Single choice

`ps.CreateIdAttr("UsdPreviewSurface")` writes which attribute?

A. `id`
B. `info:id` (value `UsdPreviewSurface`)
C. `token purpose`
D. `asset file`

---

**VIS-009** · Obj 8.2 · Difficulty: Medium · Type: Single choice

`mat.ComputeSurfaceSource()` on 26.08 returns:

A. A single `UsdShade.Shader`
B. A **tuple of length 3** `(shader, outputName, sourceType)`
C. `None` until Flatten
D. The bound mesh

---

**VIS-010** · Obj 8.2 · Difficulty: Medium · Type: Multiple select
Select two.

UsdShade building blocks for Obj 8.2:

A. `Material` (terminals)
B. `Shader` (nodedef / `info:id`)
C. `Cube` as the material type
D. `PointInstancer` as a required shader

---

**VIS-011** · Obj 8.3 · Difficulty: Easy · Type: Single choice

Correct bind sequence on USD 26.08?

A. `Bind` only
B. **`MaterialBindingAPI.Apply(prim)` then `Bind(material)`**
C. `HasAPI` then skip Bind
D. `SetKind("material")` on the mesh

---

**VIS-012** · Obj 8.3 · Difficulty: Medium · Type: Single choice

`Bind` **without** `Apply`. What is true?

A. No relationship is written
B. `rel material:binding` is written; **`HasAPI` stays False**
C. `HasAPI` True
D. Bind raises

---

**VIS-013** · Obj 8.3 · Difficulty: Medium · Type: Python-reading

After Apply+Bind, `ComputeBoundMaterial()[0].GetPath()` in lab 34?

A. `/World/Board`
B. `/Looks/Paint`
C. `/Looks/Paint/Preview`
D. `/__Prototype_1`

---

**VIS-014** · Obj 8.3 · Difficulty: Medium · Type: Single choice

Binding **purpose** `preview` vs `full`?

A. Illegal in OpenUSD
B. Separate bindings so a DCC/Hydra preview pass can differ from the full render
C. Purpose on Imageable, not on materials
D. `preview` deletes `full`

---

**VIS-015** · Obj 8.3 · Difficulty: Medium · Type: Single choice

`weakerThanDescendants` vs `strongerThanDescendants` on a bind?

A. Cosmetic names
B. Strength: whether this bind yields to (or overrides) **descendant** binds (collections/subsets)
C. LIVERPS letters
D. Only legal on lights

---

**VIS-016** · Obj 8.3 · Difficulty: Medium · Type: Multiple select
Select two.

Ways to bind materials besides a direct rel on the gprim:

A. Collection-based `MaterialBindingAPI` collections
B. `UsdGeom.Subset` faces with their own bind
C. `subLayers` named `material`
D. `kind = material` on the mesh

---

**VIS-017** · Obj 8.4 · Difficulty: Medium · Type: Single choice

Does `UsdPreviewSurface` **automatically** read mesh `primvars:displayColor` into `diffuseColor`?

A. Yes always
B. **No** — you connect a **`UsdPrimvarReader_float3`** (or float) whose `varname` is `displayColor` to `inputs:diffuseColor` (Obj 8.4)
C. Yes if interpolation is constant
D. Yes after Apply

---

**VIS-018** · Obj 8.4 · Difficulty: Medium · Type: Single choice

`UsdPrimvarReader_float3` `varname` input type and value for displayColor?

A. `string` `"primvars:displayColor"`
B. **`token` `displayColor`** (the primvar name without requiring the `primvars:` prefix in varname)
C. `asset`
D. `color3f`

---

**VIS-019** · Obj 8.4 · Difficulty: Medium · Type: Single choice

Texture lookup for PreviewSurface typically chains:

A. `UsdPrimvarReader_float2` (`st`) → `UsdUVTexture` → PreviewSurface `diffuseColor`
B. Mesh `points` → UVTexture
C. `UsdLux.DistantLight` → diffuseColor
D. `ComputeExtentFromPlugins`

---

**VIS-020** · Obj 8.4 · Difficulty: Easy · Type: Single choice

Reader node `info:id` for UVs?

A. `UsdPreviewSurface`
B. `UsdPrimvarReader_float2`
C. `UsdUVTexture`
D. `UsdPrimvarReader_float3`

---

**VIS-021** · Obj 8.4 · Difficulty: Medium · Type: Multiple select
Select two.

Verified Obj 8.4 network facts:

A. `diffuseColor` `HasConnectedSource()` True after connecting the reader output
B. PreviewSurface `info:id` stays `UsdPreviewSurface`
C. The reader must be type `Mesh`
D. `varname` must be the full `primvars:displayColor` path as an `asset`

---

**VIS-022** · Obj 8.2 · Difficulty: Medium · Type: Single choice

`UsdShade.NodeGraph` is for:

A. Replacing Material
B. Nesting a reusable subgraph of shaders inside/beside a Material
C. Point instancing
D. Layer offsets

---

**VIS-023** · Obj 8.1 · Difficulty: Medium · Type: Single choice

Wrong interpolation on `st` (vertex-length with faceVarying) shows up as:

A. A composition error
B. **Unexpected UVs / seams** (Obj 5.5/8.1)
C. `HasAPI` False
D. Missing `defaultPrim`

---

**VIS-024** · Obj 8.3 · Difficulty: Easy · Type: Single choice

Relationship name for a direct material bind?

A. `looks`
B. `material:binding`
C. `outputs:surface`
D. `info:id`

---

**VIS-025** · Obj 8.2 · Difficulty: Medium · Type: Single choice

PreviewSurface `diffuseColor` input is authored with `CreateInput("diffuseColor", Color3f)`. On the prim the attribute is:

A. `diffuseColor`
B. `inputs:diffuseColor`
C. `outputs:diffuseColor`
D. `primvars:diffuseColor`

---

**VIS-026** · Obj 8.4 · Difficulty: Hard · Type: Single choice

Mesh has constant `displayColor` (0.2, 0.5, 0.9) **and** a bound PreviewSurface with unconnected `diffuseColor = (1,0,0)`. What does a typical Hydra PreviewSurface draw?

A. Always the primvar (displayColor always wins)
B. The **shader input** (red) unless you connect a primvar reader — displayColor is a fallback for unshaded / simple modes, not an automatic PreviewSurface input
C. Average magenta
D. Black until Flatten

---

**VIS-027** · Obj 8.3 · Difficulty: Medium · Type: Single choice

`ComputeBoundMaterial()` return (verified)?

A. Only a Material
B. A **tuple**: bound `Material` plus the **relationship** that won
C. A Shader
D. `None` if Apply was used

---

**VIS-028** · Obj 8.1 · Difficulty: Easy · Type: Single choice

`displayOpacity` is typically:

A. A `float[]` primvar alongside `displayColor`
B. A material bind purpose
C. `metersPerUnit`
D. A relationship

---

**VIS-029** · Obj 8.3 · Difficulty: Medium · Type: Single choice

Binding a material to **some faces** of a mesh?

A. Impossible
B. `UsdGeom.Subset` (or collection bind) + MaterialBindingAPI on the subset
C. Split the USDA file
D. `visibility = invisible` on indices

---

**VIS-030** · Obj 8.2 · Difficulty: Easy · Type: Single choice

usd-core 26.8 and `UsdMtlx` / MaterialX graphs in usdview?

A. `from pxr import UsdMtlx` works on this wheel
B. **ImportError** — PreviewSurface is the visualization path this book’s environment can author; MaterialX needs a full build
C. MaterialX is a primvar interpolation
D. `UsdPreviewSurface` is an alias for MaterialX

---

**VIS-031** · Obj 8.4 · Difficulty: Medium · Type: Single choice

Connect reader result to PreviewSurface in Python:

A. `Set((1,0,0))` on diffuseColor only
B. `ps.CreateInput("diffuseColor", Color3f).ConnectToSource(reader.GetOutput("result"))`
C. `AddReference` the reader
D. `Bind(reader)`

---

**VIS-032** · Obj 8.1 · Difficulty: Medium · Type: Single choice

`GetNamespace()` of `primvars:st` vs Mesh `points`?

A. Both `primvars`
B. `st` → `primvars`; `points` → **empty** namespace
C. Both empty
D. `points` → `inputs`

---

## Answers

**VIS-001 — Answer: B.** PrimvarsAPI. Review: §11.2, §40, lab 12.

**VIS-002 — Answer: B.** `primvars:` namespace. Review: §11.1.

**VIS-003 — Answer: B.** vertex ↔ points. Review: §11.3.

**VIS-004 — Answer: A, B.** Lab 12. Review: lab 12.

**VIS-005 — Answer: A.** st texCoord. Review: §11.3, §40.4.

**VIS-006 — Answer: B.** info:id on Shader. Review: §40.3, lab 34.

**VIS-007 — Answer: B.** Material surface terminal. Review: §40.2.

**VIS-008 — Answer: B.** Verified `info:id`. Review: lab 34.

**VIS-009 — Answer: B.** Tuple length 3. Review: lab 34.

**VIS-010 — Answer: A, B.** Material + Shader. Review: §40.1.

**VIS-011 — Answer: B.** Apply then Bind. Review: lab 34.

**VIS-012 — Answer: B.** Rel without HasAPI. Review: lab 34.

**VIS-013 — Answer: B.** `/Looks/Paint`. Review: lab 34.

**VIS-014 — Answer: B.** Binding purposes. Review: §40.6.

**VIS-015 — Answer: B.** Bind strength vs descendants. Review: §40.6.

**VIS-016 — Answer: A, B.** Collections and GeomSubset. Review: §40.6, §39.5.

**VIS-017 — Answer: B.** Need PrimvarReader (Obj 8.4). Review: §40.5.

**VIS-018 — Answer: B.** Token varname `displayColor`. Review: §40.5, probe.

**VIS-019 — Answer: A.** UV reader → UVTexture → PS. Review: §40.4.

**VIS-020 — Answer: B.** float2 reader. Review: §40.4.

**VIS-021 — Answer: A, B.** Verified connection + id. Review: probe, §40.5.

**VIS-022 — Answer: B.** NodeGraph subgraph. Review: §40.1.

**VIS-023 — Answer: B.** UV seams. Review: §11.3.

**VIS-024 — Answer: B.** material:binding. Review: lab 34.

**VIS-025 — Answer: B.** `inputs:` namespace. Review: §40.2.

**VIS-026 — Answer: B.** Unconnected PS uses its input; displayColor is not auto-wired. Review: §40.5, lab 34 stretch.

**VIS-027 — Answer: B.** Tuple material + rel. Review: probe, lab 34.

**VIS-028 — Answer: A.** displayOpacity primvar. Review: §11.7.

**VIS-029 — Answer: B.** GeomSubset binds. Review: §39.5, §40.6.

**VIS-030 — Answer: B.** No UsdMtlx on usd-core. Review: §35.1, DE-039.

**VIS-031 — Answer: B.** ConnectToSource. Review: §40.2, §40.5.

**VIS-032 — Answer: B.** Verified namespaces. Review: DM-014, §5.5.

---

*Visualization domain complete: VIS-001–VIS-032 (target 32).*
