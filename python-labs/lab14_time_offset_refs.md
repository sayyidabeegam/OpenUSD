# Lab 14 — Time-offset references (`Sdf.LayerOffset`)

**Domain / objectives:** Composition 1.4 · **Chapter:** 10, 16 · **Time:** 25 min · **Difficulty:** ★★☆

## Goal
Reference the **same** animated clip twice: identity offset on `/A`, **offset 10** on `/B`. Confirm composed sample times follow `stageTime = offset + scale * layerTime`.

## Background
A **layer offset** remaps time on a reference (or payload, or sublayer) without copying the clip (Obj 1.4, Ch 10/16). `Sdf.LayerOffset(offset, scale)` defaults to `(0, 1)`. The formula:

```text
stageTime = offset + scale * layerTime
```

`lo * layerTime` applies it. Defaults (non-animated values) are **not** shifted — only samples. Before the first sample and after the last, values are held.

## Steps
1. `/A` (identity) has samples at `[0.0, 10.0]`, matching the clip.
2. `/B` (offset 10) has samples at `[10.0, 20.0]`.
3. `/A` at 0 and 10 is origin then `(10, 0, 0)`.
4. `/B` at 10 and 20 is the **same poses** — the clip started 10 frames later.
5. `LayerOffset(10) * 0` is `10.0`; `* 10` is `20.0`.

## Full script (identical to `lab14_time_offset_refs.py`)

```python
"""Lab 14 — Same animation, two layer offsets on references."""
import os
import tempfile
from pxr import Sdf, Usd

os.chdir(tempfile.mkdtemp())
open("anim.usda", "w").write("""#usda 1.0
(
    defaultPrim = "Ball"
)
def Xform "Ball"
{
    double3 xformOp:translate.timeSamples = {
        0: (0, 0, 0),
        10: (10, 0, 0),
    }
    uniform token[] xformOpOrder = ["xformOp:translate"]
}
""")
stage = Usd.Stage.CreateInMemory()
a = stage.DefinePrim("/A")
a.GetReferences().AddReference("anim.usda")
b = stage.DefinePrim("/B")
b.GetReferences().AddReference("anim.usda", Sdf.LayerOffset(10))
attr_a = a.GetAttribute("xformOp:translate")
attr_b = b.GetAttribute("xformOp:translate")
print("A samples:", attr_a.GetTimeSamples())
print("B samples:", attr_b.GetTimeSamples())
print("A at 0:", tuple(attr_a.Get(0)))
print("A at 10:", tuple(attr_a.Get(10)))
print("B at 10:", tuple(attr_b.Get(10)))
print("B at 20:", tuple(attr_b.Get(20)))
lo = Sdf.LayerOffset(10)
print("offset*0:", lo * 0)
print("offset*10:", lo * 10)
```

**Expected output**
```text
A samples: [0.0, 10.0]
B samples: [10.0, 20.0]
A at 0: (0.0, 0.0, 0.0)
A at 10: (10.0, 0.0, 0.0)
B at 10: (0.0, 0.0, 0.0)
B at 20: (10.0, 0.0, 0.0)
offset*0: 10.0
offset*10: 20.0
```

## Check your understanding
1. Write the formula that maps layer time to stage time.
2. Does a layer offset move a **default** (non-sampled) value?
3. `/B` at stage time 0 — which pose, and why?

**Answers**
1. **`stageTime = offset + scale * layerTime`.**
2. **No.** Only time samples (and clips) are remapped.
3. The **first** pose `(0, 0, 0)`, held, because stage 0 is before `/B`'s first sample at 10.

## Stretch challenge
Add `/C` with `Sdf.LayerOffset(0, 2)` (scale 2) and print its sample times. Solution: `[0.0, 20.0]` — the clip lasts twice as long (`0 + 2 * 10 = 20`).
