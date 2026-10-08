# Lab 12 — Indexed vertex `displayColor` primvar

**Domain / objectives:** Data Modeling 5.1 · Visualization 8.1 · **Chapter:** 11 · **Time:** 25 min · **Difficulty:** ★★☆

## Goal
Author a **vertex** `displayColor` primvar with **two unique colors** and **four indices** `[0, 1, 0, 1]` (paint-by-number). Print values as tuples, not `Gf.Vec3f`.

## Background
A **primvar** is a `primvars:` attribute with interpolation metadata (Ch 11). Use **`UsdGeom.PrimvarsAPI.CreatePrimvar`** so interpolation and indices are set correctly. **Indexing** stores a palette plus `primvars:foo:indices`; it is independent of interpolation. `vertex` interpolation means one value (or one index) per point.

## Steps
1. Run the script. Interpolation is `vertex`.
2. `indexed: True` after `SetIndices`.
3. Indices are `[0, 1, 0, 1]` — four corners of a quad sharing two colors.
4. Values are the palette `[(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]` (red, green).

## Full script (identical to `lab12_primvars.py`)

```python
"""Lab 12 — Indexed vertex displayColor primvar."""
from pxr import Sdf, Usd, UsdGeom, Vt

stage = Usd.Stage.CreateInMemory()
api = UsdGeom.PrimvarsAPI(UsdGeom.Mesh.Define(stage, "/Body"))
pv = api.CreatePrimvar(
    "displayColor", Sdf.ValueTypeNames.Color3fArray, UsdGeom.Tokens.vertex
)
pv.Set([(1, 0, 0), (0, 1, 0)])
pv.SetIndices(Vt.IntArray([0, 1, 0, 1]))
print("interpolation:", pv.GetInterpolation())
print("indexed:", pv.IsIndexed())
print("indices:", list(pv.GetIndices()))
print("values:", [tuple(v) for v in pv.Get()])
```

**Expected output**
```text
interpolation: vertex
indexed: True
indices: [0, 1, 0, 1]
values: [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
```

## Check your understanding
1. Does indexing change the interpolation?
2. For vertex interpolation on a 4-point mesh, what must have length 4 — values or indices?
3. Why print `tuple(v)` instead of `v`?

**Answers**
1. **No.** Indexing is independent. Interpolation still describes how values (or indices) attach to topology.
2. **Indices.** Values are the unique palette (here length 2).
3. `Get()` returns `Gf.Vec3f`; `tuple` keeps Expected output stable and readable.

## Stretch challenge
Call `pv.SetInterpolation(UsdGeom.Tokens.constant)` and think about length. Solution: constant wants **one** value (or one index). A four-index array with constant interpolation is a length mismatch — a classic Obj 5.5 unexpected-visuals bug.
