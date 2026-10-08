# Lab 20 — LIVERPS laboratory

**Domain / objectives:** Composition 1.6 · **Chapter:** 21 · **Time:** 30 min · **Difficulty:** ★★★

## Goal
Hold a referenced asset at **radius 1** constant, then beat or lose to it with **Local**, **Inherits**, **VariantSets**, and **Specializes**. Recite the winning **letter** before you look at the number.

## Background
**LIVERPS** is strongest-to-weakest: Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes (Ch 21). This lab skips E (relocates, Ch 20) and P (payloads, Lab 15) so each contest is one letter versus **R**. Weaker arcs can still **fill gaps**; here every opinion is about `radius`, so there is no gap. Predict, then run.

```text
present:  L  I  V  E  R  P  S
has field:    (whichever you authored)
winner: earliest remaining letter
```

## Steps
1. **L vs R:** local `2` beats referenced `1` → `2.0`.
2. **I vs R:** class inherit `3` beats referenced `1` → `3.0`.
3. **V vs R:** variant `10` (authored inside `GetVariantEditContext`) beats `1` → `10.0`.
4. **S vs R:** specialize `7` **loses** to referenced `1` → `1.0`.

## Full script (identical to `lab20_liverps.py`)

```python
"""Lab 20 — LIVERPS: local, inherit, variant, specialize vs a reference."""
import os
import tempfile
from pxr import Sdf, Usd

os.chdir(tempfile.mkdtemp())
open("asset.usda", "w").write("""#usda 1.0
(
    defaultPrim = "X"
)
def Sphere "X"
{
    double radius = 1
}
""")
stage = Usd.Stage.CreateInMemory()
cls = stage.CreateClassPrim("/_I")
cls.CreateAttribute("radius", Sdf.ValueTypeNames.Double).Set(3)

lvr = stage.DefinePrim("/LvsR")
lvr.GetReferences().AddReference("asset.usda")
lvr.CreateAttribute("radius", Sdf.ValueTypeNames.Double).Set(2)

ivr = stage.DefinePrim("/IvsR")
ivr.GetReferences().AddReference("asset.usda")
ivr.GetInherits().AddInherit("/_I")

vvr = stage.DefinePrim("/VvsR")
vvr.GetReferences().AddReference("asset.usda")
vset = vvr.GetVariantSets().AddVariantSet("look")
vset.AddVariant("hi")
vset.SetVariantSelection("hi")
with vset.GetVariantEditContext():
    vvr.CreateAttribute("radius", Sdf.ValueTypeNames.Double).Set(10)

base = stage.DefinePrim("/_S")
base.CreateAttribute("radius", Sdf.ValueTypeNames.Double).Set(7)
svr = stage.DefinePrim("/SvsR")
svr.GetReferences().AddReference("asset.usda")
svr.GetSpecializes().AddSpecialize("/_S")


def radius(path):
    return stage.GetPrimAtPath(path).GetAttribute("radius").Get()


print("L vs R (local 2, ref 1):", radius("/LvsR"))
print("I vs R (inherit 3, ref 1):", radius("/IvsR"))
print("V vs R (variant 10, ref 1):", radius("/VvsR"))
print("S vs R (specialize 7, ref 1):", radius("/SvsR"))
```

**Expected output**
```text
L vs R (local 2, ref 1): 2.0
I vs R (inherit 3, ref 1): 3.0
V vs R (variant 10, ref 1): 10.0
S vs R (specialize 7, ref 1): 1.0
```

## Check your understanding
1. Recite LIVERPS.
2. Why does specialize 7 lose to reference 1, while inherit 3 wins?
3. Is a session-layer opinion a LIVERPS letter?

**Answers**
1. **Local, Inherits, VariantSets, rElocates, References, Payloads, Specializes.**
2. **I is before R; S is after R.** Same asset, different arc strength.
3. **No.** The session layer is the strongest **sheet of L** (the local stack), not its own letter.

## Stretch challenge
Add a payload-backed prim `/PvsR` with payload radius 9 and a reference radius 1 on the same prim. Solution: composed radius is **1** (R before P). A field authored **only** on the payload would still show through (Ch 21 P6).
