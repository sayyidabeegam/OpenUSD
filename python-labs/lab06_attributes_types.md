# Lab 06 — Attributes and value types

**Domain / objectives:** Data Modeling 5.2 · **Chapter:** 5, 9 · **Time:** 25 min · **Difficulty:** ★☆☆

## Goal
Create attributes with four `Sdf.ValueTypeNames` (`Int`, `Float`, `Color3f`, `Point3f`), set values, and list **authored** property names (not the whole schema).

## Background
Attributes are typed. `color3f` and `point3f` are both three floats but mean different things to Hydra (a colour vs a position). `GetPropertyNames()` on an Xform also lists schema leftovers (`visibility`, `xformOpOrder`, …). `GetAuthoredPropertyNames()` is the list you wrote (Ch 5, Ch 9).

## Steps
1. Run the script. Match each type name to the value.
2. `authored` is exactly the four names you created, sorted.

## Full script (identical to `lab06_attributes_types.py`)

```python
"""Lab 06 — Attributes and value types."""
from pxr import Sdf, Usd, UsdGeom

stage = Usd.Stage.CreateInMemory()
prim = UsdGeom.Xform.Define(stage, "/P").GetPrim()
count = prim.CreateAttribute("count", Sdf.ValueTypeNames.Int)
count.Set(3)
mass = prim.CreateAttribute("mass", Sdf.ValueTypeNames.Float)
mass.Set(1.5)
tint = prim.CreateAttribute("tint", Sdf.ValueTypeNames.Color3f)
tint.Set((0.2, 0.4, 0.8))
pos = prim.CreateAttribute("pos", Sdf.ValueTypeNames.Point3f)
pos.Set((1, 2, 3))
print("count", count.GetTypeName(), count.Get())
print("mass", mass.GetTypeName(), mass.Get())
print("tint", tint.GetTypeName(), tint.Get())
print("pos", pos.GetTypeName(), pos.Get())
print("authored:", sorted(prim.GetAuthoredPropertyNames()))
```

**Expected output**
```text
count int 3
mass float 1.5
tint color3f (0.2, 0.4, 0.8)
pos point3f (1, 2, 3)
authored: ['count', 'mass', 'pos', 'tint']
```

## Check your understanding
1. Why not store the colour as `Point3f`?
2. Does `GetPropertyNames()` equal `GetAuthoredPropertyNames()` on this Xform?
3. What namespace would a primvar use? (Ch 11)

**Answers**
1. Downstream tools treat `color3f` as a colour (gamma, Hydra) and `point3f` as a position.
2. **No.** The schema adds `visibility`, `purpose`, `xformOpOrder`, `proxyPrim`.
3. `primvars:` (`primvars:displayColor`, …).

## Stretch challenge
Create `Sdf.ValueTypeNames.Token` `mode` set to `"run"`. Print `GetTypeName()`. Solution: `token`.
