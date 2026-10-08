# Lab 02 — Your first stage: Xform + Sphere, save as USDA

**Domain / objectives:** Foundations · **Chapter:** 2 · **Time:** 20 min · **Difficulty:** ★☆☆

## Goal
Create a stage, define `/World` (Xform) and `/World/Ball` (Sphere), set a radius, mark `defaultPrim`, and save USDA.

## Background
A **stage** is the live composed scene (`Usd.Stage`). `CreateNew("hello.usda")` makes a file-backed root layer. `UsdGeom.Xform.Define` / `Sphere.Define` author typed prims. `SetDefaultPrim` writes layer metadata so later references can omit a prim path (Ch 2, Ch 16).

The script `chdir`s to a temp directory so it does not clutter your repo. `ExportToString()` is the Python stand-in for `usdcat`.

## Steps
1. Run the script. Read the USDA it prints.
2. Note `double radius = 2` (you set `2.0`; USDA drops the trailing zero).
3. `file exists: True` means `Save()` wrote `hello.usda` in the temp dir.

## Full script (identical to `lab02_first_stage.py`)

```python
"""Lab 02 — Your first stage: Xform + Sphere, save as USDA."""
import os
import tempfile
from pxr import Usd, UsdGeom

os.chdir(tempfile.mkdtemp())
stage = Usd.Stage.CreateNew("hello.usda")
world = UsdGeom.Xform.Define(stage, "/World")
ball = UsdGeom.Sphere.Define(stage, "/World/Ball")
ball.GetRadiusAttr().Set(2.0)
stage.SetDefaultPrim(world.GetPrim())
stage.GetRootLayer().Save()
print(stage.GetRootLayer().ExportToString(), end="")
print("defaultPrim:", stage.GetDefaultPrim().GetName())
print("radius:", ball.GetRadiusAttr().Get())
print("file exists:", os.path.isfile("hello.usda"))
```

**Expected output**
```text
#usda 1.0
(
    defaultPrim = "World"
)

def Xform "World"
{
    def Sphere "Ball"
    {
        double radius = 2
    }
}

defaultPrim: World
radius: 2.0
file exists: True
```

## Check your understanding
1. What prim type is `/World`?
2. Why set `defaultPrim`?
3. `Get()` prints `2.0` but USDA shows `2`. Is the value different?

**Answers**
1. **Xform** — a grouping transform, not geometry.
2. So a reference to this file without `</World>` still finds the asset root.
3. No. Python `Get()` is `2.0`; USDA omits `.0` for whole doubles.

## Stretch challenge
Also define `/World/Ground` as a `Cube` with `size = 4`. Print its type name. Solution: `UsdGeom.Cube.Define(stage, "/World/Ground").GetSizeAttr().Set(4)` then `GetPrim().GetTypeName()` → `Cube`.
