# Lab 15 — Payloads, `LoadNone`, and `OpenMasked`

**Domain / objectives:** Composition 1.5 · Content Aggregation 2.x · **Chapter:** 17 · **Time:** 30 min · **Difficulty:** ★★☆

## Goal
Open a city with **payloads** on `/World/A` and `/World/B` and a **reference** on `/World/C`. Prove **`LoadNone` still loads references**, then **`Load`** one payload, then **`OpenMasked`** so `/World/B` does not exist at all.

## Background
A **payload** is a reference you can leave unloaded (Ch 17). `Usd.Stage.Open(path)` defaults to **`LoadAll`**. Pass **`Usd.Stage.LoadNone`** to open with no payloads composed. **References are not payloads** — `LoadNone` does not hide `/World/C/Hi`. `FindLoadable()` lists prims that have payloads. A **population mask** (`Usd.Stage.OpenMasked`, not `Open(path, mask)`) decides which prims **exist**; load rules decide which payloads inside the mask are composed. Default `OpenMasked` still uses `LoadAll`, so `/World/A/Hi` appears.

## Steps
1. `LoadNone C/Hi: True` — the reference is always composed.
2. `LoadNone A/Hi: False` — the payload is not loaded.
3. `loadable` is `['/World/A', '/World/B']` (not `C`). `load set` is empty.
4. `Load("/World/A")` brings `A/Hi` only; `B/Hi` stays missing.
5. `OpenMasked` with `/World/A`: `A` exists, `B` and `C` do not. `A/Hi` is True because the mask used the default load set.

## Full script (identical to `lab15_payloads_masks.py`)

```python
"""Lab 15 — LoadNone vs references, FindLoadable, OpenMasked."""
import os
import tempfile
from pxr import Usd

os.chdir(tempfile.mkdtemp())
open("hi.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Root"
)
def Xform "Root"
{
    def Cube "Hi"
    {
    }
}
""")
open("city.usda", "w").write("""#usda 1.0
def Xform "World"
{
    def Xform "A" (
        prepend payload = @./hi.usda@
    )
    {
    }
    def Xform "B" (
        prepend payload = @./hi.usda@
    )
    {
    }
    def Xform "C" (
        prepend references = @./hi.usda@
    )
    {
    }
}
""")
none = Usd.Stage.Open("city.usda", Usd.Stage.LoadNone)
print("LoadNone C/Hi:", bool(none.GetPrimAtPath("/World/C/Hi")))
print("LoadNone A/Hi:", bool(none.GetPrimAtPath("/World/A/Hi")))
print("loadable:", [str(p) for p in none.FindLoadable()])
print("load set:", [str(p) for p in none.GetLoadSet()])
none.Load("/World/A")
print("after Load A, A/Hi:", bool(none.GetPrimAtPath("/World/A/Hi")))
print("after Load A, B/Hi:", bool(none.GetPrimAtPath("/World/B/Hi")))
mask = Usd.StagePopulationMask(["/World/A"])
masked = Usd.Stage.OpenMasked("city.usda", mask)
print("masked A:", bool(masked.GetPrimAtPath("/World/A")))
print("masked B:", bool(masked.GetPrimAtPath("/World/B")))
print("masked C:", bool(masked.GetPrimAtPath("/World/C")))
print("masked A/Hi (payload LoadAll):",
      bool(masked.GetPrimAtPath("/World/A/Hi")))
```

**Expected output**
```text
LoadNone C/Hi: True
LoadNone A/Hi: False
loadable: ['/World/A', '/World/B']
load set: []
after Load A, A/Hi: True
after Load A, B/Hi: False
masked A: True
masked B: False
masked C: False
masked A/Hi (payload LoadAll): True
```

## Check your understanding
1. Does `Open(..., LoadNone)` skip references?
2. Is `Usd.Stage.Open(path, mask)` how you apply a population mask?
3. Why is `A/Hi` True on the masked stage?

**Answers**
1. **No.** `LoadNone` only skips **payloads**. `/World/C/Hi` is still there.
2. **No.** Use **`Usd.Stage.OpenMasked(path, mask)`**.
3. `OpenMasked` defaults to **`LoadAll`**, so payloads **inside the mask** load. Combine with `LoadNone` if you want them off.

## Stretch challenge
Reopen with `Usd.Stage.OpenMasked("city.usda", mask, Usd.Stage.LoadNone)` and print `A/Hi`. Solution: `False` — the prim `/World/A` exists (mask) but its payload is unloaded.
