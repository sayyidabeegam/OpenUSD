# Chapter 39 — UsdGeom: Geometry, Transforms, Cameras

> **Exam domain:** Visualization (8%) · **Objectives:** 5.1, 8.1 · **Study day:** 11 · **Est. time:** 100 min
> **Prerequisites:** Ch 2 (stages and prims), Ch 5 (attributes), Ch 6 (schemas), Ch 11 (primvars), Ch 13 (extents)

Everything you see in a USD viewport comes from the **UsdGeom** module: the shapes, where they sit, whether they are drawn, and the camera you look through. This chapter teaches the parts of UsdGeom the exam expects you to read and write fluently. Primvars were taught in Chapter 11 and extents in Chapter 13; here we only connect them to meshes.

## Learning goals

- Author transforms with xformOps and predict the result from `xformOpOrder`.
- Compute local and world transforms with `UsdGeom.XformCache`, including `resetXformStack`.
- Build a polygon mesh from `points`, `faceVertexCounts`, and `faceVertexIndices`, and choose the right `subdivisionScheme`.
- Explain how `normals` and `primvars:normals` interact.
- Split a mesh into `GeomSubset`s for per-face materials.
- Control drawing with `visibility` and `purpose`, and describe a camera with `UsdGeom.Camera`.

## Key terms

| Term | One-line definition |
|------|---------------------|
| **Xformable** | Schema base class for every prim that can carry a transform (`UsdGeom.Xformable`). |
| **Xform** | A concrete prim type (`def Xform`) that only groups and transforms its children. |
| **xformOp** | One transform step stored as an attribute named `xformOp:<type>[:<suffix>]`. |
| **xformOpOrder** | A `uniform token[]` attribute listing which xformOps apply and in which order. |
| **Local transform** | The matrix built from a prim's own xformOps (relative to its parent). |
| **World transform** | Local transform combined with every ancestor's transform (local-to-world). |
| **resetXformStack** | A marker in `xformOpOrder` meaning "ignore my parents' transforms". |
| **Gprim** | A "geometric primitive": a drawable shape such as `Mesh`, `Sphere`, `Cube`. |
| **Mesh** | A Gprim made of polygons (faces) built from points. |
| **Winding order** | The order a face lists its points; with `orientation` it decides the front side. |
| **Subdivision** | Smoothing a coarse mesh into a limit surface (default scheme `catmullClark`). |
| **GeomSubset** | A child prim that names a group of faces (or points, edges…) of its parent. |
| **Imageable** | Schema base class that adds `visibility` and `purpose` to anything drawable. |
| **Purpose** | A category (`default`, `render`, `proxy`, `guide`) that renderers include or skip. |
| **Camera** | A `UsdGeom.Camera` prim; converts to the math class `Gf.Camera`. |

---

## 39.1 `Xform` and xformOps, `xformOpOrder`

### 1. What is it?
An **xformOp** is one step of a transform, such as "translate by (10, 0, 0)" or "rotate 90° about Z". A prim stores each step as an attribute and lists the active steps, in order, in its **`xformOpOrder`** attribute.

### 2. Why do we need it?
Artists think in separate steps: move, then rotate, then scale, maybe around a pivot. Storing one opaque 4×4 matrix would lose those steps, make animation curves hard to edit, and make pivots impossible to keep. xformOps keep each step separate, typed, and animatable on its own.

### 3. Beginner explanation
Think of a recipe card. Each line is one instruction ("add salt", "stir", "bake"). The card's line order matters, and a line that is not on the card is never done, even if the salt is sitting on the counter. In USD the xformOp attributes are the ingredients on the counter, and `xformOpOrder` is the recipe card.

*Where the analogy breaks:* a recipe is read top to bottom; for a point, USD applies the **last** op on the card first (see the technical explanation).

### 4. Technical explanation
- Any prim whose schema derives from **`UsdGeom.Xformable`** can carry xformOps: `Xform`, `Mesh`, `Sphere`, `Camera`, lights, and so on. `Scope` is not Xformable, so it cannot.
- Op attributes are named `xformOp:<opType>` with an optional suffix: `xformOp:translate`, `xformOp:rotateXYZ`, `xformOp:scale`, `xformOp:translate:pivot`, `xformOp:transform` (a full matrix), `xformOp:orient` (a quaternion).
- Python adds them with `AddTranslateOp()`, `AddRotateXYZOp()`, `AddRotateZOp()`, `AddScaleOp()`, `AddOrientOp()`, `AddTransformOp()`, … Each call creates the attribute **and** appends its name to `xformOpOrder`.
- Default precisions (verified): translate is `double3`, rotate is `float`/`float3`, scale is `float3`.
- **Only ops listed in `xformOpOrder` count.** An `xformOp:*` attribute not in the list is ignored.
- **Order semantics.** For `xformOpOrder = [A, B, C]` the local matrix is the product in which **C is applied to a point first, then B, then A**. So the standard `["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]` means *scale, then rotate, then translate* — the familiar "TRS".
- In matrix terms USD uses row vectors: `p' = p · M_C · M_B · M_A`.
- An op name prefixed with `!invert!` applies the inverse of that op (used for pivots).
- Adding the same op type and suffix twice raises an error; use a suffix for a second op of the same type.

> [!NOTE] `UsdGeom.XformCommonAPI` is a helper that reads and writes the common "translate, pivot, rotate, scale, inverse pivot" stack in one call. DCC exporters often use it so that every app can understand the result.

### 5. Mental model

```text
xformOpOrder = [ translate , rotateZ , scale ]
                    ^           ^         ^
                    |           |         |
          applied 3rd     applied 2nd   applied 1st   <- to each point

  point ──► scale ──► rotate ──► translate ──► position in parent space
```

Read the list **right to left** to follow a point.

### 6. Simple example
Point (1, 0, 0). Ops: translate (10, 0, 0), rotateZ 90°, scale 2.
- Scale first: (2, 0, 0). Rotate 90° about Z: (0, 2, 0). Translate: **(10, 2, 0)**.
- Reverse the list (scale, rotate, translate): translate first gives (11, 0, 0), rotate gives (0, 11, 0), scale gives **(0, 22, 0)**.

### 7. USDA example

```usda
#usda 1.0
(
    defaultPrim = "Robot"
)

def Xform "Robot"
{
    double3 xformOp:translate = (10, 0, 0)
    float xformOp:rotateZ = 90
    float3 xformOp:scale = (2, 2, 2)
    double3 xformOp:translate:pivot = (0, 1, 0)
    float3 xformOp:rotateXYZ = (45, 0, 0)
    uniform token[] xformOpOrder = [
        "xformOp:translate",
        "xformOp:translate:pivot",
        "xformOp:rotateZ",
        "!invert!xformOp:translate:pivot",
        "xformOp:scale",
    ]
}
```

- Lines with `xformOp:` are the ingredients; `xformOpOrder` is the recipe.
- `xformOp:translate:pivot` plus its `!invert!` twin rotate the robot around (0, 1, 0) instead of its origin.
- `xformOp:rotateXYZ` is authored but **not listed**, so it has no effect.
- `xformOpOrder` is `uniform`: it cannot be animated (the op values can).

### 8. Python example
The script builds both orders from §6 and transforms the same point.

```python
from pxr import Usd, UsdGeom, Gf

stage = Usd.Stage.CreateInMemory()


def make(path, order):
    xf = UsdGeom.Xform.Define(stage, path)
    for op in order:
        if op == "T":
            xf.AddTranslateOp().Set(Gf.Vec3d(10, 0, 0))
        elif op == "R":
            xf.AddRotateZOp().Set(90)
        else:
            xf.AddScaleOp().Set(Gf.Vec3f(2, 2, 2))
    return xf


for path, order in [("/TRS", "TRS"), ("/SRT", "SRT")]:
    xf = make(path, order)
    m = xf.GetLocalTransformation()
    p = m.Transform(Gf.Vec3d(1, 0, 0))
    names = [str(n) for n in xf.GetXformOpOrderAttr().Get()]
    print(path, names)
    print("  (1,0,0) ->", tuple(round(v, 6) + 0.0 for v in p))

trs = stage.GetPrimAtPath("/TRS")
print("precisions:", [op.GetPrecision().name for op in
                      UsdGeom.Xformable(trs).GetOrderedXformOps()])
```

**Expected output**
```text
/TRS ['xformOp:translate', 'xformOp:rotateZ', 'xformOp:scale']
  (1,0,0) -> (10.0, 2.0, 0.0)
/SRT ['xformOp:scale', 'xformOp:rotateZ', 'xformOp:translate']
  (1,0,0) -> (0.0, 22.0, 0.0)
precisions: ['PrecisionDouble', 'PrecisionFloat', 'PrecisionFloat']
```

The output proves the rule: in the first prim the scale (last in the list) hit the point first.

### 9. Real-world use case
In film, a rigged prop exported from Maya keeps translate, rotate-pivot, rotate, and scale as separate ops, so a layout artist in another app can nudge only the translate in a stronger layer (Chapter 15) without baking the whole matrix. In robotics digital twins, each joint is often an Xform with a single animated `rotateZ`, which keeps joint curves readable.

### 10. Common mistakes
> [!MISTAKE] Creating `xformOp:translate` with `CreateAttribute` and forgetting `xformOpOrder`. Nothing moves. Fix: use `AddTranslateOp()`, which updates the order for you, or set `xformOpOrder` yourself.

> [!MISTAKE] Calling `AddTranslateOp()` twice on the same prim. The second call raises an error ("already exists in xformOpOrder"). Fix: reuse `GetTranslateOp()`, or add a second op with a suffix: `AddTranslateOp(opSuffix="pivot")`.

> [!MISTAKE] Overriding `xformOpOrder` in a stronger layer with a shorter list. The ops you dropped silently stop applying. Fix: compare the composed `xformOpOrder` with the authored op attributes when a prim "jumps".

### 11. Exam traps
> [!TRAP] "The first op in `xformOpOrder` is applied first." False for a point: the **last** listed op is applied to the point first.

> [!TRAP] An `xformOp:*` attribute that exists but is not in `xformOpOrder` does nothing. Questions show it in USDA to tempt you.

> [!TRAP] `Scope` is not Xformable. A `Scope` cannot carry xformOps; use `Xform` when you need a transform.

### 12. Practice questions
1. A prim has `xformOpOrder = ["xformOp:scale", "xformOp:translate"]`, scale (3, 3, 3), translate (1, 0, 0). Where does the point (0, 0, 0) end up?
2. Which method both creates `xformOp:rotateXYZ` and lists it in `xformOpOrder`?
   A. `CreateAttribute("xformOp:rotateXYZ")` · B. `AddRotateXYZOp()` · C. `SetXformOpOrder()` · D. `MakeMatrixXform()`
3. Why can `xformOpOrder` not be time-sampled?

**Answers**
1. **(3, 0, 0).** Translate is last, so it applies first: (1, 0, 0); then scale ×3 gives (3, 0, 0).
2. **B.** `AddRotateXYZOp()` creates the attribute and appends it to the order. A creates only the attribute; C sets an order from existing ops; D replaces the stack with one matrix op.
3. It is declared `uniform`, meaning one value for all time. Op values animate; the recipe does not.

### 13. Exam takeaways
> [!KEY]
> - Ops are attributes `xformOp:<type>[:suffix]`; `xformOpOrder` decides which apply and in what order.
> - Follow a point **right to left** through `xformOpOrder`; "translate, rotate, scale" = scale first.
> - Unlisted ops are ignored; `!invert!` applies an op's inverse (pivots).
> - `Add*Op()` creates the attribute and appends to the order; duplicates need a suffix.

---

## 39.2 `XformCache`, local vs. world transforms

### 1. What is it?
A prim's **local transform** places it relative to its parent. Its **world transform** (local-to-world) places it in the stage's root space by combining its local transform with all ancestors'. **`UsdGeom.XformCache`** computes world transforms and remembers the results for reuse.

### 2. Why do we need it?
A renderer, exporter, or physics tool needs world positions. Computing each prim's world matrix from scratch re-walks every ancestor, which is slow for thousands of prims sharing parents. The cache computes each ancestor once per time code.

### 3. Beginner explanation
Your seat number on a train tells you where you are *in the carriage* (local). To know where you are *in the country* (world), you also need where the carriage is on the train and where the train is on the track. If 200 passengers ask, the conductor writes the train's position down once instead of re-measuring it 200 times. That note is the cache.

*Where the analogy breaks:* the cache stores one time code at a time; ask for another time and you must call `SetTime()`.

### 4. Technical explanation
- `UsdGeom.Xformable(prim).GetLocalTransformation(time)` returns the local `Gf.Matrix4d`.
- `UsdGeom.Imageable(prim).ComputeLocalToWorldTransform(time)` computes the world matrix directly (no caching).
- `cache = UsdGeom.XformCache(time)` then:
  - `cache.GetLocalToWorldTransform(prim)` → `Gf.Matrix4d`.
  - `cache.GetLocalTransformation(prim)` → a tuple `(matrix, resetsXformStack)`.
  - `cache.GetParentToWorldTransform(prim)`, `cache.ComputeRelativeTransform(prim, ancestor)`.
  - `cache.SetTime(t)` switches time; `cache.Clear()` empties it (do this after editing transforms).
- With row vectors, `world = local × parentWorld`.
- **`resetXformStack`**: if `xformOpOrder` starts with `"!resetXformStack!"`, the prim ignores all ancestor transforms; its local transform *is* its world transform. Python: `xformable.SetResetXformStack(True)`; query with `GetResetXformStack()`.

### 5. Mental model

```text
 /World            local W  ─┐
   /Car            local C  ─┼─► world(Wheel) = Wheel · C · W
     /Wheel        local Wh ─┘
     /Sticker      ["!resetXformStack!", ...]  ─► world(Sticker) = Sticker
```

### 6. Simple example
`/Parent` translates (5, 0, 0). `/Parent/Child` translates (0, 1, 0). Child's world position is (5, 1, 0). Add `!resetXformStack!` to the child: world position becomes (0, 1, 0).

### 7. USDA example

```usda
#usda 1.0

def Xform "Parent"
{
    double3 xformOp:translate = (5, 0, 0)
    uniform token[] xformOpOrder = ["xformOp:translate"]

    def Xform "Child"
    {
        double3 xformOp:translate = (0, 1, 0)
        uniform token[] xformOpOrder = ["xformOp:translate"]
    }

    def Xform "Hud"
    {
        double3 xformOp:translate = (0, 1, 0)
        uniform token[] xformOpOrder = ["!resetXformStack!", "xformOp:translate"]
    }
}
```

- `Child` inherits the parent's (5, 0, 0) shift; world (5, 1, 0).
- `Hud` lists `!resetXformStack!` first, so it is placed at (0, 1, 0) in world space even though it sits under `Parent`.

### 8. Python example

```python
from pxr import Usd, UsdGeom, Gf

stage = Usd.Stage.CreateInMemory()
parent = UsdGeom.Xform.Define(stage, "/Parent")
op = parent.AddTranslateOp()
op.Set(Gf.Vec3d(0, 0, 0), 1)
op.Set(Gf.Vec3d(10, 0, 0), 10)
child = UsdGeom.Xform.Define(stage, "/Parent/Child")
child.AddTranslateOp().Set(Gf.Vec3d(0, 1, 0))
hud = UsdGeom.Xform.Define(stage, "/Parent/Hud")
hud.AddTranslateOp().Set(Gf.Vec3d(0, 1, 0))
hud.SetResetXformStack(True)

cache = UsdGeom.XformCache(Usd.TimeCode(10))
for prim in (child.GetPrim(), hud.GetPrim()):
    world = cache.GetLocalToWorldTransform(prim)
    local, resets = cache.GetLocalTransformation(prim)
    print(prim.GetName(), "world", world.ExtractTranslation(),
          "local", local.ExtractTranslation(), "resets", resets)

cache.SetTime(Usd.TimeCode(1))
print("t=1 child world", cache.GetLocalToWorldTransform(child.GetPrim())
      .ExtractTranslation())
direct = child.ComputeLocalToWorldTransform(Usd.TimeCode(10))
print("direct t=10", direct.ExtractTranslation())
print("Hud order", [str(t) for t in hud.GetXformOpOrderAttr().Get()])
```

**Expected output**
```text
Child world (10, 1, 0) local (0, 1, 0) resets False
Hud world (0, 1, 0) local (0, 1, 0) resets True
t=1 child world (0, 1, 0)
direct t=10 (10, 1, 0)
Hud order ['!resetXformStack!', 'xformOp:translate']
```

### 9. Real-world use case
A game-engine exporter walks 50,000 prims and writes world matrices for each mesh. Using one `XformCache` per frame means each shared parent (a building, a level) is evaluated once. HUD elements, camera-attached props, or simulation results already in world space use `resetXformStack` so they ignore the rig they are parented under.

### 10. Common mistakes
> [!MISTAKE] Reading `GetLocalTransformation()` and treating it as the world position. Fix: use `XformCache.GetLocalToWorldTransform()` or `ComputeLocalToWorldTransform()`.

> [!MISTAKE] Editing xformOps and then reading the same cache again. The cache may hold the old matrix. Fix: call `cache.Clear()` after edits, or make a new cache.

> [!MISTAKE] Expecting `XformCache.GetLocalTransformation()` to return a matrix. It returns `(matrix, resetsXformStack)`. Fix: unpack the tuple.

### 11. Exam traps
> [!TRAP] `!resetXformStack!` must be the **first** entry of `xformOpOrder`. It is a marker, not an attribute.

> [!TRAP] "XformCache is thread-safe and shared across time codes." It holds one time; switch with `SetTime()`. Answers that say it caches all times are wrong.

### 12. Practice questions
1. `/A` translates (1, 0, 0), `/A/B` translates (0, 2, 0) with `!resetXformStack!`. World position of `/A/B`?
2. Which call returns a tuple? A. `XformCache.GetLocalToWorldTransform` · B. `XformCache.GetLocalTransformation` · C. `Imageable.ComputeLocalToWorldTransform` · D. `Xformable.GetLocalTransformation`
3. Why prefer `XformCache` when exporting many prims?

**Answers**
1. **(0, 2, 0).** The reset marker discards `/A`'s transform.
2. **B.** It returns `(Gf.Matrix4d, bool resetsXformStack)`. The others return a matrix.
3. It computes each ancestor's world matrix once and reuses it for every descendant at that time.

### 13. Exam takeaways
> [!KEY]
> - Local = own ops; world = local × parent world (row vectors).
> - `UsdGeom.XformCache(time)` + `GetLocalToWorldTransform(prim)`; `SetTime()` for other frames, `Clear()` after edits.
> - `"!resetXformStack!"` first in `xformOpOrder` → ignore ancestors (`SetResetXformStack(True)`).

---

## 39.3 Meshes: `points`, `faceVertexCounts`, `faceVertexIndices`, orientation, subdivision

### 1. What is it?
A **`UsdGeom.Mesh`** is a surface made of polygons. Three arrays define it: `points` (vertex positions), `faceVertexCounts` (how many corners each face has), and `faceVertexIndices` (which points make each face, listed face after face).

### 2. Why do we need it?
Almost every asset (characters, cars, buildings) is a polygon mesh. Storing shared points once and referring to them by index keeps files small and lets neighbouring faces share corners.

### 3. Beginner explanation
Think of a connect-the-dots puzzle. `points` is the list of numbered dots. `faceVertexIndices` is the long list of dot numbers you connect. `faceVertexCounts` tells you where one shape ends and the next starts: "the first 4 numbers are shape 1, the next 3 are shape 2".

*Where the analogy breaks:* the direction you connect the dots (clockwise or counter-clockwise) also decides which side of the face is the front.

### 4. Technical explanation
- `point3f[] points` — positions in local space.
- `int[] faceVertexCounts` — one entry per face; the sum must equal `len(faceVertexIndices)`.
- `int[] faceVertexIndices` — indices into `points`; each must be in `[0, len(points))`.
- `uniform token orientation` — default **`rightHanded`**: a face whose points go **counter-clockwise when you look at it** faces you (normal points toward you). `leftHanded` flips this.
- `uniform token subdivisionScheme` — default **`catmullClark`** (verified). Allowed: `catmullClark`, `loop`, `bilinear`, `none`. The default means renderers treat the mesh as a **smooth subdivision surface**. For hard-surface or game/CAD meshes that are already final polygons, set **`none`**.
- `bool doubleSided` (default false) — whether the back side is drawn.
- `extent` must match `points` (see Chapter 13); after changing points, recompute with `UsdGeom.Boundable.ComputeExtentFromPlugins`.
- Helpers: `mesh.GetFaceCount()`, `UsdGeom.Mesh.ValidateTopology(indices, counts, numPoints)` → `(ok, reason)`.

### 5. Mental model

```text
points:            0(0,0,0)  1(1,0,0)  2(1,1,0)  3(0,1,0)  4(2,0,0)
faceVertexCounts:  [ 4 ,        3 ]
faceVertexIndices: [ 0 1 2 3 | 1 4 2 ]
                     face 0    face 1
   3 ──── 2
   │ f0  ╱ \        viewed from +Z, 0→1→2→3 is counter-clockwise
   │    ╱f1 \       → with rightHanded, the normal points to +Z (toward you)
   0 ──── 1 ── 4
```

### 6. Simple example
A single square: 4 points, `faceVertexCounts = [4]`, `faceVertexIndices = [0, 1, 2, 3]`. A square plus a triangle sharing an edge needs only 5 points, not 7, because points 1 and 2 are shared.

### 7. USDA example

```usda
#usda 1.0
(
    upAxis = "Y"
)

def Mesh "Panel"
{
    float3[] extent = [(0, 0, 0), (2, 1, 0)]
    int[] faceVertexCounts = [4, 3]
    int[] faceVertexIndices = [0, 1, 2, 3, 1, 4, 2]
    point3f[] points = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (2, 0, 0)]
    uniform token orientation = "rightHanded"
    uniform token subdivisionScheme = "none"
    color3f[] primvars:displayColor = [(0.8, 0.8, 0.8)]
}
```

- Sum of counts (4 + 3) = 7 = number of indices.
- `orientation` is written out here only for clarity; `rightHanded` is the fallback.
- `subdivisionScheme = "none"` keeps the flat polygons; remove that line and a renderer would smooth the panel.
- `primvars:displayColor` gives a viewport color without a material (Chapter 11.7).

### 8. Python example

```python
from pxr import Usd, UsdGeom, Gf

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Panel")
print("fallbacks:", mesh.GetOrientationAttr().Get(),
      mesh.GetSubdivisionSchemeAttr().Get(), mesh.GetDoubleSidedAttr().Get())

points = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (2, 0, 0)]
counts = [4, 3]
indices = [0, 1, 2, 3, 1, 4, 2]
mesh.CreatePointsAttr(points)
mesh.CreateFaceVertexCountsAttr(counts)
mesh.CreateFaceVertexIndicesAttr(indices)
mesh.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)

ok, why = UsdGeom.Mesh.ValidateTopology(indices, counts, len(points))
print("faces:", mesh.GetFaceCount(), "valid:", ok)
bad_ok, bad_why = UsdGeom.Mesh.ValidateTopology([0, 1, 9], [3], len(points))
print("bad:", bad_ok, bad_why)

extent = UsdGeom.Boundable.ComputeExtentFromPlugins(mesh, Usd.TimeCode.Default())
mesh.CreateExtentAttr(extent)
print("extent:", list(mesh.GetExtentAttr().Get()))
print("subdivisionScheme:", mesh.GetSubdivisionSchemeAttr().Get())
```

**Expected output**
```text
fallbacks: rightHanded catmullClark False
faces: 2 valid: True
bad: False Out of range face vertex index 9: Vertex must be in the range [0,5).
extent: [Gf.Vec3f(0.0, 0.0, 0.0), Gf.Vec3f(2.0, 1.0, 0.0)]
subdivisionScheme: none
```

> [!VERSION] Verified on USD 26.08: the fallback of `subdivisionScheme` is `catmullClark`, `orientation` is `rightHanded`, and `doubleSided` is `false`.

### 9. Real-world use case
A CAD-to-USD converter for a factory digital twin writes tessellated triangles. If it forgets `subdivisionScheme = "none"`, Storm and production renderers smooth every sharp machined edge into a blob, and render time explodes. Character assets for film, by contrast, keep `catmullClark` on purpose: the low-resolution cage is light to store and smooths at render time.

### 10. Common mistakes
> [!MISTAKE] Exporting triangulated game/CAD meshes with the default subdivision scheme. Edges look melted. Fix: author `subdivisionScheme = "none"`.

> [!MISTAKE] `faceVertexCounts` that do not add up to `len(faceVertexIndices)`, or an index ≥ `len(points)`. Renderers drop or garble the mesh. Fix: run `UsdGeom.Mesh.ValidateTopology`.

> [!MISTAKE] Mirroring a mesh (negative scale or flipped winding) and getting inside-out shading. Fix: reverse the winding, or set `orientation = "leftHanded"`.

> [!MISTAKE] Editing `points` without updating `extent`. The mesh gets culled at the wrong times (Chapter 13).

### 11. Exam traps
> [!TRAP] "The default `subdivisionScheme` is `none`." It is `catmullClark`. An unconfigured mesh is a smooth surface.

> [!TRAP] `faceVertexCounts` is per **face**; `faceVertexIndices` is per **face-vertex** (corner). Don't confuse the lengths.

> [!TRAP] Right-handed means counter-clockwise winding **as seen from the front**. A question may describe clockwise winding and ask which way the normal points.

### 12. Practice questions
1. A mesh has `faceVertexCounts = [3, 3, 4]`. How many entries must `faceVertexIndices` have?
2. Select two. Which values are allowed for `subdivisionScheme`? A. `catmullClark` · B. `smooth` · C. `none` · D. `polygon`
3. A low-poly game asset looks rounded and blobby in usdview. What single attribute change most likely fixes it?

**Answers**
1. **10** (3 + 3 + 4).
2. **A, C.** The allowed set is `catmullClark`, `loop`, `bilinear`, `none`. "smooth" is a value of `triangleSubdivisionRule`, not of the scheme.
3. Set `subdivisionScheme = "none"`; the default `catmullClark` smooths it.

### 13. Exam takeaways
> [!KEY]
> - `points` + `faceVertexCounts` (per face) + `faceVertexIndices` (per corner); sums must match.
> - `orientation` fallback `rightHanded`: counter-clockwise from the front faces you.
> - `subdivisionScheme` fallback **`catmullClark`** → smooth; use `none` for final polygons.
> - Keep `extent` in sync with `points`; validate topology with `Mesh.ValidateTopology`.

---

## 39.4 Normals

### 1. What is it?
A **normal** is a direction perpendicular to the surface at a point. Renderers use it to compute lighting. On a mesh you can store normals in the `normals` attribute or as the primvar `primvars:normals`.

### 2. Why do we need it?
Without authored normals, a renderer computes them from the polygons, which gives faceted or smooth shading by its own rules. Authored normals let an exporter keep the exact hard and soft edges an artist chose in the DCC.

### 3. Beginner explanation
Imagine tiny flagpoles stuck into the surface. Light is judged by the angle between the light and each flagpole. If two faces share a corner but each has its own flagpole there, the edge looks sharp; if they share one flagpole, the edge looks smooth.

*Where the analogy breaks:* the flagpoles are not geometry; they never change the shape, only the shading.

### 4. Technical explanation
- `normal3f[] normals` is defined on `UsdGeom.PointBased`. Its length depends on its **interpolation** metadata (`SetNormalsInterpolation`), which defaults to `vertex` (one per point). `faceVarying` (one per face-corner) is how hard edges are stored.
- `normals` is **not** a primvar, although it has interpolation. You can instead author `primvars:normals` (a real primvar, so it can be **indexed**, see Chapter 11.4).
- **Precedence:** if both `normals` and `primvars:normals` are authored, **`primvars:normals` wins** (UsdGeomPointBased documentation).
- Do **not** author normals on a mesh that is subdivided (`subdivisionScheme` not `none`): subdivision computes its own normals and ignores yours. Set `subdivisionScheme = "none"` when you export normals.
- Lighting expects normals that point outward on the front side defined by `orientation`.

### 5. Mental model

```text
Which normals does a renderer use?
  subdivisionScheme != "none" ─► computed by subdivision (yours ignored)
  else primvars:normals authored? ─► use primvars:normals
  else normals authored?          ─► use normals
  else                            ─► renderer computes them
```

### 6. Simple example
A cube exported with hard edges has 8 points but 24 face-corners. Store 24 normals with `faceVarying` interpolation (each face's corners point straight out), or 6 unique normals in an indexed `primvars:normals` with 24 indices.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Quad"
{
    int[] faceVertexCounts = [4]
    int[] faceVertexIndices = [0, 1, 2, 3]
    point3f[] points = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    uniform token subdivisionScheme = "none"
    normal3f[] normals = [(0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1)] (
        interpolation = "vertex"
    )
    normal3f[] primvars:normals = [(0, 0, 1)] (
        interpolation = "faceVarying"
    )
    int[] primvars:normals:indices = [0, 0, 0, 0]
}
```

- Both forms are authored. The `primvars:normals` version (+Z, indexed, faceVarying) is the one renderers use.
- The stale `normals` (−Z) would shade the quad as if it faced away; it is ignored here.
- `subdivisionScheme = "none"` so the normals are honored at all.

### 8. Python example

```python
from pxr import Usd, UsdGeom, Sdf

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Quad")
mesh.CreatePointsAttr([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)])
mesh.CreateFaceVertexCountsAttr([4])
mesh.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
mesh.CreateSubdivisionSchemeAttr("none")

print("default normals interpolation:", mesh.GetNormalsInterpolation())
mesh.CreateNormalsAttr([(0, 0, -1)] * 4)

pv = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(
    "normals", Sdf.ValueTypeNames.Normal3fArray, UsdGeom.Tokens.faceVarying)
pv.Set([(0, 0, 1)])
pv.SetIndices([0, 0, 0, 0])

api = UsdGeom.PrimvarsAPI(mesh)
if api.HasPrimvar("normals"):
    used = api.GetPrimvar("normals")
    print("using primvars:normals",
          [tuple(n) for n in used.ComputeFlattened()])
else:
    print("using normals", list(mesh.GetNormalsAttr().Get()))
print("is 'normals' a primvar?",
      UsdGeom.Primvar.IsPrimvar(mesh.GetNormalsAttr()))
```

**Expected output**
```text
default normals interpolation: vertex
using primvars:normals [(0.0, 0.0, 1.0), (0.0, 0.0, 1.0), (0.0, 0.0, 1.0), (0.0, 0.0, 1.0)]
is 'normals' a primvar? False
```

The `if` reproduces the documented rule (USD itself has no "effective normals" query; renderers apply it in Hydra). `ComputeFlattened()` expands the indexed primvar to one value per corner.

### 9. Real-world use case
A game-engine import pipeline reads `primvars:normals` (indexed, faceVarying) so hard edges survive and the data stays compact. A film studio exporting subdivision characters omits normals entirely, because the renderer derives them from the limit surface.

### 10. Common mistakes
> [!MISTAKE] Fixing shading by editing `normals` while an old `primvars:normals` is still authored. Nothing changes. Fix: edit or block `primvars:normals`, which has precedence.

> [!MISTAKE] Authoring normals on a `catmullClark` mesh and wondering why they are ignored. Fix: set `subdivisionScheme = "none"`.

> [!MISTAKE] Writing one normal per point (`vertex`) for a hard-edged cube. Edges look soft. Fix: use `faceVarying`.

### 11. Exam traps
> [!TRAP] "`normals` is a primvar because it has interpolation." No: only `primvars:`-namespaced attributes are primvars. `UsdGeom.Primvar.IsPrimvar(normalsAttr)` is `False`.

> [!TRAP] When both are present, the answer "`normals` wins because it is the schema attribute" is wrong; `primvars:normals` wins.

### 12. Practice questions
1. A mesh authors both `normals` and `primvars:normals`. Which does a conforming renderer use?
2. Which interpolation lets a cube have sharp edges with authored normals? A. `constant` · B. `uniform` · C. `vertex` · D. `faceVarying`
3. Why might authored normals be ignored on a mesh that has no `subdivisionScheme` opinion?

**Answers**
1. `primvars:normals` (documented precedence).
2. **D.** One normal per face-corner lets corners shared by two faces point in different directions. `uniform` (one per face) can also look flat but cannot express a mix of soft and hard edges.
3. The fallback is `catmullClark`, so the mesh is subdivided and normals are computed by subdivision.

### 13. Exam takeaways
> [!KEY]
> - `normals` (PointBased attribute, not a primvar) vs. `primvars:normals` (real, indexable primvar).
> - Both authored → **`primvars:normals` wins**.
> - Normals are only meaningful when `subdivisionScheme = "none"`.
> - Hard edges = `faceVarying` normals.

---

## 39.5 `GeomSubset`

### 1. What is it?
A **`GeomSubset`** is a child prim of a geometry prim that lists the indices of some of its elements (usually faces). It lets you name parts of one mesh, for example "the glass faces" of a car body.

### 2. Why do we need it?
Exporters often merge many parts into one mesh for speed, but different faces need different materials. Without subsets you would have to split the mesh into many prims.

### 3. Beginner explanation
Think of a colouring book page with numbered regions. The page is the mesh. A subset is a sticky note saying "regions 3, 4, and 9 are sky": you can now colour all sky regions blue without cutting the page apart.

*Where the analogy breaks:* subsets of one **family** can be required not to overlap (one region cannot be both "sky" and "sea"), depending on the family type.

### 4. Technical explanation
- Prim type `GeomSubset` (`UsdGeom.Subset`), defined as a **direct child** of the geometry prim.
- Attributes: `uniform token elementType` (fallback `face`; also `point`, `edge`, `segment`, `tetrahedron` in 26.08), `int[] indices`, `uniform token familyName`.
- A **family** is the set of subsets sharing a `familyName`. The parent stores the family type as `uniform token subsetFamily:<familyName>:familyType`: `unrestricted` (default), `nonOverlapping`, or `partition` (every element in exactly one subset).
- Create: `UsdGeom.Subset.CreateGeomSubset(geom, name, elementType, indices, familyName="", familyType="")`. Query: `UsdGeom.Subset.GetGeomSubsets(geom, elementType, familyName)`, `GetUnassignedIndices(subsets, elementCount)`, `ValidateFamily(geom, elementType, familyName)`.
- For materials the family name is **`materialBind`**. `UsdShade.MaterialBindingAPI(mesh).CreateMaterialBindSubset(name, indices)` creates such a subset and sets the family type to `nonOverlapping` (verified). Binding to subsets is covered in Chapter 40.6.

### 5. Mental model

```text
Mesh "Body"   (faces 0..5)    subsetFamily:materialBind:familyType = "nonOverlapping"
 ├── GeomSubset "paint"  familyName="materialBind"  indices=[0,1,2,3]
 └── GeomSubset "glass"  familyName="materialBind"  indices=[4,5]
```

### 6. Simple example
A mesh with 2 faces. Subset `left` = face 0, subset `right` = face 1, both in family `materialBind`. Unassigned faces: none.

### 7. USDA example

```usda
#usda 1.0

def Mesh "Body"
{
    int[] faceVertexCounts = [4, 4]
    int[] faceVertexIndices = [0, 1, 4, 3, 1, 2, 5, 4]
    point3f[] points = [(0, 0, 0), (1, 0, 0), (2, 0, 0),
                        (0, 1, 0), (1, 1, 0), (2, 1, 0)]
    uniform token subdivisionScheme = "none"
    uniform token subsetFamily:materialBind:familyType = "nonOverlapping"

    def GeomSubset "paint"
    {
        uniform token elementType = "face"
        uniform token familyName = "materialBind"
        int[] indices = [0]
    }

    def GeomSubset "glass"
    {
        uniform token elementType = "face"
        uniform token familyName = "materialBind"
        int[] indices = [1]
    }
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom, UsdShade

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Body")
mesh.CreatePointsAttr([(0, 0, 0), (1, 0, 0), (2, 0, 0),
                       (0, 1, 0), (1, 1, 0), (2, 1, 0)])
mesh.CreateFaceVertexCountsAttr([4, 4])
mesh.CreateFaceVertexIndicesAttr([0, 1, 4, 3, 1, 2, 5, 4])

paint = UsdGeom.Subset.CreateGeomSubset(
    mesh, "paint", UsdGeom.Tokens.face, [0], "materialBind")
print("after CreateGeomSubset:",
      UsdGeom.Subset.GetFamilyType(mesh, "materialBind"))

glass = UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).CreateMaterialBindSubset(
    "glass", [1])
print("after CreateMaterialBindSubset:",
      UsdGeom.Subset.GetFamilyType(mesh, "materialBind"))

subsets = UsdGeom.Subset.GetGeomSubsets(mesh, "face", "materialBind")
for s in subsets:
    print(s.GetPrim().GetName(), s.GetElementTypeAttr().Get(),
          list(s.GetIndicesAttr().Get()))
print("unassigned:", list(UsdGeom.Subset.GetUnassignedIndices(subsets, 2)))
print("valid family:", UsdGeom.Subset.ValidateFamily(mesh, "face", "materialBind"))
```

**Expected output**
```text
after CreateGeomSubset: unrestricted
after CreateMaterialBindSubset: nonOverlapping
paint face [0]
glass face [1]
unassigned: []
valid family: (True, '')
```

### 9. Real-world use case
An automotive configurator exports each car body as one mesh with `materialBind` subsets for paint, chrome, glass, and rubber. Swapping the paint material changes one binding, and the mesh stays a single draw call.

### 10. Common mistakes
> [!MISTAKE] Putting the GeomSubset somewhere other than directly under its mesh. It is not found. Fix: make it a direct child.

> [!MISTAKE] Misspelling the family (`"material"`, `"materialBinding"`). Material binding to subsets ignores it. Fix: use `"materialBind"`, or `CreateMaterialBindSubset`.

> [!MISTAKE] Leaving faces outside every subset and expecting them to be unshaded. They get the mesh's own binding. Check with `GetUnassignedIndices`.

### 11. Exam traps
> [!TRAP] The family name for material subsets is `materialBind`, not the material's name.

> [!TRAP] The fallback `elementType` is `face`. The family type lives on the **parent** mesh (`subsetFamily:<name>:familyType`), not on the subset.

### 12. Practice questions
1. Which `familyName` must a subset have to receive a material binding?
2. Select two. Which statements about `GeomSubset` are true? A. It must be a direct child of the geometry · B. Its `indices` refer to faces when `elementType = "face"` · C. It must be referenced from a separate layer · D. It replaces the mesh's points
3. What does `GetUnassignedIndices(subsets, 6)` return if the subsets cover faces 0–3?

**Answers**
1. `materialBind`.
2. **A, B.** Subsets live in the same namespace as children and index into the parent's elements; they do not hold geometry.
3. `[4, 5]`.

### 13. Exam takeaways
> [!KEY]
> - `GeomSubset` = direct child; `elementType` (fallback `face`), `indices`, `familyName`.
> - Material subsets: `familyName = "materialBind"`; family type stored on the mesh.
> - Create with `UsdGeom.Subset.CreateGeomSubset` or `MaterialBindingAPI.CreateMaterialBindSubset` (sets `nonOverlapping`).

---

## 39.6 Visibility and purpose

### 1. What is it?
**`visibility`** hides a prim and everything under it. **`purpose`** labels a prim as `default`, `render`, `proxy`, or `guide`, so a renderer or viewer can choose which categories to draw. Both come from **`UsdGeom.Imageable`**.

### 2. Why do we need it?
Scenes contain things that should not always appear: hidden props, light-weight stand-ins for the viewport, heavy final geometry, and helper curves for riggers. Deleting them would destroy data; visibility and purpose switch them off non-destructively.

### 3. Beginner explanation
Visibility is a light switch for a whole room: switch off the room and every lamp in it goes dark. Purpose is a label on each lamp: "work light", "display lamp", "night light". The building manager decides which labels are on tonight.

*Where the analogy breaks:* a lamp inside a dark room cannot be switched on by itself in USD; `MakeVisible()` has to change the room too.

### 4. Technical explanation
- `token visibility` — `inherited` (fallback) or `invisible`. **Animatable.** `invisible` on a prim hides all its descendants regardless of their own opinion. `ComputeVisibility(time)` returns the effective value.
- `MakeInvisible()` authors `invisible`. `MakeVisible()` on a prim under an invisible ancestor sets the ancestor to `inherited` and **makes the siblings invisible** to keep them hidden (verified).
- `uniform token purpose` — `default` (fallback), `render` (final quality, for renders), `proxy` (light stand-in, for interactive viewports), `guide` (helpers, usually never rendered). **Not animatable.**
- Purpose **inherits**: a prim with no authored purpose takes its nearest ancestor's authored purpose. `ComputePurpose()` returns the effective value; `GetOrderedPurposeTokens()` lists all four.
- `proxyPrim` relationship on a `render` prim can point to its `proxy` stand-in.
- Viewers typically show `default` + `proxy`; final renders show `default` + `render`. `UsdGeom.BBoxCache` takes the purposes to include (Chapter 44.5).

### 5. Mental model

```text
/Tree  (default)
 ├── Hi_Res   purpose = "render"   ← final frames only
 ├── Lo_Res   purpose = "proxy"    ← viewport only
 └── Pivot    purpose = "guide"    ← helpers, off by default
visibility = "invisible" on /Tree  ─► nothing under /Tree is drawn
```

### 6. Simple example
Tree with a render mesh and a proxy mesh. In usdview (proxy on) you see the light mesh; in the final render you see the full one. Set `/Tree` invisible: neither appears.

### 7. USDA example

```usda
#usda 1.0

def Xform "Tree"
{
    def Mesh "Hi_Res"
    {
        uniform token purpose = "render"
        rel proxyPrim = </Tree/Lo_Res>
    }

    def Mesh "Lo_Res"
    {
        uniform token purpose = "proxy"
    }

    def Xform "Helpers"
    {
        uniform token purpose = "guide"

        def BasisCurves "PivotAxis"
        {
        }
    }

    def Mesh "Leaves"
    {
        token visibility = "invisible"
    }
}
```

- `PivotAxis` has no purpose of its own but inherits `guide` from `Helpers`.
- `Leaves` is hidden; `visibility` could also be time-sampled to make leaves fall.

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
tree = UsdGeom.Xform.Define(stage, "/Tree")
helpers = UsdGeom.Xform.Define(stage, "/Tree/Helpers")
axis = UsdGeom.BasisCurves.Define(stage, "/Tree/Helpers/Axis")
a = UsdGeom.Mesh.Define(stage, "/Tree/A")
b = UsdGeom.Mesh.Define(stage, "/Tree/B")

print("fallbacks:", tree.GetVisibilityAttr().Get(), tree.GetPurposeAttr().Get())
helpers.CreatePurposeAttr(UsdGeom.Tokens.guide)
print("Axis purpose (inherited):", axis.ComputePurpose())
print("all purposes:", list(tree.GetOrderedPurposeTokens()))

tree.MakeInvisible()
print("A effective:", a.ComputeVisibility(),
      "| A authored:", a.GetVisibilityAttr().Get())

a.MakeVisible()
print("after A.MakeVisible():")
for x in (tree, a, b):
    print(" ", x.GetPath(), "authored", x.GetVisibilityAttr().Get(),
          "effective", x.ComputeVisibility())
```

**Expected output**
```text
fallbacks: inherited default
Axis purpose (inherited): guide
all purposes: ['default', 'render', 'proxy', 'guide']
A effective: invisible | A authored: inherited
after A.MakeVisible():
  /Tree authored inherited effective inherited
  /Tree/A authored inherited effective inherited
  /Tree/B authored invisible effective invisible
```

`MakeVisible()` on `A` had to flip `/Tree` back to `inherited`, then hid sibling `B` so it stays invisible.

### 9. Real-world use case
A forest of 10,000 trees uses `proxy` cards in the layout viewport and `render` meshes on the render farm; artists never wait for full trees to draw. Rigging controls and collision shapes are `guide`, so they never leak into final frames. Shot animators animate `visibility` to pop props in and out.

### 10. Common mistakes
> [!MISTAKE] Setting a child to `"visible"`. That token does not exist; the values are `inherited` and `invisible`. Fix: use `MakeVisible()`.

> [!MISTAKE] Trying to time-sample `purpose`. It is `uniform`. Fix: animate `visibility` instead, or use variants.

> [!MISTAKE] Tagging the root of an asset `proxy` and wondering why the final render is empty. Purpose inherits to every child. Fix: tag only the proxy branch.

### 11. Exam traps
> [!TRAP] `visibility` is animatable; `purpose` is not.

> [!TRAP] A child cannot be "more visible" than an invisible parent. Effective visibility is invisible if any ancestor is invisible.

> [!TRAP] Purpose `default` means "always drawn", not "unknown". Both render and viewport include it.

### 12. Practice questions
1. Select two. Which are valid `purpose` values? A. `render` · B. `preview` · C. `guide` · D. `hidden`
2. `/A` is invisible; `/A/B` authors `visibility = "inherited"`. What does `ComputeVisibility()` return for `/A/B`?
3. Which purpose would you give to a lightweight stand-in shown only in interactive viewports?

**Answers**
1. **A, C.** The four values are `default`, `render`, `proxy`, `guide`. `preview` is a *material* purpose (Chapter 40.6).
2. `invisible` — an invisible ancestor wins.
3. `proxy`.

### 13. Exam takeaways
> [!KEY]
> - `visibility`: `inherited` | `invisible`; animatable; invisible ancestor hides all descendants.
> - `purpose`: `default` | `render` | `proxy` | `guide`; uniform; inherits down namespace.
> - `MakeVisible()` edits ancestors and siblings to reveal one prim.
> - Viewports usually draw default + proxy; renders draw default + render.

---

## 39.7 Cameras

### 1. What is it?
A **`UsdGeom.Camera`** prim describes a physical camera: lens (focal length), film back (apertures), clipping planes, and depth-of-field settings. Its transform places it in the scene. `camera.GetCamera(time)` converts it to **`Gf.Camera`**, a math object for computing fields of view and frustums.

### 2. Why do we need it?
Layout, animation, and lighting must all render from the same shot camera. Storing it as scene description means every application and renderer uses the exact same lens and framing.

### 3. Beginner explanation
A camera prim is the spec sheet of a real camera taped to a tripod. The spec sheet says "35 mm lens, full-frame sensor"; the tripod's position is the prim's xformOps.

*Where the analogy breaks:* USD measures lens and sensor in **tenths of a scene unit**, not always millimetres.

### 4. Technical explanation
- Attributes and fallbacks (verified on 26.08): `projection = "perspective"` (or `orthographic`), `focalLength = 50`, `horizontalAperture = 20.955`, `verticalAperture = 15.2908`, `clippingRange = (1, 1000000)` (near, far in scene units), `focusDistance = 0`, `fStop = 0` (0 means no depth of field).
- Units: `focalLength` and apertures are in **tenths of a scene unit**. With `metersPerUnit = 0.01` (centimetres), that is millimetres, matching real lenses.
- In its own space, a camera looks down **−Z** with **+Y** up. Point it with normal xformOps.
- `UsdGeom.Camera(prim).GetCamera(time)` → `Gf.Camera` with `focalLength`, `horizontalAperture`, `clippingRange`, `transform`, `projection`, `frustum`, and `GetFieldOfView(Gf.Camera.FOVHorizontal)`.
- `camera.SetFromCamera(gfCamera, time)` writes a `Gf.Camera` back.
- Camera attributes are animatable (focus pulls, zooms).

### 5. Mental model

```text
          +Y
           │      clippingRange: near ───────────── far
           │       ┌──────────────────────────────────┐
  camera ●─┼──────►│  view direction = local −Z        │
           │       └──────────────────────────────────┘
   FOV ≈ 2·atan( horizontalAperture / (2·focalLength) )
```

### 6. Simple example
A 35 mm lens on the default 20.955 aperture gives a horizontal field of view of about 33.3°. Moving the camera to z = 10 and leaving no rotation makes it look back at the origin.

### 7. USDA example

```usda
#usda 1.0
(
    metersPerUnit = 0.01
    upAxis = "Y"
)

def Camera "ShotCam"
{
    float focalLength = 35
    float horizontalAperture = 36
    float verticalAperture = 24
    float2 clippingRange = (0.1, 10000)
    float focusDistance = 500
    float fStop = 2.8
    token projection = "perspective"
    double3 xformOp:translate = (0, 150, 800)
    uniform token[] xformOpOrder = ["xformOp:translate"]
}
```

- With centimetre units, 35 and 36 read as 35 mm and 36 mm (full-frame).
- `fStop = 2.8` with `focusDistance = 500` (5 m) enables depth of field.
- The camera sits 1.5 m up and 8 m back and looks down −Z toward the origin.

### 8. Python example

```python
from pxr import Usd, UsdGeom, Gf

stage = Usd.Stage.CreateInMemory()
cam = UsdGeom.Camera.Define(stage, "/ShotCam")
print("fallback focal/hAperture/clip:", cam.GetFocalLengthAttr().Get(),
      round(cam.GetHorizontalApertureAttr().Get(), 3),
      cam.GetClippingRangeAttr().Get())

cam.AddTranslateOp().Set(Gf.Vec3d(0, 0, 10))
cam.GetFocalLengthAttr().Set(35.0)
cam.GetClippingRangeAttr().Set(Gf.Vec2f(0.1, 1000))

gf = cam.GetCamera(Usd.TimeCode.Default())
print(type(gf).__name__, gf.projection)
print("focal", gf.focalLength, "clip", gf.clippingRange)
print("hFOV", round(gf.GetFieldOfView(Gf.Camera.FOVHorizontal), 2))
print("position", gf.transform.ExtractTranslation())
print("view dir", Gf.Vec3d(*[round(v, 6) + 0.0 for v in
                              gf.frustum.ComputeViewDirection()]))
```

**Expected output**
```text
fallback focal/hAperture/clip: 50.0 20.955 (1, 1000000)
Camera Gf.Camera.Perspective
focal 35.0 clip [0.1...1000]
hFOV 33.33
position (0, 0, 10)
view dir (0, 0, -1)
```

### 9. Real-world use case
In film, layout publishes `ShotCam` to a camera layer; animation, lighting, and comp all reference it, so a focal-length change propagates to every department. In manufacturing, inspection cameras in a digital twin are stored as Camera prims so simulated images match the real cameras' lenses.

### 10. Common mistakes
> [!MISTAKE] Setting `focalLength = 0.035` because "35 mm is 0.035 m". Units are tenths of a scene unit. Fix: in a centimetre scene use 35.

> [!MISTAKE] A tiny object disappears close to the camera. The near clip (fallback 1 unit) is too far. Fix: lower `clippingRange[0]`.

> [!MISTAKE] Rotating the camera expecting it to look down +Z. It looks down local −Z.

### 11. Exam traps
> [!TRAP] `GetCamera()` returns a `Gf.Camera`, not a `UsdGeom.Camera`. Questions may ask which type gives `GetFieldOfView`.

> [!TRAP] `clippingRange` is in scene units; focal length and aperture are in tenths of a scene unit. Mixing them is a classic distractor.

### 12. Practice questions
1. What does `UsdGeom.Camera(prim).GetCamera(t)` return?
2. Which local axis does a USD camera look along? A. +Z · B. −Z · C. +Y · D. −X
3. What is the fallback `clippingRange`?

**Answers**
1. A `Gf.Camera` object for time `t`.
2. **B.**
3. `(1, 1000000)`.

### 13. Exam takeaways
> [!KEY]
> - `UsdGeom.Camera`: `focalLength` (50), `horizontalAperture` (20.955), `clippingRange` (1, 1e6), `projection`.
> - Lens/aperture units = tenths of a scene unit; clipping = scene units.
> - Looks down local −Z, +Y up; placed with xformOps.
> - `GetCamera(time)` → `Gf.Camera` (FOV, frustum).

---

## Chapter lab(s)

**Lab 33 — Xforms, XformCache, and cameras** (★★☆, Obj 8.x). You build a small rig of nested Xforms, predict world positions from `xformOpOrder` before checking them with `XformCache`, add a `resetXformStack` child, and create a shot camera whose field of view you compute through `Gf.Camera`.

**Lab 11 — Build a mesh from scratch and compute its extent** (Ch 13, 39; Obj 5.6) also exercises §39.3: author `points`/`faceVertexCounts`/`faceVertexIndices`, then keep `extent` in sync.

## USDA reading exercise(s)

**Exercise 39-A.** Where does the point (1, 0, 0) of `Arm` end up in world space?

```usda
#usda 1.0

def Xform "Base"
{
    double3 xformOp:translate = (0, 5, 0)
    uniform token[] xformOpOrder = ["xformOp:translate"]

    def Xform "Arm"
    {
        double3 xformOp:translate = (2, 0, 0)
        float xformOp:rotateZ = 90
        float3 xformOp:scale = (3, 3, 3)
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateZ"]
    }
}
```

**Exercise 39-B.** Which normals does a renderer use for `Wall`, and why might your edit to `normals` have had no effect?

```usda
#usda 1.0

def Mesh "Wall"
{
    int[] faceVertexCounts = [4]
    int[] faceVertexIndices = [0, 1, 2, 3]
    point3f[] points = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    normal3f[] normals = [(0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1)]
}
```

**Exercise 39-C.** Is `/Set/Lamp/Bulb` drawn in a final render? In a viewport showing proxy?

```usda
#usda 1.0

def Xform "Set"
{
    def Xform "Lamp"
    {
        uniform token purpose = "proxy"

        def Mesh "Bulb"
        {
            token visibility = "inherited"
        }
    }
}
```

## Chapter review

### Summary
- xformOps are attributes; `xformOpOrder` chooses which apply. Read it right to left for a point.
- `XformCache(time).GetLocalToWorldTransform(prim)` gives world matrices efficiently; `!resetXformStack!` ignores ancestors.
- A Mesh = `points` + `faceVertexCounts` (per face) + `faceVertexIndices` (per corner).
- Fallbacks: `orientation = rightHanded`, `subdivisionScheme = catmullClark`, `doubleSided = false`.
- `primvars:normals` beats `normals`; normals only matter when `subdivisionScheme = "none"`.
- GeomSubsets name faces of one mesh; `familyName = "materialBind"` for materials.
- `visibility` (`inherited`/`invisible`) is animatable and prunes descendants; `purpose` is uniform and inherited.
- Cameras: lens/aperture in tenths of a scene unit, look down −Z, `GetCamera()` → `Gf.Camera`.

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| An `xformOp:*` attribute not in `xformOpOrder` | It has no effect |
| `["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]` | Scale first, rotate, then translate |
| `"!resetXformStack!"` | Ignore parent transforms |
| Many world matrices needed | `UsdGeom.XformCache` |
| Melted/rounded hard-surface mesh | `subdivisionScheme` still `catmullClark` → set `none` |
| Normals edits ignored | `primvars:normals` authored, or mesh is subdivided |
| `familyName = "materialBind"` | Per-face material binding via GeomSubset |
| A child shows `inherited` but is hidden | An ancestor is `invisible` |
| `purpose = "proxy"` | Viewport-only stand-in |
| `GetCamera()` | Returns `Gf.Camera` |

### Review questions

**Q39.1** · Obj 8.1 · Medium · Single choice
A prim's `xformOpOrder` is `["xformOp:rotateZ", "xformOp:translate"]` with rotateZ = 90 and translate = (1, 0, 0). Where does the origin (0, 0, 0) go?
A. (1, 0, 0) · B. (0, 1, 0) · C. (0, 0, 0) · D. (−1, 0, 0)

**Q39.2** · Obj 8.1 · Easy · Single choice
Which Python call computes a prim's world matrix with caching?
A. `UsdGeom.Xformable.GetLocalTransformation` · B. `UsdGeom.XformCache().GetLocalToWorldTransform` · C. `Gf.Matrix4d.GetInverse` · D. `Usd.Prim.GetTransform`

**Q39.3** · Obj 8.1 · Medium · Select two.
Which statements about `resetXformStack` are true?
A. It is written as the first entry of `xformOpOrder` · B. It is a boolean attribute named `resetXformStack` · C. It makes the prim ignore ancestor transforms · D. It resets the prim's own ops to identity

**Q39.4** · Obj 5.5 · Medium · Single choice
An imported CAD bracket looks soft and rounded, though its triangles are correct. What is the most likely cause?
A. `orientation = "leftHanded"` · B. Missing `extent` · C. `subdivisionScheme` is unauthored · D. `doubleSided = false`

**Q39.5** · Obj 8.1 · Easy · Single choice
`faceVertexCounts = [4, 4, 3]`. How long must `faceVertexIndices` be?
A. 3 · B. 4 · C. 11 · D. 12

**Q39.6** · Obj 5.5 · Medium · Single choice
A mesh authors `normals` (pointing +Y) and `primvars:normals` (pointing −Y) and has `subdivisionScheme = "none"`. Which way does lighting treat the surface as facing?
A. +Y · B. −Y · C. Average of both · D. Computed from winding, both ignored

**Q39.7** · Obj 8.3 · Medium · Select two.
Which are required for a `GeomSubset` to receive its own material binding?
A. `familyName = "materialBind"` · B. The subset is a direct child of the mesh · C. `elementType = "point"` · D. The subset is referenced from a material layer

**Q39.8** · Obj 5.5 · Medium · Single choice
`/Car` is `invisible`. You call `UsdGeom.Imageable(wheel).MakeVisible()` on `/Car/Wheel`. Which edit does USD make?
A. Authors `visibility = "visible"` on Wheel · B. Sets `/Car` to `inherited` and makes Wheel's siblings `invisible` · C. Nothing, an error is raised · D. Removes `/Car` from the stage

**Q39.9** · Obj 5.5 · Easy · Single choice
Which attribute can be time-sampled?
A. `purpose` · B. `xformOpOrder` · C. `visibility` · D. `subdivisionScheme`

**Q39.10** · Obj 8.1 · Easy · Single choice
What does `UsdGeom.Camera.GetCamera(time)` return?
A. `UsdGeom.Camera` · B. `Gf.Frustum` · C. `Gf.Camera` · D. `Gf.Matrix4d`

**Q39.11** · Obj 8.1 · Medium · USDA reading
What is the world position of `/A/B`'s origin?

```usda
#usda 1.0

def Xform "A"
{
    double3 xformOp:translate = (0, 0, 4)
    uniform token[] xformOpOrder = ["xformOp:translate"]

    def Xform "B"
    {
        double3 xformOp:translate = (1, 0, 0)
        double3 xformOp:translate:extra = (9, 9, 9)
        uniform token[] xformOpOrder = ["xformOp:translate"]
    }
}
```

A. (1, 0, 4) · B. (10, 9, 13) · C. (1, 0, 0) · D. (0, 0, 4)

**Q39.12** · Obj 8.1 · Easy · Single choice
In a scene with `metersPerUnit = 0.01`, which `focalLength` value describes a 50 mm lens?
A. 0.05 · B. 5 · C. 50 · D. 500

### Answers

**Q39.1 — B.** Translate is last, so it applies first: (1, 0, 0); rotating 90° about Z gives (0, 1, 0). A ignores the rotation. Review: §39.1.

**Q39.2 — B.** `XformCache` stores ancestor results. A gives the local matrix; C and D are not world-transform APIs. Review: §39.2.

**Q39.3 — A, C.** The marker `!resetXformStack!` goes first in `xformOpOrder` and discards ancestors. There is no such attribute (B); the prim's own ops still apply (D). Review: §39.2.

**Q39.4 — C.** The fallback is `catmullClark`, which smooths the mesh. Orientation affects facing, extent affects culling, doubleSided affects back faces. Review: §39.3.

**Q39.5 — C.** 4 + 4 + 3 = 11. Review: §39.3.

**Q39.6 — B.** `primvars:normals` has precedence over `normals`. Review: §39.4.

**Q39.7 — A, B.** Material subsets use family `materialBind` and must be direct children. `point` subsets do not carry face materials; no reference is needed. Review: §39.5 and §40.6.

**Q39.8 — B.** `MakeVisible()` makes ancestors `inherited` and hides siblings to preserve their look. `"visible"` is not a valid token. Review: §39.6.

**Q39.9 — C.** `visibility` is a varying token. The others are `uniform`. Review: §39.6.

**Q39.10 — C.** Review: §39.7.

**Q39.11 — A.** Only `xformOp:translate` is listed, so `B` is at (1, 0, 0) in `A`'s space, (1, 0, 4) in the world. The `:extra` op is ignored. Review: §39.1–39.2.

**Q39.12 — C.** Units are tenths of a scene unit; with centimetres that is millimetres. Review: §39.7.

### USDA exercise answers

**39-A — (2, 6, 0).** Scale is authored but not listed, so it is ignored. RotateZ applies first: (1, 0, 0) → (0, 1, 0). Translate (2, 0, 0) → (2, 1, 0). Parent `Base` adds (0, 5, 0) → **(2, 6, 0)**.

**39-B — Normals computed by subdivision, not the authored ones.** `subdivisionScheme` is unauthored, so it is `catmullClark`; the mesh is subdivided and its normals come from subdivision. Set `subdivisionScheme = "none"` to make `normals` count (and check no `primvars:normals` exists, which would win).

**39-C — Final render: no. Proxy viewport: yes.** `Bulb` has no purpose of its own and inherits `proxy` from `Lamp`. Renders skip proxy; viewports showing proxy draw it. Its visibility is `inherited` and no ancestor is invisible.

## Further reading

- [S06] OpenUSD API — UsdGeomXformable, UsdGeomXformCache, UsdGeomMesh, UsdGeomPointBased, UsdGeomSubset, UsdGeomImageable, UsdGeomCamera: https://openusd.org/release/api/index.html
- [S05] OpenUSD tutorial "Transformations, Time-sampled Animation, and Layer Offsets": https://openusd.org/release/tut_usd_tutorials.html
- [S04] OpenUSD Glossary (Gprim, purpose, primvar): https://openusd.org/release/glossary.html
- [S14] NVIDIA Learn OpenUSD: https://docs.nvidia.com/learn-openusd/latest/index.html
