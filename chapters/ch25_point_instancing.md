# Chapter 25 — Point Instancing

> **Exam domain:** Content Aggregation (10%) · **Objectives:** 2.1, 2.3 (also 2.4) · **Study day:** 8 · **Est. time:** 75 min
> **Prerequisites:** Ch 5 (properties and relationships), Ch 10 (time samples), Ch 19 (classes), Ch 21 (list editing and value resolution), Ch 24 (native instancing)

In Chapter 24 you met **native instancing** (also called scenegraph instancing): you mark a prim `instanceable = true`, and USD shares one **prototype** among every prim that composes the same way. Native instancing still creates one prim per instance. This chapter covers the other instancing style. A **PointInstancer** stores thousands or millions of copies as a few arrays on a single prim. It is the tool for forests, crowds of rocks, debris, and particle simulations.

## Learning goals

- Explain what a `UsdGeom.PointInstancer` is and how it differs from native instancing.
- Read and author the per-instance arrays `protoIndices`, `positions`, `orientations`, and `scales`, and the `prototypes` relationship.
- Add a new prototype to an existing PointInstancer without breaking existing instances (Obj 2.1).
- Hide instances efficiently with `invisibleIds` and `inactiveIds`, and compute the result with `ComputeMaskAtTime` (Obj 2.3).
- Use the `ids` attribute to give instances a stable identity that survives reordering.

## Key terms

| Term | One-line definition |
|------|---------------------|
| PointInstancer | A prim type (`UsdGeom.PointInstancer`) that places many copies of prototypes using per-instance arrays |
| Prototype (point instancing) | A prim (and its subtree) that the PointInstancer copies; targeted by the `prototypes` relationship |
| `prototypes` | Relationship whose ordered targets give each prototype an index 0, 1, 2… |
| `protoIndices` | `int[]` saying which prototype index each instance uses; its length is the instance count |
| `positions` / `orientations` / `scales` | Per-instance translation (`point3f[]`), rotation (`quath[]`), and scale (`float3[]`) |
| `ids` | Optional `int64[]` giving each instance a permanent ID number |
| `invisibleIds` | Animatable `int64[]` attribute listing instance IDs to hide |
| `inactiveIds` | List-editable prim metadata listing instance IDs to prune, for all time |
| Mask | A list of `True`/`False` per instance saying which instances survive hiding/pruning |

## 25.1 `UsdGeom.PointInstancer`

### 1. What is it?

A **PointInstancer** is a single prim that draws many copies ("instances") of one or more **prototype** prims. Where each copy goes, how it is rotated and scaled, and which prototype it uses are all stored as arrays on the PointInstancer prim.

### 2. Why do we need it?

Native instancing (Chapter 24) shares the *content* of each instance, but every instance is still a prim on the stage. A forest of one million trees would mean one million prims. Each prim costs memory and composition time (Chapter 26 explains why prim count matters most). A PointInstancer stores one million trees as a handful of arrays on **one** prim, so the stage stays small.

### 3. Beginner explanation

Think of the rubber stamp analogy used for all instancing in this book: one prototype, many stamps. With native instancing you buy a separate sheet of paper (a prim) for every stamp. With a PointInstancer you have one sheet of paper and a printed list: "stamp A at (0,0), stamp B at (2,0), stamp A at (4,0)…". The list is cheap; the paper is the expensive part.

Where the analogy breaks: a stamp on paper cannot be animated. PointInstancer arrays can have time samples, so instances can move, appear, and disappear over time.

### 4. Technical explanation

- `UsdGeom.PointInstancer` is a concrete typed schema. It is **Boundable** (it has an `extent`) and **Xformable**, but it is **not a Gprim**: it has no surface of its own.
- Required properties: the `prototypes` relationship, and the `protoIndices` and `positions` attributes.
- Instance count = length of `protoIndices` (`GetInstanceCount()` returns it). Every other per-instance array must have the same length.
- Prototypes can be any prim subtree, including references to whole assets. The schema docs recommend placing prototypes as children of the PointInstancer, under a `class` prim, so that ordinary traversals (`stage.Traverse()`, `GetChildren()`) skip them and they are not also drawn at their original location. (`over` also works and was the older advice.)
- Instances are **not prims**. You cannot select, reference, or override one instance by path. You change instances by editing the arrays.
- Prototypes inside a PointInstancer can themselves contain native instances or other PointInstancers (nested instancing).

> [!NOTE] PointInstancer was designed to scale to billions of instances. That is why the transform is split into separate position, orientation (quaternion), and scale arrays instead of one 4×4 matrix per instance: fewer bytes, and you can animate only the arrays that change.

### 5. Mental model

```text
 PointInstancer "Forest"   (one prim)
 +-------------------------------------------------+
 | rel prototypes  = [ Pine , Oak ]   index: 0   1 |
 | protoIndices    = [ 0,     1,     0     ]      |
 | positions       = [ (0,0,0),(2,0,0),(4,0,0) ]   |
 +-------------------------------------------------+
            |              |             |
        instance 0     instance 1    instance 2
        Pine @ x=0     Oak @ x=2     Pine @ x=4
```

### 6. Simple example

Two prototypes (a cone "Pine" and a cylinder "Oak") and three instances:

| Instance | `protoIndices` | Prototype | `positions` |
|----------|----------------|-----------|-------------|
| 0 | 0 | Pine | (0, 0, 0) |
| 1 | 1 | Oak | (2, 0, 0) |
| 2 | 0 | Pine | (4, 0, 0) |

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "Forest"
)

def PointInstancer "Forest"
{
    point3f[] positions = [(0, 0, 0), (2, 0, 0), (4, 0, 0)]
    int[] protoIndices = [0, 1, 0]
    rel prototypes = [</Forest/Protos/Pine>, </Forest/Protos/Oak>]

    class "Protos"
    {
        def Cone "Pine"
        {
        }

        def Cylinder "Oak"
        {
        }
    }
}
```

- `rel prototypes` lists the prototypes in order; Pine is index 0, Oak is index 1.
- `protoIndices` has three entries, so there are three instances.
- `class "Protos"` hides the prototypes from normal traversal, so they are drawn only through the instancer.

### 8. Python example

```python
from pxr import Usd, UsdGeom, Sdf

stage = Usd.Stage.CreateInMemory()
forest = UsdGeom.PointInstancer.Define(stage, "/Forest")
protos = stage.DefinePrim("/Forest/Protos")
protos.SetSpecifier(Sdf.SpecifierClass)          # keep prototypes out of traversal
UsdGeom.Cone.Define(stage, "/Forest/Protos/Pine")
UsdGeom.Cylinder.Define(stage, "/Forest/Protos/Oak")

forest.CreatePrototypesRel().SetTargets(
    ["/Forest/Protos/Pine", "/Forest/Protos/Oak"])
forest.CreateProtoIndicesAttr([0, 1, 0])
forest.CreatePositionsAttr([(0, 0, 0), (2, 0, 0), (4, 0, 0)])

print("instances:", forest.GetInstanceCount())
print("traversed prims:", [str(p.GetPath()) for p in stage.Traverse()])
print("is a Gprim:", forest.GetPrim().IsA(UsdGeom.Gprim))
print("is Boundable:", forest.GetPrim().IsA(UsdGeom.Boundable))
t = Usd.TimeCode.Default()
for m in forest.ComputeInstanceTransformsAtTime(t, t):
    print("instance at", tuple(m.ExtractTranslation()))
```

**Expected output**
```text
instances: 3
traversed prims: ['/Forest']
is a Gprim: False
is Boundable: True
instance at (0.0, 0.0, 0.0)
instance at (2.0, 0.0, 0.0)
instance at (4.0, 0.0, 0.0)
```

`ComputeInstanceTransformsAtTime(time, baseTime)` returns one `Gf.Matrix4d` per surviving instance (it applies the hiding mask from 25.4 by default). `baseTime` is used when velocities are authored; for static data pass the same time twice.

### 9. Real-world use case

An open-world game environment scatters 400,000 rocks, grass clumps, and bushes over terrain with a scattering tool. The tool writes one PointInstancer per biome with five to twenty prototypes each. The level loads in seconds because the stage holds a few hundred prims instead of 400,000.

### 10. Common mistakes

> [!MISTAKE] Putting prototypes under a `def` Xform outside the instancer. They are then also drawn once at their own location. Fix: put them under the instancer inside a `class` (or `over`) prim.

> [!MISTAKE] Trying to override one instance by path, e.g. `/Forest/instance_7`. Instances are not prims. Fix: edit the per-instance arrays, or use native instancing if each copy needs its own prim.

### 11. Exam traps

> [!TRAP] "A PointInstancer is a Gprim." False. It is Boundable and Xformable, but not a Gprim.

> [!TRAP] "Point instances can be selected and overridden like native instance proxies." False. Native instances (Chapter 24) are prims and have instance proxies; point instances are array entries with no prim path.

### 12. Practice questions

1. A PointInstancer has `protoIndices = [1, 1, 0, 2]`. How many instances does it draw (assuming nothing is hidden)?
   A. 3  B. 4  C. 2  D. It depends on the length of `prototypes`
2. Why does the schema documentation recommend placing prototypes under a `class` prim below the PointInstancer?
   A. Classes load faster  B. So default traversals skip them and they are not drawn in their own location  C. Because `prototypes` can only target classes  D. To make them instanceable
3. Which statement about point instances is true?
   A. Each instance is a prim with an instance proxy  B. Instances are entries in arrays on one prim  C. Each instance needs `instanceable = true`  D. Instances must all use the same prototype

**Answers**

1. **B.** The instance count is the length of `protoIndices` (4). The values only choose prototypes.
2. **B.** Default traversals skip `class` and pure `over` prims, so the prototypes appear only as instances. `prototypes` can target any prim.
3. **B.** Point instances are array entries. A, C describe native instancing; D is false because `protoIndices` mixes prototypes.

### 13. Exam takeaways

> [!KEY]
> - One PointInstancer prim = many instances; instances are array entries, not prims.
> - Required: `prototypes` (rel), `protoIndices` (int[]), `positions` (point3f[]).
> - Instance count = `len(protoIndices)`.
> - PointInstancer is Boundable and Xformable, not a Gprim.
> - Put prototypes under the instancer in a `class` prim.

## 25.2 `prototypes`, `protoIndices`, `positions`, `orientations`, `scales`

### 1. What is it?

These are the five core properties of a PointInstancer. `prototypes` lists the things to copy. The four arrays say, for each instance, which prototype to use and where, how rotated, and how big.

### 2. Why do we need it?

You must read and write these arrays correctly to add, move, or edit instances. Exam questions show a USDA snippet and ask which prototype or position an instance gets, or why an instancer draws nothing.

### 3. Beginner explanation

Picture a spreadsheet. Each row is one instance. The columns are "prototype number", "position", "rotation", and "scale". USD stores each column as its own array. Row *i* of the spreadsheet is element *i* of every array. The `prototypes` relationship is the legend that says "prototype number 0 means Pine, 1 means Oak".

Where the analogy breaks: a spreadsheet tolerates missing cells. A PointInstancer does not. If one column is shorter than `protoIndices`, transform computation fails for the whole instancer.

### 4. Technical explanation

| Property | Type | Required | Meaning per instance *i* |
|----------|------|----------|--------------------------|
| `prototypes` | relationship | yes | Ordered targets; target *k* is prototype index *k* |
| `protoIndices` | `int[]` | yes | Prototype index of instance *i* |
| `positions` | `point3f[]` | yes | Translation |
| `orientations` | `quath[]` | no | Rotation as a unit quaternion (half precision) |
| `orientationsf` | `quatf[]` | no | Same, in float precision; if authored non-empty, it is preferred over `orientations` |
| `scales` | `float3[]` | no | Non-uniform scale |
| `velocities`, `accelerations`, `angularVelocities` | `vector3f[]` | no | Motion between time samples (motion blur) |
| `ids` | `int64[]` | no | Stable ID (25.5) |
| `invisibleIds` | `int64[]` | no | Hidden IDs (25.4) |

The transform of instance *i* is built from most-local to least-local:

1. the prototype root prim's own local transform;
2. `scales[i]`;
3. `orientations[i]`;
4. `positions[i]` (plus velocity, if authored);
5. the PointInstancer prim's own transform (and its parents').

Rules:

- All per-instance arrays must match `len(protoIndices)`. If they do not, or an index is outside `[0, number of prototypes)`, `ComputeInstanceTransformsAtTime` posts a warning and returns an empty array.
- Optional arrays that are not authored are treated as identity (no rotation, scale 1).
- Pass `UsdGeom.PointInstancer.ExcludeProtoXform` as the third argument of `ComputeInstanceTransformsAtTime` to leave out step 1.
- Primvars on a PointInstancer apply per instance, like primvars on a point cloud: a `vertex` or `varying` primvar gives element *i* to instance *i*; a `constant` primvar applies to all instances.

### 5. Mental model

```text
 instance i:  prototypes[ protoIndices[i] ]
                 then scale    by scales[i]
                 then rotate   by orientations[i]
                 then move to  positions[i]
                 then apply    the instancer's own xform
 rule: every per-instance array has len(protoIndices) elements
```

### 6. Simple example

A box prototype whose own transform moves it up by 1. One instance has `scales[0] = (2,2,2)` and `positions[0] = (10,0,0)`. The box origin ends up at (10, 2, 0): the prototype's +1 is scaled to +2, then moved to x = 10.

### 7. USDA example

```usda
#usda 1.0

def PointInstancer "Rocks"
{
    quath[] orientations = [(1, 0, 0, 0), (0.7071, 0, 0, 0.7071)]
    point3f[] positions = [(10, 0, 0), (20, 0, 0)]
    int[] protoIndices = [0, 0]
    rel prototypes = </Rocks/Protos/Box>
    float3[] scales = [(2, 2, 2), (1, 1, 1)]

    class "Protos"
    {
        def Cube "Box"
        {
            double3 xformOp:translate = (0, 1, 0)
            uniform token[] xformOpOrder = ["xformOp:translate"]
        }
    }
}
```

- Two instances, both using prototype 0 (`Box`).
- Quaternions are written `(real, i, j, k)`. `(0.7071, 0, 0, 0.7071)` is a 90° turn about Z.
- Instance 0 is scaled 2× and placed at x = 10; instance 1 is rotated and placed at x = 20.

### 8. Python example

```python
from pxr import Usd, UsdGeom, Gf, Vt

stage = Usd.Stage.CreateInMemory()
rocks = UsdGeom.PointInstancer.Define(stage, "/Rocks")
box = UsdGeom.Cube.Define(stage, "/Rocks/Protos/Box")
UsdGeom.XformCommonAPI(box).SetTranslate((0, 1, 0))   # prototype's own xform

rocks.CreatePrototypesRel().SetTargets([box.GetPath()])
rocks.CreateProtoIndicesAttr([0, 0])
rocks.CreatePositionsAttr([(10, 0, 0), (20, 0, 0)])
rocks.CreateScalesAttr([(2, 2, 2), (1, 1, 1)])
turn = Gf.Quath(Gf.Rotation(Gf.Vec3d(0, 0, 1), 90).GetQuat())
rocks.CreateOrientationsAttr(Vt.QuathArray([Gf.Quath(1, 0, 0, 0), turn]))

print(rocks.GetOrientationsAttr().GetTypeName(), rocks.GetScalesAttr().GetTypeName())
t = Usd.TimeCode.Default()
for label, incl in [("include", UsdGeom.PointInstancer.IncludeProtoXform),
                    ("exclude", UsdGeom.PointInstancer.ExcludeProtoXform)]:
    xforms = rocks.ComputeInstanceTransformsAtTime(t, t, incl)
    origins = [m.Transform(Gf.Vec3d(0, 0, 0)) for m in xforms]
    print(label, [tuple(round(v, 2) for v in o) for o in origins])
```

**Expected output**
```text
quath[] float3[]
include [(10.0, 2.0, 0.0), (19.0, 0.0, 0.0)]
exclude [(10.0, 0.0, 0.0), (20.0, 0.0, 0.0)]
```

With the prototype transform included, instance 0's origin is at (10, 2, 0): the prototype's +1 in Y was scaled by 2. Instance 1's +1 in Y was rotated 90° about Z, so it points along −X (19, 0, 0). The tiny rounding comes from half-precision quaternions.

### 9. Real-world use case

A VFX crowd department simulates 50,000 birds. Each frame stores `positions`, `orientations`, and `velocities` as time samples, with `protoIndices` choosing one of four bird-flap cycles. Velocities give correct motion blur even though particles are born and die between frames.

### 10. Common mistakes

> [!MISTAKE] Adding an instance to `protoIndices` but forgetting `positions` (or `scales`). The arrays no longer match and the whole instancer computes no transforms. Fix: extend every authored per-instance array together.

> [!MISTAKE] Authoring `orientations` with `Gf.Quatf` values. The attribute type is `quath[]`; use `Gf.Quath` (or author `orientationsf` with `Gf.Quatf`).

### 11. Exam traps

> [!TRAP] Which array sets the instance count? `protoIndices`, not `positions` and not the number of `prototypes` targets.

> [!TRAP] Prototype transforms are not ignored: by default the prototype root's own transform is applied first (most locally), and the instance scale affects it.

### 12. Practice questions

1. A PointInstancer has `prototypes = [</P/A>, </P/B>, </P/C>]` and `protoIndices = [2, 0]`. Which prototypes do instances 0 and 1 use?
   A. A, B  B. C, A  C. B, C  D. C, B
2. `protoIndices` has 5 entries and `positions` has 4. What happens when you call `ComputeInstanceTransformsAtTime`?
   A. The 5th instance is placed at the origin  B. Only 4 instances are drawn  C. A warning is posted and an empty array is returned  D. USD pads `positions` automatically
3. Which properties are required on a PointInstancer? Select two.
   A. `positions`  B. `orientations`  C. `protoIndices`  D. `ids`  E. `scales`

**Answers**

1. **B.** Index 2 is the third target (C); index 0 is the first (A).
2. **C.** Mismatched lengths invalidate the computation for the whole instancer (verified: a warning and an empty result).
3. **A, C.** `prototypes`, `protoIndices`, and `positions` are required; the others are optional.

### 13. Exam takeaways

> [!KEY]
> - Instance *i* uses `prototypes[protoIndices[i]]`.
> - Types: `int[] protoIndices`, `point3f[] positions`, `quath[] orientations`, `float3[] scales`.
> - All per-instance arrays must match `len(protoIndices)`.
> - Transform order: prototype xform → scale → orientation → position → instancer xform.

## 25.3 Adding a prototype

### 1. What is it?

Adding a prototype means giving an existing PointInstancer a new kind of object to copy, for example adding a "Bush" to a forest that has only Pine and Oak, and then creating instances that use it (Obj 2.1).

### 2. Why do we need it?

Set dressers and layout artists often add variety to a scattered set late in production. You want to do this in your own layer, without rewriting the upstream data, and without changing what any existing instance shows.

### 3. Beginner explanation

The `prototypes` list is a legend: "0 = Pine, 1 = Oak". To add Bush, write "2 = Bush" at the **end** of the legend. If you squeeze Bush in at the front, Bush becomes 0, Pine becomes 1, and every existing "0" on the map suddenly means Bush.

Where the analogy breaks: a paper legend is one list. In USD the legend can be assembled from several layers through list editing (Chapter 21), so *where* your edit lands depends on the list-edit operation you author.

### 4. Technical explanation

Adding a prototype takes three steps:

1. **Create the prototype prim**, usually under the instancer's prototype container (`/Forest/Protos/Bush`). It can be a reference to an asset.
2. **Append the target** to the `prototypes` relationship. Its index is its position in the composed target list, so it must go at the end: index = number of existing prototypes.
3. **Use the new index**: author instances whose `protoIndices` value is the new index, and extend `positions` (and every other authored per-instance array, including `ids`) to the same new length.

Relationship targets are list-edited (`prepend`, `append`, `delete`, or explicit). In Python:

- `rel.AddTarget(path)` defaults to `position=Usd.ListPositionBackOfPrependList`. In a **stronger layer** over an existing list, that writes `prepend rel prototypes`, which puts the new prototype at index 0 and shifts every existing prototype by one.
- Use `rel.AddTarget(path, Usd.ListPositionBackOfAppendList)`, which writes `append rel prototypes`.
- In the **same layer** as an explicit target list, `AddTarget` simply adds to the end of that explicit list.

Arrays such as `protoIndices` and `positions` are **not** list-edited: an opinion in a stronger layer replaces the whole array. To add instances from your own layer, write the complete new arrays (old values + new values).

> [!NOTE] If you only need to *swap* what a prototype looks like (for example, a better Pine model), do not add a prototype at all: change what the existing `Pine` prim references. All instances using index 0 update, and no index changes.

### 5. Mental model

```text
 composed prototypes     index     prepend Bush (WRONG)   append Bush (RIGHT)
 ---------------------   -----     --------------------   -------------------
 Pine                      0       Bush                   Pine
 Oak                       1       Pine                   Oak
                           2       Oak                    Bush
 protoIndices [0,1] now draw:      Bush, Pine (changed!)  Pine, Oak (unchanged)
```

### 6. Simple example

Before: `prototypes = [Pine, Oak]`, `protoIndices = [0, 1]`, `positions = [(0,0,0), (2,0,0)]`.
After adding one Bush instance at x = 4: `prototypes = [Pine, Oak, Bush]`, `protoIndices = [0, 1, 2]`, `positions = [(0,0,0), (2,0,0), (4,0,0)]`.

### 7. USDA example

*File: shot_layout.usda* (a stronger layer that sublayers the published `forest.usda`; shown alone here)

```usda
#usda 1.0
(
    subLayers = [@forest.usda@]
)

over "Forest"
{
    point3f[] positions = [(0, 0, 0), (2, 0, 0), (4, 0, 0)]
    int[] protoIndices = [0, 1, 2]
    append rel prototypes = </Forest/Protos/Bush>

    over "Protos"
    {
        def Sphere "Bush"
        {
        }
    }
}
```

- `append rel prototypes` adds Bush **after** Pine and Oak from `forest.usda`, so Bush is index 2.
- `protoIndices` and `positions` are written in full because arrays replace, they do not merge.
- `over "Protos"` adds a child to the existing `class "Protos"`; the composed specifier stays `class`.

### 8. Python example

The script writes a published forest layer, then adds a Bush from a stronger layer twice: once with the default `AddTarget` (wrong) and once with an explicit append (right).

```python
from pxr import Usd, UsdGeom, Sdf

base = Usd.Stage.CreateNew("forest.usda")
forest = UsdGeom.PointInstancer.Define(base, "/Forest")
base.DefinePrim("/Forest/Protos").SetSpecifier(Sdf.SpecifierClass)
UsdGeom.Cone.Define(base, "/Forest/Protos/Pine")
UsdGeom.Cylinder.Define(base, "/Forest/Protos/Oak")
forest.CreatePrototypesRel().SetTargets(
    ["/Forest/Protos/Pine", "/Forest/Protos/Oak"])
forest.CreateProtoIndicesAttr([0, 1])
forest.CreatePositionsAttr([(0, 0, 0), (2, 0, 0)])
base.Save()

def add_bush(position):
    stage = Usd.Stage.CreateInMemory()
    stage.GetRootLayer().subLayerPaths.append("forest.usda")
    pi = UsdGeom.PointInstancer(stage.GetPrimAtPath("/Forest"))
    UsdGeom.Sphere.Define(stage, "/Forest/Protos/Bush")
    rel = pi.GetPrototypesRel()
    if position is None:
        rel.AddTarget("/Forest/Protos/Bush")              # default position
    else:
        rel.AddTarget("/Forest/Protos/Bush", position)
    new_index = len(rel.GetTargets()) - 1                   # only valid if appended
    pi.GetProtoIndicesAttr().Set(list(pi.GetProtoIndicesAttr().Get()) + [new_index])
    pi.GetPositionsAttr().Set(list(pi.GetPositionsAttr().Get()) + [(4, 0, 0)])
    names = [t.name for t in rel.GetTargets()]
    shown = [names[i] for i in pi.GetProtoIndicesAttr().Get()]
    print("  prototypes:", names)
    print("  instances draw:", shown)

print("default AddTarget (prepend):")
add_bush(None)
print("AddTarget with BackOfAppendList:")
add_bush(Usd.ListPositionBackOfAppendList)
```

**Expected output**
```text
default AddTarget (prepend):
  prototypes: ['Bush', 'Pine', 'Oak']
  instances draw: ['Bush', 'Pine', 'Oak']
AddTarget with BackOfAppendList:
  prototypes: ['Pine', 'Oak', 'Bush']
  instances draw: ['Pine', 'Oak', 'Bush']
```

With the default (prepend) the composed list becomes `[Bush, Pine, Oak]`: the two original instances silently turn into Bush and Pine, and the "new" instance gets Oak. With append, the originals are unchanged and the new instance is a Bush.

### 9. Real-world use case

A digital-twin team scatters 12,000 trees around a factory site from a GIS export. The client asks for hedges along the road. The layout artist appends a `Hedge` prototype in the site-dressing layer and writes the extended arrays there. The GIS-generated forest layer is never touched, so it can be regenerated later.

### 10. Common mistakes

> [!MISTAKE] Using `AddTarget(path)` with its default position in a stronger layer. It prepends and re-numbers every existing prototype. Fix: pass `Usd.ListPositionBackOfAppendList`, or author `append` in USDA.

> [!MISTAKE] Appending the target but writing only the new instances into `protoIndices` in the stronger layer. The array replaces the weaker one, so all old instances disappear. Fix: write old + new values.

> [!MISTAKE] Extending `protoIndices` and `positions` but not `ids` (or `scales`, `orientations`) when those are authored. Lengths mismatch and nothing is computed. Fix: extend every authored per-instance array.

### 11. Exam traps

> [!TRAP] "Add the new prototype path to `protoIndices`." No. Paths go in the `prototypes` relationship; `protoIndices` holds integers.

> [!TRAP] Answers that rebuild the whole PointInstancer or flatten the scene "to add a prototype" are heavy-handed. The minimal correct edit is: create the prim, append the target, use the new index.

### 12. Practice questions

1. A composed PointInstancer has `prototypes = [</F/P/A>, </F/P/B>]`. You add `</F/P/C>` with `append rel prototypes`. What `protoIndices` value makes an instance use C?
   A. 0  B. 1  C. 2  D. 3
2. In a stronger layer you call `rel.AddTarget("/F/P/C")` with no position argument. What is authored?
   A. `append rel prototypes = </F/P/C>`  B. `prepend rel prototypes = </F/P/C>`  C. `rel prototypes = [</F/P/A>, </F/P/B>, </F/P/C>]`  D. `add rel prototypes = </F/P/C>`
3. Which steps are needed to add a new prototype and one instance of it? Select two.
   A. Append the prototype's path to the `prototypes` relationship  B. Set `instanceable = true` on the prototype  C. Extend `protoIndices` and every other authored per-instance array by one entry  D. Add the prototype's path to `invisibleIds`  E. Flatten the stage

**Answers**

1. **C.** Indices are zero-based positions in the composed target list; C is third.
2. **B.** `AddTarget` defaults to `Usd.ListPositionBackOfPrependList`, which writes `prepend` (verified on USD 26.08).
3. **A, C.** `instanceable` is native instancing; `invisibleIds` hides IDs; flattening is unnecessary.

### 13. Exam takeaways

> [!KEY]
> - New prototype index = its position in the composed `prototypes` list, so **append** it.
> - `AddTarget` defaults to prepend; use `Usd.ListPositionBackOfAppendList` across layers.
> - Arrays replace, they don't merge: write full `protoIndices`/`positions` in your layer.
> - Extend every authored per-instance array to the same length.

> [!VERSION] The default `position` of `Usd.Relationship.AddTarget` (`Usd.ListPositionBackOfPrependList`) and the resulting `prepend` were verified on USD 26.08.

## 25.4 Hiding instances efficiently (`invisibleIds`, `MakeInvisible`, `DeactivateId`)

### 1. What is it?

A PointInstancer can hide individual instances without deleting them from its arrays. There are two built-in ways: the animatable `invisibleIds` attribute, and the list-editable `inactiveIds` metadata. USD combines both into a **mask** (Obj 2.3).

### 2. Why do we need it?

Deleting an instance means rewriting every per-instance array (millions of values, maybe over many time samples), and it shifts the index of every later instance. A downstream department (lighting, layout) should not have to rewrite an upstream simulation just to remove a tree that blocks the camera.

### 3. Beginner explanation

Imagine a printed seating chart for a stadium. To keep one seat empty, you don't reprint the chart; you put a "Reserved" sticker on it. `invisibleIds` is a sticker list you can change from frame to frame. `inactiveIds` is a sticker list that holds for the whole event, but several people can each add or remove stickers on their own copy, and the lists combine.

Where the analogy breaks: stickers on paper are visible; in USD the hidden instances are simply skipped when transforms, bounds, and drawing are computed.

### 4. Technical explanation

| | `invisibleIds` | `inactiveIds` |
|--|----------------|---------------|
| What it is | `int64[]` attribute (default `[]`) | `int64` list-op **metadata** on the prim |
| Animatable | Yes (time samples) | No: applies to all time |
| Layering | Strongest opinion replaces the whole array | List-edited (`prepend`/`append`/`delete`) across layers |
| Hide API | `InvisId(id, time)`, `InvisIds(ids, time)` | `DeactivateId(id)`, `DeactivateIds(ids)` |
| Show API | `VisId(id, time)`, `VisIds(ids, time)`, `VisAllIds(time)` | `ActivateId(id)`, `ActivateIds(ids)`, `ActivateAllIds()` |
| Good for | Per-frame camera-frustum culling, animated pop-in | Sparse, reversible pruning by downstream departments |

- Values in both lists are **IDs**: values of the `ids` array if authored, otherwise array **indices** (25.5).
- `ComputeMaskAtTime(time)` combines both lists into a `list` of booleans, one per instance, `True` = survives. If every instance survives, it returns an **empty** list (meaning "no masking").
- `ComputeInstanceTransformsAtTime` and `ComputeExtentAtTime` apply the mask by default, so hidden instances are left out of transforms and bounds. Pass `UsdGeom.PointInstancer.IgnoreMask` as the fourth argument to get all instances.
- Despite the name, `inactiveIds` does not deactivate prims: no prims are removed from the stage. It is only a mask.
- `InvisId` authors into the current edit target. If `invisibleIds` was animated in weaker layers, your stronger opinion at that time hides those weaker samples, so overriding animated `invisibleIds` sparsely is hard. That is why downstream edits prefer `inactiveIds`.

> [!TRAP] `UsdGeom.PointInstancer.MakeInvisible()` exists, but it is the method inherited from `UsdGeom.Imageable`. It sets `visibility = "invisible"` on the **whole PointInstancer prim** and takes only an optional time. It does not hide one instance. The per-instance methods are `InvisId`/`InvisIds` (and `MakeVisible()` is likewise the whole-prim Imageable method).

### 5. Mental model

```text
 ids:            [ 10   11   12   13 ]
 inactiveIds:          11              (list-op metadata, all time)
 invisibleIds:                    13   (attribute, can animate)
                  ----------------------
 mask:           [ T    F    T    F  ]  -> 2 instances drawn
 no masking at all ->  mask = []        (empty means "all pass")
```

### 6. Simple example

A forest has four trees with IDs 10–13. Lighting needs tree 11 gone for the whole shot: `DeactivateId(11)`. A camera-culling tool hides tree 13 only from frame 20 on: `InvisId(13, 20)`. The arrays of positions are unchanged.

### 7. USDA example

```usda
#usda 1.0

def PointInstancer "Forest" (
    inactiveIds = [11]
)
{
    int64[] ids = [10, 11, 12, 13]
    int64[] invisibleIds.timeSamples = {
        1: [],
        20: [13],
    }
    point3f[] positions = [(0, 0, 0), (2, 0, 0), (4, 0, 0), (6, 0, 0)]
    int[] protoIndices = [0, 0, 0, 0]
    rel prototypes = </Forest/Protos/Pine>

    class "Protos"
    {
        def Cone "Pine"
        {
        }
    }
}
```

- `inactiveIds = [11]` is prim metadata in the parentheses after the prim name, not an attribute.
- `invisibleIds` is time-sampled: from frame 20, ID 13 is hidden too.
- A stronger layer could write `delete inactiveIds = [11]` to bring tree 11 back.

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
pi = UsdGeom.PointInstancer.Define(stage, "/Forest")
UsdGeom.Cone.Define(stage, "/Forest/Protos/Pine")
pi.CreatePrototypesRel().SetTargets(["/Forest/Protos/Pine"])
pi.CreateProtoIndicesAttr([0, 0, 0, 0])
pi.CreatePositionsAttr([(0, 0, 0), (2, 0, 0), (4, 0, 0), (6, 0, 0)])
pi.CreateIdsAttr([10, 11, 12, 13])
d = Usd.TimeCode.Default()

print("nothing hidden:", list(pi.ComputeMaskAtTime(d)))
pi.DeactivateId(11)                          # list-op metadata, all time
pi.InvisId(13, Usd.TimeCode(20))             # animatable attribute
print("inactiveIds:", pi.GetPrim().GetMetadata("inactiveIds"))
print("invisibleIds @20:", list(pi.GetInvisibleIdsAttr().Get(20)))
print("mask @20:", list(pi.ComputeMaskAtTime(Usd.TimeCode(20))))
xf = pi.ComputeInstanceTransformsAtTime(Usd.TimeCode(20), Usd.TimeCode(20))
print("drawn x @20:", [m.ExtractTranslation()[0] for m in xf])
allx = pi.ComputeInstanceTransformsAtTime(
    Usd.TimeCode(20), Usd.TimeCode(20),
    UsdGeom.PointInstancer.IncludeProtoXform, UsdGeom.PointInstancer.IgnoreMask)
print("ignore mask:", len(allx))

pi.MakeInvisible()                           # Imageable method: whole prim!
print("prim visibility:", pi.GetVisibilityAttr().Get())
pi.MakeVisible()
pi.ActivateAllIds()
pi.VisAllIds(Usd.TimeCode(20))
print("after reset:", list(pi.ComputeMaskAtTime(Usd.TimeCode(20))))
```

**Expected output**
```text
nothing hidden: []
inactiveIds: SdfInt64ListOp(Explicit Items: [11])
invisibleIds @20: [13]
mask @20: [True, False, True, False]
drawn x @20: [0.0, 4.0]
ignore mask: 4
prim visibility: invisible
after reset: []
```

Notice that `MakeInvisible()` changed the prim's `visibility`, not the instance mask.

The second script shows why `inactiveIds` suits downstream work. Authored from a stronger layer, `DeactivateId` and `ActivateId` write sparse list edits instead of replacing the upstream list.

```python
from pxr import Usd, UsdGeom

up = Usd.Stage.CreateNew("sim.usda")
pi = UsdGeom.PointInstancer.Define(up, "/Debris")
pi.CreateProtoIndicesAttr([0, 0, 0, 0])
pi.DeactivateId(1)                                   # upstream prunes index 1
up.Save()

shot = Usd.Stage.CreateInMemory()
shot.GetRootLayer().subLayerPaths.append("sim.usda")
debris = UsdGeom.PointInstancer(shot.GetPrimAtPath("/Debris"))
debris.DeactivateId(2)                               # downstream prunes index 2
debris.ActivateId(1)                                 # ...and restores index 1
spec = shot.GetRootLayer().GetPrimAtPath("/Debris")
ops = spec.GetInfo("inactiveIds")
print("shot layer deletes:", list(ops.deletedItems))
print("shot layer adds:", list(ops.prependedItems) + list(ops.appendedItems))
print("composed:", list(debris.GetPrim().GetMetadata("inactiveIds").explicitItems))
print("mask:", list(debris.ComputeMaskAtTime(Usd.TimeCode.Default())))
```

**Expected output**
```text
shot layer deletes: [1]
shot layer adds: [2]
composed: [2]
mask: [True, True, False, True]
```

### 9. Real-world use case

In a film shot, the camera flies low through a forest. A pipeline tool computes, per frame, which trees are outside the camera frustum and writes them into time-sampled `invisibleIds`. Separately, the director asks to remove three trees blocking a hero moment; the lighting artist uses `DeactivateIds` in the lighting layer. If the trees are needed back, a `delete inactiveIds` in a later layer reverses it without touching the simulation.

### 10. Common mistakes

> [!MISTAKE] Deleting entries from the arrays to "hide" instances. This rewrites everything and shifts later instances. Fix: use `inactiveIds` or `invisibleIds`.

> [!MISTAKE] Calling `pi.MakeInvisible()` to hide one instance. It hides the whole instancer. Fix: `pi.InvisId(id, time)` or `pi.DeactivateId(id)`.

> [!MISTAKE] Passing an array index to `InvisId` when `ids` is authored. The lists hold ID values. Fix: look up the ID with `pi.GetIdsAttr().Get()[index]`.

### 11. Exam traps

> [!TRAP] "inactiveIds deactivates prims." No. It is a per-instance mask; no prims are deactivated or removed.

> [!TRAP] "invisibleIds can be overridden sparsely in many layers." No; it is an array attribute, so the strongest opinion replaces it (and animated values must be re-authored). `inactiveIds` is the list-edited one.

> [!TRAP] An empty result from `ComputeMaskAtTime` means **all instances are visible**, not "no instances".

### 12. Practice questions

1. A lighting artist must permanently remove five instances from an upstream simulation in their own layer, in a way a later department can undo for one of them. Which is the best choice?
   A. Remove the entries from `positions` and `protoIndices`  B. `DeactivateIds` (author `inactiveIds`)  C. `MakeInvisible()` on the PointInstancer  D. Set `active = false` on the prototypes
2. What does `ComputeMaskAtTime` return when no instance is hidden or inactive?
   A. A list of all `True`  B. `None`  C. An empty list  D. A list of all `False`
3. Which statements are true? Select two.
   A. `invisibleIds` can be time-sampled  B. `inactiveIds` can be time-sampled  C. `inactiveIds` is list-editable metadata  D. `MakeInvisible()` adds an ID to `invisibleIds`  E. Hiding an instance shifts the indices of later instances

**Answers**

1. **B.** `inactiveIds` is list-edited, so a later layer can `delete` one ID. A is destructive; C hides everything; D would hide all instances of those prototypes.
2. **C.** An empty mask is the "no masking" signal (verified on USD 26.08).
3. **A, C.** `inactiveIds` is time-uniform; `MakeInvisible()` is the whole-prim Imageable method; masking never shifts indices.

### 13. Exam takeaways

> [!KEY]
> - Hide instances with masks, never by deleting array entries.
> - `invisibleIds`: attribute, animatable, `InvisId`/`VisId`/`VisAllIds`.
> - `inactiveIds`: list-op metadata, all time, sparse and reversible, `DeactivateId`/`ActivateId`/`ActivateAllIds`.
> - `ComputeMaskAtTime` combines both; empty list = nothing masked.
> - `MakeInvisible()` on a PointInstancer hides the whole prim (Imageable).

> [!VERSION] Verified on USD 26.08: `PointInstancer` has `InvisId`, `InvisIds`, `VisId`, `VisIds`, `VisAllIds`, `DeactivateId(s)`, `ActivateId(s)`, `ActivateAllIds`, and `ComputeMaskAtTime(time)`. `MakeInvisible`/`MakeVisible` are inherited from `UsdGeom.Imageable`. Some tutorials loosely say "MakeInvisible" when they mean `InvisId`; the exam objective's intent is per-instance hiding.

## 25.5 `ids` and stable identity

### 1. What is it?

`ids` is an optional `int64[]` attribute that gives each instance a permanent ID number. When it is authored, `invisibleIds` and `inactiveIds` refer to these IDs instead of array positions.

### 2. Why do we need it?

Array positions are not stable. A re-run of a scatter tool might sort trees differently, and in simulations dead particles' slots are reused by new ones. Without IDs, "hide index 2" may hide a different tree after the upstream data changes. IDs let hiding decisions, and tracking for motion blur, follow the same object.

### 3. Beginner explanation

Seat numbers versus names. "Hide the person in seat 3" breaks when everyone changes seats. "Hide the person named Ana" still works. `ids` gives every instance a name tag.

Where the analogy breaks: the "name" is a 64-bit integer, and USD does not check that IDs are unique. Keeping them unique is the authoring tool's job.

### 4. Technical explanation

- `ids` has the same length as `protoIndices` and can be time-sampled (simulations where instances are born and die).
- If `ids` is **not** authored, the values in `invisibleIds` and `inactiveIds` are interpreted as indices into `protoIndices`.
- If `ids` **is** authored, those values are matched against `ids`; values that match no ID have no effect.
- A simulator that increments a counter at each birth produces perfect IDs.
- When you add instances (25.3), give them new IDs that no existing instance uses.

### 5. Mental model

```text
                 without ids          with ids
 order v1:  idx 0 1 2   (A B C)    id 7 8 9  (A B C)
 hide "1"   ->  B hidden           hide 8 -> B hidden
 order v2:  idx 0 1 2   (C A B)    id 9 7 8  (C A B)
 hide "1"   ->  A hidden (wrong!)  hide 8 -> B hidden (still right)
```

### 6. Simple example

Trees A, B, C have IDs 7, 8, 9. You hide ID 8 (tree B). Upstream re-sorts the arrays to C, A, B, with `ids` re-sorted to 9, 7, 8. ID 8 is still tree B, so B stays hidden.

### 7. USDA example

```usda
#usda 1.0

def PointInstancer "Particles" (
    inactiveIds = [8]
)
{
    int64[] ids = [9, 7, 8]
    point3f[] positions = [(4, 0, 0), (0, 0, 0), (2, 0, 0)]
    int[] protoIndices = [0, 0, 0]
    rel prototypes = </Particles/Protos/Drop>

    class "Protos"
    {
        def Sphere "Drop"
        {
        }
    }
}
```

- ID 8 is at array index 2 here, at position (2, 0, 0). That is the instance pruned.
- Without `ids`, `inactiveIds = [8]` would refer to index 8, which does not exist, so nothing would be hidden.

### 8. Python example

```python
from pxr import Usd, UsdGeom

def build(order, use_ids):
    stage = Usd.Stage.CreateInMemory()
    pi = UsdGeom.PointInstancer.Define(stage, "/Trees")
    UsdGeom.Cone.Define(stage, "/Trees/Protos/Pine")
    pi.CreatePrototypesRel().SetTargets(["/Trees/Protos/Pine"])
    tree_x = {"A": 0, "B": 2, "C": 4}
    tree_id = {"A": 7, "B": 8, "C": 9}
    pi.CreateProtoIndicesAttr([0] * len(order))
    pi.CreatePositionsAttr([(tree_x[n], 0, 0) for n in order])
    if use_ids:
        pi.CreateIdsAttr([tree_id[n] for n in order])
        pi.DeactivateId(8)           # "tree B" by ID
    else:
        pi.DeactivateId(1)           # "tree B" by index in the v1 order
    mask = pi.ComputeMaskAtTime(Usd.TimeCode.Default())
    return [n for n, keep in zip(order, mask) if not keep]

for use_ids in (False, True):
    v1 = build(["A", "B", "C"], use_ids)
    v2 = build(["C", "A", "B"], use_ids)
    print("ids" if use_ids else "no ids", "hidden v1:", v1, "hidden v2:", v2)
```

**Expected output**
```text
no ids hidden v1: ['B'] hidden v2: ['A']
ids hidden v1: ['B'] hidden v2: ['B']
```

Without `ids`, the same edit hides a different tree once the upstream order changes. With `ids`, the hidden tree is always B.

### 9. Real-world use case

An FX artist re-simulates a debris explosion after notes. The shot's lighting layer had deactivated three debris pieces that flew into the lens. Because the simulator writes stable `ids`, the same three pieces stay hidden in the new simulation, and nobody has to redo the lighting fix.

### 10. Common mistakes

> [!MISTAKE] Authoring `ids` with a different length than `protoIndices`. Fix: one ID per instance, extended whenever instances are added.

> [!MISTAKE] Adding `ids` to an existing instancer that already uses index-based `invisibleIds`/`inactiveIds`. The old values now mean IDs, so different (or no) instances are hidden. Fix: convert the masks to ID values when you add `ids`.

### 11. Exam traps

> [!TRAP] "`invisibleIds` always holds array indices." Only when `ids` is not authored. With `ids`, it holds ID values.

> [!TRAP] USD does not enforce unique IDs. A question asking "what guarantees uniqueness?" is pointing at the authoring tool, not at USD.

### 12. Practice questions

1. `ids = [100, 200, 300]` and `invisibleIds = [1]`. Which instances are hidden?
   A. The second instance  B. None  C. The first instance  D. All instances
2. Why should a simulation write the `ids` attribute? Select two.
   A. So that masking follows the same particle when array slots are reused  B. It makes `protoIndices` optional  C. It supports identity tracking over time  D. It reduces file size  E. It is required for `ComputeInstanceTransformsAtTime`

**Answers**

1. **B.** With `ids` authored, `1` is treated as an ID, and no instance has ID 1 (verified on USD 26.08).
2. **A, C.** `ids` is optional, adds data, and is not needed for transforms.

### 13. Exam takeaways

> [!KEY]
> - `ids` (`int64[]`, optional, animatable) = stable instance identity.
> - No `ids` → masks use indices; `ids` authored → masks use ID values.
> - Use `ids` whenever upstream order can change or slots are reused.
> - Extend `ids` along with every other array when you add instances.

## Chapter lab(s)

**Lab 24 — PointInstancer: add prototypes, hide instances** (Obj 2.1, 2.3; in `python-labs/`). You build a forest PointInstancer in a published layer, then from a shot layer you append a new prototype and instances, hide trees with `inactiveIds` and time-sampled `invisibleIds`, and check the result with `ComputeMaskAtTime` and `ComputeInstanceTransformsAtTime`. The stretch task re-sorts the upstream arrays and shows that `ids` keeps your hiding decisions stable.

## USDA reading exercises

**Exercise 25-A.** Read this layer. Which prototype does each instance draw, and which instances survive at time 5?

```usda
#usda 1.0

def PointInstancer "Set" (
    inactiveIds = [2]
)
{
    point3f[] positions = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0)]
    int[] protoIndices = [1, 0, 1, 2]
    rel prototypes = [</Set/P/Chair>, </Set/P/Table>, </Set/P/Lamp>]
    int64[] invisibleIds.timeSamples = {
        0: [3],
        10: [],
    }

    class "P"
    {
        def Cube "Chair"
        {
        }

        def Cube "Table"
        {
        }

        def Cube "Lamp"
        {
        }
    }
}
```

**Exercise 25-B.** A stronger layer contains only the following opinion over the layer above. What is the composed `prototypes` order, and which prototype does the instance at index 3 draw now?

```{.usda .norun}
over "Set"
{
    prepend rel prototypes = </Set/P/Sofa>
}
```

This fragment is not a complete layer (it is only the override part), so it is not parsed on its own.

**Answers**

- **25-A.** Instances 0–3 draw Table, Chair, Table, Lamp (`prototypes[1]`, `[0]`, `[1]`, `[2]`). No `ids` is authored, so the masks use indices. Index 2 is inactive for all time. At time 5, `invisibleIds` holds the sample from time 0, `[3]` (array values are held, not interpolated, between samples), so index 3 is hidden too. Instances 0 and 1 survive: mask `[True, True, False, False]`.
- **25-B.** The composed order is `[Sofa, Chair, Table, Lamp]`. Instance 3 has `protoIndices` value 2, which now means **Table** instead of Lamp. Every instance's prototype shifted: this is the prepend trap from 25.3.

## Chapter review

**Summary**

- A PointInstancer stores many instances as arrays on one prim; instances are not prims.
- Required: `prototypes` (rel), `protoIndices`, `positions`. Optional: `orientations` (`quath[]`), `scales`, velocities, `ids`, `invisibleIds`.
- Instance count = `len(protoIndices)`; all per-instance arrays must match it.
- Transform order: prototype root xform → scale → orientation → position → instancer xform.
- Keep prototypes under the instancer inside a `class` prim.
- Add a prototype by **appending** its target, then using the new index and extending every array.
- `AddTarget` defaults to prepend; across layers, pass `Usd.ListPositionBackOfAppendList`.
- Hide instances with `invisibleIds` (animatable) or `inactiveIds` (list-edited, all time); `ComputeMaskAtTime` combines them.
- `MakeInvisible()` on a PointInstancer hides the whole prim.
- `ids` makes hiding follow objects, not array positions.

**If you see… → think…**

| If you see… | Think… |
|-------------|--------|
| "Millions of copies, minimal prim count" | PointInstancer |
| "Add a new prototype" | Append to `prototypes`, new index = old count, extend arrays |
| `prepend rel prototypes` in a stronger layer | All existing indices shift by one |
| "Hide some instances efficiently" | `invisibleIds` / `inactiveIds`, not deleting array entries |
| "Hide per frame / animated" | `invisibleIds` (`InvisId(id, time)`) |
| "Sparse, reversible, downstream" | `inactiveIds` (`DeactivateId`, `delete inactiveIds`) |
| `MakeInvisible()` on the instancer | Whole prim hidden (Imageable visibility) |
| Empty mask from `ComputeMaskAtTime` | Nothing masked: all instances visible |
| "Instance identity survives reordering" | `ids` attribute |
| Instancer draws nothing after an edit | Array length mismatch or bad prototype index |

**Review questions**

**CA-R25-01** · Obj 2.1 · Medium · Single choice
A layout artist adds a `Bush` prototype to a published PointInstancer from a stronger layer and wants existing instances unchanged. Which authored opinion is correct?
A. `prepend rel prototypes = </Forest/Protos/Bush>`
B. `append rel prototypes = </Forest/Protos/Bush>`
C. `int[] protoIndices = [</Forest/Protos/Bush>]`
D. `rel prototypes = </Forest/Protos/Bush>`

**CA-R25-02** · Obj 2.3 · Medium · Single choice
Which call hides only instance ID 42 from frame 100 onward?
A. `pi.MakeInvisible(Usd.TimeCode(100))`
B. `pi.DeactivateId(42)`
C. `pi.InvisId(42, Usd.TimeCode(100))`
D. `pi.GetPrim().SetActive(False)`

**CA-R25-03** · Obj 2.3 · Easy · Select two
Which are valid ways to hide individual point instances without editing `positions`? Select two.
A. Author `invisibleIds`
B. Author `inactiveIds`
C. Set `instanceable = false`
D. Set `visibility = "invisible"` on the prototype
E. Remove the target from `prototypes`

**CA-R25-04** · Obj 2.1 · Medium · Code reading
`prototypes` composes to `[A, B]` and `protoIndices = [0, 1, 1]`. A stronger layer authors `append rel prototypes = <C>` and `int[] protoIndices = [2]`. How many instances are drawn, and what is the problem?
A. 4 instances, no problem
B. 1 instance; the stronger array replaced the old one, and `positions` (length 3) no longer matches, so nothing is computed
C. 3 instances; arrays merge like list ops
D. 1 instance of C

**CA-R25-05** · Obj 2.3 · Medium · Single choice
Upstream simulation data has animated `invisibleIds`. A downstream layer must hide one more instance sparsely, so it is easy to undo later. What should it author?
A. A new full `invisibleIds` time-sample set
B. `inactiveIds` via `DeactivateId`
C. `visibility = "invisible"` on the instancer
D. A shorter `positions` array

**CA-R25-06** · Obj 2.4 · Easy · Single choice
Which property determines a PointInstancer's instance count?
A. `positions`
B. `prototypes`
C. `protoIndices`
D. `ids`

**CA-R25-07** · Obj 2.3 · Hard · Code reading
`ids = [5, 6, 7]`, `invisibleIds = [0]`, `inactiveIds = [7]`. What does `ComputeMaskAtTime` return?
A. `[False, True, False]`
B. `[True, True, False]`
C. `[]`
D. `[False, True, True]`

**CA-R25-08** · Obj 2.4 · Medium · Select two
Which statements about `UsdGeom.PointInstancer` are true? Select two.
A. It is a Gprim
B. It is Boundable
C. Each instance has its own prim path
D. Its prototypes can be any prim subtree, including referenced assets
E. It requires `instanceable = true` on prototypes

**CA-R25-09** · Obj 2.4 · Medium · Single choice
A prototype's root has `xformOp:translate = (0, 1, 0)`. An instance has `scales = (3, 3, 3)` and `positions = (5, 0, 0)`. Using default arguments, where is the prototype's origin placed?
A. (5, 1, 0)
B. (5, 3, 0)
C. (15, 3, 0)
D. (5, 0, 0)

**CA-R25-10** · Obj 2.3 · Medium · Single choice
What is the main advantage of `inactiveIds` over removing entries from the per-instance arrays?
A. It reduces file size
B. It is non-destructive and list-editable, and it keeps every other instance's index
C. It makes instances load faster
D. It works only when `ids` is authored

**Answers and explanations**

- **CA-R25-01 — B.** Append keeps Pine/Oak at indices 0/1. A shifts every index; C puts a path in an int array; D replaces the list in the stronger layer, so the old prototypes are gone. Review: §25.3.
- **CA-R25-02 — C.** `InvisId` is the animatable per-instance hide. A hides the whole instancer; B hides for all time; D deactivates the prim. Review: §25.4.
- **CA-R25-03 — A, B.** Both are per-instance masks. D hides the prototype (all its instances); E breaks indices; C is native instancing. Review: §25.4.
- **CA-R25-04 — B.** Arrays are not list-edited; the stronger `[2]` replaces `[0, 1, 1]`. With `positions` still length 3, the lengths mismatch and no transforms are computed. Review: §25.3.
- **CA-R25-05 — B.** Overriding animated `invisibleIds` requires re-authoring the whole array; `inactiveIds` is sparse and list-edited. Review: §25.4.
- **CA-R25-06 — C.** `GetInstanceCount()` returns `len(protoIndices)`. Review: §25.2.
- **CA-R25-07 — B.** With `ids` authored, the `0` in `invisibleIds` matches no ID, so it hides nothing. ID 7 is at index 2 and is inactive. A wrongly treats `0` as an index. Review: §25.5.
- **CA-R25-08 — B, D.** It is Boundable, not a Gprim; instances have no prim paths; `instanceable` is native instancing. Review: §25.1.
- **CA-R25-09 — B.** Prototype xform first: (0, 1, 0) scaled by 3 is (0, 3, 0), then translated to (5, 3, 0). Review: §25.2.
- **CA-R25-10 — B.** Masking is non-destructive and never re-indexes; `inactiveIds` also composes across layers. It works with or without `ids`. Review: §25.4.

## Further reading

- [S06] OpenUSD API — `UsdGeomPointInstancer` (masking, ids, transform computation): https://openusd.org/release/api/class_usd_geom_point_instancer.html
- [S04] OpenUSD Glossary — Instancing, PointInstancer: https://openusd.org/release/glossary.html
- [S14] NVIDIA Learn OpenUSD — Asset Modularity and Instancing: https://docs.nvidia.com/learn-openusd/latest/index.html
- [S11] Maximizing USD Performance: https://openusd.org/release/maxperf.html
