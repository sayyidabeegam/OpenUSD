# Lab 21 — Composition introspection toolkit

**Domain / objectives:** Composition 1.8 · Debugging 6.2 · **Chapter:** 22, 42 · **Time:** 30 min · **Difficulty:** ★★★

## Goal
Build `/Lamp` with a **local** height 2, an **inherit** of 9, and a **reference** of 1. Print the **prim stack**, **property stack**, **ResolveInfo**, and **`PrimCompositionQuery`** arcs (strongest first) to prove local won.

## Background
When a composed value is "wrong," the data is usually still on the stage (Ch 22, Ch 42). **`GetPrimStack()`** lists prim specs strongest first. **`GetPropertyStack()`** lists property specs (with `.default` here). **`GetResolveInfo()`** names the encoding (`ResolveInfoSourceDefault` vs time samples) and the winning **arc type**. **`Usd.PrimCompositionQuery(prim).GetCompositionArcs()`** lists arcs strongest first: Root, then Inherit, then Reference in this lab. Print target paths with `str(...)`.

## Steps
1. Composed `value: 2.0` — local wins.
2. Prim stack: `shot.usda /Lamp`, then the class spec `shot.usda /_Look`, then `lamp.usda /Lamp`.
3. Property stack defaults: `2.0`, `9.0`, `1.0` — same order.
4. Resolve source is **Default** (not a time sample) on **Root** (the local site).
5. Arcs: `Root /Lamp`, `Inherit /_Look`, `Reference /Lamp`. `errors: 0`.

## Full script (identical to `lab21_composition_introspection.py`)

```python
"""Lab 21 — Prim stack, property stack, ResolveInfo, composition arcs."""
import os
import tempfile
from pxr import Sdf, Usd

os.chdir(tempfile.mkdtemp())
open("lamp.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Lamp"
)
def Xform "Lamp"
{
    double height = 1
}
""")
stage = Usd.Stage.CreateNew("shot.usda")
cls = stage.CreateClassPrim("/_Look")
cls.CreateAttribute("height", Sdf.ValueTypeNames.Double).Set(9)
prim = stage.DefinePrim("/Lamp")
prim.GetReferences().AddReference("lamp.usda")
prim.GetInherits().AddInherit("/_Look")
prim.CreateAttribute("height", Sdf.ValueTypeNames.Double).Set(2)
attr = prim.GetAttribute("height")
print("value:", attr.Get())
print("prim stack:")
for spec in prim.GetPrimStack():
    print(" ", spec.layer.GetDisplayName(), spec.path)
print("property stack:")
for spec in attr.GetPropertyStack():
    print(" ", spec.layer.GetDisplayName(), spec.path, spec.default)
info = attr.GetResolveInfo()
print("resolve:", info.GetSource(), info.GetNode().arcType)
print("arcs:")
for arc in Usd.PrimCompositionQuery(prim).GetCompositionArcs():
    print(" ", arc.GetArcType(), str(arc.GetTargetNode().path))
print("errors:", len(stage.GetCompositionErrors()))
```

**Expected output**
```text
value: 2.0
prim stack:
  shot.usda /Lamp
  shot.usda /_Look
  lamp.usda /Lamp
property stack:
  shot.usda /Lamp.height 2.0
  shot.usda /_Look.height 9.0
  lamp.usda /Lamp.height 1.0
resolve: Usd.ResolveInfoSourceDefault Pcp.ArcTypeRoot
arcs:
  Pcp.ArcTypeRoot /Lamp
  Pcp.ArcTypeInherit /_Look
  Pcp.ArcTypeReference /Lamp
errors: 0
```

## Check your understanding
1. Which stack entry won `height`, and how do you know?
2. Does `Pcp.ArcTypeRoot` mean "no composition"?
3. Why print `str(arc.GetTargetNode().path)`?

**Answers**
1. **`shot.usda /Lamp.height 2.0`** — first in the property stack. ResolveInfo source Default on Root agrees.
2. **No.** Root is the prim's own site in this layer stack (the L in LIVERPS), including local inherits listed next.
3. The path object prints as `Sdf.Path('/Lamp')` otherwise; `str` keeps Expected output stable.

## Stretch challenge
`prim.GetAttribute("height").Clear()` and reprint value + winning stack entry. Solution: value becomes `9.0` and the first property spec is `shot.usda /_Look.height` (inherit, I before R).
