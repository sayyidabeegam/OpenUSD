# Lab 33 — Xform ops, XformCache, and `Gf.Camera`

**Domain / objectives:** Visualization 8.x · **Chapter:** 39 · **Time:** 30 min · **Difficulty:** ★★☆

## Goal
Author a translate with **`AddTranslateOp`** (which fills **`xformOpOrder`**), catch a **second** `AddTranslateOp`, compose parent+child with **`XformCache`**, and convert a **`UsdGeom.Camera`** to **`Gf.Camera`** for horizontal FOV.

## Background
`AddTranslateOp()` creates `xformOp:translate` **and** appends it to `xformOpOrder`. Creating the attribute alone does not move anything (Ch 39). A second `AddTranslateOp()` without a suffix **raises**. World transforms include ancestors: Lid at local `(0,2,0)` under Box `(1,0,0)` is world `(1,2,0)`. `GetCamera(time)` returns a **`Gf.Camera`**, not another UsdGeom schema. Fallback focal **50**, horizontal aperture **20.955**. Focal 35 → hFOV **33.33** degrees.

## Steps
1. `xformOpOrder` is `['xformOp:translate']`.
2. Second `AddTranslateOp()` → `Tf.ErrorException`.
3. World Box `(1,0,0)`; Lid `(1,2,0)`.
4. Fallback 50 / 20.955. After focal 35: type `Camera`, Perspective, hFOV 33.33, position `(0,0,10)`.

## Full script (identical to `lab33_xforms_cameras.py`)

```python
"""Lab 33 — xformOpOrder, XformCache, UsdGeom.Camera → Gf.Camera."""
from pxr import Gf, Tf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
xf = UsdGeom.Xform.Define(stage, "/Box")
xf.AddTranslateOp().Set(Gf.Vec3d(1, 0, 0))
print("order:", list(xf.GetPrim().GetAttribute("xformOpOrder").Get()))
try:
    xf.AddTranslateOp()
except Tf.ErrorException:
    print("second AddTranslateOp: Tf.ErrorException")
child = UsdGeom.Xform.Define(stage, "/Box/Lid")
child.AddTranslateOp().Set(Gf.Vec3d(0, 2, 0))
cache = UsdGeom.XformCache(Usd.TimeCode.Default())
print("world Box:", tuple(
    cache.GetLocalToWorldTransform(xf.GetPrim()).ExtractTranslation()))
print("world Lid:", tuple(
    cache.GetLocalToWorldTransform(
        child.GetPrim()).ExtractTranslation()))

cam = UsdGeom.Camera.Define(stage, "/ShotCam")
print("fallback focal/hAperture:", cam.GetFocalLengthAttr().Get(),
      round(cam.GetHorizontalApertureAttr().Get(), 3))
cam.AddTranslateOp().Set(Gf.Vec3d(0, 0, 10))
cam.GetFocalLengthAttr().Set(35.0)
gf = cam.GetCamera(Usd.TimeCode.Default())
print(type(gf).__name__, gf.projection)
print("hFOV", round(gf.GetFieldOfView(Gf.Camera.FOVHorizontal), 2))
print("position", tuple(gf.transform.ExtractTranslation()))
```

**Expected output**
```text
order: ['xformOp:translate']
second AddTranslateOp: Tf.ErrorException
world Box: (1.0, 0.0, 0.0)
world Lid: (1.0, 2.0, 0.0)
fallback focal/hAperture: 50.0 20.955
Camera Gf.Camera.Perspective
hFOV 33.33
position (0.0, 0.0, 10.0)
```

## Check your understanding
1. Why use `AddTranslateOp` instead of `CreateAttribute("xformOp:translate")`?
2. What does `UsdGeom.Camera.GetCamera(t)` return?
3. Does a Camera look down +Z or −Z?

**Answers**
1. It also appends **`xformOpOrder`**. Without the order, nothing moves.
2. A **`Gf.Camera`** (math: FOV, frustum), not a `UsdGeom.Camera`.
3. **−Z** in local camera space (OpenUSD camera convention).

## Stretch challenge
`xf.AddTranslateOp(opSuffix="pivot")` after the first translate. Solution: order becomes `['xformOp:translate', 'xformOp:translate:pivot']` — suffixes allow a second translate (Ch 39).
