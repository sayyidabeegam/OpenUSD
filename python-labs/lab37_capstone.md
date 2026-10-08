# Lab 37 — Capstone: publish a component, assemble, validate, inventory

**Domain / objectives:** Content Aggregation 2.4 · Data Exchange 4.6 · Pipeline 7.2 · **Chapter:** 23, 30, 32 · **Time:** 35 min · **Difficulty:** ★★★

## Goal
Publish a **component** chair with stage metrics and `defaultPrim`, pass **UsdValidation** metadata checkers, reference it into an **assembly → group** kitchen, and ship-check with **`ComputeAllDependencies`**. Print **`Usd.GetVersion()`**.

## Background
This lab stitches Labs 22, 27, and 28 (Ch 23, 30, 32). A published component needs **defaultPrim**, **upAxis**, **metersPerUnit**, and **kind**. An assembly uses **group** organizers so referenced chairs stay valid models. `ComputeAllDependencies` on the kitchen lists both layers and an empty unresolved list — the publish gate.

## Steps
1. Chair validators report **0** errors; kind `component`.
2. `assembly is-a group: True`.
3. `/Kitchen/Props/Chair_0` is a valid component `Xform`.
4. Layers `chair.usda` + `kitchen.usda`; unresolved `[]`.
5. Version `(0, 26, 8)`.

## Full script (identical to `lab37_capstone.py`)

```python
"""Lab 37 — Capstone: component, assembly, validate, dependencies."""
import os
import tempfile
from pxr import Kind, Usd, UsdGeom, UsdUtils, UsdValidation

os.chdir(tempfile.mkdtemp())
open("chair.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Chair"
    metersPerUnit = 1
    upAxis = "Y"
)
def Xform "Chair" (
    kind = "component"
)
{
    def Cube "Seat"
    {
        double size = 1
    }
}
""")
reg = UsdValidation.ValidationRegistry()
geom = reg.GetOrLoadValidatorByName(
    "usdGeomValidators:StageMetadataChecker")
core = reg.GetOrLoadValidatorByName(
    "usdValidation:StageMetadataChecker")
chair = Usd.Stage.Open("chair.usda")
print("chair errors:",
      len(list(geom.Validate(chair))) + len(list(core.Validate(chair))))
print("chair kind:", Usd.ModelAPI(chair.GetDefaultPrim()).GetKind())
print("assembly is-a group:", Kind.Registry.IsA("assembly", "group"))

kitchen = Usd.Stage.CreateNew("kitchen.usda")
root = UsdGeom.Xform.Define(kitchen, "/Kitchen").GetPrim()
Usd.ModelAPI(root).SetKind("assembly")
kitchen.SetDefaultPrim(root)
UsdGeom.SetStageUpAxis(kitchen, "Y")
UsdGeom.SetStageMetersPerUnit(kitchen, 1)
props = UsdGeom.Xform.Define(kitchen, "/Kitchen/Props").GetPrim()
Usd.ModelAPI(props).SetKind("group")
c0 = kitchen.DefinePrim("/Kitchen/Props/Chair_0")
c0.GetReferences().AddReference("chair.usda")
kitchen.GetRootLayer().Save()
print("Chair_0 IsComponent:", c0.IsComponent())
print("Chair_0 type:", c0.GetTypeName())
layers, assets, unresolved = UsdUtils.ComputeAllDependencies(
    "kitchen.usda")
print("layers:", sorted(os.path.basename(l.realPath) for l in layers))
print("unresolved:", unresolved)
print("USD version:", Usd.GetVersion())
```

**Expected output**
```text
chair errors: 0
chair kind: component
assembly is-a group: True
Chair_0 IsComponent: True
Chair_0 type: Xform
layers: ['chair.usda', 'kitchen.usda']
unresolved: []
USD version: (0, 26, 8)
```

## Check your understanding
1. Why would Chair_0 fail `IsComponent` if Props had no kind?
2. What does a non-empty `unresolved` list mean at publish time?
3. Is `Usd.GetVersion()` `(26, 8)` or `(0, 26, 8)`?

**Answers**
1. The model hierarchy **breaks** without a group/assembly ancestor (Lab 22).
2. A dependency file is **missing** — fail the publish (Lab 28).
3. **`(0, 26, 8)`**. The leading month zero is dropped in the pip name `26.8`.

## Stretch challenge
Drop `upAxis` from `chair.usda` and re-run the geom checker. Solution: `MissingUpAxisMetadata` Error (Lab 27); the kitchen would still compose the chair.
