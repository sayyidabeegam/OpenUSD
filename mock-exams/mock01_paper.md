# Mock Exam 1 — NCP-OUSD Practice Paper

**Original practice exam. Not actual NVIDIA exam content.**

Verified against **USD 26.08** (`usd-core` 26.8). Difficulty: **medium** (paper 1 of 3).

| | |
|---|---|
| Questions | 65 |
| Time | 120 minutes |
| Blueprint mix | COMP 15 · DE 10 · PD 9 · DM 8 · DBG 7 · CA 7 · VIS 5 · CUST 4 |
| Types | Single choice, multiple select (count stated), USDA- or Python-reading |
| Answers | `mock-exams/mock01_answers.md` — **do not open until you finish** |

Work in order. Mark one letter unless the stem says **Select two** or **Select three**. USDA in this paper is always multiline (one-line `{ double x = 1 }` does not parse). Python snippets are marked `.norun`; they are stems, not labs.

This book’s readiness bar is its own. NVIDIA does not publish a passing score.

---

**M1-001** · COMP · Obj 1.6 · Difficulty: Medium · Type: Single choice

Two opinions target the same `double reach` on `/Crane`. One is authored in a **specializes** class. The other is authored on the **referenced** asset. No local, inherit, variant, or relocate opinion exists. Which value wins?

A. The specializes class, because class prims are always strongest
B. The referenced asset, because references beat specializes in LIVERPS
C. Neither — USD averages numeric opinions
D. The specializes class, because specializes sit next to local in LIVERPS

---

**M1-002** · DM · Obj 5.2 · Difficulty: Medium · Type: Python-reading

```{.python .norun}
from pxr import Usd, UsdGeom, Gf
stage = Usd.Stage.CreateInMemory()
xf = UsdGeom.Xform.Define(stage, "/T")
attr = xf.AddTranslateOp().GetAttr()
attr.ClearDefault()
attr.Set(Gf.Vec3d(0, 0, 0), 0)
attr.Set(Gf.Vec3d(10, 0, 0), 10)
print(attr.Get())
```

What does `print` show?

A. `(0, 0, 0)`
B. `(10, 0, 0)`
C. `(5, 0, 0)`
D. `None`

---

**M1-003** · DE · Obj 4.3 · Difficulty: Medium · Type: Single choice

Layout artists merge a department layer in Git several times a day. The farm opens the published cache thousands of times per lighting job. Which encoding pair fits that split?

A. Git: USDC crate; farm: USDA text
B. Git: USDA text; farm: USDC crate
C. Both Git and farm: USDZ, because it is always smallest
D. Git: `.usdz`; farm: USDA so `usdcat` can run on the farm

---

**M1-004** · COMP · Obj 1.5 · Difficulty: Medium · Type: USDA-reading

File: `setdress.usda`

```usda
#usda 1.0
over "Desk"
{
    double height = 4
}
```

File: `layout.usda`

```usda
#usda 1.0
over "Desk"
{
    double height = 12
}
```

File: `shot.usda`

```usda
#usda 1.0
(
    subLayers = [
        @./setdress.usda@,
        @./layout.usda@
    ]
)
def Xform "Desk"
{
}
```

What is the composed `height` on `/Desk`?

A. `12`, because `layout.usda` is listed last
B. `4`, because the first sublayer in the list is strongest
C. `8`, the mean of the two opinions
D. None — two sublayers with the same field is a composition error

---

**M1-005** · CA · Obj 2.4 · Difficulty: Medium · Type: Multiple select
Select two.

On USD 26.08, which statements about native-instance prototypes are true?

A. `prim.GetPrototype()` returns the shared prototype prim
B. `prim.GetMaster()` is the documented 26.08 name
C. `GetMaster` **does not exist** on `Usd.Prim` in this version
D. `prim.GetInstanceProxy()` is how you fetch the prototype

---

**M1-006** · PD · Obj 7.2 · Difficulty: Medium · Type: Single choice

`UsdUtils.ExtractExternalReferences(path)` and `UsdUtils.ComputeAllDependencies(path)` both return a 3-tuple. How do those tuples differ?

A. Extract is `(sublayers, references+other assets, payloads)` for **one** file; Compute walks the **closure** as `(layers, assets, unresolved)`
B. They are identical aliases
C. Extract returns layers; Compute returns only unresolved paths
D. Compute is USDA-only; Extract is USDC-only

---

**M1-007** · VIS · Obj 8.3 · Difficulty: Medium · Type: Single choice

You want `HasAPI(UsdShade.MaterialBindingAPI)` to be true on a mesh and a working binding. What is the correct Python order on USD 26.08?

A. `Bind(...)` only — Apply is implied
B. `UsdShade.MaterialBindingAPI.Apply(prim)` then `MaterialBindingAPI(prim).Bind(material)`
C. Author `rel material:binding` in USDA and skip Apply; HasAPI becomes true automatically
D. `UsdGeom.Gprim(prim).BindMaterial(material)`

---

**M1-008** · DBG · Obj 6.1 · Difficulty: Medium · Type: Python-reading

A listener counts `Usd.Notice.ObjectsChanged`. Three `CreateAttribute(...).Set(...)` calls on an existing prim fire **6** notices. The same two attribute specs authored inside `with Sdf.ChangeBlock():` fire **1** notice. Why use the block?

A. It disables composition so LIVERPS is skipped
B. It coalesces change processing into one notice, which can remove a notice-storm bottleneck
C. It makes `DefinePrim` of a brand-new child path always succeed
D. It writes USDC instead of USDA

---

**M1-009** · COMP · Obj 1.1 · Difficulty: Medium · Type: USDA-reading

File: `crane_asset.usda`

```usda
#usda 1.0
(
    defaultPrim = "Crane"
)
def Xform "Crane"
{
    double reach = 2
}
```

File: `crane_shot.usda`

```usda
#usda 1.0
class "_Reach"
{
    double reach = 7
}

def "Crane" (
    prepend references = @./crane_asset.usda@
    prepend inherits = </_Reach>
)
{
}
```

What is composed `reach` on `/Crane`?

A. `2` — references beat inherits
B. `7` — inherits beat references
C. `9` — USD adds the two opinions
D. None — inherit and reference cannot share a prim

---

**M1-010** · DM · Obj 5.1 / 8.1 · Difficulty: Medium · Type: Single choice

A mesh has 4 vertices and 2 triangle faces. You author `primvars:displayColor` as **vertex** interpolation. How many color values belong on the primvar array (ignoring indexing)?

A. 1 — one color for the whole mesh
B. 2 — one color per face
C. 4 — one color per vertex
D. 6 — one color per face-vertex corner

---

**M1-011** · DE · Obj 4.3 · Difficulty: Medium · Type: Single choice

`Usd.Stage.CreateNew("hero.usd")` then `Save()`. What are the crate **magic bytes** and `GetFileFormat().formatId`?

A. Magic `#usda 1.0`, formatId `usda`
B. Magic `PXR-USDC`, formatId `usdc`
C. Magic `PXR-USDC`, formatId `usd` (id follows the `.usd` plugin; magic follows crate bytes)
D. Magic `PK`, formatId `usdz`

---

**M1-012** · COMP · Obj 1.3 · Difficulty: Medium · Type: Multiple select
Select two.

A set has a cheap stand-in `Hero` and a heavy sculpt `Heavy` that lighting should be able to unload. Which pair of arcs matches that intent?

A. `Hero` uses a **reference** (always composed when the parent is)
B. `Heavy` uses a **payload** (deferred; `LoadNone` leaves it unloaded)
C. `Heavy` must be a **sublayer**, because only sublayers can unload
D. `Hero` must be a **specialize**, because specializes are optional

---

**M1-013** · PD · Obj 7.2 · Difficulty: Medium · Type: Single choice

In a work / publish / pin pipeline, which statement is true?

A. Artists should overwrite the published USDC in place so Git always has one file
B. Work layers stay editable; publish writes an immutable cache; the shot **pins** a versioned identifier
C. Pinning means deleting the work layer after each save
D. Publish layers must be USDA so the farm can `diff` them

---

**M1-014** · CUST · Obj 3.3 · Difficulty: Medium · Type: Single choice

A studio wants a new model kind `heroComponent` registered from Python on usd-core 26.8. What happens if they call `Kind.Registry.Register("heroComponent", "component")`?

A. It succeeds and `HasKind("heroComponent")` becomes true
B. The method **does not exist** — kinds are registered through the kind plugin / `plugInfo.json`, not `Kind.Registry.Register`
C. It succeeds only inside `Sdf.ChangeBlock`
D. It succeeds but only for the current stage

---

**M1-015** · CA · Obj 2.3 · Difficulty: Medium · Type: Single choice

A `UsdGeom.PointInstancer` has `protoIndices = [0, 0, 0]` and then `invisibleIds = [1]`. What is `GetInstanceCount()` after the hide?

A. `2` — hidden ids are removed from the count
B. `3` — the count still includes hidden instances; `invisibleIds` is a mask
C. `0` — any `invisibleIds` deactivates the instancer
D. `1` — only the hidden id is counted

---

**M1-016** · COMP · Obj 1.4 · Difficulty: Medium · Type: USDA-reading

File: `walk.usda`

```usda
#usda 1.0
(
    defaultPrim = "Clip"
)
def Xform "Clip"
{
    double3 xformOp:translate.timeSamples = {
        0: (0, 0, 0),
        10: (10, 0, 0),
    }
    uniform token[] xformOpOrder = ["xformOp:translate"]
}
```

File: `crowd.usda`

```usda
#usda 1.0
def "Walker" (
    prepend references = @./walk.usda@ (
        offset = 10.0
        scale = 2.0
    )
)
{
}
```

What are the composed sample times on `/Walker.xformOp:translate`?

A. `[0, 10]` — offsets never change sample times
B. `[10, 30]` — composed time is `offset + scale * layerTime`
C. `[20, 40]` — USD multiplies then adds twice
D. `[5, 15]` — USD uses `(offset + layerTime) / scale`

---

**M1-017** · DM · Obj 5.6 · Difficulty: Medium · Type: Multiple select
Select two.

An exporter moved every point on a mesh and forgot to touch `extent`. Which pair restores a valid extent?

A. `UsdGeom.Boundable.ComputeExtentFromPlugins(mesh, time)` then `mesh.GetExtentAttr().Set(...)`
B. Set `extent` to `[(0,0,0), (0,0,0)]` and hope Hydra ignores it
C. Recompute extent whenever `points` change; keep the two arrays in sync
D. Delete `extent` permanently so USD guesses at render time from `kind` alone

---

**M1-018** · VIS · Obj 8.2 · Difficulty: Medium · Type: Multiple select
Select two.

On a fresh in-memory stage, which intensity fallbacks are true on USD 26.08?

A. `UsdLux.DistantLight` intensity fallback is `50000`
B. `UsdLux.SphereLight` intensity fallback is `1`
C. Both lights fallback to `None` until you set intensity
D. Distant and Sphere share the same fallback of `1`

---

**M1-019** · DBG · Obj 6.3 · Difficulty: Medium · Type: Single choice

A referenced layer path cannot be opened (`@./missing.usda@`). A referenced prim path is well-formed but the target prim is not in that layer. Which diagnostic pair matches those two failures?

A. Both are `UnresolvedPrimPath`
B. Missing file: `InvalidAssetPath`; missing prim in an opened layer: `UnresolvedPrimPath`
C. Both are `Tf.MallocTag`
D. Missing file: `UnresolvedPrimPath`; missing prim: `InvalidAssetPath`

---

**M1-020** · COMP · Obj 1.7 · Difficulty: Medium · Type: USDA-reading

```usda
#usda 1.0
def Xform "Crate" (
    prepend variantSets = "fit"
)
{
    variantSet "fit" = {
        "tight" {
            double binWidth = 1
        }
        "loose" {
            double binWidth = 8
        }
    }
}
```

No variant is selected. What does `GetPrimAtPath("/Crate").GetAttribute("binWidth").Get()` return?

A. `1` — first variant wins automatically
B. `8` — last variant wins automatically
C. `None` — without a selection the attribute is not composed
D. `0` — USD fills a numeric zero

---

**M1-021** · DE · Obj 4.7 · Difficulty: Medium · Type: Multiple select
Select two.

You flatten a shot that **references** `bolt.usda` and has a **sublayer** of notes. Which statements match USD 26.08?

A. `stage.Flatten()` **bakes** the reference (the flattened prim no longer holds the reference list)
B. `UsdUtils.FlattenLayerStack(stage)` **keeps** references and **drops** sublayers
C. `FlattenLayerStack` keeps sublayers and deletes references
D. `Flatten()` refuses to run if any payload is unloaded

---

**M1-022** · PD · Obj 7.5 · Difficulty: Medium · Type: Single choice

On usd-core 26.8, `type(Ar.GetResolver()).__name__` is `Resolver`. Where is `DefaultResolver`?

A. There is no DefaultResolver in 26.08
B. `type(Ar.GetUnderlyingResolver()).__name__` is `DefaultResolver` — `GetResolver()` is the facade
C. `Ar.GetResolver()` is already a `DefaultResolver` instance
D. You must call `prim.GetPrototype()` to see the resolver

---

**M1-023** · CA · Obj 2.4 · Difficulty: Medium · Type: USDA-reading

```usda
#usda 1.0
def Xform "Proto"
{
    def Cube "Body"
    {
    }
}

def Xform "Wagon" (
    instanceable = true
    prepend references = </Proto>
)
{
    over "Seat"
    {
    }
}
```

Which statement is true of `/Wagon`?

A. `/Wagon/Seat` is a composed child; `Traverse` lists it
B. `/Wagon` is an instance; `/Wagon/Body` is an instance proxy; `/Wagon/Seat` is **not** composed (nested `over` of a new child is ignored)
C. `instanceable` is ignored unless the prim is a `PointInstancer`
D. `GetMaster()` returns `/Proto`

---

**M1-024** · COMP · Obj 1.8 · Difficulty: Medium · Type: USDA-reading

File: `bot_asset.usda`

```usda
#usda 1.0
(
    defaultPrim = "Bot"
)
def Xform "Bot"
{
    def Xform "Rig"
    {
        def Cube "Arm"
        {
            double size = 1
        }
    }
}
```

File: `bot_shot.usda`

```usda
#usda 1.0
(
    relocates = {
        </Bot/Rig/Arm>: </Bot/Arm>
    }
)
def "Bot" (
    prepend references = @./bot_asset.usda@
)
{
    over "Arm"
    {
        double size = 4
    }
    over "Rig"
    {
        over "Arm"
        {
            double size = 99
        }
    }
}
```

After composition, what is `size` on `/Bot/Arm`?

A. `99` — the source-path `over` is strongest
B. `4` — the **destination** `over` wins; the source-path opinion is ignored
C. `1` — relocates disable all overs
D. None — relocates cannot be authored as layer metadata

---

**M1-025** · DM · Obj 5.4 · Difficulty: Medium · Type: Multiple select
Select two.

Z-up tokens on `UsdGeom` in USD 26.08:

A. `hasattr(UsdGeom.Tokens, "Z")` is `True`
B. `hasattr(UsdGeom.Tokens, "z")` is `True`
C. `UsdGeom.Tokens.Z` does **not** exist (capital `Z` is a trap)
D. `UsdGeom.UpAxis.Z` is the only legal spelling

---

**M1-026** · VIS · Obj 8.4 · Difficulty: Medium · Type: Single choice

`UsdShade.Material.ComputeSurfaceSource()` on usd-core 26.8 returns a value whose `len(...)` is:

A. `1` — just the shader
B. `2` — shader and output name
C. `3` — a 3-tuple
D. `0` — it always returns `None`

---

**M1-027** · PD · Obj 7.3 · Difficulty: Medium · Type: Single choice

A coordinator needs one layer that still **points at** published component files, but must not keep department **sublayers**. Which API?

A. `stage.Flatten()` — it keeps references
B. `UsdUtils.FlattenLayerStack(stage)` — sublayers collapse; references remain
C. `Sdf.Layer.Export` — it always strips references
D. `Usd.Stage.OpenMasked` — it deletes sublayers as a side effect

---

**M1-028** · COMP · Obj 1.3 · Difficulty: Medium · Type: Single choice

`Usd.Stage.Open("set.usda", Usd.Stage.LoadNone)` where `/Hero` **references** `lamp.usda` (defaultPrim `Lamp` with child `Shade`) and `/Heavy` **payloads** the same file. What is in the stage?

A. Neither `/Hero/Shade` nor `/Heavy/Shade`
B. `/Hero/Shade` is composed (references still load); `/Heavy/Shade` is not (payload deferred)
C. Both children load, because `LoadNone` only skips sublayers
D. The call raises — `LoadNone` cannot be passed to `Open`

---

**M1-029** · DBG · Obj 6.1 · Difficulty: Medium · Type: Single choice

Inside `with Sdf.ChangeBlock():` you call `stage.DefinePrim("/ExistingParent/BrandNewChild")` where that child spec does not yet exist. What can happen on USD 26.08?

A. It always succeeds silently
B. It can raise `Tf.ErrorException` — defining a **new** child path inside a live ChangeBlock is a known trap
C. It converts the stage to USDA
D. It only fails if the parent is instanceable

---

**M1-030** · DE · Obj 4.3 · Difficulty: Medium · Type: Single choice

`UsdUtils.CreateNewUsdzPackage("root.usda", "out.usdz")` on usd-core 26.8 writes ZIP members with which `compress_type`?

A. `zipfile.ZIP_DEFLATED` (8)
B. `zipfile.ZIP_STORED` (0) — USDZ is store-only
C. `zipfile.ZIP_BZIP2`
D. Uncompressed only if the file is USDA

---

**M1-031** · CA · Obj 2.1 · Difficulty: Medium · Type: Single choice

A PointInstancer already has one prototype and `protoIndices` of all zeros. You `prototypes.AddTarget("/PI/Tree")` (default list position). What is the usual production hazard?

A. `AddTarget` always appends, so old indices stay valid
B. `AddTarget` **prepends** by default, so index `0` now names the new proto and every existing instance switches
C. `AddTarget` deletes `protoIndices`
D. PointInstancer forbids a second prototype

---

**M1-032** · COMP · Obj 1.1 · Difficulty: Medium · Type: USDA-reading

Same `crane_asset.usda` as M1-009 (`reach = 2`). Shot:

```usda
#usda 1.0
class "_ReachS"
{
    double reach = 7
}

def "Crane" (
    prepend references = @./crane_asset.usda@
    prepend specializes = </_ReachS>
)
{
}
```

Composed `reach`?

A. `7` — specializes beat references
B. `2` — references beat specializes
C. `None` — specialize plus reference is illegal
D. `4.5` — the mean

---

**M1-033** · DM · Obj 5.2 · Difficulty: Medium · Type: USDA-reading

File: `cached.usda`

```usda
#usda 1.0
(
    defaultPrim = "P"
)
def Sphere "P"
{
    double radius.timeSamples = {
        0: 1,
        10: 5,
    }
}
```

File: `hero.usda`

```usda
#usda 1.0
def "P" (
    prepend references = @./cached.usda@
)
{
    double radius = 9
}
```

`attr = stage.GetPrimAtPath("/P").GetAttribute("radius")`. What are `attr.Get()` and `list(attr.GetTimeSamples())`?

A. `9.0` and `[]` — a stronger **default** hides weaker samples
B. `9.0` and `[0, 10]`
C. `1.0` and `[0, 10]` — samples always beat defaults
D. `None` and `[0, 10]`

---

**M1-034** · CUST · Obj 3.4 · Difficulty: Medium · Type: Single choice

You `Sdf.Layer.FindOrOpen("schema.usda")` for a codeless schema. Does that **register** the schema with `Usd`?

A. Yes — parsing is registration
B. No — parse ≠ register; the plugin must be on `PXR_PLUGINPATH_NAME` / `Plug.Registry` so generated types exist
C. Yes, if the file is named `schema.usda`
D. Yes, but only for `UsdAPISchemaBase` types

---

**M1-035** · PD · Obj 7.6 · Difficulty: Medium · Type: Single choice

A producer must stash a pipeline `assetId` string that renderers should ignore. Best field?

A. `customData` dictionary on the prim or layer (not a schema attribute)
B. `primvars:displayColor`
C. `kind = "assetId"`
D. `upAxis`

---

**M1-036** · COMP · Obj 1.8 · Difficulty: Medium · Type: Single choice

A department layer authors `over "Lamp" { double radius = 9 }` but the composed stage still shows the referenced `1`. Which check is the most useful first step?

A. Assume USD is broken and reinstall usd-core
B. Inspect **LIVERPS and the layer stack**: a stronger opinion (local in a stronger sublayer, inherit, variant, or a muted target layer) can hide the department over
C. Convert the file to USDZ
D. Call `GetMaster()` on `/Lamp`

---

**M1-037** · VIS · Obj 8.4 · Difficulty: Medium · Type: Single choice

A UsdPreviewSurface must read **vertex displayColor**. Which reader id and input name are the usual pair?

A. `UsdPrimvarReader_float3` with `inputs:varname` = `displayColor`
B. `UsdUVTexture` with `inputs:varname` = `st`
C. `UsdPrimvarReader_float` with `inputs:varname` = `points`
D. `UsdPreviewSurface` itself reads displayColor with no reader

---

**M1-038** · DBG · Obj 6.5 · Difficulty: Medium · Type: Multiple select
Select two.

You need allocator stats and a timeline of USD work on this book’s pip `usd-core` 26.8 wheel. Which pair is accurate?

A. `Tf.MallocTag.GetTotalBytes()` often reports **0 bytes** on this wheel — tagging was not compiled in
B. `Usd.Trace.Collector` / Reporter can still record a trace of function scopes
C. `Tf.MallocTag` always matches `ps` RSS
D. Trace requires `UsdImaging` and will not import

---

**M1-039** · DE · Obj 4.4 · Difficulty: Medium · Type: Multiple select
Select two.

A DCC round-trip must keep studio identifiers stable. Which practices belong in the exporter/importer pair?

A. Run names through `Tf.MakeValidIdentifier` on export and persist the original name in `customData` if it changed
B. Drop `defaultPrim` so the DCC can pick a root at random
C. Author `metersPerUnit` and `upAxis` on the root layer and document that **composition does not auto-convert** units or axis
D. Write every mesh as `Sphere` to save bytes

---

**M1-040** · COMP · Obj 1.1 · Difficulty: Medium · Type: USDA-reading

File: `r1.usda`

```usda
#usda 1.0
(
    defaultPrim = "Ball"
)
def Sphere "Ball"
{
    double radius = 2
}
```

File: `r2.usda`

```usda
#usda 1.0
(
    defaultPrim = "Ball"
)
def Sphere "Ball"
{
    double radius = 8
}
```

File: `shot.usda`

```usda
#usda 1.0
def "Ball" (
    prepend references = @./r1.usda@
    append references = @./r2.usda@
)
{
}
```

Composed `radius` on `/Ball`?

A. `8` — append always beats prepend
B. `2` — prepended references are stronger than appended ones
C. `5` — the mean
D. None — prepend and append cannot combine

---

**M1-041** · DM · Obj 5.3 · Difficulty: Medium · Type: Single choice

`prim.GetCustomDataByKey("dept")` versus `prim.GetMetadata("documentation")`. Which statement is true?

A. They are the same field
B. `customData` is a dictionary of producer key/values; `documentation` / `userDocBrief` are the human-doc metadata fields
C. `customData` is only legal on attributes, never prims
D. Setting `customData` registers a new schema

---

**M1-042** · CA · Obj 2.4 · Difficulty: Medium · Type: USDA-reading

```usda
#usda 1.0
def Xform "Clutter"
{
    def Cube "Mug" (
        kind = "component"
    )
    {
    }
}
```

`mug = stage.GetPrimAtPath("/Clutter/Mug")`. What are `Usd.ModelAPI(mug).GetKind()` and `mug.IsComponent()`?

A. `component` and `True`
B. `component` and `False` — the parent is not a model, so the component chain is broken
C. `assembly` and `True`
D. `""` and `True`

---

**M1-043** · PD · Obj 7.4 · Difficulty: Medium · Type: Single choice

A DCC plugin is loaded against this venv. `Usd.GetVersion()` prints `(0, 26, 8)`. What must the plugin match?

A. Any USD 0.x is ABI-compatible
B. The **same** OpenUSD / usd-core ABI the DCC was built against — a 26.8 wheel does not make a 24.11 plugin safe
C. Only the Python minor version, not USD
D. `Kind.Registry` version tags

---

**M1-044** · COMP · Obj 1.2 · Difficulty: Medium · Type: Single choice

You need to open only `/World/Hero` and its descendants from a huge stage. Which API is correct on 26.08?

A. `Usd.Stage.Open(path, mask=["/World/Hero"])`
B. `Usd.Stage.OpenMasked(path, Usd.StagePopulationMask(["/World/Hero"]))`
C. `Usd.Stage.Open(path, Usd.Stage.LoadNone)` — that is a population mask
D. `prim.GetPrototype()`

---

**M1-045** · DBG · Obj 6.5 · Difficulty: Medium · Type: Single choice

Composition spews hundreds of similar asset-path warnings during `Open`. Which helper coalesces them for a readable report?

A. `UsdUtils.CoalescingDiagnosticDelegate` installed **before** `Open`
B. `Tf.MallocTag.Initialize` after `Open`
C. `Kind.Registry.GetAllKinds`
D. `UsdGeom.Tokens.Z`

---

**M1-046** · DE · Obj 4.5 · Difficulty: Medium · Type: USDA-reading

```usda
#usda 1.0
def Mesh "Bolt"
{
    rel material:binding = </Looks/Steel>
}

def Scope "Looks"
{
    def Material "Steel"
    {
    }
}
```

On `/Bolt`, `HasAPI(UsdShade.MaterialBindingAPI)` and `HasRelationship("material:binding")` are:

A. `True`, `True`
B. `False`, `True` — the rel is authored; the API schema was not applied
C. `True`, `False`
D. Both `False` — USDA cannot author relationships

---

**M1-047** · VIS · Obj 8.3 · Difficulty: Medium · Type: Multiple select
Select two.

Which statements about material **purpose** and binding strength are true?

A. `preview` purpose is the usual choice for usdview / UsdPreviewSurface lookdev
B. `allPurpose` (empty token) is a fallback when a specific purpose is not bound
C. `weakerThanDescendants` makes the ancestor always win over a child bind
D. Purpose `physics` is a required UsdShade token on every mesh

---

**M1-048** · CUST · Obj 3.7 · Difficulty: Medium · Type: Single choice

A teammate wants a Hydra **SceneIndex** plugin that emits geometry as Hydra prims, using only this book’s pip `usd-core` 26.8 environment. What is the blocker?

A. SceneIndex plugins are authored in USDA
B. `UsdImaging` / `Hd` are **not** in the usd-core wheel — you need an imaging build of OpenUSD
C. SceneIndex requires `Kind.Registry.Register`
D. SceneIndex works if you `import pxr.UsdShade`

---

**M1-049** · COMP · Obj 1.5 · Difficulty: Medium · Type: Multiple select
Select two.

Two departments must edit the same shot without clobbering each other. Which layering choices support that?

A. Each department owns a **sublayer**; the shot root lists them in strength order
B. Everyone authors into the same root layer with no sublayers
C. Use **edit targets** so a tool’s `Set` writes the intended department layer
D. Mute the root layer so no one can save

---

**M1-050** · DM · Obj 5.2 · Difficulty: Medium · Type: Python-reading

Samples at t=0 `(0,0,0)` and t=10 `(10,0,0)`. Interpolation is **linear**, then **held**. What is `attr.Get(4)` in each mode?

A. Linear `(4, 0, 0)`; held `(0, 0, 0)`
B. Linear `(0, 0, 0)`; held `(4, 0, 0)`
C. Both `(4, 0, 0)`
D. Both `None`

---

**M1-051** · PD · Obj 7.7 · Difficulty: Medium · Type: Multiple select
Select two.

A validator calls `Ar.GetResolver().Resolve("./tex/wood.png")` from a random cwd and gets empty, but the composed stage shows the texture. Why?

A. Naive `Resolve("./…")` uses **process cwd**; composition **anchors** to the layer that authored the path
B. `AnchorRelativePath` is the 26.08 replacement and always exists on `Ar.Resolver`
C. `Sdf.Layer.ComputeAbsolutePath` / `CreateIdentifier` with the layer’s `ResolvedPath` is the layer-relative check
D. Search paths apply to identifiers that start with `./`

---

**M1-052** · CA · Obj 2.2 · Difficulty: Medium · Type: Single choice

You must tint **one** native instance’s mesh without turning `instanceable` off. Which approach is legal?

A. `stage.OverridePrim("/Instance/Mesh")` and set `primvars:displayColor` on the proxy — this raises on 26.08
B. Author the color on the **instance root** (or a stronger inherited opinion that applies to that instance) so the prototype stays shared
C. Edit the prototype mesh in place — that tints **every** instance
D. Set `instanceable = false` on the prototype prim

---

**M1-053** · COMP · Obj 1.9 · Difficulty: Medium · Type: Single choice

`UsdUtils.GetModelNameFromRootLayer(layer)` on a layer with **no** `defaultPrim` and two root prims `First` then `Second` returns:

A. `''` always
B. `'First'` — it falls back to the first root prim
C. `'Second'`
D. It raises `Tf.ErrorException`

---

**M1-054** · DE · Obj 4.6 · Difficulty: Medium · Type: Multiple select
Select two.

Validation on this book’s usd-core 26.8 venv:

A. `from pxr import UsdValidation` works (`ValidationRegistry`, `Validator`, …)
B. `UsdUtils.ComplianceChecker` exists
C. `hasattr(UsdUtils, "ComplianceChecker")` is `False`
D. The `usdchecker` CLI ships in the pip wheel

---

**M1-055** · DBG · Obj 6.2 · Difficulty: Medium · Type: Single choice

`/Lamp.radius` is `1` from a reference. A **specializes** class on the shot authors `9`. Why does the artist still see `1`?

A. Specializes are stronger than references, so this cannot happen
B. References beat specializes — the class opinion is weaker, so the referenced `1` wins
C. Specializes only work inside payloads
D. Numeric attributes cannot be specialized

---

**M1-056** · CUST · Obj 3.5 · Difficulty: Medium · Type: Multiple select
Select two.

A studio needs a **custom Ar resolver** that maps `hero://` URIs. Which statements are true?

A. Implement an Ar resolver plugin, declare it in `plugInfo.json`, and put it on the plugin path
B. `Ar.GetResolver()` remains the process-wide facade after the plugin loads
C. `AnchorRelativePath` is required public API on 26.08
D. Resolvers are registered with `Kind.Registry`

---

**M1-057** · COMP · Obj 1.11 · Difficulty: Medium · Type: Multiple select
Select two.

A monolithic `hero.usda` (geo, look, rig) must split for parallel workstreams. Which split matches OpenUSD practice?

A. Payload **geometry**, payload or reference **look**, keep a small interface layer with `defaultPrim`
B. Put every department into one root layer forever
C. Use sublayers inside the asset for department work; publish pinned USDC per stream
D. Replace composition with `Flatten()` as the only daily format

---

**M1-058** · DE · Obj 4.1 · Difficulty: Medium · Type: Single choice

Exporting USD to glTF, which fidelity issue is the exporter most responsible for documenting?

A. glTF will run LIVERPS the same way USD does, so composition can be ignored
B. Materials, units, and node hierarchy must be **mapped** — glTF has no LIVERPS; PreviewSurface/USDZ extras do not always round-trip
C. glTF automatically reads USDA variants
D. `metersPerUnit` is always 1 after conversion, so no note is needed

---

**M1-059** · PD · Obj 7.2 · Difficulty: Medium · Type: Single choice

What should a shot’s published identifier pin?

A. A floating `latest/` directory that mutates every hour
B. A **versioned** asset path (or resolver URI) that will still resolve the same bytes next month
C. A relative `./temp.usda` in an artist’s home directory
D. The usd-core git commit of whoever last saved

---

**M1-060** · DM · Obj 5.5 · Difficulty: Medium · Type: Python-reading

```{.python .norun}
from pxr import Usd, UsdGeom
s = Usd.Stage.CreateInMemory()
print(UsdGeom.GetStageUpAxis(s), UsdGeom.GetStageMetersPerUnit(s))
```

What prints on USD 26.08?

A. `Z 1.0`
B. `Y 0.01`
C. `Y 1.0`
D. `Z 0.01`

---

**M1-061** · DE · Obj 4.8 · Difficulty: Medium · Type: Single choice

A DCC importer sees `formatId == "usd"` but the file’s first bytes are `#usda 1.0`. What happened?

A. The file is corrupt
B. The `.usd` plugin owns the **extension**; the **contents** can still be USDA text (or crate)
C. `formatId` always matches the magic string
D. USD refuses to open USDA bytes under a `.usd` name

---

**M1-062** · CA · Obj 2.5 · Difficulty: Medium · Type: Single choice

An assembly instance-roots several component assets. You need to **remove** a property that lives on an instanced component without breaking instancing for the others. Where can you author that?

A. On the instance **proxy** mesh with `OverridePrim` — always legal
B. At the **instance root** (or by de-instancing that one root), not on descendant proxies
C. Only by editing every prototype in the crate
D. Only with `PointInstancer.invisibleIds`

---

**M1-063** · DBG · Obj 6.4 · Difficulty: Medium · Type: Single choice

A cube is in the stage but missing in the viewport. `imageable:purpose` is `proxy` and usdview is showing **render** purpose only. What is the likely cause?

A. `kind` must be `subcomponent`
B. Purpose **mismatch** — the gprim is excluded from the viewer’s purpose mask
C. `extent` is always required for purpose to work
D. Distant lights hide proxy purpose

---

**M1-064** · DE · Obj 4.7 · Difficulty: Medium · Type: Multiple select
Select two.

A first-pass component exporter should author which root-layer facts so downstream composition is predictable?

A. `defaultPrim`
B. `metersPerUnit` and `upAxis`
C. `Kind.Registry.Register` in the USDA header
D. `GetMaster` metadata

---

**M1-065** · PD · Obj 7.8 · Difficulty: Medium · Type: Multiple select
Select two.

When extending a DCC USD importer, which hooks belong in the design?

A. Map DCC nodes to typed USD prims / API schemas; preserve unknown properties as custom attributes or `customData`
B. Call `stage.Flatten()` on every import so the DCC never sees composition
C. Honor payloads vs references (working-set load) instead of always composing the heavy sculpt
D. Require `UsdMtlx` because usd-core always ships it

---

*End of Mock Exam 1. 65 questions. Check `mock-exams/mock01_answers.md` only after you have finished.*
