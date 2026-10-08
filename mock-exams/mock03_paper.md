# Mock Exam 3 — NCP-OUSD Practice Paper

**Original practice exam. Not actual NVIDIA exam content.**

Verified against **USD 26.08** (`usd-core` 26.8). Difficulty: **hard** (paper 3 of 3). Heavier USDA-reading and debugging. Mock 1/2 answers will mislead you on several stems.

| | |
|---|---|
| Questions | 65 |
| Time | 120 minutes |
| Blueprint mix | COMP 15 · DE 10 · PD 9 · DM 8 · DBG 7 · CA 7 · VIS 5 · CUST 4 |
| Answers | `mock-exams/mock03_answers.md` — **do not open until you finish** |

This book’s Mock 3 readiness bar is **≥ 80% (52/65)** and **≥ 70% in every domain**. NVIDIA does not publish a passing score.

USDA is always multiline. Python stems are `.norun`.

---

**M3-001** · COMP · Obj 1.5 · Difficulty: Hard · Type: USDA-reading

Files `s1.usda` / `s2.usda` / `s3.usda` each `over "Anvil" { double mass = N }` with N = 1, 2, 3 respectively (multiline overs). Root:

```usda
#usda 1.0
(
    subLayers = [
        @./s1.usda@,
        @./s2.usda@,
        @./s3.usda@
    ]
)
def Xform "Anvil"
{
}
```

Composed `mass`?

A. `3` — last sublayer wins
B. `1` — first listed sublayer is strongest
C. `2` — the middle layer is the “active” edit target by default
D. `None` — three overs of the same field is an error

---

**M3-002** · DM · Obj 5.5 · Difficulty: Hard · Type: Python-reading

Samples at 0 → `(0,0,0)` and 10 → `(10,0,0)`. Both **held** and **linear**. `attr.Get(99)`?

A. Held `(10,0,0)`; linear `None`
B. Both `(10, 0, 0)` — after the last sample, both modes hold the last value
C. Both `(0, 0, 0)`
D. Linear `(99, 0, 0)`

---

**M3-003** · DE · Obj 4.5 · Difficulty: Hard · Type: Single choice

UsdLux on 26.08: `DistantLight.GetIntensityAttr().GetName()` is:

A. `intensity`
B. `inputs:intensity` (UsdLux attributes are namespaced)
C. `inputs:intensity:value`
D. `lux:intensity`

---

**M3-004** · COMP · Obj 1.1 · Difficulty: Hard · Type: USDA-reading

```usda
#usda 1.0
class "_H"
{
    double heat = 8
}

def Sphere "Forge" (
    prepend inherits = </_H>
    prepend variantSets = "fire"
    variants = {
        string fire = "hot"
    }
)
{
    variantSet "fire" = {
        "hot" {
            double heat = 2
        }
        "cold" {
            double heat = 0
        }
    }
}
```

Composed `heat`?

A. `2` — the selected variant beats inherits
B. `8` — **Inherits beat VariantSets**
C. `0` — last variant block
D. `10` — sum

---

**M3-005** · CA · Obj 2.4 · Difficulty: Hard · Type: USDA-reading

```usda
#usda 1.0
def Xform "Proto"
{
    def Cube "Body"
    {
    }
}

def Xform "Vise" (
    instanceable = true
    prepend references = </Proto>
)
{
}
```

After `prim.SetInstanceable(False)` on `/Vise`:

A. Still an instance; `GetPrototype()` still returns `/__Prototype_1`
B. `IsInstance()` is **False**; `/Vise/Body` is defined and **not** an instance proxy
C. `/Vise/Body` disappears
D. `SetInstanceable` raises on 26.08

---

**M3-006** · PD · Obj 7.5 · Difficulty: Hard · Type: Multiple select
Select two.

`stage.MuteLayer(s1_identifier)` where `s1` was the strongest sublayer (`mass = 1`, weaker `mass = 2`):

A. Composed `mass` becomes `2`
B. `GetLayerStack()` **omits** the muted layer
C. `GetLayerStack()` still lists it, only `GetMutedLayers()` changes
D. Mute deletes the file on disk

---

**M3-007** · VIS · Obj 8.4 · Difficulty: Hard · Type: Python-reading

A material’s PreviewSurface shader is connected with `CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")`. `len(material.ComputeSurfaceSource())` and the first tuple element?

A. `1`, the Material prim
B. `3`, and index 0 is the **connected UsdShade.Shader**
C. `0`, always empty until you flatten
D. `2`, shader id and material path

---

**M3-008** · DBG · Obj 6.5 · Difficulty: Hard · Type: Python-reading

```{.python .norun}
# listener records ObjectsChanged
stage.DefinePrim("/N")
# then:
prim.CreateAttribute("f", Sdf.ValueTypeNames.Float).Set(1.0)
```

Resynced paths vs changed-info-only paths:

A. DefinePrim: resync `['/N']`; Set: info-only `['/N.f']` (no resync)
B. Both operations only resync `/`
C. Set resyncs `/N`; DefinePrim is info-only
D. Notices never fire for in-memory stages

---

**M3-009** · COMP · Obj 1.1 · Difficulty: Hard · Type: USDA-reading

`cls.usda` (stronger sublayer) defines `Forge` with `prepend inherits = </_H>` and class `_H { double heat = 8 }`. Weaker sublayer `localweak.usda`:

```usda
#usda 1.0
over "Forge"
{
    double heat = 2
}
```

Composed `heat`?

A. `8` — the stronger sublayer’s inherit wins
B. `2` — a **local** opinion beats inherits even when it lives in a **weaker** sublayer
C. `None` — mixed arcs on one field fail
D. `5`

---

**M3-010** · DM · Obj 5.6 · Difficulty: Hard · Type: Python-reading

Mesh points `[(0,0,0), (2,0,0), (0,3,0)]`, one triangle (`faceVertexCounts = [3]`, indices `[0,1,2]`). `ComputeExtentFromPlugins` returns:

A. `[(0,0,0), (3,3,3)]`
B. `[(0, 0, 0), (2, 3, 0)]`
C. `None` until `extent` is authored
D. `[(0,0,0), (2,0,0)]` — Z is ignored

---

**M3-011** · DE · Obj 4.7 · Difficulty: Hard · Type: Single choice

A DCC writes `custom float studio:lod = 2` on a Mesh. Downstream has **no** studio schema plugin. `GetAttribute("studio:lod").Get()`?

A. `None` — unknown namespaces are stripped
B. `2` — custom attributes persist without a schema
C. The layer fails to open
D. Auto-converted to `primvars:studio:lod`

---

**M3-012** · COMP · Obj 1.8 · Difficulty: Hard · Type: USDA-reading

File: `rig.usda` (defaultPrim `Mill`) has `/Mill/Rig/Arm` Cube `size = 1`. Shot:

```usda
#usda 1.0
(
    relocates = {
        </World/Mill/Rig/Arm>: </World/Mill/Arm>
    }
)
def "Mill" (
    prepend references = @./rig.usda@
)
{
    over "Arm"
    {
        double size = 7
    }
}
```

What is true?

A. Relocates succeed; `/Mill/Rig/Arm` is gone; `/Mill/Arm` size 7
B. Relocates **source path does not match** the composed prim (`/Mill/...` not `/World/Mill/...`), so they are ignored; `/Mill/Rig/Arm` still exists (`size` 1) and `/Mill/Arm` is a **sibling over** (`size` 7)
C. The layer fails to parse
D. Relocates always prefix `/World` automatically

---

**M3-013** · PD · Obj 7.2 · Difficulty: Hard · Type: Single choice

`GetPrimStack()` on `/Anvil` in a root-with-two-sublayers stage. Order of layer display names (strongest first) is:

A. Weakest sublayer, then stronger, then root
B. **Root, then stronger sublayer, then weaker** (`root3.usda`, `s1.usda`, `s2.usda`)
C. Random
D. Only the muted layers

---

**M3-014** · CUST · Obj 3.6 · Difficulty: Hard · Type: Single choice

A studio needs collision properties on existing meshes without a new Gprim type. 26.08:

A. `UsdPhysics.CollisionAPI.Apply(prim)` (API schema)
B. `Kind.Registry.Register("collision")`
C. Inherit `UsdPhysicsBase` in USDA
D. Set `purpose = physics`

---

**M3-015** · CA · Obj 2.3 · Difficulty: Hard · Type: Multiple select
Select two.

A PointInstancer has 4 instances; `invisibleIds = [0, 3]`. Which are true?

A. `GetInstanceCount()` is still `4`
B. `GetInstanceCount()` becomes `2`
C. Ids 0 and 3 are masked from drawing
D. `protoIndices` is rewritten to length 2

---

**M3-016** · COMP · Obj 1.3 · Difficulty: Hard · Type: USDA-reading

```usda
#usda 1.0
def "Heavy" (
    prepend payload = @./geo.usda@
)
{
    over "Ball"
    {
        double radius = 5
    }
}
```

`geo.usda` defaultPrim `G` with child `Sphere "Ball"` `radius = 1`. Open with **`LoadNone`**. `/Heavy/Ball`?

A. Missing (`bool` False) — payloads do not compose
B. **Present** with `radius = 5` — the **local over** exists even while the payload is unloaded
C. Present with `radius = 1` — payload still loads
D. Raises

---

**M3-017** · DM · Obj 5.1 / 8.1 · Difficulty: Hard · Type: Single choice

Vertex `primvars:displayColor` on a parent Xform; child Mesh has none. The call that finds the parent’s primvar is:

A. `child.GetAttribute("displayColor")`
B. `UsdGeom.PrimvarsAPI(child).FindPrimvarWithInheritance("displayColor")`
C. `UsdShade.Material(child).GetDisplayColor()`
D. Inheritance of primvars is forbidden

---

**M3-018** · VIS · Obj 8.2 · Difficulty: Hard · Type: Multiple select
Select two.

UsdLux **namespacing** and APIs on a typed DistantLight:

A. Intensity is `inputs:intensity`
B. `LightAPI` is already applied (HasAPI True)
C. `ShadowAPI` is already applied
D. Attribute name is bare `intensity` (no `inputs:`)

---

**M3-019** · DBG · Obj 6.3 · Difficulty: Hard · Type: Single choice

`two.usda` has root prims `Alpha` (`k=1`) and `Beta` (`k=2`), **no** defaultPrim. Shot: `prepend references = @./two.usda@</Beta>`. Composed `/Hero.k`?

A. `None` — missing defaultPrim always fails
B. `2` — the **explicit prim path** selects Beta
C. `1` — first root prim always wins
D. `InvalidAssetPath`

---

**M3-020** · COMP · Obj 1.4 · Difficulty: Hard · Type: Single choice

Two crowd agents reference the same `walk.usda`. Agent A: `offset = 0`. Agent B: `offset = 4`, `scale = 1`. Sample stored at layer time 10 appears on B at composed time:

A. `10`
B. `14` (`offset + scale * layerTime`)
C. `6`
D. `4`

---

**M3-021** · DE · Obj 4.6 · Difficulty: Hard · Type: Multiple select
Select two.

`ComputeAllDependencies` on a layer that sublayers `geo.usda` (resolves `wood.png`) and authors missing `@./gone.jpg@`:

A. `wood.png` is in the **assets** list
B. `gone.jpg` is in the **unresolved** list
C. Both files are unresolved
D. Compute returns a single flat list of strings

---

**M3-022** · PD · Obj 7.4 · Difficulty: Hard · Type: Single choice

You `Set(1.0, 20)` with `GetEditTargetForLocalLayer(anim)` where `anim` is a sublayer with `offset = 10`. Sample in `anim.usda` is at:

A. `20`
B. `10`
C. `30`
D. The Set is rejected

---

**M3-023** · CA · Obj 2.2 · Difficulty: Hard · Type: Single choice

Color **one** native instance of `/Vise` without de-instancing and without editing `/__Prototype_1/Body`:

A. `OverridePrim("/Vise/Body")` then set displayColor
B. Author `primvars:displayColor` on **`/Vise`** (instance root)
C. Edit the prototype mesh — it only affects this instance
D. `GetMaster().GetPrim().SetDisplayColor`

---

**M3-024** · COMP · Obj 1.7 · Difficulty: Hard · Type: USDA-reading

Asset `Tongs` has variant set `size` selected `sm` (`span = 1`) and variant `lg` (`span = 8`). Shot:

```usda
#usda 1.0
def "Tongs" (
    prepend references = @./varasset.usda@
    variants = {
        string size = "lg"
    }
)
{
}
```

Composed `span`?

A. `1` — asset selection is stronger than the shot
B. `8` — the **referencing prim’s variant selection** is a stronger local opinion than the asset’s selection
C. `None` — two selections cancel
D. `9`

---

**M3-025** · DM · Obj 5.4 · Difficulty: Hard · Type: Multiple select
Select two.

Relationship `/A.r` targets `/B.r`; `/B.r` targets `/C`. On 26.08:

A. `GetTargets()` → `['/B.r']`
B. `GetForwardedTargets()` → `['/C']`
C. `GetTargets()` already returns `/C`
D. Forwarding requires `Kind.Registry`

---

**M3-026** · VIS · Obj 8.3 · Difficulty: Hard · Type: Single choice

A `UsdGeom.Subset` under a Mesh should receive its own material. Where is the binding authored?

A. Only on the Mesh — subsets cannot bind
B. On the **Subset** prim (`MaterialBindingAPI` Apply + Bind), typically `weakerThanDescendants` on the parent if the parent also binds
C. On the Material, targeting the subset via `GetMaster`
D. Only via PointInstancer `invisibleIds`

---

**M3-027** · PD · Obj 7.3 · Difficulty: Hard · Type: Single choice

You must **bake references** (external parties cannot see your component files) but you are fine collapsing sublayers too:

A. `UsdUtils.FlattenLayerStack` — keeps references
B. `stage.Flatten()` — bakes references
C. `MuteLayer` on every reference
D. `OpenMasked`

---

**M3-028** · COMP · Obj 1.9 · Difficulty: Hard · Type: Single choice

Preparing an internal mill asset for an external vendor. Which pair is the usual delivery?

A. Leave live `hero://` resolver URIs and unpublished work layers
B. **Localize** (or Flatten) so all needed layers/assets resolve, pin versions, set `defaultPrim`
C. Ship only a `.py` that rebuilds the stage
D. Strip `metersPerUnit` so the vendor’s DCC guesses

---

**M3-029** · DBG · Obj 6.2 · Difficulty: Hard · Type: Single choice

`GetPropertyStack` on `heat` lists: weaker-sublayer local spec `2`, then inherit node `8`. Composed value is `2`. Why is inherit listed at all?

A. Stacks are a bug
B. Weaker opinions **remain in the stack** for debugging; LIVERPS already picked local
C. Inherit actually wins; the stack is reverse order
D. `GetPropertyStack` only lists the winner

---

**M3-030** · DE · Obj 4.2 · Difficulty: Hard · Type: Single choice

A mapping table lists UsdPreviewSurface `metallic` ↔ glTF `metallicFactor` ↔ a MaterialX `metalness` input. `import pxr.UsdMtlx` on this venv:

A. Required for the table to be valid
B. **Fails** — the table is still the right artifact; the plugin is not in usd-core
C. Registers the mapping automatically
D. Converts glTF at import

---

**M3-031** · CA · Obj 2.4 · Difficulty: Hard · Type: Multiple select
Select two.

Root Xform, `Usd.ModelAPI(prim).SetKind("assembly")` (no parent):

A. `prim.IsGroup()` is `True`
B. `prim.IsComponent()` is `True`
C. `prim.IsComponent()` is `False` — assembly is a group kind
D. `IsGroup()` raises unless `kind` is exactly `"group"`

---

**M3-032** · COMP · Obj 1.6 · Difficulty: Hard · Type: Multiple select
Select two.

Which LIVERPS comparisons match 26.08?

A. Inherits beat VariantSets (M3-004)
B. Local beats Inherits even from a weaker sublayer (M3-009)
C. Specializes beat References
D. Relocates are not an arc; ignore the E

---

**M3-033** · DM · Obj 5.2 · Difficulty: Hard · Type: Multiple select
Select two.

After `CreateInMemory`, then `SetStageUpAxis(..., UsdGeom.Tokens.z)` and `SetStageMetersPerUnit(..., 1)`:

A. `GetStageUpAxis` is `Z`
B. `GetStageMetersPerUnit` is `1.0`
C. In-memory stages ignore Set* and stay `Y` / `0.01`
D. `Tokens.z` cannot be passed to `SetStageUpAxis`

---

**M3-034** · CUST · Obj 3.1 · Difficulty: Hard · Type: Single choice

`plugInfo.json` for a **codeless** schema plugin must include:

A. Only a `Kind.Registry` block
B. Plugin metadata (`SdfMetadata` / schema plugin resources) so `Plug.Registry` can find `schema.usda` — parsing the USDA by hand is not registration
C. A Hydra SceneIndex by default
D. `usdGenSchema` output checked into `site-packages` of usd-core

---

**M3-035** · PD · Obj 7.6 · Difficulty: Hard · Type: Single choice

Store a non-rendered producer id `heatId = "H-44"` on `/Forge`:

A. `kind = "H-44"`
B. `customData` key `heatId`
C. `upAxis`
D. `primvars:displayColor`

---

**M3-036** · COMP · Obj 1.2 · Difficulty: Hard · Type: Single choice

A mill yard has 50 identical vises (native instances) plus 20,000 bolts (PointInstancer). Why both styles?

A. They are identical; pick either
B. **Native instances** share a prototype prim graph (per-instance root overrides); **PointInstancer** is for huge homogeneous point samples (proto index + transforms, not a full prim per bolt)
C. PointInstancer requires `GetMaster`
D. Native instances cannot be referenced assets

---

**M3-037** · VIS · Obj 8.3 · Difficulty: Hard · Type: Single choice

Parent Mesh bind `weakerThanDescendants`; child Subset binds a different material. The subset surface uses:

A. The parent material — parent always wins
B. The **subset** material — weakerThanDescendants lets descendants win
C. Neither
D. Average of the two `diffuseColor`s

---

**M3-038** · DBG · Obj 6.4 · Difficulty: Hard · Type: Single choice

A cube has `extent` still at the default empty/old box after points moved to `(0,0,0)–(2,3,0)`. Viewport bounds look wrong. First fix?

A. `Kind.Registry.GetAllKinds()`
B. Recompute with `ComputeExtentFromPlugins` and `Set` on `extent`
C. Set `purpose = proxy`
D. `MuteLayer` the root

---

**M3-039** · DE · Obj 4.4 · Difficulty: Hard · Type: Multiple select
Select two.

Round-trip of identifier `"Ember-2"`:

A. `Tf.MakeValidIdentifier("Ember-2")` → `"Ember_2"`; keep `"Ember-2"` in `customData`
B. Hyphens are legal in prim names — skip sanitizing
C. Author `defaultPrim` plus units/upAxis
D. Drop payloads so the DCC always flattens

---

**M3-040** · COMP · Obj 1.1 · Difficulty: Hard · Type: USDA-reading

```usda
#usda 1.0
class "_Look"
{
    float roughness = 0.9
}

def "A" (
    prepend references = @./ingot.usda@
    prepend inherits = </_Look>
)
{
}

def "B" (
    prepend references = @./ingot.usda@
    prepend inherits = </_Look>
)
{
}
```

`ingot.usda` authors `roughness = 0.2`. Composed roughness on `/A` and `/B`?

A. `0.2` and `0.2`
B. `0.9` and `0.9` — inherit **broadcasts** to every inheriting reference
C. `0.9` and `0.2` — only the first inheritor wins
D. `None`, `None`

---

**M3-041** · DM · Obj 5.3 · Difficulty: Hard · Type: Single choice

`GetCustomDataByKey("heatId")` vs `GetMetadata("comment")`:

A. Aliases
B. `customData` is a dictionary of producer keys; `comment` is a separate metadata field
C. `comment` is only legal on attributes
D. Both register schemas

---

**M3-042** · CA · Obj 2.1 · Difficulty: Hard · Type: Single choice

To append a new PointInstancer prototype **without** shifting index 0 on 26.08:

A. `AddTarget(new, position=Usd.ListPositionFrontOfPrependList)`
B. `AddTarget(new, position=Usd.ListPositionBackOfAppendList)`
C. `AddTarget(new)` is guaranteed to prepend on 26.08
D. `SetTargets` is illegal

---

**M3-043** · PD · Obj 7.7 · Difficulty: Hard · Type: Multiple select
Select two.

Validating `@./maps/rust.png@` authored in `assets/cleat.usda`:

A. `layer.ComputeAbsolutePath("./maps/rust.png")` (layer-relative)
B. `Ar.GetResolver().Resolve("./maps/rust.png")` from a random cwd is sufficient
C. Empty resolve + composed texture present ⇒ you used the **cwd** resolver, not the layer anchor
D. `AnchorRelativePath` is required public API in 26.08

---

**M3-044** · COMP · Obj 1.7 · Difficulty: Hard · Type: Single choice

Empty variant selection; `with variantSet.GetVariantEditContext(): attr.Set(7)`. Where does 7 land?

A. Inside the first variant
B. **Local** on the prim (not in any variant)
C. Inside every variant
D. The context raises

---

**M3-045** · DBG · Obj 6.1 · Difficulty: Hard · Type: Single choice

`DefinePrim("/Hearth/Flue")` (new child) inside an already-open `Sdf.ChangeBlock`:

A. Always succeeds
B. Can raise `Tf.ErrorException` on 26.08
C. Converts specs to USDA
D. Only fails if Flue is instanceable

---

**M3-046** · DE · Obj 4.8 · Difficulty: Hard · Type: Single choice

Importer sees crate magic `PXR-USDC` on `mill.usd`. `formatId` is:

A. `usda`
B. `usd` (extension plugin) — magic is crate, id follows `.usd`
C. `usdc`
D. `usdz`

---

**M3-047** · VIS · Obj 8.4 · Difficulty: Hard · Type: Single choice

PreviewSurface `diffuseColor` should come from **vertex displayColor** (not a UV texture). Reader:

A. `UsdPrimvarReader_float2` / `st`
B. `UsdPrimvarReader_float3` / `varname` = `displayColor`
C. `UsdUVTexture` / `displayColor`
D. `UsdMtlx` `standard_surface`

---

**M3-048** · CUST · Obj 3.7 · Difficulty: Hard · Type: Single choice

Shipping a Hydra **SceneIndex** that emits render geometry from this book’s pip wheel:

A. Works: `import pxr.UsdImaging`
B. **Blocked** — `UsdImaging` / `Hd` are not in usd-core; you need an imaging build
C. Works via `Kind.Registry`
D. Works via `Sdf.ChangeBlock`

---

**M3-049** · COMP · Obj 1.5 · Difficulty: Hard · Type: Multiple select
Select two.

Session vs root: you `SetEditTarget(session)` then `radius.Set(9)` while root has `1`.

A. Composed `Get()` is `9` (session is strongest in the local stack)
B. Root layer still stores `1`
C. Session writes are always discarded on `Save` of the root
D. Session cannot hold attribute values

---

**M3-050** · DM · Obj 5.5 · Difficulty: Hard · Type: Single choice

Parent visibility `invisible`; child never authors visibility. `ComputeVisibility()` on the child is `invisible`. `GetVisibilityAttr().Get()` on the child is:

A. `invisible`
B. `inherited`
C. `None`
D. `visible`

---

**M3-051** · PD · Obj 7.1 · Difficulty: Hard · Type: Single choice

Stand-in for `usdzip` in this venv:

A. The `usdzip` binary in `.venv/bin`
B. `UsdUtils.CreateNewUsdzPackage` (STORE compression)
C. `zipfile.ZIP_DEFLATED` of USDA files by hand (spec-legal)
D. `usdcat --zip`

---

**M3-052** · CA · Obj 2.5 · Difficulty: Hard · Type: Single choice

Broken model hierarchy: un-kinded `/Clutter` with child `kind = component`. Child `IsComponent()`?

A. `True` because GetKind is component
B. **False** — parent is not a model
C. `True` if the child is a Cube
D. Raises

---

**M3-053** · COMP · Obj 1.11 · Difficulty: Hard · Type: Multiple select
Select two.

Split `smelter.usda` (geo, look, rig) for three TDs:

A. Payload geo; sublayer look; sublayer rig; small interface with `defaultPrim`
B. Pin published USDC per stream
C. One root layer, no arcs, daily Flatten only
D. Put kinds in `customData` instead of composition

---

**M3-054** · DE · Obj 4.3 · Difficulty: Hard · Type: Single choice

Layout layer merged in Git vs farm cache opened 10k times. Pair?

A. Git USDC / farm USDA
B. Git USDA / farm USDC
C. Both USDZ
D. Git USDZ / farm USDA

---

**M3-055** · DBG · Obj 6.2 · Difficulty: Hard · Type: Single choice

Artist sets shot variant `fire = hot` (`heat = 2`) but composed heat is still `8` from an inherit class. Why?

A. Variants cannot be selected on a referencing prim
B. **Inherits beat VariantSets** — the class opinion wins until you override with **local** (or remove the inherit)
C. Variant selections never affect doubles
D. Inherit is weaker than variants

---

**M3-056** · CUST · Obj 3.5 · Difficulty: Hard · Type: Multiple select
Select two.

`hero://mill/anvil` custom resolver:

A. Ar plugin + `plugInfo.json` + plugin path
B. `Ar.GetResolver()` stays the process facade
C. `AnchorRelativePath` must be implemented (26.08 public API)
D. Register the resolver with `Kind.Registry.Register`

---

**M3-057** · COMP · Obj 1.10 · Difficulty: Hard · Type: Single choice

Remove `primvars:displayColor` from **one** instanced vise in an assembly:

A. `OverridePrim` on `/Vise/Body`
B. Author a block/delete at the **instance root**, or de-instance that root
C. `GetMaster().Clear()`
D. Mute the prototype layer for everyone

---

**M3-058** · DE · Obj 4.1 · Difficulty: Hard · Type: Single choice

Exporting a payload-heavy mill to glTF. Fidelity note:

A. glTF will lazy-load USD payloads
B. You must **load the working set and bake** (glTF has no payloads / LIVERPS)
C. Keep `@./geo.usda@` paths inside glTF JSON
D. `metersPerUnit` is copied as a required glTF extension always

---

**M3-059** · PD · Obj 7.8 · Difficulty: Hard · Type: Multiple select
Select two.

DCC importer:

A. Map to typed prims / API schemas; keep unknowns as custom properties
B. Honor payload vs reference (working set)
C. `from pxr import UsdMtlx` is guaranteed
D. `GetMaster()` for instances

---

**M3-060** · DM · Obj 5.2 · Difficulty: Hard · Type: Single choice

One triangle mesh: `faceVertexCounts` length and `faceVertexIndices` length?

A. Counts `1`, indices `3`
B. Counts `3`, indices `1`
C. Counts `3`, indices `3`
D. Counts `1`, indices `1`

---

**M3-061** · DE · Obj 4.3 · Difficulty: Hard · Type: Single choice

USDZ from `CreateNewUsdzPackage` uses which ZIP compression?

A. DEFLATED (8)
B. STORED (0)
C. BZIP2
D. Per-member mix

---

**M3-062** · CA · Obj 2.4 · Difficulty: Hard · Type: Multiple select
Select two.

`UsdGeom.PointInstancer.Define` then:

A. `prim.IsA(UsdGeom.Gprim)` is `True`
B. `prim.IsA(UsdGeom.Gprim)` is `False`
C. `prim.IsA(UsdGeom.Boundable)` is `True`
D. `prim.IsA(UsdGeom.Boundable)` is `False`

---

**M3-063** · DBG · Obj 6.5 · Difficulty: Hard · Type: Single choice

Coalescing similar `Open` warnings: install `UsdUtils.CoalescingDiagnosticDelegate`

A. After `Open` returns
B. **Before** `Open`
C. Only inside `ChangeBlock`
D. Only if `MallocTag` is non-zero

---

**M3-064** · DE · Obj 4.7 · Difficulty: Hard · Type: Multiple select
Select two.

Component exporter root-layer checklist:

A. `defaultPrim`
B. `metersPerUnit` and `upAxis`
C. `Kind.Registry.Register` in the USDA header
D. `GetMaster` metadata

---

**M3-065** · PD · Obj 7.2 · Difficulty: Hard · Type: Single choice

`ExtractExternalReferences` vs `ComputeAllDependencies`:

A. They are aliases
B. Extract = **one file** `(sublayers, refs+assets, payloads)`; Compute = **closure** `(layers, assets, unresolved)`
C. Extract walks the closure; Compute is one file
D. Only Extract reports unresolved textures

---

*End of Mock Exam 3. 65 questions. Check `mock-exams/mock03_answers.md` only after you have finished.*
