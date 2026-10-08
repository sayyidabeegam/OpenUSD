# Mock Exam 2 — NCP-OUSD Practice Paper

**Original practice exam. Not actual NVIDIA exam content.**

Verified against **USD 26.08** (`usd-core` 26.8). Difficulty: **medium-hard** (paper 2 of 3). Do not reuse Mock 1 answers by memory — several stems look similar and are not.

| | |
|---|---|
| Questions | 65 |
| Time | 120 minutes |
| Blueprint mix | COMP 15 · DE 10 · PD 9 · DM 8 · DBG 7 · CA 7 · VIS 5 · CUST 4 |
| Answers | `mock-exams/mock02_answers.md` — **do not open until you finish** |

USDA is always multiline. Python stems are `.norun`.

---

**M2-001** · COMP · Obj 1.5 · Difficulty: Hard · Type: USDA-reading

File: `paint.usda`

```usda
#usda 1.0
over "Pier"
{
    double length = 6
}
```

File: `layout.usda`

```usda
#usda 1.0
over "Pier"
{
    double length = 15
}
```

File: `harbor.usda`

```usda
#usda 1.0
(
    subLayers = [
        @./paint.usda@,
        @./layout.usda@
    ]
)
def Xform "Pier"
{
}
```

Composed `length` is `6`. The TD mutes `paint.usda`. What is `length` now?

A. `6` — mute cannot change composed values
B. `15` — the remaining weaker sublayer is now strongest
C. `None` — muting any sublayer invalidates the prim
D. `21` — USD adds the two opinions once mute “unlocks” addition

---

**M2-002** · DM · Obj 5.4 · Difficulty: Hard · Type: Python-reading

```{.python .norun}
from pxr import Usd
stage = Usd.Stage.CreateInMemory()
p = stage.GetPrimAtPath("/Missing")
print(bool(p), p.IsValid())
p.IsDefined()
```

What happens?

A. Prints `True True`, then `IsDefined()` returns `False`
B. Prints `False False`, then `IsDefined()` **raises `RuntimeError`**
C. Prints `False False`, then `IsDefined()` returns `False`
D. `GetPrimAtPath` raises before `print`

---

**M2-003** · DE · Obj 4.3 · Difficulty: Medium · Type: Multiple select
Select two.

On USD 26.08, `Tf.MakeValidIdentifier` produces:

A. `"2ball"` → `"_ball"`
B. `"Pier-Dock"` → `"Pier_Dock"`
C. `"2ball"` is already legal and is returned unchanged
D. Hyphens are kept (`"Pier-Dock"` unchanged)

---

**M2-004** · COMP · Obj 1.1 · Difficulty: Hard · Type: USDA-reading

```usda
#usda 1.0
def Sphere "Buoy" (
    prepend variantSets = "sea"
    variants = {
        string sea = "storm"
    }
)
{
    double radius = 3
    variantSet "sea" = {
        "storm" {
            double radius = 11
        }
        "calm" {
            double radius = 1
        }
    }
}
```

Composed `radius`?

A. `11` — the selected variant always beats a local opinion
B. `3` — **local** beats VariantSets in LIVERPS
C. `1` — USD picks the last variant block
D. `None` — local plus a selection is illegal

---

**M2-005** · CA · Obj 2.1 · Difficulty: Hard · Type: Python-reading

A PointInstancer already has prototype `/PI/Bush` at index 0. Which call puts `/PI/Tree` at **index 0** (Bush shifts to 1)?

A. `prototypes.AddTarget("/PI/Tree")` with no `position` (observed order on 26.08: Bush stays 0)
B. `prototypes.AddTarget("/PI/Tree", position=Usd.ListPositionFrontOfPrependList)`
C. `prototypes.AddTarget("/PI/Tree", position=Usd.ListPositionBackOfAppendList)`
D. `prototypes.SetTargets([])` then hope indices rewrite themselves

---

**M2-006** · PD · Obj 7.5 · Difficulty: Hard · Type: Multiple select
Select two.

A validator does `Ar.GetResolver().Resolve("./maps/rust.png")` from a random cwd and gets empty, while usdview shows the texture on a prim in `assets/cleat.usda`. Which pair is true on 26.08?

A. Composition anchored the asset path to **the layer**; naive `Resolve("./…")` uses **process cwd**
B. `AnchorRelativePath` is the supported 26.08 replacement on `Ar.Resolver`
C. `layer.ComputeAbsolutePath("./maps/rust.png")` (or `CreateIdentifier` + the layer’s `ResolvedPath`) is the layer-relative check
D. Identifiers starting with `./` are looked up on the resolver **search path**

---

**M2-007** · VIS · Obj 8.2 · Difficulty: Hard · Type: Python-reading

```{.python .norun}
from pxr import Usd, UsdLux
s = Usd.Stage.CreateInMemory()
sun = UsdLux.DistantLight.Define(s, "/Sun")
sun.GetIntensityAttr().Set(2)
sun.GetExposureAttr().Set(3)
print(sun.GetIntensityAttr().Get() * (2 ** sun.GetExposureAttr().Get()))
```

What prints (UsdLux brightness model: intensity × 2^exposure)?

A. `5`
B. `6`
C. `16`
D. `8`

---

**M2-008** · DBG · Obj 6.2 · Difficulty: Hard · Type: Single choice

`GetPropertyStack()` on `/Pier.length` returns specs from `paint.usda` (default `6`) then `layout.usda` (default `15`). What does that order mean?

A. Weakest first — layout wins
B. **Strongest first** — paint’s `6` is the composed value
C. Alphabetical by layer name
D. Stacks always include only the root layer

---

**M2-009** · COMP · Obj 1.8 · Difficulty: Hard · Type: USDA-reading

File: `skiff_a.usda`

```usda
#usda 1.0
(
    defaultPrim = "Skiff"
)
def Sphere "Skiff"
{
    double radius = 3
}
```

File: `skiff_b.usda`

```usda
#usda 1.0
(
    defaultPrim = "Skiff"
)
def Sphere "Skiff"
{
    double radius = 11
}
```

File: `work.usda`

```usda
#usda 1.0
def "Skiff" (
    prepend references = @./skiff_a.usda@
    append references = @./skiff_b.usda@
)
{
}
```

File: `shot.usda`

```usda
#usda 1.0
(
    subLayers = [
        @./work.usda@
    ]
)
over "Skiff" (
    delete references = @./skiff_a.usda@
)
{
}
```

Composed `radius` on `/Skiff`?

A. `3` — delete cannot remove a prepend
B. `11` — the stronger layer’s **delete** drops `skiff_a`; the remaining append wins
C. `None` — delete of a reference is illegal
D. `7` — the mean

---

**M2-010** · DM · Obj 5.1 / 8.1 · Difficulty: Hard · Type: Single choice

Parent `/P` authors constant `primvars:displayColor = [(0, 1, 0)]`. Child mesh `/P/M` does not. How does the child read that primvar?

A. `child.GetAttribute("displayColor")`
B. `UsdGeom.PrimvarsAPI(child).FindPrimvarWithInheritance("displayColor")`
C. Inheritance of primvars is impossible; copy the array onto every mesh
D. `UsdShade.MaterialBindingAPI(child).GetDisplayColor()`

---

**M2-011** · DE · Obj 4.6 · Difficulty: Medium · Type: Single choice

`UsdUtils.ComputeAllDependencies("entry.usda")` on a layer that sublayers `geo.usda` (asset `@./tex/wood.png@`) and authors `@./gone.jpg@` (missing). The 3-tuple’s last element contains:

A. `wood.png` only
B. `gone.jpg` (unresolved)
C. Both PNG and JPG as unresolved
D. Always `[]` — Compute never reports missing files

---

**M2-012** · COMP · Obj 1.7 · Difficulty: Hard · Type: Python-reading

```{.python .norun}
vs = prim.GetVariantSet("look")
print(repr(vs.GetVariantSelection()))
with vs.GetVariantEditContext():
    prim.CreateAttribute("mark", Sdf.ValueTypeNames.Double).Set(7)
```

Selection is still `''`. Where is `mark = 7` authored?

A. Inside every variant
B. Inside `"look"` automatically
C. As a **local** opinion on the prim (empty selection → context is not a variant)
D. The `with` block raises

---

**M2-013** · PD · Obj 7.2 · Difficulty: Medium · Type: Single choice

`UsdUtils.ExtractExternalReferences("set.usda")` where the file **references** `lamp.usda` and **payloads** `crate.usda` (no sublayers) returns:

A. `(layers, assets, unresolved)`
B. `([], ['./lamp.usda'], ['./crate.usda'])` — `(sublayers, refs+assets, payloads)`
C. A flat list of strings
D. Only payloads, because Extract ignores references

---

**M2-014** · CUST · Obj 3.4 · Difficulty: Hard · Type: Single choice

You need a **new typed Gprim** (`HarborBuoy`) versus a **non-destructive API** (`HarborTagAPI`) that can apply to existing meshes. Which bases?

A. Both inherit `UsdSchemaBase` only
B. Gprim: `UsdTyped` (often via `UsdGeomGprim`); API: `UsdAPISchemaBase`
C. Gprim: `UsdAPISchemaBase`; API: `UsdTyped`
D. Both must inherit `UsdPhysicsBase`

---

**M2-015** · CA · Obj 2.3 · Difficulty: Medium · Type: Multiple select
Select two.

Hiding PointInstancer instances efficiently:

A. Author `invisibleIds` (or activate an invis-id mask) — instance count **stays** the same
B. Delete those indices from `protoIndices` every frame
C. Deactivate the whole PointInstancer prim to hide one id
D. `invisibleIds` is a mask; it does not shrink `GetInstanceCount()`

---

**M2-016** · COMP · Obj 1.4 · Difficulty: Hard · Type: Python-reading

A shot sublayers `anim.usda` with `(offset = 10)`. You `SetEditTarget(stage.GetEditTargetForLocalLayer(anim))` then `attr.Set(1.0, 20)`. Where is the sample stored in `anim.usda`?

A. t=20 — edit targets ignore offsets
B. t=10 — `GetEditTargetForLocalLayer` maps stage time through the offset (`stageTime - offset` here)
C. t=30 — USD adds offset twice
D. The Set raises because offsets forbid authoring

---

**M2-017** · DM · Obj 5.6 · Difficulty: Medium · Type: Single choice

`UsdGeom.Mesh.Define` then `GetSubdivisionSchemeAttr().Get()` before anyone authors the attribute:

A. `None`
B. `none`
C. `catmullClark` (schema fallback)
D. `bilinear`

---

**M2-018** · VIS · Obj 8.2 · Difficulty: Hard · Type: Multiple select
Select two.

`UsdLux.DistantLight.Define(stage, "/Sun")` on a fresh stage:

A. `HasAPI(UsdLux.LightAPI)` is **True** (LightAPI is built in on the typed light)
B. `HasAPI(UsdLux.ShadowAPI)` is **False** until `ShadowAPI.Apply`
C. `ShapingAPI` is also built in (HasAPI True with no Apply)
D. DistantLight cannot apply ShadowAPI

---

**M2-019** · DBG · Obj 6.3 · Difficulty: Hard · Type: Single choice

```usda
#usda 1.0
def Xform "Alpha"
{
}
def Xform "Beta"
{
}
```

A shot does `prepend references = @./nodef.usda@` with **no** `defaultPrim` on that file and **no** explicit prim path. The composition error is:

A. `InvalidAssetPath` — the file cannot be opened
B. `UnresolvedPrimPath` / unresolved **defaultPrim** on an opened layer
C. Silent success; `/Hero` becomes `Alpha`
D. `Tf.MallocTag`

---

**M2-020** · COMP · Obj 1.3 · Difficulty: Hard · Type: Single choice

Same file referenced by `/A` and payloaded by `/B`. `Usd.Stage.Open(path, Usd.Stage.LoadNone)`:

A. `/A` child geo missing; `/B` child geo present
B. `/A` child geo **present** (references still load); `/B` child geo **missing**
C. Both missing
D. `Open(..., LoadNone)` is not valid — must use `OpenMasked`

---

**M2-021** · DE · Obj 4.7 · Difficulty: Hard · Type: Multiple select
Select two.

`stage.Flatten()` of a shot that references `lantern.usda` and sublayers notes:

A. Flattened lantern prim **no longer holds** the reference list (baked)
B. Department notes from the sublayer **are baked** into the flattened root
C. Flatten **keeps** live references and only drops sublayers
D. Flatten refuses if any attribute has time samples

---

**M2-022** · PD · Obj 7.4 · Difficulty: Medium · Type: Single choice

`stage.SetEditTarget(Sdf.Layer.CreateAnonymous("elsewhere"))` when that layer is **not** in the local layer stack:

A. Silently authors into the anonymous layer
B. Raises `Tf.ErrorException` (not in the local LayerStack)
C. Redirects to the session layer
D. Converts the stage to USDA

---

**M2-023** · CA · Obj 2.4 · Difficulty: Hard · Type: USDA-reading

```usda
#usda 1.0
def "Dock"
{
}

over "Jetty"
{
}
```

Which pair matches USD 26.08?

A. `/Dock` is defined (typeless); `/Jetty` `IsDefined()` is **False** but `bool(prim)` can still be **True**
B. Both are null prims (`bool` False)
C. `/Jetty` is defined because `over` always defines
D. `/Dock` fails to parse without a type

---

**M2-024** · COMP · Obj 1.8 · Difficulty: Hard · Type: USDA-reading

File: `lantern.usda`

```usda
#usda 1.0
(
    defaultPrim = "Lantern"
)
def Xform "Lantern"
{
    def Sphere "Globe"
    {
        double radius = 1
    }
}
```

File: `shot.usda`

```usda
#usda 1.0
def "Hero" (
    prepend references = @./lantern.usda@
)
{
    over "Globe"
    {
        double radius = 4
    }
}
```

Composed `/Hero/Globe.radius`?

A. `1` — you cannot over a referenced child
B. `4` — a local over on the composed child path wins
C. `None` — name mismatch with defaultPrim
D. `5` — sum

---

**M2-025** · DM · Obj 5.2 · Difficulty: Medium · Type: Single choice

A vertex `primvars:displayColor` has 2 color samples and `SetIndices([0, 1, 0, 1])`. `IsIndexed()` is:

A. `False` — indices are only for `faceVertexIndices`
B. `True` — four corners share two stored colors
C. Illegal — index length must equal face count
D. `True` only for `uniform` interpolation

---

**M2-026** · VIS · Obj 8.4 · Difficulty: Hard · Type: Single choice

UsdPreviewSurface reads a **UV** texture. Which reader/texture pair is the usual network?

A. `UsdPrimvarReader_float2` (`varname` = `st`) → `UsdUVTexture` → PreviewSurface `diffuseColor`
B. `UsdPrimvarReader_float3` (`varname` = `st`)
C. `UsdUVTexture` with `varname` = `displayColor` and no reader
D. `UsdMtlx` node, because usd-core always includes MaterialX

---

**M2-027** · PD · Obj 7.3 · Difficulty: Medium · Type: Single choice

You need a **single layer** that still **references** published components (not baked), with department sublayers collapsed. API?

A. `stage.Flatten()`
B. `UsdUtils.FlattenLayerStack(stage)`
C. `Usd.Stage.OpenMasked`
D. `Sdf.ChangeBlock`

---

**M2-028** · COMP · Obj 1.2 · Difficulty: Medium · Type: Single choice

`Usd.Stage.Open("huge.usda", mask=["/World/Ferry"])` on usd-core 26.8:

A. Opens only `/World/Ferry`
B. **Fails / TypeError** — population masks use `OpenMasked` + `Usd.StagePopulationMask`, not an `Open(..., mask=)` kwarg
C. Equivalent to `LoadNone`
D. Equivalent to muting every other layer

---

**M2-029** · DBG · Obj 6.1 · Difficulty: Hard · Type: Single choice

You must author a **new** child `/Harbor/Winch` (no spec yet) while a `Sdf.ChangeBlock` is already active. Safest 26.08 practice?

A. `DefinePrim` inside the block — always succeeds
B. Close the block (or never open it) before `DefinePrim` of a brand-new path; defining a new child **inside** a live block can raise `Tf.ErrorException`
C. Switch to `OverridePrim` inside the block to create defs
D. ChangeBlock only wraps `MuteLayer`

---

**M2-030** · DE · Obj 4.2 · Difficulty: Medium · Type: Single choice

A mapping doc must relate UsdPreviewSurface `diffuseColor` to a MaterialX / glTF base color. On this usd-core venv, `from pxr import UsdMtlx`:

A. Succeeds; UsdMtlx is in usd-core 26.8
B. **ImportError** — conceptual mapping is still required; the MaterialX USD plugin is not in this wheel
C. Succeeds only after `Kind.Registry.Register`
D. Succeeds and registers Hydra SceneIndexes

---

**M2-031** · CA · Obj 2.1 · Difficulty: Hard · Type: Python-reading

```{.python .norun}
rel.AddTarget("/PI/Bush")
rel.AddTarget("/PI/Tree", position=Usd.ListPositionBackOfAppendList)
rel.AddTarget("/PI/Rock")  # default position
print(list(rel.GetTargets()))
```

On 26.08 this prints:

A. `['/PI/Rock', '/PI/Bush', '/PI/Tree']`
B. `['/PI/Bush', '/PI/Rock', '/PI/Tree']`
C. `['/PI/Bush', '/PI/Tree', '/PI/Rock']`
D. `['/PI/Tree', '/PI/Bush', '/PI/Rock']`

---

**M2-032** · COMP · Obj 1.6 · Difficulty: Hard · Type: Multiple select
Select two.

LIVERPS two-step resolution:

A. Strength **inside a layer stack** (sublayer order, list-ops) is decided first for each arc
B. Then arcs are compared: Local > Inherits > VariantSets > rElocates > References > Payloads > Specializes
C. Specializes beat references
D. Value clips are the “C” in LIVERPS

---

**M2-033** · DM · Obj 5.5 · Difficulty: Hard · Type: Single choice

Parent `/H` has `visibility = invisible`. Child cube `/H/C` never authors visibility. `GetVisibilityAttr().Get()` on the child vs `ComputeVisibility()`:

A. Both `invisible`
B. Get → `inherited`; Compute → `invisible`
C. Get → `invisible`; Compute → `inherited`
D. Both `None`

---

**M2-034** · CUST · Obj 3.1 · Difficulty: Medium · Type: Single choice

A C++ schema plugin built against USD 24.11 is `dlopen`’d into a process that loaded usd-core **26.8**. Likely result?

A. Always fine — Python wheels hide ABI
B. **ABI mismatch** — plugins must match the USD the process loaded
C. Fine if `plugInfo.json` lists both versions
D. Fine if you `MuteLayer` the plugin path

---

**M2-035** · PD · Obj 7.6 · Difficulty: Medium · Type: Single choice

Read a producer key stored as `customData["show"] = "harbor"`:

A. `prim.GetMetadata("show")`
B. `prim.GetCustomDataByKey("show")` (or `GetCustomData()["show"]`)
C. `prim.GetKind()`
D. `Ar.GetResolver().Resolve("show")`

---

**M2-036** · COMP · Obj 1.9 · Difficulty: Hard · Type: Single choice

A layer has **no** `defaultPrim`, root prims `Ferry` then `Barge`. `UsdUtils.GetModelNameFromRootLayer(layer)` returns:

A. `''`
B. `'Ferry'` (first root prim fallback)
C. `'Barge'`
D. Raises

---

**M2-037** · VIS · Obj 8.3 · Difficulty: Hard · Type: Single choice

A parent mesh binds a material `strongerThanDescendants`. A child subset also binds a different material. Who wins on the subset?

A. The child subset — descendants always win
B. The **parent** bind — `strongerThanDescendants` beats descendant bindings
C. Neither — USD averages shader parameters
D. Binding strength is ignored unless `HasAPI` is false

---

**M2-038** · DBG · Obj 6.5 · Difficulty: Medium · Type: Multiple select
Select two.

Live diagnostics while `Open` spews repeated asset warnings:

A. Install `UsdUtils.CoalescingDiagnosticDelegate` **before** `Open`
B. `Tf.Debug.SetDebugSymbolsByName("USD_CHANGES", True)` (or `TF_DEBUG=USD_CHANGES`) for change chatter
C. `UsdGeom.Tokens.Z` enables diagnostics
D. `GetMaster()` dumps the layer stack

---

**M2-039** · DE · Obj 4.4 · Difficulty: Hard · Type: Multiple select
Select two.

Round-tripping a DCC node named `"2ball"`:

A. Export as `Tf.MakeValidIdentifier` → `_ball`; stash `"2ball"` in `customData`
B. Keep the USDA identifier `2ball` — leading digits are legal prim names
C. Author `metersPerUnit` / `upAxis` and document that **references do not auto-convert**
D. Skip `defaultPrim` so the importer can guess

---

**M2-040** · COMP · Obj 1.1 · Difficulty: Hard · Type: USDA-reading

File: `asset.usda` — `def Xform "Winch" { double load = 2 }` with `defaultPrim = "Winch"`.

Shot:

```usda
#usda 1.0
class "_Load"
{
    double load = 11
}

def "Winch" (
    prepend references = @./asset.usda@
    prepend specializes = </_Load>
)
{
}
```

Composed `load`?

A. `11` — specializes beat references
B. `2` — references beat specializes
C. `None`
D. `13`

---

**M2-041** · DM · Obj 5.3 · Difficulty: Medium · Type: Single choice

`userDocBrief` vs `customData["assetId"]`:

A. Same field
B. `userDocBrief` / `documentation` are human-facing metadata; `customData` is a producer dictionary
C. `userDocBrief` registers a schema
D. `customData` can only live on the root layer metadata, never on a prim

---

**M2-042** · CA · Obj 2.2 · Difficulty: Hard · Type: Single choice

Tint **one** native instance without `SetInstanceable(False)` and without editing the shared prototype mesh:

A. `stage.OverridePrim("/Instance/Mesh")` and set displayColor on the proxy
B. Author `primvars:displayColor` (or an inherit) on the **instance root**
C. Edit `/__Prototype_1/Mesh` — that affects only that instance
D. Set `kind = "subcomponent"` on the proxy

---

**M2-043** · PD · Obj 7.7 · Difficulty: Hard · Type: Single choice

`PXR_PLUGINPATH_NAME` is how a pipeline injects `plugInfo.json` trees. If it is unset, `Plug.Registry.GetInstance().RegisterPlugins("/studio/plugin")` from Python:

A. Cannot work — the env var is the only mechanism
B. Can still register a path at runtime (lab pattern); the env var is the process-wide default search
C. Registers kinds only, not file formats
D. Silently installs SceneIndex plugins from usd-core

---

**M2-044** · COMP · Obj 1.7 · Difficulty: Medium · Type: Single choice

`prim.GetVariantSets().GetNames()` vs `prim.GetVariantSet("look").GetVariantNames()`:

A. They are aliases
B. `GetNames()` → variant **set** names (`['look']`); `GetVariantNames()` → names **inside** that set (`['green', 'red']`)
C. `GetNames()` lists variant values; `GetVariantNames()` lists set names
D. Only `GetMaster()` lists variants

---

**M2-045** · DBG · Obj 6.4 · Difficulty: Hard · Type: Single choice

A mesh is present in `Traverse` but missing in usdview. `purpose` is `guide`; the viewer shows **default+render** only. Cause?

A. `kind` must be `group`
B. **Purpose filter** — `guide` is excluded from that viewer mask
C. Missing `extent` always culls guide purpose
D. DistantLight intensity 50000 hides guides

---

**M2-046** · DE · Obj 4.8 · Difficulty: Medium · Type: Multiple select
Select two.

A file named `hero.usd` starts with `#usda 1.0`. Which are true on 26.08?

A. `GetFileFormat().formatId` is `usd` (the **extension** plugin)
B. The layer still opens; prims and values are there (contents are USDA text)
C. `formatId` becomes `usda` because the first line is `#usda`
D. USD refuses to open USDA bytes under a `.usd` name

---

**M2-047** · VIS · Obj 8.2 · Difficulty: Medium · Type: Multiple select
Select two.

Fresh `UsdLux.DistantLight` color-temperature fallbacks on 26.08:

A. `GetEnableColorTemperatureAttr().Get()` is `False`
B. `GetColorTemperatureAttr().Get()` is `6500`
C. Enable defaults to `True`, so Kelvin always affects the light
D. Color temperature fallback is `None` until set

---

**M2-048** · CUST · Obj 3.8 · Difficulty: Hard · Type: Single choice

A procedural Ar resolver should generate **in-memory** renderable prims from `proc://` URIs. That job is:

A. The same as a Hydra SceneIndex (and ships in usd-core)
B. An **Ar resolver plugin** (identifier → asset / layer bytes); SceneIndex is a separate imaging-time job and needs an imaging build
C. `Kind.Registry` callbacks
D. `Sdf.ChangeBlock` only

---

**M2-049** · COMP · Obj 1.5 · Difficulty: Hard · Type: Multiple select
Select two.

Authoring into a department layer without clobbering the shot root:

A. `stage.SetEditTarget(departmentLayer)` when that layer is in the local stack
B. `Usd.EditContext(stage, departmentLayer)` for a scoped change that restores the previous target
C. Always `CreateNew` a second root layer and hope composition finds it
D. `GetPrototype()` switches edit targets

---

**M2-050** · DM · Obj 5.2 · Difficulty: Hard · Type: Python-reading

Samples at 2 → `(0,0,0)` and 8 → `(6,0,0)`. Interpolation **linear**. `attr.Get(4)`?

A. `(0, 0, 0)`
B. `(2, 0, 0)`
C. `(6, 0, 0)`
D. `None`

---

**M2-051** · PD · Obj 7.1 · Difficulty: Medium · Type: Single choice

Python stand-in for `usdcat layer.usda -o out.usda` in this venv (no CLI tools):

A. `os.system("usdcat ...")` — the binary ships with usd-core
B. `Sdf.Layer.FindOrOpen(...).Export("out.usda")` (or `stage.GetRootLayer().Export`)
C. `UsdUtils.CreateNewUsdzPackage` only
D. `Kind.Registry.GetAllKinds()`

---

**M2-052** · CA · Obj 2.4 · Difficulty: Medium · Type: Multiple select
Select two.

`UsdGeom.PointInstancer` on USD 26.08:

A. It is a `UsdGeomGprim` (a gprim)
B. It is `UsdGeomBoundable`
C. It is **not** a Gprim
D. It is a `UsdShadeNodeGraph`

---

**M2-053** · COMP · Obj 1.11 · Difficulty: Hard · Type: Multiple select
Select two.

Splitting a monolithic `trawler.usda` (geo + look + rig) for parallel work:

A. Payload heavy geo; keep a small interface layer with `defaultPrim`
B. Department **sublayers** for look vs rig; publish pinned USDC
C. One shared root layer with no arcs so Git never merges
D. Replace daily work with `Flatten()` so composition never runs

---

**M2-054** · DE · Obj 4.5 · Difficulty: Hard · Type: Single choice

An exporter writes extra `custom float studio:lod = 2` on a Mesh (no studio schema plugin loaded downstream). Downstream `GetAttribute("studio:lod").Get()`?

A. Always `None` — unknown namespaces are dropped
B. The **custom attribute still composes** as a property; the typed schema is optional for storage
C. USD refuses to open the layer
D. It is converted to `primvars:studio:lod` automatically

---

**M2-055** · DBG · Obj 6.2 · Difficulty: Hard · Type: Single choice

A department over on `/Hero/Globe.radius` does not show. `GetPropertyStack` lists the over, then a **local** default on a stronger sublayer, then the referenced sample. Why is the over losing?

A. Overs cannot override references
B. A **stronger local** opinion in a stronger stack position beats the department over (same LIVERPS step: local layer-stack strength)
C. References always beat local
D. `GetPropertyStack` is unordered trivia

---

**M2-056** · CUST · Obj 3.2 · Difficulty: Medium · Type: Multiple select
Select two.

Building OpenUSD from source for a DCC that needs MaterialX and Hydra:

A. usd-core **pip** is not that build — it has no `UsdMtlx`, `UsdImaging`, or CLI
B. Enable the imaging/MaterialX options in the OpenUSD build; match the DCC’s compiler/ABI
C. `Kind.Registry.Register` replaces CMake
D. Copying `plugInfo.json` from usd-core enables Hydra

---

**M2-057** · COMP · Obj 1.10 · Difficulty: Hard · Type: Single choice

Remove a property from **one** instanced component in an assembly without de-instancing every copy:

A. `OverridePrim` on the instance-proxy mesh descendant
B. Author at the **instance root** (or de-instance **that** root only)
C. Mute the assembly root layer
D. `GetMaster().Clear()` 

---

**M2-058** · DE · Obj 4.1 · Difficulty: Medium · Type: Single choice

glTF export of a USD asset with variants and payloads. The fidelity note should say:

A. glTF evaluates LIVERPS natively
B. You must **compose or bake** a chosen working set (variant selections, loaded payloads) — glTF has no payloads/variants
C. USDZ and glTF are the same bytes
D. `metersPerUnit` is ignored in every converter

---

**M2-059** · PD · Obj 7.8 · Difficulty: Hard · Type: Multiple select
Select two.

DCC importer design on 26.08:

A. Map DCC nodes to typed prims / applied API schemas; keep unknowns as custom properties or `customData`
B. Honor **payload vs reference** so the DCC can load a working set
C. `import pxr.UsdMtlx` is guaranteed
D. Call `GetMaster()` for every instance

---

**M2-060** · DM · Obj 5.5 · Difficulty: Medium · Type: Python-reading

```{.python .norun}
from pxr import Usd, UsdGeom
xf = UsdGeom.Xform.Define(Usd.Stage.CreateInMemory(), "/X")
xf.AddTranslateOp().Set((1, 0, 0))
print(list(xf.GetXformOpOrderAttr().Get()))
```

Prints:

A. `[]`
B. `['xformOp:translate']`
C. `['translate']`
D. `None`

---

**M2-061** · DE · Obj 4.3 · Difficulty: Medium · Type: Single choice

`UsdUtils.CreateNewUsdzPackage` ZIP `compress_type` on 26.08:

A. `ZIP_DEFLATED` (8)
B. `ZIP_STORED` (0)
C. `ZIP_BZIP2`
D. Mixed per file type

---

**M2-062** · CA · Obj 2.5 · Difficulty: Hard · Type: Single choice

`UsdGeom.ModelAPI` draw modes (`cards`, `bounds`, …) apply to:

A. Every gprim, including shapeless overs
B. **Model** prims (component/assembly with a valid model hierarchy) as a cheap viz stand-in
C. PointInstancer proto indices only
D. Materials only

---

**M2-063** · DBG · Obj 6.5 · Difficulty: Medium · Type: Single choice

`Tf.MallocTag.GetTotalBytes()` on this pip wheel often returns 0. Why?

A. USD never allocates
B. The wheel was **not built with malloc tagging**; use Trace for timelines instead of trusting bytes
C. You must call `GetMaster()` first
D. MallocTag only works inside `ChangeBlock`

---

**M2-064** · DE · Obj 4.7 · Difficulty: Medium · Type: Multiple select
Select two.

A component exporter’s root layer should include:

A. `defaultPrim`
B. `metersPerUnit` and `upAxis`
C. `Kind.Registry.Register` in the USDA header
D. A `GetMaster` metadata block

---

**M2-065** · PD · Obj 7.2 · Difficulty: Hard · Type: Single choice

`ComputeAllDependencies` vs `ExtractExternalReferences` — which walks **closure** (sublayers + refs + payloads + texture assets, with unresolved listed separately)?

A. Extract (one file only)
B. **ComputeAllDependencies** → `(layers, assets, unresolved)`
C. Both are identical
D. Only `FlattenLayerStack`

---

*End of Mock Exam 2. 65 questions. Check `mock-exams/mock02_answers.md` only after you have finished.*
