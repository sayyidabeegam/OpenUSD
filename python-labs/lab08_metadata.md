# Lab 08 — Metadata, customData, assetInfo, stage metadata

**Domain / objectives:** Data Modeling 5.3, Pipeline 7.6 · **Chapter:** 12 · **Time:** 25 min · **Difficulty:** ★☆☆

## Goal
Read the **CreateInMemory** fallbacks for `upAxis` and `metersPerUnit`, then author Z-up metres, `defaultPrim`, a `customData` key, and an `assetInfo` identifier.

## Background
Stage metadata lives on the **root layer**. Fresh `CreateInMemory` stages already have `upAxis = Y` and `metersPerUnit = 0.01` (centimetres) — verified on USD 26.08 (Ch 2, Ch 28). `customData` is a dictionary on the prim (not a typed attribute). `GetCustomData()` may also include schema `userDocBrief`; this lab reads **only** the key we set (`GetCustomDataByKey`).

## Steps
1. Run the script. Defaults are Y and 0.01.
2. After the setters: Z and 1.0, defaultPrim `World`.
3. `dept` / `asset id` are the keys you authored.

## Full script (identical to `lab08_metadata.py`)

```python
"""Lab 08 — Metadata, customData, assetInfo, stage metadata."""
from pxr import Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
print("default upAxis:", UsdGeom.GetStageUpAxis(stage))
print("default meters:", UsdGeom.GetStageMetersPerUnit(stage))
UsdGeom.SetStageUpAxis(stage, "Z")
UsdGeom.SetStageMetersPerUnit(stage, 1.0)
world = UsdGeom.Xform.Define(stage, "/World")
stage.SetDefaultPrim(world.GetPrim())
prim = world.GetPrim()
prim.SetCustomDataByKey("dept", "layout")
prim.SetAssetInfoByKey("identifier", "world")
print("upAxis:", UsdGeom.GetStageUpAxis(stage))
print("meters:", UsdGeom.GetStageMetersPerUnit(stage))
print("defaultPrim:", stage.GetDefaultPrim().GetName())
print("dept:", prim.GetCustomDataByKey("dept"))
print("asset id:", prim.GetAssetInfoByKey("identifier"))
```

**Expected output**
```text
default upAxis: Y
default meters: 0.01
upAxis: Z
meters: 1.0
defaultPrim: World
dept: layout
asset id: world
```

## Check your understanding
1. What are CreateInMemory fallbacks for upAxis and metersPerUnit?
2. Is `customData` an attribute you `CreateAttribute`?
3. Why not print all of `GetCustomData()` in this lab?

**Answers**
1. **Y** and **0.01**.
2. **No.** It is prim metadata (`SetCustomDataByKey`).
3. The schema may inject `userDocBrief`; key lookup is stable.

## Stretch challenge
Set `timeCodesPerSecond` to 24 with `stage.SetTimeCodesPerSecond(24)` and print `GetTimeCodesPerSecond()`. Solution: `24.0`.
