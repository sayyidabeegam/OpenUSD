# Lab 11 — Mesh topology, `subdivisionScheme`, and extent

**Domain / objectives:** Data Modeling 5.5, 5.6 · **Chapter:** 13, 39 · **Time:** 30 min · **Difficulty:** ★★☆

## Goal
Build a triangle Mesh, see that **`extent` is not automatic**, compute it with **`ComputeExtentFromPlugins`**, `Set` it, and author **`subdivisionScheme = none`** so the polygons stay flat.

## Background
A Mesh needs `points`, `faceVertexCounts`, and `faceVertexIndices` (Ch 39). **`extent`** is a local-space AABB (`float3[]` of length 2). Changing points does **not** update it; you compute and author it (Obj 5.6, Ch 13). `ComputeExtentFromPlugins` **returns** values — it does not write. The `subdivisionScheme` fallback is **`catmullClark`** (smooth). Hard-surface / CAD meshes must set **`none`**.

## Steps
1. Run the script. Fallback scheme is `catmullClark` even though you never authored it.
2. After `CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)`, it is `none`.
3. `extent authored?: False` and `Get()` is `None`.
4. `computed` is `[(0.0, 0.0, 0.0), (1.0, 1.0, 0.0)]` — min/max of the three points.
5. After `Set`, `extent after` matches the computed box.

## Full script (identical to `lab11_mesh_extent.py`)

```python
"""Lab 11 — Mesh topology, subdivisionScheme, ComputeExtentFromPlugins."""
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
mesh = UsdGeom.Mesh.Define(stage, "/Tri")
mesh.GetPointsAttr().Set([(0, 0, 0), (1, 0, 0), (0, 1, 0)])
mesh.GetFaceVertexCountsAttr().Set([3])
mesh.GetFaceVertexIndicesAttr().Set([0, 1, 2])
print("scheme fallback:", mesh.GetSubdivisionSchemeAttr().Get())
mesh.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)
print("scheme authored:", mesh.GetSubdivisionSchemeAttr().Get())
print("extent authored?:", mesh.GetExtentAttr().HasAuthoredValue())
print("extent before:", mesh.GetExtentAttr().Get())
computed = UsdGeom.Boundable.ComputeExtentFromPlugins(
    UsdGeom.Boundable(mesh.GetPrim()), Usd.TimeCode.Default()
)
print("computed:", [tuple(v) for v in computed])
mesh.GetExtentAttr().Set(computed)
print("extent after:", [tuple(v) for v in mesh.GetExtentAttr().Get()])
```

**Expected output**
```text
scheme fallback: catmullClark
scheme authored: none
extent authored?: False
extent before: None
computed: [(0.0, 0.0, 0.0), (1.0, 1.0, 0.0)]
extent after: [(0.0, 0.0, 0.0), (1.0, 1.0, 0.0)]
```

## Check your understanding
1. Does `ComputeExtentFromPlugins` author `extent`?
2. What is the unauthored `subdivisionScheme`?
3. Is `extent` in world space or local space?

**Answers**
1. **No.** It returns a `Vt.Vec3fArray`. You must `Set`.
2. **`catmullClark`**, not `none`.
3. **Local.** Parent xforms are applied by `BBoxCache`, not stored in `extent`.

## Stretch challenge
Move one point to `(4, 0, 0)` and recompute. Solution: computed max x becomes `4.0`; the previously authored extent is stale until you `Set` again.
