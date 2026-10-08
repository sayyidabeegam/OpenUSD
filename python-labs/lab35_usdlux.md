# Lab 35 — UsdLux lights, LightAPI, intensity × 2^exposure

**Domain / objectives:** Visualization 8.x · **Chapter:** 41 · **Time:** 25 min · **Difficulty:** ★★☆

## Goal
Compare **DistantLight intensity fallback 50000** with **SphereLight 1**, prove **LightAPI is built-in** (no Apply), and scale a bulb as **intensity × 2^exposure**.

## Background
UsdLux typed lights carry **`LightAPI` automatically** — unlike `MaterialBindingAPI` on a Mesh (Ch 41). Distant (sun) fallback **50000**; local lights and Dome **1**. Distant is **not** Boundable; Sphere is. Brightness ∝ **`intensity × 2^exposure`**. Color temperature is ignored until **`enableColorTemperature`** is true (fallback False). Attribute names are **`inputs:intensity`** since 21.02.

## Steps
1. Distant `I=50000.0`; Sphere `I=1.0`.
2. `HasAPI(LightAPI)` True; applied schemas include LightAPI and collection APIs.
3. Distant not boundable; Sphere is. Sun angle ≈ 0.53°.
4. Intensity 3, exposure 2 → scale **12.0**. Color-temp enable fallback False.

## Full script (identical to `lab35_usdlux.py`)

```python
"""Lab 35 — Distant 50000 vs Sphere 1; LightAPI built-in; exposure."""
from pxr import Usd, UsdLux

stage = Usd.Stage.CreateInMemory()
sun = UsdLux.DistantLight.Define(stage, "/Lights/Sun")
bulb = UsdLux.SphereLight.Define(stage, "/Lights/Bulb")
print("distant I:", sun.GetIntensityAttr().Get())
print("sphere I:", bulb.GetIntensityAttr().Get())
print("HasAPI LightAPI:", sun.GetPrim().HasAPI(UsdLux.LightAPI))
print("applied:", list(sun.GetPrim().GetAppliedSchemas()))
print("distant boundable:", sun.GetPrim().IsA(UsdLux.BoundableLightBase))
print("sphere boundable:", bulb.GetPrim().IsA(UsdLux.BoundableLightBase))
print("sun angle:", round(sun.GetAngleAttr().Get(), 2))
api = UsdLux.LightAPI(bulb.GetPrim())
api.GetIntensityAttr().Set(3)
api.GetExposureAttr().Set(2)
print("bulb I/E:", api.GetIntensityAttr().Get(),
      api.GetExposureAttr().Get())
print("scale intensity*2**exposure:",
      api.GetIntensityAttr().Get() * (2 ** api.GetExposureAttr().Get()))
print("enableColorTemp fallback:",
      api.GetEnableColorTemperatureAttr().Get())
```

**Expected output**
```text
distant I: 50000.0
sphere I: 1.0
HasAPI LightAPI: True
applied: ['LightAPI', 'CollectionAPI:lightLink', 'CollectionAPI:shadowLink']
distant boundable: False
sphere boundable: True
sun angle: 0.53
bulb I/E: 3.0 2.0
scale intensity*2**exposure: 12.0
enableColorTemp fallback: False
```

## Check your understanding
1. Unauthored Distant `GetIntensityAttr().Get()`?
2. Must you `LightAPI.Apply` before setting intensity on a DistantLight?
3. Exposure 2 means plus 2 intensity, or ×4?

**Answers**
1. **50000.0**, not 1.
2. **No.** LightAPI is **built into** typed lights. Apply ShadowAPI/ShapingAPI only.
3. **×4** (`2^2`). Stops, not additive.

## Stretch challenge
`UsdLux.ShapingAPI.Apply(bulb.GetPrim())` and print `HasAPI`. Solution: True after Apply — ShapingAPI is optional, unlike LightAPI (Ch 41.2).
