# Lab 26 — Units and up-axis: USD does not convert

**Domain / objectives:** Data Exchange 4.7 · **Chapter:** 28 · **Time:** 30 min · **Difficulty:** ★★☆

## Goal
Reference a **meters, Z-up** chair into a **centimeters, Y-up** shot. Prove composed `size` stays **1.0**, then add **`rotateX(-90)`** and **`scale 100`** on the referencing prim so world bounds match 1 m = 100 cm.

## Background
Stage metrics (`upAxis`, `metersPerUnit`) live on the **root layer**. Composition arcs do **not** copy them (Ch 28). CreateInMemory fallback is **Y** and **0.01**. Factor = `asset_mpu / shot_mpu` (meters into cm → **100**). Read metrics by **opening the asset file**, not from the composed stage. Use a **typeless** `DefinePrim` so the asset's `Xform` type comes through; `Xform.Define` on the reference would replace a Cube/Mesh root. `+ 0.0` after `round` clears `-0.0`.

## Steps
1. Fallback metrics: `Y 0.01`.
2. Composed Cube `size` is still `1.0`. Shot stays `Y 0.01`; asset is `Z 1.0`.
3. Before correction, world range is ~1 unit tall on **Z**.
4. `factor: 100.0`. After rotate+scale, height is 100 cm on **+Y**.

## Full script (identical to `lab26_units_upaxis.py`)

```python
"""Lab 26 — USD does not convert units; you add scale and rotateX."""
import os
import tempfile
from pxr import Usd, UsdGeom

os.chdir(tempfile.mkdtemp())
print("fallback:", UsdGeom.GetStageUpAxis(Usd.Stage.CreateInMemory()),
      UsdGeom.GetStageMetersPerUnit(Usd.Stage.CreateInMemory()))

asset = Usd.Stage.CreateNew("chair_m.usda")
UsdGeom.SetStageMetersPerUnit(asset, UsdGeom.LinearUnits.meters)
UsdGeom.SetStageUpAxis(asset, UsdGeom.Tokens.z)
root = UsdGeom.Xform.Define(asset, "/Chair")
cube = UsdGeom.Cube.Define(asset, "/Chair/Geom")
cube.GetSizeAttr().Set(1.0)
cube.AddTranslateOp().Set((0, 0, 0.5))
asset.SetDefaultPrim(root.GetPrim())
asset.Save()

shot = Usd.Stage.CreateInMemory()
UsdGeom.SetStageMetersPerUnit(shot, UsdGeom.LinearUnits.centimeters)
UsdGeom.SetStageUpAxis(shot, UsdGeom.Tokens.y)
UsdGeom.Xform.Define(shot, "/World")
prim = shot.DefinePrim("/World/Chair")
prim.GetReferences().AddReference("chair_m.usda")
chair = UsdGeom.Xformable(prim)


def world_range(stage, path):
    cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default"])
    r = cache.ComputeWorldBound(
        stage.GetPrimAtPath(path)).ComputeAlignedRange()
    fix = lambda v: tuple(round(c, 3) + 0.0 for c in v)
    return fix(r.GetMin()), fix(r.GetMax())


geom = UsdGeom.Cube(shot.GetPrimAtPath("/World/Chair/Geom"))
print("composed size:", geom.GetSizeAttr().Get())
print("shot metrics:", UsdGeom.GetStageUpAxis(shot),
      UsdGeom.GetStageMetersPerUnit(shot))
print("before:", world_range(shot, "/World/Chair"))

src = Usd.Stage.Open("chair_m.usda")
print("asset metrics:", UsdGeom.GetStageUpAxis(src),
      UsdGeom.GetStageMetersPerUnit(src))
factor = (UsdGeom.GetStageMetersPerUnit(src)
          / UsdGeom.GetStageMetersPerUnit(shot))
if UsdGeom.GetStageUpAxis(src) != UsdGeom.GetStageUpAxis(shot):
    chair.AddRotateXOp().Set(-90.0)
chair.AddScaleOp().Set((factor, factor, factor))
print("factor:", factor)
print("after:", world_range(shot, "/World/Chair"))
```

**Expected output**
```text
fallback: Y 0.01
composed size: 1.0
shot metrics: Y 0.01
before: ((-0.5, -0.5, 0.0), (0.5, 0.5, 1.0))
asset metrics: Z 1.0
factor: 100.0
after: ((-50.0, 0.0, -50.0), (50.0, 100.0, 50.0))
```

## Check your understanding
1. Does referencing a meters asset into a centimeters stage rescale `size`?
2. Why open `chair_m.usda` separately to read units?
3. Why `DefinePrim` instead of `UsdGeom.Xform.Define` for `/World/Chair`?

**Answers**
1. **No.** Composed `size` stays `1.0`. You add the scale.
2. The composed stage reports **its own** root-layer metrics, not the asset's.
3. A local `Xform` type would **replace** a Cube/Mesh asset root. Typeless lets the asset's type come through; wrap with `UsdGeom.Xformable` to add ops.

## Stretch challenge
Invert the factor (`shot_mpu / asset_mpu`). Solution: scale 0.01; the chair becomes 1 cm tall in a cm stage — the classic "tiny imported hero" bug.
