# Lab 18 — Specializes vs inherits vs references

**Domain / objectives:** Composition 1.1, 1.6 · **Chapter:** 19 · **Time:** 30 min · **Difficulty:** ★★★

## Goal
Give two prims the same referenced asset (`roughness = 0.2`) and the same class (`roughness = 0.9`, `metallic = 1.0`). One **inherits**, one **specializes**. Then prove **local beats both**, and **`Clear()`** restores the LIVERPS results.

## Background
**Inherits (I)** beat **references (R)**. **Specializes (S)** lose to everything above them, including references (Ch 19, LIVERPS). Both arcs still **fill gaps**: `metallic` is only on the class, so both prims get `1.0`. `HasAuthoredInherits()` / `HasAuthoredSpecializes()` report whether the arc is authored, not which value won. A **local** `Set(0.5)` wins on both. `Clear()` removes that local opinion and composition re-resolves.

## Steps
1. Inherit: roughness **0.9** (class beats asset), metallic **1.0**.
2. Specialize: roughness **0.2** (asset beats class), metallic **1.0** (gap fill).
3. Both flags are `True`.
4. Local `0.5` on both wins (L before I and S).
5. After `Clear()`: inherit back to **0.9**, specialize back to **0.2**.

## Full script (identical to `lab18_specializes_vs_inherits.py`)

```python
"""Lab 18 — Inherits beat references; specializes lose to them."""
import os
import tempfile
from pxr import Sdf, Usd

os.chdir(tempfile.mkdtemp())
open("asset.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Mat"
)
def "Mat"
{
    double roughness = 0.2
}
""")
stage = Usd.Stage.CreateInMemory()
cls = stage.CreateClassPrim("/_base")
cls.CreateAttribute("roughness", Sdf.ValueTypeNames.Double).Set(0.9)
cls.CreateAttribute("metallic", Sdf.ValueTypeNames.Double).Set(1.0)
inh = stage.DefinePrim("/ViaInherit")
inh.GetReferences().AddReference("asset.usda")
inh.GetInherits().AddInherit("/_base")
spc = stage.DefinePrim("/ViaSpecialize")
spc.GetReferences().AddReference("asset.usda")
spc.GetSpecializes().AddSpecialize("/_base")
print("inherit roughness/metallic:",
      inh.GetAttribute("roughness").Get(),
      inh.GetAttribute("metallic").Get())
print("specialize roughness/metallic:",
      spc.GetAttribute("roughness").Get(),
      spc.GetAttribute("metallic").Get())
print("HasAuthoredInherits:", inh.HasAuthoredInherits())
print("HasAuthoredSpecializes:", spc.HasAuthoredSpecializes())
inh.CreateAttribute("roughness", Sdf.ValueTypeNames.Double).Set(0.5)
spc.CreateAttribute("roughness", Sdf.ValueTypeNames.Double).Set(0.5)
print("local on both:", inh.GetAttribute("roughness").Get(),
      spc.GetAttribute("roughness").Get())
inh.GetAttribute("roughness").Clear()
spc.GetAttribute("roughness").Clear()
print("after Clear inherit/specialize:",
      inh.GetAttribute("roughness").Get(),
      spc.GetAttribute("roughness").Get())
```

**Expected output**
```text
inherit roughness/metallic: 0.9 1.0
specialize roughness/metallic: 0.2 1.0
HasAuthoredInherits: True
HasAuthoredSpecializes: True
local on both: 0.5 0.5
after Clear inherit/specialize: 0.9 0.2
```

## Check your understanding
1. Why is inherit roughness 0.9 but specialize roughness 0.2?
2. Why is metallic 1.0 on **both** prims?
3. Does `HasAuthoredSpecializes()` mean the class value won?

**Answers**
1. **I beats R; R beats S.** Same class, same asset, different arc strength.
2. The asset does not author `metallic`. Both arcs **fill gaps** from the class.
3. **No.** It only means a specializes arc is authored. The referenced 0.2 still wins.

## Stretch challenge
Print `Usd.PrimCompositionQuery` arcs on `/ViaSpecialize` (strongest first). Solution: `Root`, then `Reference /Mat`, then `Specialize /_base` — S last (Ch 19.3).
