# Chapter 13 — Built-in Schemas, Xforms, and Extents

> **Exam domain:** Data Modeling (13%) and Debugging (11%) · **Objectives:** 5.5, 5.6, 6.4
> **Study day:** 4 · **Est. time:** 75 min
> **Prerequisites:** Chapters 6, 9, 11

## Learning goals

- Place Mesh/Cube/Xform in the **Imageable / Xformable / Boundable / Gprim** chain.
- Explain **extent** and why it must stay in sync with `points` (Obj 5.6).
- Call `ComputeExtentFromPlugins` and set the extent attribute.
- Use `UsdGeom.BBoxCache` for world bounds.
- List common causes of **unexpected visual results** (Obj 5.5 / 6.4).

## Key terms

| Term | One-line definition |
|------|---------------------|
| Imageable | Can be visualized; has purpose and visibility |
| Xformable | Can hold xformOps |
| Boundable | Has an `extent` (local-space AABB) |
| Gprim | Geometric primitive (Mesh, Cube, Sphere, …) |
| extent | Two `float3`s: min and max corner in local space |
| BBoxCache | Cached computer of world/local bounds |

---

## 13.1 Imageable, Xformable, Boundable, Gprim

### 1. What is it?

UsdGeom's typed-schema ladder: most drawables are **Gprims**, which are **Boundable**, **Xformable**, and **Imageable**.

### 2. Why do we need it?

Obj 8.x / 5.5: visibility and purpose live on Imageable. Transforms on Xformable. Extent on Boundable. Knowing `IsA` tells you which APIs are legal.

### 3. Beginner explanation

Imageable = can be seen (or hidden). Xformable = can be moved. Boundable = has a box. Gprim = is a shape.

Where the analogy breaks: **Camera** is Xformable/Imageable but not a Gprim. **Scope** groups without a local transform stack like Xform. **Xform** is Xformable but not Boundable (it has no extent of its own).

### 4. Technical explanation

Verified: `UsdGeom.Mesh` and `UsdGeom.Cube` are Gprim, Boundable, Xformable, Imageable.

Imageable attributes:

- `visibility` fallback **`inherited`**
- `purpose` fallback **`default`** (also `render`, `proxy`, `guide`)

Xformable: `xformOp:*` and `xformOpOrder` (Ch 39).

Boundable: `extent` (`float3[]` of length 2).

### 5. Mental model

```text
Imageable
  ├── Xformable
  │     ├── Boundable → Gprim → Mesh, Cube, Sphere, ...
  │     └── Camera
  └── (Scope is imageable grouping)
```

### 6. Simple example

A bounding-box tool should `IsA(UsdGeom.Boundable)`, not hard-code Mesh.

### 7. USDA example

```usda
#usda 1.0

def Cube "Box"
{
    double size = 2
    token purpose = "default"
    token visibility = "inherited"
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
cube = UsdGeom.Cube.Define(stage, "/Box").GetPrim()
print("Gprim", cube.IsA(UsdGeom.Gprim))
print("Boundable", cube.IsA(UsdGeom.Boundable))
print("Xformable", cube.IsA(UsdGeom.Xformable))
print("Imageable", cube.IsA(UsdGeom.Imageable))
img = UsdGeom.Imageable(cube)
print("visibility", img.GetVisibilityAttr().Get())
print("purpose", img.GetPurposeAttr().Get())
```

**Expected output**

```text
Gprim True
Boundable True
Xformable True
Imageable True
visibility inherited
purpose default
```

### 9. Real-world use case

A "hide guides" button sets purpose filters on BBoxCache / Hydra, not deletion.

### 10. Common mistakes

> [!MISTAKE] Calling `GetExtentAttr()` on an Xform group. Groups are not Boundable; use BBoxCache to union children.

### 11. Exam traps

> [!TRAP] "Camera is a Gprim." It is not.

### 12. Practice questions

**DM-028** · Difficulty: Easy · Type: Single choice

`extent` is an attribute of:

A. Any prim  
B. Boundable schemas (Gprims, etc.)  
C. Kind metadata  
D. Only lights  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Mesh/Cube: Imageable + Xformable + Boundable + Gprim.
> - visibility fallback `inherited`; purpose fallback `default`.

---

## 13.2 The extent attribute (Obj 5.6)

### 1. What is it?

**extent** is a `float3[]` of two corners — min and max of the prim's geometry in **local** space.

### 2. Why do we need it?

Hydra, instancing, draw modes, and frustum tools use extent (and extentsHint) as a **fast box**. If you move `points` and leave extent stale, you get clipped or missing draws (Obj 5.5, 5.6).

### 3. Beginner explanation

extent is the cardboard box around the object, measured before parent transforms.

Where the analogy breaks: Cube/Sphere schemas can **fallback** a correct extent from `size`/`radius` even when extent is not authored. A **Mesh** does not: `Get()` is `None` until you author it. Verified.

### 4. Technical explanation

- Cube `size` fallback 2.0 → extent fallback `[(-1,-1,-1), (1,1,1)]` even with `HasAuthoredValue() False`.
- Mesh with points set: `GetExtentAttr().Get()` is **None** until `Set`.
- After updating points you **must** recompute and `Set` extent (Obj 5.6).
- Type: `float3[]`, length 2, not `point3f[]` (common type trap).

### 5. Mental model

```text
extent[0] = min xyz
extent[1] = max xyz
local space, axis-aligned
```

### 6. Simple example

Triangle points (0,0,0), (2,0,0), (0,3,0) → extent [(0,0,0), (2,3,0)].

### 7. USDA example

```usda
#usda 1.0

def Mesh "Tri"
{
    int[] faceVertexCounts = [3]
    int[] faceVertexIndices = [0, 1, 2]
    point3f[] points = [(0, 0, 0), (2, 0, 0), (0, 3, 0)]
    float3[] extent = [(0, 0, 0), (2, 3, 0)]
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Tri")
mesh.GetPointsAttr().Set([(0, 0, 0), (2, 0, 0), (0, 3, 0)])
mesh.GetFaceVertexCountsAttr().Set([3])
mesh.GetFaceVertexIndicesAttr().Set([0, 1, 2])
print("authored before:", mesh.GetExtentAttr().HasAuthoredValue(), mesh.GetExtentAttr().Get())
computed = UsdGeom.Boundable.ComputeExtentFromPlugins(
    UsdGeom.Boundable(mesh.GetPrim()), Usd.TimeCode.Default()
)
print("computed:", computed)
mesh.GetExtentAttr().Set(computed)
print("authored after:", mesh.GetExtentAttr().Get())
```

**Expected output**

```text
authored before: False None
computed: [(0, 0, 0), (2, 3, 0)]
authored after: [(0, 0, 0), (2, 3, 0)]
```

### 9. Real-world use case

A deformer writes new `points` at each frame and must write `extent` time samples too, or the bounding box used for loading/culling is wrong.

### 10. Common mistakes

> [!MISTAKE] Updating points in a loop and never touching extent. Obj 5.6 is written for this.

### 11. Exam traps

> [!TRAP] "extent is in world space." Local. Parent xforms are applied by BBoxCache.

### 12. Practice questions

**DM-029** · Obj 5.6 · Difficulty: Medium · Type: Single choice

You change a Mesh's `points`. You should also:

A. Delete the prim  
B. Update `extent` (and time samples if points are sampled)  
C. Change `kind` to subcomponent  
D. Convert the file to USDZ  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Mesh extent is not automatic. Compute and author it after points change.
> - Cube/Sphere may fallback; do not generalize that to Mesh.

---

## 13.3 ComputeExtent and ComputeExtentFromPlugins

### 1. What is it?

APIs that **calculate** a bounding box from schema data. `ComputeExtentFromPlugins` dispatches to the right Gprim plugin (Mesh, Cube, Sphere, …).

### 2. Why do we need it?

You should not hand-write min/max loops in every exporter. Obj 5.6: after editing points, compute then set.

### 3. Beginner explanation

Ask the schema: "given these points (or this size), what box do you occupy?"

### 4. Technical explanation

- `UsdGeom.Boundable.ComputeExtentFromPlugins(boundable, timeCode)` → `Vt.Vec3fArray` of two vectors, or empty/failure if it cannot.
- There is also `ComputeExtent` on some concrete schemas.
- Pass the **TimeCode** that matches the points you care about (Default vs frame).
- `UsdGeom.ModelAPI.GetExtentsHint` — a model-level hint for unloaded payloads (Ch 26).

### 5. Mental model

Compute → then `GetExtentAttr().Set(...)`. Computing does not author by itself.

### 6. Simple example

Cube: plugins return `[(-1,-1,-1),(1,1,1)]` for default size 2.

### 7. USDA example

Computation is runtime. The authored result is ordinary USDA `extent`.

```usda
#usda 1.0

def Cube "Box"
{
    double size = 2
    float3[] extent = [(-1, -1, -1), (1, 1, 1)]
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
cube = UsdGeom.Cube.Define(stage, "/Box")
print("size fallback:", cube.GetSizeAttr().Get())
print(
    "plugins:",
    UsdGeom.Boundable.ComputeExtentFromPlugins(
        UsdGeom.Boundable(cube.GetPrim()), Usd.TimeCode.Default()
    ),
)
```

**Expected output**

```text
size fallback: 2.0
plugins: [(-1, -1, -1), (1, 1, 1)]
```

### 9. Real-world use case

A USD exporter's last step: traverse Boundables, compute extent at Default and at sample times, author them.

### 10. Common mistakes

> [!MISTAKE] Computing at Default while points only exist as time samples — you get an empty/wrong box. Pass the frame.

### 11. Exam traps

> [!TRAP] "ComputeExtentFromPlugins writes the attribute." It returns values. You `Set`.

### 12. Practice questions

**DM-030** · Obj 5.6 · Difficulty: Medium · Type: Single choice

`ComputeExtentFromPlugins` by itself:

A. Saves a new USDC  
B. Returns a computed box; you still author `extent` if you want it stored  
C. Deletes points  
D. Sets kind  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Compute at the correct TimeCode, then Set.
> - Plugins know Cube vs Mesh vs Sphere.

---

## 13.4 UsdGeom.BBoxCache

### 1. What is it?

**BBoxCache** computes **world** (and local) bounds, applying transforms, purpose, visibility, and child unioning, with caching.

### 2. Why do we need it?

extent is local. Layout needs a box in the stage's world. Instancers and cameras use world bounds.

### 3. Beginner explanation

extent = box in object space. BBoxCache = box after every parent transform.

### 4. Technical explanation

```{.python .norun}
cache = UsdGeom.BBoxCache(timeCode, [UsdGeom.Tokens.default_])
cache.ComputeWorldBound(prim).GetRange()
```

- Second argument is the list of **purposes** to include.
- Reuse one cache when traversing many prims.
- Verified: triangle mesh world range `[(0,0,0)...(2,3,0)]` with identity xform.

### 5. Mental model

BBoxCache = extent + xform hierarchy + purpose filter.

### 6. Simple example

Frame-all-in-camera: union world bounds of selected prims.

### 7. USDA example

No USDA for the cache. The mesh it bounds:

```usda
#usda 1.0

def Mesh "Tri"
{
    point3f[] points = [(0, 0, 0), (2, 0, 0), (0, 3, 0)]
    int[] faceVertexCounts = [3]
    int[] faceVertexIndices = [0, 1, 2]
    float3[] extent = [(0, 0, 0), (2, 3, 0)]
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Tri")
mesh.GetPointsAttr().Set([(0, 0, 0), (2, 0, 0), (0, 3, 0)])
mesh.GetFaceVertexCountsAttr().Set([3])
mesh.GetFaceVertexIndicesAttr().Set([0, 1, 2])
computed = UsdGeom.Boundable.ComputeExtentFromPlugins(
    UsdGeom.Boundable(mesh.GetPrim()), Usd.TimeCode.Default()
)
mesh.GetExtentAttr().Set(computed)
cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default"])
print(cache.ComputeWorldBound(mesh.GetPrim()).GetRange())
```

**Expected output**

```text
[(0, 0, 0)...(2, 3, 0)]
```

### 9. Real-world use case

A set dresser snaps objects using world bounds, not local extent.

### 10. Common mistakes

> [!MISTAKE] Creating a new BBoxCache per prim in a 100k loop. Reuse it.

### 11. Exam traps

> [!TRAP] Passing purposes `["render"]` and wondering why `purpose=proxy` geometry is missing from the box.

### 12. Practice questions

**DM-031** · Difficulty: Medium · Type: Single choice

extent vs BBoxCache world bound:

A. They are always identical  
B. extent is local; BBoxCache applies transforms (and purpose)  
C. BBoxCache is only for lights  
D. extent is in USDZ only  

**Answer:** B.

### 13. Exam takeaways

> [!KEY]
> - Local box = extent. World box = BBoxCache.
> - Include the purposes you actually draw.

---

## 13.5 Unexpected visual results (Obj 5.5, 6.4)

### 1. What is it?

A checklist of authored-data bugs that look like "USD is broken" in the viewer.

### 2. Why do we need it?

Obj 5.5 / 6.4: understand what causes unexpected visuals. Many are data-model mistakes from this part of the book.

### 3. Beginner explanation

If it looks wrong, ask: units, up axis, extent, primvar interpolation, winding, purpose/visibility, material binding, composition (later).

### 4. Technical explanation

| Symptom | Likely cause |
|---------|----------------|
| Object 100× too small/large | `metersPerUnit` mismatch; no auto-convert (Ch 2, 28) |
| Object on its side | `upAxis` Y vs Z |
| Mesh missing or clipped | Stale/missing **extent**; wrong purpose; inactive; payload unloaded |
| Black / wrong colors | displayColor interpolation; missing primvar; shader vs crayon |
| Inside-out mesh | `orientation` / winding / left-handed points |
| Invisible but prim exists | `visibility=invisible` vs inactive vs purpose |
| Transform ignored | Missing `xformOpOrder` (Ch 39) |
| Material does not show | Binding API not applied; target outside defaultPrim (Ch 40) |
| Instance color edits all copies | Wrote on prototype, not proxy (Ch 24) |

This chapter owns the **extent / primvar / units / purpose** rows. Composition rows expand in Ch 42.

### 5. Mental model

Wrong picture → check data, then composition, then renderer.

### 6. Simple example

Artist moves vertices in DCC, exporter writes points but not extent → usdview culls the mesh.

### 7. USDA example

A mesh that will look "empty" to bounds-based tools (no extent, no points):

```usda
#usda 1.0

def Mesh "Broken"
{
    int[] faceVertexCounts = [3]
    int[] faceVertexIndices = [0, 1, 2]
}
```

### 8. Python example

```python
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
broken = UsdGeom.Mesh.Define(stage, "/Broken")
print("points:", broken.GetPointsAttr().Get())
print("extent:", broken.GetExtentAttr().Get())
print(
    "plugins:",
    UsdGeom.Boundable.ComputeExtentFromPlugins(
        UsdGeom.Boundable(broken.GetPrim()), Usd.TimeCode.Default()
    ),
)
```

**Expected output**

```text
points: None
extent: None
plugins: None
```

### 9. Real-world use case

A ticket "hero disappeared at frame 50": points have samples, extent only has a Default box from rest pose. At frame 50 the character has walked out of the rest box.

### 10. Common mistakes

> [!MISTAKE] Blaming Hydra first. Check extent and purpose before render-delegate settings.

### 11. Exam traps

> [!TRAP] A question that shows updated points and an old extent — the answer is Obj 5.6, not "USD cannot deform."

### 12. Practice questions

**DBG-PRE-003** · Obj 5.5 · Difficulty: Medium · Type: Select two.

Select two common causes of unexpected visuals:

A. Stale mesh extent after editing points  
B. metersPerUnit mismatch across a reference  
C. Using USDA instead of USDC for a 20-line interface layer  
D. The prim's name starting with a capital letter  

**Answer:** A and B.

### 13. Exam takeaways

> [!KEY]
> - Obj 5.6: points and extent stay together (including time samples).
> - Obj 5.5: units, axis, extent, interpolation, purpose/visibility, bindings.
> - Mesh extent is not free; Cube/Sphere fallbacks can hide the issue in tests.

---

## Chapter lab(s)

Lab 11 (mesh from scratch + compute extent). Lab 12 primvars. Combined checkpoint: Day 4.

## USDA reading exercise

**USDA-14.** Cube with `size = 2` and no authored extent. What box do bounds APIs still get at rest, and why might a Mesh with authored points but no extent differ?

**Answer:** Cube can fallback to `[(-1,-1,-1),(1,1,1)]`. Mesh `Get()` is None until authored; plugins can still compute if points exist, but many systems read the **attribute**.

## Chapter review

### If you see… → think…

| If you see… | Think… |
|-------------|--------|
| Update points | Update extent (Obj 5.6) |
| World box needed | BBoxCache |
| Missing mesh in viewer | extent / purpose / payload / visibility |
| 100× scale | metersPerUnit |
| Cube extent not authored | schema fallback — don't assume Mesh does that |

### Chapter questions

**Q1.** Four rungs Imageable…Gprim?  
**Q2.** extent space?  
**Q3.** Mesh Get() extent before Set?  
**Q4.** Does ComputeExtentFromPlugins author?  
**Q5.** BBoxCache second argument?  
**Q6.** visibility fallback?  
**Q7.** Obj 5.6 in one sentence?  
**Q8.** Two unexpected-visual causes from this part?

**Answers**

1. Imageable, Xformable, Boundable, Gprim. 2. Local. 3. None. 4. No, it returns values. 5. Purposes to include. 6. `inherited`. 7. After changing points, update extent. 8. Stale extent; unit mismatch.

## Further reading

- UsdGeomBoundable, UsdGeomXformable, UsdGeomImageable  
- `UsdGeomBoundable::ComputeExtentFromPlugins`  
- `UsdGeomModelAPI::GetExtentsHint`  
- Maximizing USD Performance (extents, purposes)  
