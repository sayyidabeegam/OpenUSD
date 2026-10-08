# Lab 03 — Open and traverse a stage

**Domain / objectives:** Data Modeling 5.4 · **Chapter:** 2 · **Time:** 20 min · **Difficulty:** ★☆☆

## Goal
Write a USDA file, `Stage.Open` it, walk prims with `Traverse()`, and look up paths with `GetPrimAtPath` (including a missing path).

## Background
`Traverse()` yields defined, active, loaded prims in hierarchy order. `GetPrimAtPath` always returns a handle — you must ask `IsValid()`. A missing path is **not** an exception (Ch 2, Ch 42.2). This lab recreates `hello.usda` itself so it does not depend on Lab 02's temp directory.

## Steps
1. Run the script.
2. Confirm two prims: `/World` Xform, `/World/Ball` Sphere.
3. Confirm `/Nope` is invalid.

## Full script (identical to `lab03_open_traverse.py`)

```python
"""Lab 03 — Open and traverse a stage."""
import os
import tempfile
from pxr import Usd, UsdGeom

os.chdir(tempfile.mkdtemp())
stage = Usd.Stage.CreateNew("hello.usda")
world = UsdGeom.Xform.Define(stage, "/World")
UsdGeom.Sphere.Define(stage, "/World/Ball")
stage.SetDefaultPrim(world.GetPrim())
stage.GetRootLayer().Save()

opened = Usd.Stage.Open("hello.usda")
print("root ends:", os.path.basename(opened.GetRootLayer().identifier))
print("prims:")
for prim in opened.Traverse():
    print(" ", prim.GetPath(), prim.GetTypeName())
ball = opened.GetPrimAtPath("/World/Ball")
print("Ball valid:", ball.IsValid(), "type:", ball.GetTypeName())
print("missing valid:", opened.GetPrimAtPath("/Nope").IsValid())
```

**Expected output**
```text
root ends: hello.usda
prims:
  /World Xform
  /World/Ball Sphere
Ball valid: True type: Sphere
missing valid: False
```

## Check your understanding
1. Does `GetPrimAtPath("/Nope")` raise?
2. What does `Traverse()` skip that `TraverseAll()` would include? (Preview of Ch 42.)
3. Why `basename` the identifier?

**Answers**
1. **No.** It returns an invalid prim (`IsValid()` False).
2. Inactive, undefined overs, unloaded payloads, instance interiors.
3. The identifier may be an absolute path; display/basename stays portable.

## Stretch challenge
Print `opened.GetPrimAtPath("/World").GetChildren()` names. Solution: `[c.GetName() for c in ...GetChildren()]` → `['Ball']`.
