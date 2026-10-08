# Question Bank — Composition (COMP)

**Original practice questions.** Not actual NVIDIA exam content. Mapped to NCP-OUSD study-guide objectives 1.1–1.11 (Composition, 23%).

Verified against **USD 26.08** (`usd-core` 26.8). Domain target: 92 questions. This file currently holds **COMP-001–COMP-092** (domain complete).

Work the stems first. Answers and explanations are grouped at the end.

---

**COMP-001** · Obj 1.6 · Difficulty: Easy · Type: Single choice

What is the strength order of composition arcs, strongest to weakest, as spelled by LIVERPS?

A. Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes
B. Local, Inherits, VariantSets, References, Payloads, Specializes, rElocates
C. Local, VariantSets, Inherits, rElocates, References, Payloads, Specializes
D. Inherits, Local, VariantSets, References, Payloads, Specializes, rElocates

---

**COMP-002** · Obj 1.6 · Difficulty: Easy · Type: Single choice

In LIVERPS, what does the letter **E** stand for?

A. Expression arcs (value clips)
B. Edit targets
C. rElocates
D. Extents

---

**COMP-003** · Obj 1.6 · Difficulty: Medium · Type: Multiple select
Select two.

Which statements about LIVERPS are true?

A. A local opinion in the stage's layer stack always beats a referenced opinion on the same field.
B. Specializes beat references, which is why they are a safe place to put hero overrides.
C. Inherits beat variant opinions on the same field.
D. Value clips are the “C” in LIVERPS and sit between variants and relocates.

---

**COMP-004** · Obj 1.1 · Difficulty: Easy · Type: Single choice

A referenced asset authors `radius = 1`. You need the composed value on this shot to be `9` without editing the asset file. Which change is strongest and sufficient?

A. Add a `class` prim that specializes the sphere with `radius = 9`.
B. Author `double radius = 9` as a local opinion on the referencing prim (or a stronger local sublayer).
C. Mute the root layer so the reference can win.
D. Set `instanceable = true` on the referencing prim.

---

**COMP-005** · Obj 1.1 · Difficulty: Medium · Type: USDA-reading

File: `asset.usda`

```usda
#usda 1.0
(
    defaultPrim = "X"
)
def Sphere "X"
{
    double radius = 1
}
```

File: `shot.usda`

```usda
#usda 1.0
class "_I"
{
    double radius = 3
}

def "Ball" (
    prepend inherits = </_I>
    prepend references = @asset.usda@
)
{
}
```

What is the composed value of `/Ball.radius`?

A. `1` (the reference wins because it defines the Sphere type)
B. `3` (inherits beat references)
C. `None` (the two arcs cancel)
D. `2` (USD averages conflicting numeric opinions)

---

**COMP-006** · Obj 1.1 · Difficulty: Medium · Type: Single choice

A prim both **references** an asset that authors `radius = 1` and **specializes** a class that authors `radius = 7`. There is no local `radius`. What is the composed value?

A. `7`, because specializes are a “base class” and win like inherits
B. `1`, because references beat specializes
C. `None`, because R and S conflict
D. `7`, but only if the specialize is listed before the reference in USDA

---

**COMP-007** · Obj 1.1 · Difficulty: Medium · Type: Multiple select
Select two.

A prim has these list-edits on `references`:

```usda
#usda 1.0
def "P" (
    prepend references = @r1.usda@
    append references = @r2.usda@
)
{
}
```

`r1.usda` authors `radius = 2`; `r2.usda` authors `radius = 8`. Which statements are true?

A. The composed `radius` is `2`.
B. The composed `radius` is `8` because append is “later, therefore stronger.”
C. Prepended references are stronger than appended references.
D. USD rejects a prim that both prepends and appends the same list field.

---

**COMP-008** · Obj 1.1 · Difficulty: Hard · Type: USDA-reading

```usda
#usda 1.0
class "_I"
{
    double radius = 3
}

def Sphere "Ball" (
    prepend inherits = </_I>
    prepend variantSets = "look"
    variants = {
        string look = "hi"
    }
)
{
    variantSet "look" = {
        "hi" {
            double radius = 10
        }
    }
}
```

What is the composed value of `/Ball.radius`?

A. `10` (the selected variant is the “current look,” so it wins)
B. `3` (inherits beat variant opinions)
C. `1` (Sphere schema fallback)
D. `None` (inherit and variant block each other)

---

**COMP-009** · Obj 1.3 · Difficulty: Easy · Type: Single choice

Which statement best distinguishes a **sublayer** from a **reference**?

A. A sublayer contributes opinions in the *same* namespace as its parent layer; a reference brings another layer's contents in at a prim path (often renaming the target to that prim).
B. A sublayer is always weaker than a reference.
C. A reference can only point at `.usdc` files; a sublayer can only point at `.usda` files.
D. Sublayers load lazily like payloads; references always load.

---

**COMP-010** · Obj 1.3 · Difficulty: Medium · Type: Multiple select
Select two.

Compared with a reference, a **payload** is the better choice when you need which of the following?

A. The introduced opinions to beat local shot overrides
B. The ability to omit the target's descendants from the stage until `Load` (or a load-all open)
C. Weaker-than-reference composition strength, so local and referenced opinions still win
D. A replacement for `defaultPrim` (payloads do not use `defaultPrim`)

---

**COMP-011** · Obj 1.3 · Difficulty: Medium · Type: USDA-reading

```usda
#usda 1.0
def Xform "W"
{
    def Xform "A" (
        prepend payload = @./hi.usda@
    )
    {
    }
    def Xform "C" (
        prepend references = @./hi.usda@
    )
    {
    }
}
```

`hi.usda` has `defaultPrim = "Root"` and defines `/Root/Hi`. The stage is opened with `Usd.Stage.Open(path, Usd.Stage.LoadNone)`. Which statement is true?

A. Neither `/W/A/Hi` nor `/W/C/Hi` exists, because `LoadNone` blocks every composition arc.
B. `/W/C/Hi` exists (`True`); `/W/A/Hi` does not (`False`). References still load; payloads do not.
C. Both `/W/A/Hi` and `/W/C/Hi` exist; `LoadNone` only skips textures.
D. `/W/A/Hi` exists and `/W/C/Hi` does not, because payloads are stronger than references.

---

**COMP-012** · Obj 1.3 · Difficulty: Medium · Type: USDA-reading

```usda
#usda 1.0
def Cube "Box"
{
    double size = 9
}
```

Python: `prim.GetReferences().AddReference("nodefault.usda")` returns `True`. The referencing prim has no explicit target path. What is the composed type name of the referencing prim, and which composition error is reported?

A. Type `Cube`, error none — USD infers the first root prim
B. Type `''` (empty), error `Pcp.ErrorType_UnresolvedPrimPath`
C. Type `''`, error `Pcp.ErrorType_InvalidAssetPath`
D. `AddReference` actually returns `False` and authors nothing

---

**COMP-013** · Obj 1.3 · Difficulty: Medium · Type: Multiple select
Select two.

A lighting TD needs a shot that (1) stacks department layers that all edit `/World` in place, and (2) brings in a published chair asset under `/World/Chair_0`. Which pair of arcs matches those two jobs?

A. Sublayers for the department stack
B. A reference (or payload) for the chair asset
C. An inherit for the department stack, because inherits share namespace
D. A specialize for the chair, because specializes copy assets into a new path

---

**COMP-014** · Obj 1.4 · Difficulty: Easy · Type: Single choice

A reference is authored with `Sdf.LayerOffset(offset=10, scale=1)`. How does a **layer time** `t` in the referenced file map to **stage time**?

A. `stageTime = t / 10`
B. `stageTime = offset + scale * layerTime` → `10 + t`
C. `stageTime = layerTime` (offsets apply only to sublayers, never to references)
D. `stageTime = t - 10`

---

**COMP-015** · Obj 1.4 · Difficulty: Medium · Type: USDA-reading

File: `anim.usda`

```usda
#usda 1.0
(
    defaultPrim = "Ball"
)
def Xform "Ball"
{
    double3 xformOp:translate.timeSamples = {
        0: (0, 0, 0),
        10: (10, 0, 0),
    }
    uniform token[] xformOpOrder = ["xformOp:translate"]
}
```

File: `shot.usda`

```usda
#usda 1.0
def "B" (
    prepend references = @anim.usda@ (
        offset = 10
    )
)
{
}
```

What are the composed time-sample times on `/B.xformOp:translate`?

A. `[0.0, 10.0]` (offsets do not move sample times)
B. `[10.0, 20.0]`
C. `[−10.0, 0.0]`
D. `[]` (the offset strips samples and leaves only the default)

---

**COMP-016** · Obj 1.4 · Difficulty: Medium · Type: Single choice

The referenced asset authors both a **default** `xformOp:translate = (100, 0, 0)` and time samples at layer times 0 and 10. The reference uses `Sdf.LayerOffset(10)`. What does `attr.Get()` (no time argument) return on the referencing prim?

A. `(0, 0, 0)` — the first sample, shifted to stage time 10, then read at default
B. `(100, 0, 0)` — defaults are not shifted by a layer offset
C. `None` — `Get()` never sees a default when samples exist
D. `(10, 0, 0)` — USD adds the offset to each vector component

---

**COMP-017** · Obj 1.4 · Difficulty: Medium · Type: Single choice

A sublayer is included as `@anim.usda@ (offset = 10)`. You `Set` a time sample at stage time `20`. Where is the sample stored in `anim.usda` if the edit target was created with `stage.GetEditTargetForLocalLayer(anim)` versus a bare `Usd.EditTarget(anim)`?

A. Both store the sample at 20.
B. `GetEditTargetForLocalLayer` stores at **10**; the bare `EditTarget` stores at **20**.
C. `GetEditTargetForLocalLayer` stores at **20**; the bare `EditTarget` stores at **10**.
D. Neither can author samples into a sublayer that has an offset.

---

**COMP-018** · Obj 1.5 · Difficulty: Easy · Type: Single choice

On a multi-user shot, layout, animation, and lighting each need to author opinions without overwriting each other's files. What is the standard OpenUSD pattern?

A. One root layer with a `subLayers` list, strongest department first, each department owning one layer file
B. One root layer that `specializes` each department file
C. Native instancing of the shot so each TD gets a prototype
D. Flattening the shot at the start of every session so everyone edits a copy

---

**COMP-019** · Obj 1.5 · Difficulty: Medium · Type: Single choice

You `SetEditTarget` to a freshly created anonymous layer that is **not** in the stage's local layer stack, then `DefinePrim("/Ghost")`. What happens?

A. The prim appears on the composed stage because any edit target is automatically sublayered.
B. `SetEditTarget` raises `Tf.ErrorException` (`not in the local LayerStack`); the prim is not authored on the stage.
C. The prim is written to the session layer as a fallback.
D. The prim is written to disk next to the root layer as `Ghost.usda`.

---

**COMP-020** · Obj 1.5 · Difficulty: Medium · Type: Single choice

A shot's default edit target is the root layer. Animation should land in `anim.usda`, which is a **sublayer** of that root (not a referenced asset). What should the TD do?

A. `stage.SetEditTarget(stage.GetEditTargetForLocalLayer(animLayer))` (or an equivalent local-stack target)
B. `stage.SetEditTarget` on the referenced chair's root layer, because chairs contain the animation
C. Author in the session layer and hope `Save()` writes it into `anim.usda`
D. Call `stage.Flatten()` first so there is only one layer to target

---

**COMP-021** · Obj 1.5 · Difficulty: Medium · Type: Multiple select
Select two.

Which practices support a multi-user OpenUSD shot?

A. List stronger, later-arriving departments **first** in `subLayers` (first listed is stronger).
B. Let every TD `Save()` into the same `shot.usda` root so Git can merge USDA.
C. Keep the session layer for personal, unsaved experiments; do not publish it as the show file.
D. Put each department's work on a referenced prim at a unique path such as `/layout` vs `/anim` so they never share `/World`.

---

**COMP-022** · Obj 1.7 · Difficulty: Easy · Type: Single choice

When are **variant sets** the appropriate structure for an asset?

A. When the asset has a small set of named, mutually exclusive options the consumer will pick (size, look, LODs)
B. When you need to instance 50,000 identical trees
C. When two departments must edit `/World.tx` on the same shot at the same time
D. When you want opinions that always beat local shot overrides

---

**COMP-023** · Obj 1.7 · Difficulty: Medium · Type: Multiple select
Select two.

In which situations are variants **not** the right tool?

A. Encoding a continuous slider (any float mass between 0 and 100) as hundreds of named variants
B. Switching a robot between a handful of published looks (`clean`, `dirty`, `damaged`)
C. Replacing composition itself: putting every shot's animation clips inside the character's variant set
D. Choosing among two geometry LODs on a component (`full`, `proxy`)

---

**COMP-024** · Obj 1.7 · Difficulty: Medium · Type: USDA-reading

A Python author does this (no variant is selected first):

```{.python .norun}
vs = prim.GetVariantSets().AddVariantSet("size")
vs.AddVariant("big")
with vs.GetVariantEditContext():
    prim.GetAttribute("height").Set(3)
```

What is authored?

A. `height = 3` inside variant `big`
B. `height = 3` as a **direct local** opinion on the prim; variant `big` stays empty
C. Nothing; `GetVariantEditContext` raises if there is no selection
D. A new reference to an anonymous layer that holds `height = 3`

---

**COMP-025** · Obj 1.7 · Difficulty: Medium · Type: Single choice

A facility wants a “hero” chair that is a completely different mesh and material graph, published by a different team, swapped in at shot time. Why is a **reference** (or payload) a better swap than a variant on the hero chair itself?

A. Variants cannot store meshes; they only store tokens.
B. A different published asset is a different composition *source*; variants switch options *inside* one asset's layer stack. Cross-asset swaps belong on the referencing (assembly/shot) side.
C. References always beat variants, so the variant would never be visible.
D. Payloads are the only arc allowed to introduce materials.

---

**COMP-026** · Obj 1.8 · Difficulty: Medium · Type: Multiple select
Select two.

A stronger sublayer `strong.usda` authors `radius = 3`; a weaker sublayer authors `radius = 7`. After `stage.MuteLayer(strongIdentifier)`, the composed radius becomes `7`. Which statements explain related “my opinion vanished” cases?

A. Muting a layer removes it from the local stack, so its opinions no longer contribute.
B. A muted layer's opinions still win if the prim is `instanceable`.
C. Authoring on a layer that is **not** the current edit target (for example the root, while the target is a weaker sublayer) will not put the opinion where you think it went.
D. Muting always deletes the USDA file from disk.

---

**COMP-027** · Obj 1.8 · Difficulty: Medium · Type: Single choice

`/Room/A` references a chair and is `instanceable = true`. `/Room/A/Seat` is an instance proxy. A TD calls `stage.OverridePrim("/Room/A/Seat")` to set `size = 9`. What happens?

A. The override wins locally; only this instance's seat becomes size 9.
B. The call raises `Tf.ErrorException` (`authoring to an instance proxy is not allowed`); the nested opinion is not authored.
C. USD silently writes the opinion onto the shared prototype, changing every instance.
D. USD converts the prim to a PointInstancer automatically.

---

**COMP-028** · Obj 1.8 · Difficulty: Medium · Type: USDA-reading

```usda
#usda 1.0
def "Asset" (
    prepend variantSets = "size"
    variants = {
        string size = "big"
    }
)
{
    double height = 1
    variantSet "size" = {
        "big" {
            double height = 3
        }
    }
}
```

The variant selection is `big`. What is the composed `height`, and why might a TD think the variant “did not take effect”?

A. `3` — variants beat local opinions
B. `1` — the local opinion is **L** and beats the variant opinion **V**
C. `None` — selection and local opinion cancel
D. `2` — USD blends local and variant numeric values

---

**COMP-029** · Obj 1.8 · Difficulty: Medium · Type: Single choice

A layer authors `relocates = { </Bot/Rig/Arm>: </Bot/Arm> }`. A TD then authors `over "Rig" { over "Arm" { double radius = 9 } }` on `/Bot` in that same local stack, intending to edit the arm. The composed `/Bot/Arm.radius` stays at the referenced value. Why?

A. Relocates delete the prim, so no opinion can ever apply.
B. After a relocate, opinions at the **source** path no longer apply to the destination; author `over "Arm"` at `/Bot/Arm` (or relocate after the edit is in the source asset).
C. Relocates only work on payloads, and this prim was referenced.
D. `radius` is a schema fallback and cannot be overridden.

---

**COMP-030** · Obj 1.9 · Difficulty: Easy · Type: Single choice

You must hand a vendor a single layer with **no composition arcs**. Which API is the right primary tool?

A. `stage.Flatten()` — bakes references, payloads, inherits, variants, and sublayers into one layer
B. `UsdUtils.FlattenLayerStack(stage)` — this also bakes references away
C. `rootLayer.Export("out.usda")` — export always flattens
D. `stage.Export()` to USDZ — USDZ forbids arcs by definition

---

**COMP-031** · Obj 1.9 · Difficulty: Medium · Type: Multiple select
Select two.

`shot.usda` sublayers `bolt.usda` (a Cube named `Bolt`) and also **references** that same bolt at `/Refd`. After each operation, which descriptions match?

A. `stage.Flatten()` produces a Cube `/Refd` with `size` copied in and **no** `references` field; `/Bolt` from the sublayer is also present as a Cube.
B. `UsdUtils.FlattenLayerStack(stage)` **keeps** `prepend references` on `/Refd`, bakes the sublayer so `/Bolt` is local, and clears `subLayers`.
C. Both APIs remove every reference and every sublayer identically.
D. `FlattenLayerStack` is the only way to include the session layer.

---

**COMP-032** · Obj 1.10 · Difficulty: Easy · Type: Single choice

Where do you author `instanceable = true` so many assembly prims share one prototype?

A. On each **referencing** prim in the assembly (the instance root), not inside the component asset's default prim as a required setting
B. Only on the component's `defaultPrim` in the published asset; assemblies must not set it
C. On every descendant mesh (`Seat`, `Leg`), never on the component root
D. On the stage metadata block next to `metersPerUnit`

---

**COMP-033** · Obj 1.10 · Difficulty: Medium · Type: Single choice

An assembly instances many chairs. You must remove or override a property on **one** chair's nested `Seat` without changing the others. Which approach is valid?

A. `OverridePrim` the nested proxy path while the prim stays instanceable
B. Set `instanceable = false` on that one instance root (or de-instance), then author the nested override; the sibling instances keep the shared prototype
C. Call `prim.GetMaster()` and `Clear()` the property on the master
D. Mute the assembly root layer

---

**COMP-034** · Obj 1.10 · Difficulty: Medium · Type: Single choice

On USD 26.08, two instanceable prims that reference the same chair share a prototype. How do you obtain that prototype prim, and what is **not** available?

A. `prim.GetPrototype()` returns a prim under `/__Prototype_N`; `GetMaster()` is **not** a `Usd.Prim` method on this version
B. `prim.GetMaster()` is the only supported name; `GetPrototype()` was removed in 26.08
C. Both names exist and return different prims
D. Prototypes are only accessible from `UsdGeom.PointInstancer`

---

**COMP-035** · Obj 1.11 · Difficulty: Easy · Type: Single choice

A monolithic `Robot.usda` holds geometry, materials, and a payload of high-resolution parts in one file, and two teams block on it. What is the first composition-friendly split?

A. Separate published layers (interface/payload, geometry, materials) referenced or sublayered from a thin asset root, so each workstream owns a file
B. Copy the file per artist and flatten daily
C. Convert the whole robot to a PointInstancer
D. Replace all `def`s with `class` so nobody's edits are concrete

---

**COMP-036** · Obj 1.11 · Difficulty: Medium · Type: Multiple select
Select two.

When splitting a show into collaborative workstreams, which choices match OpenUSD practice?

A. Put **payloads on heavy component contents** so shots can open with proxies or remain unloaded
B. Put every department's animation samples in the **component asset** variant set so shots stay empty
C. Use a shot **sublayer stack** (layout, anim, lighting) so `/World` is shared and strength is explicit
D. Author relocates in every component so department layers never need matching paths

---

**COMP-037** · Obj 1.2 · Difficulty: Easy · Type: Single choice

You need tens of thousands of similar trees with per-tree position, scale, and a cheap hide. Which instancing style fits?

A. Native `instanceable` references, one prim per tree
B. A `UsdGeom.PointInstancer` with prototypes, `protoIndices`, and `positions`
C. Unique `def` copies of the full tree asset for every tree
D. One inherit arc from a class `_Tree` with no instancing

---

**COMP-038** · Obj 1.2 · Difficulty: Medium · Type: Single choice

A kitchen set has 40 hero chairs that must stay native instances for memory, plus **one** chair the director wants re-modeled at the `Seat` child. What do you do?

A. PointInstancer for all 41 chairs so `invisibleIds` can hide the hero
B. Keep 40 instanceable references; set `instanceable = false` (or a unique reference) only on the hero chair so nested edits are legal
C. Edit the shared prototype; accept that all 41 seats change
D. Switch the set to payloads only — payloads disable instancing automatically

---

**COMP-039** · Obj 1.2 · Difficulty: Medium · Type: Multiple select
Select two.

Choose an appropriate instancing style for each scale.

A. A handful of unique hero props that need arbitrary nested edits → ordinary references (or de-instanced prims), not native instances
B. Hundreds of identical published chairs in a dining hall → native `instanceable` component references
C. Millions of scattered pebbles → native instanceable Xforms, one prim each, so Hydra can name them
D. Native instances for the pebbles, because PointInstancer cannot instance more than 256 points

---

**COMP-040** · Obj 1.3 · Difficulty: Hard · Type: Single choice

You want a stage that contains `/World/A` but must not populate `/World/B` at all (not even as an unloaded payload prim). Which API is correct on USD 26.08?

A. `Usd.Stage.Open(path, mask=["/World/A"])`
B. `Usd.Stage.OpenMasked(path, Usd.StagePopulationMask([Sdf.Path("/World/A")]))`
C. `Usd.Stage.Open(path, Usd.Stage.LoadNone)` — this is equivalent to a population mask
D. `stage.MuteLayer` on the layer that defines `/World/B`

---

**COMP-041** · Obj 1.1 · Difficulty: Medium · Type: Single choice

A weaker layer prepends `references = [@r1.usda@, @r2.usda@]` (`r1` has `radius = 2`, `r2` has `radius = 8`). A stronger sublayer authors `delete references = [@r1.usda@]`. What is the composed `radius`?

A. `2` (delete cannot remove a prepended arc)
B. `8` (r1 is removed; r2 remains and is now the strongest remaining reference)
C. `None` (delete empties the whole list)
D. `5` (USD averages the remaining opinions)

---

**COMP-042** · Obj 1.8 · Difficulty: Hard · Type: Single choice

A stronger sublayer authors only a **default** `radius = 5`. A weaker sublayer authors `radius` **time samples** at 0 and 10. What does `Get()`, `Get(0)`, and `GetTimeSamples()` return?

A. `Get() = 5`, `Get(0) = 0`, samples `[0, 10]` — samples always show through
B. `Get() = 5`, `Get(0) = 5`, `Get(10) = 5`, samples `[]` — the stronger default wins at every time
C. `Get() = None` because samples exist on some layer
D. Composition error; a field cannot mix a default and samples across layers

---

**COMP-043** · Obj 1.4 · Difficulty: Medium · Type: Single choice

A reference uses `Sdf.LayerOffset(10, 2)` (offset 10, scale 2). The asset has samples at layer times 0 and 10. What are the composed sample times?

A. `[0.0, 10.0]`
B. `[10.0, 20.0]` (scale is ignored on references)
C. `[10.0, 30.0]` because `stageTime = 10 + 2 * layerTime`
D. `[5.0, 10.0]`

---

**COMP-044** · Obj 1.3 · Difficulty: Medium · Type: Single choice

On an in-memory stage you `DefinePrim("/Asset/Geo")`, set `sz = 4`, then `DefinePrim("/Inst")` and `AddInternalReference("/Asset/Geo")`. What is `/Inst.sz`?

A. `None` — internal references only work in files on disk
B. `4`
C. `0` — internal references copy the prim spec but drop attributes
D. The call raises `Tf.ErrorException` because source and destination share a stage

---

**COMP-045** · Obj 1.3 · Difficulty: Medium · Type: Single choice

A stage has payloads on `/W/A` and `/W/B` and a **reference** on `/W/C`. What does `stage.FindLoadable()` return?

A. `['/W/A', '/W/B', '/W/C']`
B. `['/W/A', '/W/B']` — only payload sites are loadable
C. `['/W/C']` — references are the loadable arcs
D. `[]` until you call `LoadNone`

---

**COMP-046** · Obj 1.3 · Difficulty: Medium · Type: Multiple select
Select two.

A stage is opened with `LoadNone`. `/W/A` has a payload to an asset that defines `/Root/Hi`. Which operations are true?

A. Before `Load`, `/W/A/Hi` does not exist and `/W/A.IsLoaded()` is `False`.
B. `stage.Load("/W/A")` makes `/W/A/Hi` exist; `Unload("/W/A")` removes it again.
C. `Load("/W/A")` is ignored because `LoadNone` locks the stage forever.
D. `FindLoadable()` includes referenced prims as well as payloads.

---

**COMP-047** · Obj 1.1 · Difficulty: Medium · Type: Single choice

Class `/_Look` authors `roughness = 0.2`. Both `/A` and `/B` inherit it. You then set `/A.roughness = 0.9` locally. What are the composed values?

A. A `0.9`, B `0.9` (inherits always stay in sync)
B. A `0.9`, B `0.2` (local on A does not change B)
C. A `0.2`, B `0.2` (inherits beat local)
D. A `0.9`, B `None`

---

**COMP-048** · Obj 1.1 · Difficulty: Medium · Type: Single choice

Continuing COMP-047: after A's local `0.9`, you change the **class** to `roughness = 0.5`. What is composed?

A. A `0.5`, B `0.5` (class edits beat local)
B. A `0.9`, B `0.5` (A keeps its local opinion; B follows the class)
C. A `0.9`, B `0.2` (the class is now ignored)
D. Both `None` until you re-AddInherit

---

**COMP-049** · Obj 1.7 · Difficulty: Easy · Type: Single choice

You add variants `big` and `small` to variant set `size`. How do you list the variant names, and what is printed?

A. `variantSet.GetNames()` → `['big', 'small']`
B. `variantSet.GetVariantNames()` → `['big', 'small']` (sorted); `GetNames()` lives on `Usd.VariantSets`, not on `Usd.VariantSet`
C. `prim.GetVariantSets().GetVariantNames()`
D. Variant names are only visible in USDA, not in Python

---

**COMP-050** · Obj 1.8 · Difficulty: Medium · Type: Single choice

`stage.OverridePrim("/NoSuch")` on an empty stage. Which description of `/NoSuch` is correct?

A. The prim exists as a handle, `IsDefined()` is `False`, specifier is `Sdf.SpecifierOver`
B. USD raises because `over` cannot create a prim
C. `IsDefined()` is `True` because any authored spec defines the prim
D. The prim is automatically converted to `def Xform`

---

**COMP-051** · Obj 1.5 · Difficulty: Easy · Type: Single choice

A root lists `subLayers = [@l1@, @l2@, @l3@]` where those layers author `radius` 1, 2, and 3. What is composed?

A. `3` (last listed wins, like CSS)
B. `1` (first listed is strongest)
C. `2` (the middle layer is the “active” edit target)
D. `None` (three opinions cancel)

---

**COMP-052** · Obj 1.3 · Difficulty: Medium · Type: Single choice

`Usd.Stage.OpenMasked("m.usda", mask)` with the mask containing only `/W/A`. The file also defines `/W/B`. What is true?

A. `/W/A` exists, `/W/B` does not
B. Both exist; the mask only skips payload loading
C. Neither exists until you `Load`
D. `OpenMasked` is not in USD 26.08; you must pass `mask=` to `Open`

---

**COMP-053** · Obj 1.1 · Difficulty: Hard · Type: Single choice

A published character **inherits** `/_Look` inside the asset (`roughness = 0.2`). A shot **references** that character at `/Hero`, then defines a shot-level `class "_Look"` with `roughness = 0.9`. What is `/Hero.roughness`?

A. `0.2` — shot classes cannot affect referenced inherits
B. `0.9` — implied inherits let the shot's `/_Look` contribute to the referenced prim
C. `None` — two `_Look` classes conflict
D. `0.2` unless you also `AddInherit("/_Look")` on `/Hero`

---

**COMP-054** · Obj 1.5 · Difficulty: Medium · Type: Multiple select
Select two.

Root authors `radius = 1`. Session authors `radius = 9`. A weaker sublayer authors `radius = 5`. Which are true?

A. Composed `radius` is `9` (session is the strongest local sheet).
B. The root layer spec still stores `1`; session opinions are not written into the root.
C. Saving the root layer publishes the session value `9` into `shot.usda`.
D. Sublayer `5` beats the session because sublayers are “more permanent.”

---

**COMP-055** · Obj 1.10 · Difficulty: Medium · Type: Single choice

On a **non-instance** prim, `attr.Set(5)` then `attr.Block()`. What does `attr.Get()` return?

A. `5` (block only hides the USDA line)
B. `None` (a block is a strong opinion that hides weaker values, including the previous default)
C. Schema fallback (for example Sphere radius `1`)
D. `0`

---

**COMP-056** · Obj 1.6 · Difficulty: Medium · Type: Single choice

Why is “composition is not merging” the right mental model for `double radius`?

A. List-op fields and scalar fields both concatenate every opinion
B. For a scalar, the **strongest** opinion replaces weaker ones; USD does not average or blend `1` and `9`
C. Weaker opinions are deleted from disk when a stronger one appears
D. Composition only runs at flatten time

---

**COMP-057** · Obj 1.6 · Difficulty: Easy · Type: Single choice

Where do **value clips** sit in LIVERPS?

A. They are the “C” between variants and relocates
B. They are not a LIVERPS letter; clip values resolve *inside* the strength of the arc/layer that introduced them
C. They always beat local opinions
D. They replaced relocates in USD 26.08

---

**COMP-058** · Obj 1.9 · Difficulty: Medium · Type: Multiple select
Select two.

A studio must deliver an internal show asset to an external vendor. Which pair belongs in the delivery checklist?

A. Flatten (or package a USDZ) so the vendor is not chasing unshipped layer paths; localize remaining asset paths
B. Include the artist's **session layer** so they see the same scratch comments
C. Strip or provide fallbacks for proprietary schemas/plugins the vendor does not have
D. Leave `subLayers` pointing at `/mnt/show/...` absolute paths so the vendor's resolver “just works”

---

**COMP-059** · Obj 1.5 · Difficulty: Easy · Type: Single choice

```{.python .norun}
stage.SetEditTarget(stage.GetRootLayer())
with Usd.EditContext(stage, stage.GetSessionLayer()):
    prim.SetMetadata("comment", "try bigger")
```

After the `with` block, what is the edit target?

A. Still the session layer
B. Restored to the root layer
C. Cleared (`None`), and the next `Set` raises
D. The referenced asset's root, because comments always go there

---

**COMP-060** · Obj 1.8 · Difficulty: Medium · Type: Single choice

You open a layer that contains only `over "Hero" { int hp = 10 }` as a stage. What happens, and what changes if you replace `over` with a typeless `def`?

A. `over`: `/Hero` is not defined and `Traverse()` is empty. Typeless `def`: `/Hero` is defined (`IsDefined()` True) and appears in `Traverse()`, still with no schema type.
B. Both specifiers define the prim the same way; only USDA spelling differs.
C. `over` defines the prim; `def` without a type is a syntax error.
D. `Traverse()` includes overs and skips defs.

---

**COMP-061** · Obj 1.4 · Difficulty: Medium · Type: Single choice

Two crowd characters must play the **same** walk clip, one starting 30 frames later. What is the composition tool?

A. Duplicate the clip file and rewrite every sample time by +30
B. Two references (or sublayers) to the same animation layer with different `Sdf.LayerOffset` / USDA `(offset = …)`
C. A variant set `time` with one variant per frame
D. `instanceable = true`, which delays time by instance index

---

**COMP-062** · Obj 1.7 · Difficulty: Medium · Type: Single choice

A component already has variant set `look = {clean, dirty}`. A shot TD also needs a one-off “muddy hero” that will never be reused. Where should that look live?

A. Add a third variant on the published component from the shot file (variants are always global)
B. Shot-level opinions (local overs / a shot-only layer) on that one instance; do not grow the published variant set for a one-off
C. A specialize of `clean`, because specializes beat local shot work
D. A PointInstancer prototype named `muddy`

---

**COMP-063** · Obj 1.8 · Difficulty: Medium · Type: Single choice

`GetPrimStack()` on a prim that is defined in the root and referenced from `r1.usda` prints display names `['shot.usda', 'r1.usda']`. What does that order mean?

A. Weakest first; `r1` wins
B. Strongest first; the root/shot spec is stronger than the referenced spec
C. Alphabetical
D. The stack only lists payloads

---

**COMP-064** · Obj 1.11 · Difficulty: Medium · Type: Multiple select
Select two.

A robot asset is being split for parallel work. Which file split matches common OpenUSD asset structure?

A. `Robot.usda` (interface + defaultPrim + payload/reference to contents), `Robot_payload.usda` / geometry layer, `Robot_mtl.usda`
B. One USDA per polygon, referenced individually from the shot
C. Shot `subLayers` for layout/anim/lighting that all overlay `/World`, leaving the robot as a referenced component
D. Bake every department into the robot's variant set `dept`

---

**COMP-065** · Obj 1.9 · Difficulty: Medium · Type: Single choice

You need a **package** the vendor can copy as one file, still containing a USDA root plus a texture. Flattening to one layer would drop the texture file. What do you do?

A. `Usd.ZipFile` / USDZ (STORE) that includes `root.usda` and `tex.png`, after making asset paths package-relative
B. Email `tex.png` separately and keep absolute `/mnt` paths in the USDA
C. `FlattenLayerStack` only — it always embeds PNG bytes
D. Rename the USDA to `.usdc` so textures inline automatically

---

**COMP-066** · Obj 1.10 · Difficulty: Medium · Type: Single choice

Which override is legal **without** de-instancing a native instance?

A. `OverridePrim("/Room/A/Seat")` and set `size`
B. An opinion on the **instance root** `/Room/A` (purpose, primvar, variant selection, some metadata)
C. Editing `/__Prototype_1/Seat` from the assembly as the supported per-instance API
D. `AddReference` on the proxy child `/Room/A/Seat`

---

**COMP-067** · Obj 1.2 · Difficulty: Medium · Type: Single choice

A stadium of 80,000 identical seats that are never edited individually, plus a broadcast booth that is a unique hero set piece. Best pairing?

A. PointInstancer (or native instances) for seats; ordinary reference for the booth
B. Native instance every seat **and** the booth so they share one prototype
C. 80,000 full `def` copies of the seat asset
D. One payload for the entire stadium so seats cannot draw until LoadAll

---

**COMP-068** · Obj 1.11 · Difficulty: Easy · Type: Single choice

Why put a payload on the **contents** of a component rather than on the assembly root of a whole city block?

A. Payloads on the assembly root are illegal
B. Consumers can already see the component's interface/proxy and choose to load heavy geometry; a city-sized payload is a coarse all-or-nothing hitch
C. Payloads only work one level below `defaultPrim`
D. Assemblies cannot contain payloads if they also use sublayers

---

**COMP-069** · Obj 1.1 · Difficulty: Medium · Type: Single choice

A weaker layer prepends two references. A stronger layer authors an **explicit** `references = [@r2.usda@]` (no prepend/append/delete). What happens?

A. USD concatenates explicit with prepend
B. The explicit list **replaces** the weaker list-edits; only `r2` remains
C. The explicit list is ignored because prepend is sticky
D. Composition error `Pcp.ErrorType_InvalidAssetPath`

---

**COMP-070** · Obj 1.4 · Difficulty: Easy · Type: Single choice

Layer offset scale is `0.5`, offset is `0`. A sample at layer time 10 appears at which stage time?

A. `20` (`layerTime / scale`)
B. `5` (`offset + scale * layerTime = 5`)
C. `10` (scale never applies to samples)
D. `0.5`

---

**COMP-071** · Obj 1.3 · Difficulty: Medium · Type: Multiple select
Select two.

Which statements about **internal** vs **external** references are true?

A. `AddInternalReference("/Asset/Geo")` reuses a prim already on this stage (or in this layer stack) at a new path.
B. `AddReference("chair.usda")` introduces another layer; it needs `defaultPrim` or an explicit prim path.
C. Internal references are always stronger than external ones (they skip LIVERPS).
D. Internal references cannot carry attributes, only transforms.

---

**COMP-072** · Obj 1.6 · Difficulty: Medium · Type: Single choice

`custom rel looks` is a list-op field. A weaker layer prepends `/MatA`; a stronger layer prepends `/MatB`. What is the composed target list (strongest-first typical)?

A. Only `/MatA` (relationships do not list-edit)
B. `/MatB` then `/MatA` (list-ops **compose**; they are the exception to “scalar replace”)
C. `/MatA` then `/MatB` because weaker is “older”
D. Empty; two prepends cancel

---

**COMP-073** · Obj 1.1 · Difficulty: Medium · Type: USDA-reading

```usda
#usda 1.0
class "_I"
{
    double radius = 3
}

def Sphere "Ball" (
    prepend inherits = </_I>
)
{
    double radius = 1
}
```

What is composed `/Ball.radius`?

A. `3` (inherits beat local)
B. `1` (local beats inherits)
C. `2` (average)
D. `None` (local and inherit cancel)

---

**COMP-074** · Obj 1.3 · Difficulty: Hard · Type: Single choice

You need `/World/A` present and **loaded**, but `/World/B` must not appear in traversal at all. `LoadNone` is not enough because B is a **reference**. What do you use?

A. `OpenMasked` with a mask of `/World/A`
B. `Unload("/World/B")` — Unload works on references
C. `MuteLayer` on the root
D. `SetInstanceable(True)` on B

---

**COMP-075** · Obj 1.5 · Difficulty: Medium · Type: Single choice

Lighting arrives last and must override animation's `intensity` on `/World/Key`. How should `subLayers` be ordered (first listed = strongest)?

A. `[anim, lighting, layout]` so lighting is in the middle
B. `[lighting, anim, layout]` (or lighting above whoever it must beat)
C. `[layout, anim, lighting]` so lighting is last and therefore strongest
D. Order does not matter; lighting always beats anim by department name

---

**COMP-076** · Obj 1.10 · Difficulty: Medium · Type: Single choice

To hide a **root-level** property opinion on one instanceable chair without de-instancing, which is a supported pattern discussed for assemblies?

A. Nested `Block()` on `/Chair_0/Seat.size` while instanceable
B. Author a block or weaker-arc workaround at the **instance root**, or de-instance that chair if the property lives on a descendant proxy
C. `GetMaster().RemoveProperty("size")`
D. Delete the prototype prim from `/__Prototype_1`

---

**COMP-077** · Obj 1.8 · Difficulty: Easy · Type: Single choice

Where are relocates authored?

A. As a `rel relocates` relationship on each moved prim
B. As **layer metadata** `relocates = { </old>: </new> }` (Python: `layer.relocates` list of path pairs)
C. As a variant set named `relocates`
D. Only inside `UsdGeom.PointInstancer`

---

**COMP-078** · Obj 1.3 · Difficulty: Easy · Type: Single choice

`AddReference("explicit.usda", "/Only")` where `/Only` is a Cube with `size = 1` and the file has **no** `defaultPrim`. Result?

A. `UnresolvedPrimPath` and empty type
B. Type `Cube`, `size` `1` — an explicit path does not need `defaultPrim`
C. `InvalidAssetPath`
D. `AddReference` returns `False`

---

**COMP-079** · Obj 1.8 · Difficulty: Medium · Type: Multiple select
Select two.

A TD's new `radius` does not show in usdview. Which are common composition causes (Obj 1.8)?

A. The opinion is on a muted layer, a weaker arc (specialize vs reference), or an instance proxy path
B. The opinion is a local default that is losing to a **weaker** layer's time samples (weaker samples always win)
C. The edit target was a different layer than the one they inspected; or a variant selection is off; or LIVERPS put an inherit above their variant
D. `metersPerUnit` of 0.01 automatically discards `radius`

---

**COMP-080** · Obj 1.1 · Difficulty: Medium · Type: Single choice

A prim has a local `roughness = 0.5` over an inherit of `0.9` and a specialize of `0.2`. After `attr.Clear()` of the local opinion, what wins?

A. Specialize `0.2` (Clear jumps to the weakest arc)
B. Inherit `0.9` (I beats S; local is gone)
C. Schema fallback only
D. `0.5` remains because Clear cannot remove local specs

---

**COMP-081** · Obj 1.3 · Difficulty: Easy · Type: Single choice

`Usd.Stage.Open("city.usda")` with no load-set argument. The file payloads `/W/A`. Is `/W/A/Hi` present?

A. No — the default is `LoadNone`
B. Yes — the default initial load set is `Usd.Stage.LoadAll`
C. Only if `A` is also referenced
D. Only after `FindLoadable()`

---

**COMP-082** · Obj 1.3 · Difficulty: Medium · Type: Single choice

`AddReference("no_such_file.usda")` (the file does not exist). Which composition error is reported?

A. `Pcp.ErrorType_UnresolvedPrimPath`
B. `Pcp.ErrorType_InvalidAssetPath`
C. No error; `AddReference` returns `False`
D. `Tf.ErrorException` and the stage fails to open

---

**COMP-083** · Obj 1.8 · Difficulty: Medium · Type: Single choice

Root authors `r = 1`; session authors `r = 9`. What does `attr.GetPropertyStack()` list first?

A. Root, then session (weakest first)
B. Session, then root (strongest first) — display names like `…-session.usda`, then the root
C. Only the referenced asset
D. Property stacks exist only after `Flatten()`

---

**COMP-084** · Obj 1.4 · Difficulty: Medium · Type: Single choice

A **sublayer** is included as `@anim.usda@ (offset = 10)`. Samples in that file sit at 0 and 10. Composed sample times?

A. `[0.0, 10.0]` — offsets apply only to references, not sublayers
B. `[10.0, 20.0]` — the same `stageTime = offset + scale * layerTime` formula
C. `[10.0, 30.0]`
D. Samples are deleted; only defaults remain

---

**COMP-085** · Obj 1.6 · Difficulty: Easy · Type: Multiple select
Select two.

Which fields **list-edit** (compose by combining edits) rather than scalar-replace?

A. `double radius`
B. `references`, `payloads`, `inherits`, `specializes`, `variantSets`
C. `rel looks` (relationship targets)
D. Layer metadata `doc` concatenates every contributing layer's documentation string

---

**COMP-086** · Obj 1.5 · Difficulty: Medium · Type: Single choice

Layout owns `layout.usda`, animation owns `anim.usda`. A layout TD accidentally `SetEditTarget` to `anim.usda` and authors `/World/Chair.xformOp:translate`. What went wrong (Obj 1.5 / 1.8)?

A. Nothing — any local sublayer is an equally valid place for layout
B. The opinion is in the wrong department file; strength may still make it visible, but the workstream split is broken and anim's next save can collide
C. USD silently moves the opinion back to `layout.usda` on Save
D. Edit targets can only be the root layer, so the Set was a no-op

---

**COMP-087** · Obj 1.9 · Difficulty: Medium · Type: Single choice

`UsdUtils.FlattenLayerStack` vs `stage.Flatten()` for a vendor who **must keep** the ability to retarget `chair.usda` after delivery?

A. Use `Flatten()` so references become baked Cubes they can still retarget
B. Use `FlattenLayerStack` — sublayers collapse, **references remain** for the vendor to re-point
C. Neither keeps references
D. Only `root.Export()` keeps references and also bakes sublayers

---

**COMP-088** · Obj 1.7 · Difficulty: Medium · Type: Single choice

A character has two variant sets, `look` and `lod`, that should combine (`dirty` + `proxy`). How does OpenUSD model that?

A. One variant set with four packed names (`dirty_proxy`, …) is required; sets cannot combine
B. Two variant sets on the same prim; selections compose independently (`look=dirty`, `lod=proxy`)
C. Nested references, because variant sets cannot coexist
D. A PointInstancer prototype per combination

---

**COMP-089** · Obj 1.2 · Difficulty: Hard · Type: Single choice

Native instances of a chair share `/__Prototype_1`. A TD needs a **displayColor** change on every instance without de-instancing. Best composition-friendly option?

A. Edit `/Room/A/Seat.displayColor` on one proxy (illegal) and hope it broadcasts
B. Author an inherited class or a component-level primvar/material binding that the instances pick up, or set a primvar on each **instance root** if the shader reads it
C. `GetMaster()` and change the mesh once
D. Convert all chairs to unique `def` copies

---

**COMP-090** · Obj 1.11 · Difficulty: Medium · Type: Multiple select
Select two.

You are splitting a monolithic `Kitchen.usda` that inlined every chair mesh. Which pair matches Obj 1.11?

A. Publish `Chair.usda` as a component; the kitchen assembly **references** it at `Chair_0`, `Chair_1`, …
B. Keep all meshes in `Kitchen.usda` but add a variant per artist name
C. Mark instanceable on the assembly's chair prims if the chairs stay identical
D. Move each chair vertex into a separate payload file named after the vertex index

---

**COMP-091** · Obj 1.8 · Difficulty: Hard · Type: USDA-reading

```usda
#usda 1.0
class "_I"
{
    double radius = 3
}

def Sphere "Ball" (
    prepend inherits = </_I>
    prepend specializes = </_S>
)
{
}

def "_S"
{
    double radius = 7
}
```

Composed `/Ball.radius`?

A. `7` (specializes beat inherits)
B. `3` (inherits beat specializes)
C. `1` (Sphere fallback)
D. `5` (average of 3 and 7)

---

**COMP-092** · Obj 1.1 · Difficulty: Medium · Type: Single choice

You need a **studio-wide fallback** roughness that every asset can beat with a local opinion, but that should **lose** to a published reference. Inherit or specialize?

A. Inherit — it beats references, so assets could not override with a reference
B. Specialize — weakest arc; local and references still win, the class is only the fallback
C. Either; they have identical strength
D. Payload — payloads beat both inherits and specializes

---

## Answers

**COMP-001 — Answer: A.** LIVERPS is Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes. B drops relocates into last place. C swaps Inherits and VariantSets. D puts Local second. Review: §21.1.

**COMP-002 — Answer: C.** E is rElocates (the glossary spelling LIVERPS). Older LIVRPS material omitted relocates; clips and edit targets are not LIVERPS letters. Review: §21.1.

**COMP-003 — Answer: A, C.** Local beats referenced opinions (A). Inherits beat variants (C). Specializes are *weaker* than references (B is backwards). Value clips are not a LIVERPS letter (D). Review: §21.1–21.2.

**COMP-004 — Answer: B.** A local opinion is L, stronger than the reference (R). Specializes (A) are weaker than the reference, so `7` would lose to `1`. Muting the root (C) removes *your* local stack. Instancing (D) does not change radius strength. Review: §14.2, §19.3.

**COMP-005 — Answer: B.** Verified: inherit `3` beats referenced `1`. USD does not average (D) or cancel (C). The Sphere type comes along with the reference; it does not make R stronger than I. Review: §19.2, §21.6.

**COMP-006 — Answer: B.** Verified with an internal reference plus specialize: composed radius is `1`. Specializes are the weakest arc; listing order in USDA does not invert R vs S. Review: §19.3–19.4.

**COMP-007 — Answer: A, C.** Verified: prepended `r1` (`radius = 2`) beats appended `r2` (`radius = 8`). Prepend is stronger than append (C). USD allows both list-ops on one field (D is false). Review: §14.4.

**COMP-008 — Answer: B.** Verified on USD 26.08: composed radius is `3.0`. I beats V even when the variant is selected. Sphere fallback is not used when an opinion exists. Review: §21.2, §21.6.

**COMP-009 — Answer: A.** Sublayers extend the *same* layer stack and namespace. References (and payloads) introduce another prim index node at the referencing path. Sublayers are not weaker than references as a class (they are Local). Format is independent. Sublayers are not lazy; payloads are. Review: §15.1, §16.6.

**COMP-010 — Answer: B, C.** Payloads are the unloadable, weaker sibling of references. They do not beat local opinions (A is the opposite of what you want for shot overrides). They still use `defaultPrim` when the target path is omitted (D). Review: §17.1, §17.5.

**COMP-011 — Answer: B.** Verified: `LoadNone` leaves `/W/C/Hi` loaded (reference) and `/W/A/Hi` unloaded (payload). `LoadNone` is not a population mask and does not skip textures as its definition. Payloads are weaker, not stronger, than references. Review: §17.2, lab 16.

**COMP-012 — Answer: B.** Verified: `AddReference` returns `True`, composed type is `''`, error is `Pcp.ErrorType_UnresolvedPrimPath` (missing `defaultPrim`, no explicit path). `InvalidAssetPath` is the missing-*file* error. USD does not silently pick the first root prim. Review: §16.2, §16.5.

**COMP-013 — Answer: A, B.** Department layers that all edit `/World` are sublayers (same namespace). A published chair under a new path is a reference or payload. Inherits broadcast *class* opinions; they are not a department file stack. Specializes do not “copy an asset to a new path”; references do. Review: §15.5, §16.1.

**COMP-014 — Answer: B.** `stageTime = offset + scale * layerTime`. The same formula applies to reference offsets and sublayer offsets. Review: §16.4, §21.4.

**COMP-015 — Answer: B.** Verified: composed sample times are `[10.0, 20.0]`. Layer times 0 and 10 plus offset 10. Review: §16.4, lab 16.

**COMP-016 — Answer: B.** Verified: `Get()` and `Get(Usd.TimeCode.Default())` return `(100, 0, 0)`. Layer offsets remap *time samples*, not the default. `Get()` is default time; it is `None` only when **no** default exists (samples-only). Review: §10.5, §21.3.

**COMP-017 — Answer: B.** Verified in lab 19: `GetEditTargetForLocalLayer` maps stage time 20 through offset 10 → stored at 10. A bare `EditTarget` records 20. Review: §15.2–15.3.

**COMP-018 — Answer: A.** Collaborative shots are a strong-to-weak `subLayers` list with one owner per file. Specializes, instancing, and flattening are the wrong tools for live multi-user authoring. Review: §15.5, §22.2.

**COMP-019 — Answer: B.** Verified: `SetEditTarget` on an anonymous (or referenced-only) layer raises `Tf.ErrorException` because the layer is not in the local LayerStack. Review: §15.3, lab 19.

**COMP-020 — Answer: A.** Animation belongs in the anim *sublayer* via a local-stack edit target (preferably `GetEditTargetForLocalLayer` so offsets map). The session layer is not a publish target; flattening destroys the collaborative stack. Review: §15.3, §15.5.

**COMP-021 — Answer: A, C.** First listed sublayer wins. Session is for scratch, not for the show. Sharing one root file (B) invites overwrite races. Putting layout and anim on different prim paths (D) splits the scene instead of overlaying `/World`. Review: §15.1, §15.5, §22.2.

**COMP-022 — Answer: A.** Variants are named, discrete options inside one asset. Instancing, multi-user layering, and beating local opinions are other arcs' jobs. Review: §18.5.

**COMP-023 — Answer: A, C.** Continuous parameters belong on attributes, not variant combinatorics. Shot animation belongs in shot layers (references to clips / time samples), not in the character's variant set. Looks and LODs (B, D) are classic variant uses. Review: §18.5.

**COMP-024 — Answer: B.** Verified: with selection `''`, `GetVariantEditContext()` authors `height = 3` on the prim itself; the `big` variant block is empty. Always `SetVariantSelection` before the context when you mean to fill a variant. Review: §18.2, lab 17.

**COMP-025 — Answer: B.** Variants switch options packaged *inside* one asset. A separately published hero is a new reference/payload at the assembly. Variants can contain meshes (A is false). Strength is LIVERPS, not “references always beat variants.” Review: §18.5, §16.1.

**COMP-026 — Answer: A, C.** Muting drops the layer from the stack (verified: mute strong → composed 7). Wrong edit target is the other common “I wrote it but I don't see it” cause. Instancing does not resurrect muted opinions; mute does not delete files. Review: §15.4, §22.6.

**COMP-027 — Answer: B.** Verified: `OverridePrim` on an instance proxy raises `Tf.ErrorException`. USD does not silently retarget the prototype. Review: §24.3, §22.4, lab 23.

**COMP-028 — Answer: B.** Verified: composed height is `1.0` even with `size = big`, because local beats variant. This is a standard “variant did nothing” debug. Review: §18.6, §21.2.

**COMP-029 — Answer: B.** Relocates move the namespace; opinions left at the old source path do not follow. Author at the destination (or in the asset before relocate). Relocates apply to referenced structure, not payloads only. Review: §20.3–20.4.

**COMP-030 — Answer: A.** `Stage.Flatten()` bakes arcs into one layer (verified: no `references` field; `/Refd` becomes a Cube). `FlattenLayerStack` keeps references. `Export` of a root layer writes that layer's specs, it does not flatten. USDZ can still describe arcs inside the package. Review: §22.3, §34.2.

**COMP-031 — Answer: A, B.** Verified on the bolt/shot setup: Flatten bakes `/Refd` to Cube and includes `/Bolt`; FlattenLayerStack keeps `prepend references` on `/Refd`, inlines `/Bolt`, `subLayers` empty. They are not identical (C). Session inclusion is a separate Flatten flag/behavior, not unique to FlattenLayerStack (D). Review: §34.2, lab 28.

**COMP-032 — Answer: A.** Instancing is opted in at the **use** site (assembly instance roots) so the published component remains a normal asset. Nesting `instanceable` on every gprim is the wrong grain. Review: §24.1, §22.4.

**COMP-033 — Answer: B.** Nested proxy authoring is forbidden (see COMP-027). De-instance that one root, then override `Seat`; other instanceable chairs still share `/__Prototype_N` (verified: sibling size stays 1). `GetMaster()` is gone. Muting the assembly is unrelated. Review: §24.5–24.6, §22.4.

**COMP-034 — Answer: A.** Verified: `GetPrototype()` path is `/__Prototype_1`; `hasattr(prim, "GetMaster")` is `False` on usd-core 26.8. PointInstancer is a different instancing style. Review: §24.2, lab 23.

**COMP-035 — Answer: A.** Split by workstream into layers connected with sublayers/references/payloads; keep a thin interface. Copy/flatten, PointInstancer, and class-only encoding do not give two teams safe files. Review: §22.1, §23.2.

**COMP-036 — Answer: A, C.** Heavy contents behind payloads; shot departments as ordered sublayers on a shared `/World`. Do not hide show animation inside the character asset (B). Relocates are for namespace repair, not a substitute for a consistent model hierarchy (D). Review: §22.1–22.2, §17.5.

**COMP-037 — Answer: B.** PointInstancer is the scale for huge, similar, mostly uniform copies with per-instance transforms and cheap hides (`invisibleIds`). Native instances still cost one prim each; full copies cost full composition. Review: §25.1, §26.1.

**COMP-038 — Answer: B.** Native instances for the crowd of identical chairs; de-instance (or don't instance) the one hero that needs nested modeling. PointInstancer is the wrong grain for hero furniture. Editing the prototype changes every instance. Payloads do not turn instancing off. Review: §26.1, §24.5.

**COMP-039 — Answer: A, B.** Unique heroes → ordinary refs; identical furniture at hundreds → native instances. Millions of pebbles belong on a PointInstancer, not one native instance prim each (C, D are wrong). Review: §26.1.

**COMP-040 — Answer: B.** Population masks use `Usd.Stage.OpenMasked`, not `Open(path, mask=...)`. `LoadNone` still *creates* payload prims and still loads references (COMP-011). Muting a whole layer is coarser than masking one subtree and may drop unrelated opinions. Review: §17.4, lab 16.

**COMP-041 — Answer: B.** Verified: delete `r1` from prepend `[r1, r2]` leaves `r2`, composed radius `8`. Delete removes listed items; it does not empty the list (C) or average (D). Review: §14.4.

**COMP-042 — Answer: B.** Verified: stronger default `5` wins at `Get()`, `Get(0)`, and `Get(10)`; `GetTimeSamples()` is `[]`. Weaker samples do not leak through a stronger default. Review: §21.3.

**COMP-043 — Answer: C.** Verified: `Sdf.LayerOffset(10, 2)` maps layer times 0 and 10 to stage times 10 and 30. `stageTime = offset + scale * layerTime`. Review: §16.4, §21.4.

**COMP-044 — Answer: B.** Verified: `AddInternalReference("/Asset/Geo")` returns `True` and `/Inst.sz` is `4`. Internal references are same-stage/same-stack reuse, not disk-only. Review: §16.3.

**COMP-045 — Answer: B.** Verified: `FindLoadable()` returns `['/W/A', '/W/B']` — payload sites only, not the reference at `/W/C`. Review: §17.2, lab 16.

**COMP-046 — Answer: A, B.** Verified: `LoadNone` → `/W/A/Hi` missing, `IsLoaded()` False; `Load` brings `Hi` in; `Unload` removes it. `LoadNone` is the initial set, not a lock (C). `FindLoadable` is payloads only (D). Review: §17.2.

**COMP-047 — Answer: B.** Verified: local on A is `0.9`; B stays at the class `0.2`. Inherits broadcast until a stronger local opinion appears on that prim. Review: §19.2, lab 18.

**COMP-048 — Answer: B.** Verified: after the class moves to `0.5`, A stays `0.9` (local) and B becomes `0.5` (still inheriting). Review: §19.2.

**COMP-049 — Answer: B.** Verified: `GetVariantNames()` → `['big', 'small']`; `GetNames()` on the `VariantSet` raises `AttributeError`; `VariantSets.GetNames()` lists set names such as `['size']`. Review: §18.1, lab 17.

**COMP-050 — Answer: A.** Verified: `OverridePrim` creates a handle, `IsDefined()` False, specifier `Sdf.SpecifierOver`. `Traverse()` skips it. A typeless `def` would define it. Review: §20.1.

**COMP-051 — Answer: B.** Verified: first listed sublayer wins (`1`). Last-listed-wins is a CSS myth. Review: §15.1.

**COMP-052 — Answer: A.** Verified: `OpenMasked` with `/W/A` keeps A and drops B. `Open(path, mask=)` is not the API. `LoadNone` is a different switch. Review: §17.4, lab 16.

**COMP-053 — Answer: B.** Verified: shot-level `class "_Look"` with `0.9` changes the referenced `/Hero.roughness` via implied inherits. You do not have to re-`AddInherit` on `/Hero`. Review: §19.5.

**COMP-054 — Answer: A, B.** Verified: composed radius is `9`; the root spec still stores `1`. Saving the root does not publish the session layer. A weaker sublayer cannot beat the session. Review: §15.3, lab 04.

**COMP-055 — Answer: B.** Verified: after `Block()`, `Get()` is `None` even on `UsdGeom.Sphere` radius (not the schema fallback `1`). A block is a strong empty opinion. Review: §21.3, §22.4.

**COMP-056 — Answer: B.** Scalars resolve to one winner. List-ops are the fields that combine. Weaker specs stay on disk. Composition runs when the stage is composed, not only at flatten. Review: §14.6.

**COMP-057 — Answer: B.** Clips are not a LIVERPS letter. They resolve inside the introducing node's strength. Review: §21.1, §21.5.

**COMP-058 — Answer: A, C.** Flatten or USDZ plus localized paths; ship or avoid proprietary schemas. Do not ship the session layer. Do not leave `/mnt/show` paths. Review: §22.3, §34.2–34.3.

**COMP-059 — Answer: B.** Verified in lab 19: `EditContext` restores the previous target (root). Review: §15.3.

**COMP-060 — Answer: A.** Verified: overlay-only `over` → not defined, empty `Traverse()`; typeless `def` → defined and listed. Review: §20.1.

**COMP-061 — Answer: B.** Same animation, different `LayerOffset` on each reference (Obj 1.4). Duplicating files, per-frame variants, and instancing do not offset time. Review: §16.4.

**COMP-062 — Answer: B.** Published variants are for reused, named options. A one-off belongs in the shot. Specializes do not beat local. Review: §18.5, §22.2.

**COMP-063 — Answer: B.** Prim stack is strongest first. Root then referenced asset. Review: §14.5, §22.5.

**COMP-064 — Answer: A, C.** Interface/payload/geo/mtl split plus shot department sublayers. Per-polygon files and stuffing departments into the asset variant set are the wrong grain. Review: §22.1, §23.2.

**COMP-065 — Answer: A.** USDZ STORE can hold `root.usda` plus `tex.png` (lab 28). Flattening does not embed PNG bytes. Review: §22.3, §7.4, lab 28.

**COMP-066 — Answer: B.** Verified: instance-root opinions (e.g. `purpose = guide`) are legal; nested `OverridePrim` on a proxy raises. Do not treat prototype internals as the per-instance API. Review: §24.4–24.5.

**COMP-067 — Answer: A.** Huge identical seats → PointInstancer or native instances; unique booth → ordinary reference. Sharing a prototype with the booth would block nested booth edits. Review: §26.1.

**COMP-068 — Answer: B.** Payload the heavy component contents so the interface stays cheap; a city-root payload is too coarse. Payloads on assemblies are legal, just usually the wrong hitch. Review: §17.5, §22.1, §26.2.

**COMP-069 — Answer: B.** An explicit list replaces weaker prepend/append/delete. It does not concatenate. Review: §14.4.

**COMP-070 — Answer: B.** `0 + 0.5 * 10 = 5`. Review: §16.4.

**COMP-071 — Answer: A, B.** Internal = path on this stage; external = another layer + `defaultPrim` or explicit path. Internal refs still follow LIVERPS and can carry attributes (verified `sz = 4`). Review: §16.2–16.3.

**COMP-072 — Answer: B.** Verified: session prepend `/MatB` plus root prepend `/MatA` → targets `['/MatB', '/MatA']`. Relationships list-edit. Review: §14.4, §14.6.

**COMP-073 — Answer: B.** Verified: local `1` beats inherit `3`. Review: §19.2, §21.2.

**COMP-074 — Answer: A.** References ignore `Unload`/`LoadNone`. A population mask is the tool that omits `/World/B` entirely. Muting the root drops everything. Review: §17.4.

**COMP-075 — Answer: B.** First listed is strongest, so lighting must appear before anim if it must win. Last-listed-wins is wrong. Review: §15.1, §15.5.

**COMP-076 — Answer: B.** Nested proxy `Block()` is the same illegal authoring as COMP-027. Instance-root opinions or de-instancing are the assembly patterns. `GetMaster` is gone; do not delete prototypes. Review: §22.4, §24.6.

**COMP-077 — Answer: B.** Relocates are layer metadata; Python `layer.relocates` is a list of path pairs. Review: §20.3.

**COMP-078 — Answer: B.** Verified: explicit `/Only` → type Cube, size 1, no `defaultPrim` required. Review: §16.2, lab 14.

**COMP-079 — Answer: A, C.** Muted/wrong-arc/proxy (A) and wrong target / variant / LIVERPS (C) are the checklist. Weaker samples do **not** beat a stronger default (COMP-042). `metersPerUnit` does not drop `radius`. Review: §22.6.

**COMP-080 — Answer: B.** Verified: local `0.5` then `Clear()` → inherit `0.9` (I beats S). Review: §19.3–19.4, lab 18.

**COMP-081 — Answer: B.** Verified: default `Open` loads payloads (`/W/A/Hi` True). `LoadNone` is opt-in. Review: §17.2.

**COMP-082 — Answer: B.** Verified: missing file → `Pcp.ErrorType_InvalidAssetPath`. Missing `defaultPrim` is `UnresolvedPrimPath` (COMP-012). `AddReference` still returns True. Review: §16.5.

**COMP-083 — Answer: B.** Verified: property stack lists session then root (strongest first). Review: §22.5, lab 21.

**COMP-084 — Answer: B.** Verified: sublayer offset 10 maps samples to `[10.0, 20.0]`. Same formula as reference offsets. Review: §15.2, §16.4.

**COMP-085 — Answer: B, C.** Composition-arc fields and relationships list-edit. `double radius` and most metadata (`doc`) scalar-replace; documentation strings do not concatenate. Review: §14.4, §14.6.

**COMP-086 — Answer: B.** Edit targets write into a specific layer; the opinion can still compose as Local, but it lives in the wrong workstream file. USD does not relocate it on Save. Review: §15.3, §15.5.

**COMP-087 — Answer: B.** Verified: FlattenLayerStack keeps `prepend references`; Flatten bakes them away. `Export` of the root writes only that layer's specs (subLayers still listed, not baked). Review: §34.2.

**COMP-088 — Answer: B.** Multiple variant sets on one prim combine by independent selections. Packing names into one set is optional, not required. Review: §18.1, §18.3.

**COMP-089 — Answer: B.** Instance-root primvars / inherited classes / material binds at a level the prototype reads. Nested proxy edits are illegal; `GetMaster` is gone; unique copies defeat instancing. Review: §24.4–24.5.

**COMP-090 — Answer: A, C.** Extract a component asset and reference it; instance identical copies. Artist-name variants and per-vertex payloads are the wrong split. Review: §22.1, §23.4, lab 22.

**COMP-091 — Answer: B.** Verified: inherit `3` beats specialize `7`. Review: §19.3, §21.2.

**COMP-092 — Answer: B.** Specializes are the weakest fallback (R beats S). Inherits would beat the published reference. Review: §19.3–19.4.

---

*Composition domain complete: COMP-001–COMP-092 (target 92).*
