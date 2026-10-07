# Chapter 26 — Large Scene Optimization

> **Exam domain:** Content Aggregation (10%), also Composition (23%) · **Objectives:** 1.2, 2.4 · **Study day:** 8 · **Est. time:** 70 min
> **Prerequisites:** Ch 6 (kinds), Ch 13 (extent), Ch 17 (payloads), Ch 18 (variant sets), Ch 23 (asset structure), Ch 24 (native instancing), Ch 25 (point instancing)

A **large scene** is a stage with thousands to millions of objects, such as a city, a forest, a factory, or a stadium crowd. This chapter puts the tools from Part IV together: when to use native instancing, point instancing, or no instancing; how payloads keep a scene light; how draw modes and extents hints let viewers show stand-ins; and how variants give you levels of detail. It ends with a decision table and the official "Maximizing USD Performance" guidance as it applies to aggregation. Chapter 44 revisits performance from the debugging side.

## Learning goals

- Choose between no instancing, native instancing, and point instancing for data at different scales (Obj 1.2).
- Structure assets with payloads so a large scene opens fast and loads only what a task needs (Obj 2.4).
- Author `UsdGeom.ModelAPI` draw modes and `extentsHint`, and compute them with `ComputeModelDrawMode` and `ComputeExtentsHint`.
- Build a level-of-detail (LOD) variant set and explain how it interacts with instancing.
- Apply the official performance guidance: prefer crate files, watch layer count, minimize prim count, use transformable gprims, and instance at a higher granularity.

## Key terms

| Term | One-line definition |
|------|---------------------|
| Prim count | Number of prims populated on the stage; the main driver of open time and memory |
| Native instancing | `instanceable = true`; instances are prims that share a prototype (Chapter 24) |
| Point instancing | A `PointInstancer` prim that stores instances as arrays (Chapter 25) |
| Working set | The subset of payloads loaded for the current task |
| Asset interface | Light top-level file of an asset: kind, assetInfo, variant sets, extents hint, and a payload to the heavy data |
| Draw mode | `model:drawMode`: a cheap stand-in (origin axes, bounding box, or textured cards) a viewer may draw instead of full geometry |
| Extents hint | `extentsHint`: a cached bounding box for a whole model, one box per purpose |
| LOD | Level of detail: lighter versions of an asset for distant or background use |
| Crate | The binary `.usdc` format (also the default for `.usd` files) |
| Transformable gprim | A geometric prim (Mesh, Cube…) that carries its own transform, so it needs no parent Xform |

## 26.1 Choosing an instancing style at different scales

### 1. What is it?

It is the decision of how to represent repeated objects: as ordinary unique prims (no instancing), as native instances (`instanceable = true`), or as entries of a PointInstancer. The right answer depends mainly on **how many** copies there are and **how much each copy must differ** (Obj 1.2).

### 2. Why do we need it?

Each style trades editability against cost. Unique prims are fully editable but expensive. Point instances are extremely cheap but are not prims, so you cannot edit one by path. Choosing wrongly gives you a city that will not open, or a hero prop nobody can art-direct.

### 3. Beginner explanation

Three ways to furnish a stadium. **No instancing**: build every seat by hand; each can be unique, and it takes forever. **Native instancing**: order seats from one catalog design; each seat still has its own spot in the inventory (a prim), and you can swap a whole seat for a different catalog design. **Point instancing**: print a seating chart that says "seat design A at these 50,000 coordinates"; there is one document and no per-seat inventory entries.

Where the analogy breaks: the styles mix. A native instance's prototype can contain a PointInstancer, and a PointInstancer's prototype can be a natively instanced asset.

### 4. Technical explanation

| | No instancing | Native instancing | Point instancing |
|--|---------------|-------------------|------------------|
| Typical count | 1 – tens | tens – tens of thousands | thousands – millions (and more) |
| Prims per copy | Whole subtree | 1 (the instance prim); subtree shared in a prototype | 0 (array entries on one prim) |
| Per-copy edits | Anything | On the instance prim: transform, visibility, variant selections, inherited primvars, material binding on the root; inside it only via composition arcs | Only via arrays and masks: position, orientation, scale, prototype index, per-instance primvars, hiding |
| Addressable by path | Yes | Yes (instance proxies are read-only) | No |
| Copies can differ in structure | Yes | Yes, via different variant selections → separate prototypes | Only by choosing a different prototype |
| Good for | Hero assets, things that will be edited | Buildings, vehicles, props in a set | Vegetation, rocks, debris, particles, crowds of simple agents |

Rules of thumb:

- If a copy needs **unique internal edits**, do not instance it (or de-instance just that one: `instanceable = false`).
- If copies need **individual identity in the scenegraph** (selectable, referenced by path, own variant selection), use **native** instancing.
- If you have **very many** copies that differ only in transform and maybe a primvar, use a **PointInstancer**.
- Instance at the **highest sensible granularity**: instance the whole asset, not each leaf mesh (26.5 explains why).
- Native instances that compose identically share one prototype. Different variant selections create different prototypes (`len(stage.GetPrototypes())` grows).

### 5. Mental model

```text
       how many copies?            do copies need unique internal edits?
   few ------------- very many            yes -> NO INSTANCING
    |                    |                no  -> need own prim/path/variant?
    v                    v                          yes -> NATIVE INSTANCING
 NATIVE or NONE    POINT INSTANCER                  no, and huge count
                                                        -> POINT INSTANCER
```

### 6. Simple example

| Content | Count | Choice |
|---------|-------|--------|
| The hero spaceship | 1 | No instancing |
| Parked cars in a city block (some get damage variants) | 300 | Native instancing |
| Grass clumps on a hillside | 2,000,000 | PointInstancer |

### 7. USDA example

The same three trees written in the two instancing styles. (`tree.usda` is a placeholder path; the layer parses on its own.)

```usda
#usda 1.0

def Xform "Native"
{
    def "Tree_01" (instanceable = true
        prepend references = @tree.usda@)
    {
        double3 xformOp:translate = (0, 0, 0)
        uniform token[] xformOpOrder = ["xformOp:translate"]
    }

    def "Tree_02" (instanceable = true
        prepend references = @tree.usda@)
    {
        double3 xformOp:translate = (5, 0, 0)
        uniform token[] xformOpOrder = ["xformOp:translate"]
    }
}

def PointInstancer "Points"
{
    point3f[] positions = [(0, 0, 0), (5, 0, 0)]
    int[] protoIndices = [0, 0]
    rel prototypes = </Points/Protos/Tree>

    class "Protos"
    {
        def "Tree" (prepend references = @tree.usda@)
        {
        }
    }
}
```

- Native: one prim per tree; each carries its own transform and could carry its own variant selection.
- Point: one prim for all trees; the transforms are array entries.

### 8. Python example

The script builds 1,000 copies of a 4-prim tree asset in each of the three styles and counts the prims each stage populates.

```python
from pxr import Usd, UsdGeom, Sdf

N = 1000
asset = Usd.Stage.CreateNew("tree.usda")
root = UsdGeom.Xform.Define(asset, "/Tree")
asset.SetDefaultPrim(root.GetPrim())
for part in ("Trunk", "Crown", "Roots"):
    UsdGeom.Cube.Define(asset, f"/Tree/{part}")
asset.Save()

def count(stage):
    scene = len(list(stage.Traverse()))
    protos = sum(len(list(Usd.PrimRange(p))) for p in stage.GetPrototypes())
    return scene, protos

def build(style):
    stage = Usd.Stage.CreateInMemory()
    UsdGeom.Xform.Define(stage, "/World")
    if style == "point":
        pi = UsdGeom.PointInstancer.Define(stage, "/World/Trees")
        proto = stage.DefinePrim("/World/Trees/Protos/Tree")
        stage.GetPrimAtPath("/World/Trees/Protos").SetSpecifier(Sdf.SpecifierClass)
        proto.GetReferences().AddReference("tree.usda")
        pi.CreatePrototypesRel().SetTargets([proto.GetPath()])
        pi.CreateProtoIndicesAttr([0] * N)
        pi.CreatePositionsAttr([(i * 3.0, 0, 0) for i in range(N)])
        return stage
    for i in range(N):
        prim = stage.DefinePrim(f"/World/Tree_{i:04d}")
        prim.GetReferences().AddReference("tree.usda")
        prim.SetInstanceable(style == "native")
    return stage

for style in ("none", "native", "point"):
    scene, protos = count(build(style))
    print(f"{style:6s} scene prims: {scene:5d}  prototype prims: {protos}")
```

**Expected output**
```text
none   scene prims:  4001  prototype prims: 0
native scene prims:  1001  prototype prims: 4
point  scene prims:     2  prototype prims: 0
```

No instancing populates 4 prims per tree. Native instancing populates 1 prim per tree plus one shared 4-prim prototype. The PointInstancer populates 2 prims in total (its prototypes sit under a `class`, so `Traverse()` skips them).

### 9. Real-world use case

An architecture (AEC) firm models a 40-floor office tower. The lobby's sculpture is unique (no instancing). The 3,000 identical desks are native instances, so facilities staff can select a desk and switch its `config` variant. The 120,000 ceiling tiles and bolts are PointInstancers per floor.

### 10. Common mistakes

> [!MISTAKE] Using PointInstancer for objects that each need a different variant selection or must be selectable by path. Fix: use native instancing for those.

> [!MISTAKE] Instancing every leaf mesh of an asset individually. Prim count does not drop. Fix: make the asset root instanceable.

> [!MISTAKE] Giving each native instance a slightly different variant selection "for variety". Each unique combination creates another prototype, eroding the savings. Fix: limit variety to a few combinations, or vary only things authored on the instance root (transform, primvars, binding).

### 11. Exam traps

> [!TRAP] "Native instancing has zero per-instance prims." No: each native instance is still one prim. Only point instancing removes per-copy prims.

> [!TRAP] "Point instancing is always better because it is cheaper." Not when copies need identity, per-copy variant selections, or path-based overrides.

### 12. Practice questions

1. A game level has 800,000 grass clumps that differ only in position, rotation, and scale. Which style fits best?
   A. No instancing  B. Native instancing  C. PointInstancer  D. One variant per clump
2. A set has 50 street lamps. The lighting team must be able to select individual lamps and switch some to a `broken` variant. Which style fits best?
   A. PointInstancer  B. Native instancing  C. No instancing for all 50  D. Flatten the set
3. A scene has 200 native instances of a car, 100 with `paint=red` and 100 with `paint=blue` selected on the instance prims. How many prototypes does USD create for them?
   A. 1  B. 2  C. 100  D. 200

**Answers**

1. **C.** Huge count, transform-only differences: a PointInstancer.
2. **B.** Native instances are prims, selectable by path, and each can have its own variant selection.
3. **B.** Instances that compose identically share a prototype; two selections give two prototypes.

### 13. Exam takeaways

> [!KEY]
> - Few and unique → no instancing; many with identity → native; huge counts → PointInstancer.
> - Native: 1 prim per copy. Point: 0 prims per copy.
> - Different variant selections on native instances → more prototypes.
> - Instance at the asset level, not per leaf mesh.

## 26.2 Payloads for scalability

### 1. What is it?

A **payload** is a composition arc you can choose not to load (Chapter 17). For large scenes, each asset's heavy geometry sits behind a payload, so a stage can open **unloaded**. You then load only the **working set** a task needs.

### 2. Why do we need it?

A city with 10,000 assets may take minutes to open fully. Many tasks, such as layout, checking what is in the scene, or editing transforms, need only the model hierarchy. With payloads, the scene opens in seconds, and each user loads only their part.

### 3. Beginner explanation

Payloads are lazy-loaded boxes in storage. Each box has a label on the outside (name, kind, size, available variants). You can arrange the boxes on the warehouse floor plan by reading labels alone, and open just the boxes you need to work inside.

Where the analogy breaks: anything written *inside* the box (inside the payloaded layer) is invisible until you load it. Information you want while unloaded, like the bounding box, must be written on the label (the asset interface layer).

### 4. Technical explanation

- Open unloaded: `Usd.Stage.Open(path, Usd.Stage.LoadNone)`. Load parts later: `stage.Load(path)`, `stage.Unload(path)`, or `stage.LoadAndUnload(loadSet, unloadSet)`. Inspect with `stage.GetLoadSet()` and `stage.FindLoadable()`.
- Unloaded prims exist, but their payload contents do not. `prim.IsLoaded()` is `False`.
- `stage.Traverse()` uses the default predicate, which **includes `IsLoaded`**, so it skips unloaded payload prims. Use `stage.TraverseAll()` or `Usd.PrimRange.Stage(stage, Usd.PrimIsActive & Usd.PrimIsDefined)` to see the unloaded model hierarchy.
- Recommended asset structure (Chapter 23 and Maximizing USD Performance): a small `.usda` **asset interface** file containing `kind`, `assetInfo`, variant sets, and an `extentsHint` (the "rest bounding box"), plus a payload to binary `.usdc` files holding geometry and shading.
- Copying information from inside the payload up onto the interface prim is sometimes called **lofting**. `extentsHint` is the classic example (26.3).
- Population masks (`Usd.Stage.OpenMasked`, Chapter 17) are a complementary tool: they limit which *paths* are composed at all.

### 5. Mental model

```text
 city.usda (assembly, opened LoadNone)
 +-- Block_A  ref -> building.usda   [kind, assetInfo, extentsHint]  <- always there
 |                     payload -> building_geo.usdc                  <- loaded on demand
 +-- Block_B  ref -> building.usda   ...
 Open fast with LoadNone  -> see hierarchy + bounds
 stage.Load("/City/Block_A") -> pull in only that geometry
```

### 6. Simple example

A city of three buildings. Opened with `LoadNone`, the stage shows `/City/B0`, `/City/B1`, `/City/B2` and their kinds, but no meshes. A layout artist loads only `B1` to fix its roof.

### 7. USDA example

*File: building.usda* (asset interface)

```usda
#usda 1.0
(
    defaultPrim = "Building"
)

def Xform "Building" (
    prepend apiSchemas = ["GeomModelAPI"]
    assetInfo = {
        string name = "Building"
    }
    kind = "component"
    prepend payload = @./building_geo.usdc@
)
{
    float3[] extentsHint = [(-5, 0, -5), (5, 30, 5)]
}
```

- `prepend payload` points at the heavy binary file.
- `kind`, `assetInfo`, and `extentsHint` live in the interface, so they are available when the payload is unloaded.

### 8. Python example

```python
from pxr import Usd, UsdGeom, Kind, Sdf

geo = Usd.Stage.CreateNew("building_geo.usdc")
geo.SetDefaultPrim(UsdGeom.Xform.Define(geo, "/Building").GetPrim())
UsdGeom.Cube.Define(geo, "/Building/Body").CreateSizeAttr(10.0)
geo.Save()

iface = Usd.Stage.CreateNew("building.usda")
b = UsdGeom.Xform.Define(iface, "/Building")
iface.SetDefaultPrim(b.GetPrim())
Usd.ModelAPI(b.GetPrim()).SetKind(Kind.Tokens.component)
b.GetPrim().GetPayloads().AddPayload("./building_geo.usdc")
iface.Save()

city = Usd.Stage.CreateNew("city.usda")
UsdGeom.Xform.Define(city, "/City")
for i in range(3):
    p = UsdGeom.Xform.Define(city, f"/City/B{i}")
    p.GetPrim().GetReferences().AddReference("building.usda")
    p.AddTranslateOp().Set((i * 20.0, 0, 0))
city.Save()

def files(stage):
    return sorted(Sdf.Layer.GetDisplayNameFromIdentifier(l.identifier)
                  for l in stage.GetUsedLayers() if not l.anonymous)

stage = Usd.Stage.Open("city.usda", Usd.Stage.LoadNone)
print("Traverse:   ", [p.GetName() for p in stage.Traverse()])
print("TraverseAll:", [p.GetName() for p in stage.TraverseAll()])
print("loadable:", [str(p) for p in stage.FindLoadable()])
print("layers unloaded:", files(stage))
stage.Load("/City/B1")
print("loaded set:", [str(p) for p in stage.GetLoadSet()])
b1 = stage.GetPrimAtPath("/City/B1")
print("B1 children:", [c.GetName() for c in b1.GetChildren()])
print("layers after load:", files(stage))
```

**Expected output**
```text
Traverse:    ['City']
TraverseAll: ['City', 'B0', 'B1', 'B2']
loadable: ['/City/B0', '/City/B1', '/City/B2']
layers unloaded: ['building.usda', 'city.usda']
loaded set: ['/City/B1']
B1 children: ['Body']
layers after load: ['building.usda', 'building_geo.usdc', 'city.usda']
```

Notice that `Traverse()` stops at unloaded prims, while `TraverseAll()` shows the model hierarchy. The heavy `.usdc` layer is opened only after a load.

### 9. Real-world use case

A manufacturing digital twin of a car plant has 9,000 robot and conveyor assets. Each is an interface file plus a payload. A process engineer opens the plant unloaded in two seconds, finds line 4 by its `assetInfo`, and loads only the 60 assets on that line for a reach study.

### 10. Common mistakes

> [!MISTAKE] Putting `kind`, `assetInfo`, or `extentsHint` inside the payloaded layer. They vanish when unloaded. Fix: author them in the interface layer, on the prim that holds the payload.

> [!MISTAKE] Using `stage.Traverse()` on an unloaded stage and concluding "the scene is empty". Fix: `stage.TraverseAll()` or a custom predicate without `IsLoaded`.

### 11. Exam traps

> [!TRAP] "Payloads are weaker than references, so they load later." Strength (LIVERPS) and loading are separate ideas. Payload strength is about which opinion wins; the load/unload choice is about whether the arc is composed.

> [!TRAP] "Unloaded prims are removed from the stage." No; the prim holding the payload remains with its interface opinions. Only the payload's contents are missing.

### 12. Practice questions

1. Where should an asset's rest bounding box be authored so that it is available when the stage is opened with `LoadNone`?
   A. Inside the payloaded geometry layer  B. On the payload-holding prim in the interface layer  C. In the session layer  D. In the root layer of every shot
2. You open a stage with `Usd.Stage.LoadNone`. Which call lists the unloaded asset prims? Select two.
   A. `stage.Traverse()`  B. `stage.TraverseAll()`  C. `stage.FindLoadable()`  D. `stage.GetLoadSet()`
3. Which file format does the official guidance recommend for an asset's heavy geometry layer?
   A. `.usda`  B. `.usdc` (crate)  C. `.abc`  D. `.usdz`

**Answers**

1. **B.** Opinions inside the payload are not composed while it is unloaded; the interface prim's opinions are.
2. **B, C.** `Traverse()` skips unloaded prims; `GetLoadSet()` lists only loaded paths (verified on USD 26.08).
3. **B.** Crate opens faster and uses less memory; USDA is fine for the small interface file.

### 13. Exam takeaways

> [!KEY]
> - Heavy data behind payloads; open with `LoadNone`; `Load` the working set.
> - Interface layer = kind, assetInfo, variants, extentsHint, payload arc.
> - `Traverse()` skips unloaded prims; `TraverseAll()` does not.
> - Payload strength (LIVERPS) and loading are unrelated.

## 26.3 Draw modes (`UsdGeom.ModelAPI`) and extents hints

### 1. What is it?

`UsdGeom.ModelAPI` is an applied API schema (written `GeomModelAPI` in USDA) for **model** prims (prims with a kind). It provides **draw modes**, cheap stand-ins a viewer can draw instead of full geometry, and **`extentsHint`**, a cached bounding box for the whole model.

### 2. Why do we need it?

Drawing 10,000 detailed buildings far from the camera wastes time. A box or a few textured cards look almost the same at a distance. Bounds are needed for framing, culling, and stand-ins. Computing them by visiting every mesh is slow, and impossible if the payload is unloaded. `extentsHint` caches them on the model.

### 3. Beginner explanation

Theatre backdrops. Distant buildings on stage are painted flat boards (cards), and furniture placeholders are taped outlines on the floor (bounds). The tape outline is also written on the label of each crate (`extentsHint`), so stagehands know how big the crate is without opening it.

Where the analogy breaks: a draw mode is only a **request** to the viewer or renderer (through Hydra/UsdImaging). The real geometry is still in the scene and still renders in tools that ignore draw modes.

### 4. Technical explanation

Draw mode attributes (all `uniform`):

| Attribute | Type | Fallback | Values / meaning |
|-----------|------|----------|------------------|
| `model:drawMode` | token | `inherited` | `origin` (axes), `bounds` (box), `cards` (textured quads), `default` (full geometry), `inherited` (use the parent's) |
| `model:applyDrawMode` | bool | `false` | Whether this prim actually switches to the resolved draw mode |
| `model:drawModeColor` | float3 | (0.18, 0.18, 0.18) | Color of the stand-in |
| `model:cardGeometry` | token | `cross` | `cross`, `box`, or `fromTexture` |
| `model:cardTextureXPos` … `ZNeg` | asset | — | One texture per card face |

- `ComputeModelDrawMode(parentDrawMode="")` resolves `inherited` by walking up to the nearest ancestor with an authored value; the root fallback is `default`.
- The stand-in is applied at a prim where `model:applyDrawMode` is true **or** (per the 26.08 schema documentation) where the prim has kind `component` and `applyDrawMode` is not authored. Below that prim, the full geometry is replaced.
- Draw modes are interpreted by imaging (UsdImaging/Hydra, e.g. usdview). `usd-core` has no imaging, so in Python you can author and resolve them, not see them.

Extents hint:

- `extentsHint` is a `float3[]` attribute on the model prim. It holds pairs `[min, max]`, one pair per purpose in the order `default`, `render`, `proxy`, `guide`. Trailing purposes with no geometry are dropped; an empty purpose in the middle is stored as an inverted (empty) box.
- `ComputeExtentsHint(bboxCache)` computes the value; `SetExtentsHint(extents, time)` authors it; `GetExtentsHint(time)` reads it.
- `UsdGeom.BBoxCache(time, purposes, useExtentsHint=True)` uses authored hints instead of visiting children. This is fast and works on unloaded payloads, but the hint is a **cache**: if geometry changes and nobody recomputes the hint, the bounds are stale.
- `extentsHint` is for models. A single gprim's own bounds live in `extent` (Chapter 13).

> [!VERSION] Verified on USD 26.08. The installed schema documentation says the draw mode is applied where `model:applyDrawMode` is true, *or* on `component`-kind prims where `applyDrawMode` is not authored. Older documentation and tutorials say that `applyDrawMode` must be set to true. Setting it explicitly works in both cases. This is imaging behavior that cannot be observed with `usd-core`; only the schema text was checked.

### 5. Mental model

```text
 /City  (assembly)          model:drawMode = "bounds"      <- sets the request
   /City/B0 (component)     drawMode: inherited -> bounds   applyDrawMode = true
       Body, Roof ...       replaced by a box drawn from B0's bounds
   /City/B1 (component)     drawMode = "default"            <- opts out: full geometry
 extentsHint on B0: [dflt min, dflt max, render min, render max, proxy min, proxy max]
```

### 6. Simple example

A city assembly sets `model:drawMode = "cards"`. Every building inherits `cards` and shows as textured cards. The hero building next to the camera authors `model:drawMode = "default"` and renders fully.

### 7. USDA example

```usda
#usda 1.0

def Xform "City" (
    prepend apiSchemas = ["GeomModelAPI"]
    kind = "assembly"
)
{
    uniform token model:drawMode = "cards"

    def Xform "Tower" (
        prepend apiSchemas = ["GeomModelAPI"]
        kind = "component"
    )
    {
        float3[] extentsHint = [(-5, 0, -5), (5, 40, 5)]
        uniform bool model:applyDrawMode = 1
        uniform asset model:cardTextureXPos = @tower_xpos.png@
        uniform token model:cardGeometry = "box"
    }

    def Xform "Hero" (
        prepend apiSchemas = ["GeomModelAPI"]
        kind = "component"
    )
    {
        uniform token model:drawMode = "default"
    }
}
```

- `City` requests `cards` for everything below it.
- `Tower` inherits `cards`, applies it, and uses `box` card geometry with a texture on its +X face.
- `Hero` overrides to `default`, so it shows full geometry.

### 8. Python example

```python
from pxr import Usd, UsdGeom, Kind

stage = Usd.Stage.CreateInMemory()
city = UsdGeom.Xform.Define(stage, "/City")
Usd.ModelAPI(city.GetPrim()).SetKind(Kind.Tokens.assembly)
tower = UsdGeom.Xform.Define(stage, "/City/Tower")
Usd.ModelAPI(tower.GetPrim()).SetKind(Kind.Tokens.component)
UsdGeom.Cube.Define(stage, "/City/Tower/Body").CreateSizeAttr(4.0)
proxy = UsdGeom.Cube.Define(stage, "/City/Tower/Proxy")
proxy.CreatePurposeAttr(UsdGeom.Tokens.proxy)
proxy.AddTranslateOp().Set((0, 10, 0))

tm = UsdGeom.ModelAPI.Apply(tower.GetPrim())
print("fallback drawMode:", tm.ComputeModelDrawMode())
print("fallback applyDrawMode:", tm.GetModelApplyDrawModeAttr().Get())
UsdGeom.ModelAPI.Apply(city.GetPrim()).CreateModelDrawModeAttr("bounds")
tm.CreateModelApplyDrawModeAttr(True)
print("inherited from City:", tm.ComputeModelDrawMode())

cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(),
                          UsdGeom.Imageable.GetOrderedPurposeTokens())
hint = tm.ComputeExtentsHint(cache)
tm.SetExtentsHint(hint)
print("purposes:", list(UsdGeom.Imageable.GetOrderedPurposeTokens()))
print("extentsHint pairs:", len(hint) // 2)
print("default box:", hint[0], hint[1])
print("proxy box:  ", hint[4], hint[5])

stage.GetPrimAtPath("/City/Tower/Body").GetAttribute("size").Set(8.0)
for use_hint in (False, True):
    c = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default"],
                          useExtentsHint=use_hint)
    r = c.ComputeWorldBound(tower.GetPrim()).ComputeAlignedRange()
    print("useExtentsHint", use_hint, "->", r.GetMin(), r.GetMax())
```

**Expected output**
```text
fallback drawMode: default
fallback applyDrawMode: False
inherited from City: bounds
purposes: ['default', 'render', 'proxy', 'guide']
extentsHint pairs: 3
default box: (-2, -2, -2) (2, 2, 2)
proxy box:   (-1, 9, -1) (1, 11, 1)
useExtentsHint False -> (-4, -4, -4) (4, 4, 4)
useExtentsHint True -> (-2, -2, -2) (2, 2, 2)
```

The middle pair (render) is an inverted "empty" box because nothing has `render` purpose. After the body grows to size 8, the cache that trusts the hint still reports the old size-4 box: a stale hint. Recompute hints whenever you publish changed geometry.

### 9. Real-world use case

In an animated feature's city set, the layout department sets `model:drawMode = "cards"` on the set's assembly. Artists scrub through shots in usdview at interactive speed, seeing card stand-ins textured from pre-rendered views. The few buildings near camera are switched to `default`. Framing in every tool uses each building's `extentsHint`, even with payloads unloaded.

### 10. Common mistakes

> [!MISTAKE] Forgetting to apply the schema: `UsdGeom.ModelAPI(prim)` without `Apply` gives you the API object but does not add `GeomModelAPI` to `apiSchemas`. Fix: `UsdGeom.ModelAPI.Apply(prim)` when authoring.

> [!MISTAKE] Publishing new geometry without recomputing `extentsHint`. Bounds-based culling then clips the asset. Fix: recompute with `ComputeExtentsHint` in the publish step.

> [!MISTAKE] Expecting draw modes to make a final render cheaper in every renderer. They are a viewer/imaging feature. Fix: use LOD variants (26.4) for renderer-independent savings.

### 11. Exam traps

> [!TRAP] `extentsHint` vs `extent`: `extent` is on a Boundable gprim (its own geometry); `extentsHint` is on a model and covers the whole subtree, per purpose.

> [!TRAP] `model:drawMode` fallback is `inherited`, not `default`. The *resolved* mode with nothing authored anywhere is `default`.

> [!TRAP] `bounds` draws a box; `origin` draws only axes at the prim's origin; `cards` draws textured quads. Don't mix them up.

### 12. Practice questions

1. Which draw mode shows a box around each model?
   A. `origin`  B. `bounds`  C. `cards`  D. `default`
2. An assembly sets `model:drawMode = "cards"`. A child component authors nothing. What does `ComputeModelDrawMode()` return for the child?
   A. `inherited`  B. `default`  C. `cards`  D. `bounds`
3. Why is `extentsHint` useful with payloads? Select two.
   A. It provides bounds while the payload is unloaded  B. It forces the payload to load  C. A `BBoxCache` with `useExtentsHint=True` can use it instead of visiting every child  D. It replaces each mesh's `extent`  E. It is recomputed automatically when geometry changes

**Answers**

1. **B.** `bounds` = box; `origin` = axes; `cards` = textured quads.
2. **C.** `inherited` resolves to the nearest authored ancestor value (verified on USD 26.08).
3. **A, C.** It is a cache: not automatic (E), and it does not replace per-gprim `extent` (D).

### 13. Exam takeaways

> [!KEY]
> - `UsdGeom.ModelAPI.Apply(prim)` → `model:drawMode` (`origin`/`bounds`/`cards`/`default`/`inherited`), `model:applyDrawMode`, card attributes.
> - `ComputeModelDrawMode()` resolves inheritance; with nothing authored it returns `default`.
> - `extentsHint` = per-purpose model bounds; `ComputeExtentsHint(bboxCache)`, `SetExtentsHint`, `GetExtentsHint`.
> - Hints are caches: recompute when geometry changes.

## 26.4 LOD with variants

### 1. What is it?

**Level of detail (LOD)** means providing lighter versions of an asset (for example `high`, `medium`, `low`) and choosing one per use. In USD you usually author LOD as a **variant set**, often named `lod`, with one variant per detail level (Chapter 18).

### 2. Why do we need it?

A building 2 km from the camera does not need 2 million polygons. Swapping to a 2,000-polygon version saves memory and render time in every renderer. Draw modes (26.3) only help viewers that support them.

### 3. Beginner explanation

A variant set is a switch with named positions. The `lod` switch has positions `high`, `medium`, and `low`. Flip it per asset instance: hero buildings on `high`, background on `low`.

Where the analogy breaks: with payloads, each switch position can point at a different payload file, so the unused detail levels are never even opened.

### 4. Technical explanation

- Author one variant per level; inside each, put a different payload or reference (e.g. `building_high.usdc`, `building_low.usdc`), or different geometry.
- Select per prim: `prim.GetVariantSets().GetVariantSet("lod").SetVariantSelection("low")`, or `variants = { string lod = "low" }` in USDA. A selection in a stronger layer (shot, layout) wins over the asset's default.
- Variant **fallbacks** (Chapter 18) can set a pipeline-wide default when nothing is selected.
- With **native instancing**, each distinct LOD selection produces a separate prototype. Two LOD levels in use → two prototypes. This is fine; just keep the number of combinations small.
- With **point instancing**, give each LOD its own prototype (one prototype per LOD level) and choose via `protoIndices`, or put a PointInstancer per LOD band.
- LOD by distance at render time is a renderer feature; USD itself stores the choices, it does not switch automatically by camera distance.

### 5. Mental model

```text
 Building  (variantSet "lod")
   {lod=high}   payload -> building_high.usdc  (2M polys)
   {lod=medium} payload -> building_med.usdc   (200k)
   {lod=low}    payload -> building_low.usdc   (2k)
 instance near camera: lod=high      instance far away: lod=low
 native instances: one prototype per distinct selection in use
```

### 6. Simple example

A street has 100 identical native-instanced houses. The 10 closest select `lod=high`; the other 90 select `lod=low`. The stage has 2 prototypes and loads only the two files in use.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "House"
)

def Xform "House" (
    kind = "component"
    variants = {
        string lod = "high"
    }
    prepend variantSets = "lod"
)
{
    variantSet "lod" = {
        "high" {
            def Sphere "Body"
            {
                double radius = 1
            }
        }
        "low" {
            def Cube "Body"
            {
                double size = 2
            }
        }
    }
}
```

- The asset defaults to `high`. A shot layer can author `variants = { string lod = "low" }` on a referencing prim.
- Here the variants hold inline geometry for brevity; production assets usually put a payload in each variant.

### 8. Python example

```python
from pxr import Usd, UsdGeom

asset = Usd.Stage.CreateNew("house.usda")
house = UsdGeom.Xform.Define(asset, "/House").GetPrim()
asset.SetDefaultPrim(house)
lod = house.GetVariantSets().AddVariantSet("lod")
for name, parts in (("high", 6), ("low", 1)):
    lod.AddVariant(name)
    lod.SetVariantSelection(name)
    with lod.GetVariantEditContext():
        for i in range(parts):
            UsdGeom.Cube.Define(asset, f"/House/Part{i}")
lod.SetVariantSelection("high")
asset.Save()

street = Usd.Stage.CreateInMemory()
for i in range(100):
    p = street.DefinePrim(f"/Street/House_{i:03d}")
    p.GetReferences().AddReference("house.usda")
    p.SetInstanceable(True)
    if i >= 10:                                   # far houses use low LOD
        p.GetVariantSets().GetVariantSet("lod").SetVariantSelection("low")

protos = street.GetPrototypes()
print("prototypes:", len(protos))
for proto in sorted(protos, key=lambda p: len(p.GetChildren())):
    users = [i for i in proto.GetInstances()]
    print(" parts:", len(proto.GetChildren()), "instances:", len(users))
print("scene prims:", len(list(street.Traverse())))
```

**Expected output**
```text
prototypes: 2
 parts: 1 instances: 90
 parts: 6 instances: 10
scene prims: 101
```

### 9. Real-world use case

A driving-simulator team (digital twin of a city for autonomous-vehicle testing) publishes every building with `lod` variants. The sensor simulation near the ego vehicle selects `high`; buildings beyond 300 m use `low`. Their scene layer writes only variant selections, so new LODs from the asset team appear automatically.

### 10. Common mistakes

> [!MISTAKE] Putting all LODs in one layer without payloads. The heavy `high` data is opened even when `low` is selected. Fix: put each level behind its own payload (or reference to a separate `.usdc` file).

> [!MISTAKE] Inconsistent prim names across LOD variants (e.g. materials bound to `/House/HighBody`). Overrides from shots then miss on some LODs. Fix: keep the same hierarchy and names in every level.

### 11. Exam traps

> [!TRAP] "USD switches LOD automatically by camera distance." No. USD stores variants; the pipeline or renderer chooses.

> [!TRAP] "Variant selections break instancing." They don't. Instances with the same selection still share a prototype; you get one prototype per distinct selection.

### 12. Practice questions

1. 500 native instances of a tree: 50 select `lod=high`, 450 select `lod=low`. How many prototypes?
   A. 1  B. 2  C. 50  D. 500
2. Which LOD setup avoids opening high-resolution data for distant instances?
   A. A `lod` variant set where each variant holds a payload to a separate file  B. All LODs as sibling prims with visibility toggles  C. `model:drawMode = "bounds"`  D. One huge `.usda` file

**Answers**

1. **B.** One prototype per distinct composed selection.
2. **A.** The unselected variants' payloads are never composed. B still loads all data; C is a viewer stand-in; D is the slowest option.

### 13. Exam takeaways

> [!KEY]
> - LOD = a variant set (`lod`) with one variant per level, ideally each with its own payload.
> - Select per instance; stronger layers override the asset default.
> - Native instances: one prototype per distinct LOD selection.
> - USD does not choose LOD by distance; your pipeline or renderer does.

## 26.5 Aggregation decision table

### 1. What is it?

**Content aggregation** is combining many assets into larger scenes: components into assemblies, assemblies into sets, sets into shots or worlds. This section collects the choices from Part IV into one decision table, and adds the official **Maximizing USD Performance** guidance that shapes them.

### 2. Why do we need it?

Exam questions in this domain are usually scenarios: "a city with 50,000 buildings must open in under a minute" or "an artist must recolor one instance". You need a fast way to map the scenario to the right tool.

### 3. Beginner explanation

Think of packing for a move. Big furniture you need right away goes in the truck whole (unique prims). Boxes of identical dishes are labelled and stacked (native instances). A bag of 10,000 screws is one bag with a count, not 10,000 entries on your list (PointInstancer). Rooms you won't use for a month stay sealed in storage (unloaded payloads).

Where the analogy breaks: in USD, you can change the packing later without moving anything. Load rules, variant selections, and masks are just opinions in a layer.

### 4. Technical explanation

**Decision table**

| Need | Tool | Chapter |
|------|------|---------|
| Reuse one asset in many places | Reference the asset interface | 16, 23 |
| Open huge scenes fast; load per task | Payloads + `LoadNone` + `Load` | 17, 26.2 |
| Restrict which paths are composed at all | Population mask (`OpenMasked`) | 17 |
| Many identical copies, each a selectable prim | Native instancing | 24 |
| Recolor/retransform one native instance without breaking instancing | Opinions on the instance root (primvars, binding, xform) | 24 |
| Millions of copies, transform-only variation | PointInstancer | 25 |
| Hide some point instances | `invisibleIds` / `inactiveIds` | 25 |
| Swap detail level | `lod` variant set | 18, 26.4 |
| Fast viewer stand-ins | `model:drawMode` + `extentsHint` | 26.3 |
| Organize assets into a navigable tree | Kinds and model hierarchy (component / assembly / group) | 6, 23 |

**Maximizing USD Performance (official guidance), applied to aggregation**

- **Prefer crate files.** Use binary `.usdc` for anything bigger than a few small definitions. A new layer named `*.usd` is crate by default. USDA is fine for small interface or assembly files that mostly reference other files.
- **Monitor layer count.** Open cost grows with the number of files. Asset structures tend to grow from three or four layers to ten or more, multiplied by every unique asset. Collapse layers at publish time where workflows allow. Count with `stage.GetUsedLayers()`. Do not respond by flattening whole sets into one file; that throws away referencing.
- **Minimize prim count.** Cost scales with prims far more than with properties, because every prim must be indexed for composition.
  - **Use transformable gprims.** A `Mesh` (any gprim) has its own `xformOp`s. Don't wrap each mesh in an `Xform` just to move it. The docs report 40–50% fewer prims in typical scenes.
  - **Instance at higher granularity.** Instancing each leaf gprim gives zero prim-count reduction and adds an arc per leaf. Instance whole assets (and add a level on top if you already instance finer).
  - **Prefer property namespaces** (`:`) for organizing data, instead of extra prims.
- **Package assets with payloads** so that scenes can open with only the model hierarchy.
- The same page also recommends building or running USD with a multithreading-friendly allocator such as jemalloc (a build issue, covered in Chapter 44).

### 5. Mental model

```text
 SCALE  ->  1 ......... 100 ........ 10,000 ........ 1,000,000+
 style      unique      native instances ........... PointInstancer
 loading    always      payloads, load the working set
 viewing    full        LOD variants  /  drawMode + extentsHint
 files      few USDA    interface .usda + payload .usdc (crate)
 prims      minimize: transformable gprims, instance whole assets
```

### 6. Simple example

A theme-park digital twin: unique hero rides (no instancing, payloaded), 4,000 benches and lamps (native instances of payloaded assets with `lod`), 600,000 plants (PointInstancers per zone), and a `bounds` draw mode on distant zones in the review viewer.

### 7. USDA example

An assembly that combines the patterns (the referenced files are placeholders; the layer parses on its own):

```usda
#usda 1.0
(
    defaultPrim = "Park"
)

def Xform "Park" (
    prepend apiSchemas = ["GeomModelAPI"]
    kind = "assembly"
)
{
    uniform token model:drawMode = "bounds"

    def "Ride" (prepend references = @ride.usda@)
    {
        uniform token model:drawMode = "default"
    }

    def "Bench_001" (instanceable = true
        prepend references = @bench.usda@
        variants = {
            string lod = "low"
        })
    {
    }

    def PointInstancer "Plants"
    {
        point3f[] positions = [(0, 0, 0), (1, 0, 0)]
        int[] protoIndices = [0, 0]
        rel prototypes = </Park/Plants/Protos/Shrub>

        class "Protos"
        {
            def "Shrub" (prepend references = @shrub.usda@)
            {
            }
        }
    }
}
```

### 8. Python example

Two of the prim-count guidelines, measured: transformable gprims versus Xform-wrapped meshes, and instancing at the asset level versus at each leaf. The script also checks that a new `.usd` layer is crate.

```python
from pxr import Usd, UsdGeom, Sdf

leg = Usd.Stage.CreateNew("leg.usd")                 # .usd -> crate by default
leg.SetDefaultPrim(UsdGeom.Cube.Define(leg, "/Leg").GetPrim())
leg.Save()
print("leg.usd header:", open("leg.usd", "rb").read(8))

asset = Usd.Stage.CreateNew("chair.usd")
asset.SetDefaultPrim(UsdGeom.Xform.Define(asset, "/Chair").GetPrim())
for i in range(4):
    asset.DefinePrim(f"/Chair/Leg{i}").GetReferences().AddReference("leg.usd")
asset.Save()

wrapped = Usd.Stage.CreateInMemory()
direct = Usd.Stage.CreateInMemory()
for i in range(100):
    UsdGeom.Xform.Define(wrapped, f"/Rock{i}").AddTranslateOp().Set((i, 0, 0))
    UsdGeom.Cube.Define(wrapped, f"/Rock{i}/Geo")
    UsdGeom.Cube.Define(direct, f"/Rock{i}").AddTranslateOp().Set((i, 0, 0))
print("Xform+Cube prims:", len(list(wrapped.Traverse())))
print("transformable gprim prims:", len(list(direct.Traverse())))

def room(granularity):
    stage = Usd.Stage.CreateInMemory()
    for i in range(50):
        chair = stage.DefinePrim(f"/Room/Chair{i}")
        chair.GetReferences().AddReference("chair.usd")
        if granularity == "asset":
            chair.SetInstanceable(True)
        else:
            for part in chair.GetChildren():           # instance each leg gprim
                part.SetInstanceable(True)
    return len(list(stage.Traverse())), len(stage.GetPrototypes())

print("leaf-level instancing (prims, prototypes):", room("leaf"))
print("asset-level instancing (prims, prototypes):", room("asset"))
chair_stage = Usd.Stage.Open("chair.usd")
used = [l for l in chair_stage.GetUsedLayers() if not l.anonymous]
print("layers used by chair.usd:", sorted(l.GetDisplayName() for l in used))
```

**Expected output**
```text
leg.usd header: b'PXR-USDC'
Xform+Cube prims: 200
transformable gprim prims: 100
leaf-level instancing (prims, prototypes): (251, 1)
asset-level instancing (prims, prototypes): (51, 1)
layers used by chair.usd: ['chair.usd', 'leg.usd']
```

Leaf-level instancing leaves the prim count where it was; asset-level instancing cuts it to one prim per chair.

### 9. Real-world use case

A games studio's open-world city originally published each building as eleven layers with an `Xform` above every mesh. After a publish step that collapsed layers to an interface `.usda` plus one `.usdc` payload, removed redundant Xforms, and instanced buildings at the asset level, the world's open time in the editor dropped from minutes to seconds.

### 10. Common mistakes

> [!MISTAKE] "Optimizing" by flattening the whole set into one giant file. You lose referencing, instancing structure, and collaborative layering. Fix: collapse layers per asset at publish; keep references between assets.

> [!MISTAKE] Storing large geometry in `.usda`. It opens slower and uses more memory. Fix: `.usdc` for heavy data; keep USDA for small interface/assembly files.

> [!MISTAKE] Wrapping every mesh in an `Xform`. Fix: put `xformOp`s on the mesh itself.

### 11. Exam traps

> [!TRAP] "Property count is the main cost." The guidance says cost scales with **prim** count much more than property count.

> [!TRAP] "Instancing each mesh gives the biggest savings." Gprim-level instancing gives no prim-count reduction; instance at a higher granularity.

> [!TRAP] "Monitor layer count" does not mean "flatten everything". It means keep the number of published layers per asset small.

### 12. Practice questions

1. According to the Maximizing USD Performance guidance, what most strongly drives stage open cost and memory?
   A. Number of properties  B. Number of prims  C. Length of prim names  D. Number of time samples
2. Which changes reduce prim count? Select two.
   A. Remove `Xform` parents that exist only to move a single mesh  B. Make each leaf mesh instanceable  C. Make whole asset roots instanceable  D. Convert `.usdc` files to `.usda`  E. Split each asset into more layers
3. A pipeline publishes each asset as twelve sublayers. What does the guidance recommend?
   A. Flatten the entire set into one file  B. Collapse layers as part of publishing, where workflows allow  C. Convert all layers to USDA  D. Nothing; layer count has no cost

**Answers**

1. **B.** Each prim must be indexed for composition; properties cost much less.
2. **A, C.** Leaf-level instancing gives no reduction (B); file format (D) and layer count (E) don't change prim count.
3. **B.** Fewer layers per asset, but keep the referencing structure; don't flatten whole sets.

### 13. Exam takeaways

> [!KEY]
> - Scale picks the style: unique → native → PointInstancer.
> - Payloads + `LoadNone` for big scenes; LOD variants and draw modes for viewing cost.
> - Prefer crate (`.usdc`; `.usd` defaults to crate); keep layer count per asset low (`GetUsedLayers`).
> - Minimize prims: transformable gprims, instance at asset level, use property namespaces.

## Chapter lab(s)

There is no lab dedicated to this chapter in the lab table. Practice its ideas with **Lab 15 — Payloads, load rules, population masks** (Ch 17), **Lab 22 — Build a component asset and an assembly** (Ch 23), **Lab 23 — Native instancing and instance proxies** (Ch 24), and **Lab 24 — PointInstancer: add prototypes, hide instances** (Ch 25). As an extension, add an `extentsHint` to the Lab 22 component and open the assembly with `LoadNone`.

## USDA reading exercises

**Exercise 26-A.** What does `ComputeModelDrawMode()` return for `/Set/Tree` and for `/Set/Hut`?

```usda
#usda 1.0

def Xform "Set" (
    prepend apiSchemas = ["GeomModelAPI"]
    kind = "assembly"
)
{
    uniform token model:drawMode = "origin"

    def Xform "Tree" (
        prepend apiSchemas = ["GeomModelAPI"]
        kind = "component"
    )
    {
    }

    def Xform "Hut" (
        prepend apiSchemas = ["GeomModelAPI"]
        kind = "component"
    )
    {
        uniform token model:drawMode = "bounds"
    }
}
```

**Exercise 26-B.** This scene has three native instances of `rock.usda`. How many prototypes will the stage have? (`rock.usda` has a `size` variant set with variants `big` and `small`.)

```usda
#usda 1.0

def Xform "Quarry"
{
    def "RockA" (instanceable = true
        prepend references = @rock.usda@
        variants = {
            string size = "big"
        })
    {
    }

    def "RockB" (instanceable = true
        prepend references = @rock.usda@
        variants = {
            string size = "small"
        })
    {
    }

    def "RockC" (instanceable = true
        prepend references = @rock.usda@
        variants = {
            string size = "big"
        })
    {
    }
}
```

**Answers**

- **26-A.** `/Set/Tree` returns `origin`: its `drawMode` is not authored (fallback `inherited`), so it takes the nearest ancestor value. `/Set/Hut` returns `bounds`, its own authored value.
- **26-B.** Two prototypes: RockA and RockC compose identically (`size=big`) and share one; RockB (`size=small`) gets another.

## Chapter review

**Summary**

- Pick the instancing style by scale and editability: unique prims, native instances, or a PointInstancer.
- Native instancing keeps one prim per copy; point instancing has none. Distinct variant selections create extra prototypes.
- Put heavy data behind payloads; open with `LoadNone`; load the working set.
- `Traverse()` skips unloaded prims; use `TraverseAll()` to see the model hierarchy.
- The asset interface holds kind, assetInfo, variants, `extentsHint`, and the payload.
- `UsdGeom.ModelAPI`: `model:drawMode` (`origin`, `bounds`, `cards`, `default`, `inherited`), `model:applyDrawMode`, card attributes.
- `extentsHint` is a per-purpose cached bound; recompute it at publish.
- LOD = a `lod` variant set, ideally with a payload per level.
- Performance guidance: crate files, few layers per asset, few prims (transformable gprims, asset-level instancing, property namespaces).

**If you see… → think…**

| If you see… | Think… |
|-------------|--------|
| "Millions of copies" | PointInstancer |
| "Each copy selectable, own variant" | Native instancing |
| "Scene must open quickly; work on a part" | Payloads, `LoadNone`, `Load` |
| "Bounds while unloaded" | `extentsHint` in the interface layer |
| "Stand-in in the viewer" | `model:drawMode` (`bounds`, `cards`, `origin`) |
| `inherited` draw mode | Resolve from nearest ancestor; root → `default` |
| "Lighter version far from camera" | `lod` variant set |
| "Open time and memory too high" | Prim count first, then layer count, then format |
| An `Xform` above every mesh | Use transformable gprims |
| Instancing at the mesh level | Instance at the asset level |

**Review questions**

**CA-R26-01** · Obj 1.2 · Medium · Single choice
A forest of 3 million trees varies only in position, rotation, scale, and one of 6 species. Which representation is best?
A. 3 million native instances
B. One PointInstancer with 6 prototypes
C. 3 million unique prims
D. A variant set with 3 million variants

**CA-R26-02** · Obj 1.2 · Medium · Single choice
Which requirement rules out point instancing for a set of 40 street cars?
A. The cars share one asset
B. Each car must be selectable by path and have its own `damage` variant selection
C. The cars must be positioned in world space
D. The cars must render with motion blur

**CA-R26-03** · Obj 2.4 · Medium · Select two
A scene of 10,000 payloaded assets opens too slowly. Which actions help directly? Select two.
A. Open the stage with `Usd.Stage.LoadNone` and load only the working set
B. Move `extentsHint` into the payloaded layer
C. Store heavy geometry in `.usdc` instead of `.usda`
D. Wrap each mesh in its own `Xform`
E. Instance each leaf mesh instead of each asset

**CA-R26-04** · Obj 2.4 · Easy · Single choice
Which `model:drawMode` value draws textured quads?
A. `origin`
B. `bounds`
C. `cards`
D. `default`

**CA-R26-05** · Obj 2.4 · Medium · Code reading
```{.python .norun}
cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default"], useExtentsHint=True)
box = cache.ComputeWorldBound(stage.GetPrimAtPath("/City/Tower"))
```
The Tower's geometry was enlarged yesterday, but its `extentsHint` was authored last month. What does `box` report?
A. The new, larger bounds
B. The old bounds from the hint
C. An error, because hints are deprecated
D. An empty box

(This snippet needs an existing stage, so it is not run.)

**CA-R26-06** · Obj 2.4 · Medium · Single choice
Where does `UsdGeom.ModelAPI.ComputeExtentsHint` take its bounds from, and what does it return?
A. From the prim's `extent` only; one box
B. From a `UsdGeom.BBoxCache` passed in; a `float3` array with one min/max pair per purpose
C. From the payload file on disk; a `Gf.Range3d`
D. From `model:drawMode`; a token

**CA-R26-07** · Obj 1.2 · Hard · Single choice
200 native instances of a lamp: 120 select `lod=low`, 80 select `lod=high`, and 10 of the `high` ones also author `primvars:displayColor` on the instance root. How many prototypes are there?
A. 1
B. 2
C. 3
D. 12

**CA-R26-08** · Obj 2.4 · Easy · Single choice
According to the Maximizing USD Performance guidance, what does "leverage transformable gprims" mean?
A. Animate every gprim
B. Put transform ops directly on the gprim instead of adding a parent Xform only to move it
C. Convert gprims to PointInstancers
D. Use `xformOp:transform` matrices only

**CA-R26-09** · Obj 2.4 · Medium · Select two
Which statements about `stage.Traverse()` on a stage opened with `LoadNone` are true? Select two.
A. It skips prims whose payloads are unloaded
B. It loads payloads as it visits them
C. `stage.TraverseAll()` includes the unloaded model prims
D. It raises an error
E. It visits the contents of the payloads

**CA-R26-10** · Obj 2.4 · Medium · Single choice
A distant building should cost less to render in every renderer, not just in usdview. Which is the most direct choice?
A. `model:drawMode = "bounds"`
B. Select `lod=low` from a `lod` variant set
C. Increase `extentsHint`
D. Set `model:applyDrawMode = false`

**Answers and explanations**

- **CA-R26-01 — B.** Huge count, transform and prototype choice only: a PointInstancer with one prototype per species. A and C create millions of prims; D misuses variants. Review: §26.1.
- **CA-R26-02 — B.** Point instances have no paths and no per-instance variant selections. A, C, D are all possible with a PointInstancer (it supports velocities for motion blur). Review: §26.1.
- **CA-R26-03 — A, C.** Loading less and using crate both cut cost. B hides bounds while unloaded; D and E add or keep prims. Review: §26.2, §26.5.
- **CA-R26-04 — C.** `cards` = textured quads; `bounds` = box; `origin` = axes; `default` = full geometry. Review: §26.3.
- **CA-R26-05 — B.** With `useExtentsHint=True`, the cache trusts the authored hint, which is stale (verified by the §26.3 Python example). Review: §26.3.
- **CA-R26-06 — B.** `ComputeExtentsHint(bboxCache)` returns a `Vt.Vec3fArray` of min/max pairs in purpose order: default, render, proxy, guide. Review: §26.3.
- **CA-R26-07 — B.** Primvars and other opinions on the instance root do not change the prototype; only the two LOD selections differ. Review: §26.4 and Chapter 24.
- **CA-R26-08 — B.** Gprims are Xformable; extra Xform parents just add prims. Review: §26.5.
- **CA-R26-09 — A, C.** The default predicate includes `IsLoaded`, so unloaded prims are skipped; `TraverseAll()` uses no such filter. Nothing is loaded automatically. Review: §26.2.
- **CA-R26-10 — B.** LOD variants change the actual scene data. Draw modes are a viewer/imaging stand-in; `extentsHint` is only a bound. Review: §26.4.

## Further reading

- [S11] Maximizing USD Performance: https://openusd.org/release/maxperf.html
- [S06] OpenUSD API — `UsdGeomModelAPI` (draw modes, extents hint): https://openusd.org/release/api/class_usd_geom_model_a_p_i.html
- [S06] OpenUSD API — `UsdGeomPointInstancer`: https://openusd.org/release/api/class_usd_geom_point_instancer.html
- [S16] Principles of Scalable Asset Structure in OpenUSD (NVIDIA): https://docs.omniverse.nvidia.com/usd/latest/learn-openusd/independent/asset-structure-principles.html
- [S17] ASWF USD Working Group — Asset structure guidelines: https://github.com/usd-wg/assets/blob/main/docs/asset-structure-guidelines.md
- [S14] NVIDIA Learn OpenUSD — Asset Structure Principles and Content Aggregation; Asset Modularity and Instancing: https://docs.nvidia.com/learn-openusd/latest/index.html
