# Lab 24 — PointInstancer: append a prototype, hide one instance

**Domain / objectives:** Content Aggregation 2.1, 2.3 · **Chapter:** 25 · **Time:** 30 min · **Difficulty:** ★★★

## Goal
Build a forest PointInstancer, **append** a third prototype without scrambling indices, confirm it is **Boundable but not a Gprim**, then **`InvisId`** one instance and see transforms skip it while **`GetInstanceCount()` stays 3**.

## Background
A **PointInstancer** stores copies as arrays on **one** prim (Ch 25). Required: `prototypes` rel, `protoIndices`, `positions`. Instance count = `len(protoIndices)`. Put prototypes under a **`class`** child so `Traverse()` skips them. **`AddTarget` prepends by default** and re-numbers every existing prototype — pass **`Usd.ListPositionBackOfAppendList`**. `InvisId(id, time)` hides one instance (not `MakeInvisible()`, which hides the whole prim). Hidden instances drop out of `ComputeInstanceTransformsAtTime` via the mask; they are not deleted.

## Steps
1. Targets after append: `Pine, Oak, Bush` (Bush last).
2. Three instances; `Traverse` is only `/Forest` (class Protos hidden).
3. Not a Gprim; is Boundable. Translations at 0, 2, 4.
4. `InvisId(1, Default)` → mask `[True, False, True]`, `invisibleIds [1]`.
5. Transforms remain at 0 and 4. Count is still 3.

## Full script (identical to `lab24_point_instancer.py`)

```python
"""Lab 24 — PointInstancer: append a prototype, hide one instance."""
from pxr import Sdf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
forest = UsdGeom.PointInstancer.Define(stage, "/Forest")
protos = stage.DefinePrim("/Forest/Protos")
protos.SetSpecifier(Sdf.SpecifierClass)
UsdGeom.Cone.Define(stage, "/Forest/Protos/Pine")
UsdGeom.Cylinder.Define(stage, "/Forest/Protos/Oak")
UsdGeom.Sphere.Define(stage, "/Forest/Protos/Bush")
rel = forest.CreatePrototypesRel()
rel.SetTargets(["/Forest/Protos/Pine", "/Forest/Protos/Oak"])
rel.AddTarget("/Forest/Protos/Bush", Usd.ListPositionBackOfAppendList)
print("targets:", [t.name for t in rel.GetTargets()])
forest.CreateProtoIndicesAttr([0, 1, 2])
forest.CreatePositionsAttr([(0, 0, 0), (2, 0, 0), (4, 0, 0)])
print("instances:", forest.GetInstanceCount())
print("traversed:", [str(p.GetPath()) for p in stage.Traverse()])
print("is Gprim:", forest.GetPrim().IsA(UsdGeom.Gprim))
print("is Boundable:", forest.GetPrim().IsA(UsdGeom.Boundable))
t = Usd.TimeCode.Default()
for m in forest.ComputeInstanceTransformsAtTime(t, t):
    print("at", tuple(m.ExtractTranslation()))
forest.InvisId(1, t)
print("mask:", list(forest.ComputeMaskAtTime(t)))
print("invisibleIds:", list(forest.GetInvisibleIdsAttr().Get()))
print("transforms after hide:")
for m in forest.ComputeInstanceTransformsAtTime(t, t):
    print("at", tuple(m.ExtractTranslation()))
print("count still:", forest.GetInstanceCount())
```

**Expected output**
```text
targets: ['Pine', 'Oak', 'Bush']
instances: 3
traversed: ['/Forest']
is Gprim: False
is Boundable: True
at (0.0, 0.0, 0.0)
at (2.0, 0.0, 0.0)
at (4.0, 0.0, 0.0)
mask: [True, False, True]
invisibleIds: [1]
transforms after hide:
at (0.0, 0.0, 0.0)
at (4.0, 0.0, 0.0)
count still: 3
```

## Check your understanding
1. Which array sets the instance count?
2. Why pass `ListPositionBackOfAppendList`?
3. Does `MakeInvisible()` hide instance 1?

**Answers**
1. **`protoIndices`**, not `positions` and not the number of prototype targets.
2. Default **`AddTarget` prepends**, so index 0 becomes the new prim and every old instance draws the wrong prototype.
3. **No.** That is Imageable visibility on the **whole** PointInstancer. Use **`InvisId(id, time)`**.

## Stretch challenge
Call `rel.AddTarget("/Forest/Protos/Bush")` with **no** list position on a stronger sublayer that already has Pine, Oak. Solution: composed targets start with Bush; existing `protoIndices` `[0, 1]` now draw Bush and Pine (Ch 25.3 prepend trap).
