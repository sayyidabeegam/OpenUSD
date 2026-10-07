# Chapter 22 — Composition Design and Debugging

> **Exam domain:** Composition (23%) · **Objectives:** 1.2, 1.5, 1.8, 1.9, 1.10, 1.11 · **Study day:** 7 · **Est. time:** 150 min
> **Prerequisites:** Ch 14–21 (all composition arcs, LIVERPS, value resolution)

Chapters 14–21 taught you each composition tool on its own. This chapter is about using them together, the way a studio or a factory does. You will split one big asset into files that several people can edit at once. You will layer a shot so departments do not overwrite each other. You will turn an internal asset into a clean package for a client. You will change instanced furniture without breaking instancing. Finally, you will learn the tools and the checklist that answer the most common composition question of all: "I authored a value, so why don't I see it?"

## Learning goals

- Split a monolithic asset into geometry, material, and layout workstreams using sublayers and references.
- Design a shot layer stack that lets several departments and artists work at the same time.
- Prepare an internal asset for external delivery with `Usd.Stage.Flatten`, `UsdUtils.FlattenLayerStack`, `UsdUtils.LocalizeAsset`, and `UsdUtils.CreateNewUsdzPackage`.
- Remove or hide properties and child prims of instanced components without editing inside an instance.
- Debug composition with `GetPrimStack`, `GetPropertyStack`, `GetResolveInfo`, `Usd.PrimCompositionQuery`, prim index dumps, and `GetCompositionErrors`.
- Apply a ten-point checklist to explain why an opinion does not take effect.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Monolithic asset** | An asset whose geometry, materials, and everything else live in one file. |
| **Workstream** | One kind of work (modeling, surfacing, layout, animation) done by one team or person. |
| **Workstream layer** | A layer that holds only one workstream's opinions, for example `chair_geo.usda`. |
| **Entry layer** | The file other people reference to use an asset; it pulls in the workstream layers. |
| **Edit target** | The layer (and optional variant) that `Usd` authoring calls write into (Ch 15). |
| **Session layer** | An in-memory layer stronger than the root layer, not saved with the stage (Ch 3). |
| **Flatten** | Bake a composed result into one layer with no composition arcs to other files. |
| **Localize** | Copy an asset and all its dependencies into one folder and rewrite paths to point there. |
| **USDZ package** | A single uncompressed zip archive holding layers and textures (Ch 7, Ch 31). |
| **Instance proxy** | A read-only prim you see under an instance; it stands for a prim in the prototype (Ch 24). |
| **Prototype** | The shared, read-only prim tree that all matching instances use (Ch 24). |
| **Value block** | An opinion of `None` that says "no value here", hiding weaker values. |
| **Prim stack** | The list of prim specs that contribute to a prim, strongest first. |
| **Property stack** | The list of property specs that contribute to an attribute or relationship, strongest first. |
| **Prim index** | The tree of composition nodes (arcs) Pcp builds for one prim (Ch 14). |

---

## 22.1 Splitting a monolithic asset into workstreams

### 1. What is it?

**Splitting a monolithic asset** means moving each kind of work into its own layer. Geometry goes into a geometry layer, materials into a material layer, and an entry layer combines them. Each team edits only its own file.

### 2. Why do we need it?

If a modeler and a surfacing artist both open and save the same file, the last save wins and the other person's work is lost. Even with file locking, only one person can work at a time. Splitting the asset lets both work in parallel. It also makes publishing safer: a material change produces a new version of the material layer only, so you know exactly what changed.

### 3. Beginner explanation

Think of the transparent sheets on an overhead projector. Instead of drawing the outline and the colors on one sheet, the modeler draws outlines on one sheet and the painter colors on another. Stack them, and you see the full picture. Each person takes away and redraws only their own sheet.

Where the analogy breaks: USD sheets are not pixels. Each sheet holds named opinions (prims and properties). If two sheets set the same property, only the stronger one is used; the weaker one is not mixed in.

### 4. Technical explanation

A common split for a component asset has three or four files:

| File | Contains | Typical owner |
|------|----------|---------------|
| `chair.usda` (entry layer) | `defaultPrim`, `kind`, variant sets, the class it inherits from, sublayer list | Asset lead / pipeline |
| `chair_geo.usda` | Meshes, transforms, extents, primvars such as UVs | Modeling |
| `chair_mtl.usda` | `Material` and `Shader` prims, `material:binding` relationships | Surfacing |
| `chair_rig.usda` (optional) | Rigging or physics data | Rigging |

Rules that make the split work:

- **All workstream layers describe the same namespace.** Each file writes under `/Chair`, using `def` for prims it owns and `over` for prims another file defines (Ch 20). That is why **sublayers** are the natural tool inside one asset: sublayers merge layers that share the same paths (Ch 15).
- **Order sets priority.** In `subLayers = [@./chair_mtl.usda@, @./chair_geo.usda@]` the first entry is stronger. Put the layer that "decorates" others (materials) above the layer it decorates (geometry).
- **Avoid overlap.** If two workstream layers set the same property, one silently wins. Agree on ownership: geometry never authors `material:binding`; surfacing never authors `points`.
- **References combine assets; sublayers combine workstreams.** A set or room file *references* `chair.usda` (Ch 16). The reference brings the whole layer stack of the asset under a new prim path. Layout is a scene-level workstream: it lives in its own layer of the set or shot, and only places references.
- **Payloads** often wrap the heavy workstream layers so a scene can skip loading them (Ch 17). The detailed "asset interface" pattern (entry layer → payload → geo/mtl) is in Chapter 23.

In Python you author each workstream with an **edit target** (Ch 15): `stage.SetEditTarget(Usd.EditTarget(geo_layer))` sends every following `Usd` authoring call into `chair_geo.usda`.

### 5. Mental model

```text
            chair.usda  (entry: defaultPrim, kind, subLayers)
                 |
        +--------+---------+
        |                  |
  chair_mtl.usda     chair_geo.usda        <- sublayers, same /Chair namespace
  (stronger)         (weaker)
  over Seat:         def Mesh Seat:
   material:binding   points, extent

  room.usda:  def "Chair_1" ( references = @chair.usda@ )   <- layout
```

One namespace, many files, one owner per file.

### 6. Simple example

| Before (monolithic) | After (split) |
|---------------------|---------------|
| `chair.usda` holds `/Chair/Geom/Seat` (mesh) and `/Chair/Looks/Wood` (material) and the binding | `chair_geo.usda` holds the mesh; `chair_mtl.usda` holds the material and the binding; `chair.usda` sublayers both |

The composed stage is identical. Only the file that each opinion lives in has changed.

### 7. USDA example

*File: chair.usda* (entry layer)

```usda
#usda 1.0
(
    defaultPrim = "Chair"
    subLayers = [
        @./chair_mtl.usda@,
        @./chair_geo.usda@
    ]
)

def Xform "Chair" (
    kind = "component"
)
{
}
```

*File: chair_geo.usda* (modeling owns this)

```usda
#usda 1.0

over "Chair"
{
    def Xform "Geom"
    {
        def Cube "Seat"
        {
            double size = 1
        }
    }
}
```

*File: chair_mtl.usda* (surfacing owns this)

```usda
#usda 1.0

over "Chair"
{
    def Scope "Looks"
    {
        def Material "Wood"
        {
        }
    }

    over "Geom"
    {
        over "Seat" (
            prepend apiSchemas = ["MaterialBindingAPI"]
        )
        {
            rel material:binding = </Chair/Looks/Wood>
        }
    }
}
```

Line notes: the entry layer `def`s `/Chair` and lists the sublayers, strongest first. `chair_geo.usda` uses `over "Chair"` because it does not own the root prim, then `def`s the seat it does own. `chair_mtl.usda` uses `over` all the way down to the seat it decorates, applies `MaterialBindingAPI` (required before binding), and binds.

### 8. Python example

The script builds the split asset from scratch with edit targets, saves it, reopens it, and reports which file each opinion lives in.

```python
from pxr import Usd, Sdf, UsdGeom, UsdShade

geo = Sdf.Layer.CreateNew("chair_geo.usda")
mtl = Sdf.Layer.CreateNew("chair_mtl.usda")
stage = Usd.Stage.CreateNew("chair.usda")
root = stage.GetRootLayer()
root.subLayerPaths = ["./chair_mtl.usda", "./chair_geo.usda"]

chair = UsdGeom.Xform.Define(stage, "/Chair")
Usd.ModelAPI(chair.GetPrim()).SetKind("component")
stage.SetDefaultPrim(chair.GetPrim())

stage.SetEditTarget(Usd.EditTarget(geo))          # modeling workstream
UsdGeom.Xform.Define(stage, "/Chair/Geom")
UsdGeom.Cube.Define(stage, "/Chair/Geom/Seat").CreateSizeAttr(1.0)

stage.SetEditTarget(Usd.EditTarget(mtl))          # surfacing workstream
mat = UsdShade.Material.Define(stage, "/Chair/Looks/Wood")
seat = stage.GetPrimAtPath("/Chair/Geom/Seat")
UsdShade.MaterialBindingAPI.Apply(seat).Bind(mat)

for layer in (root, geo, mtl):
    layer.Save()


def authored_paths(layer):
    found = []
    keep = lambda p: p.IsPrimPath() or p.IsPropertyPath()
    layer.Traverse("/", lambda p: found.append(str(p)) if keep(p) else None)
    return sorted(found)


for name in ("chair.usda", "chair_geo.usda", "chair_mtl.usda"):
    print(name)
    for path in authored_paths(Sdf.Layer.FindOrOpen(name)):
        print("   ", path)

reopened = Usd.Stage.Open("chair.usda")
seat = reopened.GetPrimAtPath("/Chair/Geom/Seat")
bound, _ = UsdShade.MaterialBindingAPI(seat).ComputeBoundMaterial()
print("bound material:", bound.GetPath())
print("seat specs from:", [s.layer.GetDisplayName() for s in seat.GetPrimStack()])
```

**Expected output**

```text
chair.usda
    /Chair
chair_geo.usda
    /Chair
    /Chair/Geom
    /Chair/Geom/Seat
    /Chair/Geom/Seat.size
chair_mtl.usda
    /Chair
    /Chair/Geom
    /Chair/Geom/Seat
    /Chair/Geom/Seat.material:binding
    /Chair/Looks
    /Chair/Looks/Wood
bound material: /Chair/Looks/Wood
seat specs from: ['chair_mtl.usda', 'chair_geo.usda']
```

The entry layer holds only `/Chair` (its `kind` is metadata on that prim, so it is not a separate path). The seat has two prim specs, one per workstream file. Each team's file contains only its own opinions plus the `over`s needed to reach them.

### 9. Real-world use case

A furniture manufacturer builds a digital twin of a showroom. CAD conversion writes `sofa_geo.usda` every night from the engineering data. A visualization artist owns `sofa_mtl.usda` and tweaks fabrics during the day. Because the nightly conversion overwrites only the geometry layer, the artist's material work is never lost, and the next morning's composed sofa has new geometry with the same fabrics.

### 10. Common mistakes

> [!MISTAKE] Using `def` for the same prim in two workstream layers with different types (for example `def Mesh "Seat"` and `def Cube "Seat"`). The stronger type wins and the other team's data no longer fits. Fix: only the owning layer `def`s a prim; other layers use `over`.

> [!MISTAKE] Putting the workstream layers in as *references* to the same prim path. That works, but it forces each file to have its own `defaultPrim` and makes the files look like separate assets. Fix: inside one asset, use sublayers; use references to bring whole assets into a scene.

> [!MISTAKE] Letting two workstreams author the same property (for example both set `primvars:displayColor`). One wins silently. Fix: write down which layer owns which properties and check with `GetPropertyStack` (§22.5).

### 11. Exam traps

> [!TRAP] "Split the asset so modeling and surfacing can work in parallel" → the answer is separate layers combined by sublayers (or by the asset interface), not variant sets. Variants are alternatives you *choose between*; workstreams are parts you *combine*.

> [!TRAP] Sublayer order: the first path in `subLayers` is the strongest. A question may list the material layer second and ask why a material opinion loses.

### 12. Practice questions

1. A modeler and a lighter must edit the same asset at the same time without overwriting each other's work. Which structure fits best?
   A. One file with two variant sets, `model` and `light`
   B. Separate layers per workstream, combined as sublayers of the asset's entry layer
   C. Two copies of the asset file, merged by hand each night
   D. One file, with each artist using a different edit target inside it

2. In `subLayers = [@./a_geo.usda@, @./a_mtl.usda@]`, both layers author `primvars:displayColor` on the same mesh. Whose value wins?

3. Why does `chair_mtl.usda` use `over "Seat"` rather than `def Mesh "Seat"`?

**Answers**

1. **B.** Separate workstream layers let each person save their own file. Variants (A) are alternatives, not parallel parts. D still has both artists writing one file.
2. **`a_geo.usda`**, because it is listed first and the first sublayer is strongest. Ownership rules should prevent this overlap.
3. The material layer does not own the seat. An `over` adds opinions without defining the prim, so the geometry layer stays the single place that defines its type.

### 13. Exam takeaways

> [!KEY]
> - One asset, one namespace, several workstream layers combined with **sublayers**.
> - The first sublayer is strongest; put "decorating" layers (materials) above geometry.
> - Only the owning layer `def`s a prim; others use `over`.
> - Assets come into scenes by **reference** (or payload); layout is its own layer in the scene.

---

## 22.2 Multi-user scene layering

### 1. What is it?

**Multi-user scene layering** is a plan for a shot or scene where each department, and sometimes each artist, writes into its own layer. The shot's root layer sublayers all of them in an agreed order.

### 2. Why do we need it?

A shot is touched by layout, animation, effects, and lighting, often on the same day. Without separate layers, they would fight over one file. With separate layers, the strength order also encodes **who may override whom**: lighting can fix a small layout problem in its own layer without asking layout to republish.

### 3. Beginner explanation

Picture a group project where each person writes on their own transparent sheet, and the sheets are stacked in a fixed order: the teacher's correction sheet on top, then the final editor, then the writers. Anyone can make a change on their own sheet, and the stacking order decides whose change you see when two people touch the same spot.

Where the analogy breaks: in USD, "seeing" is per property. A stronger sheet hides a weaker one only for the exact properties it sets; everything else on the weaker sheet still shows through.

### 4. Technical explanation

A typical shot layer stack, strongest first:

| Position | Layer | Why here |
|----------|-------|----------|
| (memory) | session layer | Temporary experiments in a tool; never saved (Ch 3) |
| 0 | `shot.usda` (root) | Shot-specific fixes by a supervisor |
| 1 | `shot_lighting.usda` | Lighting is late in the pipeline and may adjust anything |
| 2 | `shot_fx.usda` | Effects |
| 3 | `shot_anim.usda` | Animation overrides layout transforms |
| 4 | `shot_layout.usda` | References the set and characters, places them |
| 5 | `seq_010.usda` | Sequence-wide opinions shared by all shots |

Design rules:

- **One writer per layer.** Two people writing one layer at the same time causes lost work. If a department has several artists, give each a sub-layer (for example `shot_anim_jane.usda`) sublayered into the department layer.
- **Downstream departments are stronger.** A department that works later (lighting) usually sits above one that works earlier (layout), so late fixes win without republishing.
- **Shared layers are weaker.** Sequence or project layers go at the bottom so any shot can override them.
- **Use edit targets, not file juggling.** A tool sets `stage.SetEditTarget(Usd.EditTarget(layer))` to the artist's own layer. All `Usd` authoring then goes there.
- **Isolate with muting.** `stage.MuteLayer(identifier)` removes a layer's opinions from the composed result without editing any file (Ch 15). It is ideal for "what did animation change?".
- **Time offsets per layer.** `Sdf.Layer.subLayerOffsets` can shift a department layer in time (Ch 10, Ch 15).

### 5. Mental model

```text
 session (memory, not saved)           strongest
 shot.usda            <- supervisor fixes
 shot_lighting.usda   <- lighting artist's edit target
 shot_fx.usda
 shot_anim.usda       <- animator's edit target
 shot_layout.usda     <- references set + characters
 seq_010.usda                          weakest
```

Each artist points the edit target at their own row. The column order decides conflicts.

### 6. Simple example

Layout gives the ball radius `1.0`. An animator, by accident, sets radius `1.5` in `shot_anim.usda`. Because animation is stronger, the shot shows `1.5`. Muting `shot_anim.usda` instantly shows `1.0` again, which tells the supervisor which department changed it.

### 7. USDA example

*File: shot.usda*

```usda
#usda 1.0
(
    subLayers = [
        @./shot_lighting.usda@,
        @./shot_anim.usda@,
        @./shot_layout.usda@,
        @./seq_010.usda@
    ]
    startTimeCode = 1
    endTimeCode = 24
)
```

*File: shot_anim.usda*

```usda
#usda 1.0

over "World"
{
    over "Ball"
    {
        double radius = 1.5
        double3 xformOp:translate.timeSamples = {
            1: (0, 0, 0),
            24: (10, 0, 0),
        }
    }
}
```

Line notes: the root layer has no prims at all; it only orders the department layers. The animation layer uses `over` because layout defines `/World/Ball`.

### 8. Python example

```python
from pxr import Usd, Sdf, UsdGeom

order = ["shot_lighting.usda", "shot_anim.usda", "shot_layout.usda"]
layers = {name: Sdf.Layer.CreateNew(name) for name in order}
stage = Usd.Stage.CreateNew("shot.usda")
stage.GetRootLayer().subLayerPaths = ["./" + n for n in order]

stage.SetEditTarget(Usd.EditTarget(layers["shot_layout.usda"]))
ball = UsdGeom.Sphere.Define(stage, "/World/Ball")
ball.CreateRadiusAttr(1.0)

stage.SetEditTarget(Usd.EditTarget(layers["shot_anim.usda"]))
ball.GetRadiusAttr().Set(1.5)                       # the accidental edit

print("layer stack, strongest first:")
for layer in stage.GetLayerStack():
    print("   ", layer.GetDisplayName())
print("radius:", ball.GetRadiusAttr().Get())
winner = ball.GetRadiusAttr().GetPropertyStack()[0].layer
print("winning layer:", winner.GetDisplayName())

stage.MuteLayer(layers["shot_anim.usda"].identifier)
print("anim muted, radius:", ball.GetRadiusAttr().Get())
stage.UnmuteLayer(layers["shot_anim.usda"].identifier)

stage.SetEditTarget(Usd.EditTarget(stage.GetSessionLayer()))
ball.GetRadiusAttr().Set(3.0)                       # a quick experiment
print("session experiment:", ball.GetRadiusAttr().Get())
stage.GetSessionLayer().Clear()
print("after clearing session:", ball.GetRadiusAttr().Get())
```

**Expected output**

```text
layer stack, strongest first:
    shot-session.usda
    shot.usda
    shot_lighting.usda
    shot_anim.usda
    shot_layout.usda
radius: 1.5
winning layer: shot_anim.usda
anim muted, radius: 1.0
session experiment: 3.0
after clearing session: 1.5
```

`GetLayerStack()` lists the session layer first because it is the strongest. Muting is non-destructive: unmuting brings the animation opinion back.

### 9. Real-world use case

In a game cinematic team, the layout artist publishes `cine_layout.usda` with camera and character placements. Two animators each own a sublayer of `cine_anim.usda`. The lighting artist works above all of them. When the director asks why a prop moved, the lead mutes each animator's layer in turn and sees the prop jump back when the right one is muted.

### 10. Common mistakes

> [!MISTAKE] Leaving the edit target at the root layer, so every department's edits land in `shot.usda`. Fix: set the edit target to the department layer at tool start-up, and check `stage.GetEditTarget().GetLayer()` before saving.

> [!MISTAKE] Putting a shared sequence layer *above* the shot layers. Then a sequence change silently overrides every shot's fixes. Fix: shared layers go at the bottom.

> [!MISTAKE] Doing experiments in a department layer and forgetting to undo them. Fix: experiment in the session layer, which is never saved with the stage.

### 11. Exam traps

> [!TRAP] "Which approach lets several artists edit the same shot without conflicts?" The answer is separate layers with edit targets, not "lock the file" and not "use variants".

> [!TRAP] Muting a layer does not delete or edit it. A question may offer "mute the layer" as a way to *permanently* remove opinions; it is only a temporary, per-stage view.

### 12. Practice questions

1. Lighting must be able to adjust transforms authored by layout without layout republishing. Where should `shot_lighting.usda` go in the sublayer list?
2. Select two. Which actions remove a department's opinions from the composed view **without** changing any file on disk?
   A. `stage.MuteLayer(layer.identifier)`
   B. Deleting the layer's path from `subLayerPaths` and saving the root layer
   C. Opening the stage with a population mask that excludes nothing
   D. Authoring stronger opinions in the session layer that override them
   E. Calling `layer.Clear()` and `layer.Save()`
3. Why does each artist get their own layer instead of sharing a department layer?

**Answers**

1. Above (earlier in the list than) `shot_layout.usda`, so its opinions are stronger.
2. **A and D.** Muting is a per-stage view change. Session-layer opinions live in memory only. B and E change files; C masks nothing.
3. Two people saving one file at the same time lose work. One writer per layer avoids that.

### 13. Exam takeaways

> [!KEY]
> - One writer per layer; combine layers with sublayers in an agreed order.
> - Later departments are usually stronger; shared sequence layers are weakest.
> - Edit targets send authoring to the right layer; the session layer is for unsaved experiments.
> - `MuteLayer` isolates a layer's effect without editing files.

---

## 22.3 Preparing an asset for external delivery

### 1. What is it?

**Preparing an asset for delivery** turns a studio-internal asset into a self-contained package that works on someone else's computer. You remove links to internal servers and tools, collect every needed file into one place, and often bake composition into one file or one `.usdz`.

### 2. Why do we need it?

Internal assets point to places the client cannot reach: `/studio/library/rigs/…`, custom resolver URIs, in-house scripts. They may also carry private metadata such as artist names or project codes. Send them as-is and the client sees missing references, missing textures, and leaked information.

### 3. Beginner explanation

Think of sending a recipe to a friend. Your own recipe card says "use the sauce from the jar on shelf 3" and "see Grandma's notebook". Your friend has neither. Before sending, you either write the sauce recipe into the card (flatten) or put the jar and a copy of the notebook in the box with the card (localize/package), and you cross out your private notes.

Where the analogy breaks: flattening in USD is lossy in specific ways (variants not selected are dropped, arcs disappear), and packaging keeps structure but needs every file to be findable when you build the package.

### 4. Technical explanation

Four tools, each with a different result. All signatures below were checked on USD 26.08.

| Tool | Signature (Python) | Result | Keeps arcs/variants? |
|------|--------------------|--------|----------------------|
| `Usd.Stage.Flatten` | `stage.Flatten(addSourceFileComment=True)` → `Sdf.Layer` | One anonymous layer with the fully composed stage | No arcs, no unselected variants. Instancing kept via `Flattened_Prototype_N` prims |
| `UsdUtils.FlattenLayerStack` | `FlattenLayerStack(stage, tag="")` or `FlattenLayerStack(stage, resolveAssetPathFn, tag="")` → `Sdf.Layer` | Merges only the root **layer stack** (sublayers) into one layer | Yes: references, payloads, variants stay |
| `UsdUtils.LocalizeAsset` | `LocalizeAsset(assetPath, localizationDirectory, editLayersInPlace=False, processingFunc=None)` → `bool` | Copies the asset and all dependencies into a folder, rewriting paths | Yes, structure unchanged |
| `UsdUtils.CreateNewUsdzPackage` | `CreateNewUsdzPackage(assetPath, usdzFilePath, firstLayerName="", editLayersInPlace=False)` → `bool` | Same collection, written as one `.usdz` | Yes |

Facts to know:

- **Flatten anchors asset paths.** Both `Flatten` and `FlattenLayerStack` (without a callback) turn relative paths like `@./tex/wood.png@` into absolute paths on *your* disk. That leaks internal paths. Fix it with `FlattenLayerStack(stage, lambda layer, path: path)` (keep paths as authored) or by rewriting afterwards with `UsdUtils.ModifyAssetPaths(layer, fn)`.
- **Inventory first.** `UsdUtils.ComputeAllDependencies(Sdf.AssetPath(path))` returns `(layers, assets, unresolvedPaths)`. Unresolved paths are your list of internal dependencies.
- **Remove proprietary dependencies during localization.** `processingFunc(layer, dependencyInfo)` is called for every dependency. Return the `dependencyInfo` to keep it, or an empty `UsdUtils.DependencyInfo()` to remove it from the delivered layer (references are dropped, asset values cleared).
- **Unresolvable paths are not fatal by default.** Without a `processingFunc`, `LocalizeAsset` returns `False`, prints warnings, and still writes layers with remapped placeholders like `@0/publish.py@`. Always check the return value.
- **Private metadata** (`customData`, `assetInfo`, custom `studio:` attributes) is not removed by any of these tools. Clear it yourself, for example `prim.ClearCustomDataByKey("owner")` or `prim.RemoveProperty(...)` on the delivery copy.
- `usdzip` (command line) wraps `CreateNewUsdzPackage`; `usdcat --flatten` wraps `Flatten`. Neither tool ships with `usd-core`.

```{.bash .norun}
usdzip --asset chair.usda chair.usdz
usdcat --flatten shot.usda -o shot_flat.usda
```

These commands are not installed with `usd-core`; the Python example shows the same operations.

> [!VERSION] Verified on USD 26.08. `UsdUtils.LocalizeAsset` was added in 24.03; older material only shows `CreateNewUsdzPackage` and manual copying.

### 5. Mental model

```text
 internal asset --> inventory (ComputeAllDependencies)
                       |
                       +-- keep structure --> LocalizeAsset --> folder
                       |     (processingFunc drops /studio/ deps)   |
                       |                                            v
                       |                              CreateNewUsdzPackage
                       |
                       +-- bake ------------> Flatten (whole stage) or
                                              FlattenLayerStack (sublayers only)
                                              then fix absolute asset paths
 always: strip private metadata, re-open the result, check for errors
```

### 6. Simple example

`chair.usda` sublayers `chair_geo.usda` and `chair_mtl.usda`, uses texture `./tex/wood.png`, references a rig on `/studio/rigs/`, and has `customData = {owner = "jdoe"}`. Delivery: drop the rig reference, clear `owner`, copy the three layers and the texture into `delivery/`, and zip them as `chair.usdz`.

### 7. USDA example

*File: chair.usda* (internal version, before delivery)

```usda
#usda 1.0
(
    defaultPrim = "Chair"
    subLayers = [
        @./chair_mtl.usda@,
        @./chair_geo.usda@
    ]
)

def Xform "Chair" (
    customData = {
        string owner = "jdoe"
    }
    prepend references = @/studio/rigs/chair_rig.usda@
)
{
    asset studio:publishScript = @/studio/tools/publish.py@
}
```

Line notes: the `references` line and the `studio:publishScript` asset path point to internal servers; `customData.owner` is private. All three must not reach the client.

### 8. Python example

The first script inventories the asset, localizes it while dropping internal dependencies, strips private metadata, and packages it.

```python
import os
import zipfile
from pxr import Usd, Sdf, UsdUtils

os.makedirs("src/tex", exist_ok=True)
with open("src/tex/wood.png", "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n")                 # stand-in texture file
with open("src/chair_geo.usda", "w") as f:
    f.write('#usda 1.0\nover "Chair"\n{\n    def Cube "Seat"\n    {\n    }\n}\n')
with open("src/chair_mtl.usda", "w") as f:
    f.write('#usda 1.0\nover "Chair"\n{\n    def Shader "Tex"\n    {\n'
            '        asset inputs:file = @./tex/wood.png@\n    }\n}\n')
with open("src/chair.usda", "w") as f:
    f.write('''#usda 1.0
(
    defaultPrim = "Chair"
    subLayers = [@./chair_mtl.usda@, @./chair_geo.usda@]
)
def Xform "Chair" (
    customData = {string owner = "jdoe"}
    prepend references = @/studio/rigs/chair_rig.usda@
)
{
    asset studio:publishScript = @/studio/tools/publish.py@
}
''')

layers, assets, unresolved = UsdUtils.ComputeAllDependencies(
    Sdf.AssetPath("src/chair.usda"))
print("layers:", sorted(os.path.basename(l.realPath) for l in layers))
print("assets:", [os.path.relpath(a) for a in assets])
print("unresolved:", sorted(unresolved))


def drop_internal(layer, dep):
    if dep.assetPath.startswith("/studio/"):
        return UsdUtils.DependencyInfo()           # empty info = remove it
    return dep


ok = UsdUtils.LocalizeAsset(Sdf.AssetPath("src/chair.usda"), "delivery",
                            False, drop_internal)
print("localized:", ok)

stage = Usd.Stage.Open("delivery/chair.usda")
chair = stage.GetPrimAtPath("/Chair")
chair.ClearCustomDataByKey("owner")
chair.RemoveProperty("studio:publishScript")
stage.Save()
print(stage.GetRootLayer().ExportToString())

ok = UsdUtils.CreateNewUsdzPackage(Sdf.AssetPath("delivery/chair.usda"),
                                   "chair.usdz")
print("packaged:", ok, sorted(zipfile.ZipFile("chair.usdz").namelist()))
check = Usd.Stage.Open("chair.usdz")
print("errors:", len(check.GetCompositionErrors()),
      "texture:", check.GetPrimAtPath("/Chair/Tex").GetAttribute("inputs:file").Get())
```

**Expected output**

```text
layers: ['chair.usda', 'chair_geo.usda', 'chair_mtl.usda']
assets: ['src/tex/wood.png']
unresolved: ['/studio/rigs/chair_rig.usda', '/studio/tools/publish.py']
localized: True
#usda 1.0
(
    defaultPrim = "Chair"
    subLayers = [
        @./chair_mtl.usda@,
        @./chair_geo.usda@
    ]
)

def Xform "Chair"
{
}


packaged: True ['chair.usda', 'chair_geo.usda', 'chair_mtl.usda', 'tex/wood.png']
errors: 0 texture: @./tex/wood.png@
```

The internal reference is gone, the asset-valued attribute was removed, `customData` is empty, and the package opens with no composition errors. Warnings about the unresolvable `/studio/` paths go to standard error during `ComputeAllDependencies`; they are expected.

The second script compares the two flatten functions and shows the absolute-path leak and its fix.

```python
import os
from pxr import Usd, UsdUtils

with open("geo.usda", "w") as f:
    f.write('#usda 1.0\nover "Lamp"\n{\n    asset tex = @./tex/metal.png@\n}\n')
with open("lamp.usda", "w") as f:
    f.write('''#usda 1.0
(
    subLayers = [@./geo.usda@]
)
def Xform "Lamp" (
    variants = {string size = "big"}
    prepend variantSets = "size"
)
{
    variantSet "size" = {
        "big" {
            double height = 3
        }
        "small" {
            double height = 1
        }
    }
}
''')
here = os.getcwd()
stage = Usd.Stage.Open("lamp.usda")

flat = stage.Flatten(addSourceFileComment=False)
lamp = flat.GetPrimAtPath("/Lamp")
print("Flatten variant sets:", list(lamp.variantSets.keys()))
print("Flatten height:", lamp.attributes["height"].default)
print("Flatten tex:", lamp.attributes["tex"].default.path.replace(here, "<cwd>"))

stack = UsdUtils.FlattenLayerStack(stage)
lamp = stack.GetPrimAtPath("/Lamp")
print("FlattenLayerStack variant sets:", list(lamp.variantSets.keys()))
print("FlattenLayerStack tex:",
      lamp.attributes["tex"].default.path.replace(here, "<cwd>"))

kept = UsdUtils.FlattenLayerStack(stage, lambda layer, path: path)
print("with callback tex:", kept.GetPrimAtPath("/Lamp").attributes["tex"].default)

UsdUtils.ModifyAssetPaths(flat, lambda p: "./tex/" + os.path.basename(p))
print("after ModifyAssetPaths:", flat.GetPrimAtPath("/Lamp").attributes["tex"].default)
```

**Expected output**

```text
Flatten variant sets: []
Flatten height: 3.0
Flatten tex: <cwd>/tex/metal.png
FlattenLayerStack variant sets: ['size']
FlattenLayerStack tex: <cwd>/tex/metal.png
with callback tex: @./tex/metal.png@
after ModifyAssetPaths: @./tex/metal.png@
```

`Flatten` baked the selected variant (`height = 3`) and dropped the variant set. `FlattenLayerStack` kept the variant set. Both made the texture path absolute until a callback or `ModifyAssetPaths` fixed it.

### 9. Real-world use case

An automotive supplier sends a seat model to a car maker for a design review in a different tool. The supplier localizes the asset, drops references to its internal fastener library and in-house validation scripts, removes `customData` with engineer names, and delivers a `.usdz`. The car maker opens one file with no broken links. For an archival copy with no composition at all, the supplier also stores a flattened `.usdc`.

### 10. Common mistakes

> [!MISTAKE] Flattening and assuming paths are portable. `Flatten` writes absolute paths from your machine. Fix: rewrite with `UsdUtils.ModifyAssetPaths`, or use `FlattenLayerStack` with a callback that keeps authored paths.

> [!MISTAKE] Ignoring the `bool` returned by `LocalizeAsset` or `CreateNewUsdzPackage`. A `False` means some dependency could not be resolved and was written as a placeholder path. Fix: check the result and handle unresolved paths with a `processingFunc`.

> [!MISTAKE] Flattening an asset whose client needs to switch variants. `Flatten` keeps only the selected variant. Fix: use `FlattenLayerStack` or localization, which keep variant sets.

> [!MISTAKE] Forgetting metadata. None of the four tools removes `customData`, `assetInfo`, or custom attributes. Fix: strip them explicitly on the delivery copy.

### 11. Exam traps

> [!TRAP] `Usd.Stage.Flatten` vs `UsdUtils.FlattenLayerStack`: the first flattens *all* composition (references, variants, inherits); the second merges only the layer stack (sublayers) and keeps other arcs.

> [!TRAP] "Package the asset so it works offline" → localize or USDZ-package it. Flattening alone still leaves texture files outside the layer.

> [!TRAP] USDZ packages are zip archives that must be **uncompressed**; `CreateNewUsdzPackage` handles that. Do not answer "zip the folder with any zip tool" (Ch 31).

### 12. Practice questions

1. A client must be able to switch the `color` variant of a delivered asset, and the asset uses sublayers and textures. Which tool keeps the variant set while merging the sublayers into one layer?
   A. `Usd.Stage.Flatten`
   B. `UsdUtils.FlattenLayerStack`
   C. `Sdf.Layer.Export` of the root layer
   D. `Usd.Stage.Export` with `addSourceFileComment=False`
2. Select two. Which steps remove a reference to `/studio/rigs/chair_rig.usda` from a delivered asset?
   A. Return an empty `UsdUtils.DependencyInfo()` for it from `LocalizeAsset`'s `processingFunc`
   B. Call `UsdUtils.ComputeAllDependencies` on the asset
   C. Flatten the stage, which removes all arcs (and bakes the rig's opinions in if it resolved)
   D. Mute the layer that contains the reference
3. After `stage.Flatten()`, a texture attribute reads `@/home/artist/show/tex/wood.png@`. Why, and how do you fix it?

**Answers**

1. **B.** It merges sublayers but keeps references and variant sets. A bakes variants away. C exports only the root layer and leaves sublayers as links. D still contains every arc, not merged.
2. **A and C.** A removes the dependency during localization; C removes every arc. B only reports dependencies. D changes the view, not the delivered file.
3. Flattening anchors asset paths to absolute paths. Rewrite them with `UsdUtils.ModifyAssetPaths` (or use `FlattenLayerStack` with a callback that returns the authored path).

### 13. Exam takeaways

> [!KEY]
> - `Flatten` = whole stage, no arcs, selected variants only; `FlattenLayerStack` = sublayers only, arcs kept.
> - `LocalizeAsset(assetPath, dir, editLayersInPlace, processingFunc)` collects files; return an empty `DependencyInfo` to drop a dependency.
> - `CreateNewUsdzPackage(assetPath, usdzPath)` makes the single-file deliverable.
> - Flattening makes asset paths absolute; fix with `ModifyAssetPaths`. Strip private metadata yourself.

---

## 22.4 Removing properties from instanced component prims

### 1. What is it?

This is the task of hiding or removing an attribute, relationship, or child prim of a component that is **instanced** in an assembly, for example removing a tracking attribute from every chair in a room, or hiding one chair's cushion.

### 2. Why do we need it?

Instancing (Ch 24) shares one read-only **prototype** among many instances, which saves memory and load time. But the prims you see under an instance are **instance proxies**, and USD refuses edits on them. You need ways to change instanced content that respect that rule.

### 3. Beginner explanation

Instancing is a rubber stamp: one carved stamp, many prints. You cannot erase a line on one print and expect the stamp to change, and you cannot carve the stamp from the print. To change prints you either carve a different stamp (a new prototype through a variant or a different arc), change the stamp's design sheet that all stamps follow (a class all instances inherit), or draw that one picture by hand (turn off instancing for it).

Where the analogy breaks: USD carves new stamps automatically. Any two instances whose composition arcs differ get different prototypes; you never manage prototypes yourself.

### 4. Technical explanation

**What fails.** Every authoring call on an instance proxy or a prototype raises `Tf.ErrorException` ("authoring to an instance proxy is not allowed" / "authoring to an instancing prototype is not allowed"). And if you write an `over` below an instance root directly into a layer (with Sdf or by hand), composition **silently ignores** it: instances only take opinions from arcs on and above the instance root, not from local specs beneath it.

**What "remove" means.** Composition cannot delete a property that a weaker layer defines. You can:

- **Block** an attribute: an opinion of `None` (`attr.Block()`, or `= None` in USDA). The attribute still exists but has no value.
- **Block** a relationship's targets: `rel material:binding = None` leaves an empty target list.
- **Deactivate** a child prim: `active = false` hides it and all its descendants.
- **Truly remove** it only by editing the source asset layer (`Sdf.PrimSpec.RemoveProperty`), which changes every user of that asset.

**Where you may author.** The **instance root** (the prim with `instanceable = true`) is a normal prim. You can add arcs and metadata there. That gives four working approaches:

| Approach | Where you author | Affects | Prototypes |
|----------|------------------|---------|------------|
| A. Class edit | `class "_class_Chair"` in the assembly layer, for an asset that inherits it | All instances that inherit the class | Shared still |
| B. Variant | Variant selection on the instance root (asset provides e.g. `trim = bare`) | Instances with that selection | One per distinct selection |
| C. Extra arc on instance root | `prepend inherits = </_fix>` (or a reference) on chosen roots, plus a class `_fix` | Only those instances | One per distinct arc set |
| D. De-instance | `instanceable = false` on one instance, then edit its children normally | That one chair | It leaves instancing |
| E. Fix the source | Edit the component asset itself | Every user everywhere | Shared still |

Prefer A, B, or C. D costs memory if done widely. E is right only when the property should never have been there.

**Choosing an instancing style (Obj 1.2, brief).** No instancing for unique hero assets; **scenegraph instancing** (`instanceable = true`) for tens to thousands of repeated components that need their own prim paths, variants, and per-instance overrides on the root; **point instancing** (`UsdGeom.PointInstancer`, Ch 25) for thousands to millions of copies (rocks, trees, bolts) where per-copy edits are limited to position, orientation, scale, and hiding. Chapter 26 gives the full decision table.

### 5. Mental model

```text
 /Room/Chair_1  (instanceable = true)   <- editable: arcs, metadata, variant selection
   |-- Seat     (instance proxy)         <- read-only: Usd edit raises an error,
   |-- Cushion  (instance proxy)            layer overs here are ignored
         ^
         |  comes from the prototype  /__Prototype_1  (read-only)

 change instanced content = change the ARCS on the root
   (class it inherits, variant it selects, extra inherit) -> USD picks the prototype
```

### 6. Simple example

A room has three instanced chairs. Every chair carries `studio:trackingId`, which the client must not see. Chair 3 must also lose its cushion. Plan: block `studio:trackingId` in the room's `_class_Chair` (all chairs), and select the asset's `trim = bare` variant on Chair 3 only.

### 7. USDA example

*File: room.usda* (assembly; `chair.usda` inherits `</_class_Chair>` and has a `trim` variant set)

```usda
#usda 1.0
(
    defaultPrim = "Room"
)

def Xform "Room" (
    kind = "assembly"
)
{
    def "Chair_1" (
        instanceable = true
        prepend references = @./chair.usda@
    )
    {
    }

    def "Chair_3" (
        instanceable = true
        prepend references = @./chair.usda@
        variants = {
            string trim = "bare"
        }
    )
    {
    }
}

class "_class_Chair"
{
    over "Seat"
    {
        custom string studio:trackingId = None
    }
}
```

Line notes: the class `_class_Chair` in the assembly layer is stronger than the asset's own opinions (inherits beat references in LIVERPS) and reaches every chair through the inherit arc the asset already authors. `= None` is a value block. `Chair_3`'s variant selection is authored on the instance root, which is allowed.

### 8. Python example

```python
from pxr import Usd, Sdf, Tf

with open("chair.usda", "w") as f:
    f.write('''#usda 1.0
(
    defaultPrim = "Chair"
)
def Xform "Chair" (
    inherits = </_class_Chair>
    variants = {string trim = "full"}
    prepend variantSets = "trim"
)
{
    def Mesh "Seat"
    {
        custom string studio:trackingId = "XYZ-123"
    }
    def Mesh "Cushion"
    {
    }
    variantSet "trim" = {
        "bare" {
            over "Cushion" (active = false)
            {
            }
        }
        "full" {
        }
    }
}
class "_class_Chair"
{
}
''')
with open("room.usda", "w") as f:
    f.write('#usda 1.0\ndef Xform "Room"\n{\n' + "".join(
        f'    def "Chair_{i}" (instanceable = true\n'
        f'        prepend references = @./chair.usda@)\n    {{\n    }}\n'
        for i in (1, 2, 3)) + "}\n")

stage = Usd.Stage.Open("room.usda")
proxy_attr = stage.GetPrimAtPath("/Room/Chair_1/Seat").GetAttribute(
    "studio:trackingId")
try:
    proxy_attr.Block()
except Tf.ErrorException:
    print("edit on instance proxy: refused")

# A. Class edit: all chairs, prototypes stay shared.
over_seat = stage.OverridePrim("/_class_Chair/Seat")
over_seat.CreateAttribute("studio:trackingId",
                          Sdf.ValueTypeNames.String, custom=True).Block()
print("prototypes after class edit:", len(stage.GetPrototypes()))

# B. Variant on one instance root.
stage.GetPrimAtPath("/Room/Chair_3").GetVariantSet("trim").SetVariantSelection("bare")
print("prototypes after variant:", len(stage.GetPrototypes()))

# D. De-instance one chair, then edit it directly.
stage.GetPrimAtPath("/Room/Chair_2").SetInstanceable(False)
stage.GetPrimAtPath("/Room/Chair_2/Cushion").SetActive(False)

for i in (1, 2, 3):
    root = stage.GetPrimAtPath(f"/Room/Chair_{i}")
    attr = stage.GetPrimAtPath(f"/Room/Chair_{i}/Seat").GetAttribute(
        "studio:trackingId")
    cushion = stage.GetPrimAtPath(f"/Room/Chair_{i}/Cushion")
    print(f"Chair_{i}", "instance" if root.IsInstance() else "plain",
          "| trackingId exists:", attr.IsValid(), "value:", attr.Get(),
          "| cushion active:", cushion.IsActive())
print("prototypes at end:", len(stage.GetPrototypes()))
```

**Expected output**

```text
edit on instance proxy: refused
prototypes after class edit: 1
prototypes after variant: 2
Chair_1 instance | trackingId exists: True value: None | cushion active: True
Chair_2 plain | trackingId exists: True value: None | cushion active: False
Chair_3 instance | trackingId exists: True value: None | cushion active: False
prototypes at end: 2
```

Notice three things. The proxy edit raised an error. The class edit reached every chair and kept one prototype. The blocked attribute still *exists*; it just has no value. That is what "remove" means in composition.

### 9. Real-world use case

An architecture firm's office assembly contains 400 instanced desks. The desk asset carries `studio:costCode` attributes that must not leave the firm, and the client wants the monitor hidden on desks in the meeting rooms. The firm blocks `studio:costCode` in the assembly's `_class_Desk` (one edit, all desks, one prototype) and selects `monitor = none` on the 20 meeting-room desks (a second prototype). Memory stays close to two desks' worth.

### 10. Common mistakes

> [!MISTAKE] Calling `SetActive(False)` or `Block()` on `/Room/Chair_1/Seat` and expecting it to work. It raises `Tf.ErrorException`. Fix: author on the instance root (variant, inherits) or in a class.

> [!MISTAKE] Writing `over "Seat" { ... }` under an instanceable prim in the assembly layer by hand. It parses fine but composition ignores it, with no warning. Fix: move the opinion into a class or variant.

> [!MISTAKE] Turning `instanceable` off for hundreds of instances to make edits. Memory and load time grow with every de-instanced copy. Fix: use variants or class edits so instances keep sharing a few prototypes.

### 11. Exam traps

> [!TRAP] "Edit the prototype returned by `GetPrototype()`" is never correct; prototypes are read-only.

> [!TRAP] A value block (`= None`) does not delete the property. `GetAttribute(...).IsValid()` stays `True`; `Get()` returns `None`.

> [!TRAP] Look-alike answer: "Set `instanceable = false` on the prototype". Instanceable is authored on instance roots, never on prototypes.

### 12. Practice questions

1. You must hide the `Cushion` child on 50 of 300 instanced chairs and keep memory low. Which approach is best?
   A. Call `SetActive(False)` on each `/Room/Chair_N/Cushion`
   B. Select a variant that deactivates `Cushion` on those 50 instance roots
   C. Set `instanceable = false` on all 300 chairs and deactivate the cushions
   D. Edit the prototype returned by `GetPrototype()`
2. In the assembly layer you add `over "Seat" { float roughness = 0.2 }` under the instanceable `Chair_1`. What does `Chair_1/Seat.roughness` show?
3. Select two. Which statements about blocking `studio:trackingId` are true?
   A. The attribute no longer appears in the prim's property names
   B. `attr.Get()` returns `None`
   C. `attr.GetResolveInfo().ValueIsBlocked()` returns `True`
   D. The block deletes the attribute from the asset file

**Answers**

1. **B.** One variant selection creates one extra prototype for the 50 chairs. A raises errors; C destroys the memory benefit; D is not allowed.
2. The asset's value (or no value). Opinions authored below an instance root in the referencing layer are ignored by composition, silently.
3. **B and C.** A block hides the value but the property spec still exists (A false); the asset file is untouched (D false).

### 13. Exam takeaways

> [!KEY]
> - Instance proxies and prototypes are read-only: `Usd` edits raise errors; layer overs under the instance root are ignored.
> - Edit instanced content by changing arcs on the instance root or a class it inherits; USD regroups prototypes automatically.
> - "Remove" = block (`None`) an attribute or relationship, or deactivate a child prim.
> - Scenegraph instancing for repeated components; point instancing for massive counts (Ch 24–26).

---

## 22.5 Debugging composition

### 1. What is it?

**Debugging composition** means asking USD *where* a prim or value comes from: which layers, which arcs, which variant. USD has introspection APIs that answer each of those questions directly.

### 2. Why do we need it?

A composed stage hides its sources. A value of `2.0` on screen could come from the root layer, a sublayer, a variant inside a reference, or a class. Guessing wastes hours. The introspection APIs show the exact path in seconds.

### 3. Beginner explanation

Value resolution is a ladder of opinions where the strongest rung answers (Ch 21). Debugging tools let you look at the whole ladder: who stands on every rung (prim stack and property stack), who answered (resolve info), and how the ladder was built (composition query and prim index).

Where the analogy breaks: the "ladder" is really a tree of arcs (the prim index). The rungs you see in a stack are that tree flattened in strength order.

### 4. Technical explanation

| Question | API (verified on 26.08) | Returns |
|----------|-------------------------|---------|
| Which specs make this prim? | `prim.GetPrimStack()` | `[Sdf.PrimSpec]`, strongest first; each has `.layer` and `.path` |
| ...with time offsets? | `prim.GetPrimStackWithLayerOffsets()` | `[(Sdf.PrimSpec, Sdf.LayerOffset)]` |
| Which specs set this attribute? | `attr.GetPropertyStack(time=Usd.TimeCode.Default())` | `[Sdf.PropertySpec]`, strongest first |
| Where does the value come from? | `attr.GetResolveInfo(time)` | `Usd.ResolveInfo`: `GetSource()`, `GetNode()`, `ValueIsBlocked()`, `HasAuthoredValue()` |
| Which arcs build this prim? | `Usd.PrimCompositionQuery(prim).GetCompositionArcs()` | `[Usd.CompositionArc]` |
| Full composition tree | `prim.GetPrimIndex().DumpToString()` | Text listing every node |
| What failed to compose? | `stage.GetCompositionErrors()` | `[Pcp error]`, each with `errorType`, `rootSite`, `str()` |

Details:

- `ResolveInfo.GetSource()` is one of `Usd.ResolveInfoSourceNone`, `Fallback`, `Default`, `TimeSamples`, `ValueClips`, `Spline`. `GetNode()` returns the `Pcp.NodeRef` (arc) that won; `node.arcType`, `node.path`, and `node.layerStack` describe it. There is **no layer accessor** on `ResolveInfo`; for the winning layer use `attr.GetPropertyStack()[0].layer`.
- `Usd.CompositionArc` methods: `GetArcType()` (a `Pcp.ArcType`), `GetTargetNode()`, `GetTargetPrimPath()`, `GetTargetLayer()`, `GetIntroducingLayer()`, `GetIntroducingPrimPath()`, `IsImplicit()`, `IsAncestral()`, `HasSpecs()`. The root arc has no introducing layer (`None`).
- Filter the query with `Usd.PrimCompositionQuery.Filter()`; set `filter.arcTypeFilter = Usd.PrimCompositionQuery.ArcTypeFilter.Reference` (also `Inherit`, `Variant`, `Payload`, `Specialize`, `Relocate`, and combinations). `Usd.PrimCompositionQuery.GetDirectReferences(prim)` is a ready-made query.
- `GetCompositionErrors()` exists on `Usd.Stage` and lists errors such as `Pcp.ErrorType_InvalidAssetPath` (missing file) or `ErrorType_ArcCycle`. Errors are also printed as warnings when the stage opens.
- In usdview, the **Layer Stack** and **Composition** tabs show the same data. usdview is not part of `usd-core` (Ch 42).

### 5. Mental model

```text
 Is the prim there?            stage.GetPrimAtPath(p)  -> valid? active? defined?
 Which files touch it?         prim.GetPrimStack()
 Which arcs bring them?        Usd.PrimCompositionQuery(prim).GetCompositionArcs()
 Which spec sets the value?    attr.GetPropertyStack()[0]
 What kind of value won?       attr.GetResolveInfo().GetSource()
 Anything broken?              stage.GetCompositionErrors()
 Show me everything            prim.GetPrimIndex().DumpToString()
```

Work top to bottom: existence, sources, arcs, winner, errors.

### 6. Simple example

`/World/Lamp_1` reads `height = 2.0`, but the lamp asset's `small` variant says `0.5`. The property stack shows three specs: `lighting.usda` (2.0), `lamp.usda /Lamp` (1.0), `lamp.usda /Lamp{size=small}` (0.5). The first one wins: the lighting sublayer of the shot overrides the asset.

### 7. USDA example

*File: shot.usda*

```usda
#usda 1.0
(
    subLayers = [
        @./lighting.usda@
    ]
)

def "World"
{
    def "Lamp_1" (
        prepend references = [@./lamp.usda@, @./missing.usda@]
    )
    {
    }
}
```

*File: lighting.usda*

```usda
#usda 1.0

over "World"
{
    over "Lamp_1"
    {
        double height = 2
    }
}
```

Line notes: `Lamp_1` has two references; `missing.usda` does not exist, which will show up as a composition error. `lighting.usda` is a sublayer of the shot, so it is part of the root layer stack.

### 8. Python example

```python
import os
import re
from pxr import Usd

files = {
    "lamp.usda": '''#usda 1.0
(
    defaultPrim = "Lamp"
)
def Xform "Lamp" (
    variants = {string size = "small"}
    prepend variantSets = "size"
)
{
    double height = 1
    variantSet "size" = {
        "big" {
            double height = 3
        }
        "small" {
            double height = 0.5
        }
    }
}
''',
    "lighting.usda": '#usda 1.0\nover "World"\n{\n    over "Lamp_1"\n    {\n'
                     '        double height = 2\n    }\n}\n',
    "shot.usda": '''#usda 1.0
(
    subLayers = [@./lighting.usda@]
)
def "World"
{
    def "Lamp_1" (
        prepend references = [@./lamp.usda@, @./missing.usda@]
    )
    {
    }
}
''',
}
for name, text in files.items():
    with open(name, "w") as f:
        f.write(text)


def short(text):
    text = text.replace(os.getcwd() + "/", "")
    return re.sub(r"anon:0x[0-9a-f]+:", "anon:", text)


stage = Usd.Stage.Open("shot.usda")
prim = stage.GetPrimAtPath("/World/Lamp_1")
attr = prim.GetAttribute("height")

print("value:", attr.Get())
print("prim stack:")
for spec in prim.GetPrimStack():
    print("  ", spec.layer.GetDisplayName(), spec.path)
print("property stack:")
for spec in attr.GetPropertyStack():
    print("  ", spec.layer.GetDisplayName(), spec.path, spec.default)

info = attr.GetResolveInfo()
print("resolve:", info.GetSource(), info.GetNode().arcType, info.GetNode().path)
print("winning layer:", attr.GetPropertyStack()[0].layer.GetDisplayName())

print("arcs:")
for arc in Usd.PrimCompositionQuery(prim).GetCompositionArcs():
    intro = arc.GetIntroducingLayer()
    print("  ", arc.GetArcType(), arc.GetTargetNode().path,
          "introduced in", intro.GetDisplayName() if intro else None)

print("errors:")
for err in stage.GetCompositionErrors():
    print("  ", err.errorType)
    print("  ", short(str(err)).strip().replace(" for ", "\n    for "))

print("prim index (excerpt):")
for line in prim.GetPrimIndex().DumpToString().splitlines():
    if line.startswith("Node") or "Type:" in line[:10] or "Source path" in line:
        print("  ", short(line).strip())
```

**Expected output**

```text
value: 2.0
prim stack:
   shot.usda /World/Lamp_1
   lighting.usda /World/Lamp_1
   lamp.usda /Lamp
   lamp.usda /Lamp{size=small}
property stack:
   lighting.usda /World/Lamp_1.height 2.0
   lamp.usda /Lamp.height 1.0
   lamp.usda /Lamp{size=small}.height 0.5
resolve: Usd.ResolveInfoSourceDefault Pcp.ArcTypeRoot /World/Lamp_1
winning layer: lighting.usda
arcs:
   Pcp.ArcTypeRoot /World/Lamp_1 introduced in None
   Pcp.ArcTypeReference /Lamp introduced in shot.usda
   Pcp.ArcTypeVariant /Lamp{size=small} introduced in lamp.usda
errors:
   Pcp.ErrorType_InvalidAssetPath
   Could not open asset @missing.usda@
    for reference introduced by @shot.usda@</World/Lamp_1>.
prim index (excerpt):
   Node 0:
   Type:                     root
   Source path:              </World/Lamp_1>
   Node 1:
   Type:                     reference
   Source path:              </Lamp>
   Node 2:
   Type:                     variant
   Source path:              </Lamp{size=small}>
```

Reading it: the winning node is the **root** node (the shot's own layer stack, which includes `lighting.usda`), so local beats the reference and its variant. The missing file appears both as a warning on open and in `GetCompositionErrors()`. Notice that the property stack lists the variant's `0.5` last, even though variants are stronger than references in LIVERPS: the variant lives *inside* the reference, so it is only stronger than other opinions within that referenced asset.

### 9. Real-world use case

A robotics team's simulation shows a gripper at the wrong scale. Instead of opening a dozen files, the engineer runs a small script that prints `GetPropertyStack()` for `xformOp:scale`. It shows a stale override in `cell_layout_v3.usda`, a layer someone forgot to remove from the sublayer list. The fix takes a minute.

### 10. Common mistakes

> [!MISTAKE] Reading `GetResolveInfo().GetNode().layerStack` and taking its root layer as "the layer that won". The node is an arc; its layer stack may hold many sublayers. Fix: use `attr.GetPropertyStack()[0].layer` for the winning layer.

> [!MISTAKE] Looking only at the root layer with `Sdf` (the authored view) to find a value. The value may come from a sublayer or arc. Fix: use the `Usd` stack APIs, which see the composed result.

> [!MISTAKE] Ignoring warnings at stage open. They are composition errors. Fix: call `stage.GetCompositionErrors()` in tests and pipelines and fail on unexpected errors.

### 11. Exam traps

> [!TRAP] `GetPropertyStack` is on `Usd.Property` (attributes and relationships); `GetPrimStack` is on `Usd.Prim`. Do not mix them up.

> [!TRAP] Stacks are ordered **strongest first**. A question may show a stack and ask which value wins: the first entry with a value, unless it is a block.

> [!TRAP] `GetIntroducingLayer()` is the layer where the arc is *written*; `GetTargetLayer()` is the layer the arc *points to*. For a reference authored in `shot.usda` to `lamp.usda`, they are `shot.usda` and `lamp.usda`.

### 12. Practice questions

1. Which call tells you whether an attribute's value comes from time samples or a default?
   A. `attr.GetPropertyStack()`
   B. `attr.GetResolveInfo().GetSource()`
   C. `prim.GetPrimStack()`
   D. `stage.GetCompositionErrors()`
2. Select two. Which calls show arcs that bring opinions into a prim?
   A. `Usd.PrimCompositionQuery(prim).GetCompositionArcs()`
   B. `prim.GetPrimIndex().DumpToString()`
   C. `attr.Get()`
   D. `stage.GetLayerStack()`
3. `attr.GetPropertyStack()` returns specs from `fx.usda`, `layout.usda`, and `asset.usda` in that order, and all three have defaults. Which one provides `attr.Get()`?

**Answers**

1. **B.** The source enum names the kind of value. A lists specs but not which kind of value won.
2. **A and B.** The query returns arcs; the dump prints every node (arc) of the prim index. D lists only the root layer stack, not arcs.
3. `fx.usda`, the strongest (first) spec with a value.

### 13. Exam takeaways

> [!KEY]
> - `GetPrimStack` (prim) and `GetPropertyStack` (property) are strongest first.
> - `GetResolveInfo` gives the source kind and winning node; the winning layer is `GetPropertyStack()[0].layer`.
> - `Usd.PrimCompositionQuery(...).GetCompositionArcs()` → `GetArcType()`, `GetTargetNode()`, `GetIntroducingLayer()`.
> - `GetPrimIndex().DumpToString()` shows the whole arc tree; `stage.GetCompositionErrors()` lists failures.

---

## 22.6 Why an opinion does not take effect: checklist

### 1. What is it?

A ten-point checklist for the most common debugging question in USD: "I authored an opinion, but the composed stage does not show it." Each point is a real cause with a quick test.

### 2. Why do we need it?

The causes look the same from outside: the value is just "wrong". Working through a fixed list, with the tools from §22.5, finds the cause quickly and stops you from "fixing" the wrong layer.

### 3. Beginner explanation

When a letter does not arrive, you check a list: right address? posted at all? did someone at the same address throw it away? is the house even occupied? The checklist below does the same for an opinion: right layer? strong enough? right path? is the prim active? is it inside an instance?

Where the analogy breaks: in USD, nothing is lost. Every opinion is still in its layer; it just loses the strength contest or is not reachable. That is why stack tools always find it.

### 4. Technical explanation

| # | Cause | Quick test | Fix |
|---|-------|-----------|-----|
| 1 | **Wrong edit target / layer**: the edit went to the session layer or another layer that was not saved | `stage.GetEditTarget().GetLayer()`; after reopening, value is gone | Set the edit target to the intended layer, save that layer |
| 2 | **Weaker arc**: your opinion is in a reference/payload/specializes, but a stronger arc (local, inherits, variant) sets it | `GetPropertyStack()` shows a stronger spec first | Author in the stronger site or remove the stronger opinion |
| 3 | **Stronger local opinion**: a stronger sublayer in the same layer stack sets it | First spec in `GetPropertyStack()` is from another sublayer | Author in that layer, or reorder sublayers |
| 4 | **Variant selection in a stronger layer**: your layer selects `big`, a stronger one selects `small` | `prim.GetVariantSets().GetVariantSelection(name)` and the prim stack | Set the selection in the strongest needed layer |
| 5 | **Typo in path or name**: `over "Wrold"` creates a separate, undefined prim; a misspelled attribute is a new attribute | `stage.TraverseAll()` shows stray `over` prims; `GetPropertyNames()` | Correct the path or name |
| 6 | **Over on an inactive prim**: a stronger layer set `active = false` | `prim.IsActive()`; children return invalid prims | Re-activate in a stronger layer, or author elsewhere |
| 7 | **Inside an instance**: overs below an instance root are ignored; `Usd` edits there raise errors | `prim.IsInstanceProxy()` | Use a class, variant, or extra arc on the instance root (§22.4) |
| 8 | **Muted layer** | `stage.GetMutedLayers()`, `stage.IsLayerMuted(id)` | Unmute |
| 9 | **Time samples vs default**: you set the default but time samples in the same layer win at every time code; or a stronger layer's default hides weaker samples | `GetResolveInfo(t).GetSource()` | Set time samples, or clear them (`attr.Clear()`) |
| 10 | **Layer offset**: your samples are shifted by a sublayer or reference offset | `prim.GetPrimStackWithLayerOffsets()` | Author in the offset's time frame, or adjust the offset |

Other causes worth one line each: the opinion lives in an **unloaded payload** (`stage.Load(path)`); a **value block** (`None`) in a stronger layer; the file **failed to load** (check `GetCompositionErrors()`); a **value clip** supplies the value at that time (Ch 21).

### 5. Mental model

```text
 1 Is my edit in the file I think?      (edit target, saved?)
 2 Is the prim there and live?          (typo? active? loaded? instance proxy?)
 3 Is my layer in play?                 (muted? in the sublayer list? arc resolved?)
 4 Does my opinion win?                 (GetPropertyStack: who is above me?
                                         stronger sublayer, stronger arc, variant)
 5 Is it the right kind of value?       (default vs time samples, layer offset)
```

Location → existence → participation → strength → time.

### 6. Simple example

You set `radius = 5` on `/World/Ball` in `shot_anim.usda`, but the viewport shows `2`. `GetPropertyStack()` lists `shot_lighting.usda` first with `2`. Cause 3: a stronger sublayer. Talk to lighting, or author the change in their layer.

### 7. USDA example

*File: shot.usda* (three causes hiding in one file; Exercise 22-A at the end of this chapter uses it)

```usda
#usda 1.0
(
    subLayers = [
        @./anim.usda@
    ]
)

def "World"
{
    def Sphere "Ball" (
        active = false
    )
    {
        double radius = 2
    }

    def Sphere "Moon"
    {
        double radius.timeSamples = {
            1: 1,
            24: 4,
        }
        double radius = 9
    }
}

over "Wrold"
{
    over "Ball"
    {
        double radius = 5
    }
}
```

Line notes: `Ball` is inactive, so any `over` on it in `anim.usda` cannot show. `Moon` has both time samples and a default in the same layer; queries at a time code return the samples, not `9`. `over "Wrold"` is a typo: it creates a separate undefined prim that `Traverse()` does not visit.

### 8. Python example

Each block of the script reproduces one cause and prints the authored value next to the composed one.

```python
from pxr import Usd, Sdf


def stage_with(*names):
    stage = Usd.Stage.CreateInMemory()
    subs = [Sdf.Layer.CreateAnonymous(n) for n in names]
    stage.GetRootLayer().subLayerPaths = [l.identifier for l in subs]
    return stage, subs


def ball(stage, value=2.0):
    attr = stage.DefinePrim("/World/Ball").CreateAttribute(
        "radius", Sdf.ValueTypeNames.Double)
    attr.Set(value)
    return attr


# 1. Wrong edit target: the edit lands in the session layer, which is not saved.
s = Usd.Stage.CreateNew("shot.usda")
a = ball(s)
s.SetEditTarget(Usd.EditTarget(s.GetSessionLayer()))
a.Set(5.0)
s.Save()
reopened = Sdf.Layer.FindOrOpen("shot.usda")
print("1 saved file has:", reopened.GetAttributeAtPath("/World/Ball.radius").default)

# 2. Weaker arc: edit the referenced prim, but the referencing prim is stronger.
s = Usd.Stage.CreateInMemory()
lib = s.DefinePrim("/Lib/Ball")
lib.CreateAttribute("radius", Sdf.ValueTypeNames.Double).Set(1.0)
b = s.DefinePrim("/World/Ball")
b.GetReferences().AddInternalReference("/Lib/Ball")
b.GetAttribute("radius").Set(2.0)
lib.GetAttribute("radius").Set(5.0)
print("2 authored 5 in reference, composed:", b.GetAttribute("radius").Get())

# 3. Stronger local opinion: I author in the weaker sublayer.
s, (strong, weak) = stage_with("strong", "weak")
s.SetEditTarget(Usd.EditTarget(strong))
a = ball(s, 2.0)
s.SetEditTarget(Usd.EditTarget(weak))
a.Set(5.0)
print("3 authored 5 in weak sublayer, composed:", a.Get())

# 4. Variant selection in a stronger layer.
s, (strong, weak) = stage_with("strong", "weak")
p = s.DefinePrim("/World/Lamp")
vset = p.GetVariantSets().AddVariantSet("size")
for name in ("big", "small"):
    vset.AddVariant(name)
s.SetEditTarget(Usd.EditTarget(weak))
vset.SetVariantSelection("big")
s.SetEditTarget(Usd.EditTarget(strong))
vset.SetVariantSelection("small")
print("4 selected big in weak layer, composed:", vset.GetVariantSelection())

# 5. Typo in the path: a separate, undefined prim.
s = Usd.Stage.CreateInMemory()
a = ball(s)
s.OverridePrim("/Wrold/Ball").CreateAttribute(
    "radius", Sdf.ValueTypeNames.Double).Set(5.0)
print("5 typo, composed:", a.Get(),
      "| Traverse:", [str(x.GetPath()) for x in s.Traverse()])

# 6. Over on an inactive prim.
s, (strong, weak) = stage_with("strong", "weak")
s.SetEditTarget(Usd.EditTarget(weak))
s.DefinePrim("/World/Ball/Light").CreateAttribute(
    "intensity", Sdf.ValueTypeNames.Float).Set(5.0)
s.SetEditTarget(Usd.EditTarget(strong))
s.GetPrimAtPath("/World/Ball").SetActive(False)
print("6 child of inactive prim valid:", bool(s.GetPrimAtPath("/World/Ball/Light")))

# 7. Inside an instance: an over below the instance root is ignored.
s = Usd.Stage.CreateInMemory()
s.DefinePrim("/Lib/Chair/Seat").CreateAttribute(
    "h", Sdf.ValueTypeNames.Double).Set(1.0)
c = s.DefinePrim("/World/Chair")
c.GetReferences().AddInternalReference("/Lib/Chair")
c.SetInstanceable(True)
layer = s.GetRootLayer()
seat = Sdf.CreatePrimInLayer(layer, "/World/Chair/Seat")
Sdf.AttributeSpec(seat, "h", Sdf.ValueTypeNames.Double).default = 5.0
print("7 authored 5 under instance, composed:",
      s.GetPrimAtPath("/World/Chair/Seat").GetAttribute("h").Get())

# 8. Muted layer.
s, (anim,) = stage_with("anim")
s.SetEditTarget(Usd.EditTarget(anim))
a = ball(s, 5.0)
s.MuteLayer(anim.identifier)
print("8 authored 5 in muted layer, attribute valid:", a.IsValid())

# 9. Time samples beat the default in the same layer.
s = Usd.Stage.CreateInMemory()
a = ball(s, 9.0)
a.Set(1.0, 1)
a.Set(4.0, 24)
print("9 default 9, at frame 12:", a.Get(12), a.GetResolveInfo(12).GetSource())

# 10. Layer offset shifts my samples.
s, (anim,) = stage_with("anim")
s.GetRootLayer().subLayerOffsets[0] = Sdf.LayerOffset(100)
s.DefinePrim("/World/Ball")
anim_ball = Sdf.CreatePrimInLayer(anim, "/World/Ball")
spec = Sdf.AttributeSpec(anim_ball, "radius", Sdf.ValueTypeNames.Double)
anim.SetTimeSample(spec.path, 10, 5.0)
anim.SetTimeSample(spec.path, 20, 6.0)
a = s.GetPrimAtPath("/World/Ball").GetAttribute("radius")
print("10 authored at frame 10, samples on stage:", a.GetTimeSamples())
```

**Expected output**

```text
1 saved file has: 2.0
2 authored 5 in reference, composed: 2.0
3 authored 5 in weak sublayer, composed: 2.0
4 selected big in weak layer, composed: small
5 typo, composed: 2.0 | Traverse: ['/World', '/World/Ball']
6 child of inactive prim valid: False
7 authored 5 under instance, composed: 1.0
8 authored 5 in muted layer, attribute valid: False
9 default 9, at frame 12: 2.4347826086956523 Usd.ResolveInfoSourceTimeSamples
10 authored at frame 10, samples on stage: [110.0, 120.0]
```

Cause 7 is the sneakiest: no error, no warning, just an ignored opinion. Cause 8 removes the attribute entirely because the muted layer was the only place it was defined.

> [!VERSION] Verified on USD 26.08: overs authored below an instance root are ignored without a warning, and `Usd` authoring on instance proxies raises `Tf.ErrorException`.

### 9. Real-world use case

A VFX facility adds this checklist to its "my change doesn't show" help page and wraps causes 1, 5, 6, 7, 8, and 10 in an automatic script. An artist pastes a prim path and attribute name; the script prints the edit target, prim validity, active state, instance-proxy state, muted layers, the property stack with layer offsets, and the resolve source. Most tickets close without a technical director.

### 10. Common mistakes

> [!MISTAKE] "Fixing" a value by authoring it in the root layer every time. It works, but it hides the real cause and creates overrides nobody can find later. Fix: find the cause with the checklist, then author in the layer that should own the value.

> [!MISTAKE] Setting `attr.Set(value)` (default) on an animated attribute and expecting the animation to change. Fix: set time samples, or clear them with `attr.Clear()` if you want a static value.

> [!MISTAKE] Typing paths by hand in USDA overs. Fix: copy paths from the stage (`prim.GetPath()`), and check `stage.TraverseAll()` for stray `over` prims.

### 11. Exam traps

> [!TRAP] "The layer is sublayered, so its opinion must win" ignores order: the first sublayer is strongest, and the root layer beats all sublayers.

> [!TRAP] A stronger layer's *default* beats a weaker layer's *time samples* at every time code. Time samples only beat defaults within the same layer. Verified on USD 26.08.

> [!TRAP] A variant selection is itself an opinion with strength. "The variant was authored, so it applies" is wrong if a stronger layer selects another variant.

> [!TRAP] Inactive is not the same as invisible. `visibility = invisible` keeps the prim composed and editable; `active = false` removes it and its children from the stage.

### 12. Practice questions

1. An animator's `xformOp:translate` samples in `anim.usda` do not show. `GetPropertyStack()` lists `layout.usda` first, with only a default value, then `anim.usda` with time samples. What is the cause?
   A. Time samples always lose to defaults in any layer
   B. `layout.usda` is a stronger layer, and a stronger default beats weaker time samples
   C. `anim.usda` is muted
   D. The prim is an instance proxy
2. Select two. Which causes produce **no** error or warning at all?
   A. An `over` authored below an instance root in a layer
   B. `Usd` authoring on an instance proxy
   C. A stronger sublayer setting the same attribute
   D. A reference to a file that does not exist
3. Samples at frames 10 and 20 in a sublayer appear on the stage at frames 110 and 120. Which checklist item explains it, and which API shows it?

**Answers**

1. **B.** Across layers, the strongest layer with any value opinion wins; its default hides the weaker samples. A is false (within a layer, samples win); nothing indicates C or D.
2. **A and C.** Both are normal composition. B raises `Tf.ErrorException`; D reports a composition error.
3. Cause 10, a layer offset (here `offset = 100` on the sublayer). `prim.GetPrimStackWithLayerOffsets()` shows it, as does `root.subLayerOffsets`.

### 13. Exam takeaways

> [!KEY]
> - Check in order: location (edit target, saved), existence (typo, active, loaded, instance), participation (muted, resolved), strength (property stack), time (samples, offsets).
> - Overs below an instance root are ignored silently; `Usd` edits on proxies raise errors.
> - Stronger default beats weaker samples; within one layer, samples beat the default.
> - Variant selections and `active` are opinions too, with normal strength rules.

---

## Chapter lab(s)

**Lab 21 — Composition introspection toolkit** (Ch 22, 42; Obj 1.8, 6.2). You build a small shot with sublayers, references, a variant, and a class, then write a reusable `explain(prim_path, attr_name)` function that prints the prim stack, property stack with layer offsets, resolve source, composition arcs, muted layers, and composition errors. You finish by breaking the shot in five checklist ways and letting your tool diagnose each one.

Related: **Lab 28 — Dependencies, flattening, and USDZ packaging** (Obj 1.9) and **Lab 23 — Native instancing and instance proxies** (Obj 2.2, 2.5) practise §22.3 and §22.4 in depth.

## USDA reading exercises

**Exercise 22-A.** Using the `shot.usda` from §22.6 step 7 (with `anim.usda` empty), answer: (a) Which prims does `stage.Traverse()` visit? (b) What does `/World/Moon.radius` return at frame 12 and at the default time? (c) What happens to `over "Ball" { double radius = 5 }` if it is added to `anim.usda` under `over "World"`?

**Exercise 22-B.** The assembly below references `chair.usda` (which defines `/Chair/Seat` with `float roughness = 0.5` and no inherits). What is `/Room/Chair_1/Seat.roughness`, and what is `/Room/Chair_2/Seat.roughness`?

*File: room.usda*

```usda
#usda 1.0

def "Room"
{
    def "Chair_1" (
        instanceable = true
        prepend references = @./chair.usda@
    )
    {
        over "Seat"
        {
            float roughness = 0.9
        }
    }

    def "Chair_2" (
        instanceable = true
        prepend inherits = </_rough>
        prepend references = @./chair.usda@
    )
    {
    }
}

class "_rough"
{
    over "Seat"
    {
        float roughness = 0.9
    }
}
```

**Exercise 22-C.** A delivery script runs `UsdUtils.FlattenLayerStack(stage)` on an asset with a `color` variant set and a reference to `/studio/lib/bolt.usda`. Does the result still contain (a) the variant set, (b) the bolt reference, (c) relative texture paths?

---

## Chapter review

### Summary

- Split monolithic assets into workstream layers (geo, mtl, rig) that share one namespace and combine as sublayers; only the owner `def`s a prim.
- Bring assets into scenes with references or payloads; layout is a scene-level layer.
- Shot layering: one writer per layer, downstream departments stronger, shared layers weakest; use edit targets, the session layer, and muting.
- `Usd.Stage.Flatten` bakes everything (selected variants only); `UsdUtils.FlattenLayerStack` merges only sublayers and keeps arcs.
- `UsdUtils.LocalizeAsset` and `UsdUtils.CreateNewUsdzPackage` collect dependencies; a `processingFunc` can drop internal ones. Always check the `bool` result.
- Flattening makes asset paths absolute; fix with `ModifyAssetPaths` or a callback. Strip private metadata yourself.
- Instance proxies and prototypes are read-only; change instanced content through the instance root's arcs or an inherited class. "Remove" means block or deactivate.
- Debug with `GetPrimStack`, `GetPropertyStack`, `GetResolveInfo`, `PrimCompositionQuery`, `DumpToString`, `GetCompositionErrors`.
- Ten causes of "my opinion does not show": edit target, weaker arc, stronger sublayer, variant selection, typo, inactive, instance, muted, samples vs default, layer offset.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| "Several departments edit the same asset/shot" | Separate layers, sublayers, edit targets, one writer per layer |
| "Deliver to a client / external party" | Localize or USDZ-package; drop internal deps; strip metadata; check result |
| "Keep variants but merge layers" | `UsdUtils.FlattenLayerStack` |
| "Single self-contained layer, no arcs" | `Usd.Stage.Flatten` (and fix absolute paths) |
| "Remove a property from instanced components" | Block in a class / variant / extra arc on the instance root; not on proxies |
| "authoring to an instance proxy is not allowed" | You are editing below an instance root |
| "Which layer provides this value?" | `attr.GetPropertyStack()[0].layer` |
| "Time samples or default?" | `attr.GetResolveInfo(t).GetSource()` |
| "Which arcs build this prim?" | `Usd.PrimCompositionQuery(prim).GetCompositionArcs()` |
| "Missing file / broken reference" | `stage.GetCompositionErrors()` |

### Review questions

**Q1** · Obj 1.11 · Single choice
A studio wants modeling and surfacing to publish a prop independently. Which layout is most appropriate?
A. `prop.usda` with a variant set `dept = {model, surface}`
B. `prop.usda` sublayering `prop_mtl.usda` and `prop_geo.usda`, both authoring under `/Prop`
C. Two separate assets, `prop_model.usda` and `prop_surface.usda`, each with its own `defaultPrim`, referenced side by side in each shot
D. One `prop.usda` where both teams save in turn

**Q2** · Obj 1.5 · Single choice
In `subLayers = [@a.usda@, @b.usda@, @c.usda@]` on the root layer `shot.usda`, which layer's opinion wins when all four (including `shot.usda`) set the same attribute default?
A. `c.usda`
B. `a.usda`
C. `shot.usda`
D. The one saved most recently

**Q3** · Obj 1.5 · Select two.
Which practices support multi-user shot work?
A. Each artist sets the edit target to their own layer
B. Everyone writes to the root layer and merges by hand
C. Shared sequence layers placed weakest in the sublayer list
D. Variant sets named after artists
E. Saving experiments into the department layer and reverting later

**Q4** · Obj 1.9 · Single choice
Which call returns a single layer in which references and variant sets are preserved but sublayers are merged?
A. `stage.Flatten()`
B. `UsdUtils.FlattenLayerStack(stage)`
C. `UsdUtils.LocalizeAsset(Sdf.AssetPath(p), "out")`
D. `stage.GetRootLayer().Export("out.usda")`

**Q5** · Obj 1.9 · Code reading
What does this print if `/studio/tools/x.py` cannot be resolved and no `processingFunc` is passed?

```{.python .norun}
ok = UsdUtils.LocalizeAsset(Sdf.AssetPath("asset.usda"), "out")
print(ok)
```

(Not run automatically: it needs an `asset.usda` that references an internal path.)
A. `True`, and the path is removed
B. `False`, and the layer is still written with a placeholder path
C. It raises `Tf.ErrorException` and writes nothing
D. `None`

**Q6** · Obj 1.9 · Select two.
After `Usd.Stage.Flatten()`, which statements are true?
A. Unselected variants are gone
B. Asset paths are made absolute
C. `customData` with artist names is removed
D. Instancing is always removed and every instance is copied out

**Q7** · Obj 1.10 · Single choice
`/Room/Chair_1` is instanceable. Which edit removes the value of `studio:tag` from `Chair_1/Seat` while keeping `Chair_1` instanced?
A. `stage.GetPrimAtPath("/Room/Chair_1/Seat").GetAttribute("studio:tag").Block()`
B. Author `over "Seat" { custom string studio:tag = None }` under `Chair_1` in the room layer
C. Add `prepend inherits = </_fix>` on `Chair_1` and block `studio:tag` under `class "_fix"`'s `Seat`
D. Block it on `Chair_1.GetPrototype()`

**Q8** · Obj 1.10 · Single choice
After blocking `studio:tag` through a class, what does `attr.IsValid()` return?
A. `True`
B. `False`
C. `None`
D. It raises an error

**Q9** · Obj 1.8 · Code reading
`GetPropertyStack()` for `radius` returns `[session spec (no value, block), shot.usda spec (2.0), asset.usda spec (1.0)]`. What does `attr.Get()` return?
A. `2.0`
B. `1.0`
C. `None`
D. The fallback value of the schema

**Q10** · Obj 1.8 · Single choice
An artist adds `over "Ball" (active = true)` in a weak sublayer, but `Ball` stays inactive. Why?
A. `active` cannot be authored in sublayers
B. A stronger layer authors `active = false`, and `active` follows normal strength rules
C. Inactive prims can only be activated with `SetActive` in Python
D. The prim is an instance proxy

**Q11** · Obj 1.8 · Select two.
A weak layer selects variant `big`, but the prim shows `small`. Which tools confirm why?
A. `prim.GetPrimStack()` (shows which variant spec contributes)
B. `prim.GetVariantSets().GetVariantSelection("size")`
C. `stage.GetCompositionErrors()`
D. `UsdUtils.ComputeAllDependencies`

**Q12** · Obj 1.8 · Single choice
Which `Usd.CompositionArc` method tells you the layer where an arc was authored?
A. `GetTargetLayer()`
B. `GetIntroducingLayer()`
C. `GetArcType()`
D. `IsImplicit()`

**Q13** · Obj 1.2 · Single choice
A forest of 2 million trees from 12 tree models, where per-tree edits are only position, rotation, scale, and hiding. Which instancing style fits?
A. No instancing
B. Scenegraph instancing with `instanceable = true` on 2 million prims
C. `UsdGeom.PointInstancer` with 12 prototypes
D. One variant per tree

**Q14** · Obj 1.8 · USDA reading
In one layer: `double radius = 9` and `double radius.timeSamples = { 1: 1, 24: 4 }`. What does `Get(Usd.TimeCode.Default())` return, and what does `Get(1)` return?

### Answers

**Q1 — B.** Workstream layers under one namespace combined as sublayers. A uses variants for parts that should be combined. C makes two "assets" that every shot must combine. D blocks parallel work. Review: §22.1.

**Q2 — C.** The root layer is stronger than all its sublayers; among sublayers `a.usda` would be next. Save time never matters. Review: §22.2.

**Q3 — A and C.** Own edit targets avoid conflicts; shared layers weakest let shots override them. B and E cause lost or leaked work; D misuses variants. Review: §22.2.

**Q4 — B.** `FlattenLayerStack` merges only the layer stack. A removes arcs and variants. C copies files but does not merge. D exports the root layer alone. Review: §22.3.

**Q5 — B.** Verified on 26.08: it returns `False`, prints warnings, and writes layers with placeholder paths such as `@0/x.py@`. Review: §22.3.

**Q6 — A and B.** Flatten keeps only selected variants and anchors asset paths. Metadata stays (C false). Instancing is preserved through `Flattened_Prototype_N` prims (D false). Review: §22.3.

**Q7 — C.** An extra inherit on the instance root plus a class opinion changes instanced content legally. A and D raise errors; B is silently ignored. Review: §22.4.

**Q8 — A.** A block hides the value; the property still exists. Review: §22.4.

**Q9 — C.** The strongest opinion is a block, so there is no value. Weaker values are hidden. Review: §22.5, §22.6.

**Q10 — B.** `active` is ordinary metadata with strength; the stronger `false` wins. Review: §22.6 (cause 6).

**Q11 — A and B.** The prim stack shows `{size=small}` specs; `GetVariantSelection` shows the winning selection. Errors and dependencies are unrelated. Review: §22.5, §22.6 (cause 4).

**Q12 — B.** `GetIntroducingLayer()` is where the arc is authored; `GetTargetLayer()` is the layer the arc points to. Review: §22.5.

**Q13 — C.** Point instancing scales to millions with limited per-copy edits. B creates 2 million prims; A and D do not share data. Review: §22.4 (and Ch 25–26).

**Q14 —** `9.0` for the default time, `1.0` at frame 1. Time samples win at time codes; the default answers only a default-time query. Review: §22.6 (cause 9).

### USDA reading exercise answers

**22-A.** (a) `/World` and `/World/Moon`. `Ball` is inactive, so `Traverse()` skips it, and `/Wrold` is only an `over` (not defined), so `Traverse()` skips it too. (b) At frame 12: about `2.435` (linear interpolation: 1 + 3 × 11/23); at the default time: `9.0`. (c) Nothing: `Ball` is inactive in the stronger root layer, so the over is never seen (checklist cause 6).

**22-B.** `Chair_1`: `0.5`. The `over "Seat"` under an instance root is ignored (cause 7). `Chair_2`: `0.9`. The inherit is an arc on the instance root, and inherits are stronger than references. The two chairs have different prototypes.

**22-C.** (a) Yes, `FlattenLayerStack` keeps variant sets. (b) Yes, it keeps references, so the internal bolt reference is still there and must be removed separately. (c) No, it anchors asset paths to absolute paths unless you pass a callback such as `lambda layer, path: path`.

## Further reading

- [S06] OpenUSD API Reference: `UsdStage::Flatten`, `UsdPrimCompositionQuery`, `UsdResolveInfo`, `UsdProperty::GetPropertyStack`, `UsdUtils` (flatten layer stack, localize asset, USDZ). https://openusd.org/release/api/index.html
- [S04] OpenUSD Glossary: edit target, flatten, instancing, layer offset, LIVERPS. https://openusd.org/release/glossary.html
- [S07] USD Toolset: `usdcat`, `usdzip`, `usdview`. https://openusd.org/release/toolset.html
- [S08] USD FAQ: sublayers vs. references; over vs. typeless def. https://openusd.org/release/usdfaq.html
- [S09] USDZ file format specification. https://openusd.org/release/spec_usdz.html
- [S14] NVIDIA Learn OpenUSD: Asset Structure Principles and Content Aggregation; Asset Modularity and Instancing. https://docs.nvidia.com/learn-openusd/latest/index.html
- [S16] Principles of Scalable Asset Structure in OpenUSD. https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html
- [S17] ASWF USD Working Group asset structure guidelines. https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md
